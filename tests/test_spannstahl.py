"""Tests fuer Spannstahl nach SIA 262:2025 -- Sorten, Erzeugnisse, Kennwerte, Gesetz und Bild."""

import unittest

from opencivil.core.einheiten import N_PRO_MM2, PROZENT, Groesse
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.basis import Baustoffart
from opencivil.material.spannstahl import (
    SPANNSTAHLSORTEN, Erzeugnisart, spannstahl, spannstahlsorten_zum_anlegen,
)
from opencivil.projekt.projekt import Projekt
from opencivil.querschnitt.werkstoffgesetz import Spannstahlgesetz
from opencivil.web import dienst


def werte(stoff, *kurznamen):
    werk = Rechenwerk()
    stoff.ins_rechenwerk(werk)
    loesung = werk.loese_alles()
    return {k: loesung.groesse(stoff.id_von(k)) for k in kurznamen}


class TestTabellen(unittest.TestCase):
    """SIA 262:2025, Tabelle 7 und Tabelle 10 -- abgeschrieben am 2026-11-26."""

    #: Tabelle 7, Zeile fuer Zeile: Erzeugnis, ⌀, A_p, f_pk, f_p0.1k, Bezeichnung.
    TABELLE_7 = [
        ("draht", 3.0, 7.1, 1860, 1600, "Y1860C-3.0"),
        ("draht", 4.0, 12.6, 1860, 1600, "Y1860C-4.0"),
        ("draht", 5.0, 19.6, 1860, 1600, "Y1860C-5.0"),
        ("draht", 6.0, 28.3, 1770, 1520, "Y1770C-6.0"),
        ("draht", 7.0, 38.5, 1670, 1440, "Y1670C-7.0"),
        ("draht", 8.0, 50.3, 1670, 1440, "Y1670C-8.0"),
        ("draht", 10.0, 78.5, 1570, 1300, "Y1570C-10.0"),
        ("litze", 12.9, 100, 1860, 1600, "Y1860S7-12.9"),
        ("litze", 15.3, 140, 1770, 1520, "Y1770S7-15.3"),
        ("litze", 15.3, 140, 1860, 1600, "Y1860S7-15.3"),
        ("litze", 15.7, 150, 1770, 1520, "Y1770S7-15.7"),
        ("litze", 15.7, 150, 1860, 1600, "Y1860S7-15.7"),
        ("stab", 20.0, 314, 1100, 900, "Y1100H-20.0"),
        ("stab", 26.0, 531, 1030, 830, "Y1030H-26.0"),
        ("stab", 26.0, 531, 1050, 950, "Y1050H-26.0"),
        ("stab", 26.0, 531, 1230, 1080, "Y1230H-26.0"),
        ("stab", 26.5, 552, 1030, 830, "Y1030H-26.5"),
        ("stab", 26.5, 552, 1050, 950, "Y1050H-26.5"),
        ("stab", 26.5, 552, 1230, 1080, "Y1230H-26.5"),
        ("stab", 32.0, 804, 1030, 830, "Y1030H-32.0"),
        ("stab", 32.0, 804, 1050, 950, "Y1050H-32.0"),
        ("stab", 32.0, 804, 1230, 1080, "Y1230H-32.0"),
        ("stab", 36.0, 1018, 1030, 830, "Y1030H-36.0"),
        ("stab", 36.0, 1018, 1050, 950, "Y1050H-36.0"),
        ("stab", 36.0, 1018, 1230, 1080, "Y1230H-36.0"),
    ]

    #: Tabelle 10: f_pd in N/mm², gerundet gedruckt.
    TABELLE_10 = {"Y1860": 1390, "Y1770": 1320, "Y1670": 1250, "Y1570": 1130,
                  "Y1230": 940, "Y1100": 780, "Y1050": 825, "Y1030": 720}

    def test_jede_zeile_der_tabelle_7(self):
        """Jede Zeile genau einmal -- keine fehlt, keine ist erfunden."""
        gebaut = sorted(
            (e.art.value, e.durchmesser, e.flaeche, s.f_pk, s.f_p01k, e.bezeichnung(sorte))
            for sorte, s in SPANNSTAHLSORTEN.items() for e in s.erzeugnisse)
        self.assertEqual(gebaut, sorted(self.TABELLE_7))

    def test_sorten_in_der_folge_der_tabelle_10(self):
        self.assertEqual(list(SPANNSTAHLSORTEN), list(self.TABELLE_10))
        self.assertEqual(spannstahlsorten_zum_anlegen(), list(self.TABELLE_10))

    def test_bemessungswert_wie_tabelle_10(self):
        """f_pd = f_p0.1k / 1.15 (Gleichung (5)) -- die Tabelle rundet ihn auf höchstens 3 N/mm²."""
        for sorte, gedruckt in self.TABELLE_10.items():
            with self.subTest(sorte=sorte):
                f_pd = werte(spannstahl(sorte), "f_pd")["f_pd"].in_einheit(N_PRO_MM2)
                self.assertAlmostEqual(f_pd, SPANNSTAHLSORTEN[sorte].f_p01k / 1.15)
                self.assertLess(abs(f_pd - gedruckt), 3.0)

    def test_bruchdehnung_und_moduln(self):
        """eps_ud = 0.020 (Tabelle 10); E_p 200 GPa für Drähte und Stäbe, 195 GPa für Litzen (3.3.2.4)."""
        w = werte(spannstahl("Y1860"), "eps_ud", "E_p", "E_p_litze", "gamma_s",
                  "eps_pd", "eps_pd_litze")
        self.assertEqual(w["eps_ud"].in_einheit(PROZENT), 2.0)
        self.assertEqual(w["E_p"].in_einheit(N_PRO_MM2), 200000)
        self.assertEqual(w["E_p_litze"].in_einheit(N_PRO_MM2), 195000)
        self.assertEqual(w["gamma_s"].si, 1.15)
        self.assertAlmostEqual(w["eps_pd"].si, 1600 / 1.15 / 200000)
        self.assertAlmostEqual(w["eps_pd_litze"].si, 1600 / 1.15 / 195000)

    def test_der_modul_haengt_am_erzeugnis(self):
        for sorte, s in SPANNSTAHLSORTEN.items():
            for e in s.erzeugnisse:
                with self.subTest(erzeugnis=e.bezeichnung(sorte)):
                    self.assertEqual(e.modul, "E_p_litze" if e.art is Erzeugnisart.LITZE else "E_p")

    def test_abweichende_fliessgrenze_zieht_mit(self):
        eigen = spannstahl("Y1860", abweichungen={"f_p01k": Groesse(1500, N_PRO_MM2)})
        self.assertAlmostEqual(werte(eigen, "f_pd")["f_pd"].in_einheit(N_PRO_MM2), 1500 / 1.15)

    def test_unbekannte_sorte(self):
        with self.assertRaises(ValueError):
            spannstahl("Y2000")


