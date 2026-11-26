"""
Bügel als Durchstanzbewehrung (opencivil.durchstanzen.systeme) und die
Leiste in der Ansicht (opencivil.web.durchstanzdaten).

Die Regeln der Bügel gegen SIA 262:2025, 5.5.3.8 bis 5.5.3.12 und Tabelle
21; eine Innenstütze mit Bügeln durch den ganzen Nachweis, von Hand
nachgerechnet; die Wahl des Systems in Katalog, Maske und Datei; und was das
Bild der Leiste vom Kern bekommt -- bei Decke und Bodenplatte, mit und ohne
Stahlpilz.
"""

import math
import unittest
from itertools import accumulate

from opencivil.durchstanzen.bewehrung import BEREICH_VON, anrechenbar
from opencivil.durchstanzen.pruefung import tabelle_21
from opencivil.durchstanzen.systeme import SYSTEME, Durchstanzsystem
from opencivil.projekt import Projekt
from opencivil.web.api import katalog
from opencivil.web.durchstanzdaten import situation
from tests.test_durchstanzen import E_S, F_YD, TAU_CD, projekt, rechnen, texte

BUEGEL = Durchstanzsystem.BUEGEL.regeln


class TestRegeln(unittest.TestCase):
    """Die Regeln der Bügel, ohne Nachweis."""

    def test_jede_stellung_hat_ihre_regeln(self):
        self.assertEqual(set(SYSTEME), set(Durchstanzsystem))
        self.assertEqual([s.beschriftung for s in Durchstanzsystem], ["ancoPLUS", "Bügel"])

    def test_abstaende(self):
        """
        d = d_v = 234 mm: der erste bei 0.35·234 = 81.9 mm, auf 85 mm aufgerundet;
        der zweite bei d_v, 234 − 85 = 149 mm auf 145 mm abgerundet; danach
        s_1 = 0.75·234 = 175.5 mm nach Tabelle 21, auf 175 mm abgerundet.
        """
        self.assertEqual(BUEGEL.abstaende(0.234, 0.234, 4), (0.085, 0.145, 0.175, 0.175))
        self.assertEqual(BUEGEL.abstaende(0.234, 0.234, 2), (0.085, 0.145))

    def test_zwei_reihen_zaehlen_und_tabelle_21_haelt(self):
        """5.5.3.8: mindestens zwei Reihen zwischen 0.35·d_v und d_v, s_0 < s_1, s_1 nach Tabelle 21."""
        for d in (0.140, 0.160, 0.200, 0.234, 0.300, 0.450, 0.600):
            with self.subTest(d=d):
                abstaende = BUEGEL.abstaende(d, d, 6)
                grenzen = tabelle_21(d)
                self.assertGreaterEqual(anrechenbar(list(accumulate(abstaende)), d), 2)
                self.assertGreaterEqual(abstaende[0], BEREICH_VON * d)
                self.assertLess(abstaende[0], grenzen.s_1)
                self.assertTrue(all(a <= grenzen.s_1 + 1e-9 for a in abstaende[1:]))
                self.assertTrue(all(round(a * 1e3) % 5 == 0 for a in abstaende))

    def test_durchmesser_nach_tabelle_21(self):
        """5.5.3.12: höchstens der Durchmesser der Tabelle 21; unter d = 140 mm keine Bügel."""
        self.assertEqual(BUEGEL.elemente(0.139, 0.2), [])
        self.assertEqual([round(e.durchmesser * 1e3) for e in BUEGEL.elemente(0.234, 0.2)],
                         [8, 10, 12, 14, 16, 18])
        for d in (0.140, 0.200, 0.400):
            with self.subTest(d=d):
                durchmesser = [e.durchmesser for e in BUEGEL.elemente(d, 0.2)]
                self.assertTrue(durchmesser)
                self.assertLessEqual(max(durchmesser), tabelle_21(d).durchmesser + 1e-9)

    def test_hoehe_und_faktor(self):
        """Der ganze Platz zwischen den Überdeckungen; in (70) die 2 der Norm, auch an der Innenstütze."""
        self.assertAlmostEqual(BUEGEL.hoehe(0.280, 0.030, 0.030), 0.220)
        for ausnahme in (True, False):
            self.assertEqual(BUEGEL.k_sys(0.020, 0.234, ausnahme), 2.0)


