"""Tests für die Projektbeschreibung und die JSON-Schnittstelle."""

import json
import tempfile
import unittest
from pathlib import Path

from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, N_PRO_MM2, Groesse
from opencivil.projekt import (
    KombinationEintrag, LageEintrag, MaterialEintrag, PostenEintrag, Projekt,
    ProjektFehler, QuerschnittEintrag,
)
from opencivil.querschnitt.platte import Richtung
from opencivil.web import api, server


class TestProjektBeschreibung(unittest.TestCase):
    def test_beispiel_baut_durch(self):
        aufbau = Projekt.beispiel().aufbauen()
        self.assertEqual(len(aufbau.baustoffe), 2)
        self.assertEqual(len(aufbau.querschnitte), 1)
        self.assertEqual(sorted(aufbau.nachweise), ["q1.x", "q1.y"])
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        self.assertTrue(loesung.vollstaendig)
        self.assertEqual(len(loesung.urteile), 6)

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
        projekt.material_loesen("b1").abweichungen["f_ck"] = 45.0
        aufbau = projekt.aufbauen()
        c = aufbau.baustoffe["b1"]
        wid = c.id_von("f_ck")
        self.assertAlmostEqual(
            aufbau.werk.loese(wid).groesse(wid).in_einheit(N_PRO_MM2), 45.0)

    def test_ueberschreibung_kappt_den_zweig(self):
        projekt = Projekt.beispiel()
        projekt.material_loesen("b1").ueberschreibungen["f_cd"] = 12.0
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
                MaterialEintrag("b1", "beton", "C30/37", "C30/37"),
                MaterialEintrag("b2", "beton", "C30/37", "C30/37_1",
                                eigenstaendig=True, abweichungen={"f_ck": 40.0}),
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
        projekt = Projekt(materialien=[MaterialEintrag("b1", "beton", "C99/100", "C99/100")])
        with self.assertRaises(ProjektFehler) as ctx:
            projekt.aufbauen()
        self.assertIn("C99/100", str(ctx.exception))

    def test_querschnitt_ohne_bewehrung(self):
        projekt = Projekt(
            materialien=[MaterialEintrag("b1", "beton", "C30/37", "C30/37")],
            querschnitte=[QuerschnittEintrag("q1", "leer", "b1")])
        with self.assertRaises(ProjektFehler):
            projekt.aufbauen()

    def test_ohne_kombination_gibt_es_eine_warnung_statt_eines_fehlers(self):
        projekt = Projekt(
            materialien=[
                MaterialEintrag("b1", "beton", "C30/37", "C30/37"),
                MaterialEintrag("s1", "betonstahl", "B500B", "B500B"),
            ],
            querschnitte=[QuerschnittEintrag(
                "q1", "ohne Lasten", "b1",
                lagen=[LageEintrag(stahl="s1",
                                   grund=PostenEintrag(durchmesser=16.0, abstand=150.0))])])
        aufbau = projekt.aufbauen()
        self.assertTrue(aufbau.warnungen)
        self.assertEqual(aufbau.nachweise, {})

    def test_stabzahl_statt_abstand(self):
        projekt = Projekt.beispiel()
        grund = projekt.querschnitt("q1").lagen[0].grund
        grund.abstand, grund.anzahl = None, 7.0
        aufbau = projekt.aufbauen()
        posten = aufbau.querschnitte["q1"].lagen[0].grund
        self.assertIsNone(posten.abstand)
        self.assertEqual(posten.anzahl, 7.0)

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
        linie = d["linien"]["q1.x"]
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
        self.assertEqual(len(antwort["urteile"]), 6)
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


class TestMaterialsperre(unittest.TestCase):
    """Nur die unveränderte Normsorte darf die Sortenbezeichnung tragen."""

    def test_normsorte_darf_nicht_abweichen(self):
        projekt = Projekt.beispiel()
        projekt.material("b1").abweichungen["f_ck"] = 45.0
        with self.assertRaises(ProjektFehler) as ctx:
            projekt.aufbauen()
        self.assertIn("Normsorte", str(ctx.exception))

    def test_normsorte_darf_nicht_umbenannt_werden(self):
        projekt = Projekt.beispiel()
        projekt.material("b1").name = "Mein Beton"
        with self.assertRaises(ProjektFehler):
            projekt.aufbauen()

    def test_loesen_vergibt_eigenen_namen(self):
        projekt = Projekt.beispiel()
        eintrag = projekt.material_loesen("b1")
        self.assertTrue(eintrag.eigenstaendig)
        self.assertEqual(eintrag.name, "C30/37_1")
        eintrag.abweichungen["f_ck"] = 45.0
        projekt.aufbauen()  # jetzt erlaubt

    def test_loesen_weicht_belegten_namen_aus(self):
        projekt = Projekt.beispiel()
        projekt.materialien.append(
            MaterialEintrag("b2", "beton", "C30/37", "C30/37_1", eigenstaendig=True))
        self.assertEqual(projekt.material_loesen("b1").name, "C30/37_2")

    def test_doppelte_namen_verboten(self):
        projekt = Projekt.beispiel()
        projekt.materialien.append(MaterialEintrag("b2", "beton", "C30/37", "C30/37"))
        with self.assertRaises(ProjektFehler) as ctx:
            projekt.aufbauen()
        self.assertIn("zweimal vergeben", str(ctx.exception))

    def test_mehrere_materialien_bekommen_indizierte_symbole(self):
        """Sonst stünden im Bericht zwei gleich aussehende Gleichungen."""
        projekt = Projekt.beispiel()
        projekt.materialien.append(
            MaterialEintrag("b2", "beton", "C50/60", "C50/60"))
        aufbau = projekt.aufbauen()
        self.assertIn("C30/37", aufbau.baustoffe["b1"].definition("f_cd").symbol)
        self.assertIn("C50/60", aufbau.baustoffe["b2"].definition("f_cd").symbol)

    def test_einzelnes_material_bleibt_ohne_index(self):
        aufbau = Projekt.beispiel().aufbauen()
        self.assertEqual(aufbau.baustoffe["b1"].definition("f_cd").symbol, "f_{cd}")


