"""Tests für die Nachweise gegen sprödes Versagen."""

import math
import unittest

from opencivil.nachweis import mindestbewehrung, sproedes_versagen, zustand2
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
        namen = sorted(n for n, u in gefunden.items()
                       if n.startswith("Rissnormalkraft") and not u.still)
        self.assertEqual(namen, ["Rissnormalkraft x – 1. Lage",
                                 "Rissnormalkraft x – 4. Lage"])

    def test_ohne_zwaengung_rechnet_er_still_mit(self):
        """
        Ausgeschaltet heisst nicht weg: gerechnet wird weiter, damit unter der
        Tabelle ein Hinweis stehen kann -- in der Herleitung steht er nicht.
        """
        projekt = projekt_mit()
        projekt.querschnitte[0].zwaengung_x = False
        aufbau, gefunden = urteile(projekt)
        self.assertTrue(all(n.still for n in aufbau.rissnormalkraft.values()))
        rn = [u for n, u in gefunden.items() if n.startswith("Rissnormalkraft")]
        self.assertTrue(rn)
        self.assertTrue(all(u.still for u in rn))

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
        paare = [(z["zellen"][0], z["zellen"][1])
                 for z in antwort.daten["zusammenfassungen"]["q1"]["zeilen"]]
        art = r"\text{Zwängung auf Normalkraft (x)}"
        self.assertIn((art, r"\text{1. Lage}"), paare)
        self.assertIn((art, r"\text{4. Lage}"), paare)

    def test_einwirkung_und_widerstand_sind_kraefte(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": projekt_mit().als_dict()})
        zeile = next(z for z in antwort.daten["zusammenfassungen"]["q1"]["zeilen"]
                     if z["zellen"][0] == r"\text{Zwängung auf Normalkraft (x)}")
        self.assertIn("N_{Riss}", zeile["zellen"][3])
        self.assertIn("N_{s,adm,1,x}", zeile["zellen"][2])
        self.assertIn(r"\mathrm{kN}", zeile["zellen"][2])


# ===========================================================================
# Rissmoment
# ===========================================================================


class TestZustand2(unittest.TestCase):
    """Der gerissene Querschnitt für sich."""

    def test_wertigkeit_von_hand(self):
        """
        n = (E_s/E_cm)·(1+φ) = (200000/33620)·3 = 17.85

        Die Klammer ist wesentlich: E_s/(E_cm·(1+φ)) wäre das Gegenteil.
        """
        n = zustand2.wertigkeit(E_s=200e9, E_cm=33.62e9, phi=2.0)
        self.assertAlmostEqual(n, 17.85, delta=0.02)

    def test_nulllinie_von_hand(self):
        """
        n = 17.846, A_s = 2450 mm², b = 1000 mm, d = 260.1 mm:

            ρ = 17.846·2450e-6/1.0 = 43.72 mm
            x = √(43.72² + 2·260.1·43.72) − 43.72 = 113.3 mm
            z = 260.1 − 113.3/3 = 222.3 mm
        """
        z2 = zustand2.gerissen(n=17.846, a_s=2450e-6, b=1.0, d=0.2601)
        self.assertAlmostEqual(z2.x * 1e3, 113.3, delta=0.2)
        self.assertAlmostEqual(z2.z * 1e3, 222.3, delta=0.2)

    def test_die_nulllinie_erfuellt_das_erste_moment(self):
        """b·x²/2 = n·A_s·(d − x) -- die Bedingung, aus der x kommt."""
        n, a_s, b, d = 17.846, 2450e-6, 1.0, 0.2601
        x = zustand2.gerissen(n=n, a_s=a_s, b=b, d=d).x
        self.assertAlmostEqual(b * x * x / 2.0, n * a_s * (d - x), places=9)

    def test_kriechen_ist_immer_konservativ(self):
        """
        dx/dρ > 0, also senkt ein grösseres φ den Hebelarm -- für jede
        Geometrie. Nachgerechnet über einen weiten Bereich, damit die Aussage
        nicht an einem Zahlenbeispiel hängt.
        """
        for a_s in (200e-6, 1000e-6, 5000e-6):
            for d in (0.05, 0.26, 0.9):
                with self.subTest(a_s=a_s, d=d):
                    ohne = zustand2.gerissen(
                        n=zustand2.wertigkeit(E_s=200e9, E_cm=33.62e9, phi=0.0),
                        a_s=a_s, b=1.0, d=d)
                    mit = zustand2.gerissen(
                        n=zustand2.wertigkeit(E_s=200e9, E_cm=33.62e9, phi=2.0),
                        a_s=a_s, b=1.0, d=d)
                    self.assertGreater(mit.x, ohne.x)
                    self.assertLess(mit.z, ohne.z)

    def test_ohne_bewehrung_gibt_es_keine_nulllinie(self):
        with self.assertRaises(ValueError):
            zustand2.gerissen(n=17.8, a_s=0.0, b=1.0, d=0.26)


class TestRissmomentGroessen(unittest.TestCase):
    def test_von_hand(self):
        """
        h = 300 mm, f_ctm = 2.9 N/mm²:

            k_t      = 1/(1 + 0.5·0.300/3) = 0.9524
            f_ct,eff = 2.762 N/mm²
            M_Riss   = 2.762 · 300²·1000/6 = 41.4 kNm
        """
        g = sproedes_versagen.rissmoment(h=0.300, b=1.0, f_ctm=2.9e6)
        self.assertAlmostEqual(g.k_t, 0.9524, places=4)
        self.assertAlmostEqual(g.f_ct_eff / 1e6, 2.762, places=3)
        self.assertAlmostEqual(g.M_Riss / 1e3, 41.4, delta=0.1)

    def test_der_teiler_unterscheidet_sich_vom_zwang(self):
        """
        Unter Biegung reisst nur der Randbereich, unter Zwang die halbe Höhe --
        darum h/3 statt h. Das Rissmoment ist damit weniger abgemindert.
        """
        biegung = sproedes_versagen.rissmoment(h=0.800, b=1.0, f_ctm=2.9e6)
        zwang = mindestbewehrung.rissnormalkraft(
            h=0.800, b=1.0, f_ctm=2.9e6, begrenzt=False)
        self.assertGreater(biegung.k_t, zwang.k_t)

    def test_die_dicke_geht_ungekuerzt_ein(self):
        """Die 500-mm-Grenze gilt nur für die Zwängung."""
        g = sproedes_versagen.rissmoment(h=0.800, b=1.0, f_ctm=2.9e6)
        # M_Riss waechst mit h^2 -- bei 500 mm waere es weniger als die Haelfte.
        self.assertGreater(g.M_Riss,
                           sproedes_versagen.rissmoment(
                               h=0.500, b=1.0, f_ctm=2.9e6).M_Riss * 2.0)


def projekt_zwang_biegung(**abweichungen) -> Projekt:
    """Zwängung auf Biegung für alle vier Lagen eingeschaltet."""
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    q.zwaengung_biegung_lagen = [True] * 4
    for name, wert in abweichungen.items():
        setattr(q, name, wert)
    return projekt


class TestZwaengungBiegung(unittest.TestCase):
    """
    Die Stahlspannung aus einer aufgezwungenen Krümmung.

    Nicht zu verwechseln mit dem Nachweis gegen sprödes Versagen: dort steht
    der Biegewiderstand gegen das Rissmoment, hier die Stahlspannung gegen
    ihre Grenze.
    """

    def test_erste_lage_von_hand(self):
        """
        1. Lage x, φ = 2, normale Anforderung:

            n       = 17.85
            x       = 113.3 mm,  z = 222.3 mm
            M_s,adm = 500 · 2450 · 222.3 = 272.3 kNm
            M_Riss  = 41.4 kNm
            α       = 6.58
        """
        aufbau, _ = urteile(projekt_zwang_biegung())
        erg = aufbau.zwaengung_biegung["q1.x"].ergebnisse[0]
        self.assertEqual(erg.lage.nummer, 1)
        self.assertAlmostEqual(erg.n, 17.85, delta=0.02)
        self.assertAlmostEqual(erg.x * 1e3, 113.3, delta=0.3)
        self.assertAlmostEqual(erg.hebelarm * 1e3, 222.3, delta=0.3)
        self.assertAlmostEqual(erg.M_s_adm / 1e3, 272.3, delta=0.5)
        self.assertAlmostEqual(erg.erfuellungsgrad, 6.58, delta=0.03)
        self.assertTrue(erg.erfuellt)

    def test_nur_die_gewaehlten_lagen_sind_laut(self):
        """Gerechnet wird überall, sichtbar ist die eingeschaltete Lage."""
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].zwaengung_biegung_lagen = [False, True, False, False]
        aufbau, gefunden = urteile(projekt)
        self.assertEqual(sorted(aufbau.zwaengung_biegung), ["q1.x", "q1.y"])
        self.assertTrue(aufbau.zwaengung_biegung["q1.x"].still)
        laut = [n for n, u in gefunden.items()
                if n.startswith("Zwängung Biegung") and not u.still]
        self.assertEqual(laut, ["Zwängung Biegung y – 2. Lage"])

    def test_ohne_gewaehlte_lage_rechnet_er_still_mit(self):
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].zwaengung_biegung_lagen = [False] * 4
        aufbau, gefunden = urteile(projekt)
        self.assertTrue(all(n.still for n in aufbau.zwaengung_biegung.values()))
        zb = [u for n, u in gefunden.items() if n.startswith("Zwängung Biegung")]
        self.assertEqual(len(zb), 4)
        self.assertTrue(all(u.still for u in zb))

    def test_bei_den_oberen_lagen_wird_von_unten_gemessen(self):
        aufbau, _ = urteile(projekt_zwang_biegung())
        nach_lage = {e.lage.nummer: e
                     for e in aufbau.zwaengung_biegung["q1.x"].ergebnisse}
        h = 0.300
        self.assertAlmostEqual(nach_lage[1].d, nach_lage[1].z_s)
        self.assertAlmostEqual(nach_lage[4].d, h - nach_lage[4].z_s)

    def test_kriechen_macht_den_nachweis_schwerer(self):
        """Der Hebelarm schrumpft -- φ > 0 liegt auf der sicheren Seite."""
        a, _ = urteile(projekt_zwang_biegung(kriechzahl=0.0))
        b, _ = urteile(projekt_zwang_biegung(kriechzahl=2.0))
        trocken = a.zwaengung_biegung["q1.x"].ergebnisse[0]
        kriechend = b.zwaengung_biegung["q1.x"].ergebnisse[0]

        self.assertLess(trocken.x, kriechend.x)
        self.assertGreater(trocken.hebelarm, kriechend.hebelarm)
        self.assertGreater(trocken.erfuellungsgrad, kriechend.erfuellungsgrad)

    def test_eine_leere_lage_ist_nicht_machbar(self):
        projekt = projekt_zwang_biegung()
        projekt.querschnitte[0].lagen[3].grund.durchmesser = 0.0
        projekt.querschnitte[0].lagen[3].zulage.durchmesser = 0.0
        _, gefunden = urteile(projekt)
        urteil = gefunden["Zwängung Biegung x – 4. Lage"]
        self.assertFalse(urteil.erfuellt)
        self.assertIn("nicht machbar", urteil.hinweis)
        self.assertIsNone(urteil.einwirkung)

    def test_zu_wenig_bewehrung_faellt_durch(self):
        projekt = projekt_zwang_biegung()
        lage = projekt.querschnitte[0].lagen[3]
        lage.grund.durchmesser = 6.0
        lage.grund.abstand = 300.0
        lage.zulage.durchmesser = 0.0
        projekt.querschnitte[0].h = 600.0
        _, gefunden = urteile(projekt)
        self.assertFalse(gefunden["Zwängung Biegung x – 4. Lage"].erfuellt)

    def test_die_herleitung_zeigt_beide_querschnitte(self):
        from opencivil.core.protokoll import GleichungBlock

        aufbau = projekt_zwang_biegung().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        titel = [b.titel for b in loesung.protokoll.alle_bloecke()
                 if isinstance(b, GleichungBlock)]
        for erwartet in ("Rissmoment des ungerissenen Querschnitts",
                         "Wertigkeit im gerissenen Zustand",
                         "Nulllinie des gerissenen Querschnitts",
                         "Innerer Hebelarm",
                         "Aufnehmbares Moment der Bewehrung"):
            self.assertIn(erwartet, titel)


