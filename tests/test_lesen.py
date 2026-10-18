"""
Tests für das Lesen und Prüfen der Projektbeschreibung (opencivil.projekt.lesen).

Ein Leser für jeden Eintrag, eine Prüfung für jedes Feld -- und dieselbe
Prüfung für eine Datei wie für ein Projekt, das in Python gebaut wurde. Was
nicht stimmt, meldet sich mit Ort und Wert; umgedeutet wird nichts.
"""

import json
import unittest

from opencivil.core.einheiten import GRAD, MM
from opencivil.querschnitt.gesetzwahl import Rechenart
from opencivil.projekt import (
    Gebrauchswahl, KnickVerformungswahl, KombinationEintrag, PostenEintrag, Projekt,
    ProjektFehler, QuerschnittEintrag,
)
from opencivil.projekt.querschnittsanalyse import SchubwandEintrag
from opencivil.nachweis.rissanforderung import Rissanforderung
from opencivil.projekt.lesen import Bereich, felder_pruefen
from opencivil.web import dienst


def platte_roh(**aenderung) -> dict:
    """Das Beispiel als Datei, mit geänderten Feldern seiner Platte."""
    roh = Projekt.beispiel().als_dict()
    roh["querschnitte"][0].update(aenderung)
    return roh


def meldung(roh: dict) -> str:
    with unittest.TestCase().assertRaises(ProjektFehler) as fehler:
        Projekt.aus_dict(roh)
    return str(fehler.exception)


class TestStreng(unittest.TestCase):
    """Was in der Datei nicht stimmt, wird genannt -- mit Ort und Wert."""

    def test_ein_unbekanntes_feld_mit_vorschlag(self):
        text = meldung(platte_roh(rissanforderug="hoch"))
        self.assertIn("Platte 'Decke über EG'", text)
        self.assertIn("'rissanforderug' gibt es nicht", text)
        self.assertIn("Gemeint ist vielleicht 'rissanforderung'", text)

    def test_ein_text_statt_einer_zahl(self):
        text = meldung(platte_roh(h="300"))
        self.assertIn("'h' muss eine Zahl sein, nicht '300'", text)

    def test_unendlich_ist_keine_zahl(self):
        roh = platte_roh()
        roh["querschnitte"][0]["kombinationen"][0]["M_Ed"] = float("inf")
        self.assertIn("'M_Ed' muss eine Zahl sein", meldung(roh))

    def test_ein_schalter_ist_kein_text(self):
        """«false» als Text wäre als Wahrheit wahr -- der Nachweis stünde eingeschaltet da."""
        text = meldung(platte_roh(duktilitaet="false"))
        self.assertIn("'duktilitaet' ist ein Schalter", text)

    def test_eine_ganze_zahl_wird_nicht_abgeschnitten(self):
        roh = platte_roh()
        roh["querschnitte"][0]["querkraftbewehrung"]["alpha_min"] = 35.7
        text = meldung(roh)
        self.assertIn("'alpha_min' muss eine ganze Zahl sein, nicht 35.7", text)
        self.assertIn("querkraftbewehrung", text)

    def test_eine_ganze_gleitkommazahl_ist_eine_ganze_zahl(self):
        roh = platte_roh()
        roh["querschnitte"][0]["querkraftbewehrung"]["alpha_min"] = 35.0
        buegel = Projekt.aus_dict(roh).querschnitt("q1").querkraftbewehrung
        self.assertEqual(buegel.alpha_min, 35)
        self.assertIs(type(buegel.alpha_min), int)

    def test_eine_ganze_zahl_aus_json_wird_eine_zahl(self):
        """300 aus der Datei ist 300.0 -- dieselbe Zahl, in der Art des Feldes."""
        h = Projekt.aus_dict(platte_roh(h=300)).querschnitt("q1").h
        self.assertIs(type(h), float)

    def test_eine_wahl_die_es_nicht_gibt(self):
        text = meldung(platte_roh(richtung_lage1="z"))
        self.assertIn("'z' gibt es als 'richtung_lage1' nicht. Möglich sind: x, y", text)

    def test_ein_pflichtfeld_fehlt(self):
        roh = platte_roh()
        del roh["querschnitte"][0]["beton"]
        self.assertIn("das Feld 'beton' fehlt", meldung(roh))

    def test_ein_pflichtfeld_ist_leer(self):
        roh = platte_roh()
        roh["querschnitte"][0]["kombinationen"][0]["name"] = ""
        text = meldung(roh)
        self.assertIn("Platte 'Decke über EG', kombinationen 1", text)
        self.assertIn("'name' darf nicht leer sein", text)

    def test_null_nur_wo_leer_etwas_heisst(self):
        """
        Bei Durchmesser und Teilung heisst leer nichts: welche Menge gilt,
        sagt seit 2026-10-18 die Art, und beide Zahlen stehen immer da.
        """
        for feld in ("durchmesser", "abstand", "anzahl"):
            with self.subTest(feld=feld):
                roh = platte_roh()
                roh["querschnitte"][0]["lagen"][0]["grund"][feld] = None
                self.assertIn(f"'{feld}' muss eine Zahl sein, nicht None", meldung(roh))

    def test_eine_liste_bleibt_eine_liste(self):
        self.assertIn("'kombinationen' muss eine Liste sein", meldung(platte_roh(kombinationen={})))

    def test_eine_negative_kriechzahl_oeffnet_sich_und_meldet_sich_beim_rechnen(self):
        """Form beim Lesen, Inhalt vor dem Rechnen -- bis 2026-10-17 hielt sie das Öffnen auf."""
        roh = platte_roh()
        roh["querschnitte"][0]["tragsicherheit_wahl"]["kriechzahl"] = -1
        projekt = Projekt.aus_dict(roh)
        projekt.pruefen()
        with self.assertRaises(ProjektFehler) as fehler:
            projekt.aufbauen()
        self.assertIn("tragsicherheit_wahl: Kriechzahl φ kann nicht negativ sein, angegeben "
                      "ist -1.", str(fehler.exception))

    def test_mehr_als_vier_lagen(self):
        roh = platte_roh()
        lagen = roh["querschnitte"][0]["lagen"]
        lagen.append(dict(lagen[0]))
        self.assertIn("5 Lagen angegeben", meldung(roh))


