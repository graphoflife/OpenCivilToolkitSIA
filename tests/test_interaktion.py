"""
Bruchzustand gezeichneter Querschnitte -- gerade und schief.

Der wichtigste Prüfstein steht zuerst: ein Rechteck mit zwei Lagen ist eine
Platte, und dafür gibt es schon eine genaue Linie
(:mod:`opencivil.nachweis.dehnungsfaecher`). Zwei unabhängig gebaute Wege
müssen dasselbe ergeben. Danach Symmetrie, die Probe jedes Bruchzustands und
Fälle, die sich von Hand nachrechnen lassen.
"""

import math
import unittest

from opencivil.nachweis import dehnungsfaecher, linie
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.interaktion import (
    Bewehrung, Querschnitt, Teil, Werkstoff, linie_als_bewehrung,
)
from opencivil.querschnitt.werkstoffgesetz import Betongesetz, Spannungsblock, Stahlgesetz

BETON = Betongesetz(f_cd=20e6, eps_c1d=0.002, eps_c2d=0.003, k_sigma=2.0)
STAHL = Stahlgesetz(E_s=200e9, f_yd=435e6, f_yd_druck=435e6, eps_ud=0.045)
WERKSTOFFE = [
    Werkstoff("Beton", BETON.spannung, -0.003, math.inf, c_punkt=(0.002, 0.003),
              verdraengbar=True),
    Werkstoff("Stahl", STAHL.spannung, -0.045, 0.045),
]


def rechteck(y0, z0, b, h):
    return ((y0, z0), (y0 + b, z0), (y0 + b, z0 + h), (y0, z0 + h))


def querschnitt(teile, staebe, bezug=None):
    if bezug is None:
        w = geo.summe([(1.0 if t.werkstoff is not None else -1.0,
                        geo.flaechenwerte(t.punkte)) for t in teile])
        bezug = (w.y_S, w.z_S)
    return Querschnitt(werkstoffe=WERKSTOFFE, teile=teile, bewehrung=staebe, bezug=bezug)


class TestWieDiePlatte(unittest.TestCase):
    """1000×250 mit zwei Lagen -- gegen die genaue Linie der Platte."""

    h, b = 0.25, 1.0

    def setUp(self):
        self.platte = dehnungsfaecher.aufbauen(
            h=self.h, b=self.b, beton=BETON,
            lagen=[(1131e-6, 0.215, STAHL, "unten"), (565e-6, 0.035, STAHL, "oben")])
        self.neu = querschnitt(
            [Teil(rechteck(0, 0, self.b, self.h), 0, None)],
            [Bewehrung((0.5, self.h - 0.215), 1131e-6, 1, 0),
             Bewehrung((0.5, self.h - 0.035), 565e-6, 1, 0)])

    def test_momente_bei_n_null(self):
        alt = linie.schnitte(self.platte, linie.MOMENT, 0.0)
        unten = self.neu.bei_normalkraft(-math.pi / 2, 0.0)  # Zug unten
        oben = self.neu.bei_normalkraft(math.pi / 2, 0.0)    # Zug oben
        self.assertAlmostEqual(unten.M_y / max(alt), 1.0, delta=1e-4)
        self.assertAlmostEqual(oben.M_y / min(alt), 1.0, delta=1e-4)
        self.assertAlmostEqual(unten.M_z, 0.0, delta=1e-6)

    def test_reine_normalkraft(self):
        zug, druck = self.neu.normalkraft_grenzen()
        self.assertAlmostEqual(zug / max(p.N for p in self.platte), 1.0, delta=1e-9)
        self.assertAlmostEqual(druck / min(p.N for p in self.platte), 1.0, delta=1e-9)

    def test_mit_druck_innert_einem_promille(self):
        """Die alte Linie interpoliert zwischen Stützstellen, die neue sucht genau."""
        for N in (-2000e3, -500e3, 300e3):
            alt = max(linie.schnitte(self.platte, linie.MOMENT, N))
            neu = self.neu.bei_normalkraft(-math.pi / 2, N)
            self.assertAlmostEqual(neu.N, N, delta=1e-3)
            self.assertAlmostEqual(neu.M_y / alt, 1.0, delta=1e-3, msg=f"N = {N}")

    def test_faecher_von_zug_nach_druck(self):
        punkte = self.neu.faecher(-math.pi / 2)
        zug, druck = self.neu.normalkraft_grenzen()
        self.assertAlmostEqual(punkte[0].N, zug)
        self.assertAlmostEqual(punkte[-1].N, druck)
        self.assertTrue(all(p.chi >= 0.0 for p in punkte))

    def test_probe_der_anteile(self):
        """Was in der Herleitung steht, muss sich zu N und M summieren."""
        punkt = self.neu.bei_normalkraft(-math.pi / 2, -500e3)
        anteile = self.neu.anteile(punkt)
        y_S, z_S = self.neu.bezug
        self.assertAlmostEqual(sum(a.N for a in anteile), punkt.N, delta=1e-3)
        self.assertAlmostEqual(sum(-a.N * (a.z - z_S) for a in anteile), punkt.M_y, delta=1e-3)
        self.assertAlmostEqual(sum(-a.N * (a.y - y_S) for a in anteile), punkt.M_z, delta=1e-3)

    def test_druckzone(self):
        x, d = self.neu.druckzone(self.neu.bei_normalkraft(-math.pi / 2, 0.0))
        self.assertAlmostEqual(d, 0.215, delta=1e-9)
        self.assertTrue(0.0 < x < 0.25 * d)


