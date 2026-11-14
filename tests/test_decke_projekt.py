"""
Die Beschreibung einer Decke: lesen, ablegen, zeichnen ohne Oberfläche,
ihre Lasten, Lastfälle und Kombinationen -- und was die Oberfläche beim
Zeichnen vom Kern bekommt, auch die Bilder eines Falls.
"""

import math
import unittest

from opencivil.decke import geometrie as geo
from opencivil.decke.feld import GROESSEN
from opencivil.decke.modell import Flaechenlast, Linienlast, Punktlast
from opencivil.projekt import BalkensystemEintrag, DeckeEintrag, Projekt, ProjektFehler, beispiele
from opencivil.projekt.aufbau.decke import modell_von
from opencivil.web import dienst


def zwei_felder() -> Projekt:
    """
    Zwei Platten verschiedener Dicke, die sich eine Kante teilen, ringsum auf
    Wänden; ein Unterzug über die gemeinsame Kante, eine Stütze im zweiten
    Feld und eine Zone im ersten.
    """
    p = Projekt(name="Decke")
    beton = p.beton("C30/37")
    d = p.decke("Zwei Felder")
    d.platte([(0, 0), (4, 0), (4, 3), (0, 3)], beton=beton, h=200)
    d.platte([(4, 0), (8, 0), (8, 3), (4, 3)], beton=beton, h=250)
    for a, b in [((0, 0), (8, 0)), ((8, 0), (8, 3)), ((8, 3), (0, 3)), ((0, 3), (0, 0))]:
        d.lager(a, b)
    d.unterzug((4, 0), (4, 3), breite=0.5)
    d.stuetze((6, 1.5))
    d.zone([(0, 0), (1, 0), (1, 3), (0, 3)], anteil=30.0)
    return p


def mit_lasten() -> Projekt:
    """
    Die zwei Felder mit den Fällen einer frischen Decke und je einer Last
    jeder Art: Auflast auf der ganzen ersten Platte und eine Wand darauf,
    Nutzlast gezeichnet im zweiten Feld und an einem Punkt im ersten.
    """
    p = zwei_felder()
    d = p.decken[0]
    d.standardfaelle()
    _, auflast, nutzlast = d.lastfaelle
    d.plattenlast(auflast, "P1", 1.5)
    d.linienlast(auflast, (1, 1), (3, 1), wert=8.0)
    d.flaechenlast(nutzlast, [(5, 0.5), (7, 0.5), (7, 2.5), (5, 2.5)], wert=3.0)
    d.punktlast(nutzlast, (2, 2), wert=20.0, l_x=0.5)
    return p


def zeichnung(p: Projekt, kennung: str = "e1"):
    return dienst.bearbeite("decke_zeichnung", {"projekt": p.als_dict(), "kennung": kennung})


def bilder(p: Projekt, fall: str = "", kennung: str = "e1"):
    return dienst.bearbeite("decke_ergebnis", {"projekt": p.als_dict(), "kennung": kennung, "fall": fall})


