"""
Ein Streifen als Durchlaufträger -- gegen Handrechnungen.

Vorzeichen: Lasten nach unten positiv, Lagerkräfte nach oben, Lagermomente im
Gegenuhrzeigersinn; ``M > 0`` zieht unten.
"""

import unittest

from opencivil.decke.traeger import Balken, Einzellast, Halt, Streckenlast, extreme, statik, wert

q = 10e3
EI = 1e7


def balken(L, *halte, abschnitte=None):
    return Balken(L, abschnitte or [(0.0, L, EI)], list(halte))


class TestElastisch(unittest.TestCase):
    def test_einfeldtraeger(self):
        F = balken(6.0, Halt(0.0, True, False), Halt(6.0, True, False)).lagerkraefte(
            [Streckenlast(0.0, 6.0, q, q)])
        self.assertAlmostEqual(F[0][0], 3.0 * q)
        self.assertAlmostEqual(F[1][0], 3.0 * q)

    def test_eingespannt_und_gelenkig(self):
        """Am Gelenk 3qL/8, an der Einspannung 5qL/8 und qL²/8 im Gegenuhrzeigersinn."""
        L = 4.0
        F = balken(L, Halt(0.0, True, True), Halt(L, True, False)).lagerkraefte([Streckenlast(0.0, L, q, q)])
        self.assertAlmostEqual(F[0][0], 5.0 * q * L / 8.0)
        self.assertAlmostEqual(F[0][1], q * L * L / 8.0)
        self.assertAlmostEqual(F[1][0], 3.0 * q * L / 8.0)

    def test_zweifeldtraeger_ungleich_und_ungleich_steif(self):
        """Dreimomentengleichung mit ``l/EI``: Felder 4 m und 6 m, das zweite 3.375-mal steifer."""
        l1, l2, k = 4.0, 6.0, 3.375
        b = balken(l1 + l2, Halt(0.0, True, False), Halt(l1, True, False), Halt(l1 + l2, True, False),
                   abschnitte=[(0.0, l1, EI), (l1, l1 + l2, k * EI)])
        F = b.lagerkraefte([Streckenlast(0.0, l1 + l2, q, q)])
        MB = -q / 4.0 * (l1 ** 3 + l2 ** 3 / k) / (2.0 * (l1 + l2 / k))
        self.assertAlmostEqual(F[0][0], q * l1 / 2.0 + MB / l1)
        self.assertAlmostEqual(F[2][0], q * l2 / 2.0 + MB / l2)
        self.assertAlmostEqual(sum(f for f, _ in F), q * (l1 + l2))

    def test_kragarm(self):
        F = balken(2.0, Halt(0.0, True, True)).lagerkraefte([Einzellast(2.0, 5e3)])
        self.assertAlmostEqual(F[0][0], 5e3)
        self.assertAlmostEqual(F[0][1], 10e3)

    def test_beweglich(self):
        self.assertFalse(balken(4.0, Halt(1.0, True, False)).stabil)
        self.assertFalse(balken(4.0, Halt(1.0, False, True), Halt(3.0, False, True)).stabil)
        self.assertTrue(balken(4.0, Halt(1.0, True, True)).stabil)


class TestStatik(unittest.TestCase):
    def test_einfeldtraeger(self):
        L = 6.0
        stuecke = statik(L, [Streckenlast(0.0, L, q, q), Einzellast(0.0, -3.0 * q), Einzellast(L, -3.0 * q)])
        self.assertAlmostEqual(wert(stuecke, "M", 3.0), q * L * L / 8.0)
        self.assertAlmostEqual(wert(stuecke, "V", 0.0), 3.0 * q)
        (_, kleinst), (s, groesst) = extreme(stuecke, "M")
        self.assertAlmostEqual(s, 3.0)
        self.assertAlmostEqual(groesst, q * L * L / 8.0)

    def test_pressung_rundet_das_stuetzmoment_ab(self):
        """
        Schnitt A-A des Kolloquiums 4: Kragarm 0.5 m, zwei Felder 4 m, Unterzüge
        1 m breit. Mit Punktlagern −10.8 kNm/m über der Mitte, mit gleichmässiger
        Pressung −7.4 kNm/m.
        """
        p = 5.58e3
        b = balken(9.0, *(Halt(s, True, False) for s in (0.5, 4.5, 8.5)))
        F = [f for f, _ in b.lagerkraefte([Streckenlast(0.0, 9.0, p, p)])]
        MA = -p * 0.5 ** 2 / 2.0
        MB = -p * 4.0 ** 2 / 8.0 - MA / 2.0
        RA = p * 0.5 + p * 2.0 + (MB - MA) / 4.0
        self.assertAlmostEqual(F[0], RA, places=6)
        punkt = statik(9.0, [Streckenlast(0.0, 9.0, p, p)] + [Einzellast(s, -f) for s, f in zip((0.5, 4.5, 8.5), F)])
        self.assertAlmostEqual(wert(punkt, "M", 4.5), MB, places=6)
        flaeche = statik(9.0, [Streckenlast(0.0, 9.0, p, p)]
                         + [Streckenlast(s - 0.5, s + 0.5, -f, -f) for s, f in zip((0.5, 4.5, 8.5), F)])
        self.assertAlmostEqual(wert(flaeche, "M", 4.5), RA * 4.0 - p * 4.5 ** 2 / 2.0 + F[1] * 0.5 ** 2 / 2.0,
                               places=6)

    def test_ohne_gleichgewicht_wirft(self):
        with self.assertRaises(ArithmeticError):
            statik(4.0, [Streckenlast(0.0, 4.0, q, q), Einzellast(0.0, -q)])


if __name__ == "__main__":
    unittest.main()
