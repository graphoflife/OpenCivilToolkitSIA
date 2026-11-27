"""
Die Decke nach der FEM: das Dreieck DKT, die Platte gegen bekannte Lösungen
-- die gelenkige Rechteckplatte nach Navier, die ringsum eingespannte
Quadratplatte, die Kragplatte --, die Probe Σ Lagerkräfte = Σ Lasten, der
Träger gegen eine Handrechnung, das Gewicht seines Stegs in beiden
Verfahren, Teile, die sich frei bewegen könnten, und was die Oberfläche von
einer Decke nach der FEM bekommt.
"""

import math
import unittest

from opencivil.core.protokoll import TabellenBlock
from opencivil.decke import geometrie as geo
from opencivil.decke import lasten
from opencivil.decke.fem import auswertung
from opencivil.decke.fem.element import Dreieck, steifigkeit_der_platte, steifigkeit_des_traegers
from opencivil.decke.fem.rechnung import KNOTEN_HOECHSTENS, rechnen
from opencivil.decke.modell import (
    Decke, Flaechenlast, Lastfall, Linienlager, Platte, Traeger, Verfahren, Zone,
)
from opencivil.decke.rechnung import rechnen as nach_streifen
from opencivil.decke.rechnung import spitzen
from opencivil.projekt import Projekt
from opencivil.web import api
from tests.test_decke_projekt import bilder, mit_lasten, zeichnung

E = 30e9
Q = 10e3


def platte(ecken, h=0.2, nu=0.2):
    return Platte("P", tuple(ecken), h, E, 25e3, nu=nu)


def rechteck(a, b):
    return ((0.0, 0.0), (a, 0.0), (a, b), (0.0, b))


def ringsum(ecken, eingespannt=False):
    return [Linienlager(f"W{i + 1}", ecken[i], ecken[(i + 1) % len(ecken)], eingespannt=eingespannt)
            for i in range(len(ecken))]


def gleichmaessig(q=Q):
    return [Lastfall("q", [Flaechenlast("q", q, platte="P")])]


def an(e, p, groesse):
    """Eine Grösse im Fall «q» an der Stelle ``p``, in SI."""
    return getattr(auswertung.an_stelle(e, e.fall("q"), p), groesse)


class TestElement(unittest.TestCase):
    """
    Das Dreieck DKT: als starrer Körper verschoben, kostet es nichts; mit
    einer gleichmässigen Krümmung hat es an jeder Ecke genau deren Momente
    -- der Patch-Test.
    """

    ECKEN = [(0.3, 0.1), (1.4, 0.4), (0.6, 1.2)]

    def test_starr_ohne_kraft_und_moment(self):
        d = Dreieck(self.ECKEN, E, 0.2, 0.2)
        gross = max(abs(k) for zeile in d.K for k in zeile)
        for w0, ax, ay in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
            u = [x for px, py in self.ECKEN for x in (w0 + ax * px + ay * py, ax, ay)]
            kraefte = [sum(k * x for k, x in zip(zeile, u)) for zeile in d.K]
            self.assertLess(max(abs(f) for f in kraefte), 1e-9 * gross)
            self.assertLess(max(abs(m) for ecke in d.momente(u) for m in ecke), 1e-3)

    def test_gleichmaessige_kruemmung(self):
        """w = a·x² + b·x·y + c·y²: m_x = −D·(2a + 2νc), m_y = −D·(2c + 2νa), m_xy = −D·(1 − ν)·b."""
        a, b, c, nu = 0.003, -0.002, 0.005, 0.2
        d = Dreieck(self.ECKEN, E, 0.2, nu)
        D = steifigkeit_der_platte(E, 0.2, nu)
        u = [x for px, py in self.ECKEN
             for x in (a * px * px + b * px * py + c * py * py, 2 * a * px + b * py, b * px + 2 * c * py)]
        for mx, my, mxy in d.momente(u):
            self.assertAlmostEqual(mx / D, -(2 * a + 2 * nu * c), places=12)
            self.assertAlmostEqual(my / D, -(2 * c + 2 * nu * a), places=12)
            self.assertAlmostEqual(mxy / D, -(1 - nu) * b, places=12)


