"""
Plattenbereiche mit eigener Dicke beim Durchstanzen (opencivil.durchstanzen.bereiche
und .stufen): d an der Stütze, ψ aus der dünnsten Stelle, der Schnitt an jeder
Stufe nach SIA 262:2025, 4.3.6.2.7, Figur 24a und 24c, je mit eigenem Urteil,
die Kennzahl über alle Schnitte, die Prüfungen beim Einlesen und was die
Oberfläche davon zu sehen bekommt.

Das Beispiel des Plans vom 2026-11-27: Innenstütze 400 × 400 mm, Platte
240 mm, Bereich 1200 × 1200 mm mit 320 mm, C30/37, B500B, Näherungsstufe 1,
c = 30 mm.
"""

import math
import unittest

from opencivil.durchstanzen.bereiche import Dicken, Plattenbereich, Seite
from opencivil.projekt import Projekt
from opencivil.web.durchstanzdaten import situation
from tests.test_durchstanzen import F_YD, E_S, TAU_CD, projekt, rechnen, texte
from tests.test_durchstanzen_kennzahl import kennzahl
from tests.unfertig import meldung

#: k_g mit D_max = 32 mm und C30/37 -- die Untergrenze 1.2 (4.3.3.2.1).
K_G = 1.2

#: ψ in Näherungsstufe 1 mit d der Platte, 194 mm: r_s = 0.22 · 7 m.
PSI = 1.5 * 0.22 * 7.0 / 0.194 * F_YD / E_S


def quadrat(halb):
    """Ein Quadrat um die Stützenachse, in mm."""
    return [[-halb, -halb], [halb, -halb], [halb, halb], [-halb, halb]]


def mit_bereich(seite=Seite.STUETZE, halb=600.0, h_B=320.0, **felder):
    """Das Beispiel des Plans, mit einem Bereich um die Stütze."""
    p = projekt(**{"b_x": 400, "b_y": 400, "stufe": "1", "V_d": 300.0, "h": 240.0, **felder})
    p.durchstanzstellen[0].plattenbereich(quadrat(halb), h_B, seite)
    return p


def k_r(d):
    """k_r (59) mit ψ der Platte und d in m."""
    return min(2.0, 1.0 / (0.45 + 0.18 * PSI * d * 1e3 * K_G))


class TestStuetzenkopf(unittest.TestCase):
    """Zur Stütze hin dicker (Figur 24a): an der Stütze d des Bereichs, an der Kante der Platte."""

    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.loesung, cls.befund, cls.urteil = rechnen(mit_bereich())

    def test_an_der_stuetze_335_4_kn(self):
        """d = 194 + 80 = 274 mm; der Schnitt d_v/2 um die Stütze zählt ganz."""
        self.assertAlmostEqual(self.befund.d, 0.274)
        u = 0.9 * (4 * 0.400 + 2 * math.pi * 0.137)
        self.assertAlmostEqual(self.befund.V_Rd_c, k_r(0.274) * TAU_CD * 1e6 * 0.274 * u, delta=5.0)
        self.assertAlmostEqual(self.befund.V_Rd_c / 1e3, 335.4, delta=0.05)

    def test_an_der_kante_366_1_kn(self):
        """
        0.5 · 194 mm ausserhalb des Bereichs, mit d der Platte; von jeder
        Seite zählen 1.5 · d_v an den Ecken (nach Vorgabe), dazu die Bögen.
        """
        stufe, = self.befund.stufen
        self.assertEqual(stufe.stufe.bereich.name, "B1")
        self.assertAlmostEqual(stufe.stufe.d, 0.194)
        u = 0.9 * (4 * 2 * 1.5 * 0.194 + 2 * math.pi * 0.097)
        self.assertAlmostEqual(stufe.V_Rd_c, k_r(0.194) * TAU_CD * 1e6 * 0.194 * u, delta=5.0)
        self.assertAlmostEqual(stufe.V_Rd_c / 1e3, 366.1, delta=0.05)

    def test_ohne_bereich_275_4_kn(self):
        befund = rechnen(projekt(b_x=400, b_y=400, stufe="1", V_d=300.0, h=240.0))[2]
        self.assertEqual(befund.stufen, ())
        self.assertAlmostEqual(befund.V_Rd_c / 1e3, 275.4, delta=0.05)

    def test_psi_aus_der_platte(self):
        """ψ rechnet mit d der Platte, auf der sicheren Seite -- die Herleitung sagt es."""
        self.assertAlmostEqual(self.befund.psi, PSI, places=4)
        self.assertIn("ψ rechnet mit d der Platte ausserhalb der Bereiche", texte(self.loesung))

    def test_je_schnitt_ein_urteil(self):
        urteile = [u for u in self.loesung.urteile if u.raum == self.urteil.raum]
        self.assertEqual([u.fall for u in urteile],
                         ["ohne Durchstanzbewehrung", "an der Stufe von Bereich B1"])
        self.assertTrue(all(u.erfuellt for u in urteile))

    def test_kennzahl_um_die_stuetze(self):
        self.assertAlmostEqual(kennzahl(mit_bereich())[2], 335.4, delta=0.05)


