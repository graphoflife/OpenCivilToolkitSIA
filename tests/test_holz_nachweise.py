"""
Tests fuer die Nachweise eines Holzquerschnitts nach SIA 265:2012 -- von
Hand nachgerechnet.

C24 (Tabelle 6): f_m,d = 14, f_t,0,d = 8, f_c,0,d = 12, f_v,d = 1.5 N/mm²;
aus Anhang B f_c,0,k = 21, E_0,05 = 7300 N/mm². Das Rechteck 200 × 400 mm:
A = 80 000 mm², W_y = 200 · 400² / 6 = 5.333 · 10⁶ mm³, W_z = 2.667 · 10⁶ mm³,
A_V = 2/3 · A = 53 333 mm², W_T = k_2 · h · b² = 0.2459 · 400 · 200² =
3.934 · 10⁶ mm³ (h/b = 2). In Feuchteklasse 1:

* N_Rd = 8 · 80 000 = 640 kN, −12 · 80 000 = −960 kN; M_y,Rd = 14 · 5.333
  = 74.67 kNm, M_z,Rd = 37.33 kNm; V_Rd = 1.5 · 53 333 = 80 kN;
  T_Rd = 1.5 · 3.934 = 5.90 kNm.
* N = 200 kN, M_y = 30 kNm, (21): 2.5/8 + λ · 5.625/14 = 1 → λ = 1.711.
* N = −300, M_y = 20, M_z = 5, (22): (3.75/12)² + λ · (3.75 + 1.875)/14 = 1
  → λ = 2.246.
* M_y = 50 stossartig, (14): f = 1.4 · 14 = 19.6, λ = 19.6/9.375 = 2.091.
* N = −500, (10): 12/6.25 = 1.92.
* V_z = 40, T = 3, (25): v = 0.75/1.5 = 0.5, t = 0.7626/1.5 = 0.5084;
  λ·t + λ²·v² = 1 → λ = 1.227.
* V_z = 40, V_y = 20, (23): τ_d = √(0.75² + 0.375²) = 0.8385, 1.5/0.8385 = 1.789.
* T = 5, (24): 1.5/1.271 = 1.180.

Knicken, N = −300 kN, M_y = 20 kNm, alle Laengen 4 m: um y λ = 34.64,
λ_rel = 34.64/π · √(21/7300) = 0.591, k_c = 0.921 (β_c = 0.2); um z λ_rel =
1.183, k_c = 0.556 -- (29) um z: 12 · 0.556/3.75 = 1.781. Kippen mit L_D =
6 m und M_y = 40: σ_m,crit = 0.75 · 7300 · 200²/(6000 · 400) = 91.25,
λ_rel,m = 0.513, k_m = 1, (38): 14/7.5 = 1.867.

GL24h 160 × 400 in Feuchteklasse 2: k_h = (600/400)^0.1 = 1.0414, M_y,Rd =
0.8 · 1.0414 · 16 · 4.267 = 56.87 kNm. Ein Rechteck 80 × 400 aus C24 kippt:
mit a = 8 m ist σ_m,crit = 10.95, λ_rel,m = 1.480, k_m = 1/λ² = 0.456; mit
a = 3.5 m λ_rel,m = 0.979, k_m = 1.56 − 0.75 · 0.979 = 0.826.
"""

import unittest

from opencivil.bericht.markdown import als_markdown
from opencivil.core.nachweis import OHNE_EINWIRKUNG
from opencivil.holzbau import gleichungen as gl
from opencivil.holzbau.querschnitt import k_2
from opencivil.material.holz import HOLZSORTEN, Feuchteklasse, eta_t, holz, zugglied_grund
from opencivil.nachweis.qa_holz_stabilitaet import KIPPEN_NUR_RECHTECK
from opencivil.nachweis.qa_holz_werte import TORSION_NUR_RECHTECK
from opencivil.projekt import Projekt, QuerschnittsanalyseEintrag
from opencivil.web.api import katalog

#: Ein T: Flansch 300 × 60 oben, Steg 60 × 300 -- kein Rechteck.
T_QUERSCHNITT = [[120, 0], [180, 0], [180, 300], [300, 300], [300, 360], [0, 360], [0, 300],
                 [120, 300]]


