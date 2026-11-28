"""
Durchstanzbewehrung mit Plattenbereichen (opencivil.durchstanzen.mit_bewehrung,
Platz, und .bewehrung.setzen): die Leisten an der Stütze stehen im innersten
Bereich um sie, so hoch, wie er dick ist, und bleiben c_nom vor seiner Stufe
und ausserhalb der übrigen Bereiche; passt keine, sagt es die Herleitung. Der
Schnitt durch verschiedene Dicken behält sein Urteil, die Leisten zählen dort
nicht; die Leisten an den Stufen prüft tests.test_durchstanzen_stufenleisten.
Dazu, was die Ansicht der Leiste zeigt.

Das Beispiel des Plans vom 2026-11-27 (tests.test_durchstanzen_bereiche) mit
V_d = 400 kN: um die Stütze hält es ohne Bewehrung nicht (335.4 kN), an der
Stufe auch nicht (366.1 kN).
"""

import unittest

from opencivil.durchstanzen.bereiche import Seite
from opencivil.durchstanzen.pruefung import spannung
from opencivil.querschnitt.geometrie import abstand_strecke_polygon, abstand_strecke_rand, lage
from opencivil.web import dienst
from opencivil.web.durchstanzdaten import situation
from tests.test_durchstanzen import E_S, F_YD, MIT, projekt, rechnen, texte
from tests.test_durchstanzen_bereiche import mit_bereich, quadrat
from tests.test_durchstanzen_weg import STREIFEN, WEG, mit_streifen

C_NOM = 0.030

#: Vier dünnere Bereiche rund um die Stütze 400 × 400 mm, je 50 mm vor ihr, in mm.
RING = ([[-650, -650], [-250, -650], [-250, 650], [-650, 650]],
        [[250, -650], [650, -650], [650, 650], [250, 650]],
        [[-250, -650], [250, -650], [250, -250], [-250, -250]],
        [[-250, 250], [250, 250], [250, 650], [-250, 650]])


def in_m(ecken):
    return [(x / 1e3, y / 1e3) for x, y in ecken]


def strecken(leisten):
    """Je Leiste ihr Stahl: von der Wurzel bis zum letzten Anker, der ihr bleibt."""
    v = leisten.vorschlag
    return [(l.wurzel, l.anker(v.radien)[l.anzahl - 1]) for l in v.leisten]


def faelle(loesung):
    return {u.fall: u for u in loesung.urteile}


def satz(zeile):
    return "".join(t.get("text") or t.get("mathe") for t in zeile)


def ansicht(p):
    aufbau, loesung, _, _ = rechnen(p)
    return situation(aufbau, p.durchstanzstellen[0].kennung, loesung)["ansicht"]


def ohne_bereich(V_d):
    return projekt(b_x=400, b_y=400, stufe="1", V_d=V_d, h=240.0)


