"""
Grundbruch und Gleiten eines Flachfundaments (opencivil.geotechnik.grundbruch).

Die Faktoren gegen die Tabellen des Kapitels 9.2, das der Benutzer geliefert
hat (9.2.8, 9.2.11, 9.2.13, 9.2.14, 9.2.16, 9.2.17, 9.2.18), und gegen seine
eigene Tabelle der Faktoren; dazu die Lagen des Grundwassers, die
undrainierte Formel, das Gleiten, die Pruefungen der Eingabe und was die
Oberflaeche davon zu sehen bekommt.
"""

import math
import unittest

from opencivil.bericht.zusammenfassung import angaben, nachweistabelle, zusammenfassen
from opencivil.core.protokoll import HinweisArt, HinweisBlock
from opencivil.geotechnik.grundbruch import gleitkoerper
from opencivil.projekt import GrundbruchEintrag, Projekt, ProjektFehler
from opencivil.web import dienst


def rechnen(kombinationen=(("K", 1000.0, 0.0),), **felder):
    """Ein Fundament mit gamma_phi = 1, wo nicht anders gesagt: phi_eff ist dann phi_k."""
    p = Projekt(name="Probe")
    g = p.grundbruch("F", **{"gamma_phi": 1.0, "gamma_c": 1.0, **felder})
    for name, N, T in kombinationen:
        g.kombination(name, N_Ed=N, T_Ed=T)
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return aufbau, loesung, loesung.befunde[aufbau.grundbruch["g1"].id]


def faktoren(**felder):
    return rechnen(**felder)[2].spalten


def annahmen(loesung):
    return [b.text for b in loesung.protokoll.bloecke
            if isinstance(b, HinweisBlock) and b.art is HinweisArt.ANNAHME]