class TestBeschreibung(unittest.TestCase):
    def test_hin_und_zurueck(self):
        p = zwei_felder()
        self.assertEqual(Projekt.aus_dict(p.als_dict()), p)

    def test_knoten_werden_geteilt(self):
        """Die gemeinsame Kante ist ein Paar Knoten; der Unterzug läuft auf ihr."""
        d = zwei_felder().decken[0]
        p1, p2 = d.platten
        self.assertEqual((p1.knoten[1], p1.knoten[2]), (p2.knoten[0], p2.knoten[3]))
        self.assertEqual((d.unterzuege[0].von, d.unterzuege[0].bis), (p1.knoten[1], p1.knoten[2]))
        # Sechs Ecken der Platten, der Ort der Stütze und zwei Ecken der Zone.
        self.assertEqual(len(d.knoten), 9)

    def test_kennungen_und_suche(self):
        p = zwei_felder()
        d = p.decken[0]
        self.assertEqual(d.kennung, "e1")
        self.assertIs(p.bauteil("e1"), d)
        self.assertEqual([[t.kennung for t in getattr(d, liste)]
                          for liste in ("platten", "linienlager", "stuetzen", "unterzuege", "zonen")],
                         [["P1", "P2"], ["L1", "L2", "L3", "L4"], ["S1"], ["U1"], ["Z1"]])
        self.assertEqual(d.materialien(), ["b1"])

    def test_neu_hat_die_faelle_eines_frischen_balkensystems(self):
        d = DeckeEintrag.neu("e1", "Decke")
        self.assertEqual((d.knoten, d.platten, d.linienlager, d.stuetzen, d.unterzuege, d.zonen),
                         ([], [], [], [], [], []))
        self.assertEqual((d.streifenbreite, d.aufteilung.value), (0.25, "automatisch"))
        self.assertEqual([(lf.kennung, lf.name, lf.eigengewicht) for lf in d.lastfaelle],
                         [("LF1", "Eigengewicht", True), ("LF2", "Auflast", False), ("LF3", "Nutzlast", False)])
        self.assertEqual({k.name: k.faktoren for k in d.kombinationen},
                         {"GZT": {"LF1": 1.35, "LF2": 1.35, "LF3": 1.5},
                          "GZG": {"LF1": 1.0, "LF2": 1.0, "LF3": 1.0}})
        b = BalkensystemEintrag.neu("r1", "System")
        self.assertEqual((b.lastfaelle, b.kombinationen), (d.lastfaelle, d.kombinationen))
        gzt = next(k.kennung for k in d.kombinationen if k.name == "GZT")
        self.assertEqual([(z.fall, z.groesse) for z in d.diagramme],
                         [(gzt, "m_x"), (gzt, "m_y"), (gzt, "v_0"), (gzt, "lager")])

    def test_ein_anteil_ueber_hundert_haelt_das_rechnen_auf(self):
        """Die Grenzen eines Felds prüft das Rechnen, nicht schon das Zeichnen."""
        p = zwei_felder()
        p.decken[0].zone([(0, 0), (1, 0), (1, 1)], anteil=120.0)
        with self.assertRaisesRegex(ProjektFehler, "zonen 2: Anteil in Richtung 1 muss mindestens null "
                                                   "und höchstens 100 % sein, angegeben ist 120 %"):
            p.aufbauen()


class TestModell(unittest.TestCase):
    """Die Beschreibung in mm, Grad und % wird ein Modell in SI."""

    def test_einheiten(self):
        decke, meldungen = modell_von(zwei_felder().decken[0])
        self.assertEqual(meldungen, [])
        self.assertEqual([round(p.h, 9) for p in decke.platten], [0.2, 0.25])
        self.assertAlmostEqual(decke.platten[0].richtungen[1], math.pi / 2.0)
        self.assertAlmostEqual(decke.zonen[0].anteil, 0.3)
        self.assertEqual(decke.unterzuege[0].breite, 0.5)
        s = decke.stuetzen[0]
        self.assertEqual((round(s.bx, 9), s.lx, s.ly), (0.3, None, None))

    def test_ein_stuetzenbereich_von_hand(self):
        d = zwei_felder().decken[0]
        d.stuetzen[0].bereich_von_hand = True
        d.stuetzen[0].l_x, d.stuetzen[0].l_y = 1.2, 0.8
        s = modell_von(d)[0].stuetzen[0]
        self.assertEqual((s.lx, s.ly), (1.2, 0.8))

    def test_ein_fehlender_knoten_ist_eine_meldung(self):
        d = zwei_felder().decken[0]
        d.platten[1].knoten[0] = "K99"
        decke, meldungen = modell_von(d)
        self.assertEqual([p.name for p in decke.platten], ["P1"])
        self.assertEqual([m.elemente for m in meldungen], [("P2",)])


