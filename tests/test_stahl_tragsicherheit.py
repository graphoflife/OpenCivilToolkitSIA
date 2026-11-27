"""
Tests fuer die Tragsicherheit eines Stahlquerschnitts je Lastfall nach SIA
263:2013 (Plan vom 2026-11-25, Schritt 12b): Biegung und Normalkraft nach
der Klasse im Lastfall, Querkraft je Richtung.

Von Hand, S355 mit f = 355/1.05 = 338.1 N/mm²; Flaeche, Traegheitsmoment
und die Widerstaende ohne Einwirkung aus dem Umriss des Werkzeugs (die
Kennzahlen, :mod:`tests.test_stahlbau`):

* HEB 300, N_Ed = -500 kN: die Normalkraft braucht im Steg die Hoehe
  500 000/(11 · 338.1) = 134.4 mm, weniger als sein gerader Teil, 300 - 2 · 19
  - 2 · 27 = 208 mm. Das Moment verliert N²/(4 t_w f) = 16.8 kNm.
* HEB 300, V_z = 700 kN ueber der Haelfte von V_z,Rd: der Steg zwischen den
  Flanschen, h_w = 300 - 2 · 19 = 262 mm, traegt mit 1 - ρ, ρ = (V/V_Rd)²:
  das Moment verliert ρ f t_w h_w²/4 -- wie (43), dort ohne Ausrundungen.
* HEA 300, N_Ed = -1000 kN und M_y: die Flansche in Klasse 3, (54):
  M_Rd = M_el,Rd (1 - |N_Ed|/N_Rd).
* IPE 600 bei Druck in Klasse 4: N_Rd = (A - (1 - ρ) · 581 · 12) f mit
  ρ = 0.9/λ_p, λ_p = (581/12)/(28.4 ε · 2). Mit Moment (60), e_N = 0 im
  symmetrischen Steg und W_eff = I_y/300 -- der Steg ist bei Biegung
  Klasse 1: M_Rd = f W (1 - |N_Ed|/N_Rd).
* ROR 219.1 x 8: die Resultierende gegen V_Rd = 205 · 2 · 8 · (219.1 - 8)/1.05
  = 659.4 kN.
* FL 200 x 20 -- dasselbe Rechteck wie das freie Blech, als Profil: ohne
  Bleche in Klasse 1, M_Rd = f · 200 · 20²/4 = 6.76 kNm statt elastisch
  f · 200 · 20²/6, und die Querkraft mit A_v = A: V_Rd = 205 · 4000/1.05
  = 780.9 kN.
* RND 40: die Resultierende gegen V_Rd = 205 · A/1.05, A die Flaeche des
  Umrisses.
"""

import math
import unittest

from opencivil.bericht.markdown import als_markdown
from opencivil.nachweis.qa_stahl import OHNE_PROFIL, OHNE_TORSION
from opencivil.nachweis.qa_stahl_werte import ROHR_KLASSE_4
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.biegung import SCHIEF
from opencivil.querschnitt.gesetzwahl import Werkstoffsatz
from opencivil.stahlbau import widerstand as wd
from opencivil.stahlprofile.lage import Profillage
from tests.test_stahlbau import kennzahlen, rechteck
from tests.test_stahlprofile_qa import analyse, projekt

#: Die Fliessgrenze von S355 mit γ_M1, in N/mm².
F = 355.0 / 1.05

#: So weit darf die Rechnung von der Hand abweichen.
GENAU = 1e-4


def rechnen(*profile, faelle, polygone=(), einachsig=False, charakteristisch=False):
    """
    Die Urteile je (Art, Lastfall) einer Analyse aus ``profile`` mit den
    Lastfaellen ``faelle`` -- je Name ihre Werte in kN und kNm --, dazu
    Aufbau, Analyse und Loesung.
    """
    p = projekt()
    a = analyse(p, *profile, polygone=polygone)
    a.einachsig = einachsig
    if charakteristisch:
        a.werkstoffsaetze = {"st1": Werkstoffsatz.CHARAKTERISTISCH}
    for name, werte in faelle.items():
        a.lastfall(name, **werte)
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.teile[a.kennung].ziele())
    return {(u.art, u.fall): u for u in loesung.urteile}, aufbau, a, loesung


def grad(urteil):
    return urteil.erfuellungsgrad.si