class TestVorgaben(unittest.TestCase):
    """Was fehlt, bekommt die Vorgabe -- die eines frischen Eintrags an dieser Stelle."""

    def test_eine_teilweise_rechenwahl_rechnet_wie_ihr_kapitel(self):
        """Die Verformung beim Knicken ist ohne Angabe präzise, nicht von Hand."""
        roh = platte_roh(knicken_wahl_verformung={"kriechzahl": 1.5})
        wahl = Projekt.aus_dict(roh).querschnitt("q1").knicken_wahl_verformung
        self.assertEqual(wahl, KnickVerformungswahl(kriechzahl=1.5))
        self.assertIs(wahl.rechenart, Rechenart.PARABEL)

    def test_eine_teilweise_gebrauchsliste_behaelt_ihren_anteil(self):
        roh = platte_roh(quasistaendig={"aus_tragsicherheit": True})
        liste = Projekt.aus_dict(roh).querschnitt("q1").quasistaendig
        self.assertEqual(liste.anteil, 60.0)
        self.assertEqual(liste.wahl, Gebrauchswahl())

    def test_ein_listenelement_bekommt_die_vorgaben_seiner_klasse(self):
        roh = platte_roh(kombinationen=[{"name": "Feld"}])
        self.assertEqual(Projekt.aus_dict(roh).querschnitt("q1").kombinationen,
                         [KombinationEintrag(name="Feld")])

    def test_fehlende_lagen_sind_leer(self):
        roh = platte_roh()
        roh["querschnitte"][0]["lagen"] = roh["querschnitte"][0]["lagen"][:2]
        lagen = Projekt.aus_dict(roh).querschnitt("q1").lagen
        self.assertEqual(len(lagen), 4)
        self.assertFalse(lagen[3].vorhanden)


