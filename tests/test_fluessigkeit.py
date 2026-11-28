"""
Die Flüssigkeit, eine Materialart seit 2026-11-27 (opencivil.material.fluessigkeit):
das Wasser und eigene, ihre Raumlast, wie Sätze die Art nennen, das Wasser
des Pfahls -- und wie eine Datei von früher mit der Zahl γ_w gelesen wird
(opencivil.projekt.frueher). Der Grundbruch mit seinem Wasser steht in
test_grundbruch.
"""

import copy
import unittest

from opencivil.core.einheiten import KG_PRO_M3, KN_PRO_M3
from opencivil.material.arten import MATERIALARTEN, keines
from opencivil.projekt import Projekt, ProjektFehler
from opencivil.projekt.aufbau.kern import kennwert
from tests.unfertig import meldung


def raumlast(projekt, kennung):
    """γ_fl des Materials ``kennung`` in kN/m³, wie das Projekt es rechnet."""
    aufbau = projekt.aufbauen()
    return kennwert(aufbau, aufbau.baustoffe[kennung], "gamma_fl").in_einheit(KN_PRO_M3)


class TestDasWasser(unittest.TestCase):

    def test_1000_kg_pro_m3_wiegen_10_kn_pro_m3(self):
        """Mit g = 10 m/s² wie beim Eigengewicht -- die Vorgabe des Feldes γ_w von früher."""
        p = Projekt(name="Probe")
        wasser = p.fluessigkeit()
        self.assertEqual((wasser.kennung, wasser.anzeigename, wasser.ist_normsorte),
                         ("fl1", "Wasser", True))
        aufbau = p.aufbauen()
        stoff = aufbau.baustoffe["fl1"]
        self.assertAlmostEqual(kennwert(aufbau, stoff, "rho_fl").in_einheit(KG_PRO_M3), 1000.0)
        self.assertAlmostEqual(raumlast(p, "fl1"), 10.0)

    def test_eine_eigene_mit_ihrer_dichte(self):
        p = Projekt(name="Probe")
        eigen = p.eigene_fluessigkeit()
        eigen.abweichungen["rho_fl"] = 1200.0
        self.assertEqual((eigen.anzeigename, eigen.sorte), ("FL1", "Wasser"))
        self.assertAlmostEqual(raumlast(p, eigen.kennung), 12.0)

    def test_das_wasser_bleibt_wie_es_ist(self):
        """Eine feste Sorte wie eine Normsorte: wer eine andere Dichte will, legt eine eigene an."""
        p = Projekt(name="Probe")
        p.fluessigkeit().abweichungen["rho_fl"] = 1100.0
        self.assertIn("eine Normsorte darf keine abweichenden Kennwerte haben", meldung(p))


class TestDieArt(unittest.TestCase):

    def test_ohne_wertesatz_und_aus_keiner_norm(self):
        """Eine Flüssigkeit trägt nichts, und das Wasser steht in keiner Norm."""
        art = MATERIALARTEN["fluessigkeit"]
        self.assertEqual((art.mit_satz, art.aus_norm), (False, False))
        self.assertEqual({a for a, m in MATERIALARTEN.items() if not m.mit_satz},
                         {"holz", "fluessigkeit", "mauerwerk"})
        self.assertEqual({a for a, m in MATERIALARTEN.items() if not m.aus_norm},
                         {"fluessigkeit"})

    def test_die_woerter_nach_dem_geschlecht(self):
        art = MATERIALARTEN["fluessigkeit"]
        self.assertEqual((art.neu, art.eigen, art.einen, art.keinen, art.kein),
                         ("Neue Flüssigkeit", "Eigene Flüssigkeit", "eine Flüssigkeit",
                          "keine Flüssigkeit", "keine Flüssigkeit"))
        holz = MATERIALARTEN["holz"]
        self.assertEqual((holz.neu, holz.einen, holz.keinen),
                         ("Neues Holz", "ein Holz", "kein Holz"))

    def test_keines_auch_fuer_mehrere(self):
        """Verschiedene Geschlechter je mit dem eigenen Wort; bis 2026-11-27 «kein Flüssigkeit»."""
        self.assertEqual(keines(["fluessigkeit"]), "keine Flüssigkeit")
        self.assertEqual(keines(["beton", "baustahl", "holz"]), "kein Beton, Baustahl oder Holz")
        self.assertEqual(keines(["beton", "fluessigkeit"]), "kein Beton oder keine Flüssigkeit")

    def test_ein_neues_bauteil_nimmt_das_erste_wasser(self):
        """Wie «+» in der Oberfläche: Grundbruch und Pfahl beginnen mit dem Wasser des Projekts."""
        p = Projekt.neu()
        self.assertEqual(p.eintrag_anlegen("grundbrueche").wasser, "fl1")
        self.assertEqual(p.eintrag_anlegen("pfaehle").wasser, "fl1")


