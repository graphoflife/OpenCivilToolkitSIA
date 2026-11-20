"""
Die Querschnitte der Stäbe: jede Vorlage gegen das Integral über ihren Umriss.

Die Formeln stehen von Hand da (damit die Herleitung sie zeigen kann); das
Polygon-Integral der Querschnittsanalyse rechnet dieselben Werte auf einem
anderen Weg nach. Kreis und Kreisring gegen die geschlossene Form -- ihr
Umriss ist ein Vieleck. Die Torsion gegen die Tafel des Rechtecks
(Timoshenko) und gegen die Teile, aus denen sie rechnet.
"""

import math
import unittest

from opencivil.core.einheiten import MIO_MM4, MM, MM2, Groesse
from opencivil.querschnitt import vorlagen
from opencivil.querschnitt.geometrie import flaechenwerte, summe
from opencivil.stabwerk.stabquerschnitt import RAEUMLICH
from opencivil.web import systemkatalog
from opencivil.stabwerk.querschnitte import (
    DOPPEL_T, KREIS, KREISRING, RECHTECK, RECHTECKROHR, T_QUERSCHNITT, TRAPEZ, VORLAGEN,
    rechtecktorsion, vorlage,
)


class TestGegenDasIntegral(unittest.TestCase):
    def test_jede_vorlage_mit_ihren_vorgaben(self):
        for v in VORLAGEN:
            if v in (KREIS, KREISRING):
                continue
            with self.subTest(vorlage=v.name):
                masse = v.vorgaben()
                umrisse = v.umriss(masse)
                w = summe([(1.0 if i == 0 else -1.0, flaechenwerte(u))
                           for i, u in enumerate(umrisse)])
                k = v.kennwerte(masse)
                self.assertAlmostEqual(k["A"].in_einheit(MM2), w.A, delta=1e-9 * w.A)
                self.assertAlmostEqual(k["I_y"].in_einheit(MIO_MM4) * 1e6, w.I_y, delta=1e-9 * w.I_y)
                self.assertAlmostEqual(k["I_z"].in_einheit(MIO_MM4) * 1e6, w.I_z, delta=1e-9 * w.I_z)

    def test_t_mit_schwerpunkt(self):
        """Der Schwerpunkt vom oberen Rand: h − z_S des Integrals (dort von unten)."""
        masse = vorlage("t").vorgaben()
        w = flaechenwerte(vorlage("t").umriss(masse)[0])
        z_S = vorlage("t").kennwerte(masse)["z_S"].si * 1000.0
        self.assertAlmostEqual(z_S, masse["h"] - w.z_S, places=6)

    def test_kreis_und_kreisring(self):
        k = KREIS.kennwerte({"d": 400.0})
        self.assertAlmostEqual(k["A"].in_einheit(MM2), math.pi * 400 ** 2 / 4)
        r = KREISRING.kennwerte({"D": 300.0, "t": 20.0})
        self.assertAlmostEqual(r["I_y"].in_einheit(MIO_MM4) * 1e6,
                               math.pi * (300 ** 4 - 260 ** 4) / 64, places=3)

    def test_kreis_und_kreisring_ohne_starke_achse(self):
        """Um jede Achse dasselbe -- und polar, als Torsion, das Doppelte."""
        for k, d4 in ((KREIS.kennwerte({"d": 400.0}), 400.0 ** 4),
                      (KREISRING.kennwerte({"D": 300.0, "t": 20.0}), 300.0 ** 4 - 260.0 ** 4)):
            self.assertAlmostEqual(k["I_z"].si, k["I_y"].si)
            self.assertAlmostEqual(k["I_T"].in_einheit(MIO_MM4) * 1e6, math.pi * d4 / 32,
                                   places=2)


def _torsion(v, **masse):
    return v.kennwerte(masse)["I_T"].in_einheit(MIO_MM4) * 1e6


