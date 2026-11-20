"""
Mehrere Projekte in einer Datei -- die Mappe.

Gerechnet wird je Projekt; die Mappe prüft, was zwischen ihnen gilt, und
liest eine Datei mit einem einzelnen Projekt, wie sie bis 2026-11-20
geschrieben wurde, als Mappe mit diesem einen.
"""

import copy
import unittest

from opencivil.projekt import Mappe, Projekt, ProjektFehler
from opencivil.web import api, dienst


def zwei() -> dict:
    """Das Beispiel und ein neues Projekt «Halle»."""
    return {"projekte": [Projekt.beispiel().als_dict(), Projekt.neu("Halle").als_dict()]}


class TestLesen(unittest.TestCase):
    def test_hin_und_zurueck(self):
        roh = zwei()
        self.assertEqual(Mappe.aus_dict(roh).als_dict(), roh)

    def test_ein_einzelnes_projekt_ist_eine_mappe_mit_ihm(self):
        """So stehen die Dateien bis 2026-11-20 da -- und die Ablage im Browser."""
        alt = Projekt.beispiel().als_dict()
        self.assertEqual(Mappe.aus_dict(alt).als_dict(), {"projekte": [alt]})

    def test_jedes_projekt_heisst_anders(self):
        roh = zwei()
        roh["projekte"][1]["name"] = roh["projekte"][0]["name"]
        with self.assertRaisesRegex(ProjektFehler, "Das 1. und das 2. Projekt heissen beide"):
            Mappe.aus_dict(roh)

    def test_ohne_namen_geht_es_nicht(self):
        """Am Namen wählt man ein Projekt -- ohne ihn stünde ein leerer Knopf da."""
        roh = zwei()
        roh["projekte"][1]["name"] = " "
        with self.assertRaisesRegex(ProjektFehler, "^Projekt 2: ein Projekt braucht einen Namen"):
            Mappe.aus_dict(roh)

    def test_mindestens_ein_projekt(self):
        with self.assertRaisesRegex(ProjektFehler, "kein Projekt"):
            Mappe.aus_dict({"projekte": []})

    def test_ein_fehler_nennt_sein_projekt(self):
        """In jedem Projekt steht vielleicht eine Platte «Decke» -- welche ist gemeint?"""
        roh = zwei()
        platte = copy.deepcopy(roh["projekte"][0]["querschnitte"][0])
        platte["hh"] = 300
        roh["projekte"][1]["querschnitte"] = [platte]
        with self.assertRaisesRegex(
                ProjektFehler, r"^Projekt 'Halle', Platte 'Decke über EG': ein Feld 'hh'"):
            Mappe.aus_dict(roh)
        roh["projekte"][1].update(querschnitte=[], fremd=1)
        with self.assertRaisesRegex(ProjektFehler, r"^Projekt 'Halle': ein Feld 'fremd'"):
            Mappe.aus_dict(roh)

    def test_neben_den_projekten_steht_nichts(self):
        roh = {**zwei(), "auswahl": 1}
        with self.assertRaisesRegex(ProjektFehler, "'auswahl'"):
            Mappe.aus_dict(roh)
        with self.assertRaisesRegex(ProjektFehler, "Liste"):
            Mappe.aus_dict({"projekte": {"name": "Halle"}})

    def test_pruefen_wie_beim_lesen(self):
        """Was in Python gebaut ist, geht durch dieselbe Prüfung."""
        mappe = Mappe([Projekt.beispiel(), Projekt.beispiel()])
        with self.assertRaisesRegex(ProjektFehler, "heissen beide"):
            mappe.pruefen()
        mappe.projekte[1].materialien[0].kennung = mappe.projekte[1].materialien[1].kennung
        with self.assertRaisesRegex(ProjektFehler, r"^Projekt 'OCT Projekt': .*dieselbe Kennung"):
            mappe.pruefen()


class TestNeuesProjekt(unittest.TestCase):
    def test_mit_beton_und_stahl_ohne_bauteile(self):
        """So rechnet die erste Platte gleich."""
        projekt = Projekt.neu("Halle")
        self.assertEqual([m.anzeigename for m in projekt.materialien], ["C25/30", "B500B"])
        self.assertEqual(projekt.bauteile(), [])
        projekt.pruefen()

    def test_die_vorlage_der_oberflaeche(self):
        """«+» nimmt sie aus dem Katalog und setzt nur den Namen."""
        self.assertEqual(api.katalog()["neu"]["projekte"], Projekt.neu().als_dict())


class TestDienst(unittest.TestCase):
    def test_gibt_die_mappe_aufgeraeumt_zurueck(self):
        antwort = dienst.bearbeite("mappe_pruefen", {"mappe": Projekt.beispiel().als_dict()})
        self.assertEqual(antwort.status, 200)
        self.assertEqual([p["name"] for p in antwort.daten["mappe"]["projekte"]],
                         [Projekt.beispiel().name])

    def test_weist_fremde_dateien_ab(self):
        """Wie ein einzelnes Projekt: eine beliebige JSON-Datei ersetzt die Arbeit nicht durch nichts."""
        for fremd in ({}, {"foo": 1}, {"einkaufsliste": ["Brot"]}, [1, 2, 3], "text", None,
                      {"projekte": [{}]}):
            with self.subTest(fremd=fremd):
                self.assertEqual(dienst.bearbeite("mappe_pruefen", {"mappe": fremd}).status, 400)


if __name__ == "__main__":
    unittest.main()
