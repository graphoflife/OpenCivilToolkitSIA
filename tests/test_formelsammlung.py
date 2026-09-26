"""
Die Formelsammlung: jede Formel des Laufs einmal, ohne Zahlen, mit dem Warum.

Die Herleitung zeigt Formeln mit Zahlen und laesst die Erklaerungen weg; die
Sammlung zeigt die Erklaerungen und keine Zahlen. Geprueft wird, dass das
Wandern stimmt -- nichts geht verloren, nichts steht doppelt.
"""

import unittest

from opencivil.core.protokoll import TextBlock
from opencivil.projekt import Projekt
from opencivil.web import dienst


class TestFormelsammlung(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        projekt = Projekt.beispiel()
        # Mit Querkraft und einer zweiten Platte: dieselben Formeln kommen
        # dann mehrfach vor -- je Fall, je Lage, je Platte.
        for k in projekt.querschnitte[0].kombinationen:
            k.V_Ed = 80.0
        zweite = projekt.platte("Zweite", h=250)
        zweite.einwirkung("Feld", M_Ed=40, V_Ed=30)
        cls.projekt = projekt
        cls.daten = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()}).daten
        aufbau = projekt.aufbauen()
        cls.loesung = aufbau.werk.loese(*aufbau.alle_ziele())

    def eintraege(self, art, thema=None):
        return [e for t in self.daten["formelsammlung"] if thema in (None, t["thema"])
                for e in t["eintraege"] if e["art"] == art]

    def formeln(self, thema=None):
        return self.eintraege("gleichung", thema)

    def test_jede_formel_einmal(self):
        latex = [f["latex"] for f in self.formeln()]
        self.assertEqual(len(latex), len(set(latex)))

    def test_ohne_fall_und_ohne_fallwerte(self):
        """Ein Fallname oder eine Einwirkung im Symbol hiesse: das ist ein Fall."""
        for f in self.formeln():
            with self.subTest(formel=f["titel"]):
                self.assertNotIn(r"\text{Feld", f["latex"])
                self.assertNotIn(r"\mathrm{kNm}", f["latex"])

    def test_die_erklaerungen_wandern_aus_der_herleitung(self):
        erklaerungen = {b.text for b in self.loesung.protokoll.alle_bloecke()
                        if isinstance(b, TextBlock) and b.erklaerung}
        self.assertTrue(erklaerungen)
        herleitung = {b.get("text") for b in self.daten["protokoll"]}
        gesammelt = {e["text"] for e in self.eintraege("text")}
        self.assertFalse(erklaerungen & herleitung)
        self.assertEqual(erklaerungen, gesammelt)

    def test_je_formel_die_raeume_in_denen_sie_vorkam(self):
        """Danach grenzt «Aktuelle Seite» ein: beide Platten, der Beton für sich."""
        self.assertEqual(self.formeln("Beton")[0]["raeume"], ["beton.b1"])
        querkraft = {r for f in self.formeln("Querkraft") for r in f["raeume"]}
        self.assertEqual(querkraft, {"querschnitt.q1", "querschnitt.q2"})


if __name__ == "__main__":
    unittest.main()
