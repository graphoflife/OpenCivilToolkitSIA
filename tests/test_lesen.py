"""
Tests für das Lesen und Prüfen der Projektbeschreibung (opencivil.projekt.lesen).

Ein Leser für jeden Eintrag, eine Prüfung für jedes Feld -- und dieselbe
Prüfung für eine Datei wie für ein Projekt, das in Python gebaut wurde. Was
nicht stimmt, meldet sich mit Ort und Wert; umgedeutet wird nichts.
"""

import unittest

from opencivil.projekt import (
    KombinationEintrag, PostenEintrag, Projekt, ProjektFehler, QuerschnittEintrag,
    RechenwahlEintrag,
)
from opencivil.projekt.querschnittsanalyse import SchubwandEintrag
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
        roh = platte_roh()
        lage = roh["querschnitte"][0]["lagen"][0]
        lage["grund"]["abstand"], lage["grund"]["anzahl"] = None, 6
        self.assertIsNone(Projekt.aus_dict(roh).querschnitt("q1").lagen[0].grund.abstand)
        lage["grund"]["durchmesser"] = None
        self.assertIn("'durchmesser' muss eine Zahl sein, nicht None", meldung(roh))

    def test_eine_liste_bleibt_eine_liste(self):
        self.assertIn("'kombinationen' muss eine Liste sein", meldung(platte_roh(kombinationen={})))

    def test_eine_kriechzahl_ist_nicht_negativ(self):
        roh = platte_roh()
        roh["querschnitte"][0]["tragsicherheit_wahl"]["kriechzahl"] = -1
        text = meldung(roh)
        self.assertIn("tragsicherheit_wahl", text)
        self.assertIn("'kriechzahl' kann nicht negativ sein", text)

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
        self.assertEqual(wahl, RechenwahlEintrag(kriechzahl=1.5, rechenart="parabel"))

    def test_eine_teilweise_gebrauchsliste_behaelt_ihren_anteil(self):
        roh = platte_roh(quasistaendig={"aus_tragsicherheit": True})
        liste = Projekt.aus_dict(roh).querschnitt("q1").quasistaendig
        self.assertEqual(liste.anteil, 60.0)
        self.assertEqual(liste.wahl, RechenwahlEintrag.gebrauch())

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
        projekt = self.rahmen(quer="festt", k_quer=2000.0)
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
        p = self.rahmen()
        p.platte("Decke", b="1000")
        with self.assertRaises(ProjektFehler) as fehler:
            p.rechnen()
        self.assertIn("Platte 'Decke': 'b' muss eine Zahl sein, nicht '1000'",
                      str(fehler.exception))

    def test_eine_rissanforderung_mit_tippfehler(self):
        """Früher die mildeste Stufe -- ohne x-Bewehrung sogar ganz ohne Meldung."""
        p = self.rahmen()
        p.platte("Ohne x", x=[0, 0], rissanforderung="hcoh")
        with self.assertRaises(ProjektFehler) as fehler:
            p.rechnen()
        self.assertIn("'hcoh' gibt es als 'rissanforderung' nicht", str(fehler.exception))

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
        a.schubwand([50, 50], [250, 50], schnitte=9)
        with self.assertRaises(ProjektFehler) as fehler:
            p.pruefen()
        self.assertIn("9 gibt es als 'schnitte' nicht", str(fehler.exception))
        self.assertEqual(SchubwandEintrag().schnitte, 2)

    def test_ein_posten_ist_ein_posten(self):
        self.assertEqual(PostenEintrag.aus_dict({}), PostenEintrag())


if __name__ == "__main__":
    unittest.main()
