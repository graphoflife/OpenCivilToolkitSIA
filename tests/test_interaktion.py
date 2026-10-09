"""
Bruchzustand gezeichneter Querschnitte -- gerade und schief.

Der wichtigste Prüfstein steht zuerst: ein Rechteck mit zwei Lagen ist eine
Platte, und dafür gibt es schon eine genaue Linie
(:class:`~opencivil.nachweis.resistenzlinie.Ebenenlinie`). Zwei unabhängig
gebaute Wege müssen dasselbe ergeben. Danach Symmetrie, die Probe jedes Bruchzustands und
Fälle, die sich von Hand nachrechnen lassen.
"""

import math
import unittest

from opencivil.nachweis import linie
from opencivil.nachweis.rechenwahl import Rechenart, Rechenwahl
from opencivil.nachweis.resistenzlinie import Ebenenlinie
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.interaktion import (
    Bewehrung, Querschnitt, Teil, Werkstoff, _bei_n_gelesen, _schnittstellen,
    linie_als_bewehrung,
)
from opencivil.querschnitt.werkstoffgesetz import Betongesetz, Spannungsblock, Stahlgesetz

BETON = Betongesetz(f_cd=20e6, eps_c1d=0.002, eps_c2d=0.003, k_sigma=2.0)
STAHL = Stahlgesetz(E_s=200e9, f_yd=435e6, f_yd_druck=435e6, eps_ud=0.045)
WERKSTOFFE = [
    Werkstoff("Beton", BETON.spannung, -0.003, math.inf, c_punkt=(0.002, 0.003),
              verdraengbar=True),
    Werkstoff("Stahl", STAHL.spannung, -0.045, 0.045),
]


def rechteck(y0, z0, b, h):
    return ((y0, z0), (y0 + b, z0), (y0 + b, z0 + h), (y0, z0 + h))


def querschnitt(teile, staebe, bezug=None):
    if bezug is None:
        w = geo.summe([(1.0 if t.werkstoff is not None else -1.0,
                        geo.flaechenwerte(t.punkte)) for t in teile])
        bezug = (w.y_S, w.z_S)
    return Querschnitt(werkstoffe=WERKSTOFFE, teile=teile, bewehrung=staebe, bezug=bezug)


