"""
Der MCP-Zugang (opencivil/mcp): eine KI öffnet eine Projektdatei, legt an,
ändert, rechnet und speichert -- über JSON-RPC, eine Nachricht je Zeile.

Zuerst eine ganze Sitzung mit dem Server als eigenem Prozess, wie Claude Code
ihn startet; danach die Werkzeuge einzeln, mit dem Server im selben Prozess.
Jede Änderung prüft der Kern sofort: was er nicht lesen kann, ändert nichts,
und seine Meldung kommt unverändert zurück.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from opencivil.mcp.ausgabe import _stand
from opencivil.mcp.server import FASSUNGEN, Server
from opencivil.mcp.werkzeuge import WERKZEUGE

WURZEL = Path(__file__).resolve().parents[1]


def anfrage(kennung, methode, **parameter):
    return {"jsonrpc": "2.0", "id": kennung, "method": methode, "params": parameter}


def aufruf(kennung, werkzeug, **argumente):
    return anfrage(kennung, "tools/call", name=werkzeug, arguments=argumente)


class TestEineSitzung(unittest.TestCase):
    """Der Server als Prozess: alle Nachrichten hinein, je Anfrage eine Antwort heraus."""

    @classmethod
    def setUpClass(cls):
        ordner = tempfile.TemporaryDirectory()
        cls.addClassCleanup(ordner.cleanup)
        cls.datei = Path(ordner.name, "probe.json")
        nachrichten = [
            anfrage(1, "initialize", protocolVersion="2025-03-26", capabilities={},
                    clientInfo={"name": "test", "version": "0"}),
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            anfrage(2, "tools/list"),
            aufruf(3, "datei_neu"),
            aufruf(4, "eintrag_anlegen", app="Platte"),
            aufruf(5, "eintrag_aendern", eintrag="Platte 1", aenderungen=[
                {"pfad": "/h", "wert": 250}, {"pfad": "/kombinationen/0/M_Ed", "wert": 40}]),
            aufruf(6, "eintrag_aendern", eintrag="Platte 1",
                   aenderungen=[{"pfad": "/hh", "wert": 260}]),
            aufruf(7, "rechnen"),
            aufruf(8, "eintrag_loeschen", eintrag="Sandbox", app="querschnitte"),
            aufruf(9, "datei_speichern", pfad=str(cls.datei)),
            aufruf(10, "datei_neu"),
            aufruf(11, "datei_oeffnen", pfad=str(cls.datei)),
            aufruf(12, "eintrag_lesen", eintrag="Platte 1"),
            anfrage(13, "ping"),
            aufruf(14, "gibt_es_nicht"),
            anfrage(15, "resources/list"),
        ]
        zeilen = [json.dumps(n, ensure_ascii=False) for n in nachrichten] + ["kein JSON"]
        lauf = subprocess.run([sys.executable, "-m", "opencivil.mcp"], cwd=WURZEL,
                              input="\n".join(zeilen) + "\n", capture_output=True, text=True,
                              timeout=300)
        if lauf.returncode:
            raise AssertionError(lauf.stderr)
        cls.antworten = [json.loads(z) for z in lauf.stdout.splitlines()]
        cls.je_kennung = {a["id"]: a for a in cls.antworten}

    def text(self, kennung):
        ergebnis = self.je_kennung[kennung]["result"]
        return ergebnis["content"][0]["text"], ergebnis["isError"]

    def test_eine_antwort_je_anfrage_keine_auf_die_mitteilung(self):
        """15 Anfragen und eine unlesbare Zeile -- die Mitteilung bleibt ohne Antwort."""
        self.assertEqual([a["id"] for a in self.antworten], [*range(1, 16), None])

    def test_beginnen(self):
        ergebnis = self.je_kennung[1]["result"]
        self.assertEqual(ergebnis["protocolVersion"], "2025-03-26")
        self.assertEqual(ergebnis["serverInfo"]["name"], "opencivil")
        self.assertIn("tools", ergebnis["capabilities"])
        self.assertIn("Sandbox", ergebnis["instructions"])

    def test_die_werkzeuge(self):
        namen = [w["name"] for w in self.je_kennung[2]["result"]["tools"]]
        self.assertEqual(namen, list(WERKZEUGE))
        for name in ("datei_oeffnen", "eintrag_aendern", "rechnen", "herleitung", "bericht"):
            self.assertIn(name, namen)

    def test_anlegen_aendern_rechnen(self):
        self.assertEqual(self.text(4), ("Angelegt: Platte 'Platte 1' (q2).", False))
        self.assertEqual(self.text(5), ("Geändert: Platte 'Platte 1' (q2).", False))
        rechnung, fehler = self.text(7)
        self.assertFalse(fehler)
        self.assertIn("## Platte 'Platte 1' (q2) – ", rechnung)
        self.assertIn("| Nachweis | Bezeichnung | Widerstand | Einwirkung |", rechnung)
        self.assertNotIn("Sandbox", rechnung.split("\n\n", 2)[2])

    def test_ein_falsches_feld_aendert_nichts(self):
        """Die Meldung des Kerns, unverändert -- und h bleibt, was es war."""
        self.assertEqual(self.text(6), (
            "Platte 'Platte 1': ein Feld 'hh' gibt es nicht. Gemeint ist vielleicht 'h'?", True))
        self.assertEqual(json.loads(self.text(12)[0])["h"], 250)

    def test_die_sandbox_bleibt(self):
        meldung, fehler = self.text(8)
        self.assertTrue(fehler)
        self.assertEqual(meldung, "Platte 'Sandbox': die Sandbox lässt sich nicht löschen, nur "
                                  "zurücksetzen.")

    def test_gespeichert_und_wieder_geoeffnet(self):
        self.assertEqual(self.text(9), (f"Gespeichert: {self.datei}.", False))
        gespeichert = json.loads(self.datei.read_text(encoding="utf-8"))
        platte = gespeichert["projekte"][0]["querschnitte"][1]
        self.assertEqual((platte["name"], platte["h"]), ("Platte 1", 250))
        self.assertTrue(self.text(11)[0].startswith(f"Geöffnet. Mappe: Datei {self.datei}. "))

    def test_was_das_protokoll_abweist(self):
        self.assertEqual(self.je_kennung[13]["result"], {})
        self.assertEqual(self.je_kennung[14]["error"]["code"], -32602)
        self.assertEqual(self.je_kennung[15]["error"]["code"], -32601)
        self.assertEqual(self.antworten[-1]["error"]["code"], -32700)


class Verbindung:
    """Der Server im selben Prozess -- je Test einer, mit einer neuen Mappe und einer Platte."""

    def __init__(self):
        self.server = Server()
        self.n = 0

    def frage(self, methode, **parameter):
        self.n += 1
        return self.server.antwort(anfrage(self.n, methode, **parameter))

    def werkzeug(self, werkzeug, **argumente):
        """Text und ob es ein Fehler ist."""
        ergebnis = self.frage("tools/call", name=werkzeug, arguments=argumente)["result"]
        return ergebnis["content"][0]["text"], ergebnis["isError"]


class TestWerkzeuge(unittest.TestCase):

    def setUp(self):
        self.v = Verbindung()
        self.v.werkzeug("datei_neu")
        self.v.werkzeug("eintrag_anlegen", app="querschnitte")
        ordner = tempfile.TemporaryDirectory()
        self.addCleanup(ordner.cleanup)
        self.ordner = Path(ordner.name)

    def gut(self, werkzeug, **argumente):
        text, fehler = self.v.werkzeug(werkzeug, **argumente)
        self.assertFalse(fehler, text)
        return text

    def schlecht(self, werkzeug, **argumente):
        text, fehler = self.v.werkzeug(werkzeug, **argumente)
        self.assertTrue(fehler, text)
        return text

    def platte(self):
        return json.loads(self.gut("eintrag_lesen", eintrag="Platte 1"))

    # -- Protokoll und Argumente -------------------------------------------

    def test_die_fassung_des_programms_oder_die_neueste(self):
        for gewuenscht, gesprochen in (("2024-11-05", "2024-11-05"), ("1999-01-01", FASSUNGEN[0])):
            antwort = self.v.frage("initialize", protocolVersion=gewuenscht)
            self.assertEqual(antwort["result"]["protocolVersion"], gesprochen)

    def test_jedes_werkzeug_beschreibt_seine_eingaben(self):
        for werkzeug in self.v.frage("tools/list")["result"]["tools"]:
            with self.subTest(werkzeug["name"]):
                schema = werkzeug["inputSchema"]
                self.assertTrue(set(schema["required"]) <= set(schema["properties"]))
                self.assertFalse(schema["additionalProperties"])
                self.assertTrue(werkzeug["description"])
                self.assertTrue(all(e.get("description") for e in schema["properties"].values()))

    def test_argumente_die_nicht_passen(self):
        self.assertEqual(self.schlecht("datei_oeffnen", pfadd="x"),
                         "datei_oeffnen: ein Argument «pfadd» gibt es nicht. Gemeint ist "
                         "vielleicht «pfad»? Möglich sind: pfad, verwerfen.")
        self.assertIn("es fehlt «pfad»", self.schlecht("datei_oeffnen"))
        self.assertEqual(self.schlecht("datei_oeffnen", pfad=5), "«pfad» ist Text, nicht 5.")
        self.assertEqual(self.schlecht("bericht", als="pdf"),
                         "«als» ist eines von markdown, latex, nicht «pdf».")
        self.assertIn("«wert» oder «entfernen: true»",
                      self.schlecht("eintrag_aendern", eintrag="Platte 1", aenderungen=[{"pfad": "/h"}]))

    # -- Datei und Projekte -------------------------------------------------

    def test_ohne_offene_datei(self):
        for werkzeug in ("eintraege", "projekte", "datei_speichern"):
            self.assertEqual(Verbindung().werkzeug(werkzeug), (
                "Noch ist keine Projektdatei offen – zuerst datei_oeffnen oder datei_neu.", True))
        self.assertFalse(Verbindung().werkzeug("arten")[1])

    def test_ungespeichertes_geht_nicht_still_verloren(self):
        self.assertIn("noch nicht gespeichert", self.schlecht("datei_neu"))
        self.gut("datei_neu", verwerfen=True)
        self.assertNotIn("Platte 1", self.gut("eintraege", app="Platte"))

    def test_eine_fremde_datei_nur_auf_wunsch_ueberschreiben(self):
        fremd = self.ordner / "fremd.json"
        fremd.write_text("{}", encoding="utf-8")
        self.assertIn("gibt es schon", self.schlecht("datei_speichern", pfad=str(fremd)))
        self.assertEqual(fremd.read_text(encoding="utf-8"), "{}")
        self.gut("datei_speichern", pfad=str(fremd), ueberschreiben=True)
        self.gut("eintrag_aendern", eintrag="Platte 1", aenderungen=[{"pfad": "/h", "wert": 280}])
        self.gut("datei_speichern")         # die eigene: ohne Rückfrage
        self.assertEqual(json.loads(fremd.read_text(encoding="utf-8"))["projekte"][0]
                         ["querschnitte"][1]["h"], 280)

    def test_projekte(self):
        self.assertIn("«Projekt 2»", self.gut("projekt_anlegen"))
        self.assertIn("heissen beide 'Projekt 1'", self.schlecht("projekt_anlegen", name="Projekt 1"))
        self.gut("projekt_waehlen", name="Projekt 1")
        self.assertEqual(self.gut("projekte"), "Mappe: noch ohne Datei, ungespeichert. 2 Projekte: "
                                               "«Projekt 1» (gewählt), «Projekt 2».")
        self.assertIn("Gemeint ist vielleicht «Projekt 2»?",
                      self.schlecht("projekt_waehlen", name="Projekt 3"))

    # -- Eintraege ----------------------------------------------------------

    def test_ein_name_in_mehreren_apps(self):
        meldung = self.schlecht("eintrag_lesen", eintrag="Sandbox")
        self.assertTrue(meldung.startswith("«Sandbox» heissen mehrere: Platte 'Sandbox' (q1), "))
        self.assertEqual(json.loads(self.gut("eintrag_lesen", eintrag="Sandbox", app="Platte"))
                         ["kennung"], "q1")

    def test_ein_name_den_es_nicht_gibt(self):
        self.assertEqual(self.schlecht("eintrag_lesen", eintrag="Platte1"),
                         "Einen Eintrag «Platte1» gibt es im Projekt «Projekt 1» nicht. Gemeint "
                         "ist vielleicht «Platte 1»?")

    def test_alle_aenderungen_oder_keine(self):
        self.schlecht("eintrag_aendern", eintrag="Platte 1",
                      aenderungen=[{"pfad": "/h", "wert": 260}, {"pfad": "/hh", "wert": 1}])
        self.assertEqual(self.platte()["h"], 300)

    def test_was_nur_den_eintrag_anhaelt_gilt_und_sagt_es(self):
        """Der Rest rechnet weiter -- die Antwort sagt gleich, was nicht stimmt."""
        self.assertEqual(self.gut("eintrag_aendern", eintrag="q2",
                                  aenderungen=[{"pfad": "/h", "wert": -5}]),
                         "Geändert: Platte 'Platte 1' (q2).\n- Platte 'Platte 1': Dicke h muss "
                         "grösser als null sein, angegeben ist -5 mm → nichts zu rechnen.")

    def test_was_das_ganze_projekt_anhielte_gilt_nicht(self):
        """Zwei Materialien mit einem Namen -- die Seite weist das schon am Feld ab."""
        self.gut("material_anlegen", art="beton", sorte="C35/45")
        meldung = self.schlecht("eintrag_aendern", eintrag="C35/45",
                                aenderungen=[{"pfad": "/name", "wert": "C25/30"}])
        self.assertIn("Der Name 'C25/30' ist zweimal vergeben", meldung)
        self.assertIn("C35/45 (b2, Beton)", self.gut("eintraege", app="materialien"))

    def test_pfade_in_listen(self):
        self.gut("eintrag_aendern", eintrag="Platte 1", aenderungen=[
            {"pfad": "/kombinationen/-", "wert": {"name": "Neu", "M_Ed": 10}},
            {"pfad": "/kombinationen/0", "entfernen": True}])
        self.assertEqual([k["name"] for k in self.platte()["kombinationen"]], ["Neu"])
        self.assertEqual(self.schlecht("eintrag_aendern", eintrag="Platte 1",
                                       aenderungen=[{"pfad": "/kombinationen/4/M_Ed", "wert": 1}]),
                         "Pfad '/kombinationen/4/M_Ed': die Liste hat 1 Einträge, 0 bis 0.")

    def test_ganz_ersetzen_die_kennung_bleibt(self):
        inhalt = {**self.platte(), "h": 320}
        self.gut("eintrag_setzen", eintrag="Platte 1", inhalt=inhalt)
        self.assertEqual(self.platte()["h"], 320)
        self.assertIn("die Kennung bleibt 'q2'",
                      self.schlecht("eintrag_setzen", eintrag="Platte 1", inhalt={**inhalt, "kennung": "q9"}))

    def test_kopieren_loeschen_zuruecksetzen(self):
        self.assertEqual(self.gut("eintrag_kopieren", eintrag="Platte 1"),
                         "Kopiert: Platte 'Platte 1 (Kopie)' (q3).")
        self.assertEqual(self.gut("eintrag_loeschen", eintrag="q3"), "Gelöscht: Platte 'Platte 1 (Kopie)' (q3).")
        self.gut("eintrag_aendern", eintrag="q1", aenderungen=[{"pfad": "/h", "wert": 444}])
        self.gut("sandbox_zuruecksetzen", app="Platte")
        self.assertEqual(json.loads(self.gut("eintrag_lesen", eintrag="q1"))["h"], 300)

    def test_was_ein_material_nicht_kann(self):
        self.assertIn("material_anlegen", self.schlecht("eintrag_anlegen", app="materialien"))
        self.assertIn("rechnet nicht für sich", self.schlecht("rechnen", eintrag="C25/30"))

    def test_felder(self):
        felder = json.loads(self.gut("felder", art="Platte"))
        self.assertEqual(felder["klasse"], "querschnitt")
        self.assertEqual(felder["felder"]["h"]["einheit"], "mm")
        self.assertEqual(felder["felder"]["kombinationen"]["von"]["klasse"], "kombination")
        self.assertEqual(json.loads(self.gut("felder", art="kombination"))["neu"]["M_Ed"], 0.0)

    # -- Rechnen und Bericht -----------------------------------------------

    def test_ein_eintrag_allein_auch_die_sandbox(self):
        rechnung = self.gut("rechnen", eintrag="Sandbox", app="Platte")
        self.assertIn("## Platte 'Sandbox' (q1)", rechnung)
        self.assertNotIn("Platte 1", rechnung)

    def test_herleitung_und_bericht_auch_als_datei(self):
        self.assertIn("Platte 1", self.gut("herleitung", eintrag="Platte 1"))
        ziel = self.ordner / "bericht.tex"
        self.assertTrue(self.gut("bericht", als="latex", pfad=str(ziel)).startswith(f"Geschrieben: {ziel}"))
        self.assertIn(r"\documentclass", ziel.read_text(encoding="utf-8"))
        self.assertIn("gibt es schon", self.schlecht("bericht", pfad=str(ziel)))



class TestStand(unittest.TestCase):
    """Der Stand in der Kopfzeile: was sich nicht führen liess, zählt für sich."""

    def test_nicht_erfuellt_und_nicht_gefuehrt_getrennt(self):
        ja, nein = {"erfuellt": True, "offen": False}, {"erfuellt": False, "offen": False}
        offen = {"erfuellt": False, "offen": True}
        for urteile, text in (([], "kein Nachweis"), ([ja], "1 Nachweis, erfüllt"),
                              ([ja, ja], "2 Nachweise, alle erfüllt"),
                              ([nein, ja], "1 von 2 Nachweisen nicht erfüllt"),
                              ([offen, ja], "1 von 2 Nachweisen nicht geführt"),
                              ([nein, offen, offen, ja],
                               "1 von 4 Nachweisen nicht erfüllt, 2 nicht geführt")):
            with self.subTest(text=text):
                self.assertEqual(_stand(urteile), text)


if __name__ == "__main__":
    unittest.main()
