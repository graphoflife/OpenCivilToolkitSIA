"""
Die Rechenwahl: welche Gesetze zu Kriechzahl, Wertesatz und Rechenart gehören.

Geprüft wird die eine Stelle, an der das entschieden wird
(:mod:`opencivil.nachweis.rechenwahl`) -- dass jede Rechenart das tut, was ihr
Name sagt. Ob die Nachweise sie richtig benutzen, prüfen deren eigene Tests
und die Altdatei, die vor dem Umbau festgehalten wurde.
"""

import unittest

from opencivil.core.berechnung import Eingabebezug
from opencivil.nachweis.querschnittsloeser import (
    Stahllage, Werkstoffsatz, lagen_je_seite, stahl_bilinear, stahl_nur_zug,
)
from opencivil.nachweis.rechenwahl import (
    RECHENARTEN, SPANNUNGSARTEN, Kennwerte, Rechenart, Rechenwahl,
    bezuege_vereinen, gesetze,
)
from opencivil.querschnitt.werkstoffgesetz import Spannungsblock

W = Kennwerte(f_c=20e6, f_s=435e6, f_s_druck=435e6, E_cm=33.6e9, E_s=200e9,
              eps_c1d=0.002, eps_c2d=0.0035)

LAGEN = [Stahllage(a_s=1696e-6, z=0.249, nummer=2, von_unten=True),
         Stahllage(a_s=754e-6, z=0.243, nummer=2, von_unten=True),
         Stahllage(a_s=754e-6, z=0.048, nummer=3, von_unten=False)]


class TestRechenarten(unittest.TestCase):
    def test_die_listen(self):
        self.assertEqual([a.value for a in RECHENARTEN], ["handrechnung", "block", "parabel"])
        self.assertEqual(SPANNUNGSARTEN[-1], Rechenart.ELASTISCH)
        self.assertEqual(Rechenwahl().index, "Rd")
        self.assertEqual(Rechenwahl(satz=Werkstoffsatz.CHARAKTERISTISCH).index, "Rk")

    def test_aus_den_feldern_einer_beschreibung(self):
        wahl = Rechenwahl.aus(1.5, "charakteristisch", "parabel")
        self.assertEqual(wahl, Rechenwahl(1.5, Werkstoffsatz.CHARAKTERISTISCH, Rechenart.PARABEL))

    def test_nur_parabel_und_elastisch_haengen_an_der_kriechzahl(self):
        for art in SPANNUNGSARTEN:
            with self.subTest(art=art.value):
                weich = gesetze(Rechenwahl(2.0, art=art), W).beton(-0.0005)
                steif = gesetze(Rechenwahl(0.0, art=art), W).beton(-0.0005)
                self.assertEqual(weich != steif, art.mit_kriechzahl)


class TestGesetze(unittest.TestCase):
    def test_handrechnung_block_stahl_nur_auf_zug_je_seite_eine_lage(self):
        g = gesetze(Rechenwahl(art=Rechenart.HANDRECHNUNG), W)
        self.assertIsInstance(g.beton, Spannungsblock)
        self.assertEqual(g.stahl(-0.01), 0.0)
        self.assertAlmostEqual(g.stahl(0.01), 435e6)
        self.assertTrue(g.gemittelt)
        self.assertFalse(g.verdraengt)
        lagen = g.lagen(LAGEN, 0.3)
        self.assertEqual(len(lagen), 2)
        self.assertAlmostEqual(lagen[0].a_s, 2450e-6)
        self.assertAlmostEqual(lagen[0].z, (1696 * 0.249 + 754 * 0.243) / 2450)

    def test_block_genau_mit_druckstahl(self):
        g = gesetze(Rechenwahl(art=Rechenart.BLOCK), W)
        self.assertIsInstance(g.beton, Spannungsblock)
        self.assertAlmostEqual(g.stahl(-0.01), -435e6)
        self.assertTrue(g.gemittelt)
        self.assertTrue(g.verdraengt)
        self.assertEqual(g.lagen(LAGEN, 0.3), LAGEN)

    def test_parabel_und_elastisch(self):
        parabel = gesetze(Rechenwahl(art=Rechenart.PARABEL), W)
        self.assertFalse(parabel.gemittelt)
        self.assertAlmostEqual(parabel.beton(-0.002) / 1e6, -20.0)
        elastisch = gesetze(Rechenwahl(2.0, art=Rechenart.ELASTISCH), W)
        self.assertAlmostEqual(elastisch.beton(-0.0003), -33.6e9 / 3 * 0.0003)
        self.assertEqual(elastisch.beton(-0.01), -20e6)

    def test_der_ungerissene_zustand_ersetzt_nur_den_beton(self):
        g = gesetze(Rechenwahl(art=Rechenart.HANDRECHNUNG), W)
        loeser = g.loeser(h=0.3, b=1.0, lagen=LAGEN, beton=lambda eps: 1e10 * eps)
        self.assertEqual(len(loeser.lagen), 2)
        self.assertIs(loeser.stahl, g.stahl)


class TestStahl(unittest.TestCase):
    def test_eigenes_druckplateau(self):
        gesetz = stahl_bilinear(E_s=200e9, f_sd=435e6, f_sd_druck=400e6)
        self.assertAlmostEqual(gesetz(0.01), 435e6)
        self.assertAlmostEqual(gesetz(-0.01), -400e6)
        self.assertEqual(gesetz(0.05), 0.0)

    def test_gleiche_plateaus_rechnen_wie_vorher(self):
        """Bei den Normsorten sind beide gleich -- dann Bit für Bit wie bis heute."""
        alt = stahl_bilinear(E_s=200e9, f_sd=435e6)
        neu = stahl_bilinear(E_s=200e9, f_sd=435e6, f_sd_druck=435e6)
        for eps in (-0.05, -0.003, -1e-4, -0.0, 0.0, 1e-4, 0.003, 0.05):
            self.assertEqual(neu(eps), alt(eps))

    def test_nur_zug(self):
        gesetz = stahl_nur_zug(E_s=200e9, f_sd=435e6, eps_ud=0.045)
        self.assertEqual(gesetz(-0.001), 0.0)
        self.assertAlmostEqual(gesetz(0.001), 200e6)
        self.assertAlmostEqual(gesetz(0.01), 435e6)
        self.assertEqual(gesetz(0.05), 0.0)

    def test_je_seite_eine_lage_auch_ohne_angabe_der_seite(self):
        """Ohne ``von_unten`` entscheidet die Tiefe gegen h/2."""
        lagen = lagen_je_seite([Stahllage(a_s=1e-3, z=0.25), Stahllage(a_s=5e-4, z=0.05)], 0.3)
        self.assertEqual([l.von_unten for l in lagen], [True, False])


class TestBezuege(unittest.TestCase):
    def test_dieselbe_eingabe_einmal(self):
        a = [Eingabebezug("E_s", "stahl.s1.E_s"), Eingabebezug("h", "q.h")]
        b = [Eingabebezug("E_s", "stahl.s1.E_s"), Eingabebezug("f_yk", "stahl.s1.f_yk")]
        self.assertEqual([x.name for x in bezuege_vereinen(a, b)], ["E_s", "h", "f_yk"])

    def test_ein_name_mit_zwei_zahlen_ist_ein_fehler(self):
        with self.assertRaises(ValueError):
            bezuege_vereinen([Eingabebezug("E_s", "stahl.s1.E_s")],
                             [Eingabebezug("E_s", "stahl.s2.E_s")])


if __name__ == "__main__":
    unittest.main()
