"""
Tests fuer den Verbundquerschnitt nach SIA 264:2014 (Plan vom 2026-11-25,
Schritt 14a): plastischer Biegewiderstand, Querkraft, ihr Zusammenwirken
und die Klassen.

Von Hand, mit der Flaeche des IPE 300 aus dem Umriss des Werkzeugs, A_a
(die Kennzahlen des Stahls allein, :mod:`tests.test_stahlbau`), und einer
Platte 1500 × 120 mm aus C30/37 direkt auf dem Profil, Oberkante bei
z = 420 mm:

* S355: f_yd = 355/1.05; der Beton traegt 0.85 · 30/1.5 = 17 N/mm², nur
  gedrueckt. Ganz gezogen traegt das Profil N_a = A_a f_yd; die Platte
  braucht dafuer x = N_a/(1500 · 17) = 71.4 mm, weniger als 120 mm. Das
  Moment ist N_a (420 - x/2 - 150), um 426.5 kNm.
* Oben gezogen traegt die Platte nichts: es bleibt der plastische
  Widerstand des Profils allein.
* Ganz gedrueckt waere es A_a f_yd + 1500 · 120 · 17 -- der Steg liegt
  dann aber ueber Klasse 2, c/t = 35.0 > 38ε = 30.9.
* S460: f_yd = 460/1.05, x = 92.5 mm, x/h = 0.220 ueber 0.15: β nach
  Figur 1, 1 - 0.15 (x/h - 0.15)/0.25.
* V_z ueber der Haelfte von V_Rd: der Steg zwischen den Flanschen,
  t_w (h - 2 t_f), traegt mit 1 - ρ, ρ = (V/V_Rd)²; er liegt in der Mitte
  des Profils, das Moment wird N_a' (270 - x'/2).
"""

import unittest

from opencivil.nachweis.qa_verbund import OHNE_TORSION
from opencivil.nachweis.qa_verbund_kennzahlen import verbund_von
from opencivil.querschnitt.bauweise import Bauweise
from opencivil.querschnitt.plastisch import DRUCK, ZUG
from opencivil.verbund import widerstand as vw
from tests.test_stahlbau import kennzahlen, rechteck
from tests.test_stahlprofile_qa import analyse, projekt

#: Die Fliessgrenzen mit γ_a = γ_M1 = 1.05, in N/mm².
F_355 = 355.0 / 1.05
F_460 = 460.0 / 1.05

#: 0.85 f_cd von C30/37, in N/mm².
BETON = 0.85 * 30.0 / 1.5

#: Die Platte 1500 × 120 mm auf dem IPE 300, Oberkante bei z = 420 mm.
PLATTE = (rechteck(-750, 300, 1500, 120), "b1")
IPE = (0, 150, "IPE 300", {})

#: So weit darf die Rechnung von der Hand abweichen.
GENAU = 1e-4


def stahl_allein(profil=IPE):
    """Die Kennzahlen des Profils ohne Beton, in kN und kNm."""
    k, _, _ = kennzahlen(profil)
    return k


def rechnen(*profile, faelle=None, polygone=(PLATTE,), stahl="S355", betonstahl=None,
            einachsig=True):
    """
    Kennzahlen und Urteile je (Art, Lastfall) einer Analyse im Verbund --
    ``stahl`` die Sorte der Profile, ``betonstahl`` ein Stab je (y, z, Sorte)
    --, dazu Aufbau und Analyse.
    """
    p = projekt()
    if stahl != "S355":
        p.baustahl(stahl)
    a = analyse(p, *(profile or (IPE,)), polygone=polygone)
    if stahl != "S355":
        for profil in a.profile:
            profil.stahl = "st2"
    for y, z, sorte in betonstahl or ():
        if sorte != "B500B":
            p.stahl(sorte)
        a.stab(y, z, durchmesser=20, stahl="s1" if sorte == "B500B" else "s2")
    a.einachsig = einachsig
    for name, werte in (faelle or {}).items():
        a.lastfall(name, **werte)
    aufbau = p.aufbauen()
    teil = aufbau.teile[a.kennung]
    loesung = aufbau.werk.loese(*teil.ziele())
    werte = {}
    for k in teil.kennzahlen:
        w = loesung.wert(k.definition.id)
        werte[k.definition.id.rsplit(".", 1)[1]] = w.in_einheit(w.einheit)
    return werte, {(u.art, u.fall): u for u in loesung.urteile}, aufbau, a


def grad(urteil):
    return urteil.erfuellungsgrad.si