class TestWieDiePlatte(unittest.TestCase):
    """1000×250 mit zwei Lagen -- gegen die genaue Linie der Platte."""

    h, b = 0.25, 1.0

    def setUp(self):
        self.ebenen = Ebenenlinie(
            Rechenwahl(art=Rechenart.PARABEL), h=self.h, b=self.b, beton=BETON.spannung,
            lagen=[(1131e-6, 0.215, STAHL, "unten"), (565e-6, 0.035, STAHL, "oben")],
            eps_c1d=BETON.eps_c1d, eps_c2d=BETON.eps_c2d)
        self.platte = self.ebenen.punkte
        self.neu = querschnitt(
            [Teil(rechteck(0, 0, self.b, self.h), 0, None)],
            [Bewehrung((0.5, self.h - 0.215), 1131e-6, 1, 0),
             Bewehrung((0.5, self.h - 0.035), 565e-6, 1, 0)])

    def test_momente_bei_n_null(self):
        alt = linie.schnitte(self.platte, linie.MOMENT, 0.0)
        unten = self.neu.bei_normalkraft(-math.pi / 2, 0.0)  # Zug unten
        oben = self.neu.bei_normalkraft(math.pi / 2, 0.0)    # Zug oben
        self.assertAlmostEqual(unten.M_y / max(alt), 1.0, delta=1e-4)
        self.assertAlmostEqual(oben.M_y / min(alt), 1.0, delta=1e-4)
        self.assertAlmostEqual(unten.M_z, 0.0, delta=1e-6)

    def test_reine_normalkraft(self):
        zug, druck = self.neu.normalkraft_grenzen()
        self.assertAlmostEqual(zug / max(p.N for p in self.platte), 1.0, delta=1e-9)
        self.assertAlmostEqual(druck / min(p.N for p in self.platte), 1.0, delta=1e-9)

    def test_mit_druck_innert_einem_promille(self):
        """Das Polygon interpoliert zwischen Stützstellen, die Suche trifft genau."""
        for N in (-2000e3, -500e3, 300e3):
            alt = max(linie.schnitte(self.platte, linie.MOMENT, N))
            neu = self.neu.bei_normalkraft(-math.pi / 2, N)
            self.assertAlmostEqual(neu.N, N, delta=1e-3)
            self.assertAlmostEqual(neu.M_y / alt, 1.0, delta=1e-3, msg=f"N = {N}")

    def test_beide_suchen_genau_treffen_sich(self):
        """
        Beide suchen auf dem Fächer, nicht auf der Sehne: dann bleibt nur, was
        die Fasern unterscheidet -- je 200 über die Höhe, aber anders gelegt.
        """
        for N in (-2000e3, -500e3, 0.0, 300e3):
            platte = self.ebenen.moment_bei(N, positiv=True)
            neu = self.neu.bei_normalkraft(-math.pi / 2, N)
            self.assertAlmostEqual(neu.M_y / platte, 1.0, delta=1e-4, msg=f"N = {N}")

    def test_faecher_von_zug_nach_druck(self):
        punkte = self.neu.faecher(-math.pi / 2)
        zug, druck = self.neu.normalkraft_grenzen()
        self.assertAlmostEqual(punkte[0].N, zug)
        self.assertAlmostEqual(punkte[-1].N, druck)
        self.assertTrue(all(p.chi >= 0.0 for p in punkte))

    def test_probe_der_anteile(self):
        """Was in der Herleitung steht, muss sich zu N und M summieren."""
        punkt = self.neu.bei_normalkraft(-math.pi / 2, -500e3)
        anteile = self.neu.anteile(punkt)
        y_S, z_S = self.neu.bezug
        self.assertAlmostEqual(sum(a.N for a in anteile), punkt.N, delta=1e-3)
        self.assertAlmostEqual(sum(-a.N * (a.z - z_S) for a in anteile), punkt.M_y, delta=1e-3)
        self.assertAlmostEqual(sum(-a.N * (a.y - y_S) for a in anteile), punkt.M_z, delta=1e-3)

    def test_druckzone(self):
        x, d = self.neu.druckzone(self.neu.bei_normalkraft(-math.pi / 2, 0.0))
        self.assertAlmostEqual(d, 0.215, delta=1e-9)
        self.assertTrue(0.0 < x < 0.25 * d)


