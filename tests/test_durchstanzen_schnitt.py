"""
Der Nachweisschnitt um die gestützte Fläche (SIA 262:2025, 4.3.6.2.2 und
4.3.6.2.3): die Fälle der Figuren 22 und 23 gegen ihre Formeln von Hand.
"""

import math
import unittest

from opencivil.durchstanzen.schnitt import (
    Halbebene, Stuetzenflaeche, kandidat_wandecke, kandidat_wandende, kandidaten_stuetze,
    nachweisschnitt,
)

D_V = 0.25


def rechteck(b_x, b_y):
    return Stuetzenflaeche(((-b_x / 2, -b_y / 2), (b_x / 2, -b_y / 2),
                            (b_x / 2, b_y / 2), (-b_x / 2, b_y / 2)))


def schnitt(stuetze, raender=(), aussparungen=()):
    return nachweisschnitt(kandidaten_stuetze(stuetze, D_V / 2, 1.5 * D_V, raender),
                           d_v=D_V, achse=stuetze.achse, aussparungen=aussparungen)


class TestInnenstuetze(unittest.TestCase):
    def test_rechteck(self):
        """Figur 22b: u = 2·(b_x + b_y) + π·d_v."""
        self.assertAlmostEqual(schnitt(rechteck(0.4, 0.4)).u, 1.6 + math.pi * D_V, places=3)

    def test_rund(self):
        """Figur 22a: u = π·(D + d_v)."""
        rund = Stuetzenflaeche(((0.0, 0.0),), 0.2)
        self.assertAlmostEqual(schnitt(rund).u, math.pi * (0.4 + D_V), places=3)

    def test_umschlossene_flaeche(self):
        """Stütze, Streifen der Breite d_v/2 rundum und vier Viertelkreise."""
        n = schnitt(rechteck(0.4, 0.4))
        self.assertAlmostEqual(n.massgebend.flaeche,
                               0.16 + 1.6 * D_V / 2 + math.pi * (D_V / 2) ** 2, places=4)

    def test_grosse_stuetze_zaehlt_nur_neben_den_ecken(self):
        """Figur 23a: von einer Seite über 3·d_v zählen nur 1.5·d_v neben jeder Ecke."""
        n = schnitt(rechteck(1.2, 0.3))
        self.assertAlmostEqual(n.u, 2 * 3 * D_V + 2 * 0.3 + math.pi * D_V, places=3)
        self.assertAlmostEqual(n.massgebend.an_ecken, 2 * (1.2 - 3 * D_V), places=3)


class TestRand(unittest.TestCase):
    def test_am_rand_endet_der_schnitt(self):
        """Figur 22d: drei Seiten und zwei Viertelkreise; die Stütze steht am Rand."""
        rand = Halbebene((0.0, -1.0), 0.2)
        self.assertAlmostEqual(schnitt(rechteck(0.4, 0.4), [rand]).u,
                               3 * 0.4 + math.pi * D_V / 2, places=3)

    def test_zum_rand_nur_wenn_kuerzer(self):
        """Weit weg vom Rand gilt der geschlossene Schnitt, nah am Rand der zum Rand."""
        weit = Halbebene((0.0, -1.0), 0.2 + 2.0)
        self.assertEqual(schnitt(rechteck(0.4, 0.4), [weit]).massgebend.kandidat.name,
                         "geschlossen")
        nah = Halbebene((0.0, -1.0), 0.2 + 0.3)
        n = schnitt(rechteck(0.4, 0.4), [nah])
        self.assertEqual(n.massgebend.kandidat.name, "zum Rand")
        self.assertAlmostEqual(n.u, 2 * (0.4 + 0.3) + 0.4 + math.pi * D_V / 2, places=3)

    def test_ecke(self):
        """Eckstütze in der Ecke: zwei Seiten und ein Viertelkreis."""
        raender = [Halbebene((0.0, -1.0), 0.2), Halbebene((-1.0, 0.0), 0.2)]
        n = schnitt(rechteck(0.4, 0.4), raender)
        self.assertAlmostEqual(n.u, 2 * 0.4 + math.pi * D_V / 4, places=3)
        self.assertEqual(n.massgebend.kandidat.name, "zu beiden Rändern")


class TestWand(unittest.TestCase):
    def test_wandende(self):
        """Figur 23b: das Ende, zwei Viertelkreise und je 1.5·d_v entlang der Wand."""
        k = kandidat_wandende(0.25, D_V / 2, D_V)
        n = nachweisschnitt([k], d_v=D_V, achse=(0.125, 0.0))
        self.assertAlmostEqual(n.u, 0.25 + 3 * D_V + math.pi * D_V / 2, places=3)

    def test_wandecke(self):
        """Figur 23c: ein Viertelkreis um die äussere Ecke und je 1.5·d_v entlang jeder Wand."""
        k = kandidat_wandecke(0.25, D_V / 2, D_V)
        n = nachweisschnitt([k], d_v=D_V, achse=(0.125, 0.125))
        self.assertAlmostEqual(n.u, 3 * D_V + math.pi * D_V / 4, places=3)


class TestAussparung(unittest.TestCase):
    AUSSPARUNG = [(0.5, -0.2), (0.9, -0.2), (0.9, 0.2), (0.5, 0.2)]

    def test_hinter_der_aussparung_zaehlt_nichts(self):
        """
        Figur 23d: die Strahlen von der Achse an den Ecken (0.5; ±0.2) vorbei
        treffen die Seite bei x = 0.325 auf ±0.325·0.4 -- 0.26 m zählen nicht.
        """
        n = schnitt(rechteck(0.4, 0.4), aussparungen=[self.AUSSPARUNG])
        self.assertAlmostEqual(n.massgebend.hinter_aussparungen, 2 * 0.325 * 0.4, places=3)
        self.assertAlmostEqual(n.u, 1.6 + math.pi * D_V - 0.26, places=3)

    def test_weit_weg_mindert_nichts(self):
        """Weiter als 5·d_v vom Schnitt mindert eine Aussparung nicht."""
        weit = [(x + 1.5, y) for x, y in self.AUSSPARUNG]
        self.assertAlmostEqual(schnitt(rechteck(0.4, 0.4), aussparungen=[weit]).u,
                               1.6 + math.pi * D_V, places=3)


if __name__ == "__main__":
    unittest.main()