class TestMehrfachverwendung(unittest.TestCase):
    def test_zwei_platten_mit_demselben_beton(self):
        """
        Früher scheiterte das ganze Projekt: der Beton wurde von jeder Platte
        erneut angemeldet und das Rechenwerk lehnte die Doppelung ab.
        """
        projekt = Projekt.beispiel()
        zweite = QuerschnittEintrag.aus_dict(projekt.querschnitte[0].als_dict())
        zweite.kennung, zweite.name = "q2", "Zweite Platte"
        projekt.querschnitte.append(zweite)
        aufbau = projekt.aufbauen()
        self.assertEqual(sorted(aufbau.nachweise), ["q1.x", "q1.y", "q2.x", "q2.y"])
        self.assertTrue(aufbau.werk.loese(*aufbau.alle_nachweisziele()).vollstaendig)


class TestAltesFormat(unittest.TestCase):
    """Eine vor dem Vier-Lagen-Modell gespeicherte Datei muss weiter aufgehen."""

    ALT = {
        "name": "Alt",
        "materialien": [
            {"kennung": "b1", "art": "beton", "sorte": "C30/37", "name": "C30/37"},
            {"kennung": "s1", "art": "betonstahl", "sorte": "B500B", "name": "B500B"},
        ],
        "querschnitte": [{
            "kennung": "q1", "name": "Decke", "beton": "b1", "h": 300.0, "b": 1000.0,
            "ueberdeckung_unten": 30.0, "ueberdeckung_oben": 30.0,
            "lagen_unten": [
                {"durchmesser": 18.0, "stahl": "s1", "abstand": 150.0, "anzahl": None},
                {"durchmesser": 12.0, "stahl": "s1", "abstand": 150.0, "anzahl": None},
            ],
            "lagen_oben": [
                {"durchmesser": 12.0, "stahl": "s1", "abstand": 150.0, "anzahl": None},
            ],
            "kombinationen": [{"name": "Feld", "M_Ed": 100.0, "N_Ed": 0.0, "art": "N_konstant"}],
        }],
    }

    def test_wird_umgerechnet(self):
        projekt = Projekt.aus_dict(self.ALT)
        lagen = projekt.querschnitte[0].lagen
        self.assertEqual(len(lagen), 4)
        self.assertEqual(lagen[0].grund.durchmesser, 18.0)   # lagen_unten[0] -> 1. Lage
        self.assertEqual(lagen[1].grund.durchmesser, 12.0)   # lagen_unten[1] -> 2. Lage
        self.assertFalse(lagen[2].vorhanden)                 # es gab keine zweite obere
        self.assertEqual(lagen[3].grund.durchmesser, 12.0)   # lagen_oben[0] -> 4. Lage

    def test_rechnet_durch(self):
        aufbau = Projekt.aus_dict(self.ALT).aufbauen()
        self.assertTrue(aufbau.werk.loese(*aufbau.alle_nachweisziele()).vollstaendig)


