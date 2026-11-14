"""
Der innere Widerstand quer zur Pfahlachse (opencivil.pfahl.innen_quer).

Die Stützstellen und das Lesen dazwischen, die Querkraft im Bohrpfahl und im
Mikropfahl von Hand, die Längszugkraft aus der Querkraft am eingespannten
Kopf, die Hinweise, wann es den Nachweis gibt, und was die Oberfläche davon
zu sehen bekommt.
"""

import math
import unittest

from opencivil.core.protokoll import HinweisBlock
from opencivil.pfahl.innen import WAHL, biegewiderstand, querschnitt
from opencivil.pfahl.innen_quer import (
    STUETZSTELLEN, anteil, gezogen, stuetzstellen, zwischen,
)
from opencivil.projekt import Projekt
from opencivil.querschnitt.analyse import werkstoff
from opencivil.web import dienst


def projekt(**felder):
    """Ein Projekt mit C30/37 und B500B und einem Pfahl «P» mit diesen Feldern."""
    p = Projekt(name="Probe")
    beton, stahl = p.beton("C30/37").kennung, p.stahl("B500B").kennung
    return p, p.pfahl("P", stahl=stahl, beton=beton, **felder)


def im_kies(N_Ed=1000.0, H_Ed=100.0, M_Ed=0.0, **felder):
    """Ein Pfahl im Kies, ohne Wasser, mit einer Kombination «K» -- ein Bohrpfahl ⌀ 900."""
    p, t = projekt(**{"D": 900.0, "L": 12.0, "t_K": 1.0, "t_w": 30.0, **felder})
    t.schicht("Kies", d=20.0, gamma=20.0, phi_k=35.0, E_s=50.0)
    t.kombination("K", N_Ed=N_Ed, H_Ed=H_Ed, M_Ed=M_Ed)
    return p, t


def mikropfahl(H_Ed=10.0):
    """Ein Rohr 88.9 × 8 im Verpresskörper ⌀ 200, im Kies."""
    return im_kies(N_Ed=400.0, H_Ed=H_Ed, art="mikropfahl", D=200.0, L=8.0, d_a=88.9, t_r=8.0)


def rechnen(p):
    """Aufbau und Lösung -- dazu der innere Nachweis quer des Pfahls t1, wo es ihn gibt."""
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return aufbau, loesung, aufbau.feld("pfahl_innen_quer").get("t1")


def urteile(loesung, nachweis):
    return {u.langname: u for u in loesung.urteile if u.raum == nachweis.id}


def hinweise(loesung):
    return [b.text for b in loesung.protokoll.alle_bloecke() if isinstance(b, HinweisBlock)]


def neigungen(loesung):
    """Die Titel, unter denen die Herleitung die Neigung der Druckdiagonalen wählt."""
    return [b.titel for b in loesung.protokoll.alle_bloecke()
            if getattr(b, "titel", "").startswith("Neigung der Druckdiagonalen")]


def schnitt(aufbau, loesung):
    """Der Querschnitt, wie der Nachweis ihn biegt: Bemessungswerte, Beton als Parabel."""
    pfahl = aufbau.bauteil("t1").objekt
    masse = loesung.befunde["pfahl.t1.nachweis.innen"].masse
    return querschnitt(masse, [werkstoff(s, lambda kid: loesung.werte[kid].groesse.si, WAHL)
                               for s in pfahl.stoffe]), masse


#: Der Bohrpfahl ⌀ 900 von Hand: Stäbe ⌀ 20 auf r_s = 450 − 75 − 10 − 10 mm,
#: d bis zum Schwerpunkt der gezogenen Hälfte, z = 0.9 · d, b_w auf der Höhe
#: des Druckgurts; die Wendel ⌀ 10 mit 150 mm Ganghöhe, B500B und C30/37.
R_S = 0.355
D_STAT = 0.45 + 2.0 * R_S / math.pi
Z = 0.9 * D_STAT
B_W = 2.0 * math.sqrt(0.45 ** 2 - (0.45 - D_STAT + Z) ** 2)
A_SW = 2.0 * math.pi * 0.010 ** 2 / 4.0
F_YD, F_CD = 500e6 / 1.15, 20e6


def wendel(alpha):
    return 0.7 * A_SW / 0.150 * Z * F_YD / math.tan(math.radians(alpha))


def diagonalen(alpha):
    a = math.radians(alpha)
    return B_W * Z * 0.55 * F_CD * math.sin(a) * math.cos(a)


