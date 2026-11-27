"""Tests fuer den Profilblechstahl nach SIA 264:2014 -- das Material, nicht das Blech."""

import unittest

from opencivil.core.einheiten import EINHEITSLOS, N_PRO_MM2, PROMILLE, Groesse
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.arten import MATERIALARTEN
from opencivil.material.basis import Baustoffart
from opencivil.material.baustahl import DUKTILITAET
from opencivil.material.profilblech import (
    PROFILBLECHSORTEN, profilblech, profilblechsorten_zum_anlegen,
)
from opencivil.projekt.lesen import ProjektFehler
from opencivil.projekt.projekt import Projekt
from opencivil.querschnitt.werkstoffgesetz import Profilblechgesetz
from opencivil.web import dienst


def werte(stoff, *kurznamen):
    werk = Rechenwerk()
    stoff.ins_rechenwerk(werk)
    loesung = werk.loese_alles()
    return {k: loesung.groesse(stoff.id_von(k)) for k in kurznamen}


class TestSortentabelle(unittest.TestCase):
    """SIA 264:2014, 3.3.1, Tabelle 1 -- am 2026-11-27 am Seitenbild abgeschrieben."""

    TABELLE = {
        #           f_yp  f_u
        "SE 220 G": (220, 300),
        "SE 250 G": (250, 330),
        "SE 280 G": (280, 360),
        "SE 320 G": (320, 390),
        "SE 350 G": (350, 420),
        "SE 550 G": (550, 560),
    }

    def test_jede_zahl_der_tabelle(self):
        self.assertEqual(list(PROFILBLECHSORTEN), list(self.TABELLE))
        for sorte, zeile in self.TABELLE.items():
            with self.subTest(sorte=sorte):
                w = werte(profilblech(sorte), "f_yp", "f_u")
                self.assertEqual(tuple(round(g.in_einheit(N_PRO_MM2)) for g in w.values()), zeile)

    def test_zugfestigkeit_ueber_der_streckgrenze(self):
        for sorte, s in PROFILBLECHSORTEN.items():
            with self.subTest(sorte=sorte):
                self.assertLess(s.f_yp, s.f_u)

    def test_neue_ab_se_350_g(self):
        """Die übliche Sorte zuerst, dann die Tabelle in ihrer Folge."""
        self.assertEqual(profilblechsorten_zum_anlegen(),
                         ["SE 350 G", "SE 220 G", "SE 250 G", "SE 280 G", "SE 320 G", "SE 550 G"])


class TestKennwerte(unittest.TestCase):
    def setUp(self):
        self.w = werte(profilblech("SE 350 G"), "E_a", "gamma_ap", "eps_yp", "f_ypd", "eps_ud")

    def test_normvorgaben(self):
        """E_a nach SIA 264, 3.1.1 aus SIA 263, 3.2.2.1; γ_ap nach 4.1.5."""
        self.assertEqual(self.w["E_a"].in_einheit(N_PRO_MM2), 210000)
        self.assertEqual(self.w["gamma_ap"].in_einheit(EINHEITSLOS), 1.05)

    def test_bemessungswert(self):
        """f_ypd = f_yp/γ_ap = 350/1.05 = 333.3 N/mm² (4.1.3, (1))."""
        self.assertAlmostEqual(self.w["f_ypd"].in_einheit(N_PRO_MM2), 350 / 1.05)

    def test_dehnungen(self):
        """ε_yp = 350/210000 = 1.67 ‰; die Grenzdehnung 15-mal so gross, 25 ‰."""
        self.assertAlmostEqual(self.w["eps_yp"].in_einheit(PROMILLE), 350 / 210000 * 1000)
        self.assertEqual(DUKTILITAET, 15)
        self.assertAlmostEqual(self.w["eps_ud"].in_einheit(PROMILLE), 15 * 350 / 210000 * 1000)

    def test_eigene_streckgrenze_zieht_mit(self):
        eigen = profilblech("SE 350 G", abweichungen={"f_yp": Groesse(300, N_PRO_MM2)})
        w = werte(eigen, "f_ypd", "eps_ud")
        self.assertAlmostEqual(w["f_ypd"].in_einheit(N_PRO_MM2), 300 / 1.05)
        self.assertAlmostEqual(w["eps_ud"].in_einheit(PROMILLE), 15 * 300 / 210000 * 1000)

    def test_unbekannte_sorte(self):
        with self.assertRaisesRegex(ValueError, "Verfügbar: SE 220 G, "):
            profilblech("SE 390 G")


