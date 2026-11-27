"""
Die Querschnittsanalyse: ihre Vorlagen, die neue, leere Analyse und
verschmierte Stäbe. Bis 2026-11-20 standen die Tests in
test_querschnittsanalyse.py, das damit über 1000 Zeilen hatte.
"""

import math
import unittest

from opencivil.projekt import Projekt, QuerschnittsanalyseEintrag
from opencivil.querschnitt import geometrie, vorlagen
from opencivil.web import api, dienst, zeichengeometrie
from tests.test_querschnittsanalyse import balken, projekt, urteile


def eingesetzt(schluessel, **wahl):
    """Eine Vorlage in einer leeren Analyse, aus C30/37 (b1) und B500B (s1)."""
    p = projekt()
    a = p.querschnittsanalysen[0]
    for liste in ("knoten", "flaechen", "staebe", "stablinien", "schubwaende"):
        setattr(a, liste, [])
    neu = a.vorlage_einsetzen(schluessel, material="b1", stahl="s1", **wahl)
    return p, a, neu


class TestVorlagen(unittest.TestCase):
    """
    Die Vorlagen stehen im Kern und nur dort. Jede ist nach Vorgabe gültig und
    hat die Fläche, die man von Hand nachrechnet; eingesetzt kommt sie dazu.
    """

    #: Bruttofläche nach Vorgabe, von Hand: Rechteck 300·600; T-Balken
    #: 1200·200 + 300·500; Doppel-T 800·150 + 200·650 + 500·200; Trapez
    #: (400 + 300)/2 · 600; Hohlkasten 1200·800 − 800·400; Platte mit
    #: Aufbeton 1000·200 + 1000·100; Kreis als 48-Eck mit r = 250:
    #: 24 · r² · sin(7.5°). Die Ecken des Kreises sind auf Tausendstel
    #: gerundet -- das ändert seine Fläche um 0.25 mm².
    FLAECHEN = {
        "rechteck": 300 * 600,
        "tbalken": 1200 * 200 + 300 * 500,
        "doppel_t": 800 * 150 + 200 * 650 + 500 * 200,
        "trapez": (400 + 300) / 2 * 600,
        "hohlkasten": 1200 * 800 - 800 * 400,
        "aufbeton": 1000 * 200 + 1000 * 100,
        "kreis": 24 * 250 ** 2 * math.sin(math.radians(7.5)),
    }

    def eingesetzt(self, schluessel, **wahl):
        return eingesetzt(schluessel, **wahl)

    def test_jede_ist_gueltig_und_hat_ihre_flaeche(self):
        self.assertEqual({v.schluessel for v in vorlagen.VORLAGEN}, set(self.FLAECHEN))
        for v in vorlagen.VORLAGEN:
            with self.subTest(vorlage=v.name):
                p, a, _ = self.eingesetzt(v.schluessel)
                g = zeichengeometrie.geometrie(a, p)
                self.assertTrue(g["gueltig"], g["meldungen"])
                self.assertAlmostEqual(g["brutto"]["A"], self.FLAECHEN[v.schluessel], delta=0.5)

    def test_neu_ist_leer(self):
        """Eine neue Analyse ist leer (Benutzer, 2026-10-19): nichts gezeichnet, kein Lastfall."""
        a = QuerschnittsanalyseEintrag.neu("a1", "Balken")
        self.assertTrue(a.leer)
        self.assertEqual((a.knoten, a.flaechen, a.stablinien, a.lastfaelle), ([], [], [], []))

    def test_das_rechteck_der_skripte(self):
        """
        Das Rechteck der Skripte, wie die Vorlage bis 2026-11-27 und die
        frische Analyse bis 2026-10-19: dieselben Knoten, Linien und Werte.
        """
        a = balken()
        self.assertEqual([(k.kennung, k.y, k.z) for k in a.knoten], [
            ("K1", 0.0, 0.0), ("K2", 300.0, 0.0), ("K3", 300.0, 600.0), ("K4", 0.0, 600.0),
            ("K5", 50.0, 50.0), ("K6", 250.0, 50.0), ("K7", 50.0, 550.0), ("K8", 250.0, 550.0)])
        self.assertEqual([(f.kennung, f.knoten, f.material) for f in a.flaechen],
                         [("F1", ["K1", "K2", "K3", "K4"], "b1")])
        self.assertEqual([(l.von, l.bis, l.art, l.anzahl, l.durchmesser, l.stahl)
                          for l in a.stablinien],
                         [("K5", "K6", "anzahl", 3.0, 20.0, "s1"),
                          ("K7", "K8", "anzahl", 2.0, 12.0, "s1")])
        self.assertEqual(a.schubwaende, [])

    def test_kommt_dazu_und_teilt_knoten(self):
        """Ein zweites Rechteck rechts daneben hängt an den zwei gemeinsamen Ecken."""
        a = balken()
        neu = a.vorlage_einsetzen("rechteck", material="b1", stahl="s1", bewehrung=False,
                                  schubwaende=False, ursprung=(300.0, 0.0))
        self.assertEqual(neu, ["F2"])
        self.assertEqual(len(a.flaechen), 2)
        self.assertEqual(a.flaechen[1].knoten[0], "K2")
        self.assertEqual(a.flaechen[1].knoten[3], "K3")

    def test_haken_und_masse(self):
        _, a, neu = self.eingesetzt("hohlkasten", masse={"t": 150.0}, bewehrung=False)
        self.assertEqual(len(a.stablinien), 0)
        self.assertEqual([w.dicke for w in a.schubwaende], [150.0] * 4)
        self.assertEqual([f.material for f in a.flaechen], ["b1", ""])
        self.assertEqual(len(neu), 6)
        # Der Kreis hat keine Wände, auch wenn man sie will.
        _, a, _ = self.eingesetzt("kreis", schubwaende=True)
        self.assertEqual((len(a.staebe), a.schubwaende), (8, []))

    def test_masse_die_nicht_passen(self):
        with self.assertRaisesRegex(ValueError, "Steg"):
            vorlagen.vorlage("tbalken").bauen({"b": 200.0, "b_w": 300.0})
        with self.assertRaisesRegex(ValueError, "^Höhe h muss grösser als null sein, angegeben ist 0 mm.$"):
            vorlagen.vorlage("rechteck").bauen({"h": 0.0})
        # Die Überdeckung ist ein Mass wie die anderen: derselbe Satz, und die
        # Maske bekommt Vorgabe und Grenze aus dem Katalog.
        with self.assertRaisesRegex(ValueError, "^Überdeckung c_nom muss grösser als null sein"):
            vorlagen.vorlage("rechteck").bauen({"c_nom": 0.0})
        c = api.katalog()["querschnittsanalyse"]["ueberdeckung"]
        self.assertEqual((c["vorgabe"], c["angabe"]["ueber"]), (35.0, 0.0))
        d = dienst.bearbeite("vorlage", {"wahl": {"art": "hohlkasten", "masse": {"t": 700}}}).daten
        self.assertIn("Wände", d["fehler"])
        self.assertIsNone(d["teile"])
        self.assertEqual(dienst.bearbeite("vorlage", {"wahl": {"art": "dreieck"}}).status, 400)

    def test_der_kreis_mit_n_staeben(self):
        """
        Wie viele Stäbe der Kreis hat, stellt man ein (Benutzer, 2026-11-16):
        gleich verteilt, ihre Achsen c_nom + ⌀/2 vom Rand, der erste rechts --
        hier 42 + 8 = 50 mm. Eine halbe Zahl wird nicht still gerundet.
        """
        kreis = vorlagen.vorlage("kreis")
        teile = kreis.bauen({"D": 400.0, "n": 6.0, "c_nom": 42.0, "d": 16.0})
        self.assertEqual(len(teile.staebe), 6)
        for k, s in enumerate(teile.staebe):
            winkel = math.radians(60 * k)
            self.assertAlmostEqual(s["lage"][0], 200 + 150 * math.cos(winkel), delta=1e-3)
            self.assertAlmostEqual(s["lage"][1], 200 + 150 * math.sin(winkel), delta=1e-3)
        self.assertEqual(len(kreis.bauen().staebe), 8)
        with self.assertRaisesRegex(ValueError, "ganze Zahl sein, angegeben ist 7.5"):
            kreis.bauen({"n": 7.5})
        with self.assertRaisesRegex(ValueError, "grösser als null"):
            kreis.bauen({"n": 0.0})
        # Der Katalog sagt dem Fenster, dass n eine Anzahl ist: ohne Einheit,
        # in ganzen Schritten -- n gehört zur Lage, D zur Form.
        katalog = {v["schluessel"]: v for v in api.katalog()["querschnittsanalyse"]["vorlagen"]}
        angaben = lambda masse: [(m["schluessel"], m["angabe"].get("einheit"), m["schritt"],
                                  m["angabe"].get("ganz", False)) for m in masse]
        self.assertEqual(angaben(katalog["kreis"]["masse"]), [("D", "mm", 10.0, False)])
        self.assertEqual(angaben(katalog["kreis"]["lagen"][0]["masse"]),
                         [("d", "mm", 10.0, False), ("n", None, 1.0, True)])
        self.assertEqual(katalog["kreis"]["lagen"][0]["kurz"], ["⌀", "n"])

    def test_einsetzen_ueber_den_dienst(self):
        p = projekt()
        d = dienst.bearbeite("vorlage_einsetzen", {
            "projekt": p.als_dict(), "kennung": "a1", "material": "b1", "stahl": "s1",
            "wahl": {"art": "kreis", "masse": {"D": 400}}, "ursprung": [400, 0]}).daten
        self.assertEqual(d["neu"][0], "F2")
        self.assertEqual(len(d["neu"]), 9)
        self.assertEqual(len(d["elemente"]["flaechen"]), 2)
        # Der Katalog hat je Vorlage ihre Masse und eine Skizze.
        katalog = api.katalog()["querschnittsanalyse"]["vorlagen"]
        self.assertEqual([v["schluessel"] for v in katalog],
                         ["rechteck", "tbalken", "doppel_t", "trapez", "hohlkasten", "aufbeton",
                          "kreis"])
        self.assertEqual(len(katalog[0]["skizze"]["masslinien"]), 2)


