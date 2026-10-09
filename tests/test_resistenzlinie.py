"""
Die genaue Resistenzlinie der Platte -- gesucht auf dem Fächer, nicht auf der Sehne.

Was sie verspricht, steht hier als Prüfung: ihr Widerstand ist ein echter
Bruchzustand (die Probe geht auf), er hängt nicht an der Schrittweite der
Zeichnung, das Urteil passt zum Grad, und der Block der Platte ist derselbe
wie der Block der Querschnittsanalyse.
"""

import math
import unittest

from opencivil.core.protokoll import Protokoll
from opencivil.nachweis import linie as geo
from opencivil.nachweis.rechenwahl import Rechenart, Rechenwahl, betongesetz
from opencivil.nachweis.resistenzlinie import Ebenenlinie
from opencivil.querschnitt.interaktion import Bewehrung, Querschnitt, Teil, Werkstoff
from opencivil.querschnitt.werkstoffgesetz import Spannungsblock, Stahlgesetz

H, B = 0.25, 1.0
F_C, E_CM = 20e6, 32000e6
EPS_C1D, EPS_C2D = 0.002, 0.0035
STAHL = Stahlgesetz(E_s=205e9, f_yd=435e6, f_yd_druck=435e6, eps_ud=0.045)
LAGEN = [(1131e-6, 0.215, STAHL, "1. Lage unten"), (565e-6, 0.035, STAHL, "3. Lage oben")]


def ebenenlinie(art=Rechenart.PARABEL, *, schritte=80, phi=0.0):
    wahl = Rechenwahl(kriechzahl=phi, art=art)
    return Ebenenlinie(
        wahl, h=H, b=B, lagen=LAGEN, eps_c1d=EPS_C1D, eps_c2d=EPS_C2D, schritte=schritte,
        beton=betongesetz(wahl, f_c=F_C, E_cm=E_CM, eps_c1d=EPS_C1D, eps_c2d=EPS_C2D))


