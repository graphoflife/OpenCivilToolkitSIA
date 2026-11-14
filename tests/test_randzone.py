"""Der Beton nahe am Rand eines gezeichneten Querschnitts (SIA 262:2025, 4.4.2.3.7)."""

import math
import unittest

from opencivil.querschnitt.geometrie import verschachteln
from opencivil.querschnitt.randzone import flaechen_am_rand


def am_rand(polygone, traegt, abstand=250.0):
    eltern = verschachteln(polygone, [f"P{i}" for i in range(len(polygone))])
    return flaechen_am_rand(polygone, eltern, traegt, abstand)


def rechteck(y0, z0, b, h):
    return [(y0, z0), (y0 + b, z0), (y0 + b, z0 + h), (y0, z0 + h)]


class TestRandzone(unittest.TestCase):
    def test_massiges_rechteck(self):
        """1000 × 2000 mm: alles ausser dem Kern 500 × 1500 mm."""
        [A] = am_rand([rechteck(0, 0, 1000, 2000)], [True])
        self.assertAlmostEqual(A, 1000 * 2000 - 500 * 1500, delta=1e-6)

    def test_duennes_rechteck_ganz(self):
        """400 mm dick: kein Punkt liegt weiter als 200 mm vom Rand."""
        [A] = am_rand([rechteck(0, 0, 400, 2000)], [True])
        self.assertAlmostEqual(A, 400 * 2000, delta=1e-6)

    def test_einspringende_ecke(self):
        """Am L zieht die einspringende Ecke einen Viertelkreis: der Kern wird grösser."""
        L = [(0, 0), (2000, 0), (2000, 1000), (1000, 1000), (1000, 2000), (0, 2000)]
        kern = 1500 * 500 + 500 * 1000 + 250 ** 2 * (1 - math.pi / 4)
        [A] = am_rand([L], [True])
        self.assertAlmostEqual(A / (3e6 - kern), 1.0, delta=1e-4)

    def test_aussparung_hat_einen_rand(self):
        """Hohlkasten 2000 × 2000 mm, Wände 600 mm: auch die Innenseite ist Rand."""
        aussen, loch = rechteck(0, 0, 2000, 2000), rechteck(600, 600, 800, 800)
        kern = 1500 ** 2 - (1300 ** 2 - 4 * 250 ** 2 * (1 - math.pi / 4))
        A, A_loch = am_rand([aussen, loch], [True, False])
        self.assertAlmostEqual(A / (2000 ** 2 - 800 ** 2 - kern), 1.0, delta=1e-4)
        self.assertEqual(A_loch, 0.0)

    def test_zwei_betone_ohne_rand_dazwischen(self):
        """Zwei Lagen von je 400 mm: wo sie sich berühren, ist kein Rand."""
        unten, oben = rechteck(0, 0, 1000, 400), rechteck(0, 400, 1000, 400)
        A_u, A_o = am_rand([unten, oben], [True, True])
        self.assertAlmostEqual(A_u, 400 * 1000 - 500 * 150, delta=1e-6)
        self.assertAlmostEqual(A_o, A_u, delta=1e-6)

    def test_kern_aus_anderem_beton(self):
        """Ein Kern im Innern liegt ganz weiter als 250 mm vom Rand: er zählt nicht."""
        A, A_kern = am_rand([rechteck(0, 0, 1000, 2000), rechteck(300, 300, 400, 1400)],
                            [True, True])
        self.assertAlmostEqual(A, 1000 * 2000 - 500 * 1500, delta=1e-6)
        self.assertAlmostEqual(A_kern, 0.0, delta=1e-6)


if __name__ == "__main__":
    unittest.main()
