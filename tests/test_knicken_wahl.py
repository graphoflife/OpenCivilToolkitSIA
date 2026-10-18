"""
Das Knicken wählt zweimal: womit es die Verformung rechnet (e_2d) und womit
der Querschnitt widersteht (N_Rd bei M_Ed = N_Ed·e_tot).

Wählt es für den Widerstand dasselbe wie die Tragsicherheit, ist es deren
Linie -- einmal gerechnet, einmal hergeleitet. Sonst baut es eine eigene,
mit eigener Herleitung, und im Diagramm steht sie neben der massgebenden.
"""

import unittest

from opencivil.querschnitt.gesetzwahl import Rechenart
from opencivil.nachweis.resistenzlinie import Ebenenlinie
from opencivil.projekt import (
    KnickEintrag, KnickVerformungswahl, KnickWiderstandswahl, Projekt, ProjektFehler,
    RechenwahlEintrag,
)
from opencivil.web import diagrammdaten, dienst

STUETZE = KnickEintrag("Stütze", N_Ed=-800.0, M_Ed_1=20.0, laenge=4.0, knicklaenge=4.0)


def gerechnet(*, verformung=None, widerstand=None, tragsicherheit=None):
    """Nur das Knicken und was es braucht -- der Teillauf des Auges."""
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    q.knickfaelle = [STUETZE]
    q.knicken_wahl_verformung = verformung or q.knicken_wahl_verformung
    q.knicken_wahl_widerstand = widerstand or q.knicken_wahl_widerstand
    q.tragsicherheit_wahl = tragsicherheit or q.tragsicherheit_wahl
    aufbau = projekt.aufbauen()
    knicken = aufbau.knicken["q1"]
    loesung = aufbau.werk.loese(knicken.d_ausnutzung["Stütze"].id)
    return aufbau, knicken, loesung


def diagramm(aufbau) -> dict:
    """Das M-N-Bild der Platte -- nach einem ganzen Lauf, wie in der Oberflaeche."""
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return diagrammdaten.linie(aufbau.nachweise["q1.x"], loesung, aufbau)


def text(loesung) -> str:
    return " ".join(getattr(b, "text", "") + getattr(b, "latex", "")
                    for b in loesung.protokoll.alle_bloecke())


class TestVorgabe(unittest.TestCase):
    """
    Verformung präzise, Widerstand mit der 0.85·x-Vereinfachung -- gegen die
    Handrechnung der Tragsicherheit also eine eigene Linie. Die Handrechnung
    gibt es beim Knicken nicht mehr (2026-10-12).
    """

    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.knicken, cls.loesung = gerechnet()

    def test_praezise_fuer_die_verformung(self):
        self.assertEqual(self.knicken.verformung.art.value, "parabel")
        self.assertIn(r"\text{Präzise ohne Vereinfachung}", text(self.loesung))

    def test_der_widerstand_mit_der_vereinfachung(self):
        self.assertIs(self.knicken.widerstand.art, Rechenart.BLOCK)
        self.assertTrue(self.knicken.eigene_linie)
        self.assertIsInstance(self.loesung.befund(self.knicken).linie, Ebenenlinie)
        self.assertIn(r"x\text{-Vereinfachung}", text(self.loesung))

    def test_das_fenster_steht_wie_gerechnet(self):
        """Gerechnet wird bis eps_c2d = 3.5 ‰, der Stahl bis eps_ud an seiner Lage -- so steht es da."""
        self.assertIn("der Beton an den Rändern bis -3.5 ‰", text(self.loesung))
        self.assertIn("jeder Stahl an seiner Lage bis zu seiner Bruchdehnung ε_ud",
                      text(self.loesung))

    def test_im_diagramm_daneben(self):
        linie = diagramm(self.aufbau)
        self.assertIn("0.85·x-Vereinfachung", linie["knicklinie"]["beschriftung"])


class TestGeteilteLinie(unittest.TestCase):
    """Rechnet die Tragsicherheit mit der 0.85·x-Vereinfachung, ist es deren Linie."""

    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.knicken, cls.loesung = gerechnet(
            tragsicherheit=RechenwahlEintrag(rechenart="block"))

    def test_der_widerstand_ist_die_linie_der_tragsicherheit(self):
        self.assertFalse(self.knicken.eigene_linie)
        self.assertIs(self.loesung.befund(self.knicken).linie,
                      self.loesung.befund(self.aufbau.nachweise["q1.x"]).massgebend)
        self.assertIn("Dieselbe Wahl wie die Tragsicherheit", text(self.loesung))

    def test_im_diagramm_keine_eigene_linie(self):
        self.assertIsNone(diagramm(self.aufbau)["knicklinie"])


