"""
Der äussere Widerstand quer zur Pfahlachse (opencivil.pfahl.erdwiderstand, opencivil.pfahl.quer).

Der Erdwiderstand von Hand, die Brüche gegen ihre geschlossenen Lösungen --
kurzer und langer Pfahl, frei drehbar und eingespannt, mit und ohne Hebel
des Moments --, der Biegewiderstand eines Stabs gegen M_pl, und der
Nachweis, wie ein Projekt ihn rechnet: R_tr,d, die Bettungskraft, wann er
fehlt, und was die Oberfläche davon zu sehen bekommt.
"""

import math
import unittest

from opencivil.core.protokoll import HinweisBlock, TextBlock
from opencivil.pfahl.boden import Profil
from opencivil.pfahl.erdwiderstand import Erdwiderstand, Festigkeit, Linie, brueche
from opencivil.pfahl.innen import Masse, biegewiderstand, querschnitt
from opencivil.pfahl.quer import GAMMA_M_QUER
from opencivil.projekt import Projekt, ProjektFehler
from opencivil.querschnitt.interaktion import Werkstoff
from opencivil.querschnitt.werkstoffgesetz import Stahlgesetz
from opencivil.web import dienst


def projekt(**felder):
    """Ein Projekt mit C30/37 und B500B und einem Pfahl «P» mit diesen Feldern."""
    p = Projekt(name="Probe")
    beton, stahl = p.beton("C30/37").kennung, p.stahl("B500B").kennung
    return p, p.pfahl("P", stahl=stahl, beton=beton, **felder)


def im_kies(H_Ed=100.0, M_Ed=0.0, **felder):
    """Ein Bohrpfahl ⌀ 900 im Kies, ohne Wasser, mit einer Kombination «K»."""
    p, t = projekt(**{"D": 900.0, "L": 12.0, "t_K": 1.0, "t_w": 30.0, **felder})
    t.schicht("Kies", d=20.0, gamma=20.0, phi_k=35.0, E_s=50.0)
    t.kombination("K", N_Ed=1000.0, H_Ed=H_Ed, M_Ed=M_Ed)
    return p, t


def rechnen(p):
    """Aufbau und Lösung -- dazu der Nachweis quer des Pfahls t1, wo es ihn gibt."""
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return aufbau, loesung, aufbau.feld("pfahl_quer").get("t1")


def urteile(loesung, nachweis):
    return {u.langname: u for u in loesung.urteile if u.raum == nachweis.id}