class TestBewehrungJeLage(unittest.TestCase):
    """
    Je Lage Durchmesser und Teilung, die Überdeckung c_nom bis zum äussersten
    Stab (Benutzer, 2026-11-27). Das Beispiel des Plans: Rechteck b = 300 mm,
    c_nom = 35 mm, Bügel ⌀10, unten ⌀20 mit s = 100 mm -- die Achsen
    35 + 10 + 10 = 55 mm vom Rand, dazwischen 190 mm: zwei Felder zu 95 mm,
    drei Stäbe.
    """

    def test_das_beispiel_des_plans(self):
        teile = vorlagen.vorlage("rechteck").bauen()
        unten = teile.stablinien[0]
        self.assertEqual((unten["von"], unten["bis"]), ((55.0, 55.0), (245.0, 55.0)))
        self.assertEqual((unten["art"], unten["teilung"], unten["durchmesser"]),
                         ("teilung", 100.0, 20.0))
        self.assertEqual(teile.lagen, {"unten": "3 Stäbe, Abstand 95 mm",
                                       "oben": "2 Stäbe, Abstand 198 mm"})
        self.assertEqual([s["lage"] for s in teile.stabmitten[:3]],
                         [(55.0, 55.0), (150.0, 55.0), (245.0, 55.0)])

    def test_eingesetzt_zaehlt_die_zeichnung_dieselben_staebe(self):
        """Die Lage wird eine Stablinie mit Teilung, gerundet wie jede gezeichnete."""
        p, a, _ = eingesetzt("rechteck")
        linie = zeichengeometrie.geometrie(a, p)["linien"][0]
        self.assertEqual((linie["gewaehlt"], linie["teilung"], linie["felder"]), (100.0, 95.0, 2))
        self.assertEqual(linie["punkte"], [[55.0, 55.0], [150.0, 55.0], [245.0, 55.0]])

    def test_ohne_schubwaende_bis_zum_stab(self):
        """Ohne Bügel liegt die Achse c_nom + ⌀/2 = 45 mm vom Rand: 210 mm, zwei Felder zu 105."""
        teile = vorlagen.vorlage("rechteck").bauen(schubwaende=False)
        self.assertEqual(teile.stablinien[0]["von"], (45.0, 45.0))
        self.assertEqual(teile.lagen["unten"], "3 Stäbe, Abstand 105 mm")
        self.assertEqual(teile.schubwaende, [])

    def test_die_wand_mit_ihren_buegeln(self):
        """
        Die Wand endet auf der Höhe der Stabachsen und trägt die Bügel der
        Vorlage -- ohne Bewehrung dort, wo sie läge. Bügel ⌀12: 35 + 12 + 10.
        """
        for bewehrung in (True, False):
            with self.subTest(bewehrung=bewehrung):
                _, a, _ = eingesetzt("rechteck", bewehrung=bewehrung,
                                     masse={"d_b": 12.0, "s_b": 200.0})
                (wand,) = a.schubwaende
                self.assertEqual([(k.y, k.z) for k in a.knoten if k.kennung in (wand.von, wand.bis)],
                                 [(150.0, 57.0), (150.0, 600.0 - 35 - 12 - 6)])
                self.assertEqual((wand.dicke, wand.durchmesser, wand.teilung), (300.0, 12.0, 200.0))

    def test_die_staebe_muessen_platz_haben(self):
        """
        Jeder Stab ganz im Querschnitt, nicht in einem Loch: ein Kasten mit
        60 mm Wand hat für 35 + 10 + 16 mm keinen Platz, ein Flansch von
        40 mm nicht für die Stäbe oben.
        """
        platz = "passen nicht in den Querschnitt – Überdeckung, Bügel oder Durchmesser sind zu gross."
        for schluessel, masse, lage in (("rechteck", {"b": 100.0}, "unten"),
                                        ("hohlkasten", {"t": 60.0}, "unten"),
                                        ("tbalken", {"h_f": 40.0}, "oben"),
                                        ("kreis", {"D": 80.0}, "am Rand")):
            with self.subTest(vorlage=schluessel):
                with self.assertRaisesRegex(ValueError, f"^Die Stäbe {lage} {platz}$"):
                    vorlagen.vorlage(schluessel).bauen(masse)
        with self.assertRaisesRegex(ValueError, "zu niedrig"):
            vorlagen.vorlage("rechteck").bauen({"h": 100.0})
        # Acht Stäbe ⌀16 auf einem Ring von 7 mm Radius: Sehne 5 mm.
        with self.assertRaisesRegex(ValueError, "^Die Stäbe am Rand liegen ineinander – ihr "
                                                "Abstand 5 mm ist kleiner als ihr Durchmesser 16 mm.$"):
            vorlagen.vorlage("kreis").bauen({"D": 100.0})
        # Ohne Bewehrung zählt nur die Form.
        self.assertEqual(vorlagen.vorlage("hohlkasten").bauen({"t": 60.0}, bewehrung=False,
                                                              schubwaende=False).lagen, {})

    def test_im_trapez_quer_zur_schraegen_kante(self):
        """Der äusserste Stab liegt c_nom + ⌀_b + ⌀/2 = 55 mm von der schrägen Kante, nicht waagrecht."""
        teile = vorlagen.vorlage("trapez").bauen()
        links = teile.stabmitten[0]["lage"]
        kante = teile.polygone[0]["punkte"][3], teile.polygone[0]["punkte"][0]
        self.assertAlmostEqual(geometrie.abstand_zur_strecke(links, *kante), 55.0)
        self.assertAlmostEqual(links[1], 55.0)
        # Die Wand so dick wie das Trapez an der engsten Stelle zwischen den Stäben.
        self.assertAlmostEqual(teile.schubwaende[0]["dicke"], 300 + 100 * 55 / 600)

    def test_der_aufbeton_aus_seinem_beton(self):
        """Zwei Betone zur Wahl; ohne zweiten gilt der der Platte auch oben."""
        p = projekt()
        p.beton("C40/50")
        a = p.querschnittsanalysen[0]
        a.vorlage_einsetzen("aufbeton", material="b1", stahl="s1", stoffe={"aufbeton": "b2"},
                            ursprung=(1000.0, 0.0))
        self.assertEqual([f.material for f in a.flaechen[-2:]], ["b1", "b2"])
        a.vorlage_einsetzen("aufbeton", material="b1", stahl="s1", ursprung=(3000.0, 0.0))
        self.assertEqual([f.material for f in a.flaechen[-2:]], ["b1", "b1"])
        # Die Stäbe oben liegen im Aufbeton, 35 + 5 = 40 mm unter seiner Oberkante.
        teile = vorlagen.vorlage("aufbeton").bauen()
        self.assertEqual(teile.stablinien[1]["von"], (40.0, 260.0))
        self.assertEqual([x["stoff"] for x in teile.polygone], ["", "aufbeton"])

    def test_der_katalog_der_lagen(self):
        q = api.katalog()["querschnittsanalyse"]
        rechteck = q["vorlagen"][0]
        self.assertEqual([(l["schluessel"], l["name"], l["kurz"],
                           [(m["schluessel"], m["heisst"], m["vorgabe"]) for m in l["masse"]])
                          for l in rechteck["lagen"]],
                         [("unten", "unten", ["⌀", "s"], [("d_u", "Durchmesser unten ⌀_u", 20.0),
                                                          ("s_u", "Teilung unten s_u", 100.0)]),
                          ("oben", "oben", ["⌀", "s"], [("d_o", "Durchmesser oben ⌀_o", 12.0),
                                                        ("s_o", "Teilung oben s_o", 200.0)])])
        self.assertEqual([(m["schluessel"], m["vorgabe"]) for m in q["buegel"]["masse"]],
                         [("d_b", 10.0), ("s_b", 150.0)])
        aufbeton = next(v for v in q["vorlagen"] if v["schluessel"] == "aufbeton")
        self.assertEqual([(s["schluessel"], s["arten"]) for s in aufbeton["stoffe"]],
                         [("aufbeton", ["beton"])])
        # Die Skizze nach dem Dienst sagt, was aus jeder Lage wird.
        d = dienst.bearbeite("vorlage", {"wahl": {"art": "rechteck"}}).daten
        self.assertEqual(d["teile"]["lagen"]["unten"], "3 Stäbe, Abstand 95 mm")

    def test_das_aufbeton_beispiel_rechnet(self):
        """Eine Platte mit Aufbeton aus zwei Betonen rechnet wie jede Analyse."""
        p, a, _ = eingesetzt("aufbeton")
        p.beton("C40/50")
        a.flaechen[1].material = "b2"
        a.lastfall("Feld", M_y_Ed=100.0)
        e = p.rechnen()
        self.assertEqual(e.warnungen, [])
        self.assertTrue(urteile(e, "biegung") or e.urteile_von("a1"))


