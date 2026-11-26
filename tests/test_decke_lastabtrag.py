"""
Wie die Decke ihre Last von selbst aufteilt -- wo Folie 31 nichts sagt.

* Mitte eines Felds: je zur Hälfte bei gleichen Spannweiten, ganz in die
  kürzere ab dem Verhältnis 1.5, dazwischen geradlinig (Benutzer,
  2026-11-25). Fast quadratische Felder springen nicht mehr: 5 × 5.04 m und
  5 × 5.06 m teilen fast gleich.
"""

import math
import unittest

from opencivil.decke import geometrie as geo
from opencivil.decke.aufteilung import GANZ_AB, in_der_mitte
from opencivil.decke.feld import an_stelle
from opencivil.decke.modell import Decke, Flaechenlast, Lastfall, Platte
from tests.test_decke_rechnung import E, WICHTE, Rechnung, q, rechteck, waende


class TestMitteEinesFelds(Rechnung):
    """Rechteckplatten a × b auf vier Wänden; Richtung 1 ist x."""

    def in_der_platte(self, a, b):
        """Der Anteil in x und die Schnittkräfte neben der Mitte -- nicht auf einer Grenze der Streifen."""
        ecken = rechteck(0, 0, a, b)
        e = self.gerechnet(Decke(platten=[Platte("P", ecken, 0.2, E, WICHTE)],
                                 linienlager=waende(ecken, 0, 1, 2, 3),
                                 lastfaelle=[Lastfall("q", [Flaechenlast("q", q, platte="P")])]))
        p = (a / 2.0 + 0.1, b / 2.0 + 0.1)
        anteil = next(wert for zelle, wert in e.aufteilungen.zellen if geo.innen(p, zelle))
        return anteil, an_stelle(e, e.faelle[0], p)

    def test_die_regel(self):
        self.assertEqual(in_der_mitte(5.0, 5.0), 0.5)
        self.assertAlmostEqual(in_der_mitte(4.0, 5.0), 0.75)
        self.assertAlmostEqual(in_der_mitte(5.0, 4.0), 0.25)
        self.assertEqual(in_der_mitte(4.0, 4.0 * GANZ_AB), 1.0)
        self.assertEqual(in_der_mitte(8.0, 4.0), 0.0, "Folie 31: ganz in die kürzere")
        self.assertEqual(in_der_mitte(4.0, math.inf), 1.0, "nur eine Richtung hat ein Feld")
        self.assertEqual(in_der_mitte(math.inf, math.inf), 0.5)

    def test_ein_feld_4_mal_5(self):
        anteil, _ = self.in_der_platte(4.0, 5.0)
        self.assertAlmostEqual(anteil, 0.75)

    def test_kein_sprung_bei_fast_gleichen_spannweiten(self):
        anteil_1, k_1 = self.in_der_platte(5.0, 5.04)
        anteil_2, k_2 = self.in_der_platte(5.0, 5.06)
        self.assertAlmostEqual(anteil_1, 0.508)
        self.assertAlmostEqual(anteil_2, 0.512)
        self.assertLess(abs(k_2.mx - k_1.mx), 0.02 * k_1.mx)
        self.assertLess(abs(k_2.my - k_1.my), 0.02 * k_1.my)


if __name__ == "__main__":
    unittest.main()