class TestEineTuer(unittest.TestCase):
    """
    Was in Python gebaut wurde, geht durch dieselbe Prüfung wie eine Datei --
    vor jedem Rechnen. Vorher lief die Fassade an den Prüfungen der Leser
    vorbei: ein «festt» im Linienlager wurde still zur Bettung.
    """

    def rahmen(self, **linie) -> Projekt:
        p = Projekt("Probe")
        p.beton("C30/37")
        p.stahl("B500B")
        s = p.balkensystem("Rahmen")
        q = s.querschnitt("Rechteck", "rechteck")
        s.linie((0, 0), (5, 0), querschnitt=q, material="b1", **linie)
        s.lager_an((0, 0), "gelenkig")
        s.lager_an((5, 0), "verschieblich")
        return p

    def test_festt_wird_nicht_zur_feder(self):
        """An der Zeile, in der es steht -- und von Hand gesetzt beim Rechnen."""
        with self.assertRaises(ProjektFehler) as fehler:
            self.rahmen(quer="festt", k_quer=2000.0)
        self.assertIn("'festt' gibt es als 'quer' nicht", str(fehler.exception))
        projekt = self.rahmen()
        projekt.balkensysteme[0].linien[0].quer = "festt"
        with self.assertRaises(ProjektFehler) as fehler:
            projekt.rechnen()
        self.assertIn("Balkensystem 'Rahmen', linien 1", str(fehler.exception))
        self.assertIn("'festt' gibt es als 'quer' nicht", str(fehler.exception))

    def test_dieselbe_meldung_ueber_den_dienst(self):
        antwort = dienst.bearbeite("rechnen", {"projekt": self.rahmen().als_dict()})
        self.assertEqual(antwort.status, 200)
        roh = self.rahmen().als_dict()
        roh["balkensysteme"][0]["linien"][0]["quer"] = "festt"
        antwort = dienst.bearbeite("rechnen", {"projekt": roh})
        self.assertEqual(antwort.status, 400)
        self.assertIn("'festt' gibt es als 'quer' nicht", antwort.daten["fehler"])

    def test_ein_vertippter_stichwortname_beim_anlegen(self):
        p = self.rahmen()
        s = p.balkensysteme[0]
        with self.assertRaises(ProjektFehler) as fehler:
            s.stablast(s.lastfall("Wind"), s.linien[0], wert=3.0, richtng="waagrecht")
        self.assertIn("Gemeint ist vielleicht 'richtung'", str(fehler.exception))

    def test_ein_text_statt_einer_zahl_in_python(self):
        """An der Zeile, in der er steht -- nicht erst beim Rechnen."""
        p = self.rahmen()
        with self.assertRaises(ProjektFehler) as fehler:
            p.platte("Decke", b="1000")
        self.assertIn("Platte 'Decke': 'b' muss eine Zahl sein, nicht '1000'",
                      str(fehler.exception))

    def test_eine_rissanforderung_mit_tippfehler(self):
        """Früher die mildeste Stufe -- ohne x-Bewehrung sogar ganz ohne Meldung."""
        p = self.rahmen()
        with self.assertRaises(ProjektFehler) as fehler:
            p.platte("Ohne x", x=[0, 0], rissanforderung="hcoh")
        self.assertIn("'hcoh' gibt es als 'rissanforderung' nicht", str(fehler.exception))

    def test_von_hand_gesetzt_meldet_es_sich_beim_rechnen(self):
        p = self.rahmen()
        p.platte("Decke").rissanforderung = "hcoh"
        with self.assertRaises(ProjektFehler) as fehler:
            p.rechnen()
        self.assertIn("Platte 'Decke': 'hcoh' gibt es als 'rissanforderung' nicht",
                      str(fehler.exception))

    def test_ein_eintrag_am_falschen_ort(self):
        q = QuerschnittEintrag("q1", "Decke", "b1")
        q.lagen[0].grund = {"durchmesser": 12.0}
        p = self.rahmen()
        p.querschnitte.append(q)
        with self.assertRaises(ProjektFehler) as fehler:
            p.pruefen()
        self.assertIn("'grund' muss ein PostenEintrag sein", str(fehler.exception))

    def test_schnitte_einer_schubwand(self):
        p = self.rahmen()
        a = p.analyse("Unterzug")
        with self.assertRaises(ProjektFehler) as fehler:
            a.schubwand([50, 50], [250, 50], schnitte=9)
        self.assertIn("9 gibt es als 'schnitte' nicht", str(fehler.exception))
        self.assertEqual(SchubwandEintrag().schnitte, 2)

    def test_ein_posten_ist_ein_posten(self):
        self.assertEqual(PostenEintrag.aus_dict({}), PostenEintrag())



class TestInhaltVorDemRechnen(unittest.TestCase):
    """
    Form beim Lesen, Inhalt vor dem Rechnen: was erst das Rechnen braucht --
    ein Bereich, eine Regel über mehrere Felder --, hält das Öffnen nicht auf.
    """

    def test_oeffnen_geht_rechnen_meldet(self):
        roh = platte_roh()
        roh["querschnitte"][0]["haeufig"]["anteil"] = 0.0
        self.assertEqual(dienst.bearbeite("pruefen", {"projekt": roh}).status, 200)
        antwort = dienst.bearbeite("rechnen", {"projekt": roh})
        self.assertEqual(antwort.status, 400)
        self.assertIn("Platte 'Decke über EG', haeufig: Anteil aus der Tragsicherheit muss "
                      "grösser als null und höchstens 100 % sein, angegeben ist 0 %.",
                      antwort.daten["fehler"])

    def test_was_ein_bereich_verlangt(self):
        for bereich, wert, text in (
                (Bereich("Kriechzahl φ", ab=0.0), -1.0,
                 "Kriechzahl φ kann nicht negativ sein, angegeben ist -1."),
                (Bereich("Dicke h", MM, ueber=0.0), 0.0,
                 "Dicke h muss grösser als null sein, angegeben ist 0 mm."),
                (Bereich("α_min", GRAD, ab=1, bis=89), 90,
                 "α_min muss mindestens 1° und höchstens 89° sein, angegeben ist 90°."),
                (Bereich("φ_k", GRAD, ab=0.0, unter=90.0), 90.0,
                 "φ_k muss mindestens null und kleiner als 90° sein, angegeben ist 90°.")):
            with self.subTest(text=text):
                bereich.pruefen(wert - 1 if wert > 0 else wert + 1, "Hier")
                with self.assertRaises(ProjektFehler) as fehler:
                    bereich.pruefen(wert, "Hier")
                self.assertEqual(str(fehler.exception), f"Hier: {text}")