class TestImStuetzenkopf(unittest.TestCase):
    """Der Kopf 1200 × 1200 mm mit 320 mm: die Leisten stehen in ihm."""

    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.loesung, cls.befund, _ = rechnen(mit_bereich(V_d=400.0))
        cls.leisten = cls.befund.leisten

    def test_im_bereich_mit_c_nom(self):
        ecken = in_m(quadrat(600))
        self.assertEqual(len(self.leisten.vorschlag.leisten), 8)
        for a, b in strecken(self.leisten):
            self.assertGreater(lage(b, ecken), 0)
            self.assertGreaterEqual(abstand_strecke_rand(a, b, ecken), C_NOM - 1e-9)

    def test_so_hoch_wie_der_kopf_dick(self):
        """320 − 30 − 30 = 260 mm Platz: ancoPLUS 255 mm hoch; in der Platte allein 175 mm."""
        self.assertAlmostEqual(self.leisten.vorschlag.h_A, 0.255)
        self.assertAlmostEqual(rechnen(ohne_bereich(400.0))[2].leisten.vorschlag.h_A, 0.175)

    def test_urteile_an_der_stuetze(self):
        f = faelle(self.loesung)
        for fall in MIT:
            self.assertTrue(f[fall].erfuellt, fall)
        self.assertNotIn("ohne Durchstanzbewehrung", f)

    def test_herleitung(self):
        t = texte(self.loesung)
        self.assertIn("über die Stufe eines Plattenbereichs", t)
        self.assertIn("In (69) gilt dasselbe ψ wie für V_Rd,c: ψ ist die Drehung der Platte um "
                      "die Stütze; d ist das an der Stütze", t)

    def test_sigma_sd_mit_psi_der_platte_und_d_an_der_stuetze(self):
        """
        (69) mit demselben ψ wie V_Rd,c und d = 274 mm an der Stütze. Mit
        2.5 m Spannweite bleibt σ_sd unter f_yd: 364 N/mm², mit d der Platte
        wären es 348.
        """
        befund = rechnen(mit_bereich(V_d=800.0, l_x=2.5, l_y=2.5))[2]
        l = befund.leisten
        erwartet = spannung(E_S, befund.psi, 0.3 * 30 ** (2 / 3), F_YD, 0.274,
                            l.vorschlag.typ.durchmesser)
        self.assertLess(erwartet, F_YD)
        self.assertAlmostEqual(l.sigma_sd / 1e6, erwartet, delta=0.5)


class TestZuKlein(unittest.TestCase):
    """
    Ein Kopf 700 × 700 mm: 150 mm vor der Stütze die Stufe -- keine Leiste
    behält genug Anker. An der Stufe stehen Leisten (tests.test_durchstanzen_stufenleisten).
    """

    @classmethod
    def setUpClass(cls):
        cls.p = mit_bereich(V_d=400.0, halb=350.0)
        cls.aufbau, cls.loesung, cls.befund, _ = rechnen(cls.p)

    def test_der_grund_am_ort(self):
        self.assertIsNone(self.befund.leisten)
        f = faelle(self.loesung)
        for fall in MIT:
            self.assertTrue(f[fall].offen, fall)
            self.assertEqual(f[fall].begruendung,
                             "Bereich B1 ist zu klein für Leisten an der Stütze.")
        t = texte(self.loesung)
        self.assertIn("Bereich B1 ist zu klein für Leisten an der Stütze: mit c_nom Abstand zu "
                      "seiner Stufe behält keine Leiste genug Anker.", t)
        self.assertIn("Mit Plattenbereichen sucht das Werkzeug noch keinen Stahlpilz.", t)

    def test_legende(self):
        """Wo sich nicht alle Nachweise führen liessen, stehen die übrigen für sich."""
        s = situation(self.aufbau, self.p.durchstanzstellen[0].kennung, self.loesung)
        self.assertIsNone(s["ansicht"])
        legende = [satz(z) for z in s["legende"]]
        self.assertIn("Bereich B1 ist zu klein für Leisten an der Stütze. Die Nachweise mit "
                      "Durchstanzbewehrung sind darum nicht geführt.", legende)
        self.assertTrue(legende[-1].startswith("Die übrigen Nachweise erfüllt"))

    def test_kein_platz_rundum(self):
        """Vier dünnere Bereiche je 50 mm vor der Stütze: neben ihr ist zu wenig Platz."""
        p = ohne_bereich(420.0)
        for ecken in RING:
            p.durchstanzstellen[0].plattenbereich(ecken, 180.0, Seite.STUETZE)
        _, loesung, befund, _ = rechnen(p)
        self.assertIsNone(befund.leisten)
        self.assertEqual(faelle(loesung)["mit Durchstanzbewehrung"].begruendung,
                         "Neben der Stütze ist zu wenig Platz für Leisten.")


