"""
Stahlsorten im Loeser: je Seite eine Lage, mit dem Stahl ihrer Seite.

Bis 2026-10-24 liess der Editor je Seite einer Platte einen eigenen Stahl
waehlen, und hier stand, dass jede Lage mit ihm rechnet. Seither hat eine
Platte einen Stahl fuer alle Lagen (Benutzer); gemischte Sorten in einer
Platte gibt es nicht mehr. Was bleibt, ist der Loeser, der je Seite den
Stahl ihrer Lagen behaelt -- er ist unabhaengig von der Platte.
"""

import unittest

from opencivil.nachweis.querschnittsloeser import Stahllage, lagen_je_seite
from opencivil.querschnitt.werkstoffgesetz import Stahlgesetz

#: Bemessungswerte der Fliessgrenze, in Pa.
F_YD_B500B = 500e6 / 1.15
F_YD_B700B = 700e6 / 1.15


class TestHandrechnungImLoeser(unittest.TestCase):
    """Je Seite eine Lage im Schwerpunkt -- mit dem Stahl dieser Seite."""

    B500B = Stahlgesetz(E_s=200e9, f_yd=F_YD_B500B, f_yd_druck=F_YD_B500B, eps_ud=0.045)
    B700B = Stahlgesetz(E_s=200e9, f_yd=F_YD_B700B, f_yd_druck=F_YD_B700B, eps_ud=0.045)

    def test_jede_seite_behaelt_ihren_stahl(self):
        lagen = lagen_je_seite([
            Stahllage(a_s=1e-3, z=0.25, stahl=self.B700B, von_unten=True),
            Stahllage(a_s=5e-4, z=0.24, stahl=self.B700B, von_unten=True),
            Stahllage(a_s=5e-4, z=0.05, stahl=self.B500B, von_unten=False)], 0.3)
        self.assertEqual([l.stahl for l in lagen], [self.B700B, self.B500B])

    def test_zwei_staehle_auf_einer_seite_sind_ein_fehler(self):
        """Die Platte kann das nicht -- je Seite und Richtung liegt eine Lage."""
        with self.assertRaises(ValueError):
            lagen_je_seite([Stahllage(a_s=1e-3, z=0.25, stahl=self.B700B, von_unten=True),
                            Stahllage(a_s=5e-4, z=0.24, stahl=self.B500B, von_unten=True)],
                           0.3)


if __name__ == "__main__":
    unittest.main()
