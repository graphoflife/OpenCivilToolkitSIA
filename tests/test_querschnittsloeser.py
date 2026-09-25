"""Tests für den Querschnittslöser."""

import math
import unittest

from opencivil.nachweis.querschnittsloeser import (
    Querschnittsloeser, Stahllage, beton_elastisch, beton_nichtlinear,
    stahl_bilinear,
)
from opencivil.nachweis.zustand2 import gerissen, wertigkeit


def elastischer_loeser(a_s=2450e-6, d=0.2601, phi=2.0, h=0.3, b=1.0):
    """Gerissen, linear elastisch -- der Fall mit geschlossener Lösung."""
    return Querschnittsloeser(
        h=h, b=b, lagen=[Stahllage(a_s=a_s, z=d, nummer=1)],
        beton=beton_elastisch(E_c=33.62e9 / (1.0 + phi)),
        stahl=stahl_bilinear(E_s=200e9, f_sd=1e12))


class TestGegenDieGeschlosseneLoesung(unittest.TestCase):
    """
    Bei reiner Biegung im Zustand II gibt es eine Formel -- also lässt sich
    der Löser daran messen. Das ist die einzige Stelle, an der beide Wege
    dasselbe rechnen; sie muss stimmen.
    """

    def test_stahlspannung_stimmt_mit_der_formel(self):
        n = wertigkeit(E_s=200e9, E_cm=33.62e9, phi=2.0)
        z2 = gerissen(n=n, a_s=2450e-6, b=1.0, d=0.2601)
        M = 100e3

        ebene = elastischer_loeser().loese(N_Ed=0.0, M_Ed=M)
        self.assertTrue(ebene.konvergiert)
        self.assertAlmostEqual(ebene.sigma_s[0] / 1e6,
                               M / (2450e-6 * z2.z) / 1e6, delta=0.1)

    def test_die_nulllinie_stimmt_mit_der_formel(self):
        n = wertigkeit(E_s=200e9, E_cm=33.62e9, phi=2.0)
        z2 = gerissen(n=n, a_s=2450e-6, b=1.0, d=0.2601)

        ebene = elastischer_loeser().loese(N_Ed=0.0, M_Ed=100e3)
        # Nulllinie: dort, wo eps = 0.  eps(z) = eps_m + chi*(z - h/2)
        x = 0.15 - ebene.eps_m / ebene.chi
        self.assertAlmostEqual(x * 1e3, z2.x * 1e3, delta=0.5)

    def test_die_spannung_waechst_linear_mit_dem_moment(self):
        """Im linearen Gesetz muss sie das -- eine Probe auf den Löser selbst."""
        loeser = elastischer_loeser()
        eins = loeser.loese(N_Ed=0.0, M_Ed=50e3).sigma_s[0]
        zwei = loeser.loese(N_Ed=0.0, M_Ed=100e3).sigma_s[0]
        self.assertAlmostEqual(zwei / eins, 2.0, delta=0.005)


