"""
Schubwände: wie Querkraft und Torsion sich verteilen, was eine Wand trägt.

Die Fälle sind die aus dem Plan: zwei gleiche Stege, ein Kasten unter
Torsion, zwei Zellen mit und ohne gemeinsame Wand, eine offene C-Form. Jeder
Fall lässt sich von Hand nachrechnen, und für jeden gilt: die Wandkräfte
ergeben V_y, V_z und um den Schwerpunkt T.
"""

import math
import unittest

from opencivil.querschnitt import schubwaende as sw
from opencivil.querschnitt.schubwaende import Wand, WandFehler


def wand(name, von, bis, b_w=0.2, a_sw_s=1.0e-3):
    return Wand(name=name, von=von, bis=bis, b_w=b_w, a_sw_s=a_sw_s,
                f_sd=435e6, f_cd=20e6, k_c=0.55)


def kasten(y0, z0, b, h, b_w=0.2, praefix="K"):
    """Vier Wände um ein Rechteck, im Gegenuhrzeigersinn gezeichnet."""
    ecken = [(y0, z0), (y0 + b, z0), (y0 + b, z0 + h), (y0, z0 + h)]
    return [wand(f"{praefix}{i + 1}", ecken[i], ecken[(i + 1) % 4], b_w) for i in range(4)]


def summen(waende, modell, verteilung, bezug):
    """Kraft in y, in z und Moment um den Bezugspunkt -- aus den Stücken."""
    F_y = F_z = M = 0.0
    for s, q in zip(modell.stuecke, verteilung.fluss):
        e = waende[s.wand].richtung
        kraft = q * s.laenge
        F_y += kraft * e[0]
        F_z += kraft * e[1]
        m = s.mitte
        M += kraft * ((m[0] - bezug[0]) * e[1] - (m[1] - bezug[1]) * e[0])
    return F_y, F_z, M


class TestZellen(unittest.TestCase):

    def test_ein_kasten_eine_zelle(self):
        modell = sw.zellen(kasten(0, 0, 0.3, 0.6))
        self.assertEqual(len(modell.zellen), 1)
        self.assertAlmostEqual(modell.zellen[0].flaeche, 0.18)

    def test_mittelwand_teilt_in_zwei(self):
        waende = kasten(0, 0, 1.0, 0.5) + [wand("M", (0.5, 0.0), (0.5, 0.5))]
        modell = sw.zellen(waende)
        self.assertEqual(sorted(round(z.flaeche, 9) for z in modell.zellen), [0.25, 0.25])

    def test_freie_wand_ist_keine_zelle(self):
        waende = kasten(0, 0, 0.3, 0.6) + [wand("Kragarm", (0.3, 0.6), (0.8, 0.6))]
        modell = sw.zellen(waende)
        self.assertEqual(len(modell.zellen), 1)

    def test_einzelner_steg_ohne_zelle(self):
        self.assertEqual(sw.zellen([wand("Steg", (0, 0), (0, 0.5))]).zellen, ())