class TestDanebenEinHindernis(unittest.TestCase):
    """
    Der dünnere Streifen 100 mm neben der Stütze (tests.test_durchstanzen_weg):
    die Leisten bleiben ausserhalb, mit c_nom; der Schnitt durch verschiedene
    Dicken behält sein Urteil.
    """

    @classmethod
    def setUpClass(cls):
        _, cls.loesung, cls.befund, _ = rechnen(mit_streifen(V_d=420.0))

    def test_ausserhalb_mit_c_nom(self):
        streifen = in_m(STREIFEN)
        for a, b in strecken(self.befund.leisten):
            self.assertGreaterEqual(abstand_strecke_polygon(a, b, streifen), C_NOM - 1e-9)

    def test_zum_streifen_hin_keine_leiste(self):
        """Dort behielte eine Leiste keinen Anker: 11 statt 12, dafür je fünf statt vier."""
        v = self.befund.leisten.vorschlag
        self.assertEqual((len(v.leisten), len(v.radien)), (11, 5))
        ohne = rechnen(ohne_bereich(420.0))[2].leisten.vorschlag
        self.assertEqual((len(ohne.leisten), len(ohne.radien)), (12, 4))

    def test_der_weg_behaelt_sein_urteil(self):
        f = faelle(self.loesung)
        self.assertTrue(f["mit Durchstanzbewehrung"].erfuellt)
        self.assertFalse(f[WEG].erfuellt)
        self.assertAlmostEqual(f[WEG].erfuellungsgrad.si, 269.2 / 420.0, delta=1e-3)
        self.assertIn("Am Schnitt durch verschiedene Dicken zählen die Leisten an der Stütze "
                      "nicht", texte(self.loesung))


class TestAnsicht(unittest.TestCase):
    """Die Leiste in der Ansicht: h des Kopfs, rechts seine Stufe."""

    def test_stufe_zur_stuetze_hin(self):
        a = ansicht(mit_bereich(V_d=400.0))
        self.assertEqual(a["h"], 320.0)
        s = a["stufe"]
        for k, v in (("x", 400.0), ("h", 240.0), ("druck", 80.0), ("zug", 0.0)):
            self.assertAlmostEqual(s[k], v, msg=k)
        self.assertIn("Die Leiste steht in Bereich B1, 320 mm dick; rechts seine Stufe, dahinter "
                      "240 mm. Von der Stufe bleibt sie c_nom weg.",
                      [satz(z) for z in a["legende"]])

    def test_stufe_auf_der_gegenseite(self):
        s = ansicht(mit_bereich(seite=Seite.GEGENSEITE, V_d=400.0))["stufe"]
        self.assertAlmostEqual(s["druck"], 0.0)
        self.assertAlmostEqual(s["zug"], 80.0)

    def test_stufe_weit_draussen(self):
        """Ein Kopf 3 m breit: die Stufe liegt 1.3 m vor der Stütze, ausserhalb des Bilds."""
        a = ansicht(mit_bereich(V_d=400.0, halb=1500.0))
        self.assertIsNone(a["stufe"])
        self.assertEqual(a["h"], 320.0)
        self.assertIn("seine Stufe liegt weiter draussen", " ".join(satz(z) for z in a["legende"]))

    def test_ohne_bereich(self):
        a = ansicht(ohne_bereich(400.0))
        self.assertIsNone(a["stufe"])
        self.assertEqual(a["h"], 240.0)

    def test_legende_des_grundrisses(self):
        p = mit_bereich(V_d=400.0)
        aufbau, loesung, _, _ = rechnen(p)
        legende = [satz(z) for z in situation(aufbau, p.durchstanzstellen[0].kennung,
                                              loesung)["legende"]]
        self.assertTrue(any(z.startswith("Durchstanzbewehrung: 8 × ancoPLUS") for z in legende))
        self.assertTrue(any(z.startswith("An der Stufe von Bereich B1") for z in legende))
        self.assertTrue(legende[-1].startswith("Alle Nachweise erfüllt"))

    def test_rechnet_auf_der_seite(self):
        """Wie die Seite rechnet, samt Formelsammlung."""
        for p in (mit_bereich(V_d=400.0), mit_bereich(V_d=400.0, halb=350.0),
                  mit_streifen(V_d=420.0)):
            antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
            self.assertFalse(antwort.ist_fehler, antwort.daten)


if __name__ == "__main__":
    unittest.main()
