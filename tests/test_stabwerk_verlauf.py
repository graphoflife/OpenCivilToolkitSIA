"""
Schnittgrössen und Biegelinie längs der Stäbe -- gegen Handrechnungen.

Vorzeichen der Baustatik: N > 0 Zug, M > 0 zieht an der gestrichelten Faser
(bei einem Stab von links nach rechts unten), dM/dx = V − m.
"""

import math
import unittest

from opencivil.stabwerk.modell import (
    FEST, Knoten, Knotenlast, Lager, Lastart, Lastfall, Stab, Stablast, System,
)
from opencivil.stabwerk.system import rechnen
from opencivil.stabwerk.verlauf import Polynom, verlaeufe

EI, EA = 50e6, 5e9
q = 10e3
L = 6.0


def einfeldtraeger(*lasten, **stabfelder):
    s = System(
        knoten=[Knoten("K1", 0, 0), Knoten("K2", L, 0)],
        staebe=[Stab("L1", "K1", "K2", EA=EA, EI=EI, **stabfelder)],
        lager=[Lager("A1", "K1", x=FEST, z=FEST), Lager("A2", "K2", z=FEST)],
        lastfaelle=[Lastfall("LF", list(lasten))])
    e = rechnen(s)
    assert e.gueltig, [m.text for m in e.meldungen]
    return verlaeufe(e.faelle[0])["L1"]


class TestPolynom(unittest.TestCase):
    def test_rechnen(self):
        p = Polynom((1.0, 2.0)) * Polynom((0.0, 1.0))      # x + 2x²
        self.assertEqual(p(2.0), 10.0)
        self.assertEqual(p.ableitung()(2.0), 9.0)
        self.assertAlmostEqual(p.stammfunktion(1.0)(2.0), (2 + 16 / 3) - (0.5 + 2 / 3))

    def test_nullstellen(self):
        p = Polynom((-2.0, 0.0, 1.0))                       # x² − 2
        self.assertAlmostEqual(p.nullstellen(0.0, 3.0)[0], math.sqrt(2), places=12)
        self.assertEqual(Polynom((5.0,)).nullstellen(0.0, 1.0), [])


class TestEinfeldtraeger(unittest.TestCase):
    def setUp(self):
        self.v = einfeldtraeger(Stablast("L1", Lastart.LINIENLAST, q))

    def test_feldmoment_und_querkraft(self):
        self.assertAlmostEqual(self.v.bei(L / 2)["M"], q * L * L / 8, places=5)
        self.assertAlmostEqual(self.v.bei(0.0)["V"], q * L / 2, places=6)
        self.assertAlmostEqual(self.v.bei(L)["V"], -q * L / 2, places=6)
        self.assertAlmostEqual(self.v.bei(0.0)["N"], 0.0, places=6)

    def test_extrem_bei_v_gleich_null(self):
        groesst = self.v.extrem("M").groesst
        self.assertAlmostEqual(groesst[0], L / 2, places=9)
        self.assertAlmostEqual(groesst[1], q * L * L / 8, places=5)

    def test_durchbiegung(self):
        """5qL⁴/384EI, zur gestrichelten Faser hin positiv."""
        w = self.v.extrem("w").groesst
        self.assertAlmostEqual(w[1], 5 * q * L ** 4 / (384 * EI), places=12)
        self.assertAlmostEqual(w[0], L / 2, places=6)

    def test_die_biegelinie_trifft_das_ende(self):
        self.assertAlmostEqual(self.v.bei(L)["v"], 0.0, places=15)

    def test_verdrehung(self):
        """qL³/24EI an den Lagern, links im Uhrzeigersinn -- in der Mitte null."""
        phi = self.v.extrem("phi")
        self.assertAlmostEqual(phi.kleinst[1], -q * L ** 3 / (24 * EI), places=12)
        self.assertAlmostEqual(phi.kleinst[0], 0.0, places=9)
        self.assertAlmostEqual(phi.groesst[1], q * L ** 3 / (24 * EI), places=12)
        self.assertAlmostEqual(self.v.bei(L / 2)["phi"], 0.0, places=12)


class TestLasten(unittest.TestCase):
    def test_teilstrecke(self):
        """Gleichlast auf 1 bis 3 m: A = 4/6 · 2q, M(2 m) = 2·A − q/2."""
        v = einfeldtraeger(Stablast("L1", Lastart.LINIENLAST, q, von=1.0, bis=3.0))
        A = 4.0 / 6.0 * 2 * q
        self.assertAlmostEqual(v.bei(0.0)["V"], A, places=6)
        self.assertAlmostEqual(v.bei(2.0)["M"], 2 * A - q / 2, places=6)

    def test_dreieck(self):
        """Von 0 auf q: max M = qL²/(9√3) bei x = L/√3."""
        v = einfeldtraeger(Stablast("L1", Lastart.LINIENLAST, 0.0, wert_b=q))
        x, m = v.extrem("M").groesst
        self.assertAlmostEqual(x, L / math.sqrt(3), places=9)
        self.assertAlmostEqual(m, q * L * L / (9 * math.sqrt(3)), places=5)

    def test_einzelmoment_springt(self):
        """M0 im Gegenuhrzeigersinn in der Mitte: V = M0/L, M springt von M0/2 auf −M0/2."""
        M0 = 12e3
        v = einfeldtraeger(Stablast("L1", Lastart.MOMENT, M0, von=L / 2))
        self.assertAlmostEqual(v.bei(1.0)["V"], M0 / L, places=6)
        self.assertAlmostEqual(v.bei(L / 2, links=True)["M"], M0 / 2, places=6)
        self.assertAlmostEqual(v.bei(L / 2)["M"], -M0 / 2, places=6)

    def test_gleichmaessiges_moment_biegt_nicht(self):
        """Ein Moment m je Länge auf dem Einfeldträger: V = m überall, M = 0."""
        m = 3e3
        v = einfeldtraeger(Stablast("L1", Lastart.LINIENMOMENT, m))
        for x in (0.5, 3.0, 5.5):
            self.assertAlmostEqual(v.bei(x)["V"], m, places=6)
            self.assertAlmostEqual(v.bei(x)["M"], 0.0, places=6)

    def test_einzelkraft_springt(self):
        P = 20e3
        v = einfeldtraeger(Stablast("L1", Lastart.EINZELLAST, P, von=2.0))
        self.assertAlmostEqual(v.bei(2.0, links=True)["V"] - v.bei(2.0)["V"], P, places=6)
        self.assertAlmostEqual(v.bei(2.0)["M"], P * 2.0 * 4.0 / L, places=6)