class TestTorsion(unittest.TestCase):
    def test_rechteck_wie_die_tafel(self):
        """I_T = β · s · t³ mit β nach Timoshenko -- Roark trifft es auf ein Prozent."""
        for verhaeltnis, beta in ((1.0, 0.1406), (1.5, 0.196), (2.0, 0.229), (3.0, 0.263),
                                  (5.0, 0.291), (10.0, 0.312)):
            with self.subTest(s_durch_t=verhaeltnis):
                t = 100.0
                s = verhaeltnis * t
                self.assertAlmostEqual(_torsion(RECHTECK, b=t, h=s) / (beta * s * t ** 3), 1.0,
                                       delta=0.01)

    def test_rechteck_liegend_wie_stehend(self):
        self.assertAlmostEqual(_torsion(RECHTECK, b=300.0, h=600.0),
                               _torsion(RECHTECK, b=600.0, h=300.0))

    def test_t_und_doppel_t_aus_ihren_rechtecken(self):
        mm = lambda wert: Groesse(wert, MM)
        teile = lambda *paare: sum(rechtecktorsion(mm(min(a, b)), mm(max(a, b))).si * n
                                   for n, a, b in paare) * 1e12
        self.assertAlmostEqual(_torsion(T_QUERSCHNITT, b=1000.0, h=600.0, b_w=300.0, h_f=200.0),
                               teile((1, 1000.0, 200.0), (1, 300.0, 400.0)), delta=1.0)
        self.assertAlmostEqual(_torsion(DOPPEL_T, b=200.0, h=400.0, t_f=16.0, t_w=9.0),
                               teile((2, 200.0, 16.0), (1, 9.0, 368.0)), delta=1.0)

    def test_trapez_mit_gleichen_breiten_ist_ein_rechteck(self):
        self.assertAlmostEqual(_torsion(TRAPEZ, b_o=300.0, b_u=300.0, h=500.0),
                               _torsion(RECHTECK, b=300.0, h=500.0))

    def test_duennes_rohr_nach_bredt(self):
        """Mit duenner Wand bleibt fast nur der geschlossene Teil: 4 · A_m² · t / p_m."""
        b, h, t = 400.0, 600.0, 2.0
        A_m, p_m = (b - t) * (h - t), 2 * (b + h - 2 * t)
        self.assertAlmostEqual(_torsion(RECHTECKROHR, b=b, h=h, t=t) / (4 * A_m ** 2 * t / p_m),
                               1.0, delta=1e-4)


class TestPruefen(unittest.TestCase):
    def test_unmoegliche_masse(self):
        for schluessel, masse, wort in (
                ("kreisring", {"D": 100.0, "t": 60.0}, "zu dick"),
                ("rechteckrohr", {"b": 100.0, "h": 200.0, "t": 50.0}, "zu dick"),
                ("t", {"b": 200.0, "h": 600.0, "b_w": 300.0, "h_f": 100.0}, "schmaler"),
                # Ein Steg so breit wie der Flansch: dafuer gibt es das Rechteck --
                # dieselbe Regel wie in der Querschnittsanalyse.
                ("t", {"b": 300.0, "h": 600.0, "b_w": 300.0, "h_f": 100.0}, "schmaler"),
                ("doppel_t", {"b": 200.0, "h": 30.0, "t_f": 16.0, "t_w": 9.0}, "dicker"),
                ("rechteck", {"b": 0.0, "h": 600.0}, "grösser als null")):
            with self.subTest(vorlage=schluessel):
                self.assertIn(wort, vorlage(schluessel).pruefen(masse))

    def test_ein_mass_wie_ein_feld(self):
        """
        Die Masse beider Arten von Vorlagen und die Kennwerte von Hand sagen
        ihre Grenze wie ein Feld: mit seinem Satz, und der Maske mit seiner
        Angabe. Bis 2026-11-20 hatten Stab und Analyse je eine eigene Klasse
        Mass, einen eigenen Satz und im Fenster einen eigenen Mindestwert.
        """
        satz = "Breite b muss grösser als null sein, angegeben ist 0 mm."
        self.assertEqual(RECHTECK.pruefen({"b": 0.0, "h": 600.0}), satz)
        with self.assertRaisesRegex(ValueError, f"^{satz}$"):
            vorlagen.vorlage("rechteck").bauen({"b": 0.0})
        angabe = {"einheit": "mm", "ueber": 0.0, "heisst": "Breite b",
                  "verlangt": "muss grösser als null sein"}
        self.assertEqual(RECHTECK.masse[0].als_dict()["angabe"], angabe)
        self.assertEqual(vorlagen.vorlage("rechteck").masse[0].als_dict()["angabe"], angabe)
        self.assertEqual(RAEUMLICH[0].bereich.angabe(),
                         {"einheit": "mm²", "ueber": 0.0, "heisst": "Querschnittsfläche A",
                          "verlangt": "muss grösser als null sein"})
        from opencivil.projekt.balkensystem3d import Balkensystem3dEintrag
        from opencivil.stabwerk3d.rechnung import Balkensystem3d
        from opencivil.web import balkendaten
        katalog = systemkatalog.katalog(Balkensystem3dEintrag, Balkensystem3d, balkendaten.RAUM)
        self.assertEqual([k["angabe"]["einheit"] for k in katalog["kennwerte"]],
                         ["mm²", "·10⁶ mm⁴", "·10⁶ mm⁴", "·10⁶ mm⁴"])

    def test_die_vorgaben_gehen(self):
        for v in VORLAGEN:
            self.assertIsNone(v.pruefen(v.vorgaben()), v.name)

    def test_unbekannte_vorlage(self):
        with self.assertRaises(KeyError):
            vorlage("ellipse")


if __name__ == "__main__":
    unittest.main()
