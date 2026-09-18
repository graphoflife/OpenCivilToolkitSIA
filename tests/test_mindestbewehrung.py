"""Tests für die Nachweise gegen sprödes Versagen."""

import math
import unittest

from opencivil.nachweis import mindestbewehrung
from opencivil.projekt import Projekt
from opencivil.web import dienst


def projekt_mit(**abweichungen) -> Projekt:
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    q.zwaengung_x = True
    for name, wert in abweichungen.items():
        setattr(q, name, wert)
    return projekt


def urteile(projekt: Projekt):
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return aufbau, {u.name: u for u in loesung.urteile}


class TestRisskraft(unittest.TestCase):
    """Die Formeln für sich, ohne Rechenwerk."""

    def test_von_hand(self):
        """
        h = 300 mm, b = 1000 mm, f_ctm = 2.9 N/mm², unbegrenzt:

            k_t      = 1/(1 + 0.5·0.300)     = 0.8696
            f_ct,eff = 0.8696 · 2.9          = 2.522 N/mm²
            N_Riss   = 0.150 · 1.0 · 2.522e6 = 378.2 kN
        """
        g = mindestbewehrung.rissnormalkraft(
            h=0.300, b=1.0, f_ctm=2.9e6, begrenzt=False)
        self.assertAlmostEqual(g.h_eff, 0.300)
        self.assertAlmostEqual(g.k_t, 0.8696, places=4)
        self.assertAlmostEqual(g.f_ct_eff / 1e6, 2.522, places=3)
        self.assertAlmostEqual(g.N_Riss / 1e3, 378.2, delta=0.2)

    def test_die_begrenzung_greift_erst_ueber_500_mm(self):
        duenn = mindestbewehrung.rissnormalkraft(
            h=0.300, b=1.0, f_ctm=2.9e6, begrenzt=True)
        self.assertAlmostEqual(duenn.h_eff, 0.300)

        dick = mindestbewehrung.rissnormalkraft(
            h=0.800, b=1.0, f_ctm=2.9e6, begrenzt=True)
        self.assertAlmostEqual(dick.h_eff, 0.500)
        # k_t = 1/(1+0.25) = 0.800, N_Riss = 0.250 · 1.0 · 0.8·2.9e6
        self.assertAlmostEqual(dick.k_t, 0.800, places=3)
        self.assertAlmostEqual(dick.N_Riss / 1e3, 580.0, delta=0.5)

    def test_ohne_begrenzung_zaehlt_die_ganze_dicke(self):
        dick = mindestbewehrung.rissnormalkraft(
            h=0.800, b=1.0, f_ctm=2.9e6, begrenzt=False)
        self.assertAlmostEqual(dick.h_eff, 0.800)
        self.assertGreater(dick.N_Riss,
                           mindestbewehrung.rissnormalkraft(
                               h=0.800, b=1.0, f_ctm=2.9e6, begrenzt=True).N_Riss)


class TestZulaessigeStahlspannung(unittest.TestCase):
    werte = dict(f_yk=500e6, E_s=200e9, f_ctm=2.9e6, durchmesser=18e-3)

    def test_normal_ist_die_fliessgrenze(self):
        """f_yk, nicht f_yd: nachgewiesen wird das Überleben des Risses."""
        sigma = mindestbewehrung.zulaessige_stahlspannung(
            anforderung="normal", **self.werte)
        self.assertAlmostEqual(sigma / 1e6, 500.0)

    def test_erhoeht_von_hand(self):
        """sqrt(9 · 200000 · 2.9 · 0.5 / 18) = sqrt(145000) = 380.8 N/mm²."""
        sigma = mindestbewehrung.zulaessige_stahlspannung(
            anforderung="erhoeht", **self.werte)
        self.assertAlmostEqual(sigma / 1e6, math.sqrt(145000.0), places=3)
        self.assertAlmostEqual(sigma / 1e6, 380.8, delta=0.1)

    def test_hoch_von_hand(self):
        """sqrt(9 · 200000 · 2.9 · 0.2 / 18) = sqrt(58000) = 240.8 N/mm²."""
        sigma = mindestbewehrung.zulaessige_stahlspannung(
            anforderung="hoch", **self.werte)
        self.assertAlmostEqual(sigma / 1e6, 240.8, delta=0.1)

    def test_der_duennere_stab_darf_mehr(self):
        """Er verteilt den Riss auf mehr Stäbe."""
        duenn = mindestbewehrung.zulaessige_stahlspannung(
            anforderung="hoch", **{**self.werte, "durchmesser": 8e-3})
        dick = mindestbewehrung.zulaessige_stahlspannung(
            anforderung="hoch", **{**self.werte, "durchmesser": 26e-3})
        self.assertGreater(duenn, dick)

    def test_die_fliessgrenze_bleibt_die_obere_schranke(self):
        """Ein sehr dünner Stab dürfte rechnerisch mehr -- er darf es nicht."""
        sigma = mindestbewehrung.zulaessige_stahlspannung(
            anforderung="erhoeht", **{**self.werte, "durchmesser": 6e-3})
        self.assertAlmostEqual(sigma / 1e6, 500.0)

    def test_die_anforderung_ist_monoton(self):
        reihe = [mindestbewehrung.zulaessige_stahlspannung(
            anforderung=a, **self.werte) for a in ("normal", "erhoeht", "hoch")]
        self.assertEqual(reihe, sorted(reihe, reverse=True))