class TestDerPfahl(unittest.TestCase):

    def projekt(self, **felder):
        p = Projekt(name="Probe")
        p.beton("C30/37")
        p.stahl("B500B")
        p.fluessigkeit()
        return p, p.pfahl("P", stahl="s1", beton="b1", **felder)

    def test_eine_schicht_leichter_als_das_wasser(self):
        p, t = self.projekt()
        t.schicht("Kies", d=3.0, gamma=20.0, phi_k=35.0)
        t.schicht("Torf", d=20.0, gamma=10.0, phi_k=20.0)
        t.kombination("K", N_Ed=100.0)
        self.assertEqual(meldung(p), "Pfahl 'P': Schicht 2: die Raumlast γ = 10 kN/m³ muss "
                                     "grösser sein als die des Wassers «Wasser», γ_w = 10 kN/m³ – "
                                     "sonst ist γ' nicht positiv.")

    def test_aus_dem_versuch_zaehlt_das_gewicht_der_schichten_nicht(self):
        """Ohne Querlast gehen die Schichten in keine Rechnung ein, ihr Gewicht hält nichts an."""
        p, t = self.projekt(grundlage="statisch", R_ak=1000.0)
        t.schicht("Torf", d=20.0, gamma=10.0, phi_k=20.0)
        t.kombination("K", N_Ed=100.0)
        self.assertEqual(dict(p.aufbauen().unfertige), {})

    def test_ohne_wasser_fehlt_es_nur(self):
        p = Projekt(name="Probe")
        t = p.pfahl("P", stahl=p.stahl("B500B").kennung, beton=p.beton("C30/37").kennung)
        t.schicht("Kies", d=20.0)
        t.kombination("K", N_Ed=100.0)
        self.assertEqual(t.wasser, "")
        self.assertEqual(meldung(p), "Pfahl 'P': Wasser: noch kein Material gewählt.")

    def test_das_wasser_steht_in_der_herleitung(self):
        p, t = self.projekt(t_w=3.0)
        t.schicht("Kies", d=20.0)
        t.kombination("K", N_Ed=100.0)
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        pfahl = aufbau.bauteil("t1").objekt
        self.assertAlmostEqual(loesung.werte[pfahl.id_von("gamma_w")].groesse.si, 10e3)
        titel = [getattr(b, "titel", "") for b in loesung.protokoll.alle_bloecke()]
        self.assertIn("Raumlast des Grundwassers, «Wasser»", titel)


def von_frueher(projekt, *zahlen):
    """
    Die Datei von ``projekt``, wie sie vor 2026-11-27 aussah: ohne Flüssigkeit
    -- auch unter den vergebenen Kennungen --, je Grundbruch und Pfahl der Reihe
    nach eine Zahl γ_w aus ``zahlen``.
    """
    roh = copy.deepcopy(projekt.als_dict())
    roh["materialien"] = [m for m in roh["materialien"] if m["art"] != "fluessigkeit"]
    roh["vergeben"].pop("fl")
    eintraege = roh["grundbrueche"] + roh["pfaehle"]
    assert len(eintraege) == len(zahlen)
    for eintrag, zahl in zip(eintraege, zahlen):
        del eintrag["wasser"]
        eintrag["gamma_w"] = zahl
    return roh


class TestVonFrueher(unittest.TestCase):
    """Eine Datei mit der Zahl γ_w öffnet sich und rechnet wie zuvor."""

    def projekt(self):
        p = Projekt(name="Probe")
        p.beton("C30/37")
        p.stahl("B500B")
        p.fluessigkeit()
        for name in ("A", "B"):
            p.grundbruch(name).kombination("K", N_Ed=500.0)
        t = p.pfahl("P", stahl="s1", beton="b1")
        t.schicht("Kies", d=20.0)
        t.kombination("K", N_Ed=100.0)
        return p

    def test_zehn_wird_das_wasser(self):
        p = Projekt.aus_dict(von_frueher(self.projekt(), 10.0, 10, 10.0))
        wasser = [m for m in p.materialien if m.art.value == "fluessigkeit"]
        self.assertEqual([(m.kennung, m.anzeigename, m.ist_normsorte) for m in wasser],
                         [("fl1", "Wasser", True)])
        self.assertEqual([e.wasser for e in p.grundbrueche + p.pfaehle], ["fl1"] * 3)
        self.assertEqual(dict(p.aufbauen().unfertige), {})

    def test_eine_andere_zahl_wird_eine_eigene_fluessigkeit(self):
        """9.81 kN/m³ ist mit g = 10 m/s² eine Dichte von 981 kg/m³; gleiche Zahlen teilen sie."""
        p = Projekt.aus_dict(von_frueher(self.projekt(), 9.81, 10.0, 9.81))
        namen = {m.kennung: m for m in p.materialien if m.art.value == "fluessigkeit"}
        a, b = p.grundbrueche
        eigen = namen[a.wasser]
        self.assertEqual((eigen.anzeigename, eigen.abweichungen), ("FL1", {"rho_fl": 981.0}))
        self.assertTrue(namen[b.wasser].ist_normsorte)
        self.assertEqual(p.pfaehle[0].wasser, a.wasser)
        self.assertEqual(len(namen), 2)
        self.assertAlmostEqual(raumlast(p, a.wasser), 9.81)

    def test_ein_wasser_im_projekt_wird_genommen(self):
        roh = von_frueher(self.projekt(), 10.0, 10.0, 10.0)
        roh["materialien"].append({"kennung": "fl7", "art": "fluessigkeit", "sorte": "Wasser",
                                   "name": "Wasser", "eigenstaendig": False})
        p = Projekt.aus_dict(roh)
        self.assertEqual([m.kennung for m in p.materialien if m.art.value == "fluessigkeit"],
                         ["fl7"])
        self.assertEqual({e.wasser for e in p.grundbrueche + p.pfaehle}, {"fl7"})

    def test_was_keine_zahl_ist_meldet_sich(self):
        with self.assertRaisesRegex(ProjektFehler, "Grundbruch 'A': ein Feld 'gamma_w' gibt es "
                                                   "nicht"):
            Projekt.aus_dict(von_frueher(self.projekt(), "zehn", 10.0, 10.0))

    def test_eine_neue_datei_bleibt_wie_sie_ist(self):
        p = self.projekt()
        self.assertEqual(Projekt.aus_dict(p.als_dict()).als_dict(), p.als_dict())


if __name__ == "__main__":
    unittest.main()