class TestErdwiderstand(unittest.TestCase):
    """p_E,k = 3 · D · (e_p − max(0; e_a)), von Hand."""

    def test_rankine(self):
        sand = Festigkeit(True, phi=math.radians(30.0))
        self.assertAlmostEqual(sand.K_p, 3.0)
        e_p, e_a = sand.erddruecke(90e3)
        self.assertAlmostEqual(e_p, 270e3)
        self.assertAlmostEqual(e_a, 30e3)
        mit_c = Festigkeit(True, phi=math.radians(30.0), c=10e3)
        e_p, e_a = mit_c.erddruecke(90e3)
        self.assertAlmostEqual(e_p, 270e3 + 2 * 10e3 * math.sqrt(3.0))
        self.assertAlmostEqual(e_a, 30e3 - 2 * 10e3 / math.sqrt(3.0))
        # Undrainiert die totale Spannung, K = 1 und s_u statt c'.
        self.assertEqual(Festigkeit(False, s_u=40e3).erddruecke(90e3), (170e3, 10e3))

    def test_ueber_die_tiefe(self):
        """
        Sand über Ton, das Wasser im Sand: über ihm σ'_v = γ · z, darunter
        mit γ − γ_w; im Ton die totale Spannung, und wo e_a positiv wird,
        bleibt p_E,k = 3 · D · 4 · s_u.
        """
        D, b = 0.8, 2.4
        profil = Profil([4.0, 10.0], [20e3, 18e3], t_w=2.0, gamma_w=10e3)
        erd = Erdwiderstand(profil, [Festigkeit(True, phi=math.radians(30.0)),
                                     Festigkeit(False, s_u=50e3)], D)
        self.assertAlmostEqual(erd.bei(1.0), b * 8.0 / 3.0 * 20e3)
        self.assertAlmostEqual(erd.bei(3.0), b * 8.0 / 3.0 * 50e3)
        # An der Grenze der kleinere: der Sand gäbe b · 8/3 · 60 kPa = 384 kN/m, der
        # Ton, mit σ_v = 80 kPa unter 2 · s_u, nur b · (80 + 100) kPa = 432 kN/m.
        self.assertAlmostEqual(erd.bei(4.0), min(b * 8.0 / 3.0 * 60e3, b * 180e3))
        self.assertAlmostEqual(erd.bei(9.0), b * 4.0 * 50e3)
        # Geteilt an der Schicht, am Wasser und wo im Ton σ_v = 2 · s_u wird.
        linien = erd.linien(0.0, 14.0)
        grenzen = [(li.oben, li.unten) for li in linien]
        self.assertEqual([li.schicht for li in linien], [0, 0, 1, 1])
        self.assertEqual(grenzen[:2], [(0.0, 2.0), (2.0, 4.0)])
        self.assertAlmostEqual(grenzen[2][1], 4.0 + 20.0 / 18.0)
        for li in linien:
            mitte = (li.oben + li.unten) / 2.0
            with self.subTest(oben=li.oben):
                self.assertAlmostEqual(li.p(mitte), erd.je_meter(mitte, li.schicht), delta=1e-6)