class TestLeereAnalyse(unittest.TestCase):
    """
    Eine neue Analyse ist leer (Benutzer, 2026-10-19). Bis dahin hielt eine
    Analyse ohne Fläche die ganze Rechnung an: «Es gibt kein Polygon mit
    Material» -- direkt nach dem Anlegen rechnete kein Bauteil mehr.
    """

    def beschreibung(self) -> dict:
        p = Projekt.beispiel()
        p.querschnittsanalysen.append(QuerschnittsanalyseEintrag.neu("a9", "Leer"))
        return p.als_dict()

    def test_sie_haelt_das_projekt_nicht_auf(self):
        antwort = dienst.bearbeite("rechnen", {"projekt": self.beschreibung()})
        self.assertEqual(antwort.status, 200)
        self.assertIn("Querschnittsanalyse 'Leer': noch nichts gezeichnet → nichts zu rechnen.",
                      [w["text"] for w in antwort.daten["warnungen"]])
        self.assertTrue(antwort.daten["urteile"])

    def test_ein_system_mit_ihr_als_querschnitt_meldet_es(self):
        d = self.beschreibung()
        d["balkensysteme"][0]["querschnitte"][0].update(art="analyse", analyse="a9")
        antwort = dienst.bearbeite("rechnen", {"projekt": d})
        self.assertEqual(antwort.status, 200)
        meldungen = [m["text"] for m in antwort.daten["zeichendaten"]["r1"]["uebersicht"]["meldungen"]]
        self.assertTrue(any("die Querschnittsanalyse «Leer» rechnet nicht (noch nichts "
                            "gezeichnet)." in m for m in meldungen), meldungen)

    def test_ihre_diagramme_sagen_es(self):
        antwort = dienst.bearbeite("analysediagramme",
                                   {"projekt": self.beschreibung(), "kennung": "a9"})
        self.assertEqual(antwort.status, 400)
        self.assertIn("noch nichts gezeichnet", antwort.daten["fehler"])

    def test_bewehrung_ohne_polygon_haelt_nur_sie_auf(self):
        """
        Wer zuerst die Stäbe zeichnet, hat eine Weile Bewehrung ohne Beton
        darum. Bis 2026-11-19 rechnete dann kein Bauteil mehr; jetzt rechnet
        nur die Analyse nicht, und ihre Diagramme sagen warum.
        """
        p = Projekt.beispiel()
        a = QuerschnittsanalyseEintrag.neu("a9", "Halb")
        a.stab(100, 100, durchmesser=20, stahl=p.querschnittsanalysen[0].stablinien[0].stahl)
        p.querschnittsanalysen.append(a)
        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        self.assertEqual(antwort.status, 200)
        self.assertTrue(any(w["text"].startswith("Querschnittsanalyse 'Halb': Es gibt kein Polygon "
                                                 "mit Material") for w in antwort.daten["warnungen"]),
                        antwort.daten["warnungen"])
        self.assertTrue(antwort.daten["urteile"])
        diagramme = dienst.bearbeite("analysediagramme", {"projekt": p.als_dict(), "kennung": "a9"})
        self.assertEqual(diagramme.status, 400)
        self.assertIn("kein Polygon mit Material", diagramme.daten["fehler"])

    def test_bauhilfen_allein_sind_noch_leer(self):
        a = QuerschnittsanalyseEintrag.neu("a9", "Leer")
        a.hilfslinie([0, 0], [300, 0])
        self.assertTrue(a.leer)
        a.polygon([[0, 0], [300, 0], [300, 600], [0, 600]], material="b1")
        self.assertFalse(a.leer)


