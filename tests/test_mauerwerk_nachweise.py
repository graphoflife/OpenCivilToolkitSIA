"""
Die Wand aus Mauerwerk, Schritt 14b: k_N nach Theorie 2. Ordnung gegen
Figur 5 und Euler, der Lastabtrag über Pfeiler und Stürze gegen die
Handrechnung, die Nachweise der Normalkraft und der Teilflächenpressung im
Beispiel -- und was Zeichnung und Zusammenfassung davon zeigen.
"""

import math
import unittest

from opencivil.bericht.zusammenfassung import angaben
from opencivil.mauerwerk.knicken import AUSMITTE, DRUCK, STABILITAET, k_N
from opencivil.mauerwerk.lasten import abtragen
from opencivil.mauerwerk.modell import Oeffnung, Rechteck, Sturzart, Wandlast, pfeiler
from opencivil.projekt import Projekt
from opencivil.projekt.aufbau.mauerwerk import FALSCH_GEZEICHNET, OHNE_KOMBINATION
from tests.test_mauerwerk import beispielwand, zeichnung

#: SIA 266:2015, Figur 5 (S. 26), am Seitenbild abgelesen: je h_w/t_w der
#: Beiwert k_N für e_z/t_w = 0.05, 0.10 … 0.30 -- beide Ränder gelenkig, mit
#: derselben Ausmitte, E_xd/f_xd = 1000. Die Kurve 0.35 fehlt: sie liegt fast
#: doppelt so hoch, wie Figur 3 und 4 es zulassen (opencivil/mauerwerk/knicken.py).
FIGUR_5 = {
    12: (0.880, 0.759, 0.639, 0.518, 0.394, 0.267),
    16: (0.854, 0.715, 0.575, 0.433, 0.289, 0.169),
    20: (0.810, 0.640, 0.467, 0.303, 0.187, 0.107),
    24: (0.729, 0.508, 0.332, 0.213, 0.131, 0.075),
}


class TestKnicken(unittest.TestCase):
    """Der Beiwert k_N (SIA 266:2015, 4.3.1.3, Gl. (11))."""

    def test_die_kurven_der_figur_5(self):
        """Auf etwa 0.006 genau -- so dick sind die Linien des Bilds."""
        for ht, werte in FIGUR_5.items():
            for i, abgelesen in enumerate(werte):
                e = 0.05 * (i + 1)
                with self.subTest(h_t=ht, e_t=e):
                    self.assertAlmostEqual(k_N(ht, e, e).k_N, abgelesen, delta=0.008)

    def test_mittig_knickt_die_wand_wie_ein_eulerstab(self):
        """Ohne Ausmitte n = π² · (E/f) / (12 · (h/t)²), mit E/f = 1000 also 822.5/(h/t)²."""
        for ht in (30, 40):
            with self.subTest(h_t=ht):
                erg = k_N(ht, 0.0, 0.0)
                self.assertAlmostEqual(erg.k_N, math.pi ** 2 * 1000 / 12 / ht ** 2, delta=0.004)
                self.assertEqual(erg.grund, STABILITAET)

    def test_kurz_und_mittig_die_ganze_festigkeit(self):
        erg = k_N(5, 0.0, 0.0)
        self.assertEqual((erg.k_N, erg.grund), (1.0, DRUCK))

    def test_kurz_und_ausmittig_nach_gl_6(self):
        """Kaum Schlankheit: nur Gl. (6) begrenzt, k_N = 1 − 2 · e/t."""
        erg = k_N(1, 0.2, 0.2)
        self.assertAlmostEqual(erg.k_N, 0.6, delta=0.002)
        self.assertEqual(erg.grund, AUSMITTE)

    def test_schon_die_ausmitte_der_lasten_zu_gross(self):
        """Über 0.375 t trägt die Wand nichts -- schon ohne Last steht sie über der Grenze."""
        self.assertEqual(k_N(10, 0.4, 0.4).k_N, 0.0)

    def test_der_zustand_unter_der_last(self):
        """Unter n_d die verformte Wand: am Fuss die Ausmitte der Last, in der Mitte mehr."""
        erg = k_N(20, 0.1, 0.1, n_d=0.3)
        z = erg.bei_n_d
        self.assertAlmostEqual(z.e_u, 0.1)
        self.assertGreater(abs(z.e_max), 0.1)
        self.assertAlmostEqual(z.hoehe, 0.5)
        self.assertIsNone(k_N(20, 0.1, 0.1, n_d=0.9).bei_n_d)