class TestTraeger(unittest.TestCase):
    """IPE 300 aus S355 unter der Platte: plastisch, von Hand."""

    @classmethod
    def setUpClass(cls):
        cls.stahl = stahl_allein()
        cls.A_a = cls.stahl["N_Rd_zug"] * 1e3 / F_355
        cls.k, cls.urteile, cls.aufbau, cls.a = rechnen(faelle={
            "Feld": {"M_y_Ed": 300.0},
            "Stütze": {"M_y_Ed": -150.0},
            "Zug": {"N_Ed": 500.0, "T_Ed": 2.0},
            "Druck": {"N_Ed": -2000.0},
            "jenseits": {"N_Ed": -9000.0, "M_y_Ed": 10.0},
        })

    def test_die_bauweise(self):
        teil = self.aufbau.teile[self.a.kennung]
        self.assertEqual((teil.objekt.bauweise, teil.ohne_nachweis), (Bauweise.VERBUND, ""))

    def test_positives_moment_mit_der_nulllinie_in_der_platte(self):
        N_a = self.A_a * F_355
        x = N_a / (1500.0 * BETON)
        self.assertLess(x, 120.0)
        M = N_a * (420.0 - x / 2.0 - 150.0) / 1e6
        self.assertAlmostEqual(self.k["M_Rd_unten"], M, delta=1e-3)
        self.assertAlmostEqual(grad(self.urteile["M-N", "Feld"]), M / 300.0, delta=GENAU)

    def test_negatives_moment_traegt_das_profil_allein(self):
        self.assertAlmostEqual(self.k["M_Rd_oben"], self.stahl["M_Rd_oben"], delta=1e-3)
        self.assertAlmostEqual(grad(self.urteile["M-N", "Stütze"]),
                               -self.stahl["M_Rd_oben"] / 150.0, delta=GENAU)

    def test_zug_ohne_beton(self):
        self.assertAlmostEqual(self.k["N_Rd_zug"], self.stahl["N_Rd_zug"], delta=1e-3)
        self.assertAlmostEqual(grad(self.urteile["M-N", "Zug"]),
                               self.stahl["N_Rd_zug"] / 500.0, delta=GENAU)

    def test_druck_ueber_klasse_2_grau(self):
        self.assertEqual(self.k["N_Rd_druck"], 0.0)
        u = self.urteile["M-N", "Druck"]
        self.assertEqual((u.erfuellt, u.hinweis), (False, vw.UEBER_KLASSE_2))

    def test_jenseits_des_widerstands(self):
        N_pl = self.A_a * F_355 + 1500.0 * 120.0 * BETON
        u = self.urteile["M-N", "jenseits"]
        self.assertFalse(u.erfuellt)
        self.assertAlmostEqual(grad(u), N_pl / 9e6, delta=GENAU)

    def test_querkraft_traegt_der_stahl_allein(self):
        self.assertAlmostEqual(self.k["V_z_Rd"], self.stahl["V_z_Rd"], delta=1e-3)

    def test_torsion_nur_ein_hinweis(self):
        self.assertIn(OHNE_TORSION, " ".join(w.text for w in self.aufbau.warnungen))


class TestQuerkraft(unittest.TestCase):
    """Ueber der Haelfte von V_Rd traegt der Steg mit 1 - ρ -- wie im Stahl."""

    def test_der_steg_verliert(self):
        stahl = stahl_allein()
        A_a = stahl["N_Rd_zug"] * 1e3 / F_355
        V_Rd = stahl["V_z_Rd"]
        _, urteile, _, _ = rechnen(faelle={"LF": {"M_y_Ed": 300.0, "V_z_Ed": 400.0}})
        rho = (400.0 / V_Rd) ** 2
        N_a = (A_a - rho * 7.1 * (300.0 - 2 * 10.7)) * F_355
        x = N_a / (1500.0 * BETON)
        M = N_a * (270.0 - x / 2.0) / 1e6
        self.assertAlmostEqual(grad(urteile["M-N", "LF"]), M / 300.0, delta=GENAU)
        self.assertAlmostEqual(grad(urteile["V", "LF"]), V_Rd / 400.0, delta=GENAU)