class TestVerteilung(unittest.TestCase):

    def test_zwei_stege_je_die_haelfte(self):
        waende = kasten(0, 0, 1.0, 0.5)
        modell = sw.zellen(waende)
        v = sw.verteilen(waende, modell, V_y=0.0, V_z=600e3, T=0.0, bezug=(0.5, 0.25))
        stege = [abs(v.aus_querkraft[i]) for i in (1, 3)]  # rechts und links
        self.assertAlmostEqual(stege[0], 300e3, delta=1e-3)
        self.assertAlmostEqual(stege[1], 300e3, delta=1e-3)
        self.assertAlmostEqual(v.aus_querkraft[0], 0.0, delta=1e-3)
        for q in v.zellenfluss:
            self.assertAlmostEqual(q, 0.0, delta=1e-3)

    def test_kasten_unter_torsion_konstanter_fluss(self):
        waende = kasten(0, 0, 0.3, 0.6)
        modell = sw.zellen(waende)
        T = 50e3
        v = sw.verteilen(waende, modell, V_y=0.0, V_z=0.0, T=T, bezug=(0.15, 0.3))
        for q in v.fluss:
            self.assertAlmostEqual(abs(q), T / (2 * 0.18), delta=1e-6)

    def test_zwei_zellen_mittelwand_traegt_nichts(self):
        waende = kasten(0, 0, 1.0, 0.5) + [wand("M", (0.5, 0.0), (0.5, 0.5))]
        modell = sw.zellen(waende)
        T = 80e3
        v = sw.verteilen(waende, modell, V_y=0.0, V_z=0.0, T=T, bezug=(0.5, 0.25))
        for s, q in zip(modell.stuecke, v.fluss):
            if waende[s.wand].name == "M":
                self.assertAlmostEqual(q, 0.0, delta=1e-6)
            else:
                self.assertAlmostEqual(abs(q), T / (2 * 0.5), delta=1e-6)

    def test_getrennte_zellen_nach_steifigkeit(self):
        """Zwei gleiche Kästen nebeneinander, ohne gemeinsame Wand: je die Hälfte."""
        waende = kasten(0, 0, 0.4, 0.4, praefix="A") + kasten(1.0, 0, 0.4, 0.4, praefix="B")
        modell = sw.zellen(waende)
        T = 40e3
        v = sw.verteilen(waende, modell, V_y=0.0, V_z=0.0, T=T, bezug=(0.7, 0.2))
        for q in v.zellenfluss:
            self.assertAlmostEqual(q, (T / 2) / (2 * 0.16), delta=1e-6)

    def test_c_form_versatz(self):
        """Offen: der Steg trägt V_z, die Flansche bilden das Gegenpaar zum Versatz."""
        waende = [wand("oben", (0.4, 0.6), (0.0, 0.6)), wand("Steg", (0.0, 0.6), (0.0, 0.0)),
                  wand("unten", (0.0, 0.0), (0.4, 0.0))]
        modell = sw.zellen(waende)
        bezug = (0.1, 0.3)
        v = sw.verteilen(waende, modell, V_y=0.0, V_z=200e3, T=0.0, bezug=bezug)
        self.assertTrue(v.mit_drehung)
        F_y, F_z, M = summen(waende, modell, v, bezug)
        self.assertAlmostEqual(F_y, 0.0, delta=1e-3)
        self.assertAlmostEqual(F_z, 200e3, delta=1e-3)
        self.assertAlmostEqual(M, 0.0, delta=1e-3)
        self.assertGreater(abs(v.aus_querkraft[0]), 1e3)  # die Flansche arbeiten

    def test_gleichgewicht_immer(self):
        """Ein Kasten mit Kragarm, schief belastet: die Summen stimmen."""
        waende = kasten(0, 0, 0.8, 0.5) + [wand("Kragarm", (0.8, 0.5), (1.4, 0.5), b_w=0.15)]
        modell = sw.zellen(waende)
        bezug = (0.55, 0.3)
        v = sw.verteilen(waende, modell, V_y=120e3, V_z=-350e3, T=70e3, bezug=bezug)
        F_y, F_z, M = summen(waende, modell, v, bezug)
        self.assertAlmostEqual(F_y, 120e3, delta=1e-2)
        self.assertAlmostEqual(F_z, -350e3, delta=1e-2)
        self.assertAlmostEqual(M, 70e3, delta=1e-2)

    def test_eine_wand_traegt_keine_torsion(self):
        waende = [wand("Steg", (0.0, 0.0), (0.0, 0.5))]
        with self.assertRaisesRegex(WandFehler, "Torsion"):
            sw.verteilen(waende, sw.zellen(waende), V_y=0.0, V_z=100e3, T=10e3,
                         bezug=(0.0, 0.25))

    def test_parallele_waende_tragen_nicht_quer(self):
        waende = [wand("links", (0.0, 0.0), (0.0, 0.5)), wand("rechts", (0.5, 0.0), (0.5, 0.5))]
        with self.assertRaisesRegex(WandFehler, "quer"):
            sw.verteilen(waende, sw.zellen(waende), V_y=50e3, V_z=0.0, T=0.0,
                         bezug=(0.25, 0.25))

    def test_parallele_waende_tragen_laengs(self):
        waende = [wand("links", (0.0, 0.0), (0.0, 0.5)), wand("rechts", (0.5, 0.0), (0.5, 0.5))]
        v = sw.verteilen(waende, sw.zellen(waende), V_y=0.0, V_z=100e3, T=0.0,
                         bezug=(0.25, 0.25))
        self.assertAlmostEqual(v.aus_querkraft[0], 50e3, delta=1e-3)


class TestWiderstand(unittest.TestCase):

    def test_fachwerk_je_laenge(self):
        w = wand("Steg", (0, 0), (0, 0.5), b_w=0.2, a_sw_s=1.0e-3)
        r = sw.widerstand(w, alpha_min=30, alpha_max=45, zugkraft=False)
        a = math.radians(r.alpha)
        self.assertAlmostEqual(r.v_Rd_s, 1.0e-3 * 435e6 / math.tan(a))
        self.assertAlmostEqual(r.v_Rd_c, 0.2 * 0.55 * 20e6 * math.sin(a) * math.cos(a))
        self.assertTrue(30 <= r.alpha <= 45)

    def test_zug_hebt_die_neigung(self):
        w = wand("Steg", (0, 0), (0, 0.5))
        self.assertGreaterEqual(sw.widerstand(w, alpha_min=25, alpha_max=45,
                                              zugkraft=True).alpha, 40)


class TestLaengszug(unittest.TestCase):

    def test_mittiger_steg_nur_normalkraft(self):
        waende = [wand("Steg", (0.15, 0.05), (0.15, 0.55))]
        modell = sw.zellen(waende)
        v = sw.verteilen(waende, modell, V_y=0.0, V_z=300e3, T=0.0, bezug=(0.15, 0.3))
        z = sw.laengszug(modell, v, [45], (0.15, 0.3))
        self.assertAlmostEqual(z.N, 300e3, delta=1e-3)
        self.assertAlmostEqual(z.M_y, 0.0, delta=1e-3)

    def test_t_balken_steg_unter_dem_schwerpunkt(self):
        waende = [wand("Steg", (0.15, 0.05), (0.15, 0.55))]
        modell = sw.zellen(waende)
        v = sw.verteilen(waende, modell, V_y=0.0, V_z=300e3, T=0.0, bezug=(0.15, 0.45))
        z = sw.laengszug(modell, v, [45], (0.15, 0.45))
        self.assertGreater(z.M_y, 0.0)  # Zug unten
        self.assertAlmostEqual(z.M_y, 300e3 * (0.45 - 0.30), delta=1e-3)

    def test_kasten_unter_torsion(self):
        waende = kasten(0, 0, 0.3, 0.6)
        modell = sw.zellen(waende)
        T = 50e3
        v = sw.verteilen(waende, modell, V_y=0.0, V_z=0.0, T=T, bezug=(0.15, 0.3))
        z = sw.laengszug(modell, v, [30] * 4, (0.15, 0.3))
        u_k = 2 * (0.3 + 0.6)
        self.assertAlmostEqual(z.N, T * u_k / math.tan(math.radians(30)) / (2 * 0.18),
                               delta=1e-3)


if __name__ == "__main__":
    unittest.main()