def navier(x, y, a, b, D, nu, q=Q, glieder=59):
    """Die gelenkige Rechteckplatte a × b unter q als Reihe nach Navier: w, m_x, m_y."""
    w = mx = my = 0.0
    for m in range(1, glieder + 1, 2):
        for n in range(1, glieder + 1, 2):
            al, be = m * math.pi / a, n * math.pi / b
            W = 16.0 * q / (math.pi ** 2 * m * n) / (D * (al ** 2 + be ** 2) ** 2)
            s = math.sin(al * x) * math.sin(be * y)
            w += W * s
            mx += D * W * (al ** 2 + nu * be ** 2) * s
            my += D * W * (be ** 2 + nu * al ** 2) * s
    return {"w": w, "mx": mx, "my": my}


class TestNavier(unittest.TestCase):
    """Die gelenkige Rechteckplatte 6 × 4 m, h = 200 mm, ν = 0.2, q = 10 kN/m², Netz 0.25 m."""

    @classmethod
    def setUpClass(cls):
        ecken = rechteck(6.0, 4.0)
        cls.e = rechnen(Decke(platten=[platte(ecken)], linienlager=ringsum(ecken), lastfaelle=gleichmaessig(),
                              verfahren=Verfahren.FEM, netzweite=0.25))
        cls.D = steifigkeit_der_platte(E, 0.2, 0.2)

    def test_mitte_und_viertel(self):
        for p in ((3.0, 2.0), (1.5, 1.0)):
            soll = navier(*p, 6.0, 4.0, self.D, 0.2)
            for g in ("w", "mx", "my"):
                with self.subTest(ort=p, groesse=g):
                    self.assertAlmostEqual(an(self.e, p, g) / soll[g], 1.0, delta=0.015)

    def test_die_lager_tragen_die_last(self):
        f = self.e.fall("q")
        self.assertAlmostEqual(f.summe, Q * 24.0, places=6)
        self.assertAlmostEqual(f.lagerkraft / f.summe, 1.0, places=9)
        self.assertEqual((f.daneben, f.nicht_getragen), (0.0, 0.0))
        self.assertEqual(self.e.meldungen + f.meldungen, [])
        for name in ("W1", "W2", "W3", "W4"):
            F, stufen = f.linienlager[name]
            self.assertAlmostEqual(sum((ub - ua) * r for ua, ub, r, _ in stufen), F, delta=1e-6 * f.summe)

    def test_in_den_ecken_haelt_das_lager_nieder(self):
        """Nach Kirchhoff hebt sich die gelenkige Platte in den Ecken: dort zieht das Lager."""
        _, stufen = self.e.fall("q").linienlager["W1"]
        self.assertLess(stufen[0][2], 0.0)
        self.assertLess(stufen[-1][2], 0.0)
        self.assertGreater(max(r for _, _, r, _ in stufen), 0.0)


class TestEingespannt(unittest.TestCase):
    """
    Die ringsum eingespannte Quadratplatte a = 4 m, ν = 0.3, Netz 0.25 m --
    nach Timoshenko und Woinowsky-Krieger (Tafel 35): w = 0.00126·q·a⁴/D,
    in der Mitte m = 0.0231·q·a², in der Mitte eines Randes m = −0.0513·q·a².
    """

    @classmethod
    def setUpClass(cls):
        ecken = rechteck(4.0, 4.0)
        cls.e = rechnen(Decke(platten=[platte(ecken, nu=0.3)], linienlager=ringsum(ecken, eingespannt=True),
                              lastfaelle=gleichmaessig(), netzweite=0.25))
        cls.D = steifigkeit_der_platte(E, 0.2, 0.3)

    def test_mitte(self):
        self.assertAlmostEqual(an(self.e, (2.0, 2.0), "w") / (0.00126 * Q * 4.0 ** 4 / self.D), 1.0, delta=0.01)
        self.assertAlmostEqual(an(self.e, (2.0, 2.0), "mx") / (0.0231 * Q * 16.0), 1.0, delta=0.015)

    def test_rand(self):
        self.assertAlmostEqual(an(self.e, (1e-6, 2.0), "mx") / (-0.0513 * Q * 16.0), 1.0, delta=0.02)
        _, stufen = self.e.fall("q").linienlager["W4"]
        (mitte,) = [s for s in stufen if s[0] <= 2.0 <= s[1]][:1]
        self.assertAlmostEqual(mitte[3] / (-0.0513 * Q * 16.0), 1.0, delta=0.03)


