"""
Nur neu rechnen, was sich geändert hat.

Die eine Zusage des Zwischenspeichers ist nicht „schneller", sondern
**gleich**: die Antwort mit Speicher muss Zeichen für Zeichen dieselbe sein
wie die ohne. Alles andere wäre ein Werkzeug, das je nach Vorgeschichte
verschiedene Zahlen zeigt -- und das ist schlimmer als ein langsames.

Darum prüft der Kern dieser Datei eine Folge von Änderungen: jede einmal mit
warmem Speicher, einmal aus dem Kalten, und die beiden Antworten gegeneinander.
"""

import copy
import dataclasses
import json
import unittest

from opencivil.projekt import KnickEintrag, Projekt, QuerschnittEintrag
from opencivil.web import dienst, speicher


def projekt_mit_zwei_platten() -> dict:
    """
    Zwei Platten, die sich unterscheiden -- sonst merkt man nichts.

    Ohne Knickfall: seine Grenzkraft kostet je kalten Lauf zwei Sekunden, und
    fast jeder Test hier rechnet kalt. Die Änderung, die ihn braucht, legt ihn
    selbst an.
    """
    p = Projekt.beispiel()
    zweite = copy.deepcopy(p.querschnitte[0])
    zweite.kennung, zweite.name = "q2", "Platte 2"
    zweite.rissanforderung = "hoch"
    zweite.zwaengung = True
    p.querschnitte.append(zweite)
    for k in p.querschnitte[0].kombinationen:
        k.V_Ed = 80.0
    p.querschnitte[0].querkraftbewehrung.durchmesser = 10
    return p.als_dict()


def _anders(wert):
    """Irgendein anderer Wert derselben Art -- egal welcher, Hauptsache neu."""
    if isinstance(wert, bool):
        return not wert
    if isinstance(wert, (int, float)):
        return wert + 1
    if isinstance(wert, str):
        return wert + "!"
    if isinstance(wert, list):
        return wert[1:] if wert else [1]
    return None if wert is not None else 1


def rechnen(beschreibung: dict, *, frisch: bool):
    if frisch:
        dienst.SPEICHER.leeren()
    return dienst.bearbeite("rechnen", {"projekt": copy.deepcopy(beschreibung)})


def als_text(antwort) -> str:
    return json.dumps(antwort.daten, sort_keys=True, default=str)


#: Änderungen, die je eine andere Ecke der Beschreibung anfassen.
AENDERUNGEN = [
    ("gar nichts", lambda d: None),
    ("Dicke der 1. Platte", lambda d: d["querschnitte"][0].__setitem__("h", 320)),
    ("Moment der 2. Platte",
     lambda d: d["querschnitte"][1]["kombinationen"][0].__setitem__("M_Ed", 140)),
    ("Betonsorte", lambda d: (d["materialien"][0].__setitem__("sorte", "C25/30"),
                              d["materialien"][0].__setitem__("name", "C25/30"))),
    ("Durchmesser einer Lage",
     lambda d: d["querschnitte"][0]["lagen"][0]["grund"].__setitem__("durchmesser", 20)),
    ("ein Nachweisschalter",
     lambda d: d["querschnitte"][1].__setitem__("duktilitaet", True)),
    ("ein Knickfall kommt dazu",
     lambda d: d["querschnitte"][1]["knickfaelle"].append(dataclasses.asdict(
         KnickEintrag("Stütze", N_Ed=-900.0, M_Ed_1=25.0, laenge=4.0, knicklaenge=4.0)))),
    ("Normalkraft des Knickfalls",
     lambda d: d["querschnitte"][1]["knickfaelle"][0].__setitem__("N_Ed", -1400.0)),
    ("eine gelöschte Platte", lambda d: d["querschnitte"].pop()),
]


class TestDasselbeErgebnis(unittest.TestCase):
    def test_jede_aenderung_liefert_mit_und_ohne_speicher_dasselbe(self):
        beschreibung = projekt_mit_zwei_platten()
        dienst.SPEICHER.leeren()
        for name, aendern in AENDERUNGEN:
            aendern(beschreibung)
            mit = rechnen(beschreibung, frisch=False)
            ohne = rechnen(beschreibung, frisch=True)
            with self.subTest(aenderung=name):
                self.assertEqual(mit.status, 200)
                self.assertEqual(als_text(mit), als_text(ohne))
            # Warm für die nächste Runde -- geprüft wird ja der warme Fall.
            # Der Textvergleich umfasst das ganze Protokoll samt Reihenfolge
            # der Blöcke: daran hängt der Bericht.
            rechnen(beschreibung, frisch=False)


