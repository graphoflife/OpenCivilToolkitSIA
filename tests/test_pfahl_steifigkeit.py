"""
Die Steifigkeit des Einzelpfahls (opencivil.pfahl.bettung, opencivil.pfahl.steifigkeit).

Der gebettete Stab gegen die geschlossenen Lösungen: längs die von Cassan
(Kap. 12.8 des Buches), quer die des langen Balkens auf elastischer
Bettung, frei drehbar und eingespannt (Kap. 12.10). Dazu, was die Rechnung
daraus macht -- Federn am Kopf, Verläufe je Kombination mit E_s,k / 1.5 --,
und was Eintrag und Oberfläche davon zu sehen bekommen.
"""

import math
import unittest

from opencivil.core.protokoll import HinweisBlock
from opencivil.pfahl import buch
from opencivil.pfahl.bettung import Strecke, knoten, laengs, quer
from opencivil.pfahl.steifigkeit import GAMMA_E, Pfahlsteifigkeit
from opencivil.projekt import PfahlEintrag, Projekt
from opencivil.web import dienst
from opencivil.web.api import katalog

def cassan(D, L, E_b, E, mit_fuss=True):
    """
    Die Setzung des Kopfs je Spannung σ_0 nach Cassan, in m/Pa: Fuss und
    Mantel in einer Schicht.
    """
    B, R = buch.CASSAN_MANTEL * E, buch.CASSAN_FUSS * E if mit_fuss else 0.0
    a = math.sqrt(4.0 * B / (D * E_b))
    t = math.tanh(a * L)
    return D * (1.0 + R / (a * D * E_b) * t) / (R + a * D * E_b * t)


def langer_balken(k, EI):
    """λ des Balkens auf der Bettung k je Meter."""
    return (k / (4.0 * EI)) ** 0.25