class TestLasten(unittest.TestCase):
    """Lasten je Lastfall, in kN/m², kN/m und kN -- im Modell in SI, nach Namen kombiniert."""

    def test_hin_und_zurueck(self):
        p = mit_lasten()
        self.assertEqual(Projekt.aus_dict(p.als_dict()), p)
        d = p.decken[0]
        self.assertEqual([[e.kennung for e in getattr(d, liste)]
                          for liste in ("flaechenlasten", "linienlasten", "punktlasten")],
                         [["FL1"], ["LL1"], ["PL1"]])

    def test_im_modell_in_si(self):
        decke, meldungen = modell_von(mit_lasten().decken[0])
        self.assertEqual(meldungen, [])
        je = {lf.name: (lf.eigengewicht, lf.lasten) for lf in decke.lastfaelle}
        self.assertEqual(je["Eigengewicht"], (True, []))
        self.assertEqual(je["Auflast"], (False, [Flaechenlast("P1", 1500.0, platte="P1"),
                                                 Linienlast("LL1", (1.0, 1.0), (3.0, 1.0), 8000.0)]))
        flaeche, punkt = je["Nutzlast"][1]
        self.assertEqual((flaeche.name, flaeche.wert, len(flaeche.ecken)), ("FL1", 3000.0, 4))
        self.assertEqual(punkt, Punktlast("PL1", (2.0, 2.0), 20000.0, 0.5, 1.0))
        self.assertEqual({k.name: k.faktoren for k in decke.kombinationen},
                         {"GZT": {"Eigengewicht": 1.35, "Auflast": 1.35, "Nutzlast": 1.5},
                          "GZG": {"Eigengewicht": 1.0, "Auflast": 1.0, "Nutzlast": 1.0}})

    def test_eine_plattenlast_je_lastfall(self):
        """Wie in der Oberfläche: eine zweite Last auf derselben Platte im selben Lastfall ersetzt die erste."""
        d = mit_lasten().decken[0]
        d.plattenlast("LF2", "P1", 2.5)
        d.plattenlast("LF3", "P1", 4.0)
        self.assertEqual([(q.lastfall, q.wert) for q in d.platten[0].lasten], [("LF2", 2.5), ("LF3", 4.0)])
        with self.assertRaisesRegex(ProjektFehler, "eine Platte 'P9' gibt es nicht"):
            d.plattenlast("LF2", "P9", 1.0)

    def test_eine_last_ohne_lastfall_ist_ein_hinweis(self):
        """Sie bleibt weg, wie im Balkensystem -- der Rest rechnet."""
        p = mit_lasten()
        d = p.decken[0]
        d.punktlast("LF9", (2, 2), wert=20.0)
        d.kombinationen[0].faktoren["LF9"] = 2.0
        decke, meldungen = modell_von(d)
        self.assertEqual([(m.text, m.fehler) for m in meldungen], [
            ("PL2: die Last gehört zu keinem Lastfall – sie wird nicht gerechnet.", False),
            ("Kombination «GZT»: einen Lastfall «LF9» gibt es nicht – sein Beiwert zählt nicht.", False)])
        self.assertNotIn("PL2", [l.name for lf in decke.lastfaelle for l in lf.lasten])
        self.assertTrue(zeichnung(p).daten["uebersicht"]["gerechnet"])

    def test_gleiche_namen_halten_die_decke_auf(self):
        """Mit denselben Worten wie im Balkensystem -- die Regel steht an einer Stelle."""
        p = mit_lasten()
        p.decken[0].lastfaelle[2].name = "Auflast"
        b = p.balkensystem("Träger")
        b.standardfaelle()
        b.lastfaelle[2].name = "Auflast"
        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        self.assertEqual(antwort.status, 200)
        bilder = antwort.daten["zeichendaten"]
        satz = "Mehrere Lastfälle heissen «Auflast» – sie wären nicht zu unterscheiden. " \
               "Gerechnet wird erst mit verschiedenen Namen."
        for meldungen in (bilder["e1"]["meldungen"], bilder[b.kennung]["uebersicht"]["meldungen"]):
            self.assertIn(satz, [m["text"] for m in meldungen if m["fehler"]])
        self.assertFalse(bilder["e1"]["gerechnet"])

    def test_die_probe_je_fall(self):
        """Je Fall tragen die Lager die ganze Last; eine Kombination ist die Summe ihrer Fälle mal Beiwert."""
        faelle = {f["name"]: f for f in zeichnung(mit_lasten()).daten["uebersicht"]["faelle"]}
        self.assertEqual(list(faelle), ["Eigengewicht", "Auflast", "Nutzlast", "GZT", "GZG"])
        # 4 · 3 · 0.20 · 25 + 4 · 3 · 0.25 · 25 kN; 1.5 · 12 + 8 · 2; 3 · 4 + 20.
        for name, summe in (("Eigengewicht", 135.0), ("Auflast", 34.0), ("Nutzlast", 32.0)):
            self.assertAlmostEqual(faelle[name]["summe"], summe, places=6)
        self.assertAlmostEqual(faelle["GZT"]["summe"], 1.35 * 135.0 + 1.35 * 34.0 + 1.5 * 32.0, places=6)
        for f in faelle.values():
            self.assertAlmostEqual(f["lager"], f["summe"], places=6)
            self.assertEqual((f["daneben"], f["nicht_getragen"], f["meldungen"]), (0.0, 0.0, []))

    def test_daneben_meldet_der_fall(self):
        """Was neben den Platten liegt, trägt niemand -- ein Hinweis des Lastfalls und seiner Kombinationen."""
        p = mit_lasten()
        p.decken[0].flaechenlasten[0].knoten[1:3] = [p.decken[0].netz().an(9.0, 0.5),
                                                     p.decken[0].netz().an(9.0, 2.5)]
        faelle = {f["name"]: f for f in zeichnung(p).daten["uebersicht"]["faelle"]}
        # Von x = 8 bis 9 liegt sie neben den Platten: 3 kN/m² · 1 m · 2 m.
        self.assertAlmostEqual(faelle["Nutzlast"]["daneben"], 6.0, places=6)
        self.assertAlmostEqual(faelle["GZT"]["daneben"], 1.5 * 6.0, places=6)
        self.assertEqual([(m["text"], m["elemente"], m["fehler"]) for m in faelle["Nutzlast"]["meldungen"]],
                         [("Die Last «FL1» liegt zum Teil neben den Platten: 6 kN trägt niemand.", ["FL1"], False)])


