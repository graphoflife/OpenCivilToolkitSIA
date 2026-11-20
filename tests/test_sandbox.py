"""
Die Sandbox: in jedem Projekt je App ein Eintrag zum Ausprobieren.

Sie steht zuoberst in ihrer Liste und heisst immer «Sandbox». Zurücksetzen
lässt sie sich, löschen nicht, und nach jedem Laden der Seite beginnt sie
neu. Im Bericht steht sie nicht, und sie hält nichts fest: weder ein
Material noch eine Platte bleibt ihretwegen stehen.
"""

import copy
import unittest

from opencivil.projekt import Projekt, ProjektFehler
from opencivil.projekt.projekt import APPLISTEN, SANDBOX
from opencivil.projekt.staebe import Querschnittsart
from opencivil.web import api, dienst


def mit_sandboxen(projekt=None):
    """Das Beispiel -- oder ``projekt`` -- mit allen Sandboxen, wie die Seite es zeigt."""
    projekt = projekt or Projekt.beispiel()
    projekt.sandboxen_anlegen()
    return projekt


def rechnen(projekt):
    antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
    assert antwort.status == 200, antwort.daten
    return antwort.daten


class TestAnlegen(unittest.TestCase):
    def test_je_app_eine_zuoberst(self):
        projekt = mit_sandboxen()
        self.assertEqual(set(projekt.sandboxen), set(APPLISTEN))
        self.assertNotIn("materialien", projekt.sandboxen)
        for liste, kennung in projekt.sandboxen.items():
            with self.subTest(liste=liste):
                erste = getattr(projekt, liste)[0]
                self.assertEqual((erste.kennung, erste.name), (kennung, SANDBOX))
        projekt.pruefen()

    def test_vorhandene_bleiben_frisch_beginnen_alle(self):
        projekt = mit_sandboxen()
        sandbox = projekt.querschnitte[0]
        sandbox.h = 444.0
        projekt.sandboxen_anlegen()
        self.assertIs(projekt.querschnitte[0], sandbox)
        projekt.sandboxen_anlegen(frisch=True)
        self.assertEqual((projekt.querschnitte[0].kennung, projekt.querschnitte[0].h),
                         (sandbox.kennung, 300.0))

    def test_mit_dem_ersten_material_jeder_art(self):
        """Wie ein neuer Eintrag der Oberfläche -- so rechnet die Platte gleich."""
        projekt = mit_sandboxen()
        erstes = {art: next(m.kennung for m in projekt.materialien if m.art == art)
                  for art in ("beton", "betonstahl")}
        platte = projekt.querschnitte[0]
        self.assertEqual((platte.beton, platte.stahl), (erstes["beton"], erstes["betonstahl"]))
        self.assertEqual(projekt.balkensysteme[0].stabmaterialien[0].stoff, erstes["beton"])
        self.assertEqual(projekt.pfaehle[0].beton, erstes["beton"])

    def test_ohne_material_bleibt_die_wahl_leer_und_der_rest_rechnet(self):
        """
        Den einzigen Beton hält die Sandbox nicht fest -- ohne ihn sagt sie am
        Ort, was fehlt. Bis 2026-11-20 hielt eine Platte ohne Beton das ganze
        Projekt an.
        """
        projekt = mit_sandboxen(Projekt.neu())
        projekt.materialien = [m for m in projekt.materialien if m.art != "beton"]
        projekt.sandboxen_anlegen(frisch=True)
        self.assertEqual(projekt.querschnitte[0].beton, "")
        unfertige = rechnen(projekt)["unfertige"]
        for liste in ("querschnitte", "durchstanzstellen"):
            with self.subTest(liste=liste):
                self.assertEqual(unfertige[liste][projekt.sandboxen[liste]]["grund"],
                                 "Beton: noch kein Material gewählt")


class TestZuruecksetzen(unittest.TestCase):
    def test_behaelt_kennung_namen_und_platz(self):
        projekt = mit_sandboxen()
        projekt.querschnitte.reverse()
        projekt.querschnitte[-1].h = 444.0
        frisch = projekt.sandbox_zuruecksetzen("querschnitte")
        self.assertIs(projekt.querschnitte[-1], frisch)
        self.assertEqual(frisch.als_dict(), mit_sandboxen().querschnitte[0].als_dict())

    def test_nur_fuer_eine_app(self):
        with self.assertRaisesRegex(ProjektFehler, "ausser den Materialien"):
            mit_sandboxen().sandbox_zuruecksetzen("materialien")

    def test_ueber_den_dienst(self):
        projekt = mit_sandboxen()
        projekt.querschnitte[0].h = 444.0
        antwort = dienst.bearbeite("sandbox_zuruecksetzen",
                                   {"projekt": projekt.als_dict(), "liste": "querschnitte"})
        eintrag = antwort.daten["eintrag"]
        self.assertEqual((eintrag["kennung"], eintrag["name"], eintrag["h"]),
                         (projekt.sandboxen["querschnitte"], SANDBOX, 300.0))
        falsch = dienst.bearbeite("sandbox_zuruecksetzen",
                                  {"projekt": projekt.als_dict(), "liste": "materialien"})
        self.assertEqual(falsch.status, 400)