class TestGesetz(unittest.TestCase):
    def test_elastisch_ideal_plastisch(self):
        """In Zug und Druck gleich; jenseits der Grenzdehnung trägt er nichts."""
        g = Profilblechgesetz.gleich(E_a=210e9, f_yd=333e6, eps_ud=0.025)
        self.assertAlmostEqual(g.spannung(0.001), 210e6)
        self.assertAlmostEqual(g.spannung(-0.001), -210e6)
        self.assertEqual(g.spannung(0.02), 333e6)
        self.assertEqual(g.spannung(-0.02), -333e6)
        self.assertEqual(g.spannung(0.03), 0.0)

    def test_das_bild(self):
        p = Projekt(name="Blech")
        p.profilblech("SE 350 G")
        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        self.assertEqual(antwort.status, 200)
        kurve = antwort.daten["werkstoffgesetze"]["pb1"]
        self.assertEqual((kurve["titel"], kurve["name"], kurve["art"]),
                         ("Profilblechstahl – elastisch-plastisch", "SE 350 G", "profilblech"))
        self.assertEqual(kurve["referenz"], Profilblechgesetz.REFERENZ)
        ecken = [(round(q["eps"], 2), round(q["sigma"], 1)) for q in kurve["punkte"]]
        self.assertEqual(ecken, [(-25.0, -333.3), (-1.59, -333.3), (0.0, 0.0),
                                 (1.59, 333.3), (25.0, 333.3)])
        self.assertEqual([m["text"] for m in kurve["marken"]], ["ε_ypd", "ε_ud"])


class TestImProjekt(unittest.TestCase):
    def test_normsorte_und_eigener(self):
        p = Projekt(name="Blech")
        norm = p.profilblech("SE 320 G")
        eigen = p.material_anlegen("profilblech", "SE 350 G", eigen=True)
        self.assertEqual((norm.kennung, norm.name), ("pb1", "SE 320 G"))
        self.assertEqual((eigen.kennung, eigen.name), ("pb2", "PB1"))

    def test_rechnet_und_heisst_wie_die_sorte(self):
        p = Projekt(name="Blech")
        p.profilblech("SE 280 G")
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.materialziele())
        self.assertEqual(loesung.groesse("profilblech.pb1.f_yp").in_einheit(N_PRO_MM2), 280)
        self.assertEqual(aufbau.baustoffe["pb1"].art, Baustoffart.PROFILBLECH)

    def test_speichern_und_laden(self):
        p = Projekt(name="Blech")
        p.material_anlegen("profilblech", "SE 320 G", eigen=True).abweichungen = {"f_yp": 300.0}
        wieder = Projekt.aus_dict(p.als_dict())
        aufbau = wieder.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.materialziele())
        self.assertEqual(loesung.groesse("profilblech.pb1.f_yp").in_einheit(N_PRO_MM2), 300)

    def test_unbekannte_sorte(self):
        with self.assertRaises(ProjektFehler):
            Projekt(name="Blech").profilblech("SE 390 G")

    def test_maennlich(self):
        art = MATERIALARTEN["profilblech"]
        self.assertEqual((art.neu, art.einen), ("Neuer Profilblechstahl", "einen Profilblechstahl"))


if __name__ == "__main__":
    unittest.main()