class TestKragplatte(unittest.TestCase):
    """
    Kragplatte 2 m weit, 1 m breit, an der Wand eingespannt, ν = 0, Netz
    0.25 m: wie ein Kragbalken -- w = q·L⁴/(8·D) an der Spitze, an der Wand
    m = −q·L²/2 = −20 kNm/m und r = q·L = 20 kN/m.
    """

    @classmethod
    def setUpClass(cls):
        ecken = rechteck(2.0, 1.0)
        cls.e = rechnen(Decke(platten=[platte(ecken, nu=0.0)],
                              linienlager=[Linienlager("W", (0.0, 1.0), (0.0, 0.0), eingespannt=True)],
                              lastfaelle=gleichmaessig(), netzweite=0.25))
        cls.D = steifigkeit_der_platte(E, 0.2, 0.0)

    def test_spitze(self):
        self.assertAlmostEqual(an(self.e, (2.0 - 1e-6, 0.5), "w") / (Q * 2.0 ** 4 / (8.0 * self.D)), 1.0,
                               delta=0.015)

    def test_einspannung(self):
        self.assertAlmostEqual(an(self.e, (1e-6, 0.5), "mx") / -20e3, 1.0, delta=0.04)
        self.assertAlmostEqual(an(self.e, (1.0, 0.5), "mx") / -5e3, 1.0, delta=0.02)

    def test_das_lager(self):
        F, stufen = self.e.fall("q").linienlager["W"]
        self.assertAlmostEqual(F, 20e3, places=3)
        r_max, m_max = spitzen(stufen)
        self.assertAlmostEqual(m_max / -20e3, 1.0, delta=0.03)
        self.assertAlmostEqual(sum((ub - ua) * m for ua, ub, _, m in stufen) / -20e3, 1.0, delta=0.03)


class TestTraeger(unittest.TestCase):
    """
    Ein Plattenstreifen 4 m weit, 0.4 m breit, gelenkig an den Enden, ν = 0,
    q = 10 kN/m²; längs seiner Mitte ein Träger so breit wie er, b = 0.4 m.
    Über die ganze Breite trägt der Träger q·b·L²/8 = 8 kNm und an den Enden
    q·b·L/2 = 8 kN, ob mit Steg oder ohne. Mit h_T = 300 mm trägt der Balken
    davon den Anteil EI_T/(EI_T + b·E·h³/12), EI_T = E·b·((h + h_T)³ − h³)/12.

    Die Querkraft des Balkens ist je Stück gleich, die in seiner Mitte: am
    Lager steht darum die des ersten Stücks, mit dem Netz 0.2 m 7 % unter
    q·b·L/2 -- mit 0.4 m 12 %, mit 0.1 m 3.5 % (offen in TODO).
    """

    @staticmethod
    def gerechnet(h_T):
        ecken = rechteck(4.0, 0.4)
        return rechnen(Decke(
            platten=[platte(ecken, nu=0.0)],
            linienlager=[Linienlager("A", (0.0, 0.0), (0.0, 0.4)), Linienlager("B", (4.0, 0.0), (4.0, 0.4))],
            traeger=[Traeger("T", (0.0, 0.2), (4.0, 0.2), 0.4, hoehe=h_T)],
            lastfaelle=gleichmaessig(), netzweite=0.2))

    def test_ueber_die_ganze_breite(self):
        for h_T in (0.0, 0.3):
            e = self.gerechnet(h_T)
            (u,) = e.decke.traeger
            v = auswertung.traeger(e, e.fall("q"), u)
            _, mitte = min(v.proben, key=lambda x: abs(x[0] - 2.0))
            with self.subTest(h_T=h_T):
                self.assertAlmostEqual(mitte.M / 8e3, 1.0, delta=0.015)
                self.assertAlmostEqual(v.proben[0][1].V / 8e3, 1.0, delta=0.08)
                self.assertAlmostEqual(v.proben[-1][1].V / -8e3, 1.0, delta=0.08)

    def test_der_balken_traegt_nach_seiner_steifigkeit(self):
        e = self.gerechnet(0.3)
        EI = steifigkeit_des_traegers(E, 0.2, 0.4, 0.3)
        self.assertAlmostEqual(EI, E * 0.4 * (0.5 ** 3 - 0.2 ** 3) / 12.0)
        anteil = EI / (EI + 0.4 * E * 0.2 ** 3 / 12.0)
        stueck = next(x for x in e.fall("q").traeger["T"] if x.u_p <= 2.0 <= x.u_q)
        M = stueck.M_p + (stueck.M_q - stueck.M_p) * (2.0 - stueck.u_p) / (stueck.u_q - stueck.u_p)
        self.assertAlmostEqual(M / (anteil * 8e3), 1.0, delta=0.01)

    def test_ohne_steg_kein_balken(self):
        self.assertEqual(self.gerechnet(0.0).fall("q").traeger, {})