class TestSchief(unittest.TestCase):

    def stuetze(self):
        a = 0.4
        return querschnitt(
            [Teil(rechteck(0, 0, a, a), 0, None)],
            [Bewehrung((y, z), 491e-6, 1, 0) for y in (0.05, 0.35) for z in (0.05, 0.35)])

    def test_quadrat_ist_in_beiden_achsen_gleich(self):
        s = self.stuetze()
        um_y = s.in_richtung(-800e3, 100e3, 0.0)
        um_z = s.in_richtung(-800e3, 0.0, 100e3)
        self.assertAlmostEqual(um_y.moment / um_z.moment, 1.0, delta=1e-6)
        self.assertAlmostEqual(um_y.M_z, 0.0, delta=1e-3)

    def test_vorzeichen(self):
        """M_y > 0 zieht unten, M_z > 0 zieht links."""
        s = self.stuetze()
        punkt = s.in_richtung(0.0, 100e3, 0.0)
        self.assertGreater(s.dehnung(punkt, (0.2, 0.0)), 0.0)
        punkt = s.in_richtung(0.0, 0.0, 100e3)
        self.assertGreater(s.dehnung(punkt, (0.0, 0.2)), 0.0)
        self.assertLess(s.dehnung(punkt, (0.4, 0.2)), 0.0)

    def test_schraeg_trifft_die_richtung_und_ist_kleiner(self):
        s = self.stuetze()
        gerade = s.in_richtung(-800e3, 100e3, 0.0).moment
        schraeg = s.in_richtung(-800e3, 100e3, 100e3)
        self.assertAlmostEqual(math.atan2(schraeg.M_z, schraeg.M_y), math.pi / 4, delta=1e-6)
        self.assertLess(schraeg.moment, gerade)

    def test_l_dreht_die_nulllinie(self):
        """Beim L steht die Nulllinie für reines M_y nicht waagrecht."""
        l_form = ((0, 0), (0.6, 0), (0.6, 0.15), (0.15, 0.15), (0.15, 0.6), (0, 0.6))
        l = querschnitt([Teil(l_form, 0, None)],
                        [Bewehrung((0.05, 0.05), 314e-6, 1, 0),
                         Bewehrung((0.55, 0.05), 314e-6, 1, 0),
                         Bewehrung((0.05, 0.55), 314e-6, 1, 0)])
        for M_y, M_z in ((50e3, 0.0), (0.0, 50e3), (50e3, -50e3)):
            punkt = l.in_richtung(-300e3, M_y, M_z)
            self.assertAlmostEqual(punkt.N, -300e3, delta=1e-2)
            fehler = math.remainder(math.atan2(punkt.M_z, punkt.M_y)
                                    - math.atan2(M_z, M_y), 2 * math.pi)
            self.assertLess(abs(fehler), 1e-6)
        gerade = l.in_richtung(-300e3, 50e3, 0.0)
        self.assertGreater(abs(math.degrees(gerade.psi) + 90.0), 10.0)

    def test_jenseits_der_normalkraft_nichts(self):
        s = self.stuetze()
        _, druck = s.normalkraft_grenzen()
        self.assertIsNone(s.in_richtung(1.01 * druck, 100e3, 0.0))


