"""
Die Kennzahl einer Durchstanzstelle (opencivil.durchstanzen.kennzahl): der
Durchstanzwiderstand am Schnittpunkt, wo V_d − ΔV = V_Rd,c(ψ(V_d)) gilt --
gleich welche Stützenkraft eingegeben ist (Benutzer, 2026-11-27).
"""

import unittest

from opencivil.bericht.zusammenfassung import angaben, kennzahlen
from opencivil.durchstanzen.nachweis import K_R_GRENZE
from opencivil.web.api import kennzahltabellen
from tests.test_durchstanzen import TAU_CD, projekt, rechnen, texte


def kennzahl(p):
    """Aufbau und Lösung allein der Kennzahl, und ihr Wert in kN."""
    aufbau = p.aufbauen()
    teil = aufbau.bauteil(p.durchstanzstellen[0].kennung)
    loesung = aufbau.werk.loese(*teil.weitere_ziele)
    (_, wert), = kennzahlen(aufbau, teil.eintrag.kennung, loesung)
    return aufbau, loesung, wert.groesse.si / 1e3


def zwischenwerte(loesung):
    """Die Namen der Werte, die die Herleitung der Kennzahl zeigt."""
    return {b.wert_id.rsplit(".kennzahlen.", 1)[-1] for b in loesung.protokoll.bloecke
            if ".kennzahlen." in getattr(b, "wert_id", "")}


class TestAmSchnittpunkt(unittest.TestCase):
    """C30/37, B500B, die Vorgaben mit c = 35 mm, Näherungsstufe 2."""

    def test_503_6_kn_gleich_welche_stuetzenkraft(self):
        for V_d in (0.0, 300.0, 700.0):
            with self.subTest(V_d=V_d):
                self.assertAlmostEqual(kennzahl(projekt(c=35.0, V_d=V_d))[2], 503.6, delta=0.05)

    def test_dort_geht_der_nachweis_gerade_auf(self):
        """Mit der Kennzahl als V_d geht der Nachweis ohne Bewehrung auf, 1 kN darüber nicht."""
        V = kennzahl(projekt(c=35.0))[2]
        for V_d, erfuellt in ((V - 0.1, True), (V + 1.0, False)):
            with self.subTest(V_d=V_d):
                befund = rechnen(projekt(c=35.0, V_d=V_d))[2]
                self.assertEqual(befund.innen.V_d_red <= befund.V_Rd_c, erfuellt)

    def test_ohne_last_gaelte_k_r_2(self):
        """Bei V_d = 0 wären ψ = 0 und k_r = 2: 866.7 kN, ein Widerstand nur ohne Last."""
        befund = rechnen(projekt(c=35.0, V_d=0.0))[2]
        self.assertEqual((befund.psi, befund.k_r), (0.0, K_R_GRENZE))
        self.assertAlmostEqual(befund.V_Rd_c / 1e3, 866.7, delta=0.05)
        self.assertAlmostEqual(befund.V_Rd_c, K_R_GRENZE * TAU_CD * 1e6 * befund.innen.d_v
                               * befund.innen.u, delta=50.0)

    def test_mit_flaechenlast_traegt_der_schnitt_v_d_ohne_sie(self):
        """
        Mit q_d = 10 kN/m² trägt der Schnitt V_d − ΔV: bei V_d = V_Rd,c + ΔV
        rechnet der Nachweis genau die Kennzahl, als Widerstand und als Querkraft.
        """
        p = projekt(c=35.0, q_d=10.0)
        V_Rd_c = kennzahl(p)[2]
        dV = rechnen(p)[2].innen.abzug / 1e3
        befund = rechnen(projekt(c=35.0, q_d=10.0, V_d=V_Rd_c + dV))[2]
        self.assertAlmostEqual(befund.V_Rd_c / 1e3, V_Rd_c, delta=0.05)
        self.assertAlmostEqual(befund.innen.V_d_red / 1e3, V_Rd_c, delta=0.05)
        self.assertLess(V_Rd_c, 503.6)

    def test_die_herleitung_zeigt_psi_und_k_r_dort(self):
        _, loesung, _ = kennzahl(projekt(c=35.0))
        self.assertLessEqual({"V_d", "m_sdx", "psi", "k_r", "V_Rd_c", "V_d_red"},
                             zwischenwerte(loesung))
        self.assertIn("Gesucht ist V_d mit V_d − ΔV = V_Rd,c(ψ(V_d))", texte(loesung))


class TestOhneSuche(unittest.TestCase):
    """In den Stufen 1 und 3 hängt ψ nicht von V_d ab: die Kennzahl ist V_Rd,c des Nachweises."""

    def test_gleich_dem_nachweis(self):
        for stufe in ("1", "3"):
            with self.subTest(stufe=stufe):
                p = projekt(c=35.0, V_d=200.0, stufe=stufe, m_sdx=60.0, m_sdy=60.0)
                self.assertAlmostEqual(kennzahl(p)[2], rechnen(p)[2].V_Rd_c / 1e3, delta=0.05)

    def test_die_herleitung_sagt_es(self):
        _, loesung, _ = kennzahl(projekt(c=35.0, stufe="1"))
        self.assertIn("In Näherungsstufe 1 hängt ψ nicht von der Stützenkraft ab", texte(loesung))
        self.assertNotIn("m_sdx", zwischenwerte(loesung))


class TestWasDieOberflaecheSieht(unittest.TestCase):

    def test_eine_karte_kennzahlen_mit_auge(self):
        p = projekt(c=35.0)
        aufbau, loesung, _ = kennzahl(p)
        (zeile,) = kennzahltabellen(aufbau, loesung)[p.durchstanzstellen[0].kennung]["zeilen"]
        self.assertEqual(zeile["bezeichnung"], "Durchstanzwiderstand am Schnittpunkt")
        self.assertTrue(zeile["ziel"].endswith(".kennzahlen.V_Rd_c"))
        self.assertIn("503.6", str(zeile["zellen"]))

    def test_ohne_last_kein_widerstand_in_den_angaben(self):
        """Ohne Last standen dort ψ = 0, k_r = 2 und 866.7 kN -- jetzt nur der Schnitt."""
        p = projekt(c=35.0)
        aufbau, loesung, _, _ = rechnen(p)
        _, tabelle = angaben(aufbau, p.durchstanzstellen[0].kennung, loesung)
        self.assertEqual([z[0] for z in tabelle.zeilen],
                         ["Wirksame statische Höhe", "Nachweisschnitt, wirksam",
                          "Momentenübertragung"])


if __name__ == "__main__":
    unittest.main()