class TestGenau(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parabel = ebenenlinie()
        cls.block = ebenenlinie(Rechenart.BLOCK)

    def test_die_probe_geht_auf(self):
        """Die gefundene Ebene trägt genau die Normalkraft, bei der gesucht wurde."""
        for linie in (self.parabel, self.block):
            for N in (-2500e3, -800e3, 0.0, 250e3):
                for positiv in (True, False):
                    t = linie.kante(geo.MOMENT, N, positiv)
                    N_ist, M_ist = linie.kraefte(t.eps_oben, t.eps_unten)
                    self.assertAlmostEqual(N_ist, N, delta=1e-3)
                    self.assertEqual(M_ist, t.wert)

    def test_haengt_nicht_an_der_schrittweite(self):
        """Mit 20 oder 160 Schritten gezeichnet -- derselbe Widerstand."""
        grob, fein = ebenenlinie(schritte=20), ebenenlinie(schritte=160)
        for N in (-2000e3, -500e3, 0.0, 300e3):
            for positiv in (True, False):
                a = grob.moment_bei(N, positiv)
                b = fein.moment_bei(N, positiv)
                self.assertAlmostEqual(a / b, 1.0, delta=1e-9, msg=f"N = {N}")

    def test_urteil_und_grad_passen_zusammen(self):
        """Knapp darunter drin, knapp darüber draussen -- an demselben Rand."""
        for linie in (self.parabel, self.block):
            for N in (-1500e3, 0.0):
                for vz in (1.0, -1.0):
                    M_R = vz * linie.moment_bei(N, vz > 0)
                    self.assertTrue(linie.innerhalb(N, 0.999 * M_R))
                    self.assertFalse(linie.innerhalb(N, 1.001 * M_R))

    def test_reiner_druck_ist_nicht_die_spitze(self):
        """
        Gleichmässig -eps_c1d: Beton bei f_c, Stahl elastisch (410 N/mm²),
        netto. Kippt die Ebene um C, fliesst der obere Stahl -- die grösste
        Druckkraft liegt darum etwas daneben, und sie wird dort gesucht.
        """
        sigma_s = min(STAHL.E_s * EPS_C1D, STAHL.f_yd_druck)
        a_s = sum(l[0] for l in LAGEN)
        gleichmaessig = -B * H * F_C - a_s * (sigma_s - F_C)
        for art in (Rechenart.PARABEL, Rechenart.BLOCK):
            fein = ebenenlinie(art).eckwerte()["N_Rd_druck"]
            grob = ebenenlinie(art, schritte=20).eckwerte()["N_Rd_druck"]
            self.assertLess(fein, gleichmaessig)
            self.assertLess(fein / gleichmaessig, 1.01)
            self.assertAlmostEqual(grob / fein, 1.0, delta=1e-9)

    def test_reiner_zug_von_hand(self):
        erwartet = sum(l[0] for l in LAGEN) * STAHL.f_yd
        self.assertAlmostEqual(self.parabel.eckwerte()["N_Rd_zug"] / erwartet, 1.0, delta=1e-12)

    def test_groesstes_moment_zwischen_den_ebenen(self):
        """Gesucht, nicht abgelesen: nie kleiner als der grösste Punkt, und fein wie grob."""
        for positiv, schluessel in ((True, "M_Rd_max"), (False, "M_Rd_min")):
            vz = 1.0 if positiv else -1.0
            genau = self.parabel.eckwerte()[schluessel]
            self.assertGreaterEqual(vz * genau, max(vz * p.M for p in self.parabel.punkte))
            grob = ebenenlinie(schritte=20).eckwerte()[schluessel]
            self.assertAlmostEqual(grob / genau, 1.0, delta=1e-7)

    def test_bei_null_wie_die_kante(self):
        e = self.parabel.eckwerte()
        self.assertEqual(e["M_Rd_N0_pos"], self.parabel.moment_bei(0.0, True))
        self.assertEqual(e["M_Rd_N0_neg"], -self.parabel.moment_bei(0.0, False))

    def test_massgebende_grenze(self):
        """Biegung ohne Normalkraft: der Stahl fliesst bis eps_ud, oder der Beton bricht."""
        t = self.parabel.kante(geo.MOMENT, 0.0, True)
        erreicht = self.parabel.erreicht(t.eps_oben, t.eps_unten)
        self.assertTrue(erreicht)
        self.assertTrue(set(erreicht) <= {"Stahl der 1. Lage unten", "Beton am oberen Rand"})
        # Reiner Druck: alles im Punkt C.
        druck = min(self.parabel.punkte, key=lambda p: p.N)
        self.assertIn("Beton im Punkt C", self.parabel.erreicht(druck.eps_oben, druck.eps_unten))

    def test_herleitung_zeigt_die_probe(self):
        p = Protokoll()
        t = self.parabel.kante(geo.MOMENT, -500e3, True)
        self.parabel.protokoll_treffer(p, t, achse=geo.MOMENT, fest=-500e3, basis="t")
        text = repr(p.bloecke)
        self.assertIn("Probe", text)
        self.assertIn("Beton, Resultierende", text)
        self.assertIn("Massgebend", text)

    def test_mit_hand_nicht_zu_haben(self):
        with self.assertRaises(ValueError):
            ebenenlinie(Rechenart.HANDRECHNUNG)


class TestBlockWieDieQuerschnittsanalyse(unittest.TestCase):
    """Der Block der Platte ist derselbe wie der des gezeichneten Querschnitts."""

    def test_momente(self):
        block = Spannungsblock(f_cd=F_C, eps_c2d=EPS_C2D)
        qa = Querschnitt(
            werkstoffe=[Werkstoff("Beton", block, -EPS_C2D, math.inf,
                                  c_punkt=(EPS_C1D, EPS_C2D), verdraengbar=True),
                        Werkstoff("Stahl", STAHL.spannung, -STAHL.eps_ud, STAHL.eps_ud)],
            teile=[Teil(((0, 0), (B, 0), (B, H), (0, H)), 0, None)],
            bewehrung=[Bewehrung((0.5, H - 0.215), 1131e-6, 1, 0),
                       Bewehrung((0.5, H - 0.035), 565e-6, 1, 0)],
            bezug=(B / 2, H / 2))
        platte = ebenenlinie(Rechenart.BLOCK)
        for N in (-1500e3, -300e3, 0.0, 200e3):
            unten = qa.bei_normalkraft(-math.pi / 2, N)
            self.assertAlmostEqual(unten.M_y / platte.moment_bei(N, True), 1.0, delta=2e-3,
                                   msg=f"N = {N}")


if __name__ == "__main__":
    unittest.main()