def rechteck(b, h):
    return [[0, 0], [b, 0], [b, h], [0, h]]


def rechnen(sorte="C24", ecken=rechteck(200, 400), *, feuchte="1", faelle=(), stab=(),
            einachsig=False):
    """
    Die Urteile je (Art, Fall) einer Analyse aus ``sorte`` -- je Fall ein Name
    und seine Werte in kN, kNm und m --, dazu die Kennzahlen in kN und kNm und
    das Markdown der Herleitung.
    """
    p = Projekt(name="Holz")
    p.holz(sorte)
    a = QuerschnittsanalyseEintrag.neu(kennung=p.freie_kennung("a"), name="Balken")
    a.feuchteklasse = Feuchteklasse(feuchte)
    a.einachsig = einachsig
    a.polygon(ecken, material="h1")
    for name, werte in faelle:
        a.lastfall(name, **werte)
    for name, werte in stab:
        a.stabilitaetsfall(name, **werte)
    p.querschnittsanalysen.append(a)
    aufbau = p.aufbauen()
    teil = aufbau.teile[a.kennung]
    loesung = aufbau.werk.loese(*teil.ziele())
    kennzahlen = {}
    for k in teil.kennzahlen:
        w = loesung.wert(k.definition.id)
        kennzahlen[k.definition.id.rsplit(".", 1)[1]] = w.in_einheit(w.einheit)
    return ({(u.art, u.fall): u for u in loesung.urteile}, kennzahlen,
            als_markdown(loesung, aufbau=aufbau))


class TestMaterial(unittest.TestCase):
    """Was die Nachweise vom Holz brauchen: Anhang B, Feuchteklasse, η_t, Zugglied."""

    def test_anhang_b(self):
        self.assertEqual((HOLZSORTEN["C24"].f_c_0_k, HOLZSORTEN["C24"].E_0_05), (21.0, 7300.0))
        self.assertEqual((HOLZSORTEN["GL24h"].f_c_0_k, HOLZSORTEN["GL24h"].E_0_05),
                         (24.0, 9400.0))

    def test_feuchteklasse_und_dauer(self):
        self.assertEqual([k.eta_w for k in Feuchteklasse], [1.0, 0.8, 0.6])
        self.assertEqual((eta_t(False), eta_t(True)), (1.0, 1.4))

    def test_c16_ist_kein_zugglied(self):
        self.assertIn("Tabelle 6, Fussnote 2", zugglied_grund(holz("C16")))
        self.assertEqual(zugglied_grund(holz("C24")), "")

    def test_der_katalog_fuer_die_oberflaeche(self):
        k = katalog()["querschnittsanalyse"]
        self.assertEqual([f["stand"] for f in k["feuchteklassen"]],
                         ["Klasse 1, η_w = 1", "Klasse 2, η_w = 0.8", "Klasse 3, η_w = 0.6"])
        self.assertEqual([d["wert"] for d in k["einwirkungsdauern"]], [False, True])
        self.assertIn("η_t = 1.4", k["einwirkungsdauern"][1]["titel"])


class TestGleichungen(unittest.TestCase):
    """Die Zahlen ohne Rechenwerk (:mod:`opencivil.holzbau.gleichungen`)."""

    def test_k_h(self):
        self.assertAlmostEqual(gl.k_h(400.0), 1.5 ** 0.1)
        self.assertEqual((gl.k_h(600.0), gl.k_h(100.0)), (1.0, 1.1))

    def test_k_2_des_rechtecks(self):
        self.assertAlmostEqual(k_2(1.0), 0.208, places=3)
        self.assertAlmostEqual(k_2(2.0), 0.246, places=3)
        self.assertAlmostEqual(k_2(100.0), 1 / 3, places=2)

    def test_knicken_und_kippen(self):
        lam = gl.lambda_rel(4000 / (400 / 12 ** 0.5), 21.0, 7300.0)
        self.assertAlmostEqual(lam, 0.5914, places=4)
        self.assertAlmostEqual(gl.k_c(lam, 0.2), 0.9208, places=4)
        self.assertEqual(gl.k_c(0.3, 0.2), 1.0)
        self.assertEqual(gl.k_m(0.75), 1.0)
        self.assertAlmostEqual(gl.k_m(1.0), 0.81)
        self.assertAlmostEqual(gl.k_m(2.0), 0.25)

    def test_welche_gleichung(self):
        f = {"f_t": 8.0, "f_c": 12.0, "f_m_y": 14.0, "f_m_z": 14.0}
        self.assertEqual(gl.biegung_normalkraft(2.5, 5.625, 0.0, **f).gleichung, "(21)")
        self.assertEqual(gl.biegung_normalkraft(-3.75, 3.75, 0.0, **f).gleichung, "(22)")
        self.assertEqual(gl.biegung_normalkraft(0.0, 3.75, 0.0, **f).gleichung, "(14)")
        self.assertEqual(gl.biegung_normalkraft(2.5, 0.0, 0.0, **f).gleichung, "(6)")
        self.assertEqual(gl.biegung_normalkraft(-2.5, 0.0, 0.0, **f).gleichung, "(10)")
        self.assertIsNone(gl.biegung_normalkraft(0.0, 0.0, 0.0, **f))
        self.assertEqual(gl.schub_torsion(0.5, 0.5, 1.5).gleichung, "(25)")
        self.assertIsNone(gl.schub_torsion(0.0, 0.0, 1.5))


