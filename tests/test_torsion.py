"""
I_T eines gezeichneten Querschnitts, numerisch (opencivil/querschnitt/torsion.py):
gegen die genauen Werte von Rechteck, Dreieck, Kreis und Rohr, gegen Bredt beim
duennen Hohlkasten -- und was Hohlraum, Insel, getrennte Teile und schraege
Waende mit dem Gitter machen.
"""

import math
import unittest

from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.torsion import TEILUNG, torsion


def rechteck(b, h, y=0.0, z=0.0):
    return [(y, z), (y + b, z), (y + b, z + h), (y, z + h)]


def kreis(r, ecken=200):
    return [(r * math.cos(2 * math.pi * k / ecken), r * math.sin(2 * math.pi * k / ecken))
            for k in range(ecken)]


def gedreht(punkte, grad):
    c, s = math.cos(math.radians(grad)), math.sin(math.radians(grad))
    return [(y * c - z * s, y * s + z * c) for y, z in punkte]


def rechteck_genau(b, t):
    """I_T des Rechtecks aus der Reihe von St. Venant -- t die kuerzere Seite."""
    b, t = max(b, t), min(b, t)
    reihe = sum(math.tanh(n * math.pi * b / (2 * t)) / n ** 5 for n in range(1, 200, 2))
    return (1 - 192 / math.pi ** 5 * t / b * reihe) * b * t ** 3 / 3


def I_T(*polygone, traegt=None):
    """``I_T`` der Polygone, verschachtelt wie in einer Zeichnung; ohne Angabe traegt jedes."""
    traegt = traegt or [True] * len(polygone)
    eltern = geo.verschachteln(polygone, [f"P{i}" for i in range(len(polygone))])
    return torsion(polygone, traegt, eltern)


class TestGegenGenaueWerte(unittest.TestCase):
    def assertNahe(self, ist, soll, promille):
        self.assertAlmostEqual(ist / soll, 1.0, delta=promille / 1000)

    def test_rechtecke(self):
        """Das Gitter liegt auf den Kanten; ein schmales rechnet es feiner."""
        for b, h in ((1000, 1000), (1000, 250), (1000, 100)):
            with self.subTest(b=b, h=h):
                self.assertNahe(I_T(rechteck(b, h)).I_T, rechteck_genau(b, h), 0.1)

    def test_gleichseitiges_dreieck(self):
        """Schraege Kanten, genau geschnitten: a⁴·√3/80."""
        a = 1000.0
        t = I_T([(0, 0), (a, 0), (a / 2, a * math.sqrt(3) / 2)])
        self.assertNahe(t.I_T, a ** 4 * math.sqrt(3) / 80, 0.1)

    def test_kreis_und_rohr(self):
        """π·r⁴/2 und π·(R⁴ − r⁴)/2 -- das 200-Eck hat etwas weniger Fläche als der Kreis."""
        self.assertNahe(I_T(kreis(500)).I_T, math.pi * 500 ** 4 / 2, 0.5)
        rohr = I_T(kreis(500), kreis(450), traegt=[True, False])
        self.assertNahe(rohr.I_T, math.pi * (500 ** 4 - 450 ** 4) / 2, 1.0)
        self.assertEqual(len(rohr.fein.hohlraeume), 1)

    def test_duenner_hohlkasten_wie_bredt(self):
        """
        Wand 10 mm, 1000 mm breit: 4·A_m²/∮(ds/t) mit der Mittellinie. Die dicke
        Wand gibt etwas dazu, bei t/b = 1/100 gut ein halbes Prozent.
        """
        t = I_T(rechteck(1000, 1000), rechteck(980, 980, 10, 10), traegt=[True, False])
        bredt = 4 * 990 ** 4 / (4 * 990 / 10)
        self.assertGreater(t.I_T, bredt)
        self.assertNahe(t.I_T, bredt, 10)
        self.assertEqual(t.fein.hohlraeume, (980 * 980,))

    def test_gedreht_wie_gerade(self):
        """Um 30° gedreht ist das Rechteck dasselbe: kein Gitter liegt mehr auf einer Kante."""
        self.assertNahe(I_T(gedreht(rechteck(1000, 250), 30)).I_T, rechteck_genau(1000, 250), 0.5)

    def test_eine_duenne_schraege_wand_rechnet_feiner(self):
        """1000 × 20 mm um 45°: das grobe Gitter ist zu grob, gerechnet wird feiner."""
        t = I_T(gedreht(rechteck(1000, 20), 45))
        self.assertGreater(t.grob.spalten, TEILUNG)
        self.assertNahe(t.I_T, rechteck_genau(1000, 20), 10)


class TestTeileUndHohlraeume(unittest.TestCase):
    KASTEN = (rechteck(1000, 1000), rechteck(800, 800, 100, 100))

    def kasten(self):
        return I_T(*self.KASTEN, traegt=[True, False]).I_T

    def test_getrennte_teile_tragen_je_fuer_sich(self):
        t = I_T(rechteck(400, 400), rechteck(300, 600, 600, 0))
        self.assertAlmostEqual(t.I_T / (rechteck_genau(400, 400) + rechteck_genau(300, 600)),
                               1.0, delta=1e-4)

    def test_eine_insel_im_hohlraum(self):
        """Sie zaehlt zur Flaeche des Hohlraums, traegt aber fuer sich -- mit φ = 0 an ihrem Rand."""
        t = I_T(*self.KASTEN, rechteck(200, 200, 400, 400), traegt=[True, False, True])
        self.assertAlmostEqual(t.I_T / (self.kasten() + rechteck_genau(200, 200)), 1.0,
                               delta=1e-4)
        self.assertEqual(t.fein.hohlraeume, (800 * 800,))

    def test_zwei_polygone_die_sich_beruehren_sind_ein_kasten(self):
        links = [(0, 0), (500, 0), (500, 100), (100, 100), (100, 900), (500, 900), (500, 1000),
                 (0, 1000)]
        rechts = [(500, 0), (1000, 0), (1000, 1000), (500, 1000), (500, 900), (900, 900),
                  (900, 100), (500, 100)]
        self.assertAlmostEqual(I_T(links, rechts).I_T / self.kasten(), 1.0, delta=1e-9)

    def test_eine_aussparung_am_rand_ist_kein_hohlraum(self):
        """Offen nach oben: ein U, so steif wie dasselbe U als ein Polygon."""
        kerbe = I_T(rechteck(1000, 1000), rechteck(800, 900, 100, 100), traegt=[True, False])
        u = I_T([(0, 0), (1000, 0), (1000, 1000), (900, 1000), (900, 100), (100, 100),
                 (100, 1000), (0, 1000)])
        self.assertEqual(kerbe.fein.hohlraeume, ())
        self.assertAlmostEqual(kerbe.I_T / u.I_T, 1.0, delta=1e-9)
        self.assertLess(kerbe.I_T, self.kasten() / 50)


if __name__ == "__main__":
    unittest.main()
