"""Tests für die Projektbeschreibung und die JSON-Schnittstelle."""

import json
import tempfile
import unittest
from pathlib import Path

from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, N_PRO_MM2, Groesse
from opencivil.projekt import (
    Aufbau, GebrauchsfallEintrag, KnickEintrag, KombinationEintrag, LageEintrag,
    MaterialEintrag, PostenEintrag, Projekt, ProjektFehler,
    QuerkraftbewehrungEintrag, QuerschnittEintrag,
)
from opencivil.querschnitt.platte import Richtung
from opencivil.web import api, bruecke, dienst, server


class TestProjektBeschreibung(unittest.TestCase):
    def test_beispiel_baut_durch(self):
        aufbau = Projekt.beispiel().aufbauen()
        self.assertEqual(len(aufbau.baustoffe), 2)
        self.assertEqual(len(aufbau.querschnitte), 1)
        self.assertEqual(sorted(aufbau.nachweise), ["q1.x"])
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        self.assertTrue(loesung.vollstaendig)
        # Gefuehrt werden die 6 M-N-Nachweise. Die uebrigen rechnen still mit:
        # eingeschaltet hat sie niemand, und ungefragt in der Tabelle staenden
        # sie sonst bei jeder Platte.
        laut = [u for u in loesung.urteile if not u.still]
        self.assertEqual(len(laut), 3)
        self.assertTrue(all(u.art == "M-N" for u in laut))
        self.assertTrue([u for u in loesung.urteile if u.still])

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
            QuerkraftbewehrungEintrag: QuerkraftbewehrungEintrag(durchmesser=10.0),
            GebrauchsfallEintrag: GebrauchsfallEintrag("Gebrauch", M_Ed=70.0),
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
                    d_max=16.0, einlagenhoehe=40.0, k_c=0.6,
                    querkraftbewehrung=QuerkraftbewehrungEintrag(
                        durchmesser=10.0, stahl="s1", abstand_x=250.0,
                        abstand_y=None, anzahl_y=4.0,
                        alpha_min=35, alpha_max=42),
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
                                           art="M_konstant"),
                        KombinationEintrag("Stütze", -90.0, 0.0, 140.0,
                                           art="naechster_Punkt"),
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
        buegel = kopie.querschnitt("q1").querkraftbewehrung
        self.assertEqual((buegel.durchmesser, buegel.abstand_x), (10.0, 250.0))
        self.assertEqual((buegel.abstand_y, buegel.anzahl_y), (None, 4.0))
        self.assertEqual((buegel.alpha_min, buegel.alpha_max), (35, 42))
        self.assertEqual(kopie.querschnitt("q1").k_c, 0.6)

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
        # Der M-N-Nachweis entsteht (er liefert die Eckwerte), faellt aber
        # kein Urteil: ohne Schnittgroesse gibt es nichts zu beurteilen.
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        self.assertFalse([u for u in loesung.urteile if u.art == "M-N"])

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

        # Beide Platten sind gleich bewehrt, also fällt für beide gleich viel
        # an -- gefragt ist hier nur, dass nichts vermischt wird.
        self.assertEqual(len(je_platte["querschnitt.q1"]),
                         len(je_platte["querschnitt.q2"]))
        self.assertTrue(je_platte["querschnitt.q1"])
        # Und die Namen allein hätten es nicht entschieden -- sie sind gleich.
        self.assertEqual(sorted(je_platte["querschnitt.q1"]),
                         sorted(je_platte["querschnitt.q2"]))

    def test_der_raum_steht_auch_in_der_json_antwort(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": self.zweiplattenprojekt().als_dict()})
        raeume = {u["raum"] for u in antwort.daten["urteile"]}
        self.assertTrue(all(r.startswith("querschnitt.q") for r in raeume), raeume)
        # 2 Platten, je ein M-N-Nachweis in x -- mehr ist im Beispiel nicht
        # eingeschaltet, und die stillen Nachweise stehen nicht in dieser Liste.
        self.assertEqual(len(raeume), 2)


class TestNeuePlatteKommtAusDemKern(unittest.TestCase):
    """
    Die Vorlage für eine frische Platte steht an *einer* Stelle.

    Sie stand einmal auch in der Oberfläche, als Wortschatz aus zwanzig
    Feldern. Als sich die Vorgaben änderten, blieb die Kopie stehen und neue
    Platten brachten Nachweise eingeschaltet mit, die überall sonst aus waren.
    """

    def test_der_katalog_traegt_sie(self):
        vorlage = api.katalog()["neue_platte"]
        self.assertEqual(vorlage["h"], 300.0)
        # Alle vier: die y-Lagen liegen aussen und kosten x seine statische
        # Höhe -- sie leer zu lassen hiesse, mit einer Höhe zu rechnen, die es
        # auf der Baustelle nicht gibt.
        self.assertEqual([l["grund"]["durchmesser"] for l in vorlage["lagen"]],
                         [12.0] * 4)
        self.assertEqual(vorlage["kombinationen"][0]["M_Ed"], 30.0)

    def test_ihre_nachweise_sind_ausgeschaltet(self):
        vorlage = api.katalog()["neue_platte"]
        for feld in ("duktilitaet", "sproede", "zwaengung_biegung", "zwaengung"):
            with self.subTest(feld=feld):
                self.assertIs(vorlage[feld], False)
        self.assertFalse(vorlage["haeufige_aus_tragsicherheit"])

    def test_sie_folgt_den_vorgaben_der_beschreibung(self):
        """
        Der eigentliche Punkt: kein zweiter Satz Vorgaben. Ändert sich einer
        in QuerschnittEintrag, ändert sich die Vorlage mit.
        """
        from opencivil.projekt import QuerschnittEintrag

        vorlage = api.katalog()["neue_platte"]
        leer = QuerschnittEintrag(kennung="x", name="x", beton="b").als_dict()
        for feld in ("duktilitaet", "sproede", "zwaengung_biegung", "zwaengung",
                     "haeufige_aus_tragsicherheit", "automatik_modus",
                     "automatik_teilungen", "automatik_mindestdurchmesser",
                     "rissanforderung", "kriechzahl", "d_max", "k_c", "b"):
            with self.subTest(feld=feld):
                self.assertEqual(vorlage[feld], leer[feld])

    def test_sie_laesst_sich_ohne_nacharbeit_rechnen(self):
        """Was die Oberfläche einfügt, muss der Kern auch wieder annehmen."""
        vorlage = dict(api.katalog()["neue_platte"])
        vorlage.update(kennung="q9", name="Platte 9", beton="b1")
        for lage in vorlage["lagen"]:
            lage["stahl"] = "s1"
        vorlage["querkraftbewehrung"]["stahl"] = "s1"

        d = Projekt.beispiel().als_dict()
        d["querschnitte"].append(vorlage)
        antwort = dienst.bearbeite("rechnen", {"projekt": d})
        self.assertEqual(antwort.status, 200)
        self.assertIn("q9", antwort.daten["zusammenfassungen"])


class TestDoppelteFallnamen(unittest.TestCase):
    """
    Zwei Lastfälle gleichen Namens ergaben eine Zeile statt zwei.

    Die Nachweise legen ihre Ergebniswerte unter dem Fallnamen ab -- M-N,
    Querkraft und Stahlspannung alle drei. Der zweite überschrieb den ersten,
    ohne Fehler und ohne Warnung: in der Tabelle fehlte einfach eine Zeile.
    """

    def test_zwei_gleiche_kombinationen_werden_gemeldet(self):
        from opencivil.projekt import KombinationEintrag

        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        q.kombinationen = [KombinationEintrag(name="Feld", M_Ed=30.0),
                           KombinationEintrag(name="Feld", M_Ed=99.0)]
        with self.assertRaises(ProjektFehler) as fehler:
            projekt.aufbauen()
        self.assertIn("'Feld' ist zweimal", str(fehler.exception))

    def test_auch_haeufige_und_knickfaelle(self):
        from opencivil.projekt import GebrauchsfallEintrag, KnickEintrag

        for feld, eintraege in (
            ("haeufige", [GebrauchsfallEintrag("Gebrauch"), GebrauchsfallEintrag("Gebrauch")]),
            ("knickfaelle", [KnickEintrag("Stütze", N_Ed=-100.0, laenge=3.0,
                                          knicklaenge=3.0),
                             KnickEintrag("Stütze", N_Ed=-200.0, laenge=3.0,
                                          knicklaenge=3.0)]),
        ):
            with self.subTest(feld=feld):
                projekt = Projekt.beispiel()
                setattr(projekt.querschnitt("q1"), feld, eintraege)
                with self.assertRaises(ProjektFehler):
                    projekt.aufbauen()

    def test_ein_eigener_fall_darf_nicht_wie_der_abgeleitete_heissen(self):
        """
        Die abgeleiteten tragen den Namen ihrer Kombination mit angehängtem
        Anteil -- wer genau so benennt, trifft denselben Schlüssel.
        """
        from opencivil.projekt import GebrauchsfallEintrag

        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        q.rissanforderung = "hoch"
        q.haeufige = [GebrauchsfallEintrag(f"{q.kombinationen[0].name} (70 %)",
                                     M_Ed=70.0)]
        with self.assertRaises(ProjektFehler) as fehler:
            projekt.aufbauen()
        self.assertIn("abgeleitete", str(fehler.exception))

    def test_verschiedene_namen_gehen_weiterhin(self):
        """Die Regel darf nicht mehr verbieten als sie muss."""
        from opencivil.projekt import GebrauchsfallEintrag

        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        q.rissanforderung = "hoch"
        q.haeufige = [GebrauchsfallEintrag("Gebrauch", M_Ed=70.0),
                      GebrauchsfallEintrag("Gebrauch selten", M_Ed=40.0)]
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        self.assertEqual(antwort.status, 200)

    def test_zwei_platten_duerfen_dieselben_namen_tragen(self):
        """Der Name muss je Platte eindeutig sein, nicht im ganzen Projekt."""
        d = Projekt.beispiel().als_dict()
        zweite = json.loads(json.dumps(d["querschnitte"][0]))
        zweite["kennung"], zweite["name"] = "q2", "Decke über 1. OG"
        d["querschnitte"].append(zweite)
        self.assertEqual(dienst.bearbeite("rechnen", {"projekt": d}).status, 200)


class TestKurzeSchalterlisten(unittest.TestCase):
    """
    Von Hand gebaute Beschreibungen sind der zweite Weg ins Werkzeug.

    `aus_dict` bringt die Schalterlisten auf vier; wer das Feld nachträglich
    zuweist, läuft daran vorbei. Der Aufbau quittierte das mit einem nackten
    IndexError.
    """

    def test_eine_kurze_liste_stuerzt_nicht_ab(self):
        for feld, kurz in (("duktilitaet", [True]),
                           ("sproede", []),
                           ("zwaengung_biegung", [False, True])):
            with self.subTest(feld=feld):
                projekt = Projekt.beispiel()
                setattr(projekt.querschnitt("q1"), feld, list(kurz))
                aufbau = projekt.aufbauen()
                aufbau.werk.loese(*aufbau.alle_nachweisziele())

    def test_die_angegebenen_schalter_gelten_trotzdem(self):
        projekt = Projekt.beispiel()
        projekt.querschnitt("q1").duktilitaet = [True]
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        self.assertEqual(len([u for u in loesung.gefuehrte_urteile
                              if u.art == "D"]), 1)


class TestSpannungsnachweisNurWoGefordert(unittest.TestCase):
    """
    Bei normaler Rissanforderung steht in Tabelle 17 ein Strich.

    Die Maske nahm häufige Lastfälle trotzdem entgegen und rechnete sie
    stillschweigend nicht. Welche Anforderung den Nachweis verlangt, sagt
    jetzt der Katalog -- damit die Oberfläche es sagen kann, ohne die Norm
    ein zweites Mal aufzuschreiben.
    """

    def test_der_katalog_sagt_es(self):
        nach_wert = {r["wert"]: r["spannungsnachweis"]
                     for r in api.katalog()["rissanforderungen"]}
        self.assertEqual(nach_wert,
                         {"normal": False, "erhoeht": True, "hoch": True})

    def test_und_es_stimmt_mit_dem_ueberein_was_gebaut_wird(self):
        from opencivil.projekt import GebrauchsfallEintrag

        for eintrag in api.katalog()["rissanforderungen"]:
            projekt = Projekt.beispiel()
            q = projekt.querschnitt("q1")
            q.rissanforderung = eintrag["wert"]
            q.haeufige = [GebrauchsfallEintrag("Gebrauch", M_Ed=70.0)]
            with self.subTest(anforderung=eintrag["wert"]):
                self.assertEqual(bool(projekt.aufbauen().spannung),
                                 eintrag["spannungsnachweis"])


class TestStilleNachweise(unittest.TestCase):
    """
    Ausgeschaltet heisst still, nicht weg.

    Ein Schalter sagt «interessiert mich gerade nicht» und nicht «gilt nicht».
    Gerechnet wird darum weiter; was nicht aufgeht, steht als Hinweis unter
    der Zusammenfassung -- nicht in der Tabelle und nicht in der Herleitung.
    """

    def platte(self) -> Projekt:
        """
        Zu schwach bewehrt für ihr Rissmoment -- sprödes Versagen fällt durch.

        Die Einwirkung ist klein gehalten, damit die Tragsicherheit aufgeht:
        geprüft wird hier, was ein *stiller* Nachweis auslöst, und ein lauter
        daneben, der ebenfalls durchfällt, würde das verdecken.
        """
        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        q.h = 600.0
        for k in q.kombinationen:
            k.M_Ed, k.N_Ed, k.V_Ed = 10.0, 0.0, 0.0
        # Beide x-Lagen dünn: geprüft wird der schlechtere Fall, und der soll
        # am sprödem Versagen scheitern und nicht daran, dass eine Lage fehlt.
        for nummer in (1, 2, 3, 4):
            if q.richtung_von(nummer).value != "x":
                continue
            lage = q.lagen[nummer - 1]
            lage.grund.durchmesser, lage.grund.abstand = 6.0, 300.0
            lage.zulage.durchmesser = 0.0
        return projekt

    def antwort(self, projekt: Projekt) -> dict:
        return dienst.bearbeite(
            "rechnen", {"projekt": projekt.als_dict()}
        ).daten["zusammenfassungen"]["q1"]

    def test_der_hinweis_steht_unter_der_tabelle(self):
        tabelle = self.antwort(self.platte())
        stille = [h for h in tabelle["stille"]
                  if h["nachweis"].startswith("Sprödes Versagen")]
        self.assertTrue(stille, tabelle["stille"])
        self.assertEqual(len(stille), 1)          # eine Zeile, nicht zwei
        self.assertLess(float(stille[0]["grad"]), 1.0)

    def test_und_nicht_in_der_tabelle(self):
        tabelle = self.antwort(self.platte())
        arten = {z["zellen"][0] for z in tabelle["zeilen"]}
        self.assertNotIn(r"\text{Sprödes Versagen}", arten)

    def test_und_nicht_in_der_herleitung(self):
        from opencivil.core.protokoll import TitelBlock

        aufbau = self.platte().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        texte = [b.text for b in loesung.protokoll.alle_bloecke()
                 if isinstance(b, TitelBlock)]
        self.assertFalse([t for t in texte if "Sprödes Versagen" in t])

    def test_er_zaehlt_nicht_im_gesamturteil(self):
        """
        Sonst stünde oben rechts «nicht erfüllt» wegen eines Nachweises, den
        niemand führt -- und in der Tabelle fände man dazu nichts.
        """
        aufbau = self.platte().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        durchgefallen = [u for u in loesung.urteile if not u.erfuellt]
        self.assertTrue(durchgefallen)
        self.assertTrue(all(u.still for u in durchgefallen))
        self.assertTrue(loesung.alle_nachweise_erfuellt)

    def test_eingeschaltet_wechselt_er_die_seite(self):
        projekt = self.platte()
        projekt.querschnitt("q1").sproede = True
        tabelle = self.antwort(projekt)
        self.assertFalse([h for h in tabelle["stille"]
                          if h["nachweis"].startswith("Sprödes Versagen")])
        arten = {z["zellen"][0] for z in tabelle["zeilen"]}
        self.assertIn(r"\text{Sprödes Versagen}", arten)

    def test_was_aufgeht_meldet_sich_nicht(self):
        """
        Ein Hinweis zu jedem stillen Nachweis wäre bloss Rauschen -- gemeldet
        wird nur, was nicht aufgeht.
        """
        tabelle = self.antwort(Projekt.beispiel())
        # Die Duktilität geht im Beispiel auf, sie steht also nirgends.
        self.assertFalse([h for h in tabelle["stille"]
                          if h["nachweis"].startswith("Duktilität")])
        for hinweis in tabelle["stille"]:
            self.assertLess(float(hinweis["grad"]), 1.0, hinweis)

    def test_der_grad_spricht_die_sprache_seines_empfaengers(self):
        """
        `\\infty` gehört in die LaTeX-Tabelle, `∞` in den Fliesstext daneben.
        Eine Funktion, die immer LaTeX lieferte, schrieb im Hinweis wörtlich
        «α_eff = \\infty».
        """
        from opencivil.core.berechnung import NachweisUrteil
        from opencivil.core.einheiten import EINHEITSLOS, Groesse

        unendlich = NachweisUrteil(
            name="Probe", erfuellt=True,
            erfuellungsgrad=Groesse(float("inf"), EINHEITSLOS))
        self.assertEqual(unendlich.gradtext(latex=True), r"\infty")
        self.assertEqual(unendlich.gradtext(), "∞")

        endlich = NachweisUrteil(
            name="Probe", erfuellt=True,
            erfuellungsgrad=Groesse(2.345, EINHEITSLOS))
        self.assertEqual(endlich.gradtext(), "2.35")
        self.assertEqual(endlich.gradtext(latex=True), "2.35")

    def test_ein_knapp_verfehlter_grad_liest_sich_nicht_als_eins(self):
        """
        «nicht erfüllt (α_eff = 1.00)» widerspricht sich selbst. Die zweite
        Stelle rundet 0.997 auf eins -- dann kommt eine dritte dazu.
        """
        tabelle = self.antwort(Projekt.beispiel())
        knapp = [h for h in tabelle["stille"]
                 if h["nachweis"].startswith("Zwängung auf Normalkraft")]
        self.assertTrue(knapp, tabelle["stille"])
        for hinweis in knapp:
            self.assertEqual(hinweis["grad"], "0.996")


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
        # Nur die gefuehrten Nachweise -- die stillen stehen als Hinweis unter
        # der Zusammenfassung, nicht in dieser Liste.
        # 3 M-N-Fälle in x; mehr ist im Beispiel nicht eingeschaltet.
        self.assertEqual(len(antwort.daten["urteile"]), 3)
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
        self.assertEqual(sorted(kurven), ["q1.x"])
        self.assertEqual(kurven["q1.x"]["N_Ed"], 0.0)
        self.assertEqual(len(kurven["q1.x"]["aeste"]), 2)

    def test_querkraftkurven_mit_gewaehlter_normalkraft(self):
        rumpf = {**self.mit_querkraft(), "n_ed": {"q1.x": -300.0}}
        kurven = dienst.bearbeite("querkraftkurven", rumpf).daten["querkraftkurven"]
        self.assertEqual(kurven["q1.x"]["N_Ed"], -300.0)
        self.assertEqual(sorted(kurven), ["q1.x"])   # in y wird nichts geführt

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
        self.assertEqual(sorted(aufbau.nachweise), ["q1.x", "q2.x"])
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


class TestNurDieTragrichtungX(unittest.TestCase):
    """
    Schnittgrössen gehören immer zur Tragrichtung x.

    Je Kombination war das einmal wählbar -- x, y oder beide. Nachgewiesen
    wird nur noch x: die y-Lagen stehen im Querschnitt, weil sie die statische
    Höhe von x bestimmen und zum Bewehrungsgehalt zählen, aber kein Nachweis
    fragt nach ihnen. Die halbe Tabelle handelte von einer Richtung, für die
    niemand Schnittgrössen hatte.
    """

    def test_jede_kombination_wirkt_in_x(self):
        projekt = Projekt.beispiel()
        mn = [u for u in self._loesen(projekt).urteile if u.art == "M-N"]
        self.assertEqual(len(mn), len(projekt.querschnitt("q1").kombinationen))
        self.assertTrue(all("Nachweis x" in u.name for u in mn))

    def test_in_y_entsteht_kein_nachweis(self):
        aufbau = Projekt.beispiel().aufbauen()
        for feld in Aufbau.NACHWEISFELDER:
            with self.subTest(feld=feld):
                self.assertFalse([s for s in getattr(aufbau, feld)
                                  if s.endswith(".y")])

    def test_eine_alte_richtung_stoert_nicht(self):
        """``x`` und ``beide`` heissen beide: gilt in x. Das Feld entfällt."""
        for richtung in ("x", "beide"):
            with self.subTest(richtung=richtung):
                eintrag = KombinationEintrag.aus_dict(
                    {"name": "Feld", "M_Ed": 100.0, "richtung": richtung})
                self.assertEqual(eintrag.M_Ed, 100.0)
                self.assertFalse(hasattr(eintrag, "richtung"))

    def test_ein_reiner_y_lastfall_wird_gemeldet(self):
        """
        Ihn stillschweigend auf x umzudeuten hiesse, eine Zahl an einem
        anderen Querschnitt anzusetzen als der Benutzer gemeint hat.
        """
        for klasse, was in ((KombinationEintrag, "Einwirkung"),
                            (GebrauchsfallEintrag, "häufige Lastfall")):
            with self.subTest(klasse=klasse.__name__):
                with self.assertRaises(ProjektFehler) as fehler:
                    klasse.aus_dict({"name": "Feld", "M_Ed": 100.0,
                                     "richtung": "y"})
                self.assertIn("nur in y-Richtung", str(fehler.exception))

    def test_ohne_kombination_bleibt_es_stumm(self):
        """
        Keine Kombination ist eine Entscheidung des Benutzers, kein Mangel --
        dafür gibt es keine Warnung. Der M-N-Nachweis entsteht trotzdem: er
        liefert die Eckwerte der Resistenzlinie, und die gehören dem
        Querschnitt. Ein **Urteil** fällt er ohne Kombination nicht.
        """
        projekt = Projekt.beispiel()
        projekt.querschnitt("q1").kombinationen = []
        aufbau = projekt.aufbauen()
        self.assertEqual(sorted(aufbau.nachweise), ["q1.x"])
        self.assertEqual(aufbau.nachweise["q1.x"].kombinationen, [])
        # Eine Warnung gibt es -- dass ohne Schnittgrössen kein
        # Tragsicherheitsnachweis läuft. Das ist keine Aussage über die
        # Richtung, und genau darum geht es hier nicht.
        self.assertFalse([w for w in aufbau.warnungen if "Richtung" in w])

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


class TestNachweisfelder(unittest.TestCase):
    """
    Die eine Liste, aus der Rechenziele, Aufteilen und Zwischenspeichern
    folgen. Stimmt sie nicht, fällt ein Nachweis stillschweigend aus allen
    dreien heraus.
    """

    def aufbau(self):
        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        q.rissanforderung = "hoch"
        q.zwaengung = q.zwaengung_biegung = q.sproede = True
        q.duktilitaet = True
        q.knickfaelle = [KnickEintrag("Stütze", N_Ed=-500.0, M_Ed_1=20.0)]
        for k in q.kombinationen:
            k.V_Ed = 80.0
        return projekt.aufbauen(schnell=True)

    def test_jedes_feld_gibt_es_auch(self):
        aufbau = self.aufbau()
        for feld in Aufbau.NACHWEISFELDER:
            with self.subTest(feld=feld):
                self.assertIsInstance(getattr(aufbau, feld), dict)

    def test_jeder_nachweis_traegt_seine_ausnutzung(self):
        """
        Der Querkraftnachweis hiess sie einmal `d_grad` und brauchte darum
        eine eigene Zeile in der Zielliste. Jetzt heissen alle gleich.
        """
        aufbau = self.aufbau()
        nachweise = list(aufbau.alle_nachweise())
        self.assertGreaterEqual(len(nachweise), 7)
        for n in nachweise:
            with self.subTest(nachweis=type(n).__name__):
                self.assertTrue(n.d_ausnutzung)

    def test_kein_nachweis_faellt_aus_der_zielliste(self):
        aufbau = self.aufbau()
        aus_feldern = {d.id for n in aufbau.alle_nachweise()
                       for d in n.d_ausnutzung.values()}
        self.assertEqual(set(aufbau.alle_nachweisziele()), aus_feldern)

    def test_jeder_nachweis_gehoert_zu_genau_einer_platte(self):
        """Sonst käme ein Ergebnis beim Zwischenspeichern doppelt oder gar nicht."""
        aufbau = self.aufbau()
        eigene = aufbau.ziele_von("q1")
        self.assertEqual(sorted(eigene),
                         sorted(aufbau.eckwertziele() + aufbau.alle_nachweisziele()))


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
                         ["Plattendicke", "Betrachtete Breite (x)",
                          "Betrachtete Breite (y)"])
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
        self.assertEqual(len(alle["Abmessungen – Beton C30/37"]), 3)
        self.assertEqual(len(alle["Überdeckungen"]), 2)

    def test_die_zusammenfassung_kommt_fertig_aus_dem_kern(self):
        """
        Zeilen und LaTeX an einer Stelle. Die Oberfläche baute sie früher ein
        zweites Mal zusammen -- einmal fürs Auge, einmal für den Kopierknopf,
        und die beiden liefen auseinander.
        """
        antwort = dienst.bearbeite("rechnen", {"projekt": Projekt.beispiel().als_dict()})
        tabelle = antwort.daten["zusammenfassungen"]["q1"]

        # Fuenf Spalten: Nachweis, Bezeichnung, Widerstand, Einwirkung,
        # Erfuellungsgrad. Eine Spalte "Urteil" gab es einmal; sie stand neben
        # dem Grad und sagte dasselbe noch einmal.
        self.assertEqual(len(tabelle["kopf"]), 5)
        # 3 x M-N in x -- die uebrigen Nachweise rechnen still mit und
        # stehen darum nicht in der Tabelle.
        self.assertEqual(len(tabelle["zeilen"]), 3)
        for zeile in tabelle["zeilen"]:
            self.assertEqual(len(zeile["zellen"]), len(tabelle["kopf"]))
            self.assertIn("erfuellt", zeile)
        self.assertTrue(tabelle["latex"].startswith(r"\begin{array}"))
        # Welche Spalte eingefaerbt wird, sagt der Kern -- die Oberflaeche
        # soll es nicht aus der Kopfzeile erraten muessen.
        self.assertEqual(tabelle["kopf"][tabelle["grad_spalte"]], r"\alpha_{eff}")

    def test_nachweis_und_bezeichnung_stehen_getrennt(self):
        """
        Erste Spalte: was fuer ein Nachweis, ausgeschrieben und mit Richtung.
        Zweite Spalte: wie der Fall heisst.

        Beide kommen aus eigenen Feldern des Urteils und werden nicht aus dem
        langen Namen herausgeschnitten -- aus Anzeigetext auf Bedeutung zu
        schliessen geht schief, sobald jemand einen Fall "Nachweis Ost" nennt.
        """
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": Projekt.beispiel().als_dict()})
        zeilen = antwort.daten["zusammenfassungen"]["q1"]["zeilen"]
        paare = [(z["zellen"][0], z["zellen"][1]) for z in zeilen]
        self.assertIn((r"\text{Biegung und Normalkraft}", r"\text{Feld}"),
                      paare)
        # Dieselbe Kombination in y ist eine andere Zeile -- vorher waren beide
        # nicht zu unterscheiden.
        self.assertIn((r"\text{Biegung und Normalkraft}", r"\text{Feld}"),
                      paare)

    def test_der_querkraftwiderstand_ist_gross_geschrieben(self):
        projekt = Projekt.beispiel()
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 80.0
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        zeilen = antwort.daten["zusammenfassungen"]["q1"]["zeilen"]
        quer = [z for z in zeilen
                if z["zellen"][0].startswith(r"\text{Querkraft")]
        self.assertTrue(quer)
        for zeile in quer:
            self.assertTrue(zeile["zellen"][2].startswith("V_{Rd"), zeile["zellen"][2])
            self.assertTrue(zeile["zellen"][3].startswith("V_{Ed"), zeile["zellen"][3])
            self.assertNotIn("left|", zeile["zellen"][3])

    def test_ueber_der_tabelle_stehen_die_angaben_zur_platte(self):
        """
        Beton, Dicke, Breite -- und darunter die Bewehrung von unten nach oben.

        Beide kommen fertig aus dem Kern und tragen ihr eigenes LaTeX: in der
        Oberfläche sind es eine gewöhnliche Gleichung und eine gewöhnliche
        Tabelle, mit denselben Kopierknöpfen wie alles andere.
        """
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": Projekt.beispiel().als_dict()})
        tabelle = antwort.daten["zusammenfassungen"]["q1"]

        self.assertIn("C30/37", tabelle["angaben"]["latex"])
        self.assertIn("h = 300", tabelle["angaben"]["latex"])
        self.assertIn("b_x = 1000", tabelle["angaben"]["latex"])
        # b_y steht nur da, wenn es von b_x abweicht.
        self.assertNotIn("b_y", tabelle["angaben"]["latex"])

        bewehrung = tabelle["bewehrung"]
        self.assertTrue(bewehrung["latex"].startswith(r"\begin{array}"))
        erste = [z[0] for z in bewehrung["zeilen"]]
        # Wie man die Platte im Schnitt sieht: von oben nach unten, also
        # dieselbe Folge wie in der Eingabemaske.
        self.assertEqual(erste, [
            r"\text{Überdeckung oben}", r"\text{4. Lage}", r"\text{3. Lage}",
            r"\text{2. Lage}", r"\text{1. Lage}", r"\text{Überdeckung unten}",
        ])
        # Durchmesser, Teilung und Stahl stehen in derselben Zeile.
        erste_lage = bewehrung["zeilen"][4]
        self.assertIn(r"\varnothing 12@150", erste_lage[2])
        self.assertIn("B500B", erste_lage[3])

    def test_eine_leere_lage_steht_ohne_bewehrung_da(self):
        """Eine nicht definierte Lage darf keinen Stahl ausweisen."""
        projekt = Projekt.beispiel()
        lage = projekt.querschnitt("q1").lagen[1]
        lage.grund.durchmesser = 0.0
        lage.zulage.durchmesser = 0.0
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        zeilen = antwort.daten["zusammenfassungen"]["q1"]["bewehrung"]["zeilen"]
        zweite = next(z for z in zeilen if z[0] == r"\text{2. Lage}")
        self.assertEqual(zweite[2], r"\text{--}")
        self.assertEqual(zweite[3], r"\text{--}")

    def test_die_zahlen_der_tabelle_haben_feste_stellen(self):
        """In einer Spalte steht immer dieselbe Grösse, also auch dieselbe Genauigkeit."""
        antwort = dienst.bearbeite("rechnen", {"projekt": Projekt.beispiel().als_dict()})
        erste = antwort.daten["zusammenfassungen"]["q1"]["zeilen"][0]["zellen"]
        self.assertIn("100.0", erste[3])          # M_Ed, eine Nachkommastelle
        self.assertRegex(erste[4], r"^\d+\.\d{2}$")  # alpha, zwei

    def test_ohne_einwirkung_bleibt_die_mindestbewehrung(self):
        """
        Ohne Schnittgrössen und ohne Duktilität bleiben die Rissmomente.

        Sprödes Versagen unter Biegung geht jede Platte an -- unabhängig von
        Zwängung und Einwirkung. Eine Bewehrung, die das Rissmoment nicht
        übernehmen kann, kündigt nichts an.
        """
        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        q.kombinationen = []
        q.duktilitaet = [False] * 4
        q.sproede = True
        q.zwaengung_biegung = True
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        namen = [z["zellen"][0]
                 for z in antwort.daten["zusammenfassungen"]["q1"]["zeilen"]]
        self.assertTrue(namen)
        self.assertEqual(sorted(namen),
                         [r"\text{Sprödes Versagen}",
                          r"\text{Zwängung auf Biegung}"])

    def test_die_duktilitaet_laeuft_auch_ohne_schnittgroessen(self):
        projekt = Projekt.beispiel()
        projekt.querschnitt("q1").kombinationen = []
        projekt.querschnitt("q1").duktilitaet = [True, False, False, True]
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        namen = [z["zellen"][0]
                 for z in antwort.daten["zusammenfassungen"]["q1"]["zeilen"]]
        # Eine Zeile: die ungünstigere der beiden x-Lagen.
        self.assertEqual(namen, [r"\text{Duktilität}"])

    def test_jede_angabe_behaelt_ihre_wert_id(self):
        """Ohne sie liesse sich im Kasten nichts einzeln hervorheben."""
        antwort = dienst.bearbeite("rechnen", {"projekt": Projekt.beispiel().als_dict()})
        ids = {b["wert_id"] for b in antwort.daten["protokoll"] if b.get("gruppe")}
        self.assertEqual(ids, {
            "querschnitt.q1.h", "querschnitt.q1.b", "querschnitt.q1.b_y",
            "querschnitt.q1.c_nom_unten", "querschnitt.q1.c_nom_oben",
        })


