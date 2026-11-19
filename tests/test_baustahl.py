"""Tests fuer Baustahl nach SIA 263:2013 -- und fuer die Liste der Materialarten."""

import math
import unittest

from opencivil.core.einheiten import EINHEITSLOS, KG_PRO_M3, N_PRO_MM2, PROMILLE, Groesse
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.arten import MATERIALARTEN
from opencivil.material.basis import Baustoffart
from opencivil.material.baustahl import BAUSTAHLSORTEN, baustahl, baustahlsorten_zum_anlegen
from opencivil.projekt.lesen import ProjektFehler
from opencivil.projekt.projekt import Projekt
from tests.unfertig import meldung


def werte(stoff, *kurznamen):
    werk = Rechenwerk()
    stoff.ins_rechenwerk(werk)
    loesung = werk.loese_alles()
    return {k: loesung.groesse(stoff.id_von(k)) for k in kurznamen}


class TestSortentabelle(unittest.TestCase):
    """SIA 263:2013, Tabelle 1 -- abgeschrieben am 2026-11-15."""

    TABELLE = {
        #        f_y  tau_y f_u   über 40 mm
        "S235": (235, 135, 360, 215, 124, 340),
        "S275": (275, 160, 430, 255, 147, 410),
        "S355": (355, 205, 510, 335, 193, 490),
        "S460": (460, 265, 550, 430, 248, 530),
    }

    def test_jede_zahl_der_tabelle(self):
        self.assertEqual(list(BAUSTAHLSORTEN), list(self.TABELLE))
        for sorte, zeile in self.TABELLE.items():
            with self.subTest(sorte=sorte):
                w = werte(baustahl(sorte), "f_y", "tau_y", "f_u",
                          "f_y_dick", "tau_y_dick", "f_u_dick")
                self.assertEqual(tuple(round(g.in_einheit(N_PRO_MM2)) for g in w.values()), zeile)

    def test_schubfliessgrenze_ist_f_y_durch_wurzel_drei(self):
        """
        Eine Probe gegen Abschreibfehler: die Spalte tau_y ist f_y/√3, gerundet
        -- bis 40 mm auf 5 N/mm², darueber auf 1 N/mm².
        """
        for sorte, s in BAUSTAHLSORTEN.items():
            with self.subTest(sorte=sorte):
                self.assertLess(abs(s.tau_y - s.f_y / math.sqrt(3)), 2.5)
                self.assertLess(abs(s.tau_y_dick - s.f_y_dick / math.sqrt(3)), 0.5)

    def test_dick_ist_schwaecher(self):
        for sorte, s in BAUSTAHLSORTEN.items():
            with self.subTest(sorte=sorte):
                self.assertLess(s.f_y_dick, s.f_y)
                self.assertLess(s.f_u_dick, s.f_u)

    def test_neue_der_reihe_nach_ab_s235(self):
        self.assertEqual(baustahlsorten_zum_anlegen(), ["S235", "S275", "S355", "S460"])


class TestKennwerte(unittest.TestCase):
    def setUp(self):
        self.w = werte(baustahl("S355"), "E_a", "G_a", "nu_a", "rho_a",
                       "gamma_M1", "gamma_M2", "eps_y")

    def test_normvorgaben(self):
        """SIA 263:2013, 3.2.2.1 und 4.1.3."""
        self.assertEqual(self.w["E_a"].in_einheit(N_PRO_MM2), 210000)
        self.assertEqual(self.w["G_a"].in_einheit(N_PRO_MM2), 81000)
        self.assertEqual(self.w["nu_a"].in_einheit(EINHEITSLOS), 0.3)
        self.assertEqual(self.w["rho_a"].in_einheit(KG_PRO_M3), 7850)
        self.assertEqual(self.w["gamma_M1"].in_einheit(EINHEITSLOS), 1.05)
        self.assertEqual(self.w["gamma_M2"].in_einheit(EINHEITSLOS), 1.25)

    def test_schubmodul_passt_zur_querdehnung(self):
        """G = E/(2(1+ν)) = 80.8 kN/mm² -- die Norm rundet auf 81."""
        E, nu = self.w["E_a"].in_einheit(N_PRO_MM2), self.w["nu_a"].in_einheit(EINHEITSLOS)
        self.assertAlmostEqual(E / (2 * (1 + nu)) / 1000, 81, delta=0.5)

    def test_fliessdehnung(self):
        self.assertAlmostEqual(self.w["eps_y"].in_einheit(PROMILLE), 355 / 210000 * 1000)

    def test_abweichende_streckgrenze(self):
        eigen = baustahl("S355", abweichungen={"f_y": Groesse(300, N_PRO_MM2)})
        eps = werte(eigen, "eps_y")["eps_y"]
        self.assertAlmostEqual(eps.in_einheit(PROMILLE), 300 / 210000 * 1000)

    def test_unbekannte_sorte(self):
        with self.assertRaises(ValueError):
            baustahl("S500")