class TestNachweisrichtung(unittest.TestCase):
    """Je Kombination wählbar, in welcher Tragrichtung sie gilt."""

    def projekt_mit(self, *richtungen: str) -> Projekt:
        projekt = Projekt.beispiel()
        for eintrag, richtung in zip(projekt.querschnitte[0].kombinationen, richtungen):
            eintrag.richtung = richtung
        return projekt

    def test_nur_x(self):
        projekt = self.projekt_mit("x", "x", "x")
        loesung = self._loesen(projekt)
        self.assertTrue(all("Nachweis x" in u.name for u in loesung.urteile))
        self.assertEqual(len(loesung.urteile), 3)

    def test_getrennt_je_richtung(self):
        projekt = self.projekt_mit("x", "x", "y")
        namen = [u.name for u in self._loesen(projekt).urteile]
        self.assertEqual(sum("Nachweis x" in n for n in namen), 2)
        self.assertEqual(sum("Nachweis y" in n for n in namen), 1)

    def test_beide_ist_die_vorgabe_alter_beschreibungen(self):
        """Ohne das Feld darf kein Nachweis stillschweigend wegfallen."""
        eintrag = KombinationEintrag.aus_dict({"name": "Feld", "M_Ed": 100.0})
        self.assertEqual(eintrag.richtung, "beide")
        self.assertTrue(eintrag.gilt_fuer(Richtung.X))
        self.assertTrue(eintrag.gilt_fuer(Richtung.Y))

    def test_richtung_ueberlebt_das_speichern(self):
        projekt = self.projekt_mit("y", "x", "beide")
        kopie = Projekt.aus_dict(json.loads(json.dumps(projekt.als_dict())))
        self.assertEqual([k.richtung for k in kopie.querschnitte[0].kombinationen],
                         ["y", "x", "beide"])

    def test_richtung_ohne_kombination_bleibt_stumm(self):
        """
        Keine Kombination für eine Richtung ist eine Entscheidung des Benutzers,
        kein Mangel -- dafür gibt es keine Warnung.
        """
        aufbau = self.projekt_mit("x", "x", "x").aufbauen()
        self.assertEqual(sorted(aufbau.nachweise), ["q1.x"])
        self.assertEqual(aufbau.warnungen, [])

    def _loesen(self, projekt: Projekt):
        aufbau = projekt.aufbauen()
        return aufbau.werk.loese(*aufbau.alle_nachweisziele())


class TestJsonTauglich(unittest.TestCase):
    """
    json.dumps schreibt fuer unendliche Werte ``Infinity`` -- gueltiges Python,
    aber kein gueltiges JSON. Im Browser scheiterte JSON.parse, und die Antwort
    kam mit Status 200 an: "unlesbare Antwort (200)".
    """

    def test_endlich_ersetzt_unendlich(self):
        roh = {"a": float("inf"), "b": float("-inf"), "c": float("nan"),
               "d": [1.0, float("inf")], "e": {"f": float("nan")}, "g": "text", "h": 3}
        sauber = api.endlich(roh)
        self.assertIsNone(sauber["a"])
        self.assertIsNone(sauber["b"])
        self.assertIsNone(sauber["c"])
        self.assertEqual(sauber["d"], [1.0, None])
        self.assertIsNone(sauber["e"]["f"])
        self.assertEqual(sauber["g"], "text")
        self.assertEqual(sauber["h"], 3)

    def test_moment_konstant_liefert_gueltiges_json(self):
        """Genau der gemeldete Fall: 'Moment konstant' mit N_Ed = 0."""
        projekt = Projekt.beispiel()
        for k in projekt.querschnitte[0].kombinationen:
            k.art = "M_konstant"
            k.N_Ed = 0.0
        antwort = server.rechnen({"projekt": projekt.als_dict()})
        text = json.dumps(api.endlich(antwort), allow_nan=False)  # wirft bei Infinity
        self.assertNotIn("Infinity", text)
        self.assertNotIn("NaN", text)

    def test_jede_antwort_ist_ohne_sonderwerte(self):
        for art in ("N_konstant", "M_konstant", "naechster_Punkt"):
            with self.subTest(art=art):
                projekt = Projekt.beispiel()
                for k in projekt.querschnitte[0].kombinationen:
                    k.art, k.N_Ed, k.M_Ed = art, 0.0, 0.0
                antwort = server.rechnen({"projekt": projekt.als_dict()})
                json.dumps(api.endlich(antwort), allow_nan=False)


class TestUnbenutztesMaterial(unittest.TestCase):
    """
    Ein Material, das noch keine Platte verwendet, muss trotzdem gerechnet
    werden -- sonst stünden im Editor leere Felder, obwohl die Sorte alles
    hergibt.
    """

    def test_unbenutzter_beton_wird_gerechnet(self):
        projekt = Projekt.beispiel()
        projekt.materialien.append(MaterialEintrag("b2", "beton", "C12/15", "C12/15"))
        antwort = server.rechnen({"projekt": projekt.als_dict()})
        eigene = [k for k in antwort["werte"] if k.startswith("beton.b2.")]
        self.assertGreaterEqual(len(eigene), 12)
        self.assertIn("beton.b2.f_cd", antwort["werte"])

    def test_unbenutzter_stahl_wird_gerechnet(self):
        projekt = Projekt.beispiel()
        projekt.materialien.append(MaterialEintrag("s2", "betonstahl", "B700B", "B700B"))
        antwort = server.rechnen({"projekt": projekt.als_dict()})
        self.assertIn("betonstahl.s2.f_yd", antwort["werte"])

    def test_materialziele_umfassen_alle_kennwerte(self):
        aufbau = Projekt.beispiel().aufbauen()
        ziele = aufbau.materialziele()
        self.assertIn("beton.b1.f_cd", ziele)
        self.assertIn("betonstahl.s1.f_yd", ziele)