class TestTabellenDesKapitels(unittest.TestCase):
    """
    Die Zahlenwerte des Kapitels -- auf die Stellen, mit denen sie dort
    stehen. Einige Tabellenwerte weichen um eine Einheit der letzten Stelle
    von ihrer eigenen Formel ab (das Buch rundet nicht einheitlich); dort ist
    die Toleranz eine Stelle weiter und die Abweichung genannt.
    """

    def test_tragfaehigkeitsfaktoren_wie_tabelle_9_2_8(self):
        tabelle = {5.0: (6.5, 1.6, 0.1), 10.0: (8.3, 2.5, 0.5), 25.0: (20.7, 10.6, 8.1),
                   27.5: (24.9, 13.9, 12.1), 30.0: (30.1, 18.4, 18.1),
                   32.5: (37.0, 24.6, 27.0), 35.0: (46.1, 33.3, 40.7),
                   37.5: (58.4, 45.8, 61.9), 40.0: (75.3, 64.2, 95.4),
                   42.5: (99.2, 91.9, 150.0), 45.0: (134.0, 135.0, 241.0)}
        for phi, erwartet in tabelle.items():
            s = faktoren(phi_k=phi)
            for wert, soll in zip((s["c"].N, s["q"].N, s["g"].N), erwartet):
                with self.subTest(phi=phi, soll=soll):
                    # N_q bei 25° ist 10.66 -- die Tabelle schneidet ab: 10.6.
                    self.assertAlmostEqual(wert, soll, delta=max(0.07, 0.005 * soll))

    def test_gleitkoerper_wie_tabelle_9_2_11(self):
        tabelle = {20.0: (2.5, 1.2), 25.0: (3.3, 1.4), 30.0: (4.3, 1.6), 35.0: (5.8, 1.9),
                   40.0: (8.0, 2.4), 45.0: (11.6, 3.0)}
        for phi, (L, H) in tabelle.items():
            befund = rechnen(phi_k=phi, b=2.0, L=2.0)[2]
            with self.subTest(phi=phi):
                self.assertAlmostEqual(befund.L_gl / 2.0, L, delta=0.051)
                # H/b ist bei 25° 1.35 und bei 40° 2.35 -- die Tabelle: 1.4, 2.4.
                self.assertAlmostEqual(befund.H_gl / 2.0, H, delta=0.06)

    def test_formfaktoren_wie_tabelle_9_2_13(self):
        # s_c je b/L und phi = 25, 30, 35, 40, 45°, dazu s_gamma je b/L.
        tabelle = {1.0: ((1.51, 1.61, 1.72, 1.85, 2.01), 0.60),
                   0.5: ((1.25, 1.31, 1.36, 1.43, 1.50), 0.80),
                   0.2: ((1.10, 1.12, 1.14, 1.17, 1.20), 0.92),
                   0.1: ((1.05, 1.06, 1.07, 1.09, 1.10), 0.96)}
        for verhaeltnis, (s_c, s_g) in tabelle.items():
            for phi, soll in zip((25.0, 30.0, 35.0, 40.0, 45.0), s_c):
                s = faktoren(phi_k=phi, b=1.0, L=1.0 / verhaeltnis)
                with self.subTest(b_L=verhaeltnis, phi=phi):
                    # Bei b/L = 1/2 und 25° ist s_c 1.257 -- die Tabelle: 1.25.
                    self.assertAlmostEqual(s["c"].s, soll, delta=0.0081)
                    self.assertAlmostEqual(s["g"].s, s_g, delta=0.0051)

    def test_tiefenfaktoren_wie_tabelle_9_2_14(self):
        # d_c je t/b, dann d_q je t/b und phi = 25, 30, 35, 40, 45°.
        tabelle = {0.4: (1.15, (1.12, 1.12, 1.10, 1.09, 1.07)),
                   0.6: (1.22, (1.17, 1.16, 1.14, 1.12, 1.09)),
                   0.8: (1.27, (1.21, 1.20, 1.17, 1.14, 1.12)),
                   1.0: (1.32, (1.24, 1.23, 1.20, 1.17, 1.14)),
                   2.0: (1.44, (1.35, 1.32, 1.28, 1.24, 1.19)),
                   4.0: (1.52, (1.41, 1.38, 1.34, 1.28, 1.23)),
                   8.0: (1.58, (1.45, 1.42, 1.37, 1.31, 1.25)),
                   15.0: (1.60, (1.47, 1.44, 1.38, 1.32, 1.26))}
        for tiefe, (d_c, d_q) in tabelle.items():
            for phi, soll in zip((25.0, 30.0, 35.0, 40.0, 45.0), d_q):
                s = faktoren(phi_k=phi, b=1.0, L=1.0, t=tiefe, t1=tiefe)
                with self.subTest(t_b=tiefe, phi=phi):
                    # Bei t/b = 4 ist d_c 1.532 -- die Tabelle: 1.52. Bei t/b =
                    # 0.4 ist d_q bei 30° 1.110 und bei 40° 1.082 -- dort 1.12, 1.09.
                    self.assertAlmostEqual(s["c"].d, d_c, delta=0.012)
                    self.assertAlmostEqual(s["q"].d, soll, delta=0.0101)
                    self.assertEqual(s["g"].d, 1.0)

    def test_lastneigung_ohne_kohaesion_wie_tabelle_9_2_16(self):
        # Je delta_R: i_q, dann i_gamma bei alpha = 0, 10, 20°.
        tabelle = {5.0: (0.80, 0.73, 0.74, 0.74), 10.0: (0.63, 0.52, 0.53, 0.54),
                   15.0: (0.49, 0.35, 0.37, 0.38), 20.0: (0.37, 0.23, 0.24, 0.26),
                   25.0: (0.27, 0.14, 0.15, 0.16), 30.0: (0.18, 0.08, 0.08, 0.09)}
        for delta, (i_q, *i_g) in tabelle.items():
            T = 1000.0 * math.tan(math.radians(delta))
            for alpha, soll in zip((0.0, 10.0, 20.0), i_g):
                befund = rechnen(phi_k=30.0, alpha=alpha, kombinationen=(("K", 1000.0, T),))[2]
                fall = befund.ergebnisse[0]
                with self.subTest(delta=delta, alpha=alpha):
                    self.assertAlmostEqual(math.degrees(fall.delta_R), delta, places=9)
                    self.assertAlmostEqual(fall.i["q"], i_q, delta=0.0051)
                    self.assertAlmostEqual(fall.i["g"], soll, delta=0.0051)

    def test_gelaendeneigung_wie_tabelle_9_2_17(self):
        tabelle = {5.0: (0.97, 0.80), 10.0: (0.93, 0.63), 15.0: (0.90, 0.49),
                   20.0: (0.86, 0.37), 25.0: (0.83, 0.27), 30.0: (0.80, 0.18)}
        for beta, (g_c, g_q) in tabelle.items():
            s = faktoren(phi_k=30.0, beta=beta)
            with self.subTest(beta=beta):
                self.assertAlmostEqual(s["c"].g, g_c, delta=0.0051)
                self.assertAlmostEqual(s["q"].g, g_q, delta=0.0051)
                self.assertEqual(s["g"].g, s["q"].g)

    def test_sohlneigung_wie_tabelle_9_2_18(self):
        # Je alpha: b_c, b_q bei phi = 25..45°, b_gamma bei phi = 25..45° --
        # b_gamma mit tan phi, wie die Tabelle es rechnet.
        tabelle = {5.0: (0.97, (0.92, 0.90, 0.88, 0.86, 0.84), (0.90, 0.87, 0.85, 0.82, 0.79)),
                   10.0: (0.93, (0.85, 0.82, 0.78, 0.75, 0.70), (0.80, 0.76, 0.72, 0.67, 0.63)),
                   15.0: (0.90, (0.78, 0.74, 0.69, 0.64, 0.59), (0.72, 0.67, 0.61, 0.55, 0.49)),
                   20.0: (0.86, (0.72, 0.67, 0.61, 0.56, 0.50), (0.65, 0.58, 0.52, 0.45, 0.39)),
                   25.0: (0.83, (0.66, 0.60, 0.54, 0.48, 0.42), (0.58, 0.51, 0.44, 0.37, 0.31))}
        for alpha, (b_c, b_q, b_g) in tabelle.items():
            for phi, q, g in zip((25.0, 30.0, 35.0, 40.0, 45.0), b_q, b_g):
                s = faktoren(phi_k=phi, alpha=alpha)
                with self.subTest(alpha=alpha, phi=phi):
                    self.assertAlmostEqual(s["c"].b, b_c, delta=0.0051)
                    self.assertAlmostEqual(s["q"].b, q, delta=0.0051)
                    self.assertAlmostEqual(s["g"].b, g, delta=0.0051)

    def test_die_tabelle_des_benutzers(self):
        """
        Seine Tabelle der Faktoren (2026-10-16): N_q = 21.10 gibt phi = 31.2°,
        s_gamma = 0.68 gibt b/L = 0.8, d_c = 1.22 und d_q = 1.16 geben t/b =
        0.62; eine Last so schräg, dass i_q und i_gamma null werden -- i_c
        bleibt dann bei -1/(N_q - 1).
        """
        befund = rechnen(phi_k=31.195, b=2.0, L=2.5, t=1.24, t1=1.24,
                         kombinationen=(("K", 100.0, 250.0),))[2]
        c, q, g = (befund.spalten[s] for s in "cqg")
        i = befund.ergebnisse[0].i
        erwartet = {
            "N": ((c.N, 33.19), (q.N, 21.10), (g.N, 21.90)),
            "s": ((c.s, 1.51), (q.s, 1.48), (g.s, 0.68)),
            "d": ((c.d, 1.22), (q.d, 1.16), (g.d, 1.00)),
            "i": ((i["c"], -0.05), (i["q"], 0.00), (i["g"], 0.00)),
            "g": ((c.g, 1.00), (q.g, 1.00), (g.g, 1.00)),
            "b'": ((c.b, 1.00), (q.b, 1.00), (g.b, 1.00)),
        }
        for zeile, paare in erwartet.items():
            for spalte, (wert, soll) in zip("cqg", paare):
                with self.subTest(zeile=zeile, spalte=spalte):
                    self.assertAlmostEqual(wert, soll, delta=0.01)