class TestZeichnung(unittest.TestCase):
    """Was die Oberfläche beim Zeichnen vom Kern bekommt -- mit dem Rechnen und allein."""

    def test_rechnen_zeichnet_die_decke(self):
        antwort = dienst.bearbeite("rechnen", {"projekt": zwei_felder().als_dict()})
        self.assertEqual(antwort.status, 200)
        bild = antwort.daten["zeichendaten"]["e1"]
        self.assertTrue(bild["gerechnet"])
        self.assertEqual([m for m in bild["meldungen"] if m["fehler"]], [])
        self.assertEqual([r["name"] for r in bild["richtungen"]], ["x", "y"])
        self.assertEqual([u["name"] for u in bild["unterzuege"]], ["U1"])
        self.assertEqual([b["name"] for b in bild["stuetzenbereiche"]], ["S1"])
        self.assertTrue(bild["anteile"] and all(0.0 <= a["anteil"] <= 100.0 for a in bild["anteile"]))
        self.assertEqual({g["richtung"] for g in bild["grenzen"]}, {1, 2})
        # Die eigene Anfrage des Zeichenfensters sagt dasselbe.
        self.assertEqual(zeichnung(zwei_felder()).daten["uebersicht"], bild)

    def test_nur_fuer_eine_decke(self):
        p = zwei_felder()
        p.balkensystem("Träger")
        antwort = zeichnung(p, "r1")
        self.assertEqual((antwort.status, antwort.daten["fehler"]), (400, "'r1' ist keine Decke."))

    def test_ohne_platte_wird_nichts_gerechnet(self):
        p = Projekt(name="Leer")
        p.beton()
        p.decke("Leer")
        antwort = zeichnung(p)
        self.assertEqual(antwort.status, 200)
        self.assertFalse(antwort.daten["uebersicht"]["gerechnet"])

    def test_die_meldung_nennt_die_kennung_im_projekt(self):
        p = zwei_felder()
        p.decken[0].platte([(10, 0), (12, 0), (12, 2), (10, 2)], beton="b1", h=200)
        meldungen = zeichnung(p).daten["uebersicht"]["meldungen"]
        ohne = [m for m in meldungen if "trägt keine der beiden Richtungen" in m["text"]]
        self.assertEqual([m["elemente"] for m in ohne], [["P3"]])