class TestGebetteterStab(unittest.TestCase):
    """Der Löser allein, mit den Federn von aussen."""

    D, E_b, E = 0.9, 25000e6, 30e6

    def test_laengs_wie_cassan(self):
        A, L = math.pi * self.D ** 2 / 4.0, 12.0
        strecken = [Strecke(0.0, L, buch.CASSAN_MANTEL * self.E * math.pi * self.D,
                            (self.E, self.E))]
        N = 5e6 * A
        druck = laengs(strecken, self.E_b * A, A * buch.CASSAN_FUSS * self.E / self.D, N)
        self.assertAlmostEqual(druck.w[0] / (5e6 * cassan(self.D, L, self.E_b, self.E)), 1.0,
                               places=5)
        # Was der Fuss nicht trägt, hat der Mantel abgegeben.
        self.assertAlmostEqual(druck.N[-1], druck.fusskraft, delta=1e-6 * N)
        zug = laengs(strecken, self.E_b * A, 0.0, N)
        self.assertAlmostEqual(zug.w[0] / (5e6 * cassan(self.D, L, self.E_b, self.E, False)),
                               1.0, places=5)
        self.assertAlmostEqual(zug.N[-1], 0.0, delta=1e-6 * N)

    def test_quer_langer_balken(self):
        EI, k, H, M = 33600e6 * math.pi * self.D ** 4 / 64.0, 30e6, 100e3, 100e3
        lam = langer_balken(k, EI)
        strecken = [Strecke(0.0, 30.0, 0.0, (k, k))]
        frei = quer(strecken, EI, H, 0.0, eingespannt=False)
        self.assertAlmostEqual(frei.y[0] / (2 * H * lam / k), 1.0, places=5)
        self.assertAlmostEqual(frei.theta[0] / (2 * H * lam ** 2 / k), 1.0, places=5)
        groesst = max(frei.M)
        self.assertAlmostEqual(groesst / (0.3224 * H / lam), 1.0, places=3)
        self.assertAlmostEqual(frei.z[frei.M.index(groesst)], math.pi / (4 * lam), delta=0.1)
        # Unten nichts mehr: das Gleichgewicht schliesst.
        self.assertAlmostEqual(frei.V[-1], 0.0, delta=1e-6 * H)
        self.assertAlmostEqual(frei.M[-1], 0.0, delta=1e-6 * H)
        moment = quer(strecken, EI, 0.0, M, eingespannt=False)
        self.assertAlmostEqual(moment.y[0] / (2 * M * lam ** 2 / k), 1.0, places=5)
        self.assertAlmostEqual(moment.theta[0] / (4 * M * lam ** 3 / k), 1.0, places=5)
        fest = quer(strecken, EI, H, M, eingespannt=True)
        self.assertAlmostEqual(fest.y[0] / (H * lam / k), 1.0, places=5)
        self.assertAlmostEqual(fest.M[0] / (-H / (2 * lam)), 1.0, places=5)
        self.assertEqual(fest.theta[0], 0.0)

    def test_lineare_bettung(self):
        """
        Eine Bettung, die über 2 m von null an wächst: gleich wie 100 Stufen
        zu 2 cm -- feinere machten das System schlecht konditioniert --, der
        Druck ohne Sprünge, und unten schliesst das Gleichgewicht.
        """
        EI, k, H, M = 33600e6 * math.pi * self.D ** 4 / 64.0, 30e6, 100e3, 50e3
        linear = [Strecke(0.0, 2.0, 0.0, (0.0, k)), Strecke(2.0, 30.0, 0.0, (k, k))]
        n = 100
        stufen = [Strecke(2.0 * i / n, 2.0 * (i + 1) / n, 0.0, (k * (i + 0.5) / n,) * 2)
                  for i in range(n)] + [Strecke(2.0, 30.0, 0.0, (k, k))]
        for eingespannt in (False, True):
            a = quer(linear, EI, H, M, eingespannt=eingespannt)
            b = quer(stufen, EI, H, M, eingespannt=eingespannt)
            self.assertAlmostEqual(a.y[0] / b.y[0], 1.0, places=4)
            self.assertAlmostEqual(max(a.M, key=abs) / max(b.M, key=abs), 1.0, places=4)
            self.assertAlmostEqual(a.V[-1], 0.0, delta=1e-6 * H)
            self.assertAlmostEqual(a.M[-1], 0.0, delta=1e-6 * H)
        # Der Druck oben ist die wachsende Bettung mal y, Knoten für Knoten.
        frei = quer(linear, EI, H, M, eingespannt=False)
        for zi, yi, q in zip(frei.z, frei.y, frei.q):
            if zi <= 2.0:
                self.assertAlmostEqual(q, k * zi / 2.0 * yi, delta=1e-9 * k * frei.y[0])

    def test_knoten_ohne_rundungsfehler(self):
        """Eine Strecke von 0.1 m gibt bei Δz = 0.1 m ein Element, nicht zwei."""
        z = knoten([Strecke(1.5, 1.6, 0.0, (1.0, 1.0)), Strecke(1.6, 2.0, 0.0, (1.0, 1.0))], 0.1)
        self.assertEqual(len(z), 6)

    def test_ungehalten(self):
        with self.assertRaisesRegex(ValueError, "nicht gehalten"):
            laengs([Strecke(0.0, 5.0, 0.0, (0.0, 0.0))], 1e9, 0.0, 1e6)


def projekt(**felder):
    """Ein Projekt mit C30/37 und B500B und einem Pfahl «P» mit diesen Feldern."""
    p = Projekt(name="Probe")
    beton, stahl = p.beton("C30/37").kennung, p.stahl("B500B").kennung
    return p, p.pfahl("P", stahl=stahl, beton=beton, **felder)


def modul(loesung, art, kurz):
    """Der Elastizitätsmodul eines Baustoffs, wie die Lösung ihn hat, in N/m²."""
    return next(w.groesse.si for w in loesung.werte.values()
                if w.id.startswith(art + ".") and w.id.endswith("." + kurz))


def rechnen(p):
    """Aufbau, Lösung, die Federn am Kopf in SI und der Befund der Steifigkeit des Pfahls t1."""
    aufbau = p.aufbauen()
    teil = aufbau.bauteil("t1")
    loesung = aufbau.werk.loese(*teil.ziele())
    kennung = Pfahlsteifigkeit.kennung(teil.objekt)
    federn = {w.id.rsplit(".", 1)[1]: w.groesse.si for w in loesung.werte.values()
              if w.id.startswith(kennung + ".") and w.id.count(".") == 3}
    return aufbau, loesung, federn, loesung.befunde.get(kennung)