class TestGelenk(unittest.TestCase):
    def test_einseitig_eingespannt(self):
        """Links eingespannt, rechts gelenkig angeschlossen: −qL²/8 und qL³/(48EI) am Gelenk."""
        s = System(
            knoten=[Knoten("K1", 0, 0), Knoten("K2", L, 0)],
            staebe=[Stab("L1", "K1", "K2", EA=EA, EI=EI, gelenk_b=True)],
            lager=[Lager("A1", "K1", x=FEST, z=FEST, phi=FEST),
                   Lager("A2", "K2", x=FEST, z=FEST, phi=FEST)],
            lastfaelle=[Lastfall("q", [Stablast("L1", Lastart.LINIENLAST, q)])])
        e = rechnen(s)
        f = e.faelle[0]
        v = verlaeufe(f)["L1"]
        self.assertAlmostEqual(v.bei(0.0)["M"], -q * L * L / 8, places=5)
        self.assertAlmostEqual(v.bei(L)["M"], 0.0, places=6)
        # Die Drehung des Stabendes am Gelenk, im Gegenuhrzeigersinn.
        self.assertAlmostEqual(f.teile[0].d[5], q * L ** 3 / (48 * EI), places=12)


class TestBettung(unittest.TestCase):
    def test_gleichlast_biegt_nicht(self):
        k = 5e6
        s = System(
            knoten=[Knoten("K1", 0, 0), Knoten("K2", 10, 0)],
            staebe=[Stab("L1", "K1", "K2", EA=EA, EI=EI, quer=k)],
            lager=[Lager("A1", "K1", x=FEST)],
            lastfaelle=[Lastfall("q", [Stablast("L1", Lastart.LINIENLAST, q)])])
        v = verlaeufe(rechnen(s).faelle[0])["L1"]
        for x in (0.0, 2.5, 5.0, 9.9):
            self.assertAlmostEqual(v.bei(x)["M"], 0.0, delta=1e-6 * q)
            self.assertAlmostEqual(v.bei(x)["uz"], -q / k, delta=1e-12)


class TestStetig(unittest.TestCase):
    def test_ueber_den_t_stoss(self):
        """Wo der Stab geteilt ist und keine Last steht, laufen N, V und M weiter."""
        s = System(
            knoten=[Knoten("K1", 0, 0), Knoten("K2", L, 0), Knoten("K3", 2, 0), Knoten("K4", 2, 2)],
            staebe=[Stab("L1", "K1", "K2", EA=EA, EI=EI)],
            lager=[Lager("A1", "K1", x=FEST, z=FEST), Lager("A2", "K2", z=FEST)],
            lastfaelle=[Lastfall("q", [Stablast("L1", Lastart.LINIENLAST, q)])])
        v = verlaeufe(rechnen(s).faelle[0])["L1"]
        self.assertGreater(len(v.intervalle), 1)
        for groesse in ("N", "V", "M", "v"):
            self.assertAlmostEqual(v.bei(2.0, links=True)[groesse], v.bei(2.0)[groesse], places=6)

    def test_proben_mit_extremwert(self):
        v = einfeldtraeger(Stablast("L1", Lastart.LINIENLAST, q))
        proben = v.proben()
        self.assertAlmostEqual(max(p["M"] for p in proben), q * L * L / 8, places=5)
        self.assertEqual(proben[0]["x"], 0.0)
        self.assertEqual(proben[-1]["x"], L)


class TestGeneigt(unittest.TestCase):
    def test_normalkraft_im_schraegen_stab(self):
        """
        Ein Pendel unter 45° trägt eine senkrechte Last als Druck: N = −P·√2.
        Es schiebt den Knoten dabei um P nach rechts, und der waagrechte Stab
        schiebt ihn zurück -- auch er unter Druck, N = −P.
        """
        P = 10e3
        s = System(
            knoten=[Knoten("A", 0, 0), Knoten("B", 2, 2), Knoten("C", 4, 2)],
            staebe=[Stab("L1", "A", "B", EA=EA, EI=EI, gelenk_a=True, gelenk_b=True),
                    Stab("L2", "C", "B", EA=EA, EI=EI, gelenk_a=True, gelenk_b=True)],
            lager=[Lager("A1", "A", x=FEST, z=FEST), Lager("A2", "C", x=FEST, z=FEST)],
            lastfaelle=[Lastfall("P", [Knotenlast("B", Fz=-P)])])
        v = verlaeufe(rechnen(s).faelle[0])
        self.assertAlmostEqual(v["L1"].bei(1.0)["N"], -P * math.sqrt(2), places=4)
        self.assertAlmostEqual(v["L2"].bei(1.0)["N"], -P, places=4)
        self.assertAlmostEqual(v["L1"].bei(1.0)["M"], 0.0, places=6)


if __name__ == "__main__":
    unittest.main()