class TestGrundwasser(unittest.TestCase):
    """Bild 9.2.10: wo das Wasser steht, entscheidet über sigma_v0 und gamma_G."""

    GAMMA, GAMMA_W, Q = 21.0, 10.0, 5.0

    def bruchspannung(self, t, t1, **felder):
        """sigma_f von Hand aus dem Befund: c = 0, alpha = beta = 0, ohne T -- i = 1."""
        aufbau, loesung, befund = rechnen(phi_k=30.0, b=2.0, L=3.0, t=t, t1=t1, q_Ed=self.Q,
                                          gamma=self.GAMMA, gamma_w=self.GAMMA_W, **felder)
        return befund, befund.ergebnisse[0].sigma_f / 1e3, loesung

    def anteile(self, befund, sigma0, gamma_G):
        q, g = befund.spalten["q"], befund.spalten["g"]
        return (sigma0 * q.N * q.s * q.d * q.g * q.b
                + 0.5 * gamma_G * 2.0 * g.N * g.s * g.d * g.g * g.b)

    def test_lage_1_ueber_der_sohle(self):
        befund, sigma_f, _ = self.bruchspannung(t=1.5, t1=0.5)
        self.assertTrue(befund.grundwasser.startswith("Lage 1"))
        sigma0 = self.GAMMA * 0.5 + (self.GAMMA - self.GAMMA_W) * 1.0 + self.Q
        self.assertAlmostEqual(sigma_f, self.anteile(befund, sigma0, 11.0), places=6)

    def test_lage_2_auf_der_sohle(self):
        befund, sigma_f, _ = self.bruchspannung(t=1.0, t1=1.0)
        self.assertTrue(befund.grundwasser.startswith("Lage 2"))
        self.assertAlmostEqual(sigma_f, self.anteile(befund, 21.0 + self.Q, 11.0), places=6)

    def test_lage_3_tiefer_als_der_gleitkoerper(self):
        befund, sigma_f, _ = self.bruchspannung(t=1.0, t1=10.0)
        self.assertGreater(10.0 - 1.0, befund.H_gl)
        self.assertTrue(befund.grundwasser.startswith("Lage 3"))
        self.assertAlmostEqual(sigma_f, self.anteile(befund, 21.0 + self.Q, 21.0), places=6)

    def test_im_gleitkoerper_rechnet_wie_auf_der_sohle(self):
        befund, sigma_f, loesung = self.bruchspannung(t=1.0, t1=2.0)
        self.assertLess(2.0 - 1.0, befund.H_gl)
        self.assertEqual(befund.grundwasser, "Grundwasser im Gleitkörper, unter der Sohle")
        self.assertAlmostEqual(sigma_f, self.anteile(befund, 21.0 + self.Q, 11.0), places=6)
        self.assertTrue(any("Stabilitätsberechnung" in a for a in annahmen(loesung)))