class TestImProjekt(unittest.TestCase):
    def test_normsorte_und_eigener(self):
        p = Projekt(name="Stahl")
        norm = p.baustahl("S355")
        eigen = p.eigener_baustahl("S460")
        self.assertEqual((norm.kennung, norm.name), ("st1", "S355"))
        self.assertEqual((eigen.kennung, eigen.name), ("st2", "ST1"))
        self.assertEqual(p.eigener_baustahl().name, "ST2")

    def test_rechnet_und_heisst_wie_die_sorte(self):
        p = Projekt(name="Stahl")
        p.baustahl("S275")
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.materialziele())
        self.assertEqual(loesung.groesse("baustahl.st1.f_y").in_einheit(N_PRO_MM2), 275)
        self.assertEqual(aufbau.baustoffe["st1"].art, Baustoffart.BAUSTAHL)

    def test_speichern_und_laden(self):
        p = Projekt(name="Stahl")
        p.eigener_baustahl("S235").abweichungen = {"f_y": 240.0}
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.materialien[0].art, Baustoffart.BAUSTAHL)
        aufbau = wieder.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.materialziele())
        self.assertEqual(loesung.groesse("baustahl.st1.f_y").in_einheit(N_PRO_MM2), 240)

    def test_unbekannte_sorte(self):
        with self.assertRaises(ProjektFehler):
            Projekt(name="Stahl").baustahl("S500")

    def test_normsorte_nur_einmal(self):
        p = Projekt(name="Stahl")
        p.baustahl("S355")
        with self.assertRaises(ProjektFehler):
            p.baustahl("S355")

    def test_kein_beton_wo_einer_verlangt_ist(self):
        p = Projekt(name="Stahl")
        stahl = p.baustahl("S355")
        p.platte("Decke", beton=stahl.kennung, stahl=p.stahl("B500B").kennung)
        self.assertEqual(meldung(p), "Platte 'Decke': Beton: «S355» ist kein Beton.")


class TestMaterialarten(unittest.TestCase):
    """Jede Art steht in der einen Liste, mit eigenen Vorsilben."""

    def test_jede_art_genau_einmal(self):
        self.assertEqual(list(MATERIALARTEN), [a.value for a in Baustoffart])

    def test_vorsilben_verschieden(self):
        for feld in ("kennung", "eigene"):
            with self.subTest(feld=feld):
                vorsilben = [getattr(a, feld) for a in MATERIALARTEN.values()]
                self.assertEqual(len(set(vorsilben)), len(vorsilben))

    def test_anlegen_bietet_jede_sorte_einmal(self):
        for name, art in MATERIALARTEN.items():
            with self.subTest(art=name):
                self.assertEqual(sorted(art.anlegen), sorted(art.sorten))

    def test_bauen_gibt_die_art(self):
        for name, art in MATERIALARTEN.items():
            with self.subTest(art=name):
                self.assertEqual(art.bauen(art.anlegen[0]).art, art.art)


if __name__ == "__main__":
    unittest.main()