#: Eine Wand von 6 × 2.7 m mit einer Türe von 2 bis 3 m und einem Betonsturz,
#: 200 mm hoch, auf jeder Seite 150 mm aufgelegt.
WAND = Rechteck(0, 0, 6, 2.7)
TUERE = Oeffnung("O1", ((2, 0), (3, 0), (3, 2.1), (2, 2.1)), Sturzart.BETON, 0.2, 0.15)


class TestLastabtrag(unittest.TestCase):
    """Wie die Lasten zu Pfeilern und Stürzen kommen -- gegen die Handrechnung."""

    def abtrag(self, oeffnungen, lasten, eigengewicht=0.0):
        return abtragen(WAND, oeffnungen, pfeiler(WAND, oeffnungen), lasten, eigengewicht)

    def test_eine_linienlast_ueber_der_tuere(self):
        """
        q = 10 kN/m auf der ganzen Krone. Die Auflager liegen bei 1.925 und
        3.075 m. Links trägt P1 0 bis 1.85 m selbst, das linke Auflager 1.85 bis
        2 m und die halbe Türe: 1.5 + 5 = 6.5 kN, zusammen 18.5 + 6.5 = 25 kN.
        Rechts ebenso, 28.5 + 6.5 = 35 kN.
        """
        a = self.abtrag([TUERE], [Wandlast("q", 0, 6, 2.7, 60e3, 0.02)])
        self.assertAlmostEqual(a.N["P1"], 25e3)
        self.assertAlmostEqual(a.N["P2"], 35e3)
        self.assertAlmostEqual(a.R[("O1", "links")], 6.5e3)
        self.assertAlmostEqual(a.R[("O1", "rechts")], 6.5e3)
        self.assertAlmostEqual(a.M["P1"] / a.N_L["P1"], 0.02)
        self.assertEqual(a.unten, 0.0)

    def test_das_eigengewicht(self):
        """
        1 kN/m² Wand: P1 trägt 1.85 · 2.7 und 0.15 · 2.1 m² selbst, dazu sein
        Auflager -- 0.15 · 0.6 und die halbe Wand über der Türe, 0.5 · 0.6 m²:
        4.995 + 0.315 + 0.39 = 5.7 kN.
        """
        a = self.abtrag([TUERE], [], 1e3)
        self.assertAlmostEqual(a.N["P1"], 5.7e3)
        self.assertAlmostEqual(a.N["P2"], 8.4e3)
        self.assertAlmostEqual(a.R[("O1", "links")], 0.39e3)
        self.assertEqual((a.N_L["P1"], a.M["P1"]), (0.0, 0.0))

    def test_die_ausmitte_am_kopf_ist_die_der_lasten(self):
        """Das Eigengewicht kommt zu N, nicht zu N_L: M / N_L bleibt die Ausmitte der Last."""
        a = self.abtrag([TUERE], [Wandlast("q", 0, 6, 2.7, 60e3, 0.02)], 1e3)
        self.assertAlmostEqual(a.N["P1"], 30.7e3)
        self.assertAlmostEqual(a.M["P1"] / a.N_L["P1"], 0.02)

    def test_oeffnungen_uebereinander_verlieren_nichts(self):
        """Ein Fenster über einer Türe: was oben liegt, kommt ganz unten an."""
        fenster = Oeffnung("O2", ((4, 1), (5, 1), (5, 2.0), (4, 2.0)), Sturzart.BETON, 0.2, 0.15)
        tuere = Oeffnung("O3", ((3.9, 0), (5.1, 0), (5.1, 0.6), (3.9, 0.6)), Sturzart.BETON,
                         0.2, 0.15)
        a = self.abtrag([TUERE, fenster, tuere], [Wandlast("q", 0, 6, 2.7, 60e3)], 1e3)
        self.assertAlmostEqual(sum(a.N.values()) + a.unten, 60e3 + 1e3 * (16.2 - 2.1 - 1.0 - 0.72))


