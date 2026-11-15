"""
Der raeumliche Stab -- Achsen, Steifigkeit, Lasten, gegen das Lehrbuch.

Die Steifigkeitsmatrix 12 × 12 in der ueblichen Folge (u, v, w, θx, θy, θz
am Anfang, dann am Ende) und die arbeitsgleichen Knotenkraefte einer
gleichmaessigen Last, wie sie in jedem Lehrbuch der Stabstatik stehen.
"""

import math
import unittest
from types import SimpleNamespace

from opencivil.stabwerk.modell import Lastart
from opencivil.stabwerk3d import raum
from opencivil.stabwerk3d import stab as st3
from opencivil.stabwerk3d.modell import Richtung, Stablast

L, EA, EI_y, EI_z, GI_T = 4.0, 5e9, 50e6, 20e6, 10e6


def knoten(x, y, z):
    return SimpleNamespace(x=x, y=y, z=z)


class Achsen(unittest.TestCase):
    def achsen(self, b, a=(0.0, 0.0, 0.0), drehung=0.0):
        return st3.achsen(knoten(*a), knoten(*b), drehung)[1]

    def gleich(self, v, erwartet):
        for a, b in zip(v, erwartet):
            self.assertAlmostEqual(a, b, places=12)

    def test_nach_rechts(self):
        """z nach unten, y nach hinten: in der x-z-Ebene wie die gestrichelte Faser."""
        ex, ey, ez = self.achsen((3.0, 0.0, 0.0))
        self.gleich(ex, (1, 0, 0))
        self.gleich(ey, (0, -1, 0))
        self.gleich(ez, (0, 0, -1))

    def test_nach_links(self):
        """z bleibt unten -- y dreht mit."""
        ex, ey, ez = self.achsen((-3.0, 0.0, 0.0))
        self.gleich(ey, (0, 1, 0))
        self.gleich(ez, (0, 0, -1))

    def test_in_y(self):
        ex, ey, ez = self.achsen((0.0, 2.0, 0.0))
        self.gleich(ey, (1, 0, 0))
        self.gleich(ez, (0, 0, -1))

    def test_lotrecht(self):
        """Nach oben: y ist -y des Systems, z zeigt nach +x -- wie die gestrichelte Faser der Ebene."""
        ex, ey, ez = self.achsen((0.0, 0.0, 3.0))
        self.gleich(ey, (0, -1, 0))
        self.gleich(ez, (1, 0, 0))
        ex, ey, ez = self.achsen((0.0, 0.0, -3.0))
        self.gleich(ez, (-1, 0, 0))

    def test_schief_rechtssystem(self):
        ex, ey, ez = self.achsen((2.0, 1.0, 1.5), a=(0.5, -1.0, 0.0))
        for v in (ex, ey, ez):
            self.assertAlmostEqual(raum.betrag(v), 1.0, places=12)
        self.assertAlmostEqual(raum.skalar(ex, ey), 0.0, places=12)
        self.assertAlmostEqual(raum.skalar(ex, ez), 0.0, places=12)
        self.gleich(raum.kreuz(ex, ey), ez)
        self.assertAlmostEqual(ey[2], 0.0, places=12, msg="y bleibt waagrecht")
        self.assertLess(ez[2], 0.0, "z zeigt nach unten")

    def test_drehwinkel(self):
        """β = 90°: das neue y ist das alte z, das neue z das alte -y."""
        _, ey0, ez0 = self.achsen((2.0, 1.0, 1.5))
        _, ey, ez = self.achsen((2.0, 1.0, 1.5), drehung=math.pi / 2)
        self.gleich(ey, ez0)
        self.gleich(ez, raum.mal(-1.0, ey0))


class Steifigkeit(unittest.TestCase):
    def setUp(self):
        self.k = st3.steifigkeit(L, EA, EI_y, EI_z, GI_T)

    def test_lehrbuch(self):
        k = self.k
        erwartet = {
            (0, 0): EA / L, (0, 6): -EA / L, (3, 3): GI_T / L, (3, 9): -GI_T / L,
            (1, 1): 12 * EI_z / L ** 3, (1, 5): 6 * EI_z / L ** 2, (1, 7): -12 * EI_z / L ** 3,
            (1, 11): 6 * EI_z / L ** 2, (5, 5): 4 * EI_z / L, (5, 7): -6 * EI_z / L ** 2,
            (5, 11): 2 * EI_z / L, (7, 11): -6 * EI_z / L ** 2,
            (2, 2): 12 * EI_y / L ** 3, (2, 4): -6 * EI_y / L ** 2, (2, 8): -12 * EI_y / L ** 3,
            (2, 10): -6 * EI_y / L ** 2, (4, 4): 4 * EI_y / L, (4, 8): 6 * EI_y / L ** 2,
            (4, 10): 2 * EI_y / L, (8, 10): 6 * EI_y / L ** 2,
        }
        for (i, j), wert in erwartet.items():
            self.assertAlmostEqual(k[i][j], wert, delta=1e-9 * abs(wert), msg=(i, j))
            self.assertAlmostEqual(k[j][i], wert, delta=1e-9 * abs(wert), msg=(j, i))
        # Was nicht dasteht, koppelt nicht: die Ebenen wissen nichts voneinander.
        for i, j in ((1, 2), (1, 4), (2, 5), (3, 4), (0, 1), (4, 5)):
            self.assertEqual(k[i][j], 0.0, (i, j))

    def test_starre_bewegungen(self):
        """Verschieben und Drehen als Ganzes kostet nichts."""
        theta = 1e-3
        bewegungen = [
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
            # um z: v = θ·x
            [0, 0, 0, 0, 0, theta, 0, theta * L, 0, 0, 0, theta],
            # um y: w = -θ·x
            [0, 0, 0, 0, theta, 0, 0, 0, -theta * L, 0, theta, 0],
        ]
        for d in bewegungen:
            for zeile in self.k:
                self.assertAlmostEqual(sum(a * b for a, b in zip(zeile, d)), 0.0, places=3)


