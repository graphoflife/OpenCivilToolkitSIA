"""
Leisten an der Stufe eines Bereichs zur Stütze hin (opencivil.durchstanzen.stufenleisten):
hält der Schnitt an der Stufe nicht, kommen eigene Leisten ausserhalb des
Bereichs dazu, so hoch, wie die Platte dort dick ist, mit vier eigenen
Urteilen; der Schnitt an der Stufe hat dann keines mehr. Passt keine, sagt
der Grund, wo. Auf der Gegenseite keine eigenen.

Das Beispiel des Plans vom 2026-11-27 (tests.test_durchstanzen_bereiche):
Kopf 1200 × 1200 mm mit 320 mm in der Platte mit 240 mm, mit V_d = 400 kN.
An der Stufe trägt der Beton allein 366.1 kN.
"""

import unittest

from opencivil.durchstanzen.bereiche import Seite
from opencivil.durchstanzen.kennwerte import kennwerttabelle
from opencivil.durchstanzen.pruefung import spannung
from opencivil.querschnitt.geometrie import lage
from opencivil.web import dienst
from opencivil.web.durchstanzdaten import situation
from tests.test_durchstanzen import E_S, F_YD, MIT, rechnen, texte
from tests.test_durchstanzen_bereiche import mit_bereich, quadrat
from tests.test_durchstanzen_leisten_bereiche import faelle, in_m, satz

STUFE = "an der Stufe von Bereich B1"
AN_DER_STUFE = tuple(f"{fall} {STUFE}" for fall in MIT)

#: Vier dünnere Bereiche rund um den Kopf, je 50 mm vor ihm, in mm.
RING = ([[-1100, -1100], [-650, -1100], [-650, 1100], [-1100, 1100]],
        [[650, -1100], [1100, -1100], [1100, 1100], [650, 1100]],
        [[-650, -1100], [650, -1100], [650, -650], [-650, -650]],
        [[-650, 650], [650, 650], [650, 1100], [-650, 1100]])


def in_b2(V_d):
    """Kopf 900 × 900 mm mit 400 mm in B2, 1040 × 1040 mm mit 260 mm: B2 reicht 70 mm weiter."""
    p = mit_bereich(V_d=V_d, halb=450.0, h_B=400.0)
    p.durchstanzstellen[0].plattenbereich(quadrat(520.0), 260.0, Seite.STUETZE)
    return p


def mit_ring():
    p = mit_bereich(V_d=400.0)
    for ecken in RING:
        p.durchstanzstellen[0].plattenbereich(ecken, 180.0, Seite.STUETZE)
    return p


def legende(p):
    aufbau, loesung, _, _ = rechnen(p)
    return [satz(z) for z in situation(aufbau, p.durchstanzstellen[0].kennung,
                                       loesung)["legende"]]