def mit_lasten(p, **felder):
    """Die Wand des Beispiels mit den Lastfällen einer frischen Wand und 76.5 kN/m im GZT."""
    w = beispielwand(p, fuss="eingespannt", **felder)
    w.standardfaelle()
    _, auflast, nutzlast = w.lastfaelle
    w.linienlast(auflast, (0, 2.7), (6, 2.7), wert=40, e=20)
    w.linienlast(nutzlast, (0, 2.7), (6, 2.7), wert=15, e=20)
    return w


def urteile(p, w):
    """Je Stelle der Wand -- «P1 – GZT» -- ihr Urteil."""
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.materialziele(), *aufbau.ziele_von(w.kennung))
    return {u.fall: u for u in loesung.urteile}


class TestNachweise(unittest.TestCase):
    """Normalkraft je Pfeiler, Teilflächenpressung je Sturzauflager -- je Kombination."""

    def test_die_normalkraft_von_p1(self):
        """
        76.5 kN/m auf 0.8 m Pfeiler und eine halbe Türe, 1.3 m: 99.45 kN; dazu
        1.35 · 3.15 kN/m² auf 2.46 m² Mauerwerk, 10.46 kN -- 109.91 kN. Am
        eingespannten Fuss nimmt die Einspannung das Moment; am Kopf steht die
        Last 20 mm ausmittig, e_o = 0.1143 t_w -- das Eigengewicht verkleinert
        das nicht. Gl. (6) am Kopf begrenzt, k_N = 1 − 2 · 0.1143 = 0.7714,
        und N_xRd = 0.7714 · 0.8 · 0.175 · 2975 kN/m² = 321.3 kN.
        """
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        u = urteile(p, mit_lasten(p))["P1 – GZT"]
        self.assertAlmostEqual(u.einwirkung.groesse.si, 109.911e3, delta=5)
        k_N = 1 - 2 * 0.02 / 0.175
        self.assertAlmostEqual(u.widerstand.groesse.si, k_N * 0.8 * 0.175 * 2975e3, delta=50)
        self.assertTrue(u.erfuellt)

    def test_das_auflager_der_tuere(self):
        """
        Das linke Auflager trägt 0.15 m über sich und die halbe Türe, 0.65 m
        · 76.5 kN/m, dazu 1.35 · 3.15 kN/m² auf 0.39 m²: 51.38 kN. Am Rand der
        Öffnung k_m = 1: R_Rd = 2.975 N/mm² · 150 · 175 mm² = 78.09 kN.
        """
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        u = urteile(p, mit_lasten(p))["O1 links – GZT"]
        self.assertAlmostEqual(u.einwirkung.groesse.si, 51.383e3, delta=5)
        self.assertAlmostEqual(u.widerstand.groesse.si, 78.094e3, delta=1)

    def test_ein_gelenkiger_fuss_mit_ausmitte(self):
        """
        Der Pfeiler des Prüfprojekts: am Kopf eingespannt, am Fuss gelenkig
        15 mm neben der Mitte, e_u = 0.1 t_w. Er ist kurz: Gl. (6) am Fuss
        begrenzt, k_N = 1 − 2 · 0.1 = 0.8, N_xRd = 0.8 · 1.5 · 0.15 · 3500 = 630 kN.
        """
        p = Projekt.jeder_nachweis()
        w = next(x for x in p.mauerwerke if x.name == "Pfeiler aus Kalksandstein")
        u = urteile(p, w)["P1 – GZT"]
        self.assertAlmostEqual(u.einwirkung.groesse.si, (1.35 * 60 + 1.5 * 20) * 1.5e3
                               + 1.35 * 2.7e3 * 1.5 * 2.6, delta=1)
        self.assertAlmostEqual(u.widerstand.groesse.si, 630e3, delta=50)

    def test_ein_pfeiler_unter_zug_ist_nicht_gefuehrt(self):
        """Grau, nicht rot: unbewehrtes Mauerwerk trägt keinen Zug."""
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        w = mit_lasten(p)
        w.punktlast(w.lastfaelle[2], (0.4, 2.7), wert=-200)
        u = urteile(p, w)["P1 – GZT"]
        self.assertTrue(u.offen)
        self.assertFalse(u.verfehlt)
        self.assertIn("Am Kopf des Pfeilers P1 drücken die Lasten nicht", u.begruendung)

    def test_ohne_kombination_kein_nachweis(self):
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        w = beispielwand(p)
        self.assertIn(OHNE_KOMBINATION, p.aufbauen().teile[w.kennung].ohne_nachweis)

    def test_eine_schraege_last_haelt_die_nachweise_an(self):
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        w = mit_lasten(p)
        w.linienlast(w.lastfaelle[1], (0, 2.7), (6, 2.0), wert=5)
        aufbau = p.aufbauen()
        self.assertIn(FALSCH_GEZEICHNET, aufbau.teile[w.kennung].ohne_nachweis)


