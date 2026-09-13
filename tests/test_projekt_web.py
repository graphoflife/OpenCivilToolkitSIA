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
from opencivil.web import api, bruecke, dienst, server


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


class TestVollstaendigeAblage(unittest.TestCase):
    """
    Die .json-Datei muss das *ganze* Projekt enthalten.

    Sie ist das einzige, was der Benutzer in der Hand hat: im Browser abgelegt,
    heruntergeladen, weitergegeben, in einem Jahr wieder geöffnet. Fehlt darin
    ein Feld, ist die Arbeit daran still verloren -- und zwar erst beim
    Öffnen, lange nachdem man es hätte merken können.
    """

    def test_kein_feld_faellt_beim_speichern_unter_den_tisch(self):
        """
        Jedes Feld der Beschreibungsklassen muss in als_dict() auftauchen.

        Das ist der Wächter gegen den wahrscheinlichsten Fehler: jemand hängt
        ein Feld an eine dataclass und vergisst als_dict/aus_dict. Ohne diesen
        Test bliebe das bis zum ersten verlorenen Projekt unbemerkt.
        """
        import dataclasses

        beispiele = {
            MaterialEintrag: MaterialEintrag("b1", "beton", "C30/37", "C30/37"),
            PostenEintrag: PostenEintrag(durchmesser=16.0, abstand=150.0),
            LageEintrag: LageEintrag(stahl="s1"),
            KombinationEintrag: KombinationEintrag("Feld", M_Ed=100.0),
            QuerschnittEintrag: QuerschnittEintrag("q1", "Platte", "b1"),
        }
        for klasse, beispiel in beispiele.items():
            with self.subTest(klasse=klasse.__name__):
                felder = {f.name for f in dataclasses.fields(klasse)}
                gespeichert = set(beispiel.als_dict())
                self.assertEqual(
                    felder - gespeichert, set(),
                    f"{klasse.__name__}: diese Felder überleben das Speichern nicht")

    def test_ganzes_projekt_ueberlebt_die_datei(self):
        """Zwei Materialien, zwei Platten, nichts auf den Vorgabewerten."""
        projekt = Projekt(
            name="Mehrteilig",
            materialien=[
                MaterialEintrag("b1", "beton", "C30/37", "C30/37"),
                MaterialEintrag("b2", "beton", "C25/30", "C25/30_1",
                                eigenstaendig=True,
                                abweichungen={"f_ck": 27.0},
                                ueberschreibungen={"f_cd": 15.0}),
                MaterialEintrag("s1", "betonstahl", "B500B", "B500B"),
                MaterialEintrag("s2", "betonstahl", "B700B", "B700B"),
            ],
            querschnitte=[
                QuerschnittEintrag(
                    "q1", "Decke", "b1", h=280.0, b=1000.0,
                    ueberdeckung_unten=25.0, ueberdeckung_oben=35.0,
                    d_max=16.0, einlagenhoehe=40.0,
                    richtung_lage1="y", richtung_lage4="y",
                    lagen=[
                        LageEintrag(
                            stahl="s1",
                            grund=PostenEintrag(durchmesser=20.0, abstand=125.0),
                            zulage=PostenEintrag(durchmesser=14.0, anzahl=6.0)),
                        LageEintrag(stahl="s2",
                                    grund=PostenEintrag(durchmesser=12.0, abstand=200.0)),
                        LageEintrag(stahl="s1"),
                        LageEintrag(stahl="s2",
                                    grund=PostenEintrag(durchmesser=10.0, abstand=150.0)),
                    ],
                    kombinationen=[
                        KombinationEintrag("Feld", 120.0, -50.0, 80.0,
                                           art="M_konstant", richtung="x"),
                        KombinationEintrag("Stütze", -90.0, 0.0, 140.0,
                                           art="naechster_Punkt", richtung="y"),
                    ]),
                QuerschnittEintrag(
                    "q2", "Wand", "b2", h=200.0, b=1000.0,
                    lagen=[LageEintrag(stahl="s2",
                                       grund=PostenEintrag(durchmesser=10.0, abstand=100.0))],
                    kombinationen=[KombinationEintrag("Wind", 30.0, -400.0)]),
            ])

        # Genau der Weg der echten Datei: nach JSON und zurück.
        text = json.dumps(projekt.als_dict(), ensure_ascii=False, indent=2)
        kopie = Projekt.aus_dict(json.loads(text))

        self.assertEqual(kopie.als_dict(), projekt.als_dict())
        self.assertEqual(len(kopie.materialien), 4)
        self.assertEqual(len(kopie.querschnitte), 2)
        # Stichproben an Stellen, die leicht verloren gingen:
        self.assertEqual(kopie.material("b2").ueberschreibungen, {"f_cd": 15.0})
        self.assertEqual(kopie.querschnitt("q1").einlagenhoehe, 40.0)
        self.assertEqual(kopie.querschnitt("q1").richtung_lage1, "y")
        self.assertEqual(kopie.querschnitt("q1").lagen[0].zulage.anzahl, 6.0)
        self.assertEqual(kopie.querschnitt("q1").kombinationen[1].art, "naechster_Punkt")
        self.assertEqual(kopie.querschnitt("q1").kombinationen[0].V_Ed, 80.0)
        self.assertEqual(kopie.querschnitt("q2").lagen[0].stahl, "s2")

    def test_die_datei_geht_auch_durch_den_dienst(self):
        """Was gespeichert wurde, muss der Kern beim Öffnen wieder annehmen."""
        projekt = Projekt.beispiel()
        aus_datei = json.loads(json.dumps(projekt.als_dict()))
        antwort = dienst.bearbeite("pruefen", {"projekt": aus_datei})
        self.assertEqual(antwort.status, 200)
        self.assertEqual(antwort.daten["projekt"], projekt.als_dict())

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

    def test_eine_null_wird_nicht_durch_die_vorgabe_ersetzt(self):
        """
        Der schlimmste der bisherigen Fehler: `float(d.get("h") or 300.0)`
        konnte eine eingegebene Null nicht von einem fehlenden Feld
        unterscheiden. Im Eingabefeld stand 0, gerechnet wurde mit 300 mm, und
        die Oberfläche meldete «alle Nachweise erfüllt» für eine Platte ohne
        Dicke.
        """
        roh = Projekt.beispiel().als_dict()
        roh["querschnitte"][0]["h"] = 0
        self.assertEqual(Projekt.aus_dict(roh).querschnitt("q1").h, 0.0)

        # Fehlt das Feld dagegen wirklich, greift die Vorgabe weiter.
        del roh["querschnitte"][0]["h"]
        self.assertEqual(Projekt.aus_dict(roh).querschnitt("q1").h, 300.0)

    def test_unmoegliche_abmessungen_werden_benannt(self):
        def mit(**aenderung):
            projekt = Projekt.beispiel()
            for feld, wert in aenderung.items():
                setattr(projekt.querschnitt("q1"), feld, wert)
            with self.assertRaises(ProjektFehler) as ctx:
                projekt.aufbauen()
            return str(ctx.exception)

        self.assertIn("Dicke h", mit(h=0.0))
        self.assertIn("Dicke h", mit(h=-300.0))
        self.assertIn("Breite b", mit(b=0.0))
        self.assertIn("Grösstkorn", mit(d_max=0.0))
        self.assertIn("negativ", mit(ueberdeckung_unten=-10.0))
        # Zusammen dicker als die Platte: dort ist kein Platz für Bewehrung.
        self.assertIn("Überdeckungen", mit(ueberdeckung_unten=150.0, ueberdeckung_oben=150.0))

    def test_null_ueberdeckung_bleibt_erlaubt(self):
        """Unüblich, aber nicht unmöglich -- geprüft wird nur die Geometrie."""
        projekt = Projekt.beispiel()
        projekt.querschnitt("q1").ueberdeckung_unten = 0.0
        projekt.aufbauen()          # wirft nicht

    def test_materialkennwerte_muessen_positiv_sein(self):
        """
        gamma_c = 0 endete in einem ZeroDivisionError, ein negatives f_ck in
        einer komplexen Wurzel -- beides kam als Absturzmeldung beim Benutzer
        an. Jeder Kennwert dieser Baustoffe ist seiner Natur nach positiv.
        """
        for kurzname, zahl in (("gamma_c", 0.0), ("f_ck", -30.0)):
            projekt = Projekt.beispiel()
            material = projekt.material("b1")
            material.eigenstaendig = True
            material.abweichungen = {kurzname: zahl}
            with self.assertRaises(ProjektFehler) as ctx:
                projekt.aufbauen()
            self.assertIn(kurzname, str(ctx.exception))

    def test_fehlende_pflichtfelder_werden_benannt(self):
        """Vorher kam der nackte KeyError bis in die Oberfläche."""
        for weg in ("kennung", "beton"):
            roh = Projekt.beispiel().als_dict()
            del roh["querschnitte"][0][weg]
            with self.assertRaises(ProjektFehler) as ctx:
                Projekt.aus_dict(roh)
            self.assertIn(weg, str(ctx.exception))

    def test_eine_zahl_die_keine_ist(self):
        roh = Projekt.beispiel().als_dict()
        roh["querschnitte"][0]["h"] = "dreihundert"
        with self.assertRaises(ProjektFehler) as ctx:
            Projekt.aus_dict(roh)
        self.assertIn("dreihundert", str(ctx.exception))

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

    def test_leere_zulage_steht_auf_teilung(self):
        """
        Eine noch nicht gesetzte Zulage wird über die Teilung geführt.

        Sonst stünde das Feld in der Oberfläche auf 'Anzahl' -- bei einer
        Platte ist die Teilung der Regelfall.
        """
        lage = LageEintrag.aus_dict({"stahl": "s1", "grund": {"durchmesser": 16.0}})
        self.assertEqual(lage.zulage.abstand, 150.0)
        self.assertIsNone(lage.zulage.anzahl)
        self.assertFalse(lage.zulage.vorhanden)   # ohne Durchmesser trotzdem leer
        self.assertEqual(lage.grund.abstand, 150.0)

    def test_eine_gewaehlte_stabzahl_bleibt_eine_stabzahl(self):
        eintrag = PostenEintrag.aus_dict({"durchmesser": 14.0, "abstand": None, "anzahl": 6.0})
        self.assertIsNone(eintrag.abstand)
        self.assertEqual(eintrag.anzahl, 6.0)