class TestStuetzstellen(unittest.TestCase):
    """M_Rd an Stützstellen der Normalkraft, dazwischen linear."""

    def test_gleich_verteilt(self):
        s = stuetzstellen(-300.0, 900.0)
        self.assertEqual(len(s), STUETZSTELLEN)
        self.assertEqual((s[0], s[-1]), (-300.0, 900.0))
        self.assertAlmostEqual(s[1] - s[0], 1200.0 / (STUETZSTELLEN - 1))
        self.assertEqual(stuetzstellen(5.0, 5.0), [5.0])

    def test_zwischen(self):
        stellen, werte = [0.0, 1.0, 2.0, 3.0], [0.0, 4.0, 6.0, 6.0]
        self.assertEqual(zwischen(stellen, werte, 1.5), 5.0)
        # An einer Stützstelle ihr Wert, auch neben einer, die nichts trägt.
        self.assertEqual(zwischen(stellen, werte, 1.0), 4.0)
        # Zwischen ihr und der, die nichts trägt: null.
        self.assertEqual(zwischen(stellen, werte, 0.5), 0.0)
        self.assertEqual(zwischen([2.0], [7.0], 2.0), 7.0)

    def test_konkav_liegt_die_gerade_darunter(self):
        kurve = lambda N: 100.0 - 50.0 * (N - 0.3) ** 2
        stellen = stuetzstellen(-1.0, 1.0)
        werte = [kurve(N) for N in stellen]
        for k in range(201):
            x = -1.0 + k / 100.0
            self.assertLessEqual(zwischen(stellen, werte, x), kurve(x) + 1e-12)

    def test_anteil_und_zug(self):
        self.assertEqual(anteil(-50.0, 100.0), 0.5)
        self.assertEqual(anteil(10.0, 0.0), math.inf)
        self.assertEqual(anteil(0.0, 0.0), 0.0)
        # Ein Millionstel Newton am Fuss ist kein Zug.
        self.assertFalse(gezogen(-2e-6))
        self.assertTrue(gezogen(-500e3))


class TestBohrpfahl(unittest.TestCase):

    def test_querkraft_von_hand(self):
        """Unter Druck α = 30°: die Wendel trägt weniger als die Druckdiagonalen."""
        _, loesung, nachweis = rechnen(im_kies()[0])
        u = urteile(loesung, nachweis)["Querkraft im Pfahl"]
        self.assertLess(wendel(30), diagonalen(30))
        self.assertAlmostEqual(u.widerstand.groesse.si / (0.8 * wendel(30)), 1.0, places=9)
        self.assertAlmostEqual(u.einwirkung.groesse.si, 100e3)
        self.assertEqual((u.art, u.fall), ("V", "K"))
        self.assertIn("V_Rd = 268.7 kN in z = 1 m", u.begruendung)

    def test_unter_zug_steiler(self):
        """
        Unter Zug α ab 40°. Am Fuss, der nicht zieht, ist N null: dort gilt
        der Normalfall -- der Zugpfahl hat beide Bereiche.
        """
        _, loesung, nachweis = rechnen(im_kies(N_Ed=-500.0)[0])
        u = urteile(loesung, nachweis)["Querkraft im Pfahl"]
        self.assertAlmostEqual(u.widerstand.groesse.si / (0.8 * wendel(40)), 1.0, places=9)
        self.assertEqual(neigungen(loesung), [
            "Neigung der Druckdiagonalen, unter Druck: ganzgradig zwischen 30° und 45° die mit "
            "dem grössten Widerstand",
            "Neigung der Druckdiagonalen, unter Zug: ganzgradig zwischen 40° und 45° die mit "
            "dem grössten Widerstand"])

    def test_rauschen_am_fuss(self):
        """Trägt der Fuss nicht, bleibt dort ein Millionstel Newton -- das ist kein Zug."""
        _, loesung, _ = rechnen(im_kies(spitze="keine")[0])
        self.assertEqual(neigungen(loesung), [
            "Neigung der Druckdiagonalen: ganzgradig zwischen 30° und 45° die mit dem grössten "
            "Widerstand"])

    def test_laengszug_am_eingespannten_kopf(self):
        """
        Am eingespannten Kopf das grösste Moment: dort biegt der Querschnitt mit
        N − |V| · cot α, und das trägt weniger als N allein.
        """
        aufbau, loesung, nachweis = rechnen(im_kies(kopf="eingespannt")[0])
        u = urteile(loesung, nachweis)["Biegung im Pfahl"]
        self.assertIn("in z = 1 m", u.begruendung)
        q, masse = schnitt(aufbau, loesung)
        mit = biegewiderstand(q, 1000e3 - 100e3 / math.tan(math.radians(30)), 0.8, masse.n)
        self.assertAlmostEqual(u.widerstand.groesse.si / mit, 1.0, places=6)
        self.assertLess(mit, 0.95 * biegewiderstand(q, 1000e3, 0.8, masse.n))

    def test_zwischen_den_stuetzstellen_darunter(self):
        """In jeder Tiefe höchstens der genaue Biegewiderstand, und nicht viel weniger."""
        aufbau, loesung, nachweis = rechnen(im_kies()[0])
        v = loesung.befunde["pfahl.t1.steifigkeit"].verlaeufe[0]
        grenze = loesung.befunde[nachweis.id].faelle["K"].M_grenze
        q, masse = schnitt(aufbau, loesung)
        for i in range(0, len(v.z), 15):
            N_V = v.N[i] - abs(v.V[i]) / math.tan(math.radians(30))
            genau = biegewiderstand(q, N_V, 0.8, masse.n)
            with self.subTest(z=v.z[i]):
                self.assertLessEqual(grenze[i], genau * (1.0 + 1e-9))
                self.assertGreater(grenze[i], 0.99 * genau)

    def test_ganghoehe(self):
        """Mehr als 0.40 m je Gang: ein Hinweis -- und weniger Widerstand."""
        _, loesung, nachweis = rechnen(im_kies(s_w=450.0)[0])
        self.assertTrue(any(h.startswith("Die Wendel steigt mehr als 0.40 m je Gang")
                            for h in hinweise(loesung)))
        u = urteile(loesung, nachweis)["Querkraft im Pfahl"]
        self.assertAlmostEqual(u.widerstand.groesse.si / (0.8 * wendel(30) / 3.0), 1.0, places=9)
        _, loesung, _ = rechnen(im_kies()[0])
        self.assertFalse(any("Die Wendel steigt" in h for h in hinweise(loesung)))