class TestSchief(unittest.TestCase):

    def stuetze(self):
        a = 0.4
        return querschnitt(
            [Teil(rechteck(0, 0, a, a), 0, None)],
            [Bewehrung((y, z), 491e-6, 1, 0) for y in (0.05, 0.35) for z in (0.05, 0.35)])

    def test_quadrat_ist_in_beiden_achsen_gleich(self):
        s = self.stuetze()
        um_y = s.in_richtung(-800e3, 100e3, 0.0)
        um_z = s.in_richtung(-800e3, 0.0, 100e3)
        self.assertAlmostEqual(um_y.moment / um_z.moment, 1.0, delta=1e-6)
        self.assertAlmostEqual(um_y.M_z, 0.0, delta=1e-3)

    def test_vorzeichen(self):
        """M_y > 0 zieht unten, M_z > 0 zieht links."""
        s = self.stuetze()
        punkt = s.in_richtung(0.0, 100e3, 0.0)
        self.assertGreater(s.dehnung(punkt, (0.2, 0.0)), 0.0)
        punkt = s.in_richtung(0.0, 0.0, 100e3)
        self.assertGreater(s.dehnung(punkt, (0.0, 0.2)), 0.0)
        self.assertLess(s.dehnung(punkt, (0.4, 0.2)), 0.0)

    def test_schraeg_trifft_die_richtung_und_ist_kleiner(self):
        s = self.stuetze()
        gerade = s.in_richtung(-800e3, 100e3, 0.0).moment
        schraeg = s.in_richtung(-800e3, 100e3, 100e3)
        self.assertAlmostEqual(math.atan2(schraeg.M_z, schraeg.M_y), math.pi / 4, delta=1e-6)
        self.assertLess(schraeg.moment, gerade)

    def test_l_dreht_die_nulllinie(self):
        """Beim L steht die Nulllinie für reines M_y nicht waagrecht."""
        l_form = ((0, 0), (0.6, 0), (0.6, 0.15), (0.15, 0.15), (0.15, 0.6), (0, 0.6))
        l = querschnitt([Teil(l_form, 0, None)],
                        [Bewehrung((0.05, 0.05), 314e-6, 1, 0),
                         Bewehrung((0.55, 0.05), 314e-6, 1, 0),
                         Bewehrung((0.05, 0.55), 314e-6, 1, 0)])
        for M_y, M_z in ((50e3, 0.0), (0.0, 50e3), (50e3, -50e3)):
            punkt = l.in_richtung(-300e3, M_y, M_z)
            self.assertAlmostEqual(punkt.N, -300e3, delta=1e-2)
            fehler = math.remainder(math.atan2(punkt.M_z, punkt.M_y)
                                    - math.atan2(M_z, M_y), 2 * math.pi)
            self.assertLess(abs(fehler), 1e-6)
        gerade = l.in_richtung(-300e3, 50e3, 0.0)
        self.assertGreater(abs(math.degrees(gerade.psi) + 90.0), 10.0)

    def test_jenseits_der_normalkraft_nichts(self):
        s = self.stuetze()
        _, druck = s.normalkraft_grenzen()
        self.assertIsNone(s.in_richtung(1.01 * druck, 100e3, 0.0))


class TestVonHand(unittest.TestCase):

    def test_ohne_bewehrung_kein_zug(self):
        nackt = querschnitt([Teil(rechteck(0, 0, 0.3, 0.5), 0, None)], [])
        zug, druck = nackt.normalkraft_grenzen()
        self.assertAlmostEqual(zug, 0.0)
        self.assertAlmostEqual(druck, -20e6 * 0.3 * 0.5, delta=1.0)

    def test_aussparung_zaehlt_nicht(self):
        voll = querschnitt([Teil(rechteck(0, 0, 0.6, 0.8), 0, None)], [])
        kasten = querschnitt([Teil(rechteck(0, 0, 0.6, 0.8), 0, None),
                              Teil(rechteck(0.15, 0.15, 0.3, 0.5), None, 0)], [])
        self.assertAlmostEqual(voll.normalkraft_grenzen()[1] - kasten.normalkraft_grenzen()[1],
                               -20e6 * 0.3 * 0.5, delta=1.0)

    def test_druck_mit_staeben(self):
        """Gleichmässig -eps_c1d: Beton bei f_cd, Stahl elastisch bei E_s·eps_c1d."""
        s = querschnitt([Teil(rechteck(0, 0, 0.4, 0.4), 0, None)],
                        [Bewehrung((y, z), 491e-6, 1, 0) for y in (0.05, 0.35) for z in (0.05, 0.35)])
        a_s = 4 * 491e-6
        erwartet = -20e6 * (0.16 - a_s) - a_s * 200e9 * 0.002
        self.assertAlmostEqual(s.normalkraft_grenzen()[1] / erwartet, 1.0, delta=1e-9)

    def test_verschmierte_linie_wie_einzelstaebe(self):
        teil = Teil(rechteck(0, 0, 1.0, 0.3), 0, None)
        staebe = querschnitt([teil], [Bewehrung((0.05 + 0.1 * k, 0.04), 1500e-6 / 10, 1, 0)
                                      for k in range(10)])
        linie_ = querschnitt([teil], linie_als_bewehrung((0.0, 0.04), (1.0, 0.04),
                                                         1500e-6, 1, 0))
        a = staebe.bei_normalkraft(-math.pi / 2, 0.0).M_y
        b = linie_.bei_normalkraft(-math.pi / 2, 0.0).M_y
        self.assertAlmostEqual(a / b, 1.0, delta=1e-3)


