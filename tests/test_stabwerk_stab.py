"""
Der einzelne Stab: Steifigkeit, arbeitsgleiche Lasten, Bettung.

Die Lasten gegen die Volleinspannkräfte der Tabellenbücher -- arbeitsgleich
heisst hier: genau sie, mit umgekehrtem Vorzeichen. In den Achsen des Stabs
zeigt y nach links, eine Last nach unten ist also negativ.
"""

import math
import unittest

from opencivil.stabwerk.stab import (
    Punkt, Strecke, aufteilen, bettung, drehung, formfunktionen, knotenlasten,
    mal, steifigkeit,
)

L = 5.0


class TestSteifigkeit(unittest.TestCase):
    def test_symmetrisch(self):
        k = steifigkeit(L, 3e6, 4e4)
        for i in range(6):
            for j in range(6):
                self.assertEqual(k[i][j], k[j][i])

    def test_starrkoerper_ohne_kraft(self):
        """Verschieben und Drehen als Ganzes kostet keine Kraft."""
        k = steifigkeit(L, 3e6, 4e4)
        for d in ([1, 0, 0, 1, 0, 0], [0, 1, 0, 0, 1, 0], [0, 0, 1, 0, L, 1]):
            for f in mal(k, d):
                self.assertAlmostEqual(f, 0.0, delta=1e-9)

    def test_kragarm_von_hand(self):
        """Eingespannt links, Kraft P rechts quer: v = PL³/(3EI), θ = PL²/(2EI)."""
        EI = 4e4
        k = steifigkeit(L, 1.0, EI)
        # Nur das freie Ende: v2, θ2.
        a, b, c = k[4][4], k[4][5], k[5][5]
        P = 1000.0
        det = a * c - b * b
        v2, t2 = (c * P) / det, (-b * P) / det
        self.assertAlmostEqual(v2, P * L ** 3 / (3 * EI), places=9)
        self.assertAlmostEqual(t2, P * L ** 2 / (2 * EI), places=9)

    def test_drehung_ist_orthogonal(self):
        a = math.radians(33.0)
        T = drehung(math.cos(a), math.sin(a))
        for i in range(6):
            for j in range(6):
                s = sum(T[i][k] * T[j][k] for k in range(6))
                self.assertAlmostEqual(s, 1.0 if i == j else 0.0, places=12)


class TestKnotenlasten(unittest.TestCase):
    """Vorzeichen: y nach links, also eine Last nach unten negativ."""

    def assertListenGleich(self, ist, soll, places=9):
        for a, b in zip(ist, soll):
            self.assertAlmostEqual(a, b, places=places)

    def test_gleichlast(self):
        q = 10e3
        f = knotenlasten(L, [Strecke(0.0, L, py_a=-q, py_b=-q)])
        self.assertListenGleich(f, [0, -q * L / 2, -q * L ** 2 / 12, 0, -q * L / 2, q * L ** 2 / 12])

    def test_dreieck(self):
        """Von 0 auf q: 3qL/20 und qL²/30 links, 7qL/20 und qL²/20 rechts."""
        q = 10e3
        f = knotenlasten(L, [Strecke(0.0, L, py_a=0.0, py_b=-q)])
        self.assertListenGleich(f, [0, -3 * q * L / 20, -q * L ** 2 / 30,
                                    0, -7 * q * L / 20, q * L ** 2 / 20])

    def test_einzelkraft(self):
        P, a = 20e3, 1.5
        b = L - a
        f = knotenlasten(L, [Punkt(a, Py=-P)])
        self.assertListenGleich(f, [0, -P * b * b * (3 * a + b) / L ** 3, -P * a * b * b / L ** 2,
                                    0, -P * a * a * (a + 3 * b) / L ** 3, P * a * a * b / L ** 2])

    def test_einzelmoment(self):
        M, a = 8e3, 2.0
        b = L - a
        f = knotenlasten(L, [Punkt(a, M=M)])
        self.assertListenGleich(f, [0, -6 * a * b * M / L ** 3, b * (b - 2 * a) * M / L ** 2,
                                    0, 6 * a * b * M / L ** 3, a * (a - 2 * b) * M / L ** 2])

    def test_gleichmaessiges_moment(self):
        """Über die ganze Länge: nur ein Kräftepaar, keine Endmomente."""
        m = 3e3
        f = knotenlasten(L, [Strecke(0.0, L, m_a=m, m_b=m)])
        self.assertListenGleich(f, [0, -m, 0, 0, m, 0])

    def test_laengs(self):
        p = 4e3
        f = knotenlasten(L, [Strecke(0.0, L, px_a=p, px_b=p)])
        self.assertListenGleich(f, [p * L / 2, 0, 0, p * L / 2, 0, 0])

    def test_teile_ergeben_das_ganze(self):
        """Eine Gleichlast in zwei Stücken gibt dieselben Kräfte wie in einem."""
        q = 7e3
        ganz = knotenlasten(L, [Strecke(0.0, L, py_a=-q, py_b=-q)])
        teile = knotenlasten(L, [Strecke(0.0, 2.0, py_a=-q, py_b=-q),
                                 Strecke(2.0, L, py_a=-q, py_b=-q)])
        self.assertListenGleich(teile, ganz)


class TestBettung(unittest.TestCase):
    def test_ist_das_integral(self):
        """k · ∫ Nᵀ N dx, mit vielen Punkten nachgerechnet."""
        k_q, k_l = 2e6, 5e5
        kb = bettung(L, k_q, k_l)
        n = 2000
        soll = [[0.0] * 6 for _ in range(6)]
        for i in range(n):
            x = (i + 0.5) * L / n
            n1, n2, h1, h2, h3, h4 = formfunktionen(x, L)
            quer = {1: h1, 2: h2, 4: h3, 5: h4}
            laengs = {0: n1, 3: n2}
            for a, fa in quer.items():
                for b, fb in quer.items():
                    soll[a][b] += k_q * fa * fb * L / n
            for a, fa in laengs.items():
                for b, fb in laengs.items():
                    soll[a][b] += k_l * fa * fb * L / n
        for i in range(6):
            for j in range(6):
                self.assertAlmostEqual(kb[i][j], soll[i][j], delta=1e-5 * abs(kb[1][1]))


class TestAufteilen(unittest.TestCase):
    def test_einzellast_auf_der_grenze_zaehlt_einmal(self):
        lasten = [Punkt(2.0, Py=-1.0), Punkt(0.0, Py=-2.0), Punkt(L, Py=-3.0)]
        erstes = aufteilen(lasten, 0.0, 2.0, ende=False)
        zweites = aufteilen(lasten, 2.0, L, ende=True)
        self.assertEqual([p.Py for p in erstes], [-2.0])
        self.assertEqual(sorted(p.Py for p in zweites), [-3.0, -1.0])
        self.assertEqual(sorted(p.a for p in zweites), [0.0, 3.0])

    def test_strecke_wird_geschnitten(self):
        """Ein Trapez von 0 bis 5 m, 0 bis 10: auf [2, 3] von 4 bis 6."""
        teil = aufteilen([Strecke(0.0, L, py_a=0.0, py_b=10.0)], 2.0, 3.0, ende=False)[0]
        self.assertEqual((teil.a, teil.b), (0.0, 1.0))
        self.assertAlmostEqual(teil.py_a, 4.0)
        self.assertAlmostEqual(teil.py_b, 6.0)


if __name__ == "__main__":
    unittest.main()
