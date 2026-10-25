"""
Die Querschnitte der Stäbe: jede Vorlage gegen das Integral über ihren Umriss.

Die Formeln stehen von Hand da (damit die Herleitung sie zeigen kann); das
Polygon-Integral der Querschnittsanalyse rechnet dieselben Werte auf einem
anderen Weg nach. Kreis und Kreisring gegen die geschlossene Form -- ihr
Umriss ist ein Vieleck.
"""

import math
import unittest

from opencivil.core.einheiten import MIO_MM4, MM2
from opencivil.querschnitt.geometrie import flaechenwerte, summe
from opencivil.stabwerk.querschnitte import KREIS, KREISRING, VORLAGEN, vorlage


class TestGegenDasIntegral(unittest.TestCase):
    def test_jede_vorlage_mit_ihren_vorgaben(self):
        for v in VORLAGEN:
            if v in (KREIS, KREISRING):
                continue
            with self.subTest(vorlage=v.name):
                masse = v.vorgaben()
                umrisse = v.umriss(masse)
                w = summe([(1.0 if i == 0 else -1.0, flaechenwerte(u))
                           for i, u in enumerate(umrisse)])
                k = v.kennwerte(masse)
                self.assertAlmostEqual(k["A"].in_einheit(MM2), w.A, delta=1e-9 * w.A)
                self.assertAlmostEqual(k["I"].in_einheit(MIO_MM4) * 1e6, w.I_y, delta=1e-9 * w.I_y)

    def test_t_mit_schwerpunkt(self):
        """Der Schwerpunkt vom oberen Rand: h − z_S des Integrals (dort von unten)."""
        masse = vorlage("t").vorgaben()
        w = flaechenwerte(vorlage("t").umriss(masse)[0])
        z_S = vorlage("t").kennwerte(masse)["z_S"].si * 1000.0
        self.assertAlmostEqual(z_S, masse["h"] - w.z_S, places=6)

    def test_kreis_und_kreisring(self):
        k = KREIS.kennwerte({"d": 400.0})
        self.assertAlmostEqual(k["A"].in_einheit(MM2), math.pi * 400 ** 2 / 4)
        r = KREISRING.kennwerte({"D": 300.0, "t": 20.0})
        self.assertAlmostEqual(r["I"].in_einheit(MIO_MM4) * 1e6,
                               math.pi * (300 ** 4 - 260 ** 4) / 64, places=3)


class TestPruefen(unittest.TestCase):
    def test_unmoegliche_masse(self):
        for schluessel, masse, wort in (
                ("kreisring", {"D": 100.0, "t": 60.0}, "zu dick"),
                ("rechteckrohr", {"b": 100.0, "h": 200.0, "t": 50.0}, "zu dick"),
                ("t", {"b": 200.0, "h": 600.0, "b_w": 300.0, "h_f": 100.0}, "schmaler"),
                # Ein Steg so breit wie der Flansch: dafuer gibt es das Rechteck --
                # dieselbe Regel wie in der Querschnittsanalyse.
                ("t", {"b": 300.0, "h": 600.0, "b_w": 300.0, "h_f": 100.0}, "schmaler"),
                ("doppel_t", {"b": 200.0, "h": 30.0, "t_f": 16.0, "t_w": 9.0}, "dicker"),
                ("rechteck", {"b": 0.0, "h": 600.0}, "grösser als null")):
            with self.subTest(vorlage=schluessel):
                self.assertIn(wort, vorlage(schluessel).pruefen(masse))

    def test_die_vorgaben_gehen(self):
        for v in VORLAGEN:
            self.assertIsNone(v.pruefen(v.vorgaben()), v.name)

    def test_unbekannte_vorlage(self):
        with self.assertRaises(KeyError):
            vorlage("ellipse")


if __name__ == "__main__":
    unittest.main()