class TestWasUebernommenWird(unittest.TestCase):
    def test_eine_unveraenderte_platte_wird_uebernommen(self):
        beschreibung = projekt_mit_zwei_platten()
        rechnen(beschreibung, frisch=True)
        dienst.SPEICHER.treffer = 0
        rechnen(beschreibung, frisch=False)
        self.assertEqual(dienst.SPEICHER.treffer, 2)

    def test_die_geaenderte_platte_wird_neu_gerechnet(self):
        beschreibung = projekt_mit_zwei_platten()
        rechnen(beschreibung, frisch=True)
        dienst.SPEICHER.treffer = dienst.SPEICHER.fehlgriffe = 0
        beschreibung["querschnitte"][0]["h"] = 340
        rechnen(beschreibung, frisch=False)
        self.assertEqual(dienst.SPEICHER.treffer, 1)      # die andere gilt noch
        self.assertEqual(dienst.SPEICHER.fehlgriffe, 1)

    def test_ein_geaendertes_material_verwirft_alle_platten(self):
        """
        Grob mit Absicht: welche Lage welches Material benutzt, steht in
        derselben Beschreibung. Ein Vergleich, der das erst auflösen müsste,
        wäre die Stelle, an der man eines vergisst.
        """
        beschreibung = projekt_mit_zwei_platten()
        rechnen(beschreibung, frisch=True)
        dienst.SPEICHER.treffer = dienst.SPEICHER.fehlgriffe = 0
        beschreibung["materialien"][0]["sorte"] = "C25/30"
        beschreibung["materialien"][0]["name"] = "C25/30"
        rechnen(beschreibung, frisch=False)
        self.assertEqual(dienst.SPEICHER.treffer, 0)
        self.assertEqual(dienst.SPEICHER.fehlgriffe, 2)

    def test_eine_geloeschte_platte_raeumt_ihren_platz(self):
        beschreibung = projekt_mit_zwei_platten()
        rechnen(beschreibung, frisch=True)
        self.assertEqual(dienst.SPEICHER.belegt, 2)
        beschreibung["querschnitte"].pop()
        rechnen(beschreibung, frisch=False)
        self.assertEqual(dienst.SPEICHER.belegt, 1)

    def test_eine_rueckverfolgung_fuellt_den_speicher_nicht(self):
        """
        Ein Teillauf rechnet absichtlich nicht alles. Ihn als ganzes Ergebnis
        aufzubewahren wäre der Weg zu Zahlen, die niemand erklären kann.
        """
        beschreibung = projekt_mit_zwei_platten()
        dienst.SPEICHER.leeren()
        antwort = dienst.bearbeite("rechnen", {
            "projekt": beschreibung, "ziele": ["querschnitt.q1.h"]})
        self.assertEqual(antwort.status, 200)
        self.assertEqual(dienst.SPEICHER.belegt, 0)


class TestAbdruck(unittest.TestCase):
    def test_gleiche_beschreibung_gleicher_abdruck(self):
        d = projekt_mit_zwei_platten()
        self.assertEqual(speicher.abdruck(d, "q1"),
                         speicher.abdruck(copy.deepcopy(d), "q1"))

    def test_jedes_feld_der_platte_faellt_auf(self):
        """
        Der Abdruck muss **jede** Änderung sehen. Eine, die er übersieht,
        lässt das Bauteil als unverändert gelten und liefert stillschweigend
        eine alte Zahl -- von allen Fehlern der schlimmste.

        Darum keine Auswahl von Proben, sondern alle Felder der Datenklasse.
        Ein neues Feld ist damit automatisch mitgeprüft; vergessen kann man es
        nicht mehr.
        """
        for feld in dataclasses.fields(QuerschnittEintrag):
            if feld.name == "kennung":
                continue                       # die ist der Schlüssel selbst
            eintrag = QuerschnittEintrag.aus_dict(
                projekt_mit_zwei_platten()["querschnitte"][0])
            vorher = speicher.abdruck({"querschnitte": [eintrag.als_dict()],
                                       "materialien": []}, "q1")
            setattr(eintrag, feld.name, _anders(getattr(eintrag, feld.name)))
            nachher = speicher.abdruck({"querschnitte": [eintrag.als_dict()],
                                        "materialien": []}, "q1")
            with self.subTest(feld=feld.name):
                self.assertNotEqual(nachher, vorher)

    def test_auch_das_material_faellt_auf(self):
        d = projekt_mit_zwei_platten()
        vorher = speicher.abdruck(d, "q1")
        d["materialien"][0]["ueberschreibungen"] = {"f_ck": 33.0}
        self.assertNotEqual(speicher.abdruck(d, "q1"), vorher)

    def test_eine_andere_platte_aendert_den_abdruck_nicht(self):
        """Genau das ist der Punkt der Übung."""
        d = projekt_mit_zwei_platten()
        vorher = speicher.abdruck(d, "q1")
        d["querschnitte"][1]["h"] = 400
        self.assertEqual(speicher.abdruck(d, "q1"), vorher)


class TestPlaetze(unittest.TestCase):
    def test_der_speicher_waechst_nicht_ohne_ende(self):
        s = speicher.Ergebnisspeicher(plaetze=2)
        for i in range(5):
            s.merken(f"q{i}", "a", speicher.Teilergebnis())
        self.assertEqual(s.belegt, 2)
        self.assertIsNone(s.hole("q0", "a"))
        self.assertIsNotNone(s.hole("q4", "a"))


class TestMitgebrachteWerte(unittest.TestCase):
    """Das Mittel, mit dem mehrere Läufe zu einer Herleitung werden."""

    def test_ein_mitgebrachter_wert_wird_nicht_erneut_hergeleitet(self):
        aufbau = Projekt.beispiel().aufbauen()
        ziel = aufbau.materialziele()[0]
        einmal = aufbau.werk.loese(ziel)
        self.assertTrue(einmal.protokoll.bloecke)

        nochmal = aufbau.werk.loese(ziel, bekannt=einmal.werte)
        self.assertEqual(nochmal.protokoll.bloecke, [])
        self.assertEqual(nochmal.werte[ziel].groesse.si,
                         einmal.werte[ziel].groesse.si)


if __name__ == "__main__":
    unittest.main()
