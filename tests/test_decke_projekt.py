"""
Die Beschreibung einer Decke: lesen, ablegen, zeichnen ohne Oberfläche --
und was die Oberfläche beim Zeichnen vom Kern bekommt.
"""

import math
import unittest

from opencivil.projekt import DeckeEintrag, Projekt, ProjektFehler
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


def zeichnung(p: Projekt, kennung: str = "e1"):
    return dienst.bearbeite("decke_zeichnung", {"projekt": p.als_dict(), "kennung": kennung})


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

    def test_neu_ist_leer(self):
        d = DeckeEintrag.neu("e1", "Decke")
        self.assertEqual((d.knoten, d.platten, d.linienlager, d.stuetzen, d.unterzuege, d.zonen),
                         ([], [], [], [], [], []))
        self.assertEqual((d.streifenbreite, d.aufteilung.value), (0.25, "automatisch"))

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


if __name__ == "__main__":
    unittest.main()