class TestLastneigung(unittest.TestCase):
    def test_klammer_unter_null_gilt_null_und_steht_als_annahme(self):
        _, loesung, befund = rechnen(phi_k=30.0, kombinationen=(("Steil", 100.0, 300.0),))
        fall = befund.ergebnisse[0]
        self.assertEqual(fall.i["q"], 0.0)
        self.assertEqual(fall.i["g"], 0.0)
        self.assertAlmostEqual(fall.i["c"], -1.0 / (befund.spalten["q"].N - 1.0))
        self.assertTrue(any("kleiner als null" in a for a in annahmen(loesung)))

    def test_kohaesion_macht_die_last_weniger_schraeg(self):
        ohne = rechnen(phi_k=30.0, kombinationen=(("K", 500.0, 100.0),))[2].ergebnisse[0]
        mit = rechnen(phi_k=30.0, c_k=10.0, kombinationen=(("K", 500.0, 100.0),))[2].ergebnisse[0]
        nenner = 500.0 + 1.0 * 1.0 * 10.0 / math.tan(math.radians(30.0))
        self.assertAlmostEqual(mit.i["q"], (1.0 - 0.5 * 100.0 / nenner) ** 5)
        self.assertGreater(mit.i["q"], ohne.i["q"])

    def test_widerstand_und_urteil(self):
        _, loesung, befund = rechnen(phi_k=35.0, b=2.0, L=2.0, t=1.0, t1=10.0,
                                     kombinationen=(("A", 800.0, 50.0), ("B", 20000.0, 0.0)))
        a, b = befund.ergebnisse
        self.assertAlmostEqual(a.N_Rd, a.sigma_f * 4.0)
        self.assertTrue(a.erfuellt)
        self.assertAlmostEqual(a.erfuellungsgrad, a.N_Rd / 800e3)
        self.assertFalse(b.erfuellt)
        urteile = {u.fall: u for u in loesung.urteile if u.art == "GB"}
        self.assertEqual(set(urteile), {"A", "B"})
        self.assertEqual(urteile["A"].widerstand.groesse.si, a.N_Rd)
        self.assertEqual(urteile["A"].einwirkung.groesse.si, 800e3)