class TestAmStuetzenkopf(unittest.TestCase):
    """Das Beispiel: Leisten an der Stütze im Kopf, und eigene an seiner Stufe."""

    @classmethod
    def setUpClass(cls):
        cls.p = mit_bereich(V_d=400.0)
        cls.aufbau, cls.loesung, cls.befund, _ = rechnen(cls.p)
        cls.stufe = cls.befund.stufen[0]
        cls.leisten = cls.stufe.leisten

    def test_vier_eigene_urteile(self):
        """Der Schnitt an der Stufe urteilt nicht mehr; sein Grad bleibt ein Wert: 366.1/400."""
        f = faelle(self.loesung)
        for fall in (*MIT, *AN_DER_STUFE):
            self.assertTrue(f[fall].erfuellt, fall)
        self.assertNotIn(STUFE, f)
        grad = next(w.groesse.si for k, w in self.loesung.werte.items()
                    if k.endswith("stufe.B1.erfuellungsgrad"))
        self.assertAlmostEqual(grad, 366.1 / 400.0, delta=1e-3)

    def test_ausserhalb_des_kopfs(self):
        """Jede Leiste setzt am Rand des Kopfs an, 600 mm vor der Achse, und läuft nach aussen."""
        v = self.leisten.vorschlag
        kopf = in_m(quadrat(600))
        self.assertEqual(len(v.leisten), 24)
        for l in v.leisten:
            self.assertAlmostEqual(max(abs(l.wurzel[0]), abs(l.wurzel[1])), 0.6)
            for anker in l.anker(v.radien):
                self.assertLess(lage(anker, kopf), 0)

    def test_so_hoch_wie_die_platte(self):
        """240 − 30 − 30 = 180 mm Platz: ancoPLUS 175 mm hoch -- im Kopf an der Stütze 255."""
        self.assertAlmostEqual(self.leisten.vorschlag.h_A, 0.175)
        self.assertAlmostEqual(self.befund.leisten.vorschlag.h_A, 0.255)

    def test_mit_den_werten_der_stufe(self):
        """V_d,s = 400 − 366.1 kN; d_v = 194 mm der Platte, aussen 194 − 30 = 164 mm."""
        l = self.leisten
        self.assertAlmostEqual(l.V_d_s / 1e3, 400.0 - 366.1, delta=0.1)
        self.assertAlmostEqual(l.innen.d_v, 0.194)
        self.assertAlmostEqual(l.aussen.d_v, 0.164)
        self.assertIs(l.innen, self.stufe.stufe.pruefung)

    def test_herleitung(self):
        t = texte(self.loesung)
        self.assertIn("Durchstanzbewehrung an der Stufe von Bereich B1 An der Stufe von Bereich "
                      "B1 reicht der Beton allein nicht", t)
        self.assertIn("Vorgeschlagen wird ancoPLUS von AncoTech an der Stufe von Bereich B1: "
                      "24 × ancoPLUS DX3-0175", t)
        self.assertIn("In (69) gilt dasselbe ψ wie für V_Rd,c an der Stufe", t)
        self.assertIn("Ausserhalb der Durchstanzbewehrung an der Stufe von Bereich B1", t)
        self.assertNotIn("zählen die Leisten an der Stütze nicht", t)

    def test_tabelle(self):
        zeilen = kennwerttabelle(self.befund).zeilen
        self.assertIn(["Durchstanzbewehrung an der Stufe von Bereich B1", "",
                       "24 × ancoPLUS DX3-0175", ""], zeilen)
        zeichen = [getattr(z[1], "latex", z[1]) for z in zeilen]
        self.assertIn("V_{Rd,s,B1}", zeichen)
        self.assertIn("V_{Rd,c,out,B1}", zeichen)

    def test_grundriss(self):
        s = situation(self.aufbau, self.p.durchstanzstellen[0].kennung, self.loesung)
        self.assertEqual(len(s["stufen"][0]["leisten"]["leisten"]), 24)
        self.assertTrue(s["stufen"][0]["leisten"]["aussen"])
        zeilen = legende(self.p)
        self.assertTrue(any(z.startswith("Durchstanzbewehrung an der Stufe von Bereich B1: "
                                         "24 × ancoPLUS DX3-0175") for z in zeilen))
        self.assertTrue(zeilen[-1].startswith("Alle Nachweise erfüllt"))


class TestSpannung(unittest.TestCase):

    def test_sigma_sd_mit_d_an_der_stufe(self):
        """(69) mit ψ der Stütze und d = 194 mm an der Stufe: mit 2.5 m Spannweite unter f_yd."""
        befund = rechnen(mit_bereich(V_d=800.0, l_x=2.5, l_y=2.5))[2]
        l = befund.stufen[0].leisten
        erwartet = spannung(E_S, befund.psi, 0.3 * 30 ** (2 / 3), F_YD, 0.194,
                            l.vorschlag.typ.durchmesser)
        self.assertLess(erwartet, F_YD)
        self.assertAlmostEqual(l.sigma_sd / 1e6, erwartet, delta=0.5)


