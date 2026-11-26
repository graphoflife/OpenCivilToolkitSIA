"""
Was «+», ⧉ und × in einer App tun, im Kern (opencivil/projekt/projekt.py):
ein neuer Eintrag heisst «Platte 1», eine Kopie «… (Kopie)», die Kopie der
Sandbox wie ein neuer; gelöscht wird weder die Sandbox noch, worauf ein
Bauteil zeigt. Die Oberfläche tut dasselbe in JavaScript, mit dem Stamm des
Namens aus dem Katalog -- test_zustand_js hält die Namen beider gleich.
"""

import unittest

from opencivil.projekt import Projekt, ProjektFehler
from opencivil.projekt.projekt import APPLISTEN, SANDBOX, kopie_name, naechster_name
from opencivil.web import api, dienst


def mit_sandboxen():
    projekt = Projekt.beispiel()
    projekt.sandboxen_anlegen()
    return projekt


class TestNamen(unittest.TestCase):

    def test_der_erste_freie(self):
        self.assertEqual(naechster_name("Platte", []), "Platte 1")
        self.assertEqual(naechster_name("Platte", ["Platte 1", "Platte 3"]), "Platte 2")

    def test_eine_kopie_und_noch_eine(self):
        self.assertEqual(kopie_name("Decke", ["Decke"]), "Decke (Kopie)")
        self.assertEqual(kopie_name("Decke", ["Decke", "Decke (Kopie)"]), "Decke (Kopie 2)")

    def test_jede_app_hat_einen_stamm_und_der_katalog_nennt_ihn(self):
        """Auch das Projekt: «+» der Projektreihe gibt «Projekt 2»."""
        staemme = api.katalog()["staemme"]
        self.assertEqual(set(staemme), {*APPLISTEN, "projekte"})
        self.assertTrue(all(staemme.values()))
        self.assertEqual((staemme["querschnitte"], staemme["projekte"]), ("Platte", "Projekt"))


class TestAnlegen(unittest.TestCase):

    def test_wie_plus_in_der_app(self):
        projekt = mit_sandboxen()
        vorher = len(projekt.querschnitte)
        neu = projekt.eintrag_anlegen("querschnitte")
        self.assertEqual((neu.name, neu.beton, neu.stahl), ("Platte 1", "b1", "s1"))
        self.assertIs(projekt.querschnitte[-1], neu)
        self.assertEqual(len(projekt.querschnitte), vorher + 1)
        self.assertEqual(projekt.eintrag_anlegen("querschnitte").name, "Platte 2")
        projekt.pruefen()

    def test_jede_kennung_ist_neu(self):
        """Auch nach einem Löschen: die gelöschte kommt nie wieder."""
        projekt = mit_sandboxen()
        erste = projekt.eintrag_anlegen("pfaehle").kennung
        projekt.eintrag_loeschen(erste)
        self.assertNotEqual(projekt.eintrag_anlegen("pfaehle").kennung, erste)

    def test_eine_liste_die_es_nicht_gibt(self):
        with self.assertRaisesRegex(ProjektFehler, "Eine App mit der Liste 'platten' gibt es "
                                                   "nicht. Möglich sind: querschnitte, "):
            Projekt.neu().eintrag_anlegen("platten")

    def test_ein_material_nach_seiner_art(self):
        projekt = Projekt.neu()
        self.assertEqual(projekt.material_anlegen("baustahl", "S355").name, "S355")
        eigen = projekt.material_anlegen("beton", "C30/37", eigen=True)
        self.assertEqual((eigen.name, eigen.sorte, eigen.eigenstaendig), ("BE1", "C30/37", True))
        self.assertEqual(projekt.material_anlegen("holz", "GL24h").kennung, "h1")
        with self.assertRaisesRegex(ProjektFehler, "Eine Materialart 'mauerwerk' gibt es nicht"):
            projekt.material_anlegen("mauerwerk", "MB")


class TestKopieren(unittest.TestCase):

    def test_gleich_hinter_dem_original(self):
        projekt = mit_sandboxen()
        original = projekt.querschnitte[1]
        kopie = projekt.eintrag_kopieren(original.kennung)
        self.assertIs(projekt.querschnitte[2], kopie)
        self.assertEqual(kopie.name, f"{original.name} (Kopie)")
        self.assertEqual(kopie.h, original.h)
        self.assertNotEqual(kopie.kennung, original.kennung)
        self.assertEqual(projekt.eintrag_kopieren(original.kennung).name,
                         f"{original.name} (Kopie 2)")

    def test_die_kopie_der_sandbox_ist_ein_gewoehnlicher_eintrag(self):
        projekt = mit_sandboxen()
        kopie = projekt.eintrag_kopieren(projekt.sandboxen["querschnitte"])
        self.assertEqual(kopie.name, "Platte 1")
        self.assertFalse(projekt.ist_sandbox(kopie.kennung))

    def test_ein_material_hat_keine_app(self):
        with self.assertRaisesRegex(ProjektFehler, "in keiner App"):
            mit_sandboxen().eintrag_kopieren("b1")


class TestLoeschen(unittest.TestCase):

    def test_ein_eintrag_geht(self):
        projekt = mit_sandboxen()
        kennung = projekt.querschnitte[1].kennung
        self.assertEqual(projekt.eintrag_loeschen(kennung).kennung, kennung)
        self.assertNotIn(kennung, [q.kennung for q in projekt.querschnitte])

    def test_nicht_die_sandbox(self):
        projekt = mit_sandboxen()
        with self.assertRaisesRegex(ProjektFehler, f"Platte '{SANDBOX}': die Sandbox lässt sich "
                                                   f"nicht löschen, nur zurücksetzen."):
            projekt.eintrag_loeschen(projekt.sandboxen["querschnitte"])

    def test_nicht_worauf_ein_bauteil_zeigt(self):
        """Die Meldung nennt, wer darauf zeigt -- mit Namen."""
        with self.assertRaisesRegex(ProjektFehler, r"Material 'C30/37': bleibt, solange noch "
                                                   r"darauf zeigt: Platte 'Decke über EG'"):
            mit_sandboxen().eintrag_loeschen("b1")

    def test_eine_kennung_die_es_nicht_gibt(self):
        with self.assertRaisesRegex(ProjektFehler, "Einen Eintrag 'x9' gibt es im Projekt nicht."):
            mit_sandboxen().eintrag_loeschen("x9")


class TestNur(unittest.TestCase):
    """Ein Bauteil allein -- mit denen, deren Querschnitt es nimmt."""

    def test_ein_system_behaelt_die_analyse_seines_stabs(self):
        projekt = Projekt.beispiel()
        system = projekt.balkensysteme[0]
        self.assertTrue(system.bezuege())
        allein = projekt.nur(system.kennung)
        self.assertEqual({e.kennung for e in allein.bauteile()},
                         {system.kennung, *system.bezuege()})

    def test_die_herleitung_eines_eintrags(self):
        """Der Bericht mit ``nur``: dieses Bauteil, nicht die anderen."""
        projekt = Projekt.beispiel()
        rumpf = {"projekt": projekt.als_dict(), "nur": projekt.grundbrueche[0].kennung}
        text = dienst.bearbeite("bericht", rumpf).daten["markdown"]
        self.assertIn(projekt.grundbrueche[0].name, text)
        self.assertNotIn(projekt.querschnitte[0].name, text)


if __name__ == "__main__":
    unittest.main()