class TestInnenstuetzeMitBuegeln(unittest.TestCase):
    """C30/37, h = 280 mm, Stütze 400 × 400 mm, V_d = 800 kN: der Beton allein reicht nicht."""

    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.loesung, cls.befund, _ = rechnen(
            projekt(b_x=400, b_y=400, V_d=800.0, system="buegel"))
        cls.urteile = {u.fall: u for u in cls.loesung.urteile}
        cls.b = cls.befund.leisten

    def test_vier_urteile(self):
        self.assertEqual(set(self.urteile), {"mit Durchstanzbewehrung", "Verformungsvermögen",
                                             "Betondruckdiagonale",
                                             "ausserhalb der Durchstanzbewehrung"})
        self.assertTrue(all(u.erfuellt for u in self.urteile.values()))

    def test_vorschlag(self):
        """⌀8 reicht; h_A = 280 − 30 − 30; zwei Schenkel je Linie im Bereich."""
        v = self.b.vorschlag
        self.assertIs(v.system, BUEGEL)
        self.assertAlmostEqual(v.typ.durchmesser, 0.008)
        self.assertAlmostEqual(v.h_A, 0.220)
        self.assertEqual(v.abstaende[:3], (0.085, 0.145, 0.175))
        self.assertEqual(v.anrechenbar, 2)
        self.assertRegex(v.name, r"^\d+ × \d+( \+ \d+ × \d+)* Bügelschenkel ⌀8$")

    def test_beitrag_der_bewehrung_von_hand(self):
        """(68) und (69) mit ⌀8: V_Rd,s = ΣA_sw · k_e · σ_sd."""
        v = self.b.vorschlag
        sigma = min(E_S * self.befund.psi / 6 * (1 + 2.9 / F_YD * 234.0 / 8.0), F_YD)
        self.assertAlmostEqual(self.b.sigma_sd / 1e6, sigma, places=3)
        A_sw = len(v.leisten) * 2 * math.pi * 8.0 ** 2 / 4
        self.assertAlmostEqual(self.b.V_Rd_s, A_sw * 0.9 * sigma, delta=1.0)
        self.assertAlmostEqual(self.b.f_yd / 1e6, F_YD, places=3)

    def test_druckdiagonale_mit_dem_faktor_der_norm(self):
        """(70): 2·k_r, nicht der Faktor eines Gutachtens."""
        self.assertEqual(self.b.k_sys, 2.0)
        self.assertAlmostEqual(self.b.V_Rd_max, min(2.0 * self.befund.k_r, 3.5) * TAU_CD
                               * 234.0 * self.befund.innen.u * 1e3, delta=1.0)

    def test_herleitung_spricht_von_buegeln(self):
        t = texte(self.loesung)
        for satz in ("Platz für die Bügelschenkel zwischen den Überdeckungen",
                     "Höhe der Bügel: der ganze Platz zwischen den Überdeckungen",
                     "Faktor der Norm in Gleichung (70)"):
            self.assertIn(satz, t)
        self.assertNotIn("ancoPLUS", t)

    def test_zu_viel_last_ohne_pilz(self):
        """
        V_d = 1000 kN: mit 2·k_r bricht die Druckdiagonale, und auch um einen
        ZEUS reicht sie nicht -- das sagt der Hinweis; ancoPLUS hält dort mit
        dem Faktor seines Gutachtens um einen Pilz.
        """
        _, loesung, befund, _ = rechnen(projekt(b_x=400, b_y=400, V_d=1000.0, system="buegel"))
        urteile = {u.fall: u for u in loesung.urteile}
        self.assertFalse(urteile["Betondruckdiagonale"].erfuellt)
        self.assertIsNone(befund.pilz)
        self.assertIn("Auch kein ZEUS-Stahlpilz reicht", texte(loesung))