class TestGegenseite(unittest.TestCase):
    """Auf der Gegenseite dicker (Figur 24c): der Schnitt liegt 0.5 · d_v innerhalb der Stufe."""

    def test_weit_genug_d_des_bereichs_und_ein_schnitt_innen(self):
        """Der Bereich reicht 400 mm über die Stütze hinaus, mehr als d_v = 274 mm."""
        befund = rechnen(mit_bereich(Seite.GEGENSEITE))[2]
        self.assertAlmostEqual(befund.d, 0.274)
        self.assertAlmostEqual(befund.V_Rd_c / 1e3, 335.4, delta=0.05)
        stufe, = befund.stufen
        u = 0.9 * 4 * 2 * 1.5 * 0.194
        self.assertAlmostEqual(stufe.V_Rd_c, k_r(0.194) * TAU_CD * 1e6 * 0.194 * u, delta=5.0)

    def test_zu_knapp_gilt_d_der_platte(self):
        """
        Nur 200 mm über die Stütze hinaus: der Riss endete jenseits der Stufe
        -- an der Stütze gilt d der Platte (nach Vorgabe), wie ohne Bereich.
        """
        _, loesung, befund, _ = rechnen(mit_bereich(Seite.GEGENSEITE, halb=400.0))
        self.assertAlmostEqual(befund.d, 0.194)
        self.assertAlmostEqual(befund.V_Rd_c / 1e3, 275.4, delta=0.05)
        self.assertIn("reicht aber nicht d_v über die Stütze hinaus", texte(loesung))

    def test_ohne_platz_kein_eigener_schnitt(self):
        """50 mm über die Stütze hinaus: innerhalb der Stufe kein Schnitt 0.5 · d_v neben ihr."""
        _, loesung, befund, urteil = rechnen(mit_bereich(Seite.GEGENSEITE, halb=250.0))
        stufe, = befund.stufen
        self.assertIsNone(stufe.stufe.pruefung)
        self.assertIsNone(stufe.V_Rd_c)
        self.assertIn("kein Platz für einen eigenen Schnitt", texte(loesung))
        self.assertEqual([u.fall for u in loesung.urteile if u.raum == urteil.raum],
                         ["ohne Durchstanzbewehrung"])

    def test_kennzahl_an_der_stufe(self):
        """Die Stufe hält weniger als die Stütze: dort liegt der Schnittpunkt, 290.1 kN."""
        V = kennzahl(mit_bereich(Seite.GEGENSEITE))[2]
        self.assertAlmostEqual(V, 290.1, delta=0.05)
        for V_d, erfuellt in ((V - 0.1, True), (V + 1.0, False)):
            with self.subTest(V_d=V_d):
                _, loesung, befund, urteil = rechnen(mit_bereich(Seite.GEGENSEITE, V_d=V_d))
                an_stufe = next(u for u in loesung.urteile if u.raum == urteil.raum
                                and u.fall == "an der Stufe von Bereich B1")
                self.assertEqual(an_stufe.erfuellt, erfuellt)