class TestNichtImProjekt(unittest.TestCase):
    """Was das Projekt zusammenfasst, lässt sie aus; sie selbst rechnet wie jedes Bauteil."""

    @classmethod
    def setUpClass(cls):
        # Die Sandbox der Platten bekommt die Platte des Beispiels: ohne die
        # Ausnahme stünde sie im Bericht.
        cls.projekt = mit_sandboxen()
        platte = copy.deepcopy(cls.projekt.querschnitte[1])
        platte.kennung, platte.name = cls.projekt.sandboxen["querschnitte"], SANDBOX
        cls.projekt.querschnitte[0] = platte

    def test_sie_rechnet(self):
        kennung = self.projekt.sandboxen["querschnitte"]
        self.assertIn(kennung, rechnen(self.projekt)["zusammenfassungen"])

    def test_nicht_im_bericht(self):
        antwort = dienst.bearbeite("bericht", {"projekt": self.projekt.als_dict()})
        self.assertNotIn(SANDBOX, antwort.daten["markdown"])
        self.assertIn(self.projekt.querschnitte[1].name, antwort.daten["markdown"])

    def test_ihre_warnung_traegt_ihren_namensraum(self):
        """Daran lässt die Oberfläche sie unter «Gesamt» weg, wie ihre Abschnitte."""
        projekt = mit_sandboxen()
        analyse = projekt.sandboxen["querschnittsanalysen"]
        self.assertIn({"raum": f"querschnittsanalyse.{analyse}",
                       "text": "Querschnittsanalyse 'Sandbox': noch nichts gezeichnet → "
                               "nichts zu rechnen."}, rechnen(projekt)["warnungen"])

    def test_nicht_in_den_urteilen_des_projekts(self):
        sandboxen = set(self.projekt.sandboxen.values())
        urteile = self.projekt.rechnen().urteile
        self.assertTrue(urteile)
        self.assertFalse([u.raum for u in urteile if u.raum.split(".")[1] in sandboxen])

    def test_ohne_sandboxen(self):
        ohne = self.projekt.ohne_sandboxen()
        self.assertEqual(ohne.sandboxen, {})
        beispiel = Projekt.beispiel()
        for liste in APPLISTEN:
            with self.subTest(liste=liste):
                self.assertEqual([e.kennung for e in getattr(ohne, liste)],
                                 [e.kennung for e in getattr(beispiel, liste)])
        self.assertEqual(len(self.projekt.querschnitte), 2)


class TestHaeltNichtsFest(unittest.TestCase):
    def test_der_einzige_beton_laesst_sich_loeschen(self):
        """Sonst hielte die Sandbox der Platten ihn fest."""
        projekt = mit_sandboxen(Projekt.neu())
        beton = next(m for m in projekt.materialien if m.art == "beton")
        antwort = dienst.bearbeite("verweise",
                                   {"projekt": projekt.als_dict(), "kennung": beton.kennung})
        self.assertEqual(antwort.daten["verweise"], [])

    def test_ein_gewoehnlicher_eintrag_schon(self):
        projekt = mit_sandboxen()
        beton = projekt.querschnitte[1].beton
        self.assertIn(projekt.querschnitte[1], projekt.verweise(beton))
        self.assertNotIn(projekt.querschnitte[0], projekt.verweise(beton))

    def test_was_geloescht_ist_sagt_sie_selbst(self):
        """Mit Namen statt Kennung -- die stünde nirgends, wo man sie sähe."""
        projekt = mit_sandboxen()
        # In der Sandbox der Rahmen des Beispiels; dann gehen er und die
        # Analyse seines Unterzugs weg.
        rahmen = next(s for s in projekt.balkensysteme if not projekt.ist_sandbox(s.kennung))
        sandbox = copy.deepcopy(rahmen)
        sandbox.kennung, sandbox.name = projekt.sandboxen["balkensysteme"], SANDBOX
        projekt.balkensysteme = [sandbox]
        projekt.querschnittsanalysen = [a for a in projekt.querschnittsanalysen
                                        if projekt.ist_sandbox(a.kennung)]
        grund = rechnen(projekt)["unfertige"]["balkensysteme"][sandbox.kennung]["grund"]
        self.assertIn("«Unterzug» nimmt eine Querschnittsanalyse, die es nicht mehr gibt", grund)
        self.assertNotIn("'a", grund)


