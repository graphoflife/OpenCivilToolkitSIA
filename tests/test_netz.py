"""
Der Baukasten für Knoten: Kennungen, die nie wiederkommen, und gleiche
Koordinaten, die ein Knoten sind.
"""

import unittest
from dataclasses import dataclass

from opencivil.projekt.netz import Netz, naechste_kennung


@dataclass
class Knoten:
    kennung: str
    y: float
    z: float


def netz(*knoten):
    liste = list(knoten)
    return liste, Netz(liste, neu=Knoten)


class TestKennungen(unittest.TestCase):

    def test_die_groesste_plus_eins(self):
        self.assertEqual(naechste_kennung(["K1", "K2", "K7"], "K"), "K8")

    def test_eine_luecke_wird_nicht_gefuellt(self):
        """K3 war einmal da und ist gelöscht -- eine Meldung, die darauf zeigt, soll ins Leere zeigen."""
        self.assertEqual(naechste_kennung(["K1", "K2", "K4"], "K"), "K5")

    def test_nur_die_eigene_vorsilbe_zaehlt(self):
        self.assertEqual(naechste_kennung(["L9", "K2", "KX", "K"], "K"), "K3")
        self.assertEqual(naechste_kennung([], "F"), "F1")


class TestNetz(unittest.TestCase):

    def test_gleiche_koordinaten_sind_ein_knoten(self):
        liste, n = netz()
        a = n.an(0, 0)
        b = n.an(300, 0)
        self.assertEqual(n.an(0.0, 0.0), a)
        self.assertNotEqual(a, b)
        self.assertEqual([k.kennung for k in liste], ["K1", "K2"])

    def test_beinahe_gleich_ist_ein_anderer_knoten(self):
        """Fangen ist Sache des Zeichenfensters -- hier wird nichts stillschweigend vereint."""
        _, n = netz()
        self.assertNotEqual(n.an(0, 0), n.an(0.01, 0))

    def test_bestehende_knoten_werden_gefunden(self):
        liste, n = netz(Knoten("K4", 50.0, 50.0), Knoten("K9", 250.0, 50.0))
        self.assertEqual(n.an(250, 50), "K9")
        self.assertEqual(n.an(150, 50), "K10")
        self.assertEqual(len(liste), 3)
        self.assertEqual(n.lage("K10"), (150.0, 50.0))
        self.assertIsNone(n.lage("K1"))


if __name__ == "__main__":
    unittest.main()