class TestFedernAmKopf(unittest.TestCase):
    """Eine Schicht, ohne Abminderung: dieselben geschlossenen Lösungen."""

    @classmethod
    def setUpClass(cls):
        cls.D, cls.L, cls.E = 0.9, 12.0, 30e6
        p, t = projekt(D=900.0, L=cls.L, t_K=0.0, t_red=0.0)
        t.schicht("Kies", d=40.0, E_s=30.0)
        t.kombination("K", N_Ed=2000.0, H_Ed=150.0)
        cls.aufbau, cls.loesung, cls.federn, cls.befund = rechnen(p)
        cls.A, cls.I = math.pi * cls.D ** 2 / 4.0, math.pi * cls.D ** 4 / 64.0
        cls.E_cm = modul(cls.loesung, "beton", "E_cm")

    def test_laengs(self):
        """k_v = N / s_0 = A · σ_0 / s_0."""
        druck = self.A / cassan(self.D, self.L, self.E_cm, self.E)
        zug = self.A / cassan(self.D, self.L, self.E_cm, self.E, False)
        self.assertAlmostEqual(self.federn["k_v"] / druck, 1.0, places=4)
        self.assertAlmostEqual(self.federn["k_v_zug"] / zug, 1.0, places=4)

    def test_quer_wie_der_lange_balken(self):
        """λL ≈ 3.5: lang genug, dass die geschlossene Lösung auf ein Prozent stimmt."""
        lam = langer_balken(self.E, self.E_cm * self.I)
        self.assertGreater(lam * self.L, 3.4)
        erwartet = {"k_h": self.E / (2 * lam), "K_HH": self.E / lam,
                    "K_HM": -self.E / (2 * lam ** 2), "K_MM": self.E / (2 * lam ** 3)}
        for kurz, wert in erwartet.items():
            with self.subTest(kurz):
                self.assertAlmostEqual(self.federn[kurz] / wert, 1.0, delta=0.01)

    def test_die_matrix_passt_zur_freien_feder(self):
        f = self.federn
        self.assertAlmostEqual(f["K_HH"] - f["K_HM"] ** 2 / f["K_MM"], f["k_h"],
                               delta=1e-9 * f["k_h"])

    def test_kennzahlen_unter_dem_pfahl(self):
        from opencivil.bericht.zusammenfassung import kennzahlen
        zeilen = kennzahlen(self.aufbau, "t1", self.loesung)
        self.assertEqual([k.definition.symbol for k, _ in zeilen],
                         ["k_v", "k_{v,Z}", "k_h", "K_{HH}", "K_{HM}", "K_{MM}"])
        self.assertEqual(zeilen[0][1].einheit.name, "MN/m")

    def test_je_kombination_mit_dem_bemessungswert(self):
        """Mit E_s,k / γ_E: y_0 = 2·H·λ_d / k_d."""
        v = self.befund.verlaeufe[0]
        k = self.E / GAMMA_E
        lam = langer_balken(k, self.E_cm * self.I)
        self.assertAlmostEqual(v.y[0] / (2 * 150e3 * lam / k), 1.0, delta=0.01)
        self.assertAlmostEqual(v.z[0], 0.0)
        self.assertAlmostEqual(v.z[-1], self.L)
        self.assertAlmostEqual(v.N[0], 2000e3)
        self.assertAlmostEqual(v.p[0] * self.D, k * v.y[0], delta=1e-6 * k * v.y[0])
        self.assertGreater(v.N_b, 0.0)