class TestVerschachtelt(unittest.TestCase):
    """B1 mit 320 mm zur Stütze hin in B2 mit 280 mm auf der Gegenseite, Platte 240 mm."""

    def test_jede_stufe_mit_dem_d_jenseits(self):
        p = mit_bereich()
        p.durchstanzstellen[0].plattenbereich(quadrat(1000.0), 280.0, Seite.GEGENSEITE)
        befund = rechnen(p)[2]
        self.assertAlmostEqual(befund.d, 0.274)
        self.assertEqual([(x.stufe.bereich.name, round(x.stufe.d, 3)) for x in befund.stufen],
                         [("B1", 0.234), ("B2", 0.194)])

    def test_dicken(self):
        """Wie weit Druck- und Zugseite je Bereich versetzt sind, gegen den äusseren."""
        b2 = Plattenbereich("B2", tuple(map(tuple, quadrat(1.0))), 0.28, Seite.GEGENSEITE)
        b1 = Plattenbereich("B1", tuple(map(tuple, quadrat(0.6))), 0.32, Seite.STUETZE)
        dicken = Dicken(0.24, 0.194, (b1, b2))
        self.assertIs(dicken.aussen(b1), b2)
        self.assertIsNone(dicken.aussen(b2))
        self.assertAlmostEqual(dicken.versatz(b1).druck, 0.04)
        self.assertAlmostEqual(dicken.versatz(b1).zug, 0.04)
        self.assertAlmostEqual(dicken.d_von(b1), 0.274)


class TestWasNichtGeht(unittest.TestCase):

    def test_duenner_keine_stufe(self):
        """Ein dünnerer Bereich gibt an seiner Stufe keinen Schnitt: jenseits trägt es mehr."""
        befund = rechnen(mit_bereich(h_B=200.0))[2]
        self.assertAlmostEqual(befund.d, 0.154)
        self.assertEqual(befund.stufen, ())

    def test_ohne_bewehrungsvorschlag(self):
        _, loesung, befund, urteil = rechnen(mit_bereich(V_d=500.0))
        self.assertFalse(urteil.erfuellt)
        self.assertIsNone(befund.leisten)
        self.assertIn("Mit Plattenbereichen schlägt das Werkzeug noch keine Durchstanzbewehrung "
                      "vor.", texte(loesung))

    def test_neben_der_stuetze_noch_nicht(self):
        p = projekt(b_x=400, b_y=400, stufe="1", V_d=300.0, h=240.0)
        p.durchstanzstellen[0].plattenbereich([[600, -300], [1200, -300], [1200, 300], [600, 300]],
                                              320.0)
        _, loesung, befund, _ = rechnen(p)
        self.assertAlmostEqual(befund.V_Rd_c / 1e3, 275.4, delta=0.05)
        self.assertIn("Bereich B1 umschliesst die Stütze nicht", texte(loesung))

    def test_an_der_wand_noch_nicht(self):
        p = projekt(lage="wandende", V_d=300.0)
        p.durchstanzstellen[0].plattenbereich(quadrat(800.0), 360.0)
        _, loesung, befund, _ = rechnen(p)
        self.assertEqual(befund.stufen, ())
        self.assertIn("rechnet das Werkzeug Plattenbereiche noch nicht", texte(loesung))

    def test_teilweise_ueberdeckt(self):
        p = mit_bereich()
        p.durchstanzstellen[0].plattenbereich([[0, 0], [900, 0], [900, 900], [0, 900]], 300.0)
        self.assertIn("Bereich B1 und Bereich B2 überlappen sich teilweise", meldung(p))

    def test_durch_die_stuetze(self):
        p = projekt(b_x=400, b_y=400, V_d=300.0)
        p.durchstanzstellen[0].plattenbereich([[0, -500], [800, -500], [800, 500], [0, 500]], 360.0)
        self.assertIn("Bereich B1 schneidet die Stütze", meldung(p))


class TestWasDieOberflaecheSieht(unittest.TestCase):

    def test_bereiche_und_stufen_im_grundriss(self):
        p = mit_bereich()
        aufbau, loesung, _, _ = rechnen(p)
        s = situation(aufbau, p.durchstanzstellen[0].kennung, loesung)
        self.assertEqual(s["bereiche"], [{"name": "B1", "punkte": quadrat(600.0), "h": 320.0,
                                          "seite": "stuetze"}])
        stufe, = s["stufen"]
        self.assertEqual((stufe["name"], stufe["farbe"]), ("B1", 0))
        legende = " ".join(t.get("text", "") for zeile in s["legende"] for t in zeile)
        self.assertIn("Schnitt an der Stufe von Bereich B1 (grün)", legende)
        self.assertIn("Alle Nachweise erfüllt", legende)

    def test_datei_hin_und_zurueck(self):
        p = mit_bereich(Seite.GEGENSEITE)
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.als_dict(), p.als_dict())
        b, = wieder.durchstanzstellen[0].plattenbereiche
        self.assertEqual((b.kennung, b.knoten, b.h, b.seite),
                         ("B1", ["K1", "K2", "K3", "K4"], 320.0, Seite.GEGENSEITE))


if __name__ == "__main__":
    unittest.main()