class TestC24(unittest.TestCase):
    """Das Rechteck 200 × 400 mm aus C24, Feuchteklasse 1 -- siehe Dateikopf."""

    @classmethod
    def setUpClass(cls):
        cls.urteile, cls.kennzahlen, cls.text = rechnen(faelle=[
            ("Z", {"N_Ed": 200, "M_y_Ed": 30}),
            ("D", {"N_Ed": -300, "M_y_Ed": 20, "M_z_Ed": 5}),
            ("M", {"M_y_Ed": 50, "stossartig": True}),
            ("N", {"N_Ed": -500}),
            ("V", {"V_z_Ed": 40, "T_Ed": 3}),
            ("VV", {"V_z_Ed": 40, "V_y_Ed": 20}),
            ("T", {"T_Ed": 5}),
        ], stab=[
            ("S1", {"N_Ed": -300, "M_y_Ed": 20, "L_K_y": 4, "L_K_z": 4, "L_D": 4}),
            ("S2", {"N_Ed": -300, "L_K_y": 4, "L_K_z": 2, "L_D": 0}),
            ("S3", {"M_y_Ed": 40, "L_K_y": 0, "L_K_z": 0, "L_D": 6}),
        ])

    def grad(self, art, fall):
        return self.urteile[(art, fall)].erfuellungsgrad.si

    def test_kennzahlen(self):
        erwartet = {"N_Rd_zug": 640.0, "N_Rd_druck": -960.0, "M_y_Rd": 74.667,
                    "M_z_Rd": 37.333, "V_z_Rd": 80.0, "V_y_Rd": 80.0, "T_Rd": 5.901}
        for kurz, wert in erwartet.items():
            with self.subTest(kurz=kurz):
                self.assertAlmostEqual(self.kennzahlen[kurz], wert, places=2)

    def test_biegung_und_normalkraft(self):
        for fall, grad, gleichung in (("Z", 1.7111, "(21)"), ("D", 2.2458, "(22)"),
                                      ("M", 2.0907, "(14)"), ("N", 1.92, "(10)")):
            with self.subTest(fall=fall):
                self.assertAlmostEqual(self.grad("M-N", fall), grad, places=3)
                self.assertTrue(self.urteile[("M-N", fall)].begruendung.startswith(gleichung))

    def test_schub_und_torsion(self):
        for fall, grad, gleichung in (("V", 1.2269, "(25)"), ("VV", 1.7889, "(23)"),
                                      ("T", 1.1802, "(24)")):
            with self.subTest(fall=fall):
                self.assertAlmostEqual(self.grad("V+T", fall), grad, places=3)
                self.assertTrue(self.urteile[("V+T", fall)].begruendung.startswith(gleichung))
        self.assertEqual(self.urteile[("V+T", "Z")].begruendung, OHNE_EINWIRKUNG)

    def test_knicken_und_kippen(self):
        for fall, grad, begruendung in (("S1", 1.7806, "(29) um z"), ("S2", 2.9467, "(29) um y"),
                                        ("S3", 1.8667, "(38) um y")):
            with self.subTest(fall=fall):
                self.assertAlmostEqual(self.grad("Stab", fall), grad, places=3)
                self.assertTrue(self.urteile[("Stab", fall)].begruendung.startswith(begruendung))

    def test_stossartig_steht_in_der_herleitung(self):
        self.assertIn(r"\eta = \eta_w \cdot \eta_t = 1 \cdot 1.4 = 1.4", self.text)