class TestQuerschnittAusDerSandbox(unittest.TestCase):
    """
    Nur eine Sandbox darf den Querschnitt einer Sandbox nehmen: die beginnt
    nach jedem Laden der Seite neu, und ein gewöhnliches Bauteil rechnete
    dann still mit anderem.
    """

    @classmethod
    def setUpClass(cls):
        projekt = mit_sandboxen()
        platte = projekt.sandboxen["querschnitte"]
        rahmen = next(s for s in projekt.balkensysteme if not projekt.ist_sandbox(s.kennung))
        for q in rahmen.querschnitte:
            if q.art.aus_bauteil:
                q.art, q.platte = Querschnittsart.PLATTE, platte
        # Die Sandbox der Balkensysteme bekommt denselben Rahmen.
        sandbox = copy.deepcopy(rahmen)
        sandbox.kennung, sandbox.name = projekt.sandboxen["balkensysteme"], SANDBOX
        projekt.balkensysteme[0] = sandbox
        cls.projekt, cls.rahmen, cls.sandbox = projekt, rahmen, sandbox
        cls.unfertige = rechnen(projekt)["unfertige"]["balkensysteme"]

    def test_ein_gewoehnliches_bauteil_nicht(self):
        grund = self.unfertige[self.rahmen.kennung]["grund"]
        self.assertIn("nimmt die Platte «Sandbox»", grund)
        self.assertIn("Kopie", grund)

    def test_eine_sandbox_schon(self):
        self.assertNotIn(self.sandbox.kennung, self.unfertige)


class TestPruefen(unittest.TestCase):
    def setUp(self):
        self.roh = mit_sandboxen().als_dict()

    def pruefen(self, muster):
        with self.assertRaisesRegex(ProjektFehler, muster):
            Projekt.aus_dict(self.roh).pruefen()

    def test_geloescht(self):
        self.roh["querschnitte"] = self.roh["querschnitte"][1:]
        self.pruefen("nur zurücksetzen")

    def test_umbenannt(self):
        self.roh["querschnitte"][0]["name"] = "Spielwiese"
        self.pruefen("heisst «Sandbox», nicht «Spielwiese»")

    def test_keine_bei_den_materialien(self):
        self.roh["sandboxen"]["materialien"] = self.roh["materialien"][0]["kennung"]
        self.pruefen("Liste 'materialien' hat keine")

    def test_ein_bauteil_allein(self):
        """Die Bewehrungssuche rechnet ein Bauteil allein -- mit oder ohne seine Sandbox."""
        projekt = mit_sandboxen()
        allein = projekt.nur(projekt.querschnitte[1].kennung)
        self.assertEqual(allein.sandboxen, {"skripte": projekt.sandboxen["skripte"]})
        allein.pruefen()
        sandbox = projekt.nur(projekt.sandboxen["querschnitte"])
        self.assertEqual(set(sandbox.sandboxen), {"querschnitte", "skripte"})
        sandbox.pruefen()


class TestOeffnen(unittest.TestCase):
    def test_fehlende_kommen_dazu(self):
        """Eine Datei von vor der Sandbox -- und eine neue Vorlage."""
        alt = Projekt.beispiel().als_dict()
        mappe = dienst.bearbeite("mappe_oeffnen", {"mappe": alt}).daten["mappe"]
        self.assertEqual(set(mappe["projekte"][0]["sandboxen"]), set(APPLISTEN))

    def test_wie_gespeichert_oder_frisch(self):
        """Öffnen stellt sie her, wie gespeichert; die Seite lädt sie frisch."""
        projekt = mit_sandboxen()
        projekt.querschnitte[0].h = 444.0
        roh = {"projekte": [projekt.als_dict()]}
        wie, frisch = (dienst.bearbeite("mappe_oeffnen", {"mappe": roh, "frisch": f})
                       .daten["mappe"]["projekte"][0] for f in (False, True))
        self.assertEqual((wie["querschnitte"][0]["h"], frisch["querschnitte"][0]["h"]),
                         (444.0, 300.0))
        self.assertEqual(frisch["querschnitte"][0]["kennung"], projekt.sandboxen["querschnitte"])
        self.assertEqual(frisch["querschnitte"][1:], wie["querschnitte"][1:])


class TestKatalog(unittest.TestCase):
    """Die Oberfläche legt Neues nach dem Katalog an -- mit denselben ersten Materialien."""

    def test_die_ersten_materialien(self):
        erste = api.katalog()["erste_materialien"]
        self.assertEqual(set(erste), set(APPLISTEN))
        self.assertEqual(erste["querschnitte"], {"beton": "beton", "stahl": "betonstahl"})
        self.assertEqual(erste["balkensysteme"], {"stabmaterialien/0/stoff": "beton"})
        self.assertEqual(erste["skripte"], {})


if __name__ == "__main__":
    unittest.main()
