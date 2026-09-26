"""
Die Formelsammlung: jede Formel einmal, ohne Zahlen, mit dem Warum.

Zwei Sammlungen: die ganze, zum Nachschlagen in der Oberfläche -- an kein
Projekt gebunden --, und die eines Laufs, im Bericht als «Verwendete Formeln».
Die Herleitung zeigt Formeln mit Zahlen und lässt die Erklärungen weg; die
Sammlung zeigt die Erklärungen und keine Zahlen. Geprüft wird, dass das
Wandern stimmt -- nichts geht verloren, nichts steht doppelt.
"""

import unittest

from opencivil.bericht.formelsammlung import formelsammlung, vollstaendig
from opencivil.core.protokoll import GleichungBlock, TextBlock
from opencivil.projekt import Projekt
from opencivil.web import api


class TestFormelsammlung(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.alle = vollstaendig()
        aufbau = Projekt.beispiel().aufbauen()
        cls.loesung = aufbau.werk.loese(*aufbau.alle_ziele())

    def formeln(self):
        return [b for t in self.alle for b in t.bloecke if isinstance(b, GleichungBlock)]

    def test_jede_formel_einmal(self):
        latex = [f.latex for f in self.formeln()]
        self.assertEqual(len(latex), len(set(latex)))

    def test_ohne_fall_und_ohne_fallwerte(self):
        """Ein Fallname oder eine Einwirkung im Symbol hiesse: das ist ein Fall."""
        for f in self.formeln():
            with self.subTest(formel=f.titel):
                self.assertNotIn(r"\text{Feld", f.latex)
                self.assertNotIn(r"\mathrm{kNm}", f.latex)

    def test_jeder_nachweis_auch_wenn_das_projekt_ihn_nicht_fuehrt(self):
        """
        Zum Nachschlagen: das Beispiel führt nur Biegung und Normalkraft, die
        ganze Sammlung trotzdem Knicken, Querkraft, Duktilität ...
        """
        im_beispiel = {t.name for t in formelsammlung(self.loesung.protokoll)}
        alle = {t.name for t in self.alle}
        self.assertNotIn("Knicken", im_beispiel)
        self.assertLessEqual(
            {"Beton", "Betonstahl", "Biegung und Normalkraft", "Querkraft",
             "Duktilität", "Sprödes Versagen", "Knicken"}, alle)
        self.assertLess(im_beispiel, alle)

    def test_jedes_thema_weiss_seinen_bestandteil(self):
        """Danach zeigt die Oberfläche beim Beton nur Beton, bei der Platte die Platte."""
        art = {t.name: t.art for t in self.alle}
        self.assertEqual(art["Beton"], "beton")
        self.assertEqual(art["Betonstahl"], "betonstahl")
        for name in ("Querschnitt", "Biegung und Normalkraft", "Querkraft", "Knicken"):
            with self.subTest(thema=name):
                self.assertEqual(art[name], "querschnitt")
        self.assertEqual({t["art"] for t in api.formelsammlung_liste(self.alle)},
                         {"beton", "betonstahl", "querschnitt"})

    def test_die_erklaerungen_wandern_aus_der_herleitung(self):
        """Im Bericht unter «Verwendete Formeln»: die Erklärungen dieses Laufs, alle."""
        erklaerungen = {b.text for b in self.loesung.protokoll.alle_bloecke()
                        if isinstance(b, TextBlock) and b.erklaerung}
        self.assertTrue(erklaerungen)
        herleitung = {b.get("text") for b in api.protokoll_liste(self.loesung.protokoll)}
        gesammelt = {b.text for t in formelsammlung(self.loesung.protokoll)
                     for b in t.erklaerungen}
        self.assertFalse(erklaerungen & herleitung)
        self.assertEqual(erklaerungen, gesammelt)


if __name__ == "__main__":
    unittest.main()
