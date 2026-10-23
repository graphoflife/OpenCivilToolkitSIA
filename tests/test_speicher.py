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

from opencivil.core.rechenwerk import Loesung
from opencivil.projekt import KnickEintrag, Projekt, QuerschnittEintrag
from opencivil.web import dienst, speicher


def projekt_mit_zwei_platten() -> dict:
    """
    Zwei Platten, die sich unterscheiden -- sonst merkt man nichts. Dazu der
    Unterzug, der Rahmen, das Fundament und seine Setzung des Beispiels: sechs
    Bauteile, jedes mit eigenem Platz im Speicher. Der Rahmen nimmt den
    Querschnitt des Unterzugs.

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
        dienst.ANALYSEN.leeren()
    return dienst.bearbeite("rechnen", {"projekt": copy.deepcopy(beschreibung)})


def projekt_mit_analysen() -> dict:
    """
    Dazu Analysen: an der ersten Platte ein Bild aus N und M und eine
    Momenten-Krümmungs-Linie, am Unterzug ein Bild. Die zweite Platte und
    das Fundament haben keine -- an ihnen sieht man, was nicht neu rechnen soll.
    """
    p = Projekt.aus_dict(projekt_mit_zwei_platten())
    p.querschnitte[0].spannungsfall("Bild", art="schnittgroessen", N_Ed=-200.0, M_Ed=60.0)
    p.querschnitte[0].spannungsfall("Linie", art="moment_kruemmung")
    p.querschnittsanalysen[0].spannungsfall("Bild", art="schnittgroessen", M_Ed=100.0)
    return p.als_dict()


def analysen_zaehlen(beschreibung: dict, aendern) -> tuple:
    """Warm gerechnet, geändert, nochmals: wie viele Analysen aus dem Speicher kamen, wie viele neu."""
    rechnen(beschreibung, frisch=True)
    dienst.ANALYSEN.treffer = dienst.ANALYSEN.fehlgriffe = 0
    aendern(beschreibung)
    antwort = rechnen(beschreibung, frisch=False)
    assert antwort.status == 200, antwort.daten
    return dienst.ANALYSEN.treffer, dienst.ANALYSEN.fehlgriffe


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
    ("Moment des Unterzugs",
     lambda d: d["querschnittsanalysen"][0]["lastfaelle"][0].__setitem__("M_y_Ed", 120.0)),
    ("ein Stab im Unterzug", lambda d: (
        d["querschnittsanalysen"][0]["knoten"].append({"kennung": "K99", "y": 150.0, "z": 300.0}),
        d["querschnittsanalysen"][0]["staebe"].append(
            {"kennung": "S99", "knoten": "K99", "durchmesser": 16.0, "stahl": "s1"}))),
    ("eine Last des Rahmens",
     lambda d: d["balkensysteme"][0]["linien"][1]["lasten"][0].__setitem__("wert_a", 30.0)),
    ("der Reibungswinkel des Fundaments",
     lambda d: d["grundbrueche"][0].__setitem__("phi_k", 28.0)),
    ("eine Schicht unter der Setzung",
     lambda d: d["setzungen"][0]["schichten"][1].__setitem__("M_E", 12.0)),
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
        self.assertEqual(dienst.SPEICHER.treffer, 6)

    def test_die_geaenderte_platte_wird_neu_gerechnet(self):
        beschreibung = projekt_mit_zwei_platten()
        rechnen(beschreibung, frisch=True)
        dienst.SPEICHER.treffer = dienst.SPEICHER.fehlgriffe = 0
        beschreibung["querschnitte"][0]["h"] = 340
        rechnen(beschreibung, frisch=False)
        self.assertEqual(dienst.SPEICHER.treffer, 5)      # die anderen gelten noch
        self.assertEqual(dienst.SPEICHER.fehlgriffe, 1)

    def test_die_geaenderte_analyse_wird_neu_gerechnet(self):
        beschreibung = projekt_mit_zwei_platten()
        rechnen(beschreibung, frisch=True)
        dienst.SPEICHER.treffer = dienst.SPEICHER.fehlgriffe = 0
        beschreibung["querschnittsanalysen"][0]["schubwaende"][0]["dicke"] = 120.0
        rechnen(beschreibung, frisch=False)
        self.assertEqual(dienst.SPEICHER.treffer, 4)      # Platten, Fundament, Setzung gelten noch
        # Die Analyse -- und der Rahmen, der ihren Querschnitt nimmt.
        self.assertEqual(dienst.SPEICHER.fehlgriffe, 2)

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
        self.assertEqual(dienst.SPEICHER.fehlgriffe, 6)

    def test_eine_geloeschte_platte_raeumt_ihren_platz(self):
        beschreibung = projekt_mit_zwei_platten()
        rechnen(beschreibung, frisch=True)
        self.assertEqual(dienst.SPEICHER.belegt, 6)
        beschreibung["querschnitte"].pop()
        rechnen(beschreibung, frisch=False)
        self.assertEqual(dienst.SPEICHER.belegt, 5)

    def test_eine_rueckverfolgung_fuellt_den_speicher_nicht(self):
        """
        Ein Teillauf rechnet absichtlich nicht alles. Ihn als ganzes Ergebnis
        aufzubewahren wäre der Weg zu Zahlen, die niemand erklären kann.
        """
        beschreibung = projekt_mit_analysen()
        dienst.SPEICHER.leeren()
        dienst.ANALYSEN.leeren()
        antwort = dienst.bearbeite("rechnen", {
            "projekt": beschreibung, "ziele": ["querschnitt.q1.h"]})
        self.assertEqual(antwort.status, 200)
        self.assertEqual(dienst.SPEICHER.belegt, 0)
        self.assertEqual(dienst.ANALYSEN.belegt, 0)


class TestAnalysenAusDemSpeicher(unittest.TestCase):
    """
    Die Spannung-Dehnung-Analysen eines Bauteils gelten, solange sein Abdruck
    derselbe ist -- wie seine Nachweise. Bis 2026-10-18 rechnete jede Rechnung
    alle neu: am Prüfprojekt zwei Drittel jeder Rechnung, auch nach einer
    Änderung an einem Bauteil ohne Analyse.
    """

    #: Änderungen, nach denen warm und kalt dasselbe herauskommen muss.
    AENDERUNGEN = [
        ("gar nichts", lambda d: None),
        ("Dicke der Platte ohne Analyse", lambda d: d["querschnitte"][1].__setitem__("h", 330)),
        ("Dicke der Platte mit Analysen", lambda d: d["querschnitte"][0].__setitem__("h", 320)),
        ("Moment einer Analyse",
         lambda d: d["querschnitte"][0]["spannungsfaelle"][0].__setitem__("M_Ed", 75.0)),
        ("Betonsorte", lambda d: (d["materialien"][0].__setitem__("sorte", "C25/30"),
                                  d["materialien"][0].__setitem__("name", "C25/30"))),
        ("ein Stab im Unterzug", lambda d: (
            d["querschnittsanalysen"][0]["knoten"].append({"kennung": "K99", "y": 150.0, "z": 300.0}),
            d["querschnittsanalysen"][0]["staebe"].append(
                {"kennung": "S99", "knoten": "K99", "durchmesser": 16.0, "stahl": "s1"}))),
        ("die Analysen der Platte fallen weg",
         lambda d: d["querschnitte"][0].__setitem__("spannungsfaelle", [])),
    ]

    def test_jede_aenderung_liefert_mit_und_ohne_speicher_dasselbe(self):
        beschreibung = projekt_mit_analysen()
        rechnen(beschreibung, frisch=True)
        for name, aendern in self.AENDERUNGEN:
            aendern(beschreibung)
            mit = rechnen(beschreibung, frisch=False)
            ohne = rechnen(beschreibung, frisch=True)
            with self.subTest(aenderung=name):
                self.assertEqual(mit.status, 200)
                self.assertEqual(als_text(mit), als_text(ohne))
            rechnen(beschreibung, frisch=False)

    def test_unveraendert_kommen_alle_aus_dem_speicher(self):
        self.assertEqual(analysen_zaehlen(projekt_mit_analysen(), lambda d: None), (2, 0))

    def test_ein_bauteil_ohne_analyse_rechnet_keine_neu(self):
        def aendern(d):
            d["querschnitte"][1]["h"] = 330
            d["grundbrueche"][0]["phi_k"] = 28.0
        self.assertEqual(analysen_zaehlen(projekt_mit_analysen(), aendern), (2, 0))

    def test_eine_geaenderte_analyse_rechnet_nur_ihr_bauteil_neu(self):
        def aendern(d):
            d["querschnitte"][0]["spannungsfaelle"][1]["N_Ed"] = -500.0
        self.assertEqual(analysen_zaehlen(projekt_mit_analysen(), aendern), (1, 1))

    def test_ein_geaendertes_material_rechnet_alle_neu(self):
        def aendern(d):
            d["materialien"][0]["sorte"] = d["materialien"][0]["name"] = "C25/30"
        self.assertEqual(analysen_zaehlen(projekt_mit_analysen(), aendern), (0, 2))

    def test_ein_bauteil_ohne_analysen_raeumt_seinen_platz(self):
        beschreibung = projekt_mit_analysen()
        rechnen(beschreibung, frisch=True)
        self.assertEqual(dienst.ANALYSEN.belegt, 2)
        beschreibung["querschnitte"][0]["spannungsfaelle"] = []
        antwort = rechnen(beschreibung, frisch=False)
        self.assertEqual(dienst.ANALYSEN.belegt, 1)
        self.assertEqual(list(antwort.daten["spannungsanalysen"]), ["a1"])


class TestBilderAusDemSpeicher(unittest.TestCase):
    """
    Die Bilder lesen die Befunde der Lösung, nicht die Rechenobjekte. Aus dem
    Speicher müssen sie dieselben sein wie frisch gerechnet -- obwohl jede
    Anfrage den Aufbau neu baut und keines seiner Objekte je gerechnet hat.
    """

    ANFRAGEN = [
        ("analysediagramme", {"kennung": "a1"}),
        ("balkensystem_verlauf", {"kennung": "r1", "fall": "Tragsicherheit"}),
    ]

    def test_warm_wie_kalt(self):
        beschreibung = projekt_mit_zwei_platten()
        for art, rumpf in self.ANFRAGEN:
            rumpf = {"projekt": beschreibung, **rumpf}
            dienst.SPEICHER.leeren()
            kalt = dienst.bearbeite(art, copy.deepcopy(rumpf))
            rechnen(beschreibung, frisch=True)
            dienst.SPEICHER.treffer = 0
            warm = dienst.bearbeite(art, copy.deepcopy(rumpf))
            with self.subTest(anfrage=art):
                self.assertEqual(dienst.SPEICHER.treffer, 1)    # wirklich aus dem Speicher
                self.assertEqual(kalt.status, 200)
                self.assertEqual(als_text(warm), als_text(kalt))


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
            s.merken(f"q{i}", "a", Loesung())
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
        # Und er steht auch nicht in der Loesung: sie haelt fest, was dieser
        # Lauf gerechnet hat -- den mitgebrachten hat der Aufrufer schon.
        self.assertEqual(nochmal.werte, {})
        self.assertFalse(nochmal.nicht_berechenbar)


if __name__ == "__main__":
    unittest.main()