class TestPlastisch(unittest.TestCase):
    """Klasse 1 und 2: der plastische Zustand bei N_Ed, in der Richtung der Einwirkung."""

    @classmethod
    def setUpClass(cls):
        cls.k, _, _ = kennzahlen((0, 0, "HEB 300", {}))
        cls.urteile, cls.aufbau, cls.a, cls.loesung = rechnen((0, 0, "HEB 300", {}), faelle={
            "N": {"N_Ed": -500, "M_y_Ed": 200},
            "V": {"M_y_Ed": 100, "V_z_Ed": 700},
            "jenseits": {"N_Ed": -6000, "M_y_Ed": 50},
            "Druck": {"N_Ed": -3000},
            "T": {"T_Ed": 5},
        })

    def test_der_steg_traegt_die_normalkraft(self):
        M_Rd = self.k["M_Rd_unten"] - (500e3) ** 2 / (4 * 11 * F) / 1e6
        self.assertAlmostEqual(grad(self.urteile["M-N", "N"]), M_Rd / 200, delta=GENAU)

    def test_eine_grosse_querkraft_nimmt_dem_steg(self):
        rho = (700 / self.k["V_z_Rd"]) ** 2
        M_Rd = self.k["M_Rd_unten"] - rho * F * 11 * 262 ** 2 / 4 / 1e6
        self.assertAlmostEqual(grad(self.urteile["M-N", "V"]), M_Rd / 100, delta=GENAU)
        self.assertAlmostEqual(grad(self.urteile["V", "V"]), self.k["V_z_Rd"] / 700, delta=GENAU)

    def test_jenseits_der_normalkraft(self):
        """Mehr Druck, als der ganze Querschnitt traegt: kein Zustand -- N_Rd gegen N_Ed."""
        u = self.urteile["M-N", "jenseits"]
        self.assertFalse(u.erfuellt)
        self.assertAlmostEqual(grad(u), -self.k["N_Rd_druck"] / 6000, delta=GENAU)

    def test_reiner_druck(self):
        self.assertAlmostEqual(grad(self.urteile["M-N", "Druck"]), -self.k["N_Rd_druck"] / 3000,
                               delta=GENAU)

    def test_torsion_nur_ein_hinweis(self):
        """T allein: kein Nachweis, aber die Warnung mit dem Namen des Lastfalls."""
        u = self.urteile["M-N", "T"]
        self.assertTrue(u.erfuellt)
        self.assertTrue(math.isinf(grad(u)))
        self.assertIn(f"Querschnittsanalyse 'Profile', T: {OHNE_TORSION}",
                      [w.text for w in self.aufbau.warnungen])

    def test_ohne_querkraft_kein_querkraftnachweis(self):
        self.assertTrue(math.isinf(grad(self.urteile["V", "N"])))

    def test_die_herleitung(self):
        """Je Nachweis eine Ueberschrift, I_T unter seiner eigenen; V_y = 0 steht nicht da."""
        text = als_markdown(self.loesung, aufbau=self.aufbau)
        stellen = [text.index(f"\n### {t}\n") for t in
                   ("Kennzahlen", "Biegung und Normalkraft", "Querkraft",
                    "Torsionsträgheitsmoment")]
        self.assertEqual(stellen, sorted(stellen))
        nachweis = text[stellen[2]:stellen[3]]
        self.assertIn("**Querkraft in z**", nachweis)
        self.assertNotIn("Querkraft in y", nachweis)


class TestRichtung(unittest.TestCase):
    """Zweiachsig dreht die Nulllinie, bis der Widerstand in die Richtung der Einwirkung zeigt."""

    def test_der_widerstand_zeigt_wie_die_einwirkung(self):
        _, aufbau, a, _ = rechnen((0, 0, "HEB 300", {}), faelle={"LF": {"M_y_Ed": 1}})
        stahl = aufbau.feld("qa_stahl")[a.kennung].stahl
        x = wd.rechnen(stahl, [F], [math.sqrt(235 / 355)], -1000e3, 200e6, 100e6, [], (0.0, 0.0),
                       SCHIEF)
        self.assertEqual(x.klasse, 1)
        self.assertAlmostEqual(x.plastisch.N, -1000e3, delta=1.0)
        self.assertAlmostEqual(x.plastisch.M_z / x.plastisch.M_y, 0.5, places=3)

    def test_einachsig_zaehlt_M_z_nicht(self):
        k, _, _ = kennzahlen((0, 0, "HEB 300", {}))
        urteile, *_ = rechnen((0, 0, "HEB 300", {}), faelle={"LF": {"M_y_Ed": 200, "M_z_Ed": 50}},
                              einachsig=True)
        self.assertAlmostEqual(grad(urteile["M-N", "LF"]), k["M_Rd_unten"] / 200, delta=GENAU)

    def test_charakteristisch_ohne_gamma(self):
        k, _, _ = kennzahlen((0, 0, "HEB 300", {}))
        urteile, *_ = rechnen((0, 0, "HEB 300", {}), faelle={"LF": {"M_y_Ed": 200}},
                              charakteristisch=True)
        self.assertAlmostEqual(grad(urteile["M-N", "LF"]), k["M_Rd_unten"] * 1.05 / 200,
                               delta=GENAU)