class TestUrteilsraum(unittest.TestCase):
    """
    Jedes Urteil trägt den Namensraum seines Nachweises.

    Ohne ihn musste die Oberfläche aus dem Anzeigetext zurückschliessen, zu
    welcher Platte ein Urteil gehört -- und packte bei zwei Platten mit
    denselben Tragrichtungen alle Nachweise in dieselbe Tabelle.
    """

    def zweiplattenprojekt(self) -> Projekt:
        projekt = Projekt.beispiel()
        zweite = Projekt.aus_dict(json.loads(json.dumps(projekt.als_dict()))).querschnitt("q1")
        zweite.kennung, zweite.name = "q2", "Decke über 1. OG"
        projekt.querschnitte.append(zweite)
        return projekt

    def test_zwei_platten_teilen_ihre_urteile_nicht(self):
        aufbau = self.zweiplattenprojekt().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())

        je_platte = {"querschnitt.q1": [], "querschnitt.q2": []}
        for urteil in loesung.urteile:
            passend = [ns for ns in je_platte if urteil.raum.startswith(f"{ns}.")]
            self.assertEqual(len(passend), 1, f"'{urteil.name}' gehört zu {passend}")
            je_platte[passend[0]].append(urteil.name)

        # Beide Platten sind gleich bewehrt, also fällt für beide gleich viel an.
        self.assertEqual(len(je_platte["querschnitt.q1"]), 6)
        self.assertEqual(len(je_platte["querschnitt.q2"]), 6)
        # Und die Namen allein hätten es nicht entschieden -- sie sind gleich.
        self.assertEqual(sorted(je_platte["querschnitt.q1"]),
                         sorted(je_platte["querschnitt.q2"]))

    def test_der_raum_steht_auch_in_der_json_antwort(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": self.zweiplattenprojekt().als_dict()})
        raeume = {u["raum"] for u in antwort.daten["urteile"]}
        self.assertTrue(all(r.startswith("querschnitt.q") for r in raeume), raeume)
        self.assertEqual(len(raeume), 4)   # 2 Platten x 2 Richtungen


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
        self.assertEqual(len(k["erfuellungsarten"]), 4)
        self.assertTrue(any(v["berechnet"] for v in k["kennwerte"]["beton"]))
        self.assertTrue(any(v["aus_sorte"] for v in k["kennwerte"]["beton"]))

    def test_alles_ist_json_faehig(self):
        d = api.loesung_dict(self.loesung, self.aufbau, self.ziele)
        json.dumps(d)  # wirft, wenn etwas nicht serialisierbar ist

    def test_werte_tragen_ihre_herkunft(self):
        d = api.loesung_dict(self.loesung, self.aufbau, self.ziele)
        f_cd = d["werte"]["beton.b1.f_cd"]
        self.assertEqual(f_cd["quelle"], "berechnet")
        # Die Oberfläche bekommt die lesbare Schreibweise -- sie setzt diese
        # Einheit als blanken Text neben die Zahl, nicht als LaTeX.
        self.assertEqual(f_cd["einheit"], "N/mm²")
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


class TestDienst(unittest.TestCase):
    """Der Rechendienst -- ohne Server, ohne Browser, ohne Dateisystem."""

    def rumpf(self, **zusatz):
        return {"projekt": Projekt.beispiel().als_dict(), **zusatz}

    def test_rechnen(self):
        antwort = dienst.bearbeite("rechnen", self.rumpf())
        self.assertEqual(antwort.status, 200)
        self.assertTrue(antwort.daten["vollstaendig"])
        self.assertEqual(len(antwort.daten["urteile"]), 6)
        self.assertTrue(antwort.daten["alle_nachweise_erfuellt"])

    def test_rechnen_mit_einzelziel(self):
        antwort = dienst.bearbeite("rechnen", self.rumpf(ziele=["beton.b1.f_cd"]))
        self.assertEqual(set(antwort.daten["werte"]), {
            "beton.b1.eta_fc", "beton.b1.f_ck", "beton.b1.f_cd", "beton.b1.gamma_c",
        })
        self.assertEqual(
            antwort.daten["ketten"]["beton.b1.f_cd"]["berechnungen"][-1], "beton.b1.f_cd")

    def test_unbekanntes_ziel(self):
        antwort = dienst.bearbeite("rechnen", self.rumpf(ziele=["gibt.es.nicht"]))
        self.assertEqual(antwort.status, 400)
        self.assertIn("gibt.es.nicht", antwort.daten["fehler"])

    def mit_querkraft(self):
        projekt = Projekt.beispiel()
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 120.0
        return {"projekt": projekt.als_dict()}

    def test_querkraftkurven_ohne_angabe(self):
        """Ohne gewählte Normalkraft gilt die des ersten Falls der Richtung."""
        antwort = dienst.bearbeite("querkraftkurven", self.mit_querkraft())
        kurven = antwort.daten["querkraftkurven"]
        self.assertEqual(sorted(kurven), ["q1.x", "q1.y"])
        self.assertEqual(kurven["q1.x"]["N_Ed"], 0.0)
        self.assertEqual(len(kurven["q1.x"]["aeste"]), 2)

    def test_querkraftkurven_mit_gewaehlter_normalkraft(self):
        rumpf = {**self.mit_querkraft(), "n_ed": {"q1.x": -300.0}}
        kurven = dienst.bearbeite("querkraftkurven", rumpf).daten["querkraftkurven"]
        self.assertEqual(kurven["q1.x"]["N_Ed"], -300.0)
        self.assertEqual(kurven["q1.y"]["N_Ed"], 0.0)   # unberührt

    def test_eine_normalkraft_die_keine_zahl_ist(self):
        """
        Kam als roher ValueError mit Status 500 beim Benutzer an. Die Anfrage
        stammt zwar aus der eigenen Oberfläche, aber das ist keine
        Zusicherung -- sie steht offen im Netz.
        """
        rumpf = {**self.mit_querkraft(), "n_ed": {"q1.x": "viel"}}
        antwort = dienst.bearbeite("querkraftkurven", rumpf)
        self.assertEqual(antwort.status, 400)
        self.assertIn("q1.x", antwort.daten["fehler"])
        self.assertIn("viel", antwort.daten["fehler"])

    def test_leere_normalkraft_faellt_auf_die_vorgabe_zurueck(self):
        for wert in (None, ""):
            rumpf = {**self.mit_querkraft(), "n_ed": {"q1.x": wert}}
            antwort = dienst.bearbeite("querkraftkurven", rumpf)
            self.assertEqual(antwort.status, 200)
            self.assertEqual(antwort.daten["querkraftkurven"]["q1.x"]["N_Ed"], 0.0)

    def test_unbekannte_anfrage(self):
        antwort = dienst.bearbeite("gibtesnicht", {})
        self.assertEqual(antwort.status, 404)
        # Die Meldung soll weiterhelfen, nicht bloss abweisen.
        self.assertIn("rechnen", antwort.daten["fehler"])

    def test_ziele_auflisten(self):
        antwort = dienst.bearbeite("ziele", self.rumpf())
        ids = {z["id"] for z in antwort.daten["ziele"]}
        self.assertIn("beton.b1.f_cd", ids)
        self.assertIn("betonstahl.s1.f_yd", ids)
        self.assertTrue(all("symbol" in z for z in antwort.daten["ziele"]))

    def test_alles_rechnen(self):
        antwort = dienst.bearbeite("alles", self.rumpf())
        self.assertGreater(len(antwort.daten["werte"]), 30)

    def test_katalog_und_beispiel_brauchen_keinen_rumpf(self):
        self.assertIn("betonsorten", dienst.bearbeite("katalog").daten)
        self.assertTrue(dienst.bearbeite("beispiel").daten["materialien"])

    def test_bericht_schreibt_nichts(self):
        antwort = dienst.bearbeite("bericht", self.rumpf())
        self.assertIn(r"\documentclass", antwort.daten["tex"])
        # Kein Pfad in der Antwort: der Dienst fasst die Platte nicht an.
        self.assertNotIn("tex_pfad", antwort.daten)

    def test_pruefen_reicht_das_projekt_aufgeraeumt_zurueck(self):
        antwort = dienst.bearbeite("pruefen", self.rumpf())
        self.assertEqual(antwort.daten["projekt"], Projekt.beispiel().als_dict())

    def test_pruefen_meldet_kaputte_beschreibung(self):
        kaputt = Projekt.beispiel().als_dict()
        kaputt["materialien"][0]["name"] = kaputt["materialien"][1]["name"]
        antwort = dienst.bearbeite("pruefen", {"projekt": kaputt})
        self.assertEqual(antwort.status, 400)

    def test_pruefen_weist_fremde_dateien_ab(self):
        """
        Projekt.aus_dict ist mit Absicht nachsichtig und macht aus jedem dict
        notfalls ein leeres Projekt. Beim Öffnen einer Datei wäre das fatal:
        eine beliebige JSON-Datei würde die Arbeit wortlos durch nichts
        ersetzen.
        """
        for fremd in ({}, {"foo": 1}, {"einkaufsliste": ["Brot"]}, [1, 2, 3], "text", None):
            with self.subTest(fremd=fremd):
                antwort = dienst.bearbeite("pruefen", {"projekt": fremd})
                self.assertEqual(antwort.status, 400)

    def test_pruefen_nimmt_auch_unvollstaendiges(self):
        """Ein Projekt ohne Querschnitte ist erlaubt -- man fängt ja irgendwo an."""
        antwort = dienst.bearbeite("pruefen", {"projekt": {"name": "Leer"}})
        self.assertEqual(antwort.status, 200)
        self.assertEqual(antwort.daten["projekt"]["name"], "Leer")

    def test_fehler_bringt_den_dienst_nicht_um(self):
        """Auch Unerwartetes kommt als Antwort zurueck, nicht als Ausnahme."""
        antwort = dienst.bearbeite("rechnen", {"projekt": {"materialien": "kein Feld"}})
        self.assertGreaterEqual(antwort.status, 400)
        self.assertIn("fehler", antwort.daten)


class TestDienstUeberJson(unittest.TestCase):
    """Der Weg, den die Bruecke im Browser nimmt."""

    def test_umschlag(self):
        roh = dienst.bearbeite_json(
            "rechnen", json.dumps({"projekt": Projekt.beispiel().als_dict()}))
        umschlag = json.loads(roh)
        self.assertEqual(umschlag["status"], 200)
        self.assertTrue(umschlag["daten"]["vollstaendig"])

    def test_kaputtes_json(self):
        umschlag = json.loads(dienst.bearbeite_json("rechnen", "{nicht json"))
        self.assertEqual(umschlag["status"], 400)

    def test_rumpf_muss_ein_objekt_sein(self):
        umschlag = json.loads(dienst.bearbeite_json("rechnen", "[1, 2, 3]"))
        self.assertEqual(umschlag["status"], 400)

    def test_kein_rumpf(self):
        umschlag = json.loads(dienst.bearbeite_json("katalog"))
        self.assertEqual(umschlag["status"], 200)

    def test_json_bleibt_lesbar_fuer_den_browser(self):
        """
        Unendliche Werte kommen in Nachweisen vor (Erfüllungsgrad ohne
        Einwirkung). json.dumps schriebe dafür ``Infinity`` -- gültiges Python,
        ungültiges JSON, und JSON.parse im Browser bricht ab.
        """
        roh = dienst.bearbeite_json(
            "rechnen", json.dumps({"projekt": Projekt.beispiel().als_dict()}))
        self.assertNotIn("Infinity", roh)
        self.assertNotIn("NaN", roh)


class TestServerHuelle(unittest.TestCase):
    """Was der Server über den Dienst hinaus beisteuert."""

    def test_ohne_pdf_bleibt_die_platte_unberuehrt(self):
        antwort = server.bericht_mit_pdf(
            {"projekt": Projekt.beispiel().als_dict(), "pdf": False})
        self.assertIn(r"\documentclass", antwort.daten["tex"])
        self.assertNotIn("tex_pfad", antwort.daten)

    def test_mit_pdf_wird_das_tex_abgelegt(self):
        alt = server.AUSGABE_ORDNER
        try:
            with tempfile.TemporaryDirectory() as ordner:
                server.AUSGABE_ORDNER = Path(ordner)
                antwort = server.bericht_mit_pdf(
                    {"projekt": Projekt.beispiel().als_dict()})
                abgelegt = Path(antwort.daten["tex_pfad"])
                self.assertTrue(abgelegt.is_file())
                # Auf der Platte steht genau das, was auch der Browser bekäme.
                self.assertEqual(
                    abgelegt.read_text(encoding="utf-8"), antwort.daten["tex"])
        finally:
            server.AUSGABE_ORDNER = alt

    def test_statische_pfade_bleiben_im_projekt(self):
        for pfad in ("/../../etc/passwd", "/daten/projekt.json", "/.git/config",
                     "/gibtesnicht", "/tests/test_projekt_web.py",
                     "/web/../daten/projekt.json"):
            with self.subTest(pfad=pfad):
                self.assertIsNone(server.aufloesen(pfad))

        for pfad in ("/", "/index.html", "/web/index.html",
                     "/opencivil/projekt.py", "/opencivil/web/dienst.py"):
            with self.subTest(pfad=pfad):
                self.assertIsNotNone(server.aufloesen(pfad))

    def test_der_kern_ist_ueber_das_netz_erreichbar(self):
        """
        Die Brücke im Browser lädt den Rechenkern als ``.py``-Dateien nach.
        Läge ``opencivil/`` nicht im ausgelieferten Baum, bliebe die Seite
        stumm -- lokal wie auf GitHub Pages.
        """
        self.assertIn("opencivil", server.OEFFENTLICH)
        for datei in bruecke.kerndateien():
            with self.subTest(datei=datei):
                self.assertIsNotNone(server.aufloesen("/" + datei))


class TestBruecke(unittest.TestCase):
    """Das Manifest, aus dem der Browser den Rechenkern zusammenliest."""

    def test_manifest_ist_auf_dem_stand_der_quellen(self):
        self.assertTrue(
            bruecke.stimmt_ueberein(),
            "web/kern/dateien.json passt nicht mehr zu den Dateien unter "
            "opencivil/. Bitte 'python3 -m opencivil.web.bruecke' laufen lassen -- "
            "sonst lädt die Seite einen veralteten Kern.")

    def test_der_dienst_ist_im_manifest(self):
        dateien = bruecke.kerndateien()
        self.assertIn("opencivil/web/dienst.py", dateien)
        self.assertIn("opencivil/projekt.py", dateien)

    def test_kein_zwischenstand_im_manifest(self):
        self.assertFalse(
            [d for d in bruecke.kerndateien() if "__pycache__" in d])

    def test_schreiben_ist_wiederholbar(self):
        """Zweimal geschrieben ergibt zeichengleich dasselbe -- sonst rauscht das Diff."""
        with tempfile.TemporaryDirectory() as ordner:
            a = bruecke.schreiben(Path(ordner) / "a.json").read_text(encoding="utf-8")
            b = bruecke.schreiben(Path(ordner) / "b.json").read_text(encoding="utf-8")
        self.assertEqual(a, b)


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
        # Über bearbeite_json, also über genau den Weg, den der Browser nimmt:
        # nach_json wirft bei Infinity, statt es stumm durchzulassen.
        text = dienst.bearbeite_json(
            "rechnen", json.dumps({"projekt": projekt.als_dict()}))
        self.assertEqual(json.loads(text)["status"], 200)
        self.assertNotIn("Infinity", text)
        self.assertNotIn("NaN", text)

    def test_jede_antwort_ist_ohne_sonderwerte(self):
        for art in ("N_konstant", "M_konstant", "naechster_Punkt"):
            with self.subTest(art=art):
                projekt = Projekt.beispiel()
                for k in projekt.querschnitte[0].kombinationen:
                    k.art, k.N_Ed, k.M_Ed = art, 0.0, 0.0
                umschlag = json.loads(dienst.bearbeite_json(
                    "rechnen", json.dumps({"projekt": projekt.als_dict()})))
                self.assertEqual(umschlag["status"], 200)


class TestUnbenutztesMaterial(unittest.TestCase):
    """
    Ein Material, das noch keine Platte verwendet, muss trotzdem gerechnet
    werden -- sonst stünden im Editor leere Felder, obwohl die Sorte alles
    hergibt.
    """

    def test_unbenutzter_beton_wird_gerechnet(self):
        projekt = Projekt.beispiel()
        projekt.materialien.append(MaterialEintrag("b2", "beton", "C12/15", "C12/15"))
        werte = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()}).daten["werte"]
        eigene = [k for k in werte if k.startswith("beton.b2.")]
        self.assertGreaterEqual(len(eigene), 12)
        self.assertIn("beton.b2.f_cd", werte)

    def test_unbenutzter_stahl_wird_gerechnet(self):
        projekt = Projekt.beispiel()
        projekt.materialien.append(MaterialEintrag("s2", "betonstahl", "B700B", "B700B"))
        werte = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()}).daten["werte"]
        self.assertIn("betonstahl.s2.f_yd", werte)

    def test_materialziele_umfassen_alle_kennwerte(self):
        aufbau = Projekt.beispiel().aufbauen()
        ziele = aufbau.materialziele()
        self.assertIn("beton.b1.f_cd", ziele)
        self.assertIn("betonstahl.s1.f_yd", ziele)


