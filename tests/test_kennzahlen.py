"""
Die Kennzahlen einer Platte (opencivil.nachweis.kennzahlen): was sie in x
aufnimmt, auch ohne Einwirkung -- Eckwerte der Handrechnung, x/d, der
Querkraftwiderstand bei N_Ed = 0 und die Vergroesserungsfaktoren.
"""

import math
import unittest

from opencivil.bericht.zusammenfassung import kennzahlen
from opencivil.nachweis import linie as geo
from opencivil.nachweis.querkraft_buegel import neigungen
from opencivil.querschnitt.fachwerk import beste_neigung
from opencivil.projekt import Projekt, RechenwahlEintrag
from opencivil.web import dienst


def rechnen(projekt):
    aufbau = projekt.aufbauen()
    return aufbau, aufbau.werk.loese(*aufbau.alle_ziele())


def wert(aufbau, loesung, kurz, kennung="q1"):
    w = loesung.werte.get(aufbau.kennzahlen[kennung].d[kurz].id)
    return None if w is None else w.groesse.si


class TestHandrechnung(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.loesung = rechnen(Projekt.beispiel())

    def test_die_eckwerte_der_tragsicherheit(self):
        """Dieselbe Linie wie die Tragsicherheit -- ihr Befund, nicht noch einmal."""
        mn = self.aufbau.feld("nachweise")["q1.x"]
        linie = self.loesung.befunde[mn.id].massgebend
        eck = linie.eckwerte()
        self.assertAlmostEqual(wert(self.aufbau, self.loesung, "M_Rd_pos"), eck["M_Rd_N0_pos"])
        self.assertAlmostEqual(wert(self.aufbau, self.loesung, "M_Rd_neg"), eck["M_Rd_N0_neg"])
        self.assertAlmostEqual(wert(self.aufbau, self.loesung, "N_Rd_druck"), eck["N_Rd_druck"])
        zug = linie.kante(geo.NORMALKRAFT, 0.0, positiv=True).wert
        self.assertAlmostEqual(wert(self.aufbau, self.loesung, "N_Rd_zug"), zug)
        self.assertFalse(self.aufbau.kennzahlen["q1"].eigene_linie)

    def test_zugwiderstand_bei_null_moment_von_hand(self):
        """Zwischen grösster Zugkraft (N_t, M_t) und M_Rd- bei N = 0 auf M = 0 interpoliert."""
        f_yd = 500e6 / 1.15
        a_u = math.pi * (18e-3 ** 2 + 12e-3 ** 2) / 4 / 0.15
        a_o = math.pi * 12e-3 ** 2 / 4 / 0.15
        z_u = (math.pi * 18e-3 ** 2 / 4 * 0.249 + math.pi * 12e-3 ** 2 / 4 * 0.246) \
            / (math.pi * (18e-3 ** 2 + 12e-3 ** 2) / 4)
        N_t = (a_u + a_o) * f_yd
        M_t = a_u * f_yd * (z_u - 0.15) + a_o * f_yd * (0.048 - 0.15)
        M_neg = wert(self.aufbau, self.loesung, "M_Rd_neg")
        erwartet = N_t + (0.0 - M_t) / (M_neg - M_t) * (0.0 - N_t)
        self.assertAlmostEqual(wert(self.aufbau, self.loesung, "N_Rd_zug"), erwartet, delta=1.0)

    def test_x_durch_d(self):
        """x = A_s f_yd / (0.85 b f_cd), d bis zum Schwerpunkt der gezogenen Lage."""
        f_yd, f_cd = 500e6 / 1.15, 20e6
        a_u = math.pi * (18e-3 ** 2 + 12e-3 ** 2) / 4 / 0.15
        z_u = (math.pi * 18e-3 ** 2 / 4 * 0.249 + math.pi * 12e-3 ** 2 / 4 * 0.246) \
            / (math.pi * (18e-3 ** 2 + 12e-3 ** 2) / 4)
        x = a_u * f_yd / (0.85 * 1.0 * f_cd)
        self.assertAlmostEqual(wert(self.aufbau, self.loesung, "x_d_pos"), x / z_u, places=9)

    def test_mit_anderer_rechenwahl_eine_eigene_handrechnung(self):
        """Präzise in der Tragsicherheit -- die Kennzahlen bleiben die der Handrechnung."""
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].tragsicherheit_wahl = RechenwahlEintrag(rechenart="parabel")
        aufbau, loesung = rechnen(projekt)
        self.assertTrue(aufbau.kennzahlen["q1"].eigene_linie)
        for kurz in ("M_Rd_pos", "M_Rd_neg", "N_Rd_zug", "N_Rd_druck", "x_d_pos", "x_d_neg"):
            with self.subTest(kurz=kurz):
                self.assertAlmostEqual(wert(aufbau, loesung, kurz),
                                       wert(self.aufbau, self.loesung, kurz), places=6)
        titel = [getattr(b, "text", "") for b in loesung.protokoll.alle_bloecke()]
        self.assertTrue(any(t.startswith("Kennzahlen: Resistenzlinie") for t in titel))