if __name__ == "__main__":
    unittest.main()


class TestSpannungsblock(unittest.TestCase):
    """
    Der Block springt bei 0.15·ε_c2d von null auf f_cd. In der Mitte jeder
    Faser gelesen, sprang darum auch N -- am Kastenträger des vollen Berichts
    stand in der Probe 638.7 kN, nachgewiesen wurden 664.0 kN. Über die Faser
    gemittelt, wächst N stetig, und jede verlangte Normalkraft wird getroffen.
    """

    def setUp(self):
        block = Spannungsblock(f_cd=20e6, eps_c2d=0.003)
        werkstoffe = [
            Werkstoff("Beton", block, -0.003, math.inf, c_punkt=(0.002, 0.003),
                      verdraengbar=True),
            Werkstoff("Stahl", STAHL.spannung, -0.045, 0.045),
        ]
        # Ein Kasten mit Loch und Stäben im Beton: Fasern und verdrängtes
        # Material springen beide.
        teile = [Teil(rechteck(0, 0, 0.8, 0.6), 0, None),
                 Teil(rechteck(0.15, 0.15, 0.5, 0.3), None, 0)]
        staebe = [Bewehrung((y, z), 314e-6, 1, 0)
                  for y in (0.05, 0.4, 0.75) for z in (0.05, 0.55)]
        w = geo.summe([(1.0, geo.flaechenwerte(teile[0].punkte)),
                       (-1.0, geo.flaechenwerte(teile[1].punkte))])
        self.q = Querschnitt(werkstoffe=werkstoffe, teile=teile, bewehrung=staebe,
                             bezug=(w.y_S, w.z_S))

    def test_mittel_ist_der_anteil_ueber_dem_knick(self):
        block = Spannungsblock(f_cd=20e6, eps_c2d=0.003)
        knick = -block.eps_knick                       # -0.45 ‰
        self.assertEqual(block.mittel(-0.001, -0.002), -20e6)
        self.assertEqual(block.mittel(0.001, -0.0001), 0.0)
        self.assertAlmostEqual(block.mittel(knick + 0.0001, knick - 0.0001), -10e6)
        self.assertAlmostEqual(block.mittel(knick - 0.0003, knick + 0.0001), -15e6)
        self.assertEqual(block.mittel(-0.001, -0.001), block(-0.001))

    def test_jede_normalkraft_wird_getroffen(self):
        zug, druck = self.q.normalkraft_grenzen()
        for psi in (-math.pi / 2, -2.0, 0.3):
            for anteil in (0.9, 0.5, 0.1, -0.2, -0.6, -0.95):
                N = anteil * (zug if anteil > 0 else -druck)
                punkt = self.q.bei_normalkraft(psi, N)
                with self.subTest(psi=psi, N=N):
                    self.assertAlmostEqual(punkt.N, N, delta=1e-3)
                    self.assertAlmostEqual(sum(a.N for a in self.q.anteile(punkt)), N, delta=1e-3)