class TestQuerkraftbewehrungInDerAusgabe(unittest.TestCase):
    """Was die Oberfläche von den Bügeln zu sehen bekommt."""

    def projekt(self, **buegel) -> dict:
        p = Projekt.beispiel()
        q = p.querschnitt("q1")
        for k in q.kombinationen:
            k.V_Ed = 150.0
            k.richtung = "x"
        b = q.querkraftbewehrung
        b.durchmesser, b.stahl = 10.0, "s1"
        b.abstand_x, b.abstand_y = 200.0, 200.0
        for name, wert in buegel.items():
            setattr(b, name, wert)
        return p.als_dict()

    def test_die_buegel_stehen_in_der_bewehrungsuebersicht(self):
        antwort = dienst.bearbeite("rechnen", {"projekt": self.projekt()})
        zeilen = antwort.daten["zusammenfassungen"]["q1"]["bewehrung"]["zeilen"]
        letzte = zeilen[-1]
        self.assertEqual(letzte[0], r"\text{Querkraftbewehrung}")
        # Kurzform wie bei den Lagen: Durchmesser und die beiden Teilungen.
        self.assertEqual(letzte[2], r"\varnothing 10@200@200")
        self.assertIn("B500B", letzte[3])
        # Der Bügelquerschnitt steht in der Herleitung, wo er hergeleitet
        # wird -- in einer Übersicht ist er nur Ballast.
        self.assertNotIn(r"A_{\varnothing,V}", letzte[2])

    def test_eine_stabzahl_in_y_steht_als_stueckzahl_da(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": self.projekt(abstand_y=None, anzahl_y=5.0)})
        letzte = antwort.daten["zusammenfassungen"]["q1"]["bewehrung"]["zeilen"][-1]
        self.assertEqual(letzte[2], r"\varnothing 10@200@5\,\text{Stk}")

    def test_ohne_buegel_steht_dort_nichts(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": Projekt.beispiel().als_dict()})
        erste = [z[0] for z
                 in antwort.daten["zusammenfassungen"]["q1"]["bewehrung"]["zeilen"]]
        self.assertNotIn(r"\text{Querkraftbewehrung}", erste)

    def test_mit_buegeln_tritt_das_neigungsdiagramm_an_die_stelle_der_m_v_kurve(self):
        antwort = dienst.bearbeite("rechnen", {"projekt": self.projekt()})
        self.assertEqual(antwort.daten["querkraftkurven"], {})
        self.assertTrue(antwort.daten["neigungskurven"])

    def test_ohne_buegel_bleibt_es_bei_der_m_v_kurve(self):
        p = Projekt.beispiel()
        for k in p.querschnitt("q1").kombinationen:
            k.V_Ed = 150.0
        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        self.assertTrue(antwort.daten["querkraftkurven"])
        self.assertEqual(antwort.daten["neigungskurven"], {})

    def test_je_statischer_hoehe_ein_eigenes_bild(self):
        """
        Feld und Stütze haben verschiedene Vorzeichen des Moments, also
        verschiedene statische Höhen -- und damit verschiedene Kurven.
        """
        antwort = dienst.bearbeite("rechnen", {"projekt": self.projekt()})
        kurven = antwort.daten["neigungskurven"]
        hoehen = {round(k["d"], 6) for k in kurven.values()}
        self.assertEqual(len(kurven), len(hoehen))
        for kurve in kurven.values():
            self.assertTrue(kurve["faelle"])

    def test_die_kurve_reicht_ueber_die_grenzen_hinaus(self):
        """
        Gezeichnet wird von 25° bis 45°, blass ausserhalb der beiden Grenzen.
        Ein dort abgeschnittener Ast liesse offen, ob die Kurve endet oder der
        Bereich.
        """
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": self.projekt(alpha_min=35, alpha_max=40)})
        kurve = next(iter(antwort.daten["neigungskurven"].values()))
        winkel = [p["alpha"] for p in kurve["punkte"]]
        self.assertEqual(winkel, list(range(25, 46)))
        drin = [p["alpha"] for p in kurve["punkte"] if p["im_bereich"]]
        self.assertEqual(drin, list(range(35, 41)))

    def test_bei_zug_waechst_die_achse_mit(self):
        """α_min = 40 und α_max = 50 müssen beide ins Bild passen."""
        p = Projekt.beispiel()
        q = p.querschnitt("q1")
        q.kombinationen = [q.kombinationen[0]]
        q.kombinationen[0].V_Ed = 150.0
        q.kombinationen[0].N_Ed = 400.0
        b = q.querkraftbewehrung
        b.durchmesser, b.stahl = 10.0, "s1"
        b.abstand_x, b.abstand_y = 200.0, 200.0
        b.alpha_min, b.alpha_max = 30, 50

        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        kurve = next(iter(antwort.daten["neigungskurven"].values()))
        self.assertTrue(kurve["zug"])
        self.assertEqual((kurve["alpha_min"], kurve["alpha_max"]), (40, 50))
        self.assertEqual(kurve["punkte"][-1]["alpha"], 50)

    # Ein Widerstand von null trug seinen Grund -- geprüft wurde das an einer
    # Bügeldefinition, die in y nicht rechenbar war. In y wird nichts mehr
    # nachgewiesen; dieselbe Zusage prüft jetzt `TestOhneBewehrungInX`.

    def test_erfuellte_nachweise_tragen_keinen_hinweis(self):
        """Sonst stünde unter jeder Tabelle eine Wand aus Begründungen."""
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": Projekt.beispiel().als_dict()})
        zeilen = antwort.daten["zusammenfassungen"]["q1"]["zeilen"]
        self.assertTrue(zeilen)
        self.assertFalse([z for z in zeilen if z["erfuellt"] and z["hinweis"]])


class TestOhneBewehrungInX(unittest.TestCase):
    """
    Die Tragrichtung x ohne jeden Bewehrungsposten.

    Der Nachweis entfiel früher stillschweigend: wer eine Einwirkung angegeben
    hatte, fand sie in der Zusammenfassung nirgends wieder. Ein leerer Platz
    liest sich aber wie «geprüft und in Ordnung».
    """

    def projekt(self, *, mit_querkraft: bool = False) -> Projekt:
        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        for nummer in (1, 2, 3, 4):
            if q.richtung_von(nummer).value != "x":
                continue
            q.lagen[nummer - 1].grund.durchmesser = 0.0
            q.lagen[nummer - 1].zulage.durchmesser = 0.0
        if mit_querkraft:
            q.kombinationen[0].V_Ed = 120.0
        return projekt

    def zeilen(self, projekt: Projekt):
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        self.assertEqual(antwort.status, 200)
        return antwort.daten["zusammenfassungen"]["q1"]["zeilen"]

    def test_der_nachweis_steht_da_und_ist_nicht_erfuellt(self):
        zeilen = [z for z in self.zeilen(self.projekt())
                  if "Rd,x" in z["zellen"][2]]
        self.assertEqual(len(zeilen), 3)          # drei Kombinationen
        for zeile in zeilen:
            self.assertFalse(zeile["erfuellt"])
            self.assertEqual(zeile["zellen"][4], "0.00")
            self.assertIn("0.0", zeile["zellen"][2])    # M_Rd = 0
            self.assertIn("keine Bewehrung definiert", zeile["hinweis"])

    def test_die_einwirkung_steht_trotzdem_da(self):
        """Ohne sie bliebe unklar, wogegen der Widerstand null nicht reicht."""
        zeile = next(z for z in self.zeilen(self.projekt())
                     if "M_{Rd,x}" in z["zellen"][2])
        self.assertIn("M_{Ed,x}", zeile["zellen"][3])
        self.assertIn("100.0", zeile["zellen"][3])

    def test_auch_die_querkraft_faellt_aus(self):
        """
        Ohne Bewehrung gibt es keine statische Höhe, also auch keinen
        Querkraftwiderstand. Nur die M-N-Zeile zu zeigen hiesse, die Lücke
        halb zu schliessen.
        """
        zeilen = self.zeilen(self.projekt(mit_querkraft=True))
        quer = [z for z in zeilen if "V_{Rd,x}" in z["zellen"][2]]
        self.assertEqual(len(quer), 1)
        self.assertEqual(quer[0]["zellen"][4], "0.00")
        self.assertIn("V_{Ed,x}", quer[0]["zellen"][3])

    def test_erst_alle_m_n_dann_die_querkraft(self):
        """Dieselbe Folge wie dort, wo wirklich gerechnet wird."""
        zeilen = self.zeilen(self.projekt(mit_querkraft=True))
        arten = [z["zellen"][0].startswith(r"\text{Biegung und Normalkraft")
                 for z in zeilen]
        self.assertEqual(arten, sorted(arten, reverse=True), zeilen)

    def test_die_y_lagen_bleiben_unberuehrt(self):
        """Sie stehen im Querschnitt und zählen zum Bewehrungsgehalt."""
        projekt = self.projekt()
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        bewehrung = antwort.daten["zusammenfassungen"]["q1"]["bewehrung"]
        self.assertIn("12@150", bewehrung["latex"])


class TestGradzeichen(unittest.TestCase):
    """
    `\\,^{\\circ}` ist ein Exponent ohne Basis -- daran bricht KaTeX ab.

    Im Bericht stand dann der rohe Quelltext statt `30°`, und zwar für den
    ganzen Kasten, in dem die Winkel mit den übrigen Bügelangaben zusammenstehen.
    """

    def test_das_gradzeichen_hat_eine_basis(self):
        from opencivil.core.einheiten import GRAD, Groesse

        latex = Groesse(30, GRAD).als_latex(0, GRAD)
        self.assertEqual(latex, r"30{}^{\circ}")
        self.assertNotIn(r"\,^", latex)

    def test_in_der_herleitung_steht_es_richtig(self):
        projekt = Projekt.beispiel()
        b = projekt.querschnitt("q1").querkraftbewehrung
        b.durchmesser, b.stahl = 10.0, "s1"
        b.abstand_x = b.abstand_y = 300.0
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 100.0

        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        winkel = [b["latex"] for b in antwort.daten["protokoll"]
                  if b.get("art") == "gleichung" and r"\alpha_{min}" in b.get("latex", "")]
        self.assertTrue(winkel)
        for latex in winkel:
            self.assertNotIn(r"\,^{\circ}", latex)

    def test_die_buegelangaben_stehen_in_einem_kasten(self):
        """
        Fünf Vorgaben, ein Kasten. Der Bügelquerschnitt lief früher zwischen
        Durchmesser und Teilung -- und zerriss ihn damit in zwei.
        """
        projekt = Projekt.beispiel()
        b = projekt.querschnitt("q1").querkraftbewehrung
        b.durchmesser, b.stahl = 10.0, "s1"
        b.abstand_x = b.abstand_y = 300.0
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 100.0

        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        gruppen = [b.get("gruppe") for b in antwort.daten["protokoll"]
                   if b.get("art") == "gleichung"]
        # Die fünf Angaben müssen ohne Unterbruch aufeinanderfolgen.
        erste = gruppen.index("Querkraftbewehrung")
        self.assertEqual(gruppen[erste:erste + 5], ["Querkraftbewehrung"] * 5)
        self.assertNotEqual(gruppen[erste + 5], "Querkraftbewehrung")


class TestMindestbewehrungsEingaben(unittest.TestCase):
    """
    Nur die Eingaben -- der Nachweis selbst steht noch aus.

    Was hier zählt: die Angaben überleben die Datei, und eine unbekannte
    Rissanforderung wird nicht stillschweigend auf die mildeste gezogen.
    """

    def test_vorgaben(self):
        q = Projekt.beispiel().querschnitt("q1")
        self.assertEqual(q.rissanforderung, "normal")
        self.assertFalse(q.zwaengung)
        self.assertFalse(q.zwaengung_begrenzt)
        # Die 70 % sind eine Abschaetzung und keine Norm -- eingeschaltet wird
        # sie von Hand. Gerechnet wird sie trotzdem, still.
        self.assertFalse(q.haeufige_aus_tragsicherheit)
        self.assertEqual(q.haeufige, [])

    def test_alles_ueberlebt_die_datei(self):
        from opencivil.projekt import GebrauchsfallEintrag

        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        q.rissanforderung = "hoch"
        q.zwaengung = True
        q.zwaengung_begrenzt = True
        q.haeufige_aus_tragsicherheit = False
        q.haeufige = [GebrauchsfallEintrag("Gebrauch", M_Ed=70.0, N_Ed=-40.0)]

        kopie = Projekt.aus_dict(json.loads(json.dumps(projekt.als_dict())))
        k = kopie.querschnitt("q1")
        self.assertEqual(k.rissanforderung, "hoch")
        self.assertEqual((k.zwaengung, k.zwaengung_begrenzt), (True, True))
        self.assertFalse(k.haeufige_aus_tragsicherheit)
        self.assertEqual(len(k.haeufige), 1)
        self.assertEqual((k.haeufige[0].name, k.haeufige[0].M_Ed,
                          k.haeufige[0].N_Ed), ("Gebrauch", 70.0, -40.0))

    def test_eine_beschreibung_ohne_die_felder_bekommt_die_vorgaben(self):
        d = Projekt.beispiel().als_dict()
        for q in d["querschnitte"]:
            for feld in ("rissanforderung", "zwaengung",
                         "zwaengung_begrenzt", "haeufige",
                         "haeufige_aus_tragsicherheit"):
                q.pop(feld, None)
        q = Projekt.aus_dict(d).querschnitt("q1")
        self.assertEqual(q.rissanforderung, "normal")
        self.assertFalse(q.haeufige_aus_tragsicherheit)

    def test_unbekannte_rissanforderung_wird_gemeldet(self):
        d = Projekt.beispiel().als_dict()
        d["querschnitte"][0]["rissanforderung"] = "mittel"
        with self.assertRaises(ProjektFehler) as fehler:
            Projekt.aus_dict(d)
        self.assertIn("Unbekannte Rissanforderung", str(fehler.exception))

    def test_der_katalog_kennt_die_drei_stufen(self):
        stufen = api.katalog()["rissanforderungen"]
        self.assertEqual([s["wert"] for s in stufen],
                         ["normal", "erhoeht", "hoch"])
        self.assertEqual([s["beschriftung"] for s in stufen],
                         ["Normal", "Erhöht", "Hoch"])

    def test_eigene_lastfaelle_ersetzen_die_ableitung(self):
        """
        Die häufigen Lastfälle werden gerechnet -- aber nur bei erhöhter oder
        hoher Anforderung. Bei normaler steht in Tabelle 17 ein Strich.
        """
        from opencivil.projekt import GebrauchsfallEintrag

        ohne = dienst.bearbeite(
            "rechnen", {"projekt": Projekt.beispiel().als_dict()})
        self.assertFalse([u for u in ohne.daten["urteile"]
                          if u["art"] == "σ_s"])

        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        q.rissanforderung = "hoch"
        q.haeufige_aus_tragsicherheit = False
        q.haeufige = [GebrauchsfallEintrag("Gebrauch", M_Ed=70.0)]
        mit = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        namen = [u["fall"] for u in mit.daten["urteile"] if u["art"] == "σ_s"]
        self.assertEqual(namen, ["Gebrauch"])