class TestBeta(unittest.TestCase):
    """S460: β nach Figur 1, sobald x_p/h ueber 0.15 liegt."""

    def test_von_hand(self):
        A_a = stahl_allein()["N_Rd_zug"] * 1e3 / F_355
        k, urteile, _, _ = rechnen(stahl="S460", faelle={"Feld": {"M_y_Ed": 400.0}})
        N_a = A_a * F_460
        x = N_a / (1500.0 * BETON)
        beta = 1.0 - 0.15 * (x / 420.0 - 0.15) / 0.25
        self.assertGreater(x / 420.0, 0.15)
        M = beta * N_a * (420.0 - x / 2.0 - 150.0) / 1e6
        self.assertAlmostEqual(k["M_Rd_unten"], M, delta=1e-3)
        self.assertAlmostEqual(grad(urteile["M-N", "Feld"]), M / 400.0, delta=GENAU)

    def test_figur_1_endet_bei_0_4(self):
        self.assertEqual(vw.Beta(100.0, 400.0).beta, 1.0 - 0.15 * 0.1 / 0.25)
        self.assertEqual(vw.Beta(50.0, 400.0).beta, 1.0)
        self.assertIsNone(vw.Beta(170.0, 400.0).beta)

    def test_tiefe_druckzone_grau(self):
        _, urteile, _, _ = rechnen(stahl="S460", faelle={"LF": {"N_Ed": -3000.0, "M_y_Ed": 100.0}})
        u = urteile["M-N", "LF"]
        self.assertEqual((u.erfuellt, u.hinweis), (False, vw.UEBER_FIGUR_1))


class TestBetonstahl(unittest.TestCase):
    """Gezogener Betonstahl muss in Klasse B oder C sein (5.1.2.3)."""

    def test_b500a_gezogen_grau(self):
        k, urteile, _, _ = rechnen(betonstahl=[(0, 380, "B500A")],
                                   faelle={"Stütze": {"M_y_Ed": -100.0},
                                           "Feld": {"M_y_Ed": 100.0}})
        u = urteile["M-N", "Stütze"]
        self.assertFalse(u.erfuellt)
        self.assertIn("B500A", u.hinweis)
        self.assertEqual(k["M_Rd_oben"], 0.0)
        self.assertTrue(urteile["M-N", "Feld"].erfuellt)

    def test_b500b_gezogen_traegt_mit(self):
        stahl = stahl_allein()
        k, _, _, _ = rechnen(betonstahl=[(0, 380, "B500B")])
        self.assertLess(k["M_Rd_oben"], stahl["M_Rd_oben"])


class TestKammerbeton(unittest.TestCase):
    """Beton im I-Profil: Flansche innen, Steg beidseits -- Tabelle 3 und 5.2.1.3."""

    def bleche(self, polygone):
        p = projekt()
        a = analyse(p, (0, 150, "HEB 300", {}), polygone=polygone)
        teil = p.aufbauen().teile[a.kennung]
        verbund = verbund_von(teil.objekt)
        stahl = verbund.stahl.teile[0]
        return {b.name: verbund.kammerbetoniert(stahl, b) for b in stahl.bleche}

    def test_ganz_eingebettet(self):
        bleche = self.bleche([(rechteck(-150, 0, 300, 300), "b1")])
        self.assertTrue(all(bleche.values()), bleche)

    def test_nur_eine_platte_darueber(self):
        bleche = self.bleche([(rechteck(-750, 300, 1500, 120), "b1")])
        self.assertFalse(any(bleche.values()), bleche)

    def test_hebt_den_flansch_in_klasse_2(self):
        """HEA 300 aus S460: c/t = 8.5 liegt ueber 10ε = 7.2, aber unter 14ε = 10.0."""
        hea = (0, 145, "HEA 300", {})
        kammer = [(-150, 0), (150, 0), (150, 290), (750, 290), (750, 410), (-750, 410),
                  (-750, 290), (-150, 290)]
        nur_platte = (rechteck(-750, 290, 1500, 120), "b1")
        ohne, _, _, _ = rechnen(hea, polygone=[nur_platte], stahl="S460")
        mit, _, aufbau, a = rechnen(hea, polygone=[(kammer, "b1")], stahl="S460")
        self.assertEqual(ohne["N_Rd_druck"], 0.0)
        A_a = stahl_allein(hea)["N_Rd_zug"] * 1e3 / F_355
        N = -(A_a * F_460 + (300 * 290 + 1500 * 120 - A_a) * BETON) / 1e3
        self.assertAlmostEqual(mit["N_Rd_druck"], N, delta=1e-2)
        verbund = verbund_von(aufbau.teile[a.kennung].objekt)
        quellen = {z.blech.name: z.tabelle for z in verbund.zustaende(DRUCK, [0.715] * 3)}
        self.assertEqual(quellen["Steg"], "SIA 264, 5.2.1.3")
        self.assertTrue(all(q == "SIA 264, Tabelle 3" for b, q in quellen.items() if b != "Steg"))

    def test_im_zug_keine_quelle(self):
        p = projekt()
        a = analyse(p, (0, 150, "HEB 300", {}), polygone=[(rechteck(-150, 0, 300, 300), "b1")])
        verbund = verbund_von(p.aufbauen().teile[a.kennung].objekt)
        self.assertTrue(all(z.tabelle == "" for z in verbund.zustaende(ZUG, [0.814] * 3)))


if __name__ == "__main__":
    unittest.main()
