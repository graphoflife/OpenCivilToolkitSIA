"""
Das Knicken wählt zweimal: womit es die Verformung rechnet (e_2d) und womit
der Querschnitt widersteht (N_Rd bei M_Ed = N_Ed·e_tot).

Wählt es für den Widerstand dasselbe wie die Tragsicherheit, ist es deren
Linie -- einmal gerechnet, einmal hergeleitet. Sonst baut es eine eigene,
mit eigener Herleitung, und im Diagramm steht sie neben der massgebenden.
"""

import unittest

from opencivil.nachweis.resistenzlinie import Ebenenlinie, Handlinie
from opencivil.projekt import KnickEintrag, Projekt, RechenwahlEintrag
from opencivil.web import diagrammdaten

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


def text(loesung) -> str:
    return " ".join(getattr(b, "text", "") + getattr(b, "latex", "")
                    for b in loesung.protokoll.alle_bloecke())


class TestVorgabe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.knicken, cls.loesung = gerechnet()

    def test_parabel_fuer_die_verformung(self):
        self.assertEqual(self.knicken.verformung.art.value, "parabel")
        self.assertIn(r"\text{Parabel}", text(self.loesung))

    def test_der_widerstand_ist_die_linie_der_tragsicherheit(self):
        self.assertFalse(self.knicken.eigene_linie)
        self.assertIs(self.knicken.linie, self.aufbau.nachweise["q1.x"].massgebend)
        self.assertIsInstance(self.knicken.linie, Handlinie)
        self.assertIn("Dieselbe Wahl wie die Tragsicherheit", text(self.loesung))

    def test_das_fenster_steht_wie_gerechnet(self):
        """Gerechnet wird bis eps_c2d = 3.5 ‰ -- so steht es auch da."""
        self.assertIn("-3.5 ‰ bis 45.0 ‰", text(self.loesung))

    def test_im_diagramm_keine_eigene_linie(self):
        linie = diagrammdaten.linie(self.aufbau.nachweise["q1.x"], self.aufbau)
        self.assertIsNone(linie["knicklinie"])


class TestEigeneLinie(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.knicken, cls.loesung = gerechnet(
            widerstand=RechenwahlEintrag(werkstoffsatz="charakteristisch", rechenart="parabel"))

    def test_mit_eigener_herleitung(self):
        self.assertTrue(self.knicken.eigene_linie)
        self.assertIsInstance(self.knicken.linie, Ebenenlinie)
        t = text(self.loesung)
        self.assertIn("Widerstand: Resistenzlinie aus Dehnungsebenen", t)
        self.assertIn(r"\text{charakteristisch}", t)

    def test_die_zeichen_folgen_dem_widerstand(self):
        erg = self.knicken.ergebnisse[0]
        urteil = next(u for u in self.loesung.urteile if u.fall == "Stütze")
        self.assertIn("N_{Rk,K}", urteil.widerstand.symbol)
        self.assertIn("N_Rk", erg.begruendung)

    def test_im_diagramm_daneben(self):
        linie = diagrammdaten.linie(self.aufbau.nachweise["q1.x"], self.aufbau)
        self.assertIn("Parabel", linie["knicklinie"]["beschriftung"])
        self.assertGreater(len(linie["knicklinie"]["punkte"]), 100)

    def test_der_grenzpunkt_liegt_in_ihr(self):
        """
        Bei N_Rd steht der Stab an seiner Grenze. Ist es die Festigkeit, liegt
        der Punkt auf der Linie; beim schlanken Stab ist es die Stabilität --
        die Folge läuft knapp darüber nicht mehr ein --, und er liegt darin.
        """
        erg = self.knicken.ergebnisse[0]
        self.assertLessEqual(erg.M_bei_N_Rd, self.knicken.linie.moment_bei(-erg.N_Rd, True))


class TestGleicheWahl(unittest.TestCase):
    def test_die_kriechzahl_zaehlt_nur_wo_sie_wirkt(self):
        parabel = RechenwahlEintrag(kriechzahl=1.0, rechenart="parabel")
        _, geteilt, _ = gerechnet(widerstand=parabel, tragsicherheit=parabel)
        self.assertFalse(geteilt.eigene_linie)
        _, anders, _ = gerechnet(widerstand=RechenwahlEintrag(kriechzahl=2.0, rechenart="parabel"),
                                 tragsicherheit=parabel)
        self.assertTrue(anders.eigene_linie)
        # Bei der Handrechnung wirkt phi nicht: dieselbe Linie.
        _, hand, _ = gerechnet(widerstand=RechenwahlEintrag(kriechzahl=3.0))
        self.assertFalse(hand.eigene_linie)


class TestVerformung(unittest.TestCase):
    def test_mehr_kriechen_mehr_ausmitte(self):
        e_2d = {}
        for phi in (0.0, 2.0):
            _, knicken, _ = gerechnet(
                verformung=RechenwahlEintrag(kriechzahl=phi, rechenart="parabel"))
            e_2d[phi] = knicken.ergebnisse[0].e_2d
        self.assertGreater(e_2d[2.0], e_2d[0.0])

    def test_block_rechnet_auch(self):
        _, knicken, loesung = gerechnet(verformung=RechenwahlEintrag(rechenart="block"))
        self.assertTrue(knicken.ergebnisse[0].stabil)
        self.assertIn(r"\text{Block }", text(loesung))


class TestDatei(unittest.TestCase):
    def test_elastisch_gibt_es_beim_knicken_nicht(self):
        from opencivil.projekt import ProjektFehler
        daten = Projekt.beispiel().als_dict()
        daten["querschnitte"][0]["knicken_wahl_verformung"] = {"rechenart": "elastisch"}
        with self.assertRaises(ProjektFehler):
            Projekt.aus_dict(daten)


if __name__ == "__main__":
    unittest.main()