def projekt_sproede(**abweichungen) -> Projekt:
    """Sprödes Versagen für die 1. Lage eingeschaltet."""
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    q.sproede_lagen = [True, False, False, False]
    for name, wert in abweichungen.items():
        setattr(q, name, wert)
    return projekt


class TestSproedesVersagen(unittest.TestCase):
    """M_Rd(N_Ed = 0) gegen M_Riss -- der einfachere und strengere Weg."""

    def test_erste_lage_von_hand(self):
        """
        1. Lage x: M_Rd(N=0) = 248.7 kNm, M_Riss = 41.4 kNm, α = 6.01.
        """
        aufbau, _ = urteile(Projekt.beispiel())
        erg = aufbau.sproede["q1.x"].ergebnisse[0]
        self.assertEqual(erg.lage.nummer, 1)
        self.assertAlmostEqual(erg.M_Rd / 1e3, 248.7, delta=0.5)
        self.assertAlmostEqual(aufbau.sproede["q1.x"].groessen.M_Riss / 1e3,
                               41.4, delta=0.1)
        self.assertAlmostEqual(erg.erfuellungsgrad, 6.01, delta=0.05)
        self.assertTrue(erg.erfuellt)

    def test_vorgegeben_ist_keine_lage(self):
        """
        Eingeschaltet wird der Nachweis von Hand; von selbst rechnet er still
        mit. Eine Vorgabe stünde sonst ungefragt in jeder Tabelle.
        """
        _, gefunden = urteile(Projekt.beispiel())
        sv = {n: u for n, u in gefunden.items() if n.startswith("Sprödes Versagen")}
        self.assertEqual(len(sv), 4)
        self.assertFalse([n for n, u in sv.items() if not u.still])

    def test_die_eingeschaltete_lage_ist_laut(self):
        _, gefunden = urteile(projekt_sproede())
        laut = sorted(n for n, u in gefunden.items()
                      if n.startswith("Sprödes Versagen") and not u.still)
        self.assertEqual(laut, ["Sprödes Versagen x – 1. Lage"])

    def test_die_obere_lage_nimmt_den_negativen_eckwert(self):
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].sproede_lagen = [True, False, False, True]
        aufbau, _ = urteile(projekt)
        nach_lage = {e.lage.nummer: e for e in aufbau.sproede["q1.x"].ergebnisse}
        # Die 4. Lage traegt weniger -- ⌀12 gegen ⌀18+⌀12.
        self.assertLess(nach_lage[4].M_Rd, nach_lage[1].M_Rd)
        self.assertGreater(nach_lage[4].M_Rd, 0.0)

    def test_ohne_gewaehlte_lage_rechnet_er_still_mit(self):
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].sproede_lagen = [False] * 4
        aufbau, gefunden = urteile(projekt)
        self.assertTrue(all(n.still for n in aufbau.sproede.values()))
        sv = [u for n, u in gefunden.items() if n.startswith("Sprödes Versagen")]
        self.assertEqual(len(sv), 4)
        self.assertTrue(all(u.still for u in sv))

    def test_er_laeuft_ohne_schnittgroessen(self):
        """Die Resistenzlinie gehört dem Querschnitt, nicht der Einwirkung."""
        projekt = projekt_sproede(kombinationen=[])
        aufbau, gefunden = urteile(projekt)
        self.assertIn("q1.x", aufbau.sproede)
        self.assertTrue([n for n, u in gefunden.items()
                         if n.startswith("Sprödes Versagen") and not u.still])

    def test_zu_wenig_bewehrung_faellt_durch(self):
        projekt = Projekt.beispiel()
        lage = projekt.querschnitte[0].lagen[0]
        lage.grund.durchmesser = 6.0
        lage.grund.abstand = 300.0
        lage.zulage.durchmesser = 0.0
        projekt.querschnitte[0].h = 600.0
        _, gefunden = urteile(projekt)
        self.assertFalse(gefunden["Sprödes Versagen x – 1. Lage"].erfuellt)

    def test_die_herleitung_stellt_beide_gegenueber(self):
        from opencivil.core.protokoll import GleichungBlock

        aufbau = projekt_sproede().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        titel = [b.titel for b in loesung.protokoll.alle_bloecke()
                 if isinstance(b, GleichungBlock)]
        for erwartet in ("Rissmoment des ungerissenen Querschnitts",
                         "Biegewiderstand gegen Rissmoment"):
            self.assertIn(erwartet, titel)

    def test_die_stille_lage_steht_nicht_in_der_herleitung(self):
        """Mitrechnen ja, mitschreiben nein -- sonst wäre still nur ein Wort."""
        from opencivil.core.protokoll import GleichungBlock

        aufbau = projekt_sproede().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        titel = [b.titel for b in loesung.protokoll.alle_bloecke()
                 if isinstance(b, GleichungBlock)]
        self.assertIn("Biegewiderstand gegen Rissmoment", titel)
        # Vier Lagen sind gerechnet, geschrieben ist die eine eingeschaltete.
        self.assertEqual(titel.count("Biegewiderstand gegen Rissmoment"), 1)