class TestVonHand(unittest.TestCase):

    def test_ohne_bewehrung_kein_zug(self):
        nackt = querschnitt([Teil(rechteck(0, 0, 0.3, 0.5), 0, None)], [])
        zug, druck = nackt.normalkraft_grenzen()
        self.assertAlmostEqual(zug, 0.0)
        self.assertAlmostEqual(druck, -20e6 * 0.3 * 0.5, delta=1.0)

    def test_aussparung_zaehlt_nicht(self):
        voll = querschnitt([Teil(rechteck(0, 0, 0.6, 0.8), 0, None)], [])
        kasten = querschnitt([Teil(rechteck(0, 0, 0.6, 0.8), 0, None),
                              Teil(rechteck(0.15, 0.15, 0.3, 0.5), None, 0)], [])
        self.assertAlmostEqual(voll.normalkraft_grenzen()[1] - kasten.normalkraft_grenzen()[1],
                               -20e6 * 0.3 * 0.5, delta=1.0)

    def test_druck_mit_staeben(self):
        """Gleichmässig -eps_c1d: Beton bei f_cd, Stahl elastisch bei E_s·eps_c1d."""
        s = querschnitt([Teil(rechteck(0, 0, 0.4, 0.4), 0, None)],
                        [Bewehrung((y, z), 491e-6, 1, 0) for y in (0.05, 0.35) for z in (0.05, 0.35)])
        a_s = 4 * 491e-6
        erwartet = -20e6 * (0.16 - a_s) - a_s * 200e9 * 0.002
        self.assertAlmostEqual(s.normalkraft_grenzen()[1] / erwartet, 1.0, delta=1e-9)

    def test_verschmierte_linie_wie_einzelstaebe(self):
        teil = Teil(rechteck(0, 0, 1.0, 0.3), 0, None)
        staebe = querschnitt([teil], [Bewehrung((0.05 + 0.1 * k, 0.04), 1500e-6 / 10, 1, 0)
                                      for k in range(10)])
        linie_ = querschnitt([teil], linie_als_bewehrung((0.0, 0.04), (1.0, 0.04),
                                                         1500e-6, 1, 0))
        a = staebe.bei_normalkraft(-math.pi / 2, 0.0).M_y
        b = linie_.bei_normalkraft(-math.pi / 2, 0.0).M_y
        self.assertAlmostEqual(a / b, 1.0, delta=1e-3)


if __name__ == "__main__":
    unittest.main()


class TestSpannungsblock(unittest.TestCase):
    """
    Der Block springt bei 0.15·ε_c2d von null auf f_cd. In der Mitte jeder
    Faser gelesen, sprang darum auch N -- am Kastenträger des vollen Berichts
    stand in der Probe 638.7 kN, nachgewiesen wurden 664.0 kN. Über die Faser
    gemittelt, wächst N stetig, und jede verlangte Normalkraft wird getroffen.
    """

    def setUp(self):
        block = Spannungsblock(f_cd=20e6, eps_c2d=0.003)
        werkstoffe = [
            Werkstoff("Beton", block, -0.003, math.inf, c_punkt=(0.002, 0.003),
                      verdraengbar=True),
            Werkstoff("Stahl", STAHL.spannung, -0.045, 0.045),
        ]
        # Ein Kasten mit Loch und Stäben im Beton: Fasern und verdrängtes
        # Material springen beide.
        teile = [Teil(rechteck(0, 0, 0.8, 0.6), 0, None),
                 Teil(rechteck(0.15, 0.15, 0.5, 0.3), None, 0)]
        staebe = [Bewehrung((y, z), 314e-6, 1, 0)
                  for y in (0.05, 0.4, 0.75) for z in (0.05, 0.55)]
        w = geo.summe([(1.0, geo.flaechenwerte(teile[0].punkte)),
                       (-1.0, geo.flaechenwerte(teile[1].punkte))])
        self.q = Querschnitt(werkstoffe=werkstoffe, teile=teile, bewehrung=staebe,
                             bezug=(w.y_S, w.z_S))

    def test_mittel_ist_der_anteil_ueber_dem_knick(self):
        block = Spannungsblock(f_cd=20e6, eps_c2d=0.003)
        knick = -block.eps_knick                       # -0.45 ‰
        self.assertEqual(block.mittel(-0.001, -0.002), -20e6)
        self.assertEqual(block.mittel(0.001, -0.0001), 0.0)
        self.assertAlmostEqual(block.mittel(knick + 0.0001, knick - 0.0001), -10e6)
        self.assertAlmostEqual(block.mittel(knick - 0.0003, knick + 0.0001), -15e6)
        self.assertEqual(block.mittel(-0.001, -0.001), block(-0.001))

    def test_jede_normalkraft_wird_getroffen(self):
        zug, druck = self.q.normalkraft_grenzen()
        for psi in (-math.pi / 2, -2.0, 0.3):
            for anteil in (0.9, 0.5, 0.1, -0.2, -0.6, -0.95):
                N = anteil * (zug if anteil > 0 else -druck)
                punkt = self.q.bei_normalkraft(psi, N)
                with self.subTest(psi=psi, N=N):
                    self.assertAlmostEqual(punkt.N, N, delta=1e-3)
                    self.assertAlmostEqual(sum(a.N for a in self.q.anteile(punkt)), N, delta=1e-3)