class TestBilder(unittest.TestCase):
    """Die Bilder eines Falls: Schnittkräfte in Zellen, ihre grössten Werte und was die Lager tragen."""

    @classmethod
    def setUpClass(cls):
        cls.antwort = bilder(mit_lasten(), "GZT")
        cls.e = cls.antwort.daten["ergebnis"]

    def test_die_zellen_decken_die_platten(self):
        self.assertEqual(self.antwort.status, 200)
        self.assertAlmostEqual(sum(geo.flaeche(z) for z in self.e["zellen"]), 8.0 * 3.0, places=3)
        self.assertEqual(set(self.e["werte"]), set(GROESSEN))
        self.assertTrue(all(len(w) == len(self.e["zellen"]) for w in self.e["werte"].values()))
        self.assertEqual(self.e["einheiten"]["m_x"], "kNm/m")
        self.assertEqual(self.e["einheiten"]["v_0"], "kN/m")

    def test_die_extreme_fassen_jede_zelle(self):
        for g, extrem in self.e["extreme"].items():
            self.assertLessEqual(max(self.e["werte"][g]), extrem["groesst"]["wert"], g)
            self.assertGreaterEqual(min(self.e["werte"][g]), extrem["kleinst"]["wert"], g)
        # Ohne Einspannung kein negatives Moment ausser über Unterzug und Stütze.
        self.assertLess(self.e["extreme"]["m_x"]["kleinst"]["wert"], 0.0)

    def test_die_lager_tragen_die_last(self):
        faelle = {f["name"]: f for f in self.antwort.daten["uebersicht"]["faelle"]}
        stuetzen = sum(s["F"] for s in self.e["stuetzen"])
        waende = sum(l["F"] for l in self.e["linienlager"])
        self.assertAlmostEqual(stuetzen + waende, faelle["GZT"]["lager"], places=3)
        self.assertEqual([s["name"] for s in self.e["stuetzen"]], ["S1"])
        for l in self.e["linienlager"]:
            self.assertAlmostEqual(sum((ub - ua) * r for ua, ub, r, _ in l["stufen"]), l["F"], places=2)
            self.assertEqual(l["r_max"], max((s[2] for s in l["stufen"]), key=abs))
            self.assertEqual((l["eingespannt"], l["m_max"]), (False, 0.0))

    def test_eingespannt_das_moment_als_betrag(self):
        """Kragplatte 2 m, an der Wand eingespannt: q·L²/2 = 20 kNm/m, ob die Wand auf- oder abwärts gezeichnet ist."""
        for a, b in (((0, 0), (0, 1)), ((0, 1), (0, 0))):
            p = Projekt(name="Krag")
            d = p.decke("Krag", streifenbreite=0.5)
            d.platte([(0, 0), (2, 0), (2, 1), (0, 1)], beton=p.beton("C30/37"), h=200)
            d.lager(a, b, eingespannt=True)
            fall = d.lastfall("q")
            d.plattenlast(fall, "P1", 10.0)
            (wand,) = bilder(p, "q").daten["ergebnis"]["linienlager"]
            self.assertTrue(wand["eingespannt"])
            self.assertAlmostEqual(wand["F"], 20.0, places=6)
            self.assertAlmostEqual(wand["m_max"], 20.0, places=6)

    def test_kolloquium_4(self):
        """
        Die Beispieldecke: m_x bis −60.1 kNm/m im Unterzug über der mittleren
        Stütze, m_y bis 123.7 im mittleren Unterzug quer dazu; die Stützen
        tragen 115.0, 276.4 und 115.0 kN, die Wand den Rest der 920.7 kN.
        """
        p = beispiele.jeder_nachweis()
        k4 = next(d for d in p.decken if d.name == "Kolloquium 4")
        e = bilder(p, "q_d", k4.kennung).daten["ergebnis"]
        self.assertEqual(e["extreme"]["m_x"]["kleinst"], {"wert": -60.121, "ort": [4.5, 5.0]})
        self.assertEqual(e["extreme"]["m_y"]["groesst"]["wert"], 123.728)
        self.assertEqual(e["extreme"]["m_y"]["groesst"]["ort"][0], 4.5)
        self.assertEqual([(s["name"], round(s["F"], 1)) for s in e["stuetzen"]],
                         [("S1", 115.0), ("S2", 276.4), ("S3", 115.0)])
        (wand,) = e["linienlager"]
        self.assertAlmostEqual(wand["F"] + sum(s["F"] for s in e["stuetzen"]), 18.6 * 9.0 * 5.5, places=6)

    def test_ohne_fall_nur_die_uebersicht(self):
        antwort = bilder(mit_lasten())
        self.assertEqual(antwort.status, 200)
        self.assertIsNone(antwort.daten["ergebnis"])
        self.assertTrue(antwort.daten["uebersicht"]["gerechnet"])

    def test_ein_fall_den_es_nicht_gibt(self):
        antwort = bilder(mit_lasten(), "GZX")
        self.assertEqual((antwort.status, antwort.daten["fehler"]),
                         (400, "Einen Fall «GZX» gibt es in «Zwei Felder» nicht. "
                               "Gerechnet sind: Eigengewicht, Auflast, Nutzlast, GZT, GZG."))

    def test_nur_fuer_eine_decke(self):
        p = zwei_felder()
        p.balkensystem("Träger")
        antwort = bilder(p, "GZT", "r1")
        self.assertEqual((antwort.status, antwort.daten["fehler"]), (400, "'r1' ist keine Decke."))


if __name__ == "__main__":
    unittest.main()