class TestLastenPruefen(unittest.TestCase):
    """Was der Kern an einer Last beanstandet -- rot, mit ihrem Namen."""

    def meldungen(self, *orte):
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        w = mit_lasten(p)
        for ort in orte:
            w.punktlast(w.lastfaelle[1], ort, wert=10)
        return [(m["text"], m["fehler"]) for m in zeichnung(p, w)["meldungen"]]

    def test_auf_der_wand_keine_meldung(self):
        self.assertEqual(self.meldungen((3.4, 2.7)), [])

    def test_neben_der_wand(self):
        self.assertEqual(self.meldungen((6.5, 2.7)),
                         [("Die Last PL1 liegt nicht ganz auf der Wand.", True)])

    def test_in_einer_oeffnung(self):
        self.assertEqual(self.meldungen((1.3, 1.0)),
                         [("Die Last PL1 liegt in der Öffnung O1.", True)])


class TestWasDieOberflaecheZeigt(unittest.TestCase):

    def test_je_ort_das_ungünstigste_urteil(self):
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        u = zeichnung(p, mit_lasten(p))["urteile"]
        self.assertEqual(sorted(u), ["O1 links", "O1 rechts", "O2 links", "O2 rechts", "O3 links",
                                     "O3 rechts", "P1", "P2", "P3", "P4"])
        self.assertEqual(u["P1"]["zustand"], "erfuellt")
        self.assertTrue(u["P1"]["titel"].startswith("Normalkraft – GZT: erfüllt, "))

    def test_die_angaben_ueber_den_nachweisen(self):
        """Im Verband mal 0.85, μ_d ohne; vollfugig f_yd aus f_yd,v."""
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        w = mit_lasten(p)
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.materialziele(), *aufbau.ziele_von(w.kennung))
        gleichung, tabelle = angaben(aufbau, w.kennung, loesung)
        self.assertIn("Verbandmauerwerk – f, E und G mal 0.85", gleichung.latex)
        self.assertEqual([(z[1].latex, z[2], z[3]) for z in tabelle.zeilen],
                         [("f_{xd}", "3.50", "2.98"), ("f_{yd,v}", "1.60", "1.36"),
                          ("E_{xd}", "3500", "2975"), ("G_d", "1400", "1190"),
                          (r"\mu_d", "0.60", "0.60")])


if __name__ == "__main__":
    unittest.main()