class TestWahlen(unittest.TestCase):

    def test_abminderung_macht_weicher(self):
        def k_h(t_red):
            p, t = projekt(D=900.0, L=12.0, t_K=0.0, t_red=t_red)
            t.schicht("Kies", d=40.0)
            return rechnen(p)[2]["k_h"]

        self.assertLess(k_h(3.0), k_h(0.0))
        # Unter t_red ändert sie nichts.
        p, t = projekt(D=900.0, L=12.0, t_K=3.0, t_red=3.0)
        t.schicht("Kies", d=40.0)
        q, r = projekt(D=900.0, L=12.0, t_K=3.0, t_red=0.0)
        r.schicht("Kies", d=40.0)
        self.assertAlmostEqual(rechnen(p)[2]["k_h"], rechnen(q)[2]["k_h"])

    def test_ohne_mantelreibung_keine_feder_laengs(self):
        """Eine Auffüllung mit q_s,k = 0 trägt auch elastisch nicht -- quer schon."""
        def federn(q_s):
            p, t = projekt(t_K=0.0)
            t.schicht("Auffüllung", d=4.0, mantel="eingeben", q_s=q_s)
            t.schicht("Kies", d=20.0)
            return rechnen(p)[2]

        ohne, mit = federn(0.0), federn(10.0)
        self.assertLess(ohne["k_v"], mit["k_v"])
        self.assertEqual(ohne["k_h"], mit["k_h"])

    def test_ohne_fuss_druck_wie_zug(self):
        p, t = projekt(spitze="keine")
        t.schicht("Kies", d=20.0)
        f = rechnen(p)[2]
        self.assertAlmostEqual(f["k_v"], f["k_v_zug"])

    def test_eingespannt_zaehlt_das_moment_nicht(self):
        p, t = projekt(kopf="eingespannt")
        t.schicht("Kies", d=20.0)
        t.kombination("Nur Moment", N_Ed=500.0, M_Ed=100.0)
        t.kombination("Quer", N_Ed=500.0, H_Ed=100.0, M_Ed=100.0)
        _, loesung, _, befund = rechnen(p)
        nur, beides = befund.verlaeufe
        self.assertFalse(nur.quer)
        self.assertEqual(beides.theta[0], 0.0)
        self.assertLess(beides.M[0], 0.0)
        texte = [b.text for b in loesung.protokoll.alle_bloecke() if isinstance(b, HinweisBlock)]
        self.assertEqual(sum("zählt nicht" in t for t in texte), 2)

    def test_mikropfahl_rechnet_mit_dem_rohr(self):
        """Nur das Rohr nach der Abrostung biegt sich; λL ≈ 19, ein langer Balken."""
        p = Projekt(name="Probe")
        stahl = p.stahl("B500B").kennung
        t = p.pfahl("M", stahl=stahl, art="mikropfahl", D=200.0, L=8.0, t_K=0.0, t_red=0.0,
                    d_a=88.9, t_r=8.0, dt=1.0)
        t.schicht("Kies", d=20.0, E_s=40.0)
        _, loesung, federn, _ = rechnen(p)
        aussen, innen = 0.0889 - 0.002, 0.0889 - 0.016
        EI = modul(loesung, "betonstahl", "E_s") * math.pi * (aussen ** 4 - innen ** 4) / 64.0
        lam = langer_balken(40e6, EI)
        self.assertAlmostEqual(federn["k_h"] / (40e6 / (2 * lam)), 1.0, delta=0.005)


class TestEintrag(unittest.TestCase):

    def test_vorgaben(self):
        t = PfahlEintrag.neu("t1", "P")
        self.assertEqual((t.kopf.value, t.t_red), ("frei", 2.0))
        self.assertEqual(t.schichten[0].E_s, 30.0)
        self.assertEqual((t.kombinationen[0].H_Ed, t.kombinationen[0].M_Ed), (0.0, 0.0))

    def test_hin_und_zurueck(self):
        p, t = projekt(kopf="eingespannt", t_red=1.5)
        t.schicht("Kies", d=20.0, E_s=80.0)
        t.kombination("K", N_Ed=-200.0, H_Ed=50.0, M_Ed=-20.0)
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.als_dict(), p.als_dict())

    def test_aus_dem_versuch_ohne_schichten_keine_steifigkeit(self):
        p, t = projekt(grundlage="statisch", eta_a=1.0)
        t.kombination("K", N_Ed=500.0)
        aufbau, loesung, federn, befund = rechnen(p)
        self.assertEqual((federn, befund), ({}, None))
        self.assertTrue(any("keine Steifigkeit" in w for w in aufbau.warnungen))

    def test_aus_dem_versuch_traegt_der_fuss(self):
        p, t = projekt(grundlage="statisch", eta_a=1.0, spitze="keine")
        t.schicht("Kies", d=20.0)
        f = rechnen(p)[2]
        self.assertGreater(f["k_v"], f["k_v_zug"])


class TestWasDieOberflaecheSieht(unittest.TestCase):

    def test_katalog(self):
        self.assertEqual([k["wert"] for k in katalog()["pfahl"]["koepfe"]],
                         ["frei", "eingespannt"])

    def test_verlaeufe(self):
        p, t = projekt()
        t.schicht("Kies", d=20.0)
        t.kombination("Kombination 1", N_Ed=-300.0)
        t.kombination("Quer", N_Ed=800.0, H_Ed=120.0)
        daten = dienst.rechnen({"projekt": p.als_dict()})["zeichendaten"]["t1"]
        laengs_, quer_ = daten["verlaeufe"]
        self.assertEqual(laengs_["name"], "Kombination 1")
        self.assertNotIn("y", laengs_)
        self.assertAlmostEqual(quer_["N"][0], 800.0)
        self.assertAlmostEqual(quer_["V"][0], 120.0)
        self.assertAlmostEqual(quer_["z"][0], 1.0)
        self.assertEqual(len(quer_["z"]), len(quer_["M"]))


if __name__ == "__main__":
    unittest.main()