class TestFlaecheDerWiderstaende(unittest.TestCase):
    """
    Das Interaktionsdiagramm ist ein Schnitt durch die Fläche aller
    Bruchzustände. Bei festem N kommt er aus derselben Suche wie der
    Nachweis; bei festem Moment aus den Fächern, linear gelesen -- dort
    gilt eine Schranke gegen die genaue Suche.
    """

    @classmethod
    def setUpClass(cls):
        # Unten mehr Stahl als oben, also kein Spiegel um y: die beiden Äste
        # sind verschieden, und links wie rechts ist es symmetrisch.
        cls.q = querschnitt(
            [Teil(rechteck(0, 0, 0.3, 0.6), 0, None)],
            [Bewehrung((y, 0.05), 314e-6, 1, 0) for y in (0.05, 0.15, 0.25)]
            + [Bewehrung((y, 0.55), 113e-6, 1, 0) for y in (0.05, 0.25)])

    def genauer_umriss(self, N, achse, wert, neigungen=360):
        umriss = [(p.M_y, p.M_z) for p in (
            self.q.bei_normalkraft(2 * math.pi * k / neigungen, N) for k in range(neigungen))]
        stellen = _schnittstellen(umriss, achse, wert)
        return min(stellen), max(stellen)

    def test_der_faecher_hat_keine_sehne_mehr(self):
        """
        Gleichmässig in der Krümmung verteilt, sprang N zwischen zwei
        Stützstellen um ein Drittel der Spanne; dazwischen war die Linie eine
        Sehne. Jetzt liegt sie überall nah an der genauen Suche.
        """
        f = self.q.faecher(-math.pi / 2)
        spanne = f[0].N - f[-1].N
        self.assertLessEqual(max(a.N - b.N for a, b in zip(f, f[1:])), 0.05 * spanne + 1e-6)
        for i in range(1, 40):
            N = f[0].N - spanne * i / 40
            genau = self.q.bei_normalkraft(-math.pi / 2, N)
            gelesen = _bei_n_gelesen(f, N)[0]
            self.assertAlmostEqual(gelesen / genau.M_y, 1.0, delta=2e-3, msg=f"N = {N}")

    def test_bei_festem_n_wie_der_nachweis(self):
        N = -500e3
        punkte = self.q.schnitt("N", N, neigungen=36)
        self.assertEqual(len(punkte), 36)
        for k, (n, m_y, m_z) in enumerate(punkte):
            genau = self.q.bei_normalkraft(2 * math.pi * k / 36, N)
            self.assertAlmostEqual(n, N, delta=1e-3)
            self.assertEqual((m_y, m_z), (genau.M_y, genau.M_z))

    def test_bei_m_z_null_die_beiden_aeste_der_linie_um_y(self):
        """Je Stufe auf 0.3 % des grössten Moments -- so fein liest der Fächer."""
        punkte = self.q.schnitt("M_z", 0.0)
        groesstes = max(abs(M_y) for _, M_y, _ in punkte)
        je_n = {}
        for N, M_y, M_z in punkte:
            self.assertEqual(M_z, 0.0)
            je_n.setdefault(N, []).append(M_y)
        for N, werte in je_n.items():
            for psi, wert in ((-math.pi / 2, max(werte)), (math.pi / 2, min(werte))):
                genau = self.q.bei_normalkraft(psi, N).M_y
                self.assertAlmostEqual(wert, genau, delta=3e-3 * groesstes,
                                       msg=f"N = {N}, ψ = {psi}")

    def test_bei_festem_moment_abseits_der_achse(self):
        """M_z = 40 kNm: auf jeder Stufe dort, wo der genaue Umriss die Gerade kreuzt."""
        je_n = {}
        for N, M_y, M_z in self.q.schnitt("M_z", 40e3):
            self.assertEqual(M_z, 40e3)
            je_n.setdefault(N, []).append(M_y)
        stufen = sorted(je_n)
        for N in stufen[5::12]:
            links, rechts = self.genauer_umriss(N, 1, 40e3)
            spanne = max(abs(links), abs(rechts), 1e3)
            self.assertAlmostEqual(min(je_n[N]), links, delta=5e-3 * spanne)
            self.assertAlmostEqual(max(je_n[N]), rechts, delta=5e-3 * spanne)

    def test_jenseits_der_flaeche_nichts(self):
        self.assertEqual(self.q.schnitt("M_z", 1e9), [])
        zug, _ = self.q.normalkraft_grenzen()
        self.assertEqual(self.q.schnitt("N", 2 * zug), [])

    def test_nur_n_m_y_und_m_z(self):
        with self.assertRaises(ValueError):
            self.q.schnitt("V", 0.0)
