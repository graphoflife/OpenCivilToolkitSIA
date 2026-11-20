"""
Die Fläche aller Bruchzustände eines gezeichneten Querschnitts, geschnitten
-- was das Interaktionsdiagramm der Querschnittsanalyse zeigt.
"""

import math
import unittest

from opencivil.querschnitt.interaktion import Bewehrung, Teil
from opencivil.querschnitt.widerstandsflaeche import _bei_n_gelesen, _schnittstellen, schnitt
from tests.test_interaktion import querschnitt, rechteck


class TestFlaecheDerWiderstaende(unittest.TestCase):
    """
    Das Interaktionsdiagramm ist ein Schnitt durch die Fläche aller
    Bruchzustände. Bei festem N kommt er aus derselben Suche wie der
    Nachweis; bei festem Moment aus den Fächern, linear gelesen -- dort
    gilt eine Schranke gegen die genaue Suche.
    """

    @classmethod
    def setUpClass(cls):
        # Unten mehr Stahl als oben, also kein Spiegel um y: die beiden Äste
        # sind verschieden, und links wie rechts ist es symmetrisch.
        cls.q = querschnitt(
            [Teil(rechteck(0, 0, 0.3, 0.6), 0, None)],
            [Bewehrung((y, 0.05), 314e-6, 1, 0) for y in (0.05, 0.15, 0.25)]
            + [Bewehrung((y, 0.55), 113e-6, 1, 0) for y in (0.05, 0.25)])

    def genauer_umriss(self, N, achse, wert, neigungen=360):
        umriss = [(p.M_y, p.M_z) for p in (
            self.q.bei_normalkraft(2 * math.pi * k / neigungen, N) for k in range(neigungen))]
        stellen = _schnittstellen(umriss, achse, wert)
        return min(stellen), max(stellen)

    def test_der_faecher_hat_keine_sehne_mehr(self):
        """
        Gleichmässig in der Krümmung verteilt, sprang N zwischen zwei
        Stützstellen um ein Drittel der Spanne; dazwischen war die Linie eine
        Sehne. Jetzt liegt sie überall nah an der genauen Suche.
        """
        f = self.q.faecher(-math.pi / 2)
        spanne = f[0].N - f[-1].N
        self.assertLessEqual(max(a.N - b.N for a, b in zip(f, f[1:])), 0.05 * spanne + 1e-6)
        for i in range(1, 40):
            N = f[0].N - spanne * i / 40
            genau = self.q.bei_normalkraft(-math.pi / 2, N)
            gelesen = _bei_n_gelesen(f, N)[0]
            self.assertAlmostEqual(gelesen / genau.M_y, 1.0, delta=2e-3, msg=f"N = {N}")

    def test_bei_festem_n_wie_der_nachweis(self):
        N = -500e3
        punkte = schnitt(self.q, "N", N, neigungen=36)
        self.assertEqual(len(punkte), 36)
        for k, (n, m_y, m_z) in enumerate(punkte):
            genau = self.q.bei_normalkraft(2 * math.pi * k / 36, N)
            self.assertAlmostEqual(n, N, delta=1e-3)
            self.assertEqual((m_y, m_z), (genau.M_y, genau.M_z))

    def test_bei_m_z_null_die_beiden_aeste_der_linie_um_y(self):
        """Je Stufe auf 0.3 % des grössten Moments -- so fein liest der Fächer."""
        punkte = schnitt(self.q, "M_z", 0.0)
        groesstes = max(abs(M_y) for _, M_y, _ in punkte)
        je_n = {}
        for N, M_y, M_z in punkte:
            self.assertEqual(M_z, 0.0)
            je_n.setdefault(N, []).append(M_y)
        for N, werte in je_n.items():
            for psi, wert in ((-math.pi / 2, max(werte)), (math.pi / 2, min(werte))):
                genau = self.q.bei_normalkraft(psi, N).M_y
                self.assertAlmostEqual(wert, genau, delta=3e-3 * groesstes,
                                       msg=f"N = {N}, ψ = {psi}")

    def test_bei_festem_moment_abseits_der_achse(self):
        """M_z = 40 kNm: auf jeder Stufe dort, wo der genaue Umriss die Gerade kreuzt."""
        je_n = {}
        for N, M_y, M_z in schnitt(self.q, "M_z", 40e3):
            self.assertEqual(M_z, 40e3)
            je_n.setdefault(N, []).append(M_y)
        stufen = sorted(je_n)
        for N in stufen[5::12]:
            links, rechts = self.genauer_umriss(N, 1, 40e3)
            spanne = max(abs(links), abs(rechts), 1e3)
            self.assertAlmostEqual(min(je_n[N]), links, delta=5e-3 * spanne)
            self.assertAlmostEqual(max(je_n[N]), rechts, delta=5e-3 * spanne)

    def test_jenseits_der_flaeche_nichts(self):
        self.assertEqual(schnitt(self.q, "M_z", 1e9), [])
        zug, _ = self.q.normalkraft_grenzen()
        self.assertEqual(schnitt(self.q, "N", 2 * zug), [])

    def test_nur_n_m_y_und_m_z(self):
        with self.assertRaises(ValueError):
            schnitt(self.q, "V", 0.0)


if __name__ == "__main__":
    unittest.main()
