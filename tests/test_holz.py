"""
Tests fuer Holz nach SIA 265:2012 -- Sorten, Kennwerte, Gesetz, Bild und
Holz als Material eines Stabs.

Von Hand, C24 (Tabelle 6): f_t,0,d = 8, f_c,0,d = 12, E_0,mean = 11 000
N/mm² -- bricht auf Zug bei 8/11 000 = 0.727 ‰, erreicht auf Druck die
Festigkeit bei 12/11 000 = 1.091 ‰, elastisch-plastisch bis 3 · 1.091 =
3.273 ‰. Ein Balken 300 × 600 mm aus GL24h: EI = 11 000 N/mm² · 300 · 600³
/ 12 mm⁴, Eigengewicht 500 kg/m³ · 10 m/s² · 0.18 m² = 900 N/m.
"""

import unittest

from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.arten import MATERIALARTEN
from opencivil.material.holz import HOLZSORTEN, STAUCHBARKEIT, Holzart, holz, holzsorten_zum_anlegen
from opencivil.querschnitt.werkstoffgesetz import Holzgesetz, HolzPlastisch
from opencivil.stabwerk3d.rechnung import RAUMKENNWERTE
from opencivil.web import dienst
from opencivil.web.api import katalog
from tests.traeger import traeger

MPA = 1e6


def werte(sorte, *kurznamen):
    """Die Kennwerte einer Sorte, in N/mm², kg/m³ oder ‰ wie im Material."""
    stoff = holz(sorte)
    werk = Rechenwerk()
    stoff.ins_rechenwerk(werk)
    loesung = werk.loese_alles()
    return tuple(round(loesung.groesse(stoff.id_von(k)).zahl, 9) for k in kurznamen)


class TestTabellen(unittest.TestCase):
    """SIA 265:2012, Tabellen 6 und 7 -- am 2026-11-26 vom Seitenbild abgeschrieben."""

    def test_die_sorten_in_der_folge_der_tabellen(self):
        self.assertEqual(list(HOLZSORTEN), ["C16", "C24", "C30", "D30", "GL24k", "GL24h", "GL28k",
                                            "GL28h", "GL32k", "GL32h", "GL36k", "GL36h"])
        self.assertEqual(holzsorten_zum_anlegen()[:2], ["C24", "C16"])
        arten = {name: s.art for name, s in HOLZSORTEN.items()}
        self.assertEqual([n for n, a in arten.items() if a is Holzart.NADELHOLZ], ["C16", "C24", "C30"])
        self.assertEqual([n for n, a in arten.items() if a is Holzart.LAUBHOLZ], ["D30"])
        self.assertEqual(len([a for a in arten.values() if a is Holzart.BRETTSCHICHTHOLZ]), 8)

    def test_c24_die_hervorgehobene_spalte_der_tabelle_6(self):
        self.assertEqual(
            werte("C24", "f_m_k", "E_0_mean", "rho_k", "f_m_d", "f_t_0_d", "f_c_0_d", "f_t_90_d",
                  "f_c_90_d", "f_v_d", "E_90_mean", "G_mean"),
            (24, 11000, 350, 14, 8, 12, 0.1, 1.8, 1.5, 300, 500))

    def test_gl24h_die_hervorgehobene_spalte_der_tabelle_7(self):
        self.assertEqual(
            werte("GL24h", "f_m_k", "E_0_mean", "rho_k", "f_m_d", "f_t_0_d", "f_c_0_d",
                  "f_t_90_d", "f_c_90_d", "f_v_d", "E_90_mean", "G_mean"),
            (24, 11000, 380, 16, 12, 14.5, 0.15, 1.9, 1.8, 300, 500))

    def test_laubholz_und_hochwertiges_brettschichtholz(self):
        self.assertEqual(werte("D30", "f_m_d", "f_t_90_d", "f_c_90_d", "f_v_d", "E_90_mean",
                               "G_mean"), (17, 0.2, 5.3, 2, 600, 1000))
        self.assertEqual(werte("GL36h", "f_m_d", "f_t_0_d", "f_c_0_d", "E_0_mean", "rho_k",
                               "G_mean"), (24, 18, 20.5, 14000, 450, 600))

    def test_beiwert_und_dichte_je_holzart(self):
        """γ_M/η_M nach Tabelle 1; die Dichte aus SIA 261:2020, Tabelle 28, durch g = 10 m/s²."""
        self.assertEqual(werte("C30", "gamma_M_eta_M", "rho_mean"), (1.7, 500))
        self.assertEqual(werte("D30", "gamma_M_eta_M", "rho_mean"), (1.7, 750))
        self.assertEqual(werte("GL28k", "gamma_M_eta_M", "rho_mean"), (1.5, 500))

    def test_die_dehnungen_von_hand(self):
        eps_t, eps_c, eps_cu = werte("C24", "eps_t_0_d", "eps_c_0_d", "eps_cu")
        self.assertAlmostEqual(eps_t, 8 / 11000 * 1000, places=9)
        self.assertAlmostEqual(eps_c, 12 / 11000 * 1000, places=9)
        self.assertAlmostEqual(eps_cu, STAUCHBARKEIT * 12 / 11000 * 1000, places=9)
        self.assertEqual(STAUCHBARKEIT, 3.0)

    def test_unbekannte_sorte(self):
        with self.assertRaisesRegex(ValueError, "Unbekannte Holzsorte 'C40'"):
            holz("C40")