class TestNichtsStill(unittest.TestCase):
    """
    Was beim Rechnen bisher still einen Ersatz bekam, meldet sich: ein Posten
    mit Durchmesser ohne Teilung, eine Knicklänge null, ein Stab ohne Stahl,
    ein Kennwert, den es nicht gibt, zwei gleiche Kennungen.
    """

    def fehler(self, projekt: Projekt) -> str:
        with self.assertRaises(ProjektFehler) as fehler:
            projekt.aufbauen()
        return str(fehler.exception)

    def test_ein_posten_mit_durchmesser_braucht_eine_teilung(self):
        """Bis 2026-10-16 hiess eine Teilung von null still «kein Stab»."""
        p = Projekt.beispiel()
        p.querschnitt("q1").lagen[1].grund.abstand = 0.0
        self.assertIn("lagen 2, grund: die Teilung muss grösser als null sein",
                      self.fehler(p))
        grund = p.querschnitt("q1").lagen[1].grund
        grund.art, grund.anzahl = "anzahl", 0.0
        self.assertIn("braucht eine Stabzahl grösser als null", self.fehler(p))

    def test_eine_knicklaenge_von_null(self):
        """Sie rechnete und hiess «erfüllt»."""
        p = Projekt.beispiel()
        p.querschnitt("q1").knickfall("Wand", N_Ed=-500.0, laenge=0.0)
        self.assertIn("knickfaelle 'Wand': Systemlänge muss grösser als null sein, "
                      "angegeben ist 0 m.", self.fehler(p))

    def test_die_grenzen_der_buegel_gelten_auch_ohne_buegel(self):
        """Bis 2026-10-17 prüfte die Platte k_c und α nur, wenn Bügel lagen."""
        for setzen, text in (
                (lambda q: setattr(q, "k_c", 0.0),
                 "Platte 'Decke über EG': k_c muss grösser als null sein, angegeben ist 0."),
                (lambda q: setattr(q.querkraftbewehrung, "alpha_max", 90),
                 "querkraftbewehrung: α_max muss mindestens 1° und höchstens 89° sein, "
                 "angegeben ist 90°."),
                (lambda q: setattr(q.querkraftbewehrung, "durchmesser", -10.0),
                 "querkraftbewehrung: Bügeldurchmesser kann nicht negativ sein")):
            with self.subTest(text=text):
                p = Projekt.beispiel()
                q = p.querschnitt("q1")
                q.querkraftbewehrung.durchmesser = 0.0
                setzen(q)
                self.assertIn(text, self.fehler(p))

    def test_die_grenzen_des_gezeichneten_querschnitts(self):
        for feld, wert, text in (("alpha_min", 60, "α_min = 60° ist grösser als α_max"),
                                 ("k_c", -1.0, "k_c muss grösser als null sein"),
                                 ("x_d_max", 0.9, "max. x/d muss grösser als null")):
            with self.subTest(feld=feld):
                p = Projekt.beispiel()
                setattr(p.querschnittsanalysen[0], feld, wert)
                self.assertIn(text, self.fehler(p))

    def test_ein_stab_ohne_stahl_nimmt_nicht_den_ersten(self):
        p = Projekt.beispiel()
        p.querschnittsanalysen[0].stablinien[0].stahl = ""
        self.assertIn("Linie 1 hat kein Material", self.fehler(p))

    def test_buegel_ohne_stahl_nehmen_nicht_den_ersten(self):
        p = Projekt.beispiel()
        buegel = p.querschnitt("q1").querkraftbewehrung
        buegel.durchmesser, buegel.stahl = 10.0, ""
        self.assertIn("Querkraftbewehrung von 'Decke über EG' hat kein Material", self.fehler(p))

    def test_ein_stahl_ist_kein_beton(self):
        p = Projekt.beispiel()
        p.querschnitt("q1").beton = "s1"
        self.assertIn("braucht einen Beton, 'B500B' ist keiner", self.fehler(p))

    def test_ein_kennwert_den_es_nicht_gibt(self):
        """Eine Abweichung «fck» fiel still weg -- gerechnet wurde mit der Sorte."""
        p = Projekt.beispiel()
        p.eigener_beton().abweichungen = {"fck": 35.0}
        self.assertIn("einen Kennwert 'fck' gibt es nicht", self.fehler(p))

    def test_zwei_gleiche_kennungen(self):
        """Das spätere Material ersetzte still das frühere."""
        p = Projekt.beispiel()
        p.beton("C50/60").kennung = "b1"
        self.assertIn("dieselbe Kennung 'b1'", self.fehler(p))

    def test_zwei_werkstoffwahlen_fuer_ein_material(self):
        from opencivil.projekt import WerkstoffwahlEintrag
        p = Projekt.beispiel()
        a = p.querschnittsanalysen[0]
        a.werkstoffwahl = [WerkstoffwahlEintrag("b1"), WerkstoffwahlEintrag("b1", betongesetz="block")]
        self.assertIn("zwei Werkstoffwahlen", self.fehler(p))

    def test_zwei_lastfaelle_mit_derselben_kennung_im_rahmen(self):
        """Eine Last fiel still in beide -- jetzt rechnet das System nicht und sagt warum."""
        p = Projekt.beispiel()
        rahmen = p.balkensysteme[0]
        rahmen.lastfaelle[1].kennung = rahmen.lastfaelle[0].kennung
        meldungen = [m.text for m in rahmen.modell().meldungen if m.fehler]
        self.assertTrue(any("Mehrere Lastfälle haben die Kennung" in m for m in meldungen))

    def test_ein_unbekanntes_mass_eines_stabquerschnitts(self):
        """``B=500`` stand still da, gerechnet wurde mit b = 300."""
        p = Projekt.beispiel()
        q = p.balkensysteme[0].querschnitt("Stütze", "rechteck", B=500.0)
        self.assertIn("ein Mass «B» gibt es bei «Rechteck» nicht", q.fehler())

    def test_eine_leere_teilungsliste_der_suche(self):
        """Sie wurde still zu 150 mm."""
        p = Projekt.beispiel()
        p.querschnitt("q1").automatik_teilungen = []
        antwort = dienst.bearbeite("bewehrung_suchen", {"projekt": p.als_dict(), "kennung": "q1"})
        self.assertEqual(antwort.status, 400)
        self.assertIn("mindestens eine Teilung", antwort.daten["fehler"])

    def test_eine_unbekannte_rissanforderung_im_nachweis(self):
        from opencivil.nachweis.rissanforderung import Rissanforderung
        with self.assertRaisesRegex(ValueError, "'mittel' gibt es als Rissanforderung nicht"):
            Rissanforderung("mittel")
        self.assertEqual([a.gegen_fliessen for a in Rissanforderung], [False, True, True])