class TestProbe(unittest.TestCase):
    """
    Was der Löser liefert, muss die Einwirkung erzeugen. Das ist die Aussage,
    die in der Mitschrift steht -- also wird genau sie geprüft.
    """

    def faelle(self):
        # Nur Fälle, die der Querschnitt auch tragen kann. Mit **einer**
        # unteren Lage und Netto-Zug nimmt der Beton gar nichts auf: dann
        # liegt die Resultierende zwingend im Stahl, und es gäbe genau ein
        # zugehöriges Moment. Zug wird darum unten mit zwei Lagen geprüft.
        return [(0.0, 100e3), (-300e3, 100e3),
                (-1000e3, 20e3), (0.0, -8e3), (-500e3, -60e3)]

    def test_gleichgewicht_bei_reiner_biegung_und_mit_normalkraft(self):
        loeser = elastischer_loeser()
        for N_Ed, M_Ed in self.faelle():
            with self.subTest(N=N_Ed, M=M_Ed):
                e = loeser.loese(N_Ed=N_Ed, M_Ed=M_Ed)
                self.assertTrue(e.konvergiert)
                self.assertAlmostEqual(e.N_int, N_Ed, delta=max(1.0, abs(N_Ed) * 1e-6))
                self.assertAlmostEqual(e.M_int, M_Ed, delta=max(1.0, abs(M_Ed) * 1e-6))

    def test_gleichgewicht_unter_zug_mit_zwei_lagen(self):
        """
        Mit Bewehrung oben und unten trägt der Querschnitt auch reinen Zug --
        die beiden Lagen teilen ihn nach ihrem Hebelarm auf.
        """
        loeser = Querschnittsloeser(
            h=0.3, b=1.0,
            lagen=[Stahllage(a_s=1200e-6, z=0.26, nummer=1),
                   Stahllage(a_s=1200e-6, z=0.04, nummer=4)],
            beton=beton_elastisch(E_c=33.62e9 / 3.0),
            stahl=stahl_bilinear(E_s=200e9, f_sd=1e12))
        for N_Ed, M_Ed in [(200e3, 0.0), (200e3, 10e3), (500e3, -15e3)]:
            with self.subTest(N=N_Ed, M=M_Ed):
                e = loeser.loese(N_Ed=N_Ed, M_Ed=M_Ed)
                self.assertTrue(e.konvergiert)
                self.assertAlmostEqual(e.N_int, N_Ed, delta=abs(N_Ed) * 1e-5)
                self.assertAlmostEqual(e.M_int, M_Ed, delta=max(1.0, abs(M_Ed) * 1e-5))

    def test_gleichgewicht_mit_dem_nichtlinearen_gesetz(self):
        """
        Der Fall aus dem Referenzskript: h = 300, ⌀26 oben und unten,
        N = -3000 kN, M = 150 kNm, φ = 1.
        """
        d, d_u = 0.3 - 0.030 - 0.010 - 0.013, 0.030 + 0.010 + 0.013
        a_s = 5 * math.pi * 0.026 ** 2 / 4
        loeser = Querschnittsloeser(
            h=0.3, b=1.0,
            lagen=[Stahllage(a_s=a_s, z=d, nummer=1),
                   Stahllage(a_s=a_s, z=d_u, nummer=4)],
            beton=beton_nichtlinear(f_cd=28.1e6, E_c=39e9 / 2.0),
            stahl=stahl_bilinear(E_s=205e9, f_sd=300e6))

        e = loeser.loese(N_Ed=-3000e3, M_Ed=150e3)
        self.assertTrue(e.konvergiert)
        self.assertAlmostEqual(e.N_int / 1e3, -3000.0, delta=1.0)
        self.assertAlmostEqual(e.M_int / 1e3, 150.0, delta=0.5)
        # Beide Lagen gedrückt -- bei dieser Normalkraft plausibel.
        self.assertLess(e.sigma_s[0], 0.0)
        self.assertLess(e.sigma_s[1], 0.0)


class TestGrenzen(unittest.TestCase):
    def test_ohne_einwirkung_ist_die_ebene_null(self):
        """
        Exakt null, nicht bis auf die Schranke der Bisektion: der Rest von
        1e-11 gab als Stahlspannung von einem Pascal einen Erfüllungsgrad
        von 3·10⁸ statt ∞.
        """
        e = elastischer_loeser().loese(N_Ed=0.0, M_Ed=0.0)
        self.assertTrue(e.konvergiert)
        self.assertEqual((e.eps_m, e.chi), (0.0, 0.0))
        self.assertEqual(max(e.sigma_s), 0.0)

    def test_ueberforderter_querschnitt_meldet_sich(self):
        """
        Kein Ergebnis ist besser als ein erfundenes: wo kein Gleichgewicht
        möglich ist, sagt der Löser das.
        """
        loeser = Querschnittsloeser(
            h=0.3, b=1.0, lagen=[Stahllage(a_s=200e-6, z=0.26)],
            beton=beton_nichtlinear(f_cd=20e6, E_c=33e9),
            stahl=stahl_bilinear(E_s=200e9, f_sd=435e6))
        e = loeser.loese(N_Ed=0.0, M_Ed=5000e3)
        self.assertFalse(e.konvergiert)

    def test_das_fenster_haengt_an_der_kruemmung(self):
        """
        Je stärker gekrümmt, desto enger der zulässige Bereich für eps_m --
        sonst fiele eine Randfaser aus dem gültigen Dehnungsbereich, und dort
        ist nichts mehr monoton.
        """
        loeser = Querschnittsloeser(
            h=0.3, b=1.0, lagen=[Stahllage(a_s=2450e-6, z=0.26)],
            beton=beton_nichtlinear(f_cd=20e6, E_c=33e9),
            stahl=stahl_bilinear(E_s=200e9, f_sd=435e6))
        weit = loeser._fenster(0.0)
        eng = loeser._fenster(0.1)
        self.assertGreater(weit[1] - weit[0], eng[1] - eng[0])
        self.assertIsNone(loeser._fenster(1.0))

    def test_stahl_jenseits_der_bruchdehnung_traegt_nichts(self):
        gesetz = stahl_bilinear(E_s=200e9, f_sd=435e6, eps_ud=0.045)
        self.assertAlmostEqual(gesetz(0.01) / 1e6, 435.0)
        self.assertAlmostEqual(gesetz(0.05), 0.0)

    def test_beton_nimmt_keinen_zug(self):
        gesetz = beton_nichtlinear(f_cd=20e6, E_c=33e9)
        self.assertAlmostEqual(gesetz(0.001), 0.0)
        self.assertAlmostEqual(gesetz(-0.0025) / 1e6, -20.0)
        self.assertAlmostEqual(gesetz(-0.004), 0.0)