class TestQuerkraft(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.loesung = rechnen(Projekt.beispiel())

    def test_ohne_buegel_das_kleinere_beider_seiten(self):
        """M = 0: tau_cd d_v; M = M_Rd: k_d = 1/(1 + f_yd/E_s · d · k_g)."""
        tau = self.loesung.werte["beton.b1.tau_cd"].groesse.si
        k_g, eps = 1.2, (500 / 1.15) / 200000
        d_u, d_o = 0.249, 0.300 - 0.048
        null = [tau * d for d in (d_u, d_o)]
        voll = [tau * d / (1.0 + eps * d * 1e3 * k_g) for d in (d_u, d_o)]
        self.assertAlmostEqual(wert(self.aufbau, self.loesung, "V_Rd_max"), min(null), places=6)
        self.assertAlmostEqual(wert(self.aufbau, self.loesung, "V_Rd_min"), min(voll), places=6)
        self.assertNotIn("V_Rd_buegel", self.aufbau.kennzahlen["q1"].d)

    def test_mit_buegeln_bei_der_guenstigsten_neigung(self):
        projekt = Projekt.beispiel()
        b = projekt.querschnitte[0].querkraftbewehrung
        b.durchmesser, b.abstand_x, b.abstand_y = 10.0, 200.0, 200.0
        aufbau, loesung = rechnen(projekt)
        kz = aufbau.kennzahlen["q1"]
        self.assertNotIn("V_Rd_max", kz.d)
        f_yd = loesung.werte["betonstahl.s1.f_yd"].groesse.si
        f_cd = loesung.werte["beton.b1.f_cd"].groesse.si
        a_s = math.pi * 0.010 ** 2 / 4
        erwartet = min(
            beste_neigung(neigungen(alpha_min=b.alpha_min, alpha_max=b.alpha_max,
                                    a_s=a_s, s_x=0.2, s_y=0.2,
                                    d=d, f_yd=f_yd, f_cd=f_cd, k_c=0.55)).V_Rd
            for d in (0.249, 0.252))
        self.assertAlmostEqual(wert(aufbau, loesung, "V_Rd_buegel"), erwartet, places=6)


class TestImmer(unittest.TestCase):
    def test_auch_ohne_einwirkung(self):
        projekt = Projekt.beispiel()
        platte = projekt.querschnitte[0]
        platte.kombinationen = []
        platte.verformung.faelle = []
        antwort = dienst.rechnen({"projekt": projekt.als_dict()})
        namen = [k["beschriftung"] for k in antwort["kennzahlen"]["q1"]]
        self.assertEqual(namen, [
            "Bewehrungsmass", "Höhe der Distanzhalter",
            "Vergrösserungsfaktor, Zug unten", "Vergrösserungsfaktor, Zug oben",
            "Momentenwiderstand, Zug unten", "Momentenwiderstand, Zug oben",
            "Zugwiderstand", "Druckwiderstand",
            "Bezogene Druckzonenhöhe, Zug unten", "Bezogene Druckzonenhöhe, Zug oben",
            "Querkraftwiderstand ohne Bügel, grösster",
            "Querkraftwiderstand ohne Bügel, kleinster"])
        faktor = next(k for k in antwort["kennzahlen"]["q1"] if k["symbol"] == r"\omega_w")
        self.assertEqual(faktor["text"], "4.00")

    def test_ohne_x_bewehrung_nur_was_es_gibt(self):
        projekt = Projekt(name="Probe")
        projekt.beton("C30/37")
        projekt.stahl("B500B")
        projekt.platte("Ohne x", h=250, x=[0, 0], y=[12, 12])
        aufbau, loesung = rechnen(projekt)
        self.assertEqual([k.beschriftung for k, _ in kennzahlen(aufbau, "q1", loesung)],
                         ["Bewehrungsmass", "Höhe der Distanzhalter"])

    def test_im_bericht(self):
        projekt = Projekt.beispiel()
        text = projekt.rechnen().bericht()
        teil = text[text.index("Decke über EG\n-"):]
        self.assertIn("Kennzahlen", teil)
        self.assertIn("Querkraftwiderstand ohne Bügel, kleinster", teil)


class TestEinseitigBewehrt(unittest.TestCase):
    """
    Nur eine Seite bewehrt: die Linie liegt ganz bei M >= 0 oder M <= 0 und
    berührt M = 0 nur, entlang der Kante vom reinen Druck bis N = 0. Bis
    2026-10-18 fand die Schnittsuche dort nichts, und nur oben bewehrt stand
    als Druckwiderstand 0 statt -5000 kN.
    """

    def test_der_druckwiderstand_auf_beiden_seiten_gleich(self):
        for x in ([12, 0], [0, 12]):
            with self.subTest(x=x):
                projekt = Projekt(name="Probe")
                projekt.beton("C30/37")
                projekt.stahl("B500B")
                projekt.platte("Probe", h=250, x=x, y=[10, 10])
                aufbau, loesung = rechnen(projekt)
                self.assertAlmostEqual(wert(aufbau, loesung, "N_Rd_druck"), -5.0e6, delta=1.0)

    def test_nur_unten_bewehrt_fehlt_was_oben_waere(self):
        """
        Ohne obere x-Lage gibt es für Zug oben weder x/d noch omega_w' -- sie
        fehlen, statt 0 zu zeigen. M_Rd- ist dagegen wirklich null: ohne obere
        Bewehrung trägt die Platte kein negatives Moment.
        """
        projekt = Projekt(name="Probe")
        projekt.beton("C30/37")
        projekt.stahl("B500B")
        projekt.platte("Probe", h=250, x=[12, 0], y=[10, 10])
        aufbau, loesung = rechnen(projekt)
        self.assertEqual([k.beschriftung for k, _ in kennzahlen(aufbau, "q1", loesung)], [
            "Bewehrungsmass", "Höhe der Distanzhalter", "Vergrösserungsfaktor, Zug unten",
            "Momentenwiderstand, Zug unten", "Momentenwiderstand, Zug oben",
            "Zugwiderstand", "Druckwiderstand", "Bezogene Druckzonenhöhe, Zug unten",
            "Querkraftwiderstand ohne Bügel, grösster",
            "Querkraftwiderstand ohne Bügel, kleinster"])
        self.assertEqual(wert(aufbau, loesung, "M_Rd_neg"), 0.0)
        self.assertGreater(wert(aufbau, loesung, "x_d_pos"), 0.0)
        texte = [getattr(b, "text", "") for b in loesung.protokoll.alle_bloecke()]
        self.assertIn("Zug oben ohne x-Bewehrung → kein d, kein x/d dieser Seite.", texte)

    def test_die_kante_findet_den_beruehrten_eckpunkt(self):
        linie = [geo.Stelle(N=-5000.0, M=0.0), geo.Stelle(N=0.0, M=0.0),
                 geo.Stelle(N=300.0, M=-25.0), geo.Stelle(N=0.0, M=-64.0)]
        self.assertEqual(geo.kante(linie, geo.NORMALKRAFT, 0.0, positiv=False)[0], -5000.0)
        self.assertEqual(geo.kante(linie, geo.NORMALKRAFT, 0.0, positiv=True)[0], 0.0)


if __name__ == "__main__":
    unittest.main()