class TestSteg(unittest.TestCase):
    """
    Platte 4 × 2 m, h = 200 mm, ringsum gelenkig; längs y = 1 ein Träger
    b = 0.4 m mit h_T = 300 mm. Im Eigengewicht wiegt die Platte 25·0.2·8 =
    40 kN und der Steg 25·0.4·0.3·4 = 12 kN -- in beiden Verfahren.
    """

    @staticmethod
    def decke():
        ecken = rechteck(4.0, 2.0)
        return Decke(platten=[platte(ecken)], linienlager=ringsum(ecken),
                     traeger=[Traeger("T", (0.0, 1.0), (4.0, 1.0), 0.4, hoehe=0.3)],
                     lastfaelle=[Lastfall("g", eigengewicht=True)], netzweite=0.5)

    def test_eine_linienlast(self):
        (steg,) = lasten.stege(self.decke())
        self.assertEqual((steg.name, steg.a, steg.b), ("Eigengewicht T", (0.0, 1.0), (4.0, 1.0)))
        self.assertAlmostEqual(steg.wert, 3e3)

    def test_in_beiden_verfahren(self):
        for rechnung in (rechnen, nach_streifen):
            f = rechnung(self.decke()).fall("g")
            with self.subTest(rechnung=rechnung.__module__):
                self.assertAlmostEqual(f.summe, 52e3, places=6)
                self.assertAlmostEqual(f.lagerkraft, 52e3, delta=1e-3)

    def test_im_bericht_der_streifenmethode(self):
        p = Projekt(name="Steg")
        d = p.decke("Steg")
        d.platte([(0, 0), (4, 0), (4, 2), (0, 2)], beton=p.beton("C30/37"), h=200)
        for a, b in [((0, 0), (4, 0)), ((4, 0), (4, 2)), ((4, 2), (0, 2)), ((0, 2), (0, 0))]:
            d.lager(a, b)
        d.traeger_legen((0, 1), (4, 1), breite=0.4, h_T=300)
        d.standardfaelle()
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.materialziele(), *aufbau.ziele_von(d.kennung))
        (tabelle,) = [b for b in loesung.protokoll.alle_bloecke()
                      if isinstance(b, TabellenBlock) and b.titel.startswith("Lasten")]
        zeilen = [[str(getattr(z, "latex", z)) for z in zeile] for zeile in tabelle.zeilen]
        self.assertIn(["Eigengewicht", "Eigengewicht T1", "(0.00, 1.00) – (4.00, 1.00)", r"3.00\ \mathrm{kN/m}"],
                      zeilen)


class TestGrenzen(unittest.TestCase):
    """Was die FEM nicht rechnet: Teile, die sich frei bewegen könnten, ein zu feines Netz, Zonen."""

    def test_eine_platte_auf_einem_lager(self):
        e = rechnen(Decke(platten=[platte(rechteck(2.0, 1.0))], linienlager=[Linienlager("W", (0, 0), (0, 1))],
                          lastfaelle=gleichmaessig()))
        f = e.fall("q")
        self.assertAlmostEqual(f.nicht_getragen, 20e3, places=3)
        self.assertAlmostEqual(f.lagerkraft, 0.0, delta=1e-6)
        self.assertEqual([m.text for m in f.meldungen],
                         ["Die Platte «P» ist nicht genug gehalten – sie könnte sich frei bewegen. 20 kN fallen aus."])

    def test_ein_zu_feines_netz(self):
        ecken = rechteck(6.0, 4.0)
        e = rechnen(Decke(platten=[platte(ecken)], linienlager=ringsum(ecken), lastfaelle=gleichmaessig(),
                          netzweite=0.05))
        (m,) = e.meldungen
        self.assertTrue(m.fehler)
        self.assertIn(f"mehr als {KNOTEN_HOECHSTENS}", m.text)
        self.assertRegex(m.text, r"Bitte die Netzweite mindestens 0\.\d+ m wählen\.$")
        self.assertIsNone(e.netz)
        self.assertEqual(e.faelle, [])

    def test_zonen_zaehlen_nur_in_der_streifenmethode(self):
        ecken = rechteck(2.0, 2.0)
        e = rechnen(Decke(platten=[platte(ecken)], linienlager=ringsum(ecken), lastfaelle=gleichmaessig(),
                          zonen=[Zone("Z", ((0, 0), (1, 0), (1, 1), (0, 1)), 0.3)]))
        self.assertEqual([(m.text, m.fehler) for m in e.meldungen],
                         [("Die Zone «Z» zählt nur in der Streifenmethode: die FEM teilt die Last nicht auf.", False)])
        self.assertAlmostEqual(e.fall("q").lagerkraft, 40e3, delta=1e-3)