class TestNachweis(unittest.TestCase):
    def test_zwei_urteile_je_richtung(self):
        """Ein Zwang kennt keine Zugseite -- beide Lagen müssen können."""
        _, gefunden = urteile(projekt_mit())
        namen = sorted(n for n in gefunden if n.startswith("Rissnormalkraft"))
        self.assertEqual(namen, ["Rissnormalkraft x – 1. Lage",
                                 "Rissnormalkraft x – 4. Lage"])

    def test_ohne_zwaengung_laeuft_er_nicht(self):
        projekt = projekt_mit()
        projekt.querschnitte[0].zwaengung_x = False
        aufbau, gefunden = urteile(projekt)
        self.assertEqual(aufbau.rissnormalkraft, {})
        self.assertFalse([n for n in gefunden if n.startswith("Rissnormalkraft")])

    def test_beide_richtungen_getrennt(self):
        projekt = projekt_mit(zwaengung_y=True)
        aufbau, gefunden = urteile(projekt)
        self.assertEqual(sorted(aufbau.rissnormalkraft), ["q1.x", "q1.y"])
        self.assertEqual(
            len([n for n in gefunden if n.startswith("Rissnormalkraft")]), 4)

    def test_erste_lage_von_hand(self):
        """
        1. Lage x: ⌀18@150 + ⌀12@150, A_s = 2450 mm², normale Anforderung.

            N_s,adm = 2450 · 500 = 1225 kN
            N_Riss  = 378.2 kN
            α       = 3.24
        """
        aufbau, gefunden = urteile(projekt_mit())
        erg = aufbau.rissnormalkraft["q1.x"].ergebnisse[0]
        self.assertEqual(erg.lage.nummer, 1)
        self.assertAlmostEqual(erg.a_s * 1e6, 2450.0, delta=2.0)
        self.assertAlmostEqual(erg.sigma_s_adm / 1e6, 500.0)
        self.assertAlmostEqual(erg.N_s_adm / 1e3, 1225.2, delta=1.0)
        self.assertAlmostEqual(erg.erfuellungsgrad, 3.24, delta=0.02)
        self.assertTrue(erg.erfuellt)

    def test_der_dickste_stab_der_lage_zaehlt(self):
        """
        Er verteilt den Riss auf die wenigsten Stäbe und bekommt damit die
        grösste Spannung -- also ist er massgebend.
        """
        aufbau, _ = urteile(projekt_mit(rissanforderung="hoch"))
        erg = aufbau.rissnormalkraft["q1.x"].ergebnisse[0]
        # Grund ⌀18, Zulage ⌀12 -> der Grundstab bestimmt.
        self.assertAlmostEqual(erg.durchmesser * 1e3, 18.0)

    def test_eine_haertere_anforderung_macht_den_nachweis_schwerer(self):
        grade = {}
        for anforderung in ("normal", "erhoeht", "hoch"):
            aufbau, _ = urteile(projekt_mit(rissanforderung=anforderung))
            grade[anforderung] = aufbau.rissnormalkraft["q1.x"].ergebnisse[0].erfuellungsgrad
        self.assertGreater(grade["normal"], grade["erhoeht"])
        self.assertGreater(grade["erhoeht"], grade["hoch"])

    def test_eine_leere_lage_ist_nicht_machbar(self):
        projekt = projekt_mit()
        projekt.querschnitte[0].lagen[3].grund.durchmesser = 0.0
        projekt.querschnitte[0].lagen[3].zulage.durchmesser = 0.0
        _, gefunden = urteile(projekt)
        urteil = gefunden["Rissnormalkraft x – 4. Lage"]
        self.assertFalse(urteil.erfuellt)
        self.assertIn("nicht machbar", urteil.hinweis)
        self.assertIsNone(urteil.einwirkung)
        self.assertIsNone(urteil.widerstand)

    def test_das_urteil_traegt_den_raum_seiner_platte(self):
        _, gefunden = urteile(projekt_mit())
        for name, urteil in gefunden.items():
            if name.startswith("Rissnormalkraft"):
                self.assertTrue(urteil.raum.startswith("querschnitt.q1"), urteil.raum)

    def test_die_herleitung_ist_vollstaendig(self):
        from opencivil.core.protokoll import GleichungBlock

        aufbau = projekt_mit(rissanforderung="erhoeht").aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        titel = [b.titel for b in loesung.protokoll.alle_bloecke()
                 if isinstance(b, GleichungBlock)]
        for erwartet in ("Rissaktive Plattendicke", "Beiwert für die Plattendicke",
                         "Wirksame Zugfestigkeit",
                         "Risskraft der gezogenen Querschnittshälfte",
                         "Aufnehmbare Risskraft"):
            self.assertIn(erwartet, titel)
        self.assertTrue(any("Zulässige Stahlspannung" in t for t in titel))


class TestInDerZusammenfassung(unittest.TestCase):
    def test_die_zeilen_stehen_da(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": projekt_mit().als_dict()})
        namen = [z["zellen"][0]
                 for z in antwort.daten["zusammenfassungen"]["q1"]["zeilen"]]
        self.assertIn(r"\text{N\_Riss: 1. Lage x}", namen)
        self.assertIn(r"\text{N\_Riss: 4. Lage x}", namen)

    def test_einwirkung_und_widerstand_sind_kraefte(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": projekt_mit().als_dict()})
        zeile = next(z for z in antwort.daten["zusammenfassungen"]["q1"]["zeilen"]
                     if z["zellen"][0] == r"\text{N\_Riss: 1. Lage x}")
        self.assertIn("N_{Riss}", zeile["zellen"][2])
        self.assertIn("N_{s,adm,1,x}", zeile["zellen"][1])
        self.assertIn(r"\mathrm{kN}", zeile["zellen"][1])