class TestUndrainiert(unittest.TestCase):
    """Kap. 9.2.17: phi = 0, c = s_u, die Korrekturen als Summanden."""

    def test_flach_eingebunden(self):
        s_u, b, L, t, T = 40.0, 2.0, 4.0, 1.0, 100.0
        _, _, befund = rechnen(phi_k=0.0, c_k=s_u, b=b, L=L, t=t, beta=10.0, alpha=5.0,
                               q_Ed=3.0, kombinationen=(("K", 600.0, T),))
        self.assertTrue(befund.undrainiert)
        self.assertEqual(set(befund.spalten), {"c"})
        c = befund.spalten["c"]
        self.assertEqual(c.N, 5.1)
        self.assertAlmostEqual(c.s, 0.2 * b / L)
        self.assertAlmostEqual(c.d, 0.4 * t / b)
        self.assertAlmostEqual(c.g, 10.0 / 147.0)
        self.assertAlmostEqual(c.b, 5.0 / 147.0)
        fall = befund.ergebnisse[0]
        i_c = 0.5 - 0.5 * math.sqrt(1.0 - T / (s_u * b * L))
        self.assertAlmostEqual(fall.i["c"], i_c)
        sigma_f = 5.1 * s_u * (1.0 + c.s + c.d - i_c - c.b - c.g) + 21.0 * t + 3.0
        self.assertAlmostEqual(fall.sigma_f / 1e3, sigma_f, places=6)
        self.assertAlmostEqual(fall.N_Rd / 1e3, sigma_f * b * L, places=6)

    def test_tief_eingebunden(self):
        c = rechnen(phi_k=0.0, c_k=50.0, b=1.0, L=1.0, t=2.0)[2].spalten["c"]
        self.assertAlmostEqual(c.d, 0.007 * math.degrees(math.atan(2.0)))

    def test_zu_schraeg_gibt_keinen_widerstand(self):
        _, loesung, befund = rechnen(phi_k=0.0, c_k=20.0, b=1.0, L=1.0,
                                     kombinationen=(("K", 100.0, 25.0),))
        fall = befund.ergebnisse[0]
        self.assertIsNone(fall.i["c"])
        self.assertFalse(fall.erfuellt)
        self.assertEqual(fall.N_Rd, 0.0)
        self.assertIn("kein Grundbruchwiderstand", fall.hinweis)
        urteil = next(u for u in loesung.urteile if u.art == "GB")
        self.assertFalse(urteil.erfuellt)
        self.assertEqual(urteil.hinweis, fall.hinweis)


class TestGleiten(unittest.TestCase):
    def test_reibung_mit_dem_bemessungswert(self):
        _, loesung, _ = rechnen(phi_k=30.0, gamma_phi=1.25, delta_faktor=2.0 / 3.0,
                                kombinationen=(("K", 1000.0, 150.0),))
        urteil = next(u for u in loesung.urteile if u.art == "GL")
        phi_eff = math.atan(math.tan(math.radians(30.0)) / 1.25)
        T_Rd = 1000e3 * math.tan(2.0 / 3.0 * phi_eff)
        self.assertAlmostEqual(urteil.widerstand.groesse.si, T_Rd, delta=1e-6)
        self.assertAlmostEqual(urteil.erfuellungsgrad.si, T_Rd / 150e3)
        self.assertTrue(urteil.erfuellt)

    def test_ohne_T_ist_es_unendlich_erfuellt(self):
        _, loesung, _ = rechnen(phi_k=30.0)
        urteil = next(u for u in loesung.urteile if u.art == "GL")
        self.assertTrue(urteil.erfuellt)
        self.assertEqual(urteil.erfuellungsgrad.si, math.inf)

    def test_undrainiert_ohne_reibung(self):
        _, loesung, _ = rechnen(phi_k=0.0, c_k=50.0, kombinationen=(("K", 300.0, 10.0),))
        urteil = next(u for u in loesung.urteile if u.art == "GL")
        self.assertEqual(urteil.widerstand.groesse.si, 0.0)
        self.assertFalse(urteil.erfuellt)