class TestVerschmierteStaebe(unittest.TestCase):
    """
    Eine verschmierte Linie aus ⌀, Teilung und Länge: A_s = L/s · π⌀²/4 --
    ohne eigene Länge über die der Linie (Benutzer, 2026-10-24).
    """

    def projekt(self, **felder):
        p = projekt()
        p.querschnittsanalysen[0].stablinie([50, 300], [250, 300], art="flaeche",
                                            verschmiert="staebe", stahl="s1",
                                            **{"durchmesser": 12.0, "teilung": 150.0, **felder})
        return p

    def flaeche(self, p):
        return p.rechnen().aufbau.querschnittsanalysen["a1"].bewehrungselemente[-1].flaeche

    def test_ueber_die_linie(self):
        # 200 mm Linie: 200/150 · π · 12²/4 = 150.8 mm².
        self.assertAlmostEqual(self.flaeche(self.projekt()), 200 / 150 * math.pi * 12 ** 2 / 4)

    def test_ueber_eine_eigene_laenge(self):
        # Ein Meter: 1000/150 · π · 12²/4 = 754 mm², verteilt über die 200 mm der Linie.
        self.assertAlmostEqual(self.flaeche(self.projekt(laenge=1000.0)),
                               1000 / 150 * math.pi * 12 ** 2 / 4)

    def test_die_zeichnung_zeigt_dieselbe(self):
        """Die graue Zahl im Fenster: die Fläche, mit der gerechnet wird."""
        p = self.projekt(laenge=1000.0)
        linie = zeichengeometrie.geometrie(p.querschnittsanalysen[0], p)["linien"][-1]
        self.assertAlmostEqual(linie["flaeche"], self.flaeche(p))

    def test_die_flaeche_von_hand_bleibt(self):
        """Die Fläche von Hand zählt nur, solange der Schalter auf «Stahlfläche» steht."""
        p = self.projekt(flaeche=999.0)
        self.assertAlmostEqual(self.flaeche(p), 200 / 150 * math.pi * 12 ** 2 / 4)
        p.querschnittsanalysen[0].stablinien[-1].verschmiert = "flaeche"
        self.assertEqual(self.flaeche(p), 999.0)

    def test_falsche_zahlen(self):
        """
        Die Grenzen stehen an den Feldern; die Meldung nennt die Linie, wie
        die Zeichnung sie nennt.
        """
        for felder, text in (({"teilung": 0.0}, "Teilung muss grösser als null sein"),
                             ({"durchmesser": 0.0}, "Durchmesser muss grösser als null sein"),
                             ({"laenge": -1.0}, "Länge muss grösser als null sein")):
            with self.subTest(felder=felder):
                warnungen = self.projekt(**felder).rechnen().warnungen
                # Die Vorlage hat zwei Linien -- diese ist die dritte.
                self.assertTrue(any(f"Linie 3: {text}" in w for w in warnungen), warnungen)

    def test_herleitung(self):
        text = str(self.projekt().rechnen().bericht())
        self.assertIn("Verschmierte Stäbe: ⌀ im Abstand s über die Länge L", text)
        self.assertIn(r"\text{verschmiert: } \varnothing 12\ @\ 150\ \text{auf}\ 200", text)


if __name__ == "__main__":
    unittest.main()
