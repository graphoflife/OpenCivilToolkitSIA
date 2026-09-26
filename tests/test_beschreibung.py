"""Tests für die Projektbeschreibung: lesen, ablegen, prüfen, aufbauen."""

import dataclasses
import json
import tempfile
import unittest
from pathlib import Path

from opencivil.core.einheiten import N_PRO_MM2
from opencivil.projekt import (
    Aufbau, GebrauchsfallEintrag, Gebrauchsliste, KnickEintrag, KombinationEintrag,
    LageEintrag, MaterialEintrag, ObergrenzeEintrag, PostenEintrag, Projekt,
    ProjektFehler, QuerkraftbewehrungEintrag, QuerschnittEintrag, SpannungsfallEintrag,
)
from opencivil.web import api, dienst


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
                    "q1", "Decke", "b1", h=280.0, b=900.0,
                    ueberdeckung_unten=25.0, ueberdeckung_oben=35.0,
                    d_max=16.0, einlagenhoehe=40.0, k_c=0.6,
                    rissanforderung="hoch", beschreibung="Unter dem Dach",
                    kriechzahl=2.5, zwaengung=True, zwaengung_begrenzt=True,
                    haeufig=Gebrauchsliste(anteil=75.0, aus_tragsicherheit=True, faelle=[
                        GebrauchsfallEintrag("Gebrauch", M_Ed=70.0, N_Ed=-40.0)]),
                    quasistaendig=Gebrauchsliste(anteil=55.0, aus_tragsicherheit=True, faelle=[
                        GebrauchsfallEintrag("Dauer", M_Ed=40.0, N_Ed=-5.0, aktiv=False)]),
                    knickfaelle=[KnickEintrag("Stütze", N_Ed=-900.0, M_Ed_1=25.0,
                                              laenge=5.0, knicklaenge=3.5)],
                    spannungsfaelle=[SpannungsfallEintrag("Feld", M_Ed=80.0)],
                    automatik_modus="grund_mit", automatik_dicke=True,
                    automatik_teilungen=[100.0, 200.0],
                    automatik_mindestdurchmesser=12.0, automatik_querkraft=True,
                    automatik_y_wie_x=True, automatik_mindestdicke=180.0,
                    automatik_grenze=ObergrenzeEintrag(
                        grund=PostenEintrag(durchmesser=26.0, abstand=150.0),
                        zulage=PostenEintrag(durchmesser=20.0, abstand=150.0)),
                    automatik_querkraft_teilungen=[150.0],
                    sproede=True, zwaengung_biegung=True, duktilitaet=True, x_d_max=0.42,
                    querkraftbewehrung=QuerkraftbewehrungEintrag(
                        durchmesser=10.0, stahl="s1", abstand_x=250.0,
                        abstand_y=None, anzahl_y=4.0,
                        alpha_min=35, alpha_max=42),
                    richtung_lage1="x", richtung_lage4="x",
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
        self.assertEqual(kopie.querschnitt("q1").richtung_lage1, "x")
        self.assertEqual(kopie.querschnitt("q1").lagen[0].zulage.anzahl, 6.0)
        self.assertEqual(kopie.querschnitt("q1").kombinationen[1].art, "naechster_Punkt")
        self.assertEqual(kopie.querschnitt("q1").kombinationen[0].V_Ed, 80.0)
        self.assertEqual(kopie.querschnitt("q2").lagen[0].stahl, "s2")
        buegel = kopie.querschnitt("q1").querkraftbewehrung
        self.assertEqual((buegel.durchmesser, buegel.abstand_x), (10.0, 250.0))
        self.assertEqual((buegel.abstand_y, buegel.anzahl_y), (None, 4.0))
        self.assertEqual((buegel.alpha_min, buegel.alpha_max), (35, 42))
        self.assertEqual(kopie.querschnitt("q1").k_c, 0.6)

        # Keine Auswahl von Proben: jedes Feld der ersten Platte weicht von
        # der Vorgabe ab, der Vergleich oben prüft also alle. Ein neues Feld
        # fällt hier auf, bis es mitgeprüft wird.
        vorgabe = QuerschnittEintrag("q9", "X", "b9")
        self.assertEqual([f.name for f in dataclasses.fields(QuerschnittEintrag)
                          if getattr(projekt.querschnitt("q1"), f.name)
                          == getattr(vorgabe, f.name)], [])

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
        self.assertFalse(vorlage["haeufig"]["aus_tragsicherheit"])

    def test_sie_folgt_den_vorgaben_der_beschreibung(self):
        """
        Der eigentliche Punkt: kein zweiter Satz Vorgaben. Ändert sich einer
        in QuerschnittEintrag, ändert sich die Vorlage mit.
        """
        from opencivil.projekt import QuerschnittEintrag

        vorlage = api.katalog()["neue_platte"]
        leer = QuerschnittEintrag(kennung="x", name="x", beton="b").als_dict()
        for feld in ("duktilitaet", "sproede", "zwaengung_biegung", "zwaengung",
                     "haeufig", "quasistaendig", "automatik_modus",
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
            ("haeufig", [GebrauchsfallEintrag("Gebrauch"), GebrauchsfallEintrag("Gebrauch")]),
            ("knickfaelle", [KnickEintrag("Stütze", N_Ed=-100.0, laenge=3.0,
                                          knicklaenge=3.0),
                             KnickEintrag("Stütze", N_Ed=-200.0, laenge=3.0,
                                          knicklaenge=3.0)]),
        ):
            with self.subTest(feld=feld):
                projekt = Projekt.beispiel()
                q = projekt.querschnitt("q1")
                if feld == "haeufig":
                    q.haeufig.faelle = eintraege
                else:
                    setattr(q, feld, eintraege)
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
        q.haeufig.faelle = [GebrauchsfallEintrag(
            f"{q.kombinationen[0].name} (70 %)", M_Ed=70.0)]
        with self.assertRaises(ProjektFehler) as fehler:
            projekt.aufbauen()
        self.assertIn("abgeleitete", str(fehler.exception))

    def test_verschiedene_namen_gehen_weiterhin(self):
        """Die Regel darf nicht mehr verbieten als sie muss."""
        from opencivil.projekt import GebrauchsfallEintrag

        projekt = Projekt.beispiel()
        q = projekt.querschnitt("q1")
        q.rissanforderung = "hoch"
        q.haeufig.faelle = [GebrauchsfallEintrag("Gebrauch", M_Ed=70.0),
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

    def test_ein_feld_ausserhalb_der_liste_scheitert_laut(self):
        """
        Die andere Richtung: ein Nachweis, der in einem Feld landet, das die
        Liste nicht kennt, waere kein Ziel und fehlte still in jeder Tabelle.
        Das Anmelden weist ihn darum zurueck.
        """
        from unittest import mock

        ohne_knicken = tuple(f for f in Aufbau.NACHWEISFELDER if f != "knicken")
        with mock.patch.object(Aufbau, "NACHWEISFELDER", ohne_knicken):
            with self.assertRaises(ValueError) as fehler:
                self.aufbau()
        self.assertIn("'knicken'", str(fehler.exception))

    def test_jeder_nachweis_gehoert_zu_genau_einer_platte(self):
        """Sonst käme ein Ergebnis beim Zwischenspeichern doppelt oder gar nicht."""
        aufbau = self.aufbau()
        eigene = aufbau.ziele_von("q1")
        self.assertEqual(sorted(eigene),
                         sorted(aufbau.eckwertziele() + aufbau.alle_nachweisziele()))


class TestAusgeschaltetHeisstStill(unittest.TestCase):
    """
    Ausgeschaltet heisst nicht weg: der Nachweis rechnet still mit. In
    Tabelle und Herleitung steht er nicht, unter der Tabelle kann ein Hinweis
    stehen. Für jeden Schalter derselbe Mechanismus -- darum ein Test.
    """

    #: Schalter der Platte -> (Feld im Aufbau, Art der Urteile).
    SCHALTER = {
        "duktilitaet": ("duktilitaet", "D"),
        "sproede": ("sproede", "SV"),
        "zwaengung": ("rissnormalkraft", "N_Riss"),
        "zwaengung_biegung": ("zwaengung_biegung", "ZB"),
    }

    def test_jeder_schalter(self):
        for schalter, (feld, art) in self.SCHALTER.items():
            projekt = Projekt.beispiel()
            setattr(projekt.querschnitt("q1"), schalter, False)
            aufbau = projekt.aufbauen()
            loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
            with self.subTest(schalter=schalter):
                self.assertTrue(all(n.still for n in getattr(aufbau, feld).values()))
                urteile = [u for u in loesung.urteile if u.art == art]
                self.assertEqual(len(urteile), 2)          # beide x-Lagen
                self.assertTrue(all(u.still for u in urteile))
                self.assertFalse([u for u in loesung.gefuehrte_urteile if u.art == art])


class TestEinUrteilJeLagennachweis(unittest.TestCase):
    """
    Gerechnet wird jede x-Lage, in der Tabelle steht eine Zeile: die
    schlechtere. Vier Zeilen für eine Frage wären drei zuviel -- beantwortet
    wird sie ohnehin von der schlechteren Lage. Derselbe Mechanismus für jeden
    Lagennachweis (``Nachweis.teilurteile``), darum ein Test.
    """

    def test_jeder_lagennachweis(self):
        projekt = Projekt.beispiel()
        for schalter in TestAusgeschaltetHeisstStill.SCHALTER:
            setattr(projekt.querschnitt("q1"), schalter, True)
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        for schalter, (feld, art) in TestAusgeschaltetHeisstStill.SCHALTER.items():
            with self.subTest(schalter=schalter):
                nachweis, = getattr(aufbau, feld).values()
                self.assertEqual(len(nachweis.ergebnisse), 2)       # beide x-Lagen
                laut = [u for u in loesung.gefuehrte_urteile if u.art == art]
                self.assertEqual(len(laut), 1)
                self.assertAlmostEqual(
                    laut[0].erfuellungsgrad.si,
                    min(e.erfuellungsgrad for e in nachweis.ergebnisse), places=9)


class TestMindestbewehrungsEingaben(unittest.TestCase):
    """
    Die Eingaben der Mindestbewehrung: sie überleben die Datei, und eine
    unbekannte Rissanforderung wird nicht stillschweigend auf die mildeste
    gezogen.
    """

    def test_vorgaben(self):
        q = Projekt.beispiel().querschnitt("q1")
        self.assertEqual(q.rissanforderung, "normal")
        self.assertFalse(q.zwaengung)
        self.assertFalse(q.zwaengung_begrenzt)
        # Die 70 % sind eine Abschaetzung und keine Norm -- eingeschaltet wird
        # sie von Hand. Gerechnet wird sie trotzdem, still.
        self.assertFalse(q.haeufig.aus_tragsicherheit)
        self.assertEqual(q.haeufig.faelle, [])

    def test_eine_beschreibung_ohne_die_felder_bekommt_die_vorgaben(self):
        d = Projekt.beispiel().als_dict()
        for q in d["querschnitte"]:
            for feld in ("rissanforderung", "zwaengung",
                         "zwaengung_begrenzt", "haeufig"):
                q.pop(feld, None)
        q = Projekt.aus_dict(d).querschnitt("q1")
        self.assertEqual(q.rissanforderung, "normal")
        self.assertFalse(q.haeufig.aus_tragsicherheit)

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


if __name__ == "__main__":
    unittest.main()