class TestBrettschichtholz(unittest.TestCase):
    """GL24h 160 × 400 mm in Feuchteklasse 2: k_h und η_w = 0.8."""

    def test_k_h_und_feuchte(self):
        urteile, kennzahlen, text = rechnen(
            "GL24h", rechteck(160, 400), feuchte="2",
            faelle=[("M", {"M_y_Ed": 40}), ("DD", {"N_Ed": -1200, "M_y_Ed": 5})])
        self.assertAlmostEqual(kennzahlen["M_y_Rd"], 56.873, places=2)
        self.assertAlmostEqual(kennzahlen["M_z_Rd"], 21.845, places=2)
        self.assertAlmostEqual(kennzahlen["N_Rd_druck"], -742.4, places=2)
        self.assertAlmostEqual(urteile[("M-N", "M")].erfuellungsgrad.si, 1.4218, places=3)
        druck = urteile[("M-N", "DD")]
        self.assertFalse(druck.erfuellt)
        self.assertAlmostEqual(druck.erfuellungsgrad.si, 0.6187, places=3)
        self.assertIn("k_h", text)


class TestKippen(unittest.TestCase):
    """Ein Rechteck 80 × 400 mm aus C24 unter M_y = 10 kNm -- k_m in beiden Ästen."""

    def test_zwei_abstaende(self):
        urteile, _, _ = rechnen(ecken=rechteck(80, 400), stab=[
            ("weit", {"M_y_Ed": 10, "L_K_y": 0, "L_K_z": 0, "L_D": 8}),
            ("eng", {"M_y_Ed": 10, "L_K_y": 0, "L_K_z": 0, "L_D": 3.5})])
        self.assertAlmostEqual(urteile[("Stab", "weit")].erfuellungsgrad.si, 1.3627, places=3)
        self.assertAlmostEqual(urteile[("Stab", "eng")].erfuellungsgrad.si, 2.4657, places=3)


class TestGrau(unittest.TestCase):
    """Was das Werkzeug beim Holz nicht nachweist, sagt der Fall -- statt einer Zahl."""

    def test_t_ohne_torsion_und_kippen(self):
        """
        Knicken geht auch beim T: um z ist I_z = 140.4 · 10⁶ mm⁴, i_z = 62.45 mm,
        λ_rel = 1.094, k_c = 0.620 -- N_Rd = 0.620 · 12 · 36 000 = 267.8 kN.
        """
        urteile, _, _ = rechnen(ecken=T_QUERSCHNITT, faelle=[("T", {"T_Ed": 2})], stab=[
            ("Kippen", {"M_y_Ed": 20, "L_K_y": 0, "L_K_z": 0, "L_D": 4}),
            ("Knicken", {"N_Ed": -100, "L_K_y": 4, "L_K_z": 4, "L_D": 0})])
        for art, fall, grund in (("V+T", "T", TORSION_NUR_RECHTECK),
                                 ("Stab", "Kippen", KIPPEN_NUR_RECHTECK)):
            with self.subTest(fall=fall):
                u = urteile[(art, fall)]
                self.assertEqual((u.erfuellt, u.erfuellungsgrad.si, u.begruendung),
                                 (False, 0.0, grund))
        self.assertAlmostEqual(urteile[("Stab", "Knicken")].erfuellungsgrad.si, 2.6778, places=3)

    def test_einachsig_ohne_m_z(self):
        """Einachsig zaehlt M_z nicht: (22) mit M_y allein, λ = 0.9023/0.2679 = 3.369."""
        urteile, _, _ = rechnen(faelle=[("D", {"N_Ed": -300, "M_y_Ed": 20, "M_z_Ed": 5})],
                                einachsig=True)
        self.assertAlmostEqual(urteile[("M-N", "D")].erfuellungsgrad.si, 3.3687, places=3)


if __name__ == "__main__":
    unittest.main()
