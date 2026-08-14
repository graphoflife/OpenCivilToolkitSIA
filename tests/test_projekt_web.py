"""Tests für die Projektbeschreibung und die JSON-Schnittstelle."""

import json
import tempfile
import unittest
from pathlib import Path

from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, N_PRO_MM2, Groesse
from opencivil.projekt import (
    KombinationEintrag, LageEintrag, MaterialEintrag, Projekt, ProjektFehler,
    QuerschnittEintrag,
)
from opencivil.web import api, server


class TestProjektBeschreibung(unittest.TestCase):
    def test_beispiel_baut_durch(self):
        aufbau = Projekt.beispiel().aufbauen()
        self.assertEqual(len(aufbau.baustoffe), 2)
        self.assertEqual(len(aufbau.querschnitte), 1)
        self.assertEqual(len(aufbau.nachweise), 1)
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        self.assertTrue(loesung.vollstaendig)
        self.assertEqual(len(loesung.urteile), 3)

    def test_hin_und_zurueck(self):
        original = Projekt.beispiel()
        kopie = Projekt.aus_dict(json.loads(json.dumps(original.als_dict())))
        self.assertEqual(kopie.als_dict(), original.als_dict())

    def test_speichern_und_laden(self):
        with tempfile.TemporaryDirectory() as ordner:
            pfad = Path(ordner) / "unter" / "projekt.json"
            Projekt.beispiel().speichern(pfad)
            self.assertEqual(Projekt.laden(pfad).als_dict(), Projekt.beispiel().als_dict())

    def test_abweichung_wird_in_der_anzeigeeinheit_gelesen(self):
        """Die Beschreibung enthält blanke Zahlen -- die Einheit kommt aus der Definition."""
        projekt = Projekt.beispiel()
        projekt.material("b1").abweichungen["f_ck"] = 45.0
        aufbau = projekt.aufbauen()
        c = aufbau.baustoffe["b1"]
        wid = c.id_von("f_ck")
        self.assertAlmostEqual(
            aufbau.werk.loese(wid).groesse(wid).in_einheit(N_PRO_MM2), 45.0)

    def test_ueberschreibung_kappt_den_zweig(self):
        projekt = Projekt.beispiel()
        projekt.material("b1").ueberschreibungen["f_cd"] = 12.0
        aufbau = projekt.aufbauen()
        c = aufbau.baustoffe["b1"]
        loesung = aufbau.werk.loese(c.id_von("f_cd"))
        self.assertAlmostEqual(
            loesung.groesse(c.id_von("f_cd")).in_einheit(N_PRO_MM2), 12.0)
        self.assertFalse(loesung.hat(c.id_von("eta_fc")))

    def test_zwei_materialien_gleicher_sorte_bleiben_getrennt(self):
        projekt = Projekt(
            name="zwei",
            materialien=[
                MaterialEintrag("b1", "beton", "C30/37", "A"),
                MaterialEintrag("b2", "beton", "C30/37", "B", abweichungen={"f_ck": 40.0}),
            ])
        aufbau = projekt.aufbauen()
        werk = aufbau.werk
        a, b = aufbau.baustoffe["b1"], aufbau.baustoffe["b2"]
        self.assertNotEqual(a.id_von("f_ck"), b.id_von("f_ck"))
        loesung = werk.loese(a.id_von("f_ck"), b.id_von("f_ck"))
        self.assertAlmostEqual(loesung.groesse(a.id_von("f_ck")).in_einheit(N_PRO_MM2), 30)
        self.assertAlmostEqual(loesung.groesse(b.id_von("f_ck")).in_einheit(N_PRO_MM2), 40)

    def test_fehlendes_material_wird_benannt(self):
        projekt = Projekt.beispiel()
        projekt.materialien = [m for m in projekt.materialien if m.kennung != "b1"]
        with self.assertRaises(ProjektFehler) as ctx:
            projekt.aufbauen()
        self.assertIn("b1", str(ctx.exception))

    def test_unbekannte_sorte_wird_benannt(self):
        projekt = Projekt(materialien=[MaterialEintrag("b1", "beton", "C99/100")])
        with self.assertRaises(ProjektFehler) as ctx:
            projekt.aufbauen()
        self.assertIn("C99/100", str(ctx.exception))

    def test_querschnitt_ohne_bewehrung(self):
        projekt = Projekt(
            materialien=[MaterialEintrag("b1", "beton", "C30/37")],
            querschnitte=[QuerschnittEintrag("q1", "leer", "b1")])
        with self.assertRaises(ProjektFehler):
            projekt.aufbauen()

    def test_ohne_kombination_gibt_es_eine_warnung_statt_eines_fehlers(self):
        projekt = Projekt(
            materialien=[
                MaterialEintrag("b1", "beton", "C30/37"),
                MaterialEintrag("s1", "betonstahl", "B500B"),
            ],
            querschnitte=[QuerschnittEintrag(
                "q1", "ohne Lasten", "b1",
                lagen_unten=[LageEintrag(16.0, "s1", abstand=150.0)])])
        aufbau = projekt.aufbauen()
        self.assertTrue(aufbau.warnungen)
        self.assertEqual(aufbau.nachweise, {})

    def test_stabzahl_statt_abstand(self):
        projekt = Projekt.beispiel()
        lage = projekt.querschnitt("q1").lagen_unten[0]
        lage.abstand, lage.anzahl = None, 7.0
        aufbau = projekt.aufbauen()
        self.assertIsNone(aufbau.querschnitte["q1"].lagen_unten[0].abstand)
        self.assertEqual(aufbau.querschnitte["q1"].lagen_unten[0].anzahl, 7.0)

    def test_freie_kennung(self):
        projekt = Projekt.beispiel()
        self.assertNotIn(projekt.freie_kennung("b"), ["b1"])


