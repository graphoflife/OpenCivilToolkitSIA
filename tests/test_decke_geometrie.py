"""
Die Geometrie der Decke -- Vielecke, Schnitte und die Breite quer zum Streifen.
"""

import math
import unittest

from opencivil.decke import geometrie as geo

QUADRAT = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]
#: Ein L: 4 × 4 ohne das Viertel oben rechts.
EL = [(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 2.0), (2.0, 4.0), (0.0, 4.0)]


class TestVieleck(unittest.TestCase):
    def test_flaeche_und_umlaufsinn(self):
        self.assertAlmostEqual(geo.flaeche(QUADRAT), 4.0)
        self.assertAlmostEqual(geo.flaeche(list(reversed(QUADRAT))), -4.0)
        self.assertAlmostEqual(geo.flaeche(geo.gegen_uhrzeiger(list(reversed(QUADRAT)))), 4.0)

    def test_schwerpunkt_des_l(self):
        x, y = geo.schwerpunkt(EL)
        # Drei Quadrate 2 × 2 mit Mitten (1, 1), (3, 1), (1, 3).
        self.assertAlmostEqual(x, 5.0 / 3.0)
        self.assertAlmostEqual(y, 5.0 / 3.0)

    def test_innen_mit_rand(self):
        self.assertTrue(geo.innen((1.0, 1.0), EL))
        self.assertFalse(geo.innen((3.0, 3.0), EL))
        self.assertTrue(geo.innen((3.0, 2.0), EL), "auf dem Rand zählt als innen")
        self.assertTrue(geo.innen((2.0, 2.0), EL), "die einspringende Ecke")

    def test_ein_l_zerfaellt_in_dreiecke_derselben_flaeche(self):
        stuecke = geo.dreiecke(EL)
        self.assertGreater(len(stuecke), 1)
        self.assertAlmostEqual(sum(geo.flaeche(s) for s in stuecke), 12.0)
        self.assertTrue(all(geo.flaeche(s) > 0.0 for s in stuecke))

    def test_ein_konvexes_bleibt_ganz(self):
        self.assertEqual(len(geo.dreiecke(QUADRAT)), 1)

    def test_punkte_auf_einer_geraden_fallen_weg(self):
        self.assertEqual(len(geo.bereinigt([(0, 0), (1, 0), (2, 0), (2, 2), (2, 2), (0, 2)])), 4)


class TestSchnitte(unittest.TestCase):
    def test_konvexer_schnitt(self):
        c = geo.schnitt(QUADRAT, [(1.0, 1.0), (3.0, 1.0), (3.0, 3.0), (1.0, 3.0)])
        self.assertAlmostEqual(abs(geo.flaeche(c)), 1.0)

    def test_was_sich_nur_beruehrt_schneidet_nicht(self):
        self.assertEqual(geo.schnitt(QUADRAT, [(2.0, 0.0), (3.0, 0.0), (3.0, 2.0), (2.0, 2.0)]), [])

    def test_band(self):
        c = geo.im_band(QUADRAT, (0.0, 1.0), 0.5, 1.5)
        self.assertAlmostEqual(abs(geo.flaeche(c)), 2.0)

    def test_strecke_im_l(self):
        teile = geo.strecke_im_vieleck((-1.0, 3.0), (5.0, 3.0), EL)
        self.assertEqual(len(teile), 1)
        u0, u1 = teile[0]
        self.assertAlmostEqual(-1.0 + 6.0 * u0, 0.0)
        self.assertAlmostEqual(-1.0 + 6.0 * u1, 2.0)

    def test_strecke_auf_dem_rand_zaehlt(self):
        teile = geo.strecke_im_vieleck((0.0, 0.0), (4.0, 0.0), EL)
        self.assertEqual(teile, [(0.0, 1.0)])

    def test_strecke_in_konvex(self):
        u0, u1 = geo.strecke_in_konvex((-1.0, 1.0), (3.0, 1.0), QUADRAT)
        self.assertAlmostEqual(u0, 0.25)
        self.assertAlmostEqual(u1, 0.75)
        self.assertIsNone(geo.strecke_in_konvex((-1.0, 3.0), (3.0, 3.0), QUADRAT))


class TestBreite(unittest.TestCase):
    """Die Breite quer zu ``n`` -- dazwischen linear, ihr Integral die Fläche."""

    @staticmethod
    def integral(verlauf):
        return sum(0.5 * (wa + wb) * (sb - sa) for (sa, wa), (sb, wb) in zip(verlauf, verlauf[1:]))

    def test_rechteck_quer_und_laengs(self):
        verlauf = geo.breite([(0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (0.0, 1.0)], (1.0, 0.0))
        self.assertEqual([s for s, _ in verlauf], [0.0, 3.0])
        self.assertTrue(all(abs(w - 1.0) < 1e-12 for _, w in verlauf), "Randkanten zählen mit ihrer Länge")

    def test_dreieck_waechst_linear(self):
        verlauf = geo.breite([(0.0, 0.0), (2.0, 0.0), (2.0, 2.0)], (1.0, 0.0))
        self.assertEqual(verlauf, [(0.0, 0.0), (2.0, 2.0)])

    def test_schief_das_integral_ist_die_flaeche(self):
        stueck = geo.gegen_uhrzeiger([(0.3, 0.1), (2.2, 0.4), (2.5, 1.9), (0.9, 2.3), (0.1, 1.2)])
        for winkel in (0.0, 0.4, 1.3, math.pi / 2):
            n, _ = geo.richtung(winkel)
            self.assertAlmostEqual(self.integral(geo.breite(stueck, n)), geo.flaeche(stueck), places=12)


if __name__ == "__main__":
    unittest.main()