class TestGleitkoerper(unittest.TestCase):
    def test_umriss_trifft_L_und_H(self):
        for phi in (20.0, 30.0, 40.0):
            befund = rechnen(phi_k=phi, b=1.5, L=2.0)[2]
            zug = gleitkoerper(1.5, math.radians(phi), schritte=600)
            with self.subTest(phi=phi):
                self.assertEqual(zug[0], (-1.5, 0.0))
                self.assertAlmostEqual(zug[-1][0], befund.L_gl, places=9)
                self.assertEqual(zug[-1][1], 0.0)
                self.assertAlmostEqual(max(z for _, z in zug), befund.H_gl, places=5)


class TestEintrag(unittest.TestCase):
    def test_vorgaben_des_benutzers(self):
        g = GrundbruchEintrag.neu("g1", "Fundament 1")
        self.assertEqual(
            (g.phi_k, g.gamma_phi, g.c_k, g.gamma_c, g.gamma, g.gamma_w, g.q_Ed, g.b, g.L,
             g.t1, g.t, g.alpha, g.beta),
            (30.0, 1.2, 0.0, 1.5, 21.0, 10.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0))
        self.assertEqual([(k.name, k.N_Ed, k.T_Ed) for k in g.kombinationen],
                         [("Kombination 1", 1000.0, 200.0)])

    def test_hin_und_zurueck(self):
        p = Projekt(name="Probe")
        g = p.grundbruch("Hang", phi_k=33.0, c_k=5.0, b=1.6, L=4.0, t=0.8, t1=2.0,
                         alpha=5.0, beta=15.0, q_Ed=10.0, delta_faktor=0.67,
                         beschreibung="am Bach")
        g.kombination("A", N_Ed=900.0, T_Ed=120.0)
        g.kombination("B", N_Ed=300.0).aktiv = False
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.grundbrueche, p.grundbrueche)
        self.assertEqual(wieder.grundbrueche[0].kennung, "g1")
        self.assertEqual(p.grundbruch("Zweiter").kennung, "g2")

    def test_ohne_eingeschaltete_kombination_kein_nachweis(self):
        p = Projekt(name="Probe")
        g = p.grundbruch("F")
        g.kombination("A", N_Ed=500.0).aktiv = False
        aufbau = p.aufbauen()
        self.assertEqual(aufbau.grundbruch, {})
        self.assertEqual(aufbau.gleiten, {})
        self.assertIn("Grundbruch 'F': keine Kombination → kein Nachweis.", aufbau.warnungen)

    def test_namen_eindeutig(self):
        for namen in (("A", "A"), ("Feld A", "Feld-A")):
            g = GrundbruchEintrag.neu("g1", "F")
            g.kombinationen = []
            for name in namen:
                g.kombination(name, N_Ed=100.0)
            with self.subTest(namen=namen), self.assertRaises(ProjektFehler):
                g.pruefen()

    def test_unmoegliche_zahlen(self):
        faelle = {
            "Breite b": {"b": 0.0},
            "kürzere Seite": {"b": 2.0, "L": 1.0},
            "Raumlast": {"gamma": 10.0, "gamma_w": 10.0},
            "φ_k": {"phi_k": 90.0},
            "α": {"alpha": -1.0},
            "β": {"beta": 95.0},
            "nur die Kohäsion": {"phi_k": 0.0, "c_k": 0.0},
            "Tiefe t": {"t": -0.5},
            "δ*/φ": {"delta_faktor": 0.0},
        }
        for wort, felder in faelle.items():
            p = Projekt(name="Probe")
            p.grundbruch("F", **felder).kombination("K", N_Ed=100.0)
            with self.subTest(wort=wort):
                with self.assertRaises(ProjektFehler) as fehler:
                    p.aufbauen()
                self.assertIn(wort, str(fehler.exception))
        for N, T in ((0.0, 0.0), (100.0, -1.0)):
            p = Projekt(name="Probe")
            p.grundbruch("F").kombination("K", N_Ed=N, T_Ed=T)
            with self.subTest(N=N, T=T), self.assertRaises(ProjektFehler):
                p.aufbauen()