if __name__ == "__main__":
    unittest.main()


class TestAngabengruppen(unittest.TestCase):
    """
    Die Plattenangaben stehen in zwei Kästen -- bleiben aber einzelne Blöcke.

    Das ist der Kern: würde man sie im Protokoll zu *einem* Block verschmelzen,
    verlöre die Rückverfolgung ihre Auflösung. Wird nur `h` gebraucht, läuft
    auch nur dessen Vorgabe, und dann steht im Kasten eben nur `h`.
    """

    def gruppen(self, ziele=None):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": Projekt.beispiel().als_dict(), "ziele": ziele})
        self.assertEqual(antwort.status, 200)
        gefunden = {}
        for block in antwort.daten["protokoll"]:
            if block.get("gruppe"):
                gefunden.setdefault(block["gruppe"], []).append(block["titel"])
        return gefunden

    def test_zwei_kaesten_statt_vier_zeilen(self):
        gruppen = self.gruppen()
        self.assertEqual(sorted(gruppen), ["Abmessungen – Beton C30/37", "Überdeckungen"])
        self.assertEqual(gruppen["Abmessungen – Beton C30/37"],
                         ["Plattendicke", "Betrachtete Breite"])
        self.assertEqual(gruppen["Überdeckungen"],
                         ["Überdeckung unten", "Überdeckung oben"])

    def test_die_betonsorte_steht_im_kastennamen(self):
        """
        Sie ist keine gerechnete Grösse und hat darum keine eigene Kette. Als
        Aufschrift des Kastens gilt sie dagegen immer -- eine Platte hat genau
        einen Beton.
        """
        self.assertIn("Beton C30/37", " ".join(self.gruppen()))

    def test_die_rueckverfolgung_verkleinert_den_kasten(self):
        nur_h = self.gruppen(["querschnitt.q1.h"])
        self.assertEqual(nur_h, {"Abmessungen – Beton C30/37": ["Plattendicke"]})

        nur_unten = self.gruppen(["querschnitt.q1.c_nom_unten"])
        self.assertEqual(nur_unten, {"Überdeckungen": ["Überdeckung unten"]})

    def test_ohne_plattenwerte_gibt_es_keinen_kasten(self):
        self.assertEqual(self.gruppen(["beton.b1.f_cd"]), {})

    def test_ein_ziel_das_alles_braucht_zeigt_alles(self):
        alle = self.gruppen(["querschnitt.q1.bewehrungsmass"])
        self.assertEqual(len(alle["Abmessungen – Beton C30/37"]), 2)
        self.assertEqual(len(alle["Überdeckungen"]), 2)

    def test_jede_angabe_behaelt_ihre_wert_id(self):
        """Ohne sie liesse sich im Kasten nichts einzeln hervorheben."""
        antwort = dienst.bearbeite("rechnen", {"projekt": Projekt.beispiel().als_dict()})
        ids = {b["wert_id"] for b in antwort.daten["protokoll"] if b.get("gruppe")}
        self.assertEqual(ids, {
            "querschnitt.q1.h", "querschnitt.q1.b",
            "querschnitt.q1.c_nom_unten", "querschnitt.q1.c_nom_oben",
        })