class TestApiAbbildung(unittest.TestCase):
    def setUp(self):
        self.projekt = Projekt.beispiel()
        self.aufbau = self.projekt.aufbauen()
        self.ziele = self.aufbau.alle_nachweisziele()
        self.loesung = self.aufbau.werk.loese(*self.ziele)

    def test_katalog(self):
        k = api.katalog()
        self.assertEqual(len(k["betonsorten"]), 9)
        self.assertEqual(len(k["stahlsorten"]), 5)
        self.assertEqual(len(k["erfuellungsarten"]), 3)
        self.assertTrue(any(v["berechnet"] for v in k["kennwerte"]["beton"]))
        self.assertTrue(any(v["aus_sorte"] for v in k["kennwerte"]["beton"]))

    def test_alles_ist_json_faehig(self):
        d = api.loesung_dict(self.loesung, self.aufbau, self.ziele)
        json.dumps(d)  # wirft, wenn etwas nicht serialisierbar ist

    def test_werte_tragen_ihre_herkunft(self):
        d = api.loesung_dict(self.loesung, self.aufbau, self.ziele)
        f_cd = d["werte"]["beton.b1.f_cd"]
        self.assertEqual(f_cd["quelle"], "berechnet")
        self.assertEqual(f_cd["einheit"], "N/mm^2")
        self.assertIn("mathrm", f_cd["latex"])

    def test_protokoll_enthaelt_gleichungen_und_tabellen(self):
        d = api.loesung_dict(self.loesung, self.aufbau, self.ziele)
        arten = {b["art"] for b in d["protokoll"]}
        self.assertIn("gleichung", arten)
        self.assertIn("tabelle", arten)

    def test_ketten_je_ziel(self):
        d = api.loesung_dict(self.loesung, self.aufbau, self.ziele)
        for ziel in self.ziele:
            self.assertIn(ziel, d["ketten"])
            self.assertTrue(d["ketten"][ziel]["berechnungen"])

    def test_linie_wird_mitgeliefert(self):
        d = api.loesung_dict(self.loesung, self.aufbau, self.ziele)
        linie = d["linien"]["q1"]
        self.assertGreater(len(linie["punkte"]), 100)
        self.assertEqual(len(linie["kombinationen"]), 3)
        self.assertIn("art_text", linie["kombinationen"][0])

    def test_zuordnung_verbindet_kennung_und_wert_id(self):
        d = api.loesung_dict(self.loesung, self.aufbau, self.ziele)
        self.assertEqual(
            d["zuordnung"]["materialien"]["b1"]["kennwerte"]["f_cd"], "beton.b1.f_cd")


class TestServerEndpunkte(unittest.TestCase):
    """Die Endpunktfunktionen ohne laufenden Server."""

    def rumpf(self, **zusatz):
        return {"projekt": Projekt.beispiel().als_dict(), **zusatz}

    def test_rechnen(self):
        antwort = server.rechnen(self.rumpf())
        self.assertTrue(antwort["vollstaendig"])
        self.assertEqual(len(antwort["urteile"]), 3)
        self.assertTrue(antwort["alle_nachweise_erfuellt"])

    def test_rechnen_mit_einzelziel(self):
        antwort = server.rechnen(self.rumpf(ziele=["beton.b1.f_cd"]))
        self.assertEqual(set(antwort["werte"]), {
            "beton.b1.eta_fc", "beton.b1.f_ck", "beton.b1.f_cd", "beton.b1.gamma_c",
        })
        self.assertEqual(antwort["ketten"]["beton.b1.f_cd"]["berechnungen"][-1], "beton.b1.f_cd")

    def test_unbekanntes_ziel(self):
        with self.assertRaises(server.ApiFehler) as ctx:
            server.rechnen(self.rumpf(ziele=["gibt.es.nicht"]))
        self.assertEqual(ctx.exception.status, 400)

    def test_ziele_auflisten(self):
        antwort = server.ziele_auflisten(self.rumpf())
        ids = {z["id"] for z in antwort["ziele"]}
        self.assertIn("beton.b1.f_cd", ids)
        self.assertIn("betonstahl.s1.f_yd", ids)
        self.assertTrue(all("symbol" in z for z in antwort["ziele"]))

    def test_alles_rechnen(self):
        antwort = server.alles_rechnen(self.rumpf())
        self.assertGreater(len(antwort["werte"]), 30)

    def test_bericht(self):
        antwort = server.bericht(self.rumpf(pdf=False))
        self.assertIn(r"\documentclass", antwort["tex"])
        self.assertTrue(Path(antwort["tex_pfad"]).exists())

    def test_projekt_speichern_und_laden(self):
        alt = server.PROJEKT_DATEI
        try:
            with tempfile.TemporaryDirectory() as ordner:
                server.PROJEKT_DATEI = Path(ordner) / "projekt.json"
                eigen = Projekt.beispiel()
                eigen.name = "Eigener Name"
                server.projekt_speichern(eigen.als_dict())
                self.assertEqual(server.projekt_laden().name, "Eigener Name")
        finally:
            server.PROJEKT_DATEI = alt

    def test_ohne_datei_kommt_das_beispiel(self):
        alt = server.PROJEKT_DATEI
        try:
            with tempfile.TemporaryDirectory() as ordner:
                server.PROJEKT_DATEI = Path(ordner) / "gibt-es-nicht.json"
                self.assertTrue(server.projekt_laden().materialien)
        finally:
            server.PROJEKT_DATEI = alt


if __name__ == "__main__":
    unittest.main()