class TestZusammenfassung(unittest.TestCase):
    def test_faktoren_als_tabelle_und_die_nachweise(self):
        aufbau, loesung, _ = rechnen(phi_k=30.0, b=2.0, L=2.0, t=1.0, t1=10.0,
                                     kombinationen=(("A", 800.0, 50.0), ("B", 900.0, 80.0)))
        kopf, tabelle = angaben(aufbau, "g1", loesung)
        self.assertEqual(kopf.titel, "Angaben zum Fundament")
        self.assertIn(r"\varphi_{eff}", kopf.latex)
        self.assertEqual(tabelle.titel, "Tragfähigkeitsfaktoren")
        self.assertEqual(tabelle.kopf, ["Kohäsion", "", "Seitliche Auflast", "",
                                        "Gewicht Gleitkörper", ""])
        # N, s, d, je Kombination i, g, b'.
        self.assertEqual(len(tabelle.zeilen), 7)
        self.assertEqual([z[0].latex for z in tabelle.zeilen][:3], ["N_{c}", "s_{c}", "d_{c}"])
        self.assertIn("A", tabelle.zeilen[3][0].latex)
        bauteil = next(b for b in zusammenfassen(aufbau, loesung).bauteile if b.kennung == "g1")
        self.assertEqual([(z.nachweis, z.fall) for z in bauteil.zeilen],
                         [("Grundbruch", "A"), ("Grundbruch", "B"),
                          ("Gleiten", "A"), ("Gleiten", "B")])
        self.assertEqual(len(nachweistabelle(bauteil).zeilen), 4)

    def test_undrainiert_nur_die_kohaesion(self):
        aufbau, loesung, _ = rechnen(phi_k=0.0, c_k=40.0)
        _, tabelle = angaben(aufbau, "g1", loesung)
        for zeile in tabelle.zeilen:
            self.assertEqual(zeile[2:], ["–", "–", "–", "–"])

    def test_ohne_kombination_kein_gleitkoerper(self):
        p = Projekt(name="Probe")
        p.grundbruch("F")
        s = dienst.rechnen({"projekt": p.als_dict()})["grundbrueche"]["g1"]
        self.assertEqual((s["umriss"], s["faelle"], s["H_gl"], s["massgebend"]),
                         ([], [], None, None))

    def test_der_dienst_liefert_die_situation(self):
        p = Projekt(name="Probe")
        g = p.grundbruch("F", phi_k=32.0, b=2.0, L=2.5, t=1.0, t1=0.5)
        g.kombination("Leicht", N_Ed=500.0, T_Ed=20.0)
        g.kombination("Schwer", N_Ed=3000.0, T_Ed=400.0)
        antwort = dienst.rechnen({"projekt": p.als_dict()})
        s = antwort["grundbrueche"]["g1"]
        self.assertFalse(s["undrainiert"])
        self.assertTrue(s["grundwasser"].startswith("Lage 1"))
        self.assertAlmostEqual(s["umriss"][-1][0], s["L_gl"])
        self.assertEqual([f["name"] for f in s["faelle"]], ["Leicht", "Schwer"])
        self.assertAlmostEqual(s["faelle"][1]["delta_R"], math.degrees(math.atan(400 / 3000)))
        grade = {f["name"]: min(f["grad_grundbruch"], f["grad_gleiten"]) for f in s["faelle"]}
        self.assertEqual(s["massgebend"], min(grade, key=grade.get))
        zuordnung = antwort["zuordnung"]["grundbrueche"]["g1"]
        self.assertEqual(zuordnung["namensraum"], "grundbruch.g1")
        self.assertIn("phi_eff", zuordnung["werte"])
        zusammenfassung = antwort["zusammenfassungen"]["g1"]
        self.assertEqual(zusammenfassung["bewehrung"]["titel"], "Tragfähigkeitsfaktoren")


if __name__ == "__main__":
    unittest.main()