class TestBrueche(unittest.TestCase):
    """Die Mechanismen gegen ihre geschlossenen Lösungen."""

    c, L, M_R = 200e3, 12.0, 500e3

    def gleich(self, L=None, oben=0.0):
        """p_E überall c, vom Kopf in ``oben`` an."""
        return [Linie(0, oben, oben + (L or self.L), self.c, self.c)]

    @staticmethod
    def bruch(alle, was):
        return next(b for b in alle if b.was == was)

    def test_langer_pfahl_frei(self):
        """Ein Gelenk, wo die Querkraft null wird: H = c · s_h, mit s_h aus M_R und dem Hebel e."""
        for e in (0.0, 1.0, -0.5):
            with self.subTest(e=e):
                s = -e + math.sqrt(e * e + 2.0 * self.M_R / self.c)
                alle = brueche(self.gleich(), 0.0, self.M_R, eingespannt=False, e=e)
                b = self.bruch(alle, "Gelenk im Pfahl")
                self.assertAlmostEqual(b.H / (self.c * s), 1.0, places=4)
                self.assertAlmostEqual(b.lage, s, delta=0.01)
                self.assertIs(min(alle, key=lambda x: x.H), b)

    def test_kurzer_pfahl_frei(self):
        """Ohne Gelenk dreht er um s_r = L/√2: H = (√2 − 1) · c · L; verschoben H = c · L."""
        alle = brueche(self.gleich(), 0.0, 1e12, eingespannt=False)
        b = self.bruch(alle, "Drehung des ganzen Pfahls")
        self.assertAlmostEqual(b.H / ((math.sqrt(2.0) - 1.0) * self.c * self.L), 1.0, places=4)
        self.assertAlmostEqual(b.lage, self.L / math.sqrt(2.0), delta=0.01)
        self.assertIs(min(alle, key=lambda x: x.H), b)
        verschoben = self.bruch(alle, "Verschiebung des ganzen Pfahls")
        self.assertAlmostEqual(verschoben.H, self.c * self.L)
        self.assertIsNone(verschoben.lage)

    def test_eingespannt(self):
        """Lang zwei Gelenke, H = 2 · √(M_R · c); kurz verschoben, H = c · L."""
        alle = brueche(self.gleich(), 0.0, self.M_R, eingespannt=True)
        b = self.bruch(alle, "Gelenke am Kopf und im Pfahl")
        self.assertAlmostEqual(b.H / (2.0 * math.sqrt(self.M_R * self.c)), 1.0, places=4)
        self.assertIs(min(alle, key=lambda x: x.H), b)
        self.assertEqual([x.was for x in alle], ["Gelenk am Kopf, darunter Drehung",
                                                 "Gelenke am Kopf und im Pfahl",
                                                 "Verschiebung des ganzen Pfahls"])
        kurz = min(brueche(self.gleich(L=2.0), 0.0, self.M_R, eingespannt=True),
                   key=lambda x: x.H)
        self.assertEqual(kurz.was, "Verschiebung des ganzen Pfahls")
        self.assertAlmostEqual(kurz.H, self.c * 2.0)

    def test_linear_wie_broms(self):
        """p = a · s, lang und frei: s_h³ = 3 · M_R / a, H = a · s_h² / 2."""
        a, L = 100e3, 20.0
        s = (3.0 * self.M_R / a) ** (1.0 / 3.0)
        b = self.bruch(brueche([Linie(0, 0.0, L, 0.0, a * L)], 0.0, self.M_R, eingespannt=False),
                       "Gelenk im Pfahl")
        self.assertAlmostEqual(b.H / (a * s * s / 2.0), 1.0, places=4)

    def test_s_ab_kopf(self):
        """Dieselben Linien um t_K tiefer, mit dem Kopf dort: derselbe Bruch."""
        oben = brueche(self.gleich(), 0.0, self.M_R, eingespannt=False)
        tiefer = brueche(self.gleich(oben=3.0), 3.0, self.M_R, eingespannt=False)
        for a, b in zip(oben, tiefer):
            self.assertAlmostEqual(a.H, b.H, delta=1e-6 * a.H)

    def test_integrale_exakt(self):
        """Über Stücke verschiedener Neigung: verschoben genau ∫ p ds."""
        linien = [Linie(0, 0.0, 1.37, 50e3, 120e3), Linie(1, 1.37, 5.0, 300e3, 410e3)]
        verschoben = self.bruch(brueche(linien, 0.0, self.M_R, eingespannt=False),
                                "Verschiebung des ganzen Pfahls")
        self.assertAlmostEqual(verschoben.H, 1.37 * 85e3 + 3.63 * 355e3, delta=1e-6)


class TestBiegewiderstand(unittest.TestCase):
    """η_i · M_R(N / η_i) -- ein Stab aus Stahl ohne Normalkraft gegen M_pl."""

    stahl = Werkstoff("B500B", Stahlgesetz(E_s=205e9, f_yd=500e6, f_yd_druck=500e6,
                                           eps_ud=0.045), -0.045, 0.045)

    def test_vollstab_und_rohr(self):
        for masse, M_pl in ((Masse(d_aussen=0.036), 500e6 * 0.036 ** 3 / 6.0),
                            (Masse(d_aussen=0.0869, d_innen=0.0729),
                             500e6 * (0.0869 ** 3 - 0.0729 ** 3) / 6.0)):
            with self.subTest(masse=masse):
                q = querschnitt(masse, [self.stahl])
                self.assertAlmostEqual(biegewiderstand(q, 0.0, 0.8) / (0.8 * M_pl), 1.0,
                                       delta=0.01)

    def test_eta_i_verkleinert_die_flaeche(self):
        q = querschnitt(Masse(d_aussen=0.036), [self.stahl])
        self.assertAlmostEqual(biegewiderstand(q, 100e3, 0.5),
                               0.5 * biegewiderstand(q, 200e3, 1.0), delta=1.0)
        # Mehr Normalkraft, als der Stab trägt: kein Biegewiderstand mehr.
        self.assertEqual(biegewiderstand(q, 1e9, 0.8), 0.0)


