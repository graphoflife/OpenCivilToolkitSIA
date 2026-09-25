"""Tests für die JSON-Schnittstelle: was die Oberfläche zu sehen bekommt."""

import json
import unittest

from opencivil.core.einheiten import EINHEITSLOS, Groesse
from opencivil.projekt import GebrauchsfallEintrag, Projekt
from opencivil.web import api, dienst


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


class TestSpannungsnachweisNurWoGefordert(unittest.TestCase):
    """
    Bei normaler Rissanforderung steht in Tabelle 17 ein Strich.

    Die Maske nahm häufige Lastfälle trotzdem entgegen und rechnete sie
    stillschweigend nicht. Welche Anforderung den Nachweis verlangt, sagt
    jetzt der Katalog -- damit die Oberfläche es sagen kann, ohne die Norm
    ein zweites Mal aufzuschreiben.
    """

    def test_der_katalog_sagt_es(self):
        nach_wert = {r["wert"]: r["fliessnachweis"]
                     for r in api.katalog()["rissanforderungen"]}
        self.assertEqual(nach_wert,
                         {"normal": False, "erhoeht": True, "hoch": True})

    def test_und_es_stimmt_mit_dem_ueberein_was_gebaut_wird(self):
        from opencivil.projekt import GebrauchsfallEintrag

        for eintrag in api.katalog()["rissanforderungen"]:
            projekt = Projekt.beispiel()
            q = projekt.querschnitt("q1")
            q.rissanforderung = eintrag["wert"]
            q.haeufig.faelle = [GebrauchsfallEintrag("Gebrauch", M_Ed=70.0)]
            with self.subTest(anforderung=eintrag["wert"]):
                self.assertEqual(bool(projekt.aufbauen().spannung),
                                 eintrag["fliessnachweis"])


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
        arten = {z["zellen"][0]["text"] for z in tabelle["zeilen"]}
        self.assertNotIn("Sprödes Versagen", arten)

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
        arten = {z["zellen"][0]["text"] for z in tabelle["zeilen"]}
        self.assertIn("Sprödes Versagen", arten)

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
        self.assertTrue(tabelle["latex"].startswith(r"\begin{tabular}"))
        # Welche Spalte eingefaerbt wird, sagt der Kern -- die Oberflaeche
        # soll es nicht aus der Kopfzeile erraten muessen.
        self.assertEqual(tabelle["kopf"][tabelle["grad_spalte"]],
                         {"mathe": r"\alpha_{eff}"})

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
        paare = [(z["zellen"][0]["text"], z["zellen"][1]["text"]) for z in zeilen]
        self.assertIn(("Biegung und Normalkraft", "Feld"), paare)
        # Dieselbe Kombination in y ist eine andere Zeile -- vorher waren beide
        # nicht zu unterscheiden.
        self.assertIn(("Biegung und Normalkraft", "Feld"), paare)

    def test_der_querkraftwiderstand_ist_gross_geschrieben(self):
        projekt = Projekt.beispiel()
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 80.0
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        zeilen = antwort.daten["zusammenfassungen"]["q1"]["zeilen"]
        quer = [z for z in zeilen
                if z["zellen"][0]["text"].startswith("Querkraft")]
        self.assertTrue(quer)
        for zeile in quer:
            self.assertTrue(zeile["zellen"][2]["mathe"].startswith("V_{Rd"), zeile["zellen"][2])
            self.assertTrue(zeile["zellen"][3]["mathe"].startswith("V_{Ed"), zeile["zellen"][3])
            self.assertNotIn("left|", zeile["zellen"][3]["mathe"])

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
        self.assertTrue(bewehrung["latex"].startswith(r"\begin{tabular}"))
        erste = [z[0]["text"] for z in bewehrung["zeilen"]]
        # Wie man die Platte im Schnitt sieht: von oben nach unten, also
        # dieselbe Folge wie in der Eingabemaske.
        self.assertEqual(erste, [
            "Überdeckung oben", "4. Lage", "3. Lage",
            "2. Lage", "1. Lage", "Überdeckung unten",
        ])
        # Durchmesser, Teilung und Stahl stehen in derselben Zeile.
        erste_lage = bewehrung["zeilen"][4]
        self.assertIn(r"\varnothing 12@150", erste_lage[2]["mathe"])
        self.assertEqual(erste_lage[3], {"text": "B500B"})

    def test_eine_leere_lage_steht_ohne_bewehrung_da(self):
        """Eine nicht definierte Lage darf keinen Stahl ausweisen."""
        projekt = Projekt.beispiel()
        lage = projekt.querschnitt("q1").lagen[1]
        lage.grund.durchmesser = 0.0
        lage.zulage.durchmesser = 0.0
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        zeilen = antwort.daten["zusammenfassungen"]["q1"]["bewehrung"]["zeilen"]
        zweite = next(z for z in zeilen if z[0] == {"text": "2. Lage"})
        self.assertEqual(zweite[2], {"text": "–"})
        self.assertEqual(zweite[3], {"text": "–"})

    def test_die_zahlen_der_tabelle_haben_feste_stellen(self):
        """In einer Spalte steht immer dieselbe Grösse, also auch dieselbe Genauigkeit."""
        antwort = dienst.bearbeite("rechnen", {"projekt": Projekt.beispiel().als_dict()})
        erste = antwort.daten["zusammenfassungen"]["q1"]["zeilen"][0]["zellen"]
        self.assertIn("100.0", erste[3]["mathe"])  # M_Ed, eine Nachkommastelle
        self.assertRegex(erste[4]["mathe"], r"^\d+\.\d{2}$")  # alpha, zwei

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
        namen = [z["zellen"][0]["text"]
                 for z in antwort.daten["zusammenfassungen"]["q1"]["zeilen"]]
        self.assertTrue(namen)
        self.assertEqual(sorted(namen),
                         ["Sprödes Versagen", "Zwängung auf Biegung"])

    def test_die_duktilitaet_laeuft_auch_ohne_schnittgroessen(self):
        projekt = Projekt.beispiel()
        projekt.querschnitt("q1").kombinationen = []
        projekt.querschnitt("q1").duktilitaet = [True, False, False, True]
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        namen = [z["zellen"][0]["text"]
                 for z in antwort.daten["zusammenfassungen"]["q1"]["zeilen"]]
        # Eine Zeile: die ungünstigere der beiden x-Lagen.
        self.assertEqual(namen, ["Duktilität"])

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
        self.assertEqual(letzte[0], {"text": "Querkraftbewehrung"})
        # Kurzform wie bei den Lagen: Durchmesser und die beiden Teilungen.
        self.assertEqual(letzte[2], {"mathe": r"\varnothing 10@200@200"})
        self.assertEqual(letzte[3], {"text": "B500B"})
        # Der Bügelquerschnitt steht in der Herleitung, wo er hergeleitet
        # wird -- in einer Übersicht ist er nur Ballast.
        self.assertNotIn(r"A_{\varnothing,V}", letzte[2]["mathe"])

    def test_eine_stabzahl_in_y_steht_als_stueckzahl_da(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": self.projekt(abstand_y=None, anzahl_y=5.0)})
        letzte = antwort.daten["zusammenfassungen"]["q1"]["bewehrung"]["zeilen"][-1]
        self.assertEqual(letzte[2], {"mathe": r"\varnothing 10@200@5\,\text{Stk}"})

    def test_ohne_buegel_steht_dort_nichts(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": Projekt.beispiel().als_dict()})
        erste = [z[0]["text"] for z
                 in antwort.daten["zusammenfassungen"]["q1"]["bewehrung"]["zeilen"]]
        self.assertNotIn("Querkraftbewehrung", erste)

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
                  if "Rd,x" in z["zellen"][2]["mathe"]]
        self.assertEqual(len(zeilen), 3)          # drei Kombinationen
        for zeile in zeilen:
            self.assertFalse(zeile["erfuellt"])
            self.assertEqual(zeile["zellen"][4], {"mathe": "0.00"})
            self.assertIn("0.0", zeile["zellen"][2]["mathe"])    # M_Rd = 0
            self.assertIn("keine Bewehrung definiert", zeile["hinweis"])

    def test_die_einwirkung_steht_trotzdem_da(self):
        """Ohne sie bliebe unklar, wogegen der Widerstand null nicht reicht."""
        zeile = next(z for z in self.zeilen(self.projekt())
                     if "M_{Rd,x}" in z["zellen"][2]["mathe"])
        self.assertIn("M_{Ed,x}", zeile["zellen"][3]["mathe"])
        self.assertIn("100.0", zeile["zellen"][3]["mathe"])

    def test_auch_die_querkraft_faellt_aus(self):
        """
        Ohne Bewehrung gibt es keine statische Höhe, also auch keinen
        Querkraftwiderstand. Nur die M-N-Zeile zu zeigen hiesse, die Lücke
        halb zu schliessen.
        """
        zeilen = self.zeilen(self.projekt(mit_querkraft=True))
        quer = [z for z in zeilen if "V_{Rd,x}" in z["zellen"][2]["mathe"]]
        self.assertEqual(len(quer), 1)
        self.assertEqual(quer[0]["zellen"][4], {"mathe": "0.00"})
        self.assertIn("V_{Ed,x}", quer[0]["zellen"][3]["mathe"])

    def test_erst_alle_m_n_dann_die_querkraft(self):
        """Dieselbe Folge wie dort, wo wirklich gerechnet wird."""
        zeilen = self.zeilen(self.projekt(mit_querkraft=True))
        arten = [z["zellen"][0]["text"].startswith("Biegung und Normalkraft")
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


if __name__ == "__main__":
    unittest.main()