class TestLinear(unittest.TestCase):
    """Klasse 3 nach (54), Klasse 4 nach (60) -- als Widerstaende, mit dem Faktor λ auf M."""

    def test_klasse_3(self):
        k, _, _ = kennzahlen((0, 0, "HEA 300", {}))
        urteile, *_ = rechnen((0, 0, "HEA 300", {}), faelle={"LF": {"N_Ed": -1000, "M_y_Ed": 100}})
        u = urteile["M-N", "LF"]
        self.assertIn("Klasse 3, (54)", u.begruendung)
        M_Rd = k["M_Rd_unten"] * (1 - 1000 / k["N_Rd_zug"])
        self.assertAlmostEqual(grad(u), M_Rd / 100, delta=GENAU)

    def test_klasse_4(self):
        urteile, _, a, loesung = rechnen((0, 0, "IPE 600", {}), faelle={
            "N": {"N_Ed": -4000}, "NM": {"N_Ed": -4000, "M_y_Ed": 50},
            "zuviel": {"N_Ed": -6000, "M_y_Ed": 50}})
        wert = lambda g: loesung.wert(f"querschnittsanalyse.{a.kennung}.{g}").groesse.si  # noqa: E731
        lam = (581 / 12) / (28.4 * math.sqrt(235 / 355) * 2)
        N_Rd = (wert("A") * 1e6 - (1 - 0.9 / lam) * 581 * 12) * F / 1e3
        W = wert("I_y") * 1e12 / 300
        for fall, soll in (("N", N_Rd / 4000), ("NM", F * W * (1 - 4000 / N_Rd) / 50e6),
                           ("zuviel", N_Rd / 6000)):
            with self.subTest(fall=fall):
                self.assertAlmostEqual(grad(urteile["M-N", fall]), soll, delta=GENAU)
        self.assertIn("Klasse 4, (60)", urteile["M-N", "NM"].begruendung)
        self.assertIn("schon N_Ed allein", urteile["M-N", "zuviel"].begruendung)
        self.assertFalse(urteile["M-N", "zuviel"].erfuellt)

    def test_das_freie_blech_unter_dem_profil(self):
        """Zieht das Moment das Blech, Klasse 1; drueckt es, Klasse 3 -- wie die Kennzahlen."""
        blech = (rechteck(-150, -170, 300, 20), "st1")
        k, _, _ = kennzahlen((0, 0, "HEB 300", {}), polygone=[blech])
        urteile, *_ = rechnen((0, 0, "HEB 300", {}), polygone=[blech],
                              faelle={"plus": {"M_y_Ed": 100}, "minus": {"M_y_Ed": -100}})
        self.assertIn("Klasse 1", urteile["M-N", "plus"].begruendung)
        self.assertIn("Klasse 3", urteile["M-N", "minus"].begruendung)
        self.assertAlmostEqual(grad(urteile["M-N", "plus"]), k["M_Rd_unten"] / 100, delta=GENAU)
        self.assertAlmostEqual(grad(urteile["M-N", "minus"]), -k["M_Rd_oben"] / 100, delta=GENAU)


class TestRohr(unittest.TestCase):
    def test_klasse_4_nicht_fuehrbar(self):
        urteile, *_ = rechnen((0, 0, "ROR 323.9 x 5", {}),
                              faelle={"LF": {"N_Ed": -500, "M_y_Ed": 30}})
        u = urteile["M-N", "LF"]
        self.assertEqual((u.erfuellt, u.hinweis), (False, ROHR_KLASSE_4))

    def test_die_resultierende_querkraft(self):
        urteile, *_ = rechnen((0, 0, "ROR 219.1 x 8", {}),
                              faelle={"LF": {"V_y_Ed": 300, "V_z_Ed": 400}})
        V_Rd = 205 * 2 * 8 * (219.1 - 8) / 1.05 / 1e3
        self.assertAlmostEqual(grad(urteile["V", "LF"]), V_Rd / 500, delta=GENAU)


class TestVollstahl(unittest.TestCase):
    """Ohne Bleche Klasse 1, die Querkraft im ganzen Querschnitt -- nach Vorgabe."""

    def test_flachstahl(self):
        urteile, *_ = rechnen((0, 0, "FL 200 x 20", {}), faelle={"LF": {"M_y_Ed": 1, "V_z_Ed": 10}})
        self.assertAlmostEqual(grad(urteile["M-N", "LF"]), F * 200 * 20 ** 2 / 4 / 1e6, delta=GENAU)
        self.assertAlmostEqual(grad(urteile["V", "LF"]), 205 * 200 * 20 / 1.05 / 1e3 / 10,
                               delta=GENAU)

    def test_rundstahl_traegt_die_resultierende(self):
        urteile, *_ = rechnen((0, 0, "RND 40", {}), faelle={"LF": {"V_y_Ed": 30, "V_z_Ed": 40}})
        A = geo.flaechenwerte(Profillage("RND 40").umrisse[0]).A
        self.assertAlmostEqual(grad(urteile["V", "LF"]), 205 * A / 1.05 / 1e3 / 50, delta=GENAU)


class TestOhneProfil(unittest.TestCase):
    def test_ein_freies_blech_traegt_keine_querkraft(self):
        urteile, *_ = rechnen(polygone=[(rechteck(-100, -10, 200, 20), "st1")],
                              faelle={"LF": {"M_y_Ed": 1, "V_z_Ed": 10}})
        u = urteile["V", "LF"]
        self.assertEqual((u.erfuellt, u.hinweis), (False, OHNE_PROFIL))
        M_Rd = F * 200 * 20 ** 2 / 6 / 1e6
        self.assertAlmostEqual(grad(urteile["M-N", "LF"]), M_Rd, delta=GENAU)


if __name__ == "__main__":
    unittest.main()