class TestSeite(unittest.TestCase):
    """
    Die zwei Felder mit ihren Lasten nach der FEM, wie die Oberfläche sie
    bekommt: das Netz, je Fall die Probe, die Bilder mit der Durchbiegung --
    und kein Dreieck über den Rand einer Platte.
    """

    @classmethod
    def setUpClass(cls):
        cls.projekt = mit_lasten()
        cls.projekt.decken[0].verfahren = Verfahren.FEM
        cls.uebersicht = zeichnung(cls.projekt).daten["uebersicht"]
        cls.e = bilder(cls.projekt, "GZT").daten["ergebnis"]

    def test_die_uebersicht(self):
        u = self.uebersicht
        self.assertEqual((u["gerechnet"], u["verfahren"]), (True, "fem"))
        self.assertNotIn("anteile", u)
        self.assertEqual(u["netz"]["weite"], 0.5)
        self.assertEqual([t["name"] for t in u["traeger"]], ["T1"])
        for f in u["faelle"]:
            self.assertAlmostEqual(f["lager"], f["summe"], places=6)
            self.assertAlmostEqual(sum(l["F"] for l in f["je_lager"]), f["lager"], places=6)

    def test_kein_dreieck_ueber_den_rand(self):
        netz = self.uebersicht["netz"]
        platten = [[(0, 0), (4, 0), (4, 3), (0, 3)], [(4, 0), (8, 0), (8, 3), (4, 3)]]
        flaechen = [0.0, 0.0]
        for d in netz["dreiecke"]:
            ecken = [netz["knoten"][k] for k in d]
            (i,) = [i for i, p in enumerate(platten) if geo.innen(geo.schwerpunkt(ecken), p)]
            # Auf dem Rand zählt als innen.
            self.assertTrue(all(geo.innen(q, platten[i]) for q in ecken))
            flaechen[i] += geo.flaeche(ecken)
        self.assertEqual([round(a, 6) for a in flaechen], [12.0, 12.0])

    def test_die_bilder(self):
        e = self.e
        self.assertEqual(len(e["zellen"]), len(self.uebersicht["netz"]["dreiecke"]))
        self.assertAlmostEqual(sum(geo.flaeche(z) for z in e["zellen"]), 24.0, places=3)
        self.assertIn("w", e["werte"])
        self.assertEqual(e["einheiten"]["w"], "mm")
        self.assertGreater(e["extreme"]["w"]["groesst"]["wert"], 0.0)
        for g, extrem in e["extreme"].items():
            self.assertLessEqual(max(e["werte"][g]), extrem["groesst"]["wert"] + 1e-3, g)
            self.assertGreaterEqual(min(e["werte"][g]), extrem["kleinst"]["wert"] - 1e-3, g)
        faelle = {f["name"]: f for f in self.uebersicht["faelle"]}
        self.assertAlmostEqual(sum(s["F"] for s in e["stuetzen"]) + sum(l["F"] for l in e["linienlager"]),
                               faelle["GZT"]["lager"], places=3)
        (t,) = e["traeger"]
        self.assertEqual((t["kennung"], t["L"]), ("T1", 3.0))

    def test_die_streifenmethode_hat_keine_durchbiegung(self):
        self.assertNotIn("w", bilder(mit_lasten(), "GZT").daten["ergebnis"]["werte"])
        groessen = {g["wert"]: g["verfahren"] for g in api.katalog()["decke"]["diagrammgroessen"]}
        self.assertEqual(groessen["w"], ["fem"])
        self.assertEqual(groessen["m_x"], ["streifen", "fem"])
        self.assertEqual(groessen["M"], ["streifen", "fem"])


if __name__ == "__main__":
    unittest.main()
