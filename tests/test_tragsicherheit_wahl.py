"""
Die Tragsicherheit wählt, womit sie rechnet -- und Querkraft und sprödes
Versagen lesen aus derselben Linie.

Vorgabe ist, was bis 2026-10-09 fest galt: die Handrechnung mit
Bemessungswerten. Charakteristisch heissen die Widerstände R_k, die Kennungen
der Werte bleiben. Mit Block oder Parabel hält das Urteil gegen den Rand des
Dehnungsfächers, und die Herleitung zeigt seine Probe.
"""

import json
import unittest

from opencivil.nachweis.rechenwahl import Rechenart, Rechenwahl
from opencivil.nachweis.resistenzlinie import Ebenenlinie, Handlinie
from opencivil.projekt import Projekt, ProjektFehler, RechenwahlEintrag

KENNUNG = "q1.x"
BASIS = "querschnitt.q1.nachweis.mn.x"


def gerechnet(rechenart="handrechnung", werkstoffsatz="bemessung", kriechzahl=0.0):
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    q.tragsicherheit_wahl = RechenwahlEintrag(
        kriechzahl=kriechzahl, werkstoffsatz=werkstoffsatz, rechenart=rechenart)
    # Eine Querkraft, damit ihr Nachweis laut rechnet und m_R herleitet.
    q.kombinationen[1].V_Ed = 120.0
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return aufbau, loesung


def text(loesung) -> str:
    return " ".join(getattr(b, "text", "") + getattr(b, "latex", "")
                    for b in loesung.protokoll.alle_bloecke())


class TestVorgabe(unittest.TestCase):
    def test_handrechnung_mit_bemessungswerten(self):
        aufbau, loesung = gerechnet()
        mn = aufbau.nachweise[KENNUNG]
        self.assertEqual(mn.wahl, Rechenwahl())
        self.assertIsInstance(mn.massgebend, Handlinie)
        # Daneben die Parabel, zum Vergleich.
        self.assertIsInstance(mn.vergleich, Ebenenlinie)
        self.assertIs(mn.vergleich.wahl.art, Rechenart.PARABEL)
        self.assertIn(r"\text{Handrechnung, Block }", text(loesung))

    def test_die_neue_platte_bringt_die_vorgabe_mit(self):
        q = Projekt.beispiel().querschnitte[0]
        self.assertEqual(q.tragsicherheit_wahl, RechenwahlEintrag())


class TestCharakteristisch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.loesung = gerechnet(werkstoffsatz="charakteristisch")
        cls.mn = cls.aufbau.nachweise[KENNUNG]

    def test_reiner_druck_mit_f_ck(self):
        """Die Handrechnung: N_R^- = -b·h·f_ck, ohne Bewehrung."""
        N = self.loesung.werte[f"{BASIS}.N_Rd_druck"].groesse.si
        self.assertAlmostEqual(N, -1.0 * 0.3 * 30e6, delta=1e-3)

    def test_die_zeichen_heissen_rk_die_kennungen_bleiben(self):
        wert = self.loesung.werte[f"{BASIS}.M_Rd_N0_pos"]
        self.assertIn("M_{Rk,x}", wert.symbol)
        self.assertIn("N_{Rk,x}", self.loesung.werte[f"{BASIS}.N_Rd_zug"].symbol)
        self.assertIn("M_{Rk}", text(self.loesung))
        self.assertNotIn("M_{Rd}(N_{Ed}=0)", text(self.loesung))

    def test_mehr_als_mit_bemessungswerten(self):
        _, bemessung = gerechnet()
        schluessel = f"{BASIS}.M_Rd_N0_pos"
        self.assertGreater(self.loesung.werte[schluessel].groesse.si,
                           bemessung.werte[schluessel].groesse.si)

    def test_querkraft_und_sproedes_versagen_folgen(self):
        t = text(self.loesung)
        self.assertIn("m_{Rk}(N_{Ed})", t)
        sv = self.aufbau.sproede[KENNUNG]
        M = self.loesung.werte[f"{BASIS}.M_Rd_N0_pos"].groesse.si
        unten = next(e for e in sv.ergebnisse if e.lage.von_unten)
        self.assertEqual(unten.M_Rd, M)
        self.assertIn("M_Rk(N_Ed = 0)", unten.begruendung)