class TestEigeneLinie(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.knicken, cls.loesung = gerechnet(
            widerstand=KnickWiderstandswahl(werkstoffsatz="charakteristisch", rechenart="parabel"))

    def test_mit_eigener_herleitung(self):
        self.assertTrue(self.knicken.eigene_linie)
        self.assertIsInstance(self.loesung.befund(self.knicken).linie, Ebenenlinie)
        t = text(self.loesung)
        self.assertIn("Widerstand: Resistenzlinie aus Dehnungsebenen", t)
        self.assertIn(r"\text{charakteristisch}", t)

    def test_die_zeichen_folgen_dem_widerstand(self):
        erg = self.loesung.befund(self.knicken).ergebnisse[0]
        urteil = next(u for u in self.loesung.urteile if u.fall == "Stütze")
        self.assertIn("N_{Rk,K}", urteil.widerstand.symbol)
        self.assertIn("N_Rk", erg.begruendung)

    def test_im_diagramm_daneben(self):
        linie = diagramm(self.aufbau)
        self.assertIn("Präzise", linie["knicklinie"]["beschriftung"])
        self.assertGreater(len(linie["knicklinie"]["punkte"]), 100)

    def test_der_grenzpunkt_liegt_in_ihr(self):
        """
        Bei N_Rd steht der Stab an seiner Grenze. Ist es die Festigkeit, liegt
        der Punkt auf der Linie; beim schlanken Stab ist es die Stabilität --
        die Folge läuft knapp darüber nicht mehr ein --, und er liegt darin.
        """
        befund = self.loesung.befund(self.knicken)
        erg = befund.ergebnisse[0]
        self.assertLessEqual(erg.M_bei_N_Rd, befund.linie.moment_bei(-erg.N_Rd, True))


class TestGleicheWahl(unittest.TestCase):
    def test_die_kriechzahl_zaehlt_nur_wo_sie_wirkt(self):
        parabel = RechenwahlEintrag(kriechzahl=1.0, rechenart="parabel")
        _, geteilt, _ = gerechnet(widerstand=KnickWiderstandswahl(kriechzahl=1.0, rechenart="parabel"),
                                  tragsicherheit=parabel)
        self.assertFalse(geteilt.eigene_linie)
        _, anders, _ = gerechnet(widerstand=KnickWiderstandswahl(kriechzahl=2.0, rechenart="parabel"),
                                 tragsicherheit=parabel)
        self.assertTrue(anders.eigene_linie)
        # Bei der 0.85·x-Vereinfachung wirkt phi nicht: dieselbe Linie.
        block = RechenwahlEintrag(rechenart="block")
        _, gleich, _ = gerechnet(widerstand=KnickWiderstandswahl(kriechzahl=3.0, rechenart="block"),
                                 tragsicherheit=block)
        self.assertFalse(gleich.eigene_linie)


class TestVerformung(unittest.TestCase):
    def test_mehr_kriechen_mehr_ausmitte(self):
        e_2d = {}
        for phi in (0.0, 2.0):
            _, knicken, loesung = gerechnet(
                verformung=KnickVerformungswahl(kriechzahl=phi))
            e_2d[phi] = loesung.befund(knicken).ergebnisse[0].e_2d
        self.assertGreater(e_2d[2.0], e_2d[0.0])

    def test_den_block_gibt_es_fuer_die_verformung_nicht(self):
        """
        Mit ihm trüge auf flachen Stücken jede Krümmung dasselbe Moment, und
        nahe der Grenzkraft hinge N_Rd an der Suche (2026-10-15).
        """
        p = Projekt.beispiel()
        p.querschnitte[0].knicken_wahl_verformung.rechenart = "block"
        with self.assertRaisesRegex(ProjektFehler, "'block' gibt es als 'rechenart' nicht"):
            p.pruefen()

    def test_die_werte_sind_waehlbar(self):
        """Charakteristisch ist der Beton steifer begrenzt: weniger Ausmitte als mit f_cd."""
        e_2d = {}
        for satz in ("bemessung", "charakteristisch"):
            _, knicken, loesung = gerechnet(
                verformung=KnickVerformungswahl(werkstoffsatz=satz))
            e_2d[satz] = loesung.befund(knicken).ergebnisse[0].e_2d
        self.assertLess(e_2d["charakteristisch"], e_2d["bemessung"])


class TestDatei(unittest.TestCase):
    def oeffnen(self, **wahl) -> str:
        """Öffnet das Beispiel mit dieser Wahl -- und gibt die Meldung zurück."""
        daten = Projekt.beispiel().als_dict()
        daten["querschnitte"][0].update(wahl)
        antwort = dienst.bearbeite("pruefen", {"projekt": daten})
        self.assertEqual(antwort.status, 400)
        return antwort.daten["fehler"]

    def test_elastisch_gibt_es_beim_knicken_nicht(self):
        self.assertIn("knicken_wahl_verformung: 'elastisch' gibt es als 'rechenart' nicht",
                      self.oeffnen(knicken_wahl_verformung={"rechenart": "elastisch"}))

    def test_die_handrechnung_einer_alten_datei_wird_genannt(self):
        """
        Bis 2026-10-12 gab es sie beim Knicken. Eine alte Datei, die sie noch
        wählt, wird nicht mehr umgedeutet -- sie nennt die Wahl.
        """
        for feld in ("knicken_wahl_verformung", "knicken_wahl_widerstand"):
            with self.subTest(feld=feld):
                text = self.oeffnen(**{feld: {"rechenart": "handrechnung"}})
                self.assertIn(f"{feld}: 'handrechnung' gibt es als 'rechenart' nicht", text)

    def test_der_block_gibt_es_in_der_verformung_nicht(self):
        self.assertIn("'block' gibt es als 'rechenart' nicht", self.oeffnen(
            knicken_wahl_verformung={"rechenart": "block"}))

    def test_eine_teilweise_wahl_rechnet_wie_ihr_kapitel(self):
        daten = Projekt.beispiel().als_dict()
        daten["querschnitte"][0]["knicken_wahl_verformung"] = {
            "kriechzahl": 1.5, "werkstoffsatz": "charakteristisch"}
        wahl = Projekt.aus_dict(daten).querschnitte[0].knicken_wahl_verformung
        self.assertEqual((wahl.rechenart, wahl.kriechzahl, wahl.werkstoffsatz),
                         ("parabel", 1.5, "charakteristisch"))

    def test_von_hand_gesetzt_meldet_sich(self):
        p = Projekt.beispiel()
        p.querschnitte[0].knicken_wahl_widerstand.rechenart = "handrechnung"
        with self.assertRaisesRegex(ProjektFehler, "'handrechnung' gibt es als 'rechenart' nicht"):
            p.pruefen()


if __name__ == "__main__":
    unittest.main()