class TestGesetz(unittest.TestCase):
    """Figur 17: bis f_pd mit E_p, dann waagrecht bis eps_ud -- nur auf Zug."""

    def setUp(self):
        self.g = Spannstahlgesetz(E_p=195e9, f_pd=1391e6, eps_ud=0.02)

    def test_elastisch_dann_plastisch(self):
        self.assertAlmostEqual(self.g.spannung(0.005), 975e6)
        self.assertEqual(self.g.spannung(0.01), 1391e6)
        self.assertEqual(self.g.spannung(0.02), 1391e6)
        self.assertAlmostEqual(self.g.eps_pd, 1391 / 195000)

    def test_jenseits_der_bruchdehnung_nichts(self):
        self.assertEqual(self.g.spannung(0.0201), 0.0)

    def test_gedrueckt_nichts(self):
        """Die Figur kennt nur den Zug -- gedrückt trägt der Spannstahl hier nichts."""
        self.assertEqual(self.g.spannung(-0.001), 0.0)
        self.assertEqual(self.g.spannung(0.0), 0.0)

    def test_formel(self):
        self.assertIn(r"\min(E_p\,\varepsilon_p;\ f_{pd})", self.g.latex())


class TestBild(unittest.TestCase):
    def kurven(self, *sorten):
        p = Projekt(name="Spannstahl")
        for sorte in sorten:
            p.spannstahl(sorte)
        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        self.assertEqual(antwort.status, 200)
        return antwort.daten["werkstoffgesetze"]

    def test_y1860(self):
        """Vom Nullpunkt bis f_pd = 1391.3 N/mm² bei 6.96 ‰, waagrecht bis 20 ‰."""
        kurve = self.kurven("Y1860")["sp1"]
        self.assertEqual((kurve["titel"], kurve["name"], kurve["art"]),
                         ("Spannstahl – bilineare Beziehung", "Y1860", "spannstahl"))
        self.assertEqual(kurve["referenz"], Spannstahlgesetz.REFERENZ)
        ecken = [(round(q["eps"], 2), round(q["sigma"], 1)) for q in kurve["punkte"]]
        self.assertEqual(ecken, [(0.0, 0.0), (6.96, 1391.3), (20.0, 1391.3)])
        self.assertEqual([m["text"] for m in kurve["marken"]], ["ε_pd", "ε_ud"])

    def test_hinweis_nur_wo_es_litzen_gibt(self):
        kurven = self.kurven("Y1860", "Y1030")
        self.assertIn("Litzen steigen mit E_p = 195000 N/mm² flacher an und fliessen ab "
                      "ε_pd = 7.13 ‰ statt 6.96 ‰", kurven["sp1"]["hinweis"])
        self.assertEqual(kurven["sp2"]["hinweis"], "")


class TestImProjekt(unittest.TestCase):
    def test_normsorte_und_eigener(self):
        p = Projekt(name="Spannstahl")
        norm = p.spannstahl("Y1860")
        eigen = p.eigener_spannstahl("Y1770")
        self.assertEqual((norm.kennung, norm.name), ("sp1", "Y1860"))
        self.assertEqual((eigen.kennung, eigen.name), ("sp2", "SP1"))

    def test_speichern_und_laden(self):
        p = Projekt(name="Spannstahl")
        p.eigener_spannstahl("Y1860").abweichungen = {"f_pk": 1900.0}
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.materialien[0].art, Baustoffart.SPANNSTAHL)
        aufbau = wieder.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.materialziele())
        self.assertEqual(loesung.groesse("spannstahl.sp1.f_pk").in_einheit(N_PRO_MM2), 1900)

    def test_katalog_nennt_die_erzeugnisse(self):
        """Das Fenster des Materials zeigt sie, ein Spannglied wählt eines."""
        katalog = dienst.bearbeite("katalog", {}).daten["materialarten"]
        art = katalog["spannstahl"]
        self.assertEqual(art["titel"], "Spannstahl")
        self.assertEqual(art["erzeugnisquelle"], "SIA 262:2025, 3.3.2.2, Tabelle 7")
        litze = art["erzeugnisse"]["Y1860"][-1]
        self.assertEqual(litze, {"art": "litze", "beschriftung": "Litze", "durchmesser": 15.7,
                                 "flaeche": 150.0, "bezeichnung": "Y1860S7-15.7",
                                 "modul": "E_p_litze"})
        self.assertEqual(katalog["beton"]["erzeugnisse"], {})


if __name__ == "__main__":
    unittest.main()