class TestWahlDesSystems(unittest.TestCase):

    def test_katalog(self):
        k = katalog()
        self.assertEqual(k["durchstanzen"]["systeme"], [
            {"wert": "ancoplus", "beschriftung": "ancoPLUS"},
            {"wert": "buegel", "beschriftung": "Bügel"}])
        gruppe = next(g for g in k["vorgaben"]["durchstanz"] if g["titel"] == "Durchstanzbewehrung")
        self.assertEqual(gruppe["nach"], ["plattenart", "system"])
        self.assertEqual(gruppe["felder"]["bodenplatte|buegel"][0]["beschriftung"], "Bügel von oben")
        self.assertEqual(gruppe["felder"]["decke|ancoplus"][0]["beschriftung"], "Ankerköpfe von unten")
        self.assertEqual(k["neu"]["durchstanzstellen"]["system"], "ancoplus")

    def test_datei_hin_und_zurueck(self):
        p = projekt(system="buegel", plattenart="bodenplatte")
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.als_dict(), p.als_dict())
        self.assertIs(wieder.durchstanzstellen[0].system, Durchstanzsystem.BUEGEL)


class TestAnsicht(unittest.TestCase):
    """Was das Bild der Leiste vom Kern bekommt, in mm."""

    @staticmethod
    def ansicht(**felder):
        p = projekt(b_x=400, b_y=400, **felder)
        aufbau, loesung, befund, _ = rechnen(p)
        return situation(aufbau, p.durchstanzstellen[0].kennung, loesung)["ansicht"], befund

    def test_decke_mit_ancoplus(self):
        a, befund = self.ansicht(V_d=800.0)
        v = befund.leisten.vorschlag
        self.assertEqual((a["form"], a["druckseite"]), ("kopfanker", "unten"))
        self.assertEqual((a["h"], a["c"], a["c_v"]), (280.0, 30.0, 30.0))
        self.assertAlmostEqual(a["h_A"], 215.0)
        self.assertAlmostEqual(a["durchmesser"], 10.0)
        laengste = max(len(l.anker(v.radien)) for l in v.leisten)
        self.assertEqual(len(a["radien"]), laengste)
        for r, soll in zip(a["radien"], v.radien):
            self.assertAlmostEqual(r, soll * 1e3)
        self.assertAlmostEqual(a["zaehlt"][0], 0.35 * 234.0)
        self.assertAlmostEqual(a["zaehlt"][1], 234.0)
        # Die äussere Lage x: 30 + 16/2 tief, die innere y: 30 + 16 + 16/2; die Leiste läuft nach rechts.
        self.assertEqual([(round(l["tiefe"], 6), l["laengs"]) for l in a["lagen"]],
                         [(38.0, True), (54.0, False)])
        self.assertAlmostEqual(a["stuetze"]["rand"], 0.0)
        self.assertAlmostEqual(a["stuetze"]["achse"], -200.0)
        self.assertIsNone(a["pilz"])

    def test_bodenplatte_mit_buegeln(self):
        a, _ = self.ansicht(V_d=800.0, system="buegel", plattenart="bodenplatte")
        self.assertEqual((a["form"], a["druckseite"]), ("buegel", "oben"))
        self.assertAlmostEqual(a["h_A"], 220.0)
        zeilen = a["legende"]
        self.assertTrue(all(set(z) in ({"text"}, {"mathe"}) for zeile in zeilen for z in zeile))
        erste = "".join(z.get("text", "") for z in zeilen[0])
        self.assertIn("Die Linie mit den meisten Bügelschenkeln", erste)
        self.assertIn("bis auf die Biegungen", erste)

    def test_mit_stahlpilz(self):
        """Der Rand der Stütze liegt hinter dem Rand des Pilzes, an dem die Leisten ansetzen."""
        a, befund = self.ansicht(V_d=1000.0)
        self.assertIsNotNone(befund.pilz)
        self.assertAlmostEqual(a["pilz"]["hoehe"], befund.pilz.pilz.h * 1e3)
        self.assertLess(a["stuetze"]["rand"], -1.0)
        self.assertLess(a["stuetze"]["achse"], a["stuetze"]["rand"])
        self.assertIn("Links der Stahlpilz", "".join(z.get("text", "") for z in a["legende"][-1]))

    def test_ohne_bewehrung_kein_bild(self):
        a, befund = self.ansicht(V_d=300.0)
        self.assertIsNone(befund.leisten)
        self.assertIsNone(a)


if __name__ == "__main__":
    unittest.main()