class TestGesetz(unittest.TestCase):
    """C24: linear bis zum Bruch, oder auf Druck elastisch-plastisch."""

    linear = Holzgesetz(E=11000 * MPA, f_t=8 * MPA, f_c=12 * MPA)
    plastisch = HolzPlastisch(E=11000 * MPA, f_t=8 * MPA, f_c=12 * MPA,
                              eps_cu=STAUCHBARKEIT * 12 / 11000)

    def test_linear_bis_zum_bruch(self):
        g = self.linear
        self.assertAlmostEqual(g(0.0005) / MPA, 5.5)
        self.assertAlmostEqual(g(-0.001) / MPA, -11.0)
        self.assertAlmostEqual(g(8 / 11000) / MPA, 8.0)          # auf der Grenze gilt es
        self.assertAlmostEqual(g(-12 / 11000) / MPA, -12.0)
        self.assertEqual(g(0.00073), 0.0)                         # gebrochen
        self.assertEqual(g(-0.0011), 0.0)

    def test_auf_druck_elastisch_plastisch(self):
        g = self.plastisch
        self.assertAlmostEqual(g(-0.001) / MPA, -11.0)
        self.assertAlmostEqual(g(-0.002) / MPA, -12.0)
        self.assertAlmostEqual(g(-3 * 12 / 11000) / MPA, -12.0)
        self.assertEqual(g(-0.0033), 0.0)
        self.assertEqual(g(0.00073), 0.0)                         # Zug bricht wie linear

    def test_die_formeln(self):
        self.assertIn(r"-\frac{f_{c,0,d}}{E_{0,mean}} \le \varepsilon", self.linear.latex())
        self.assertIn(r"\max(E_{0,mean}\,\varepsilon;\ -f_{c,0,d})", self.plastisch.latex())
        self.assertEqual(self.plastisch.ROLLEN, ("f_t", "f_c", "E", "eps_cu"))


class TestBild(unittest.TestCase):
    """Das Bild im Material: die Linie und die zweite, auf Druck elastisch-plastisch."""

    def test_c24(self):
        p = traeger()
        p.holz("C24")
        gesetz = dienst.rechnen({"projekt": p.als_dict()})["werkstoffgesetze"]["h1"]
        self.assertEqual((gesetz["name"], gesetz["art"]), ("C24", "holz"))
        punkte = [(round(q["eps"], 3), q["sigma"]) for q in gesetz["punkte"]]
        self.assertEqual(punkte, [(-1.091, -12.0), (0.0, 0.0), (0.727, 8.0)])
        zweite = [(round(q["eps"], 3), q["sigma"]) for q in gesetz["zweite"]["punkte"]]
        self.assertEqual(zweite, [(-3.273, -12.0), (-1.091, -12.0), (0.0, 0.0), (0.727, 8.0)])
        self.assertIn("3.27 ‰", gesetz["zweite"]["beschreibung"])
        self.assertIn("nach Vorgabe", gesetz["zweite"]["beschreibung"])


class TestRegister(unittest.TestCase):
    def test_wie_ein_satz_die_art_nennt(self):
        """Bis 2026-11-26 stand «Neuer» und «keinen» fest im Text: «Neuer Holz»."""
        arten = katalog()["materialarten"]
        self.assertEqual([arten["holz"][k] for k in ("titel", "neu", "eigen", "keinen")],
                         ["Holz", "Neues Holz", "Eigenes Holz", "kein Holz"])
        self.assertEqual([arten["baustahl"][k] for k in ("neu", "eigen", "keinen")],
                         ["Neuer Baustahl", "Eigener Baustahl", "keinen Baustahl"])
        self.assertEqual((MATERIALARTEN["holz"].kennung, MATERIALARTEN["holz"].eigene), ("h", "H"))
        self.assertEqual(MATERIALARTEN["holz"].einen, "ein Holz")


class TestStab(unittest.TestCase):
    """Holz als Material eines Stabs: E_0,mean, die Dichte nach SIA 261 und im Raum G_mean."""

    def test_ein_balken_aus_brettschichtholz(self):
        p = traeger()
        p.holz("GL24h")
        s = p.balkensysteme[0]
        s.lastfaelle[0].eigengewicht = True
        s.linien[0].material = s.holz("h1").kennung
        e = p.rechnen()
        EI = 11000e6 * 0.3 * 0.6 ** 3 / 12
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q1.M2.EI").groesse.si, EI, delta=1e-9 * EI)
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q1.M2.g_k").groesse.si, 900.0, delta=1e-9)
        self.assertEqual(p.verweise("h1"), [s])

    def test_ein_geloeschtes_holz_sagt_es_am_stab(self):
        p = traeger()
        s = p.balkensysteme[0]
        s.linien[0].material = s.holz("h7").kennung
        meldungen = [m.text for m in p.rechnen().balkensystem("r1").ergebnis.meldungen if m.haelt_an]
        self.assertEqual(meldungen, ["L1 nimmt ein Holz des Projekts, aber das gewählte Material "
                                     "gibt es nicht mehr – eines wählen."])

    def test_im_raum_der_schubmodul(self):
        self.assertEqual(RAUMKENNWERTE["holz"], {"E": "E_0_mean", "rho": "rho_mean", "G": "G_mean"})


if __name__ == "__main__":
    unittest.main()