class Lasten(unittest.TestCase):
    q = 6e3

    def test_gleichmaessig_quer(self):
        """In z: qL/2 und ∓qL²/12 um y; in y: qL/2 und ±qL²/12 um z."""
        q = self.q
        f = st3.knotenlasten(L, st3.strecke(0.0, L, p_a=(0, 0, q), p_b=(0, 0, q)))
        for i, wert in ((2, q * L / 2), (8, q * L / 2), (4, -q * L ** 2 / 12), (10, q * L ** 2 / 12)):
            self.assertAlmostEqual(f[i], wert, places=6)
        f = st3.knotenlasten(L, st3.strecke(0.0, L, p_a=(0, q, 0), p_b=(0, q, 0)))
        for i, wert in ((1, q * L / 2), (7, q * L / 2), (5, q * L ** 2 / 12), (11, -q * L ** 2 / 12)):
            self.assertAlmostEqual(f[i], wert, places=6)

    def test_torsion_und_laengs(self):
        m, p = 2e3, 3e3
        f = st3.knotenlasten(L, st3.strecke(0.0, L, p_a=(p, 0, 0), p_b=(p, 0, 0),
                                            m_a=(m, 0, 0), m_b=(m, 0, 0)))
        for i, wert in ((0, p * L / 2), (6, p * L / 2), (3, m * L / 2), (9, m * L / 2)):
            self.assertAlmostEqual(f[i], wert, places=6)

    def test_einzellasten(self):
        f = st3.knotenlasten(L, st3.punkt(L, P=(1.0, 2.0, 3.0), M=(4.0, 5.0, 6.0)))
        self.assertEqual(f[6:], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

    def test_jede_last_in_allen_teilen(self):
        """Damit die drei Verlaeufe an denselben Stellen springen."""
        lasten = st3.punkt(1.0, P=(0, 0, 5.0))
        self.assertEqual((len(lasten.z), len(lasten.y), len(lasten.t)), (1, 1, 1))
        self.assertFalse(lasten.mit_torsion)
        self.assertTrue(st3.punkt(1.0, M=(1.0, 0, 0)).mit_torsion)

    def test_resultierende(self):
        """Eine gleichmaessige Last laengs eines Stabs in x: q·L in der Mitte."""
        q = self.q
        _, achsen = st3.achsen(knoten(1, 2, 3), knoten(1 + L, 2, 3))
        lasten = st3.lokal(Stablast("L1", Lastart.LINIENLAST, q), L, achsen)
        F = st3.resultierende(lasten, (1.0, 2.0, 3.0), achsen)
        mitte = (1 + L / 2, 2.0, 3.0)
        erwartet = [0.0, 0.0, -q * L, *raum.kreuz(mitte, (0.0, 0.0, -q * L))]
        for a, b in zip(F, erwartet):
            self.assertAlmostEqual(a, b, places=6)


class Richtungen(unittest.TestCase):
    def setUp(self):
        # Ein Dach, um 30° geneigt, in der x-z-Ebene.
        self.L = 4.0
        a = knoten(0, 0, 0)
        b = knoten(self.L * math.cos(math.radians(30)), 0, self.L * math.sin(math.radians(30)))
        self.achsen = st3.achsen(a, b)[1]

    def resultierende(self, **felder):
        last = Stablast("L1", Lastart.LINIENLAST, 1e3, **felder)
        return st3.resultierende(st3.lokal(last, self.L, self.achsen), (0, 0, 0), self.achsen)

    def test_projiziert(self):
        """Schnee je Meter Grundriss: cos 30° weniger je Meter Stab."""
        gesamt = self.resultierende()[2]
        projiziert = self.resultierende(projiziert=True)[2]
        self.assertAlmostEqual(gesamt, -4e3, places=6)
        self.assertAlmostEqual(projiziert, -4e3 * math.cos(math.radians(30)), places=6)

    def test_lokal(self):
        """Quer z des Stabs steht senkrecht auf dem Dach, nach unten."""
        F = self.resultierende(richtung=Richtung.QUER_Z)
        self.assertAlmostEqual(F[0], 4e3 * math.sin(math.radians(30)), places=6)
        self.assertAlmostEqual(F[2], -4e3 * math.cos(math.radians(30)), places=6)
        F = self.resultierende(richtung=Richtung.QUER_Y)
        self.assertAlmostEqual(F[1], -4e3, places=6)

    def test_ausserhalb(self):
        last = Stablast("L1", Lastart.EINZELLAST, 1e3, von=5.0)
        self.assertIsInstance(st3.lokal(last, self.L, self.achsen), str)


if __name__ == "__main__":
    unittest.main()
