"""
Der Baukasten für Knoten: Kennungen, die nie wiederkommen, und gleiche
Koordinaten, die ein Knoten sind.
"""

import unittest
from dataclasses import dataclass, field

from opencivil.projekt.netz import Netz, neue_kennung


@dataclass
class Knoten:
    kennung: str
    y: float
    z: float


@dataclass
class Bauteil:
    """Was ein Bauteil fuer das Netz hat: seine Knoten und seine Zaehlung."""
    knoten: list = field(default_factory=list)
    vergeben: dict = field(default_factory=dict)


def netz(*knoten):
    bauteil = Bauteil(list(knoten))
    return bauteil.knoten, Netz(bauteil, neu=Knoten)


class TestKennungen(unittest.TestCase):

    def test_die_groesste_plus_eins(self):
        self.assertEqual(neue_kennung(Bauteil(), "K", ["K1", "K2", "K7"]), "K8")

    def test_eine_luecke_wird_nicht_gefuellt(self):
        """K3 war einmal da und ist gelöscht -- eine Meldung, die darauf zeigt, soll ins Leere zeigen."""
        self.assertEqual(neue_kennung(Bauteil(), "K", ["K1", "K2", "K4"]), "K5")

    def test_auch_die_letzte_kommt_nie_wieder(self):
        """
        LK3 gelöscht, die nächste heisst LK4 -- bis 2026-11-19 hiess sie
        wieder LK3, und eine Diagrammzeile, die auf die gelöschte zeigte,
        zeigte still die neue (Benutzer: eine Kennung kommt nie wieder).
        """
        bauteil = Bauteil()
        self.assertEqual(neue_kennung(bauteil, "LK", ["LK1", "LK2"]), "LK3")
        self.assertEqual(neue_kennung(bauteil, "LK", ["LK1", "LK2"]), "LK4")
        self.assertEqual(bauteil.vergeben, {"LK": 4})

    def test_nur_die_eigene_vorsilbe_zaehlt(self):
        bauteil = Bauteil(vergeben={"L": 12})
        self.assertEqual(neue_kennung(bauteil, "K", ["L9", "K2", "KX", "K"]), "K3")
        self.assertEqual(neue_kennung(bauteil, "F", []), "F1")


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

    def test_ein_geloeschter_knoten_kommt_nicht_wieder(self):
        liste, n = netz()
        n.an(0, 0)
        n.an(300, 0)
        liste.pop()
        _, n = netz(*liste)
        self.assertEqual(n.an(600, 0), "K2", "ohne Zaehlung zaehlen nur die vorhandenen")
        bauteil = Bauteil()
        n = Netz(bauteil, neu=Knoten)
        n.an(0, 0)
        n.an(300, 0)
        bauteil.knoten.pop()
        self.assertEqual(Netz(bauteil, neu=Knoten).an(600, 0), "K3")

    def test_bestehende_knoten_werden_gefunden(self):
        liste, n = netz(Knoten("K4", 50.0, 50.0), Knoten("K9", 250.0, 50.0))
        self.assertEqual(n.an(250, 50), "K9")
        self.assertEqual(n.an(150, 50), "K10")
        self.assertEqual(len(liste), 3)
        self.assertEqual(n.lage("K10"), (150.0, 50.0))
        self.assertIsNone(n.lage("K1"))


if __name__ == "__main__":
    unittest.main()