class TestGenaueLinie(unittest.TestCase):
    def test_jede_rechenart_und_jeder_satz(self):
        for art in ("handrechnung", "block", "parabel"):
            for satz in ("bemessung", "charakteristisch"):
                with self.subTest(art=art, satz=satz):
                    aufbau, loesung = gerechnet(art, satz)
                    mn = aufbau.nachweise[KENNUNG]
                    self.assertIs(mn.massgebend.wahl.art, Rechenart(art))
                    # Die Vergleichslinie: Parabel neben der Hand, sonst die Hand.
                    erwartet = Rechenart.PARABEL if art == "handrechnung" else Rechenart.HANDRECHNUNG
                    self.assertIs(mn.vergleich.wahl.art, erwartet)
                    for a in mn.auswertungen:
                        self.assertEqual(a.innerhalb,
                                         mn.massgebend.innerhalb(a.schnittgroessen.N_Ed.si,
                                                                 a.schnittgroessen.M_Ed.si))

    def test_drei_wege_zum_selben_widerstand(self):
        """
        Block und Parabel sind beide genau und liegen beisammen. Die Hand
        lässt den Druckstahl weg: an der Stütze, wo unten viel Stahl gedrückt
        wird, liegt sie deutlich darunter. Höher als die genaue Linie liegt sie
        kaum -- nur dort, wo der Stahl bei eps_ud reisst, bevor der Beton
        eps_c2d erreicht, ist die Druckzone weniger voll als ihr Block.
        """
        _, hand = gerechnet()
        _, block = gerechnet("block")
        _, parabel = gerechnet("parabel")
        for fall in ("Feld", "Feld_mit_Druck", "Stütze"):
            schluessel = f"{BASIS}.{fall}.M_Rd_bei_N_Ed"
            h, b, p = (x.werte[schluessel].groesse.si for x in (hand, block, parabel))
            self.assertAlmostEqual(b / p, 1.0, delta=0.01, msg=fall)
            self.assertLess(h / p, 1.002, msg=fall)
        stuetze = f"{BASIS}.Stütze.M_Rd_bei_N_Ed"
        self.assertLess(hand.werte[stuetze].groesse.si, 0.95 * parabel.werte[stuetze].groesse.si)

    def test_die_herleitung_zeigt_die_probe(self):
        _, loesung = gerechnet("block")
        t = text(loesung)
        self.assertIn("Resistenzlinie aus Dehnungsebenen", t)
        self.assertIn("Probe", t)
        self.assertIn("Massgebend", t)

    def test_phi_nur_bei_der_parabel(self):
        _, null = gerechnet("parabel", kriechzahl=0.0)
        _, zwei = gerechnet("parabel", kriechzahl=2.0)
        schluessel = f"{BASIS}.Feld_mit_Druck.M_Rd_bei_N_Ed"
        self.assertNotEqual(null.werte[schluessel].groesse.si, zwei.werte[schluessel].groesse.si)
        _, block_null = gerechnet("block", kriechzahl=0.0)
        _, block_zwei = gerechnet("block", kriechzahl=2.0)
        self.assertEqual(block_null.werte[schluessel].groesse.si,
                         block_zwei.werte[schluessel].groesse.si)

    def test_querkraft_liest_aus_derselben_linie(self):
        aufbau, loesung = gerechnet("parabel")
        mn, qk = aufbau.nachweise[KENNUNG], aufbau.querkraft[KENNUNG]
        self.assertEqual(qk.mn.moment_bei(-300e3, True), mn.massgebend.moment_bei(-300e3, True))


class TestDatei(unittest.TestCase):
    def test_hin_und_zurueck(self):
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].tragsicherheit_wahl = RechenwahlEintrag(
            kriechzahl=1.5, werkstoffsatz="charakteristisch", rechenart="parabel")
        kopie = Projekt.aus_dict(json.loads(json.dumps(projekt.als_dict())))
        self.assertEqual(kopie.querschnitte[0].tragsicherheit_wahl,
                         projekt.querschnitte[0].tragsicherheit_wahl)

    def test_alte_datei_uebernimmt_das_phi_der_platte(self):
        daten = Projekt.beispiel().als_dict()
        platte = daten["querschnitte"][0]
        del platte["tragsicherheit_wahl"]
        platte["kriechzahl"] = 1.5
        wahl = Projekt.aus_dict(daten).querschnitte[0].tragsicherheit_wahl
        self.assertEqual(wahl, RechenwahlEintrag(kriechzahl=1.5))

    def test_elastisch_gibt_es_hier_nicht(self):
        daten = Projekt.beispiel().als_dict()
        daten["querschnitte"][0]["tragsicherheit_wahl"] = {"rechenart": "elastisch"}
        with self.assertRaises(ProjektFehler) as fehler:
            Projekt.aus_dict(daten)
        self.assertIn("Tragsicherheit", str(fehler.exception))

    def test_negatives_phi(self):
        daten = Projekt.beispiel().als_dict()
        daten["querschnitte"][0]["tragsicherheit_wahl"] = {"kriechzahl": -1}
        with self.assertRaises(ProjektFehler):
            Projekt.aus_dict(daten)


if __name__ == "__main__":
    unittest.main()