class TestNachweis(unittest.TestCase):
    """Wie ein Projekt den Pfahl quer nachweist."""

    def test_bemessungswert(self):
        """R_tr,d = η_a,tr · R_tr,k / 1.4, und der Grad R_tr,d / H_Ed."""
        p, t = im_kies(eta_tr=0.6)
        _, loesung, quer = rechnen(p)
        fall = loesung.befunde[quer.id].faelle["K"]
        self.assertAlmostEqual(fall.R_trd, 0.6 * fall.R_trk / GAMMA_M_QUER)
        self.assertEqual(fall.bruch.was, "Gelenk im Pfahl")
        u = urteile(loesung, quer)["Äusserer Pfahlwiderstand quer"]
        self.assertAlmostEqual(u.erfuellungsgrad.si, fall.R_trd / 100e3, delta=1e-6)
        self.assertEqual((u.art, u.fall), ("R_tr", "K"))

    def test_der_hebel_des_moments(self):
        """Ein Moment, das wie H dreht, verkleinert R_tr,k; eines dagegen vergrössert ihn."""
        R = {}
        for M_Ed in (0.0, 100.0, -100.0):
            p, _ = im_kies(M_Ed=M_Ed)
            _, loesung, quer = rechnen(p)
            R[M_Ed] = loesung.befunde[quer.id].faelle["K"].R_trk
        self.assertLess(R[100.0], R[0.0])
        self.assertGreater(R[-100.0], R[0.0])

    def test_querkraft_negativ(self):
        """Dieselbe Last in die andere Richtung: derselbe Widerstand, verglichen mit dem Betrag."""
        p, _ = im_kies(H_Ed=100.0)
        _, loesung, quer = rechnen(p)
        q, _ = im_kies(H_Ed=-100.0)
        _, loesung_neg, quer_neg = rechnen(q)
        self.assertAlmostEqual(loesung_neg.befunde[quer_neg.id].faelle["K"].R_trd,
                               loesung.befunde[quer.id].faelle["K"].R_trd)
        u = urteile(loesung_neg, quer_neg)["Äusserer Pfahlwiderstand quer"]
        self.assertAlmostEqual(u.einwirkung.groesse.si, 100e3)
        self.assertIn("|H_Ed| = 100 kN", u.begruendung)

    def test_nur_ein_moment(self):
        """Frei drehbar mit M_Ed und ohne H_Ed: nur die Bettungskraft; eingespannt gar nichts."""
        p, _ = im_kies(H_Ed=0.0, M_Ed=100.0)
        _, loesung, quer = rechnen(p)
        self.assertEqual(list(urteile(loesung, quer)), ["Bettungskraft am Pfahl"])
        self.assertIsNone(loesung.befunde[quer.id].faelle["K"].R_trd)
        self.assertTrue(any("Ohne Querkraft am Kopf" in b.text
                            for b in loesung.protokoll.alle_bloecke() if isinstance(b, TextBlock)))
        q, _ = im_kies(H_Ed=0.0, M_Ed=100.0, kopf="eingespannt")
        self.assertIsNone(rechnen(q)[2])

    def test_bettung_am_terrain(self):
        """
        Der Kopf am Terrain im Sand ohne Kohäsion, die Bettung nicht
        abgemindert: dort hält der Boden nichts, die Bettungskraft schon --
        nicht erfüllt, mit dem Hinweis. Mit Abminderung geht es auf.
        """
        p, _ = im_kies(t_K=0.0, t_red=0.0)
        _, loesung, quer = rechnen(p)
        u = urteile(loesung, quer)["Bettungskraft am Pfahl"]
        self.assertEqual(u.erfuellungsgrad.si, 0.0)
        self.assertIn("in z = 0 m", u.begruendung)
        self.assertTrue(any("Der Boden gibt hier nach" in b.text
                            for b in loesung.protokoll.alle_bloecke()
                            if isinstance(b, HinweisBlock)))
        q, _ = im_kies(t_K=0.0, t_red=2.0)
        _, loesung, quer = rechnen(q)
        self.assertGreater(urteile(loesung, quer)["Bettungskraft am Pfahl"].erfuellungsgrad.si,
                           1.0)

    def test_grenze_im_befund(self):
        """In jeder Tiefe p_E,d / D -- in 6 m Tiefe von Hand."""
        p, _ = im_kies()
        aufbau, loesung, quer = rechnen(p)
        steifigkeit = loesung.befunde["pfahl.t1.steifigkeit"]
        v = steifigkeit.verlaeufe[0]
        grenze = loesung.befunde[quer.id].faelle["K"].grenze
        self.assertEqual(len(grenze), len(v.z))
        s = math.sin(math.radians(35.0))
        K_p = (1.0 + s) / (1.0 - s)
        i = min(range(len(v.z)), key=lambda k: abs(v.z[k] - 6.0))
        hand = 0.7 / 1.4 * 3.0 * 0.9 * (K_p - 1.0 / K_p) * 20e3 * v.z[i] / 0.9
        self.assertAlmostEqual(grenze[i] / hand, 1.0, places=9)

    def test_wann_es_ihn_gibt(self):
        """Nur mit Steifigkeit und einer Kombination, die quer belastet -- sonst eine Warnung."""
        p, _ = im_kies(H_Ed=0.0)
        self.assertIsNone(rechnen(p)[2])
        q, t = projekt(art="mikropfahl", D=200.0, L=8.0, grundlage="statisch", eta_a=1.0,
                       R_ak=900.0, R_ak_zug=700.0, d_a=88.9, t_r=8.0)
        t.kombination("K", N_Ed=400.0, H_Ed=10.0)
        aufbau, _, quer = rechnen(q)
        self.assertIsNone(quer)
        self.assertIn("Pfahl 'P': die Schichten reichen nicht bis unter den Fuss → keine "
                      "Steifigkeit und kein Widerstand quer.", aufbau.warnungen)

    def test_regeln(self):
        """η_a,tr höchstens wie gerechnet; mit R_a,k aus dem Versuch prüft quer die Schichten."""
        p, _ = im_kies(eta_tr=0.8)
        with self.assertRaises(ProjektFehler) as fehler:
            p.aufbauen()
        self.assertIn("η_a,tr = 0.8 liegt über 0.7", str(fehler.exception))
        q, t = projekt(grundlage="statisch", eta_a=1.0, R_ak=3000.0, R_ak_zug=1000.0)
        t.schicht("Kies", d=20.0, phi_k=0.0)
        t.kombination("K", N_Ed=1000.0)
        q.aufbauen()
        t.kombinationen[0].H_Ed = 50.0
        with self.assertRaises(ProjektFehler) as fehler:
            q.aufbauen()
        self.assertIn("drainiert braucht φ'_k über null", str(fehler.exception))


class TestWasDieOberflaecheSieht(unittest.TestCase):

    def test_grenze_und_legende(self):
        p, _ = im_kies()
        d = dienst.rechnen({"projekt": p.als_dict()})["zeichendaten"]["t1"]
        v = d["verlaeufe"][0]
        self.assertEqual(len(v["p_grenze"]), len(v["z"]))
        self.assertTrue(all(g >= 0.0 for g in v["p_grenze"]))
        zeilen = ["".join(z.get("text") or z["mathe"] for z in zeile) for zeile in d["legende"]]
        self.assertTrue(any(z.startswith("Quer, in «K» R_{tr,d} = ") for z in zeilen))
        legende = ["".join(z.get("text") or z["mathe"] for z in zeile)
                   for zeile in d["verlaufslegende"]]
        self.assertTrue(any(z.startswith("Gestrichelt, so weit sie ins Bild fallen, die Grenzen")
                            and "p_{E,d} / D" in z for z in legende))


if __name__ == "__main__":
    unittest.main()
