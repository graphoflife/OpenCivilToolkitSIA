"""
HALFEN HDB als Durchstanzbewehrung (opencivil.durchstanzen.systeme).

Die Durchmesser des Herstellers bis zur Grenze der Tabelle 21, angeordnet
wie die Bügel nach SIA 262:2025, 5.5.3.8 und 5.5.3.9, mit der 2 der Norm in
Gleichung (70) statt der 3.5 des Herstellers (4.3.6.5.9: dessen Gutachten
liegt nicht vor); eine Innenstütze durch den ganzen Nachweis, von Hand
nachgerechnet; das Bild der Leiste und die Datei.
"""

import math
import unittest

from opencivil.durchstanzen import produkte
from opencivil.durchstanzen.pruefung import tabelle_21
from opencivil.durchstanzen.systeme import Durchstanzsystem
from opencivil.projekt import Projekt
from opencivil.web.durchstanzdaten import situation
from tests.test_durchstanzen import E_S, F_YD, TAU_CD, projekt, rechnen, texte

HDB = Durchstanzsystem.HDB.regeln
BUEGEL = Durchstanzsystem.BUEGEL.regeln


class TestRegeln(unittest.TestCase):
    """Die Regeln von HDB, ohne Nachweis."""

    def test_durchmesser_des_herstellers_bis_tabelle_21(self):
        """12, 14, 16, 20 und 25 mm (Produktinformation), höchstens so dick, wie Tabelle 21 zulässt."""
        self.assertEqual(produkte.HDB_DURCHMESSER, (12, 14, 16, 20, 25))
        for d, soll in ((0.139, []), (0.150, [12]), (0.234, [12, 14, 16]),
                        (0.300, [12, 14, 16, 20]), (0.400, [12, 14, 16, 20, 25])):
            with self.subTest(d=d):
                self.assertEqual([round(e.durchmesser * 1e3) for e in HDB.elemente(d, 0.2)], soll)
                if soll:
                    self.assertLessEqual(max(soll), tabelle_21(d).durchmesser * 1e3 + 1e-9)

    def test_abstaende_wie_bei_buegeln(self):
        """Beide stehen nach der Norm: 0.35·d_v, dann d_v, dann s_1 nach Tabelle 21."""
        self.assertEqual(HDB.abstaende(0.234, 0.234, 4), (0.085, 0.145, 0.175, 0.175))
        for d in (0.140, 0.200, 0.300, 0.450, 0.700):
            with self.subTest(d=d):
                self.assertEqual(HDB.abstaende(d, d, 6), BUEGEL.abstaende(d, d, 6))

    def test_hoehe_auf_5_mm_abgerundet(self):
        """280 − 30 − 30 = 220 mm bleibt; 280 − 30 − 32 = 218 mm wird 215 mm."""
        self.assertAlmostEqual(HDB.hoehe(0.280, 0.030, 0.030), 0.220)
        self.assertAlmostEqual(HDB.hoehe(0.280, 0.030, 0.032), 0.215)

    def test_faktor_der_norm_statt_des_herstellers(self):
        """In (70) die 2, auch an der Innenstütze; die 3.5 des Herstellers nennt nur der Text."""
        self.assertEqual(produkte.HDB_FAKTOR, 3.5)
        for ausnahme in (True, False):
            self.assertEqual(HDB.k_sys(0.020, 0.234, ausnahme), 2.0)
        self.assertIn("nennt der Hersteller 3.5 anstelle der 2", HDB.k_sys_text)


class TestInnenstuetzeMitHdb(unittest.TestCase):
    """C30/37, h = 280 mm, d = 234 mm, Stütze 400 × 400 mm, V_d = 800 kN: der Beton allein reicht nicht."""

    @classmethod
    def setUpClass(cls):
        cls.p = projekt(b_x=400, b_y=400, V_d=800.0, system="hdb")
        cls.aufbau, cls.loesung, cls.befund, _ = rechnen(cls.p)
        cls.urteile = {u.fall: u for u in cls.loesung.urteile}
        cls.b = cls.befund.leisten

    def test_vier_urteile(self):
        self.assertEqual(set(self.urteile), {"mit Durchstanzbewehrung", "Verformungsvermögen",
                                             "Betondruckdiagonale",
                                             "ausserhalb der Durchstanzbewehrung"})
        self.assertTrue(all(u.erfuellt for u in self.urteile.values()))

    def test_vorschlag(self):
        """⌀12, der dünnste; h_A = 280 − 30 − 30; zwei Anker je Leiste im Bereich."""
        v = self.b.vorschlag
        self.assertIs(v.system, HDB)
        self.assertAlmostEqual(v.typ.durchmesser, 0.012)
        self.assertAlmostEqual(v.h_A, 0.220)
        self.assertEqual(v.abstaende[:3], (0.085, 0.145, 0.175))
        self.assertEqual(v.anrechenbar, 2)
        self.assertRegex(v.name, r"^\d+ × HDB ⌀12 mit \d+ Ankern( \+ \d+ × HDB ⌀12 mit \d+ Ankern)*$")

    def test_beitrag_der_bewehrung_von_hand(self):
        """(68) und (69) mit ⌀12: V_Rd,s = ΣA_sw · k_e · σ_sd, je Leiste zwei Anker im Bereich."""
        v = self.b.vorschlag
        sigma = min(E_S * self.befund.psi / 6 * (1 + 2.9 / F_YD * 234.0 / 12.0), F_YD)
        self.assertAlmostEqual(self.b.sigma_sd / 1e6, sigma, places=3)
        A_sw = len(v.leisten) * 2 * math.pi * 12.0 ** 2 / 4
        self.assertAlmostEqual(self.b.V_Rd_s, A_sw * 0.9 * sigma, delta=1.0)

    def test_druckdiagonale_mit_dem_faktor_der_norm(self):
        """(70): 2·k_r, nicht die 3.5 des Herstellers."""
        self.assertEqual(self.b.k_sys, 2.0)
        self.assertAlmostEqual(self.b.V_Rd_max, min(2.0 * self.befund.k_r, 3.5) * TAU_CD
                               * 234.0 * self.befund.innen.u * 1e3, delta=1.0)

    def test_herleitung_spricht_von_hdb(self):
        t = texte(self.loesung)
        for satz in ("Platz für die Anker zwischen den Überdeckungen",
                     "Höhe der Anker: der Platz zwischen den Überdeckungen, auf 5 mm abgerundet",
                     "Für HALFEN HDB nennt der Hersteller 3.5 anstelle der 2",
                     "Faktor der Norm in Gleichung (70)"):
            self.assertIn(satz, t)
        self.assertNotIn("ancoPLUS", t)
        self.assertNotIn("Bügel", t)

    def test_ansicht_der_leiste(self):
        a = situation(self.aufbau, self.p.durchstanzstellen[0].kennung, self.loesung)["ansicht"]
        self.assertEqual((a["form"], a["druckseite"]), ("kopfanker", "unten"))
        self.assertAlmostEqual(a["h_A"], 220.0)
        self.assertAlmostEqual(a["durchmesser"], 12.0)
        erste = "".join(z.get("text", "") for z in a["legende"][0])
        self.assertIn("Die Leiste mit den meisten Ankern", erste)

    def test_datei_hin_und_zurueck(self):
        wieder = Projekt.aus_dict(self.p.als_dict())
        self.assertEqual(wieder.als_dict(), self.p.als_dict())
        self.assertIs(wieder.durchstanzstellen[0].system, Durchstanzsystem.HDB)


if __name__ == "__main__":
    unittest.main()