class TestNurAnDerStufe(unittest.TestCase):
    """Ein Kopf 900 × 900 mm mit 400 mm, V_d = 380 kN: um die Stütze hält es, an der Stufe nicht."""

    def test_nur_die_stufe_bekommt_leisten(self):
        _, loesung, befund, _ = rechnen(mit_bereich(V_d=380.0, halb=450.0, h_B=400.0))
        f = faelle(loesung)
        self.assertTrue(f["ohne Durchstanzbewehrung"].erfuellt)
        self.assertIsNone(befund.leisten)
        self.assertIsNotNone(befund.stufen[0].leisten)
        for fall in AN_DER_STUFE:
            self.assertTrue(f[fall].erfuellt, fall)
        for fall in MIT:
            self.assertNotIn(fall, f)


class TestKeinPlatz(unittest.TestCase):

    def test_jenseits_zu_klein(self):
        """B2 reicht nur 70 mm über den Kopf: dort behält keine Leiste genug Anker."""
        _, loesung, befund, _ = rechnen(in_b2(450.0))
        f = faelle(loesung)
        for fall in AN_DER_STUFE:
            self.assertTrue(f[fall].offen, fall)
            self.assertEqual(f[fall].begruendung,
                             "Bereich B2 ist zu klein für Leisten an der Stufe von Bereich B1.")
        self.assertIsNone(befund.stufen[0].leisten)
        self.assertIsNotNone(befund.stufen[1].leisten)
        self.assertTrue(f["mit Durchstanzbewehrung an der Stufe von Bereich B2"].erfuellt)

    def test_jeder_grund_einmal(self):
        """Unter dem Bild die Gründe der Stütze und der Stufe, je einmal."""
        self.assertIn("Bereich B1 ist zu klein für Leisten an der Stütze. Bereich B2 ist zu klein "
                      "für Leisten an der Stufe von Bereich B1. Die Nachweise mit "
                      "Durchstanzbewehrung sind darum nicht geführt.", legende(in_b2(450.0)))

    def test_ringsum_duennere_bereiche(self):
        """Vier dünnere Bereiche je 50 mm vor dem Kopf: an seiner Stufe ist zu wenig Platz."""
        _, loesung, befund, _ = rechnen(mit_ring())
        f = faelle(loesung)
        self.assertIsNone(befund.stufen[0].leisten)
        self.assertEqual(f[AN_DER_STUFE[0]].begruendung,
                         "An der Stufe von Bereich B1 ist zu wenig Platz für Leisten.")
        self.assertTrue(f["mit Durchstanzbewehrung"].erfuellt)


class TestGegenseite(unittest.TestCase):
    """Auf der Gegenseite (Figur 24c) liegt der Schnitt im Bereich: keine eigenen Leisten."""

    def test_der_schnitt_behaelt_sein_urteil(self):
        _, loesung, befund, _ = rechnen(mit_bereich(seite=Seite.GEGENSEITE, V_d=400.0))
        f = faelle(loesung)
        self.assertFalse(f[STUFE].erfuellt)
        self.assertNotIn(AN_DER_STUFE[0], f)
        self.assertIsNone(befund.stufen[0].leisten)
        self.assertIn("An der Stufe von Bereich B1 zählen die Leisten an der Stütze nicht, und "
                      "eigene schlägt das Werkzeug dort noch nicht vor.", texte(loesung))


class TestAufDerSeite(unittest.TestCase):

    def test_rechnet(self):
        """Wie die Seite rechnet, samt Formelsammlung."""
        for p in (mit_bereich(V_d=400.0), in_b2(450.0), mit_ring(),
                  mit_bereich(V_d=380.0, halb=450.0, h_B=400.0)):
            antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
            self.assertFalse(antwort.ist_fehler, antwort.daten)


if __name__ == "__main__":
    unittest.main()