class TestWahlen(unittest.TestCase):
    """
    Ein Wahlfeld hält das Mitglied seiner Wahl -- gelesen, gebaut oder im Code
    zugewiesen. Bis 2026-10-17 hielt es Text, und rund dreissig Stellen machten
    daraus wieder das Mitglied.
    """

    def test_lesen_gibt_das_mitglied(self):
        roh = Projekt.beispiel().als_dict()
        roh["querschnitte"][0]["rissanforderung"] = "hoch"
        self.assertIs(Projekt.aus_dict(roh).querschnitte[0].rissanforderung,
                      Rissanforderung.HOCH)

    def test_text_im_code_wird_das_mitglied(self):
        q = Projekt.beispiel().querschnitte[0]
        q.rissanforderung = "erhoeht"
        self.assertIs(q.rissanforderung, Rissanforderung.ERHOEHT)

    def test_die_datei_bleibt_text(self):
        p = Projekt.beispiel()
        p.querschnitte[0].rissanforderung = Rissanforderung.HOCH
        roh = json.loads(json.dumps(p.als_dict()))
        self.assertEqual(roh["querschnitte"][0]["rissanforderung"], "hoch")

    def test_unbekanntes_meldet_sich_mit_ort(self):
        q = Projekt.beispiel().querschnitte[0]
        q.rissanforderung = "mittel"
        with self.assertRaisesRegex(ProjektFehler, "Platte: 'mittel' gibt es als "
                                    "'rissanforderung' nicht. Möglich sind: normal, erhoeht, hoch"):
            felder_pruefen(q, "Platte")


if __name__ == "__main__":
    unittest.main()