class TestMikropfahl(unittest.TestCase):

    def test_querkraft_von_hand(self):
        """V_Rd = η_i · A_v · f_yd / √3, A_v = 2 · A / π -- ohne Fachwerk biegt er mit N."""
        aufbau, loesung, nachweis = rechnen(mikropfahl()[0])
        A = math.pi * (0.0889 ** 2 - 0.0729 ** 2) / 4.0
        u = urteile(loesung, nachweis)["Querkraft im Pfahl"]
        self.assertAlmostEqual(u.widerstand.groesse.si / (0.8 * 2.0 * A / math.pi * F_YD
                                                          / math.sqrt(3.0)), 1.0, places=6)
        v = loesung.befunde["pfahl.t1.steifigkeit"].verlaeufe[0]
        q, _ = schnitt(aufbau, loesung)
        grenze = loesung.befunde[nachweis.id].faelle["K"].M_grenze
        self.assertAlmostEqual(grenze[0] / biegewiderstand(q, v.N[0], 0.8), 1.0, places=6)

    def test_halbe_querkraft(self):
        """Über der Hälfte des Widerstands mindert die Querkraft den Biegewiderstand: ein Hinweis."""
        _, loesung, _ = rechnen(mikropfahl(H_Ed=150.0)[0])
        self.assertTrue(any("mehr als die Hälfte ihres Widerstands" in h
                            for h in hinweise(loesung)))
        _, loesung, _ = rechnen(mikropfahl()[0])
        self.assertFalse(any("mehr als die Hälfte ihres Widerstands" in h
                             for h in hinweise(loesung)))


class TestWannEsIhnGibt(unittest.TestCase):

    def test_nur_quer_belastet(self):
        """Ohne Querkraft und Moment keiner; am eingespannten Kopf zählt ein Moment allein nicht."""
        self.assertIsNone(rechnen(im_kies(H_Ed=0.0)[0])[2])
        self.assertIsNone(rechnen(im_kies(H_Ed=0.0, M_Ed=100.0, kopf="eingespannt")[0])[2])
        _, loesung, nachweis = rechnen(im_kies(H_Ed=0.0, M_Ed=100.0)[0])
        self.assertEqual(sorted(urteile(loesung, nachweis)),
                         ["Biegung im Pfahl", "Querkraft im Pfahl"])

    def test_nur_mit_steifigkeit(self):
        """Reichen die Schichten nicht unter den Fuss, gibt es keine Verläufe und keinen Nachweis."""
        p, t = projekt(art="mikropfahl", D=200.0, L=8.0, grundlage="statisch", eta_a=1.0,
                       R_ak=900.0, R_ak_zug=700.0, d_a=88.9, t_r=8.0)
        t.kombination("K", N_Ed=400.0, H_Ed=10.0)
        self.assertIsNone(rechnen(p)[2])


class TestWasDieOberflaecheSieht(unittest.TestCase):

    def test_grenzen_neben_M_und_V(self):
        p, _ = im_kies()
        d = dienst.rechnen({"projekt": p.als_dict()})["zeichendaten"]["t1"]
        v = d["verlaeufe"][0]
        self.assertEqual(len(v["M_grenze"]), len(v["z"]))
        self.assertTrue(all(g > 0.0 for g in v["M_grenze"]))
        self.assertEqual({round(g, 1) for g in v["V_grenze"]}, {268.7})
        legende = ["".join(z.get("text") or z["mathe"] for z in zeile)
                   for zeile in d["verlaufslegende"]]
        self.assertTrue(any("neben M und V der Widerstand des Pfahls" in z for z in legende))


if __name__ == "__main__":
    unittest.main()
