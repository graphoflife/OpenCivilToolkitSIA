"""
Der Bericht einer Decke je Fall: die Träger, was die Lager tragen, die
grössten Schnittkräfte der Platte, die Biegewiderstände, die sie verlangt,
und die Lastverteilelemente -- gegen das Kolloquium 4 und die Bilder
desselben Falls.
"""

import math
import unittest

from opencivil.core.latex import Mathe
from opencivil.core.protokoll import GleichungBlock, HinweisBlock, TabellenBlock, TitelBlock
from opencivil.decke.feld import GROESSEN
from opencivil.decke.herleitung import SCHNITTKRAEFTE
from opencivil.decke.streifen import richtung
from opencivil.projekt import beispiele
from opencivil.web import dienst

PROJEKT = beispiele.jeder_nachweis()


def kennung(name: str) -> str:
    return next(d.kennung for d in PROJEKT.decken if d.name == name)


def gerechnet(name: str, ohne_herleitung: bool = False):
    """Die Lösung einer Beispieldecke und ihr Befund."""
    aufbau = PROJEKT.aufbauen()
    k = kennung(name)
    loesung = aufbau.werk.loese(*aufbau.materialziele(), *aufbau.ziele_von(k), ohne_herleitung=ohne_herleitung)
    return loesung, loesung.befunde[aufbau.decken[k].rechnung.id]


def tabelle(loesung, fall: str, titel: str):
    """Die Zeilen der Tabelle ``titel`` unter dem Fall ``fall``, jede Zelle als Text."""
    im_fall = False
    for b in loesung.protokoll.alle_bloecke():
        if isinstance(b, TitelBlock):
            im_fall = b.text.endswith(f"«{fall}»")
        elif im_fall and isinstance(b, TabellenBlock) and b.titel == titel:
            return [[z.latex if isinstance(z, Mathe) else z for z in zeile] for zeile in b.zeilen]
    raise AssertionError(f"Keine Tabelle «{titel}» unter «{fall}».")


def schief(loesung):
    """Die Hinweise auf schiefe Platten."""
    return [b.text for b in loesung.protokoll.alle_bloecke()
            if isinstance(b, HinweisBlock) and "schief zu x und y" in b.text]


class TestKolloquium4(unittest.TestCase):
    """Die Beispieldecke der Musterlösung: 920.7 kN auf eine Wand und drei Stützen."""

    @classmethod
    def setUpClass(cls):
        cls.loesung, cls.befund = gerechnet("Kolloquium 4")

    def zeilen(self, titel):
        return tabelle(self.loesung, "q_d", titel)

    def test_die_ansaetze_mit_ihrer_stelle(self):
        stellen = {b.titel: b.referenz for b in self.loesung.protokoll.alle_bloecke()
                   if isinstance(b, GleichungBlock)}
        self.assertEqual(stellen["Vom Streifen zur Platte: je Meter, in den Achsen x und y"],
                         "Stahlbeton II, 7.2 Platten, Folie 14")
        self.assertEqual(stellen["Ein Flächenlager drückt gleichmässig über seine Breite l"],
                         "Stahlbeton II, 7.2 Platten, Folie 33")
        self.assertEqual(stellen["Erforderliche Biegewiderstände, linearisierte Fliessbedingung"],
                         "SIA 262:2025, 4.3.2.6, (34)")
        self.assertEqual(stellen["Was ein Lastverteilelement l_x × l_y zusätzlich braucht"],
                         "Stahlbeton II, 7.2 Platten, Folie 38")

    def test_gleiche_feldstreifen_in_einer_zeile(self):
        """
        Die 18 Feldstreifen in x tragen dasselbe: eine Zeile. Die in y trennt
        der mittlere Unterzug -- in seiner Breite tragen sie nichts.
        """
        zeilen = self.zeilen("Träger, je Meter ihrer Breite")
        self.assertEqual([z[0] for z in zeilen], ["x1 … x18", "y5 … y16", "y21 … y32", "U4", "U1", "U2", "U3"])
        self.assertEqual(zeilen[0][3:], ["50.2", "U1 11.4 · U2 27.4 · U3 11.4", "-7.4", "4.50", "6.0", "2.05"])
        self.assertEqual(zeilen[5][4:], ["L1 100.0 · S2 276.4", "0.0", "–", "123.7", "2.47"])

    def test_lagerkraefte(self):
        self.assertEqual(self.zeilen("Lagerkräfte"),
                         [["S1 · Stütze", "115.0", "–"], ["S2 · Stütze", "276.4", "–"],
                          ["S3 · Stütze", "115.0", "–"], ["L1 · Linienlager", "414.3", "100.0"]])

    def test_dieselben_zahlen_wie_im_bild(self):
        """Die grössten Schnittkräfte stehen im Bericht wie im Bild, am selben Ort."""
        bild = dienst.bearbeite("decke_ergebnis", {"projekt": PROJEKT.als_dict(), "kennung": kennung("Kolloquium 4"),
                                                   "fall": "q_d"}).daten["ergebnis"]["extreme"]
        zeilen = self.zeilen("Schnittkräfte der Platte, je Meter")
        self.assertEqual([g for g, _, _ in SCHNITTKRAEFTE], list(GROESSEN))
        for (groesse, _, _), zeile in zip(SCHNITTKRAEFTE, zeilen):
            for art, spalte in (("kleinst", 1), ("groesst", 3)):
                wert, ort = zeile[spalte].split("\\")[0], zeile[spalte + 1]
                self.assertAlmostEqual(float(wert), bild[groesse][art]["wert"], delta=0.051, msg=groesse)
                if ort == "–":
                    self.assertEqual(wert, "0.0", groesse)
                    continue
                for im_bericht, im_bild in zip(ort.strip("()").split(","), bild[groesse][art]["ort"]):
                    self.assertAlmostEqual(float(im_bericht), im_bild, delta=0.006, msg=groesse)

    def test_die_biegewiderstaende(self):
        """Oben in x über der mittleren Stütze 60.1 kNm/m, unten in y im mittleren Unterzug 123.7."""
        zeilen = {z[0]: z[2:] for z in self.zeilen("Erforderliche Biegewiderstände, ohne Lastverteilelemente")}
        self.assertEqual(zeilen["m'_{xu}"], ["60.1\\ \\mathrm{kNm/m}", "(4.50, 5.00)"])
        self.assertEqual(zeilen["m_{yu}"], ["123.7\\ \\mathrm{kNm/m}", "(4.50, 2.47)"])
        self.assertEqual(zeilen["m'_{yu}"], ["0.0\\ \\mathrm{kNm/m}", "–"])

    def test_lastverteilelement_ueber_der_mittelstuetze(self):
        """S2 trägt 276.4 kN über 1 × 1 m: oben 34.5 kNm/m, unten 9.4 -- die Musterlösung 34.4 und 9.4."""
        s2 = self.zeilen("Lastverteilelemente: was der Bereich zusätzlich braucht")[1]
        self.assertEqual(s2, ["S2 · Stütze", "276.4", "1.00 \\times 1.00", "34.5", "9.4", "34.5", "9.4"])

    def test_kein_hinweis_in_x_und_y(self):
        self.assertEqual(schief(self.loesung), [])

    def test_still_dasselbe_ohne_bericht(self):
        """Ohne Herleitung rechnet die Decke dasselbe -- und sucht nichts für einen Bericht, den niemand liest."""
        still, befund = gerechnet("Kolloquium 4", ohne_herleitung=True)
        self.assertEqual(still.protokoll.alle_bloecke(), [])
        laut, leise = self.befund.ergebnis.fall("q_d"), befund.ergebnis.fall("q_d")
        self.assertEqual([laut.stuetzenkraft(s) for s in ("S1", "S2", "S3")],
                         [leise.stuetzenkraft(s) for s in ("S1", "S2", "S3")])


class TestJedeWahl(unittest.TestCase):
    """Geteilte Streifen, drei Richtungen und ein Rand, der nur die Drehung hält."""

    @classmethod
    def setUpClass(cls):
        cls.loesung, _ = gerechnet("Jede Wahl")

    def test_ein_hinweis_bei_der_schiefen_platte(self):
        """P3 trägt in 0° und 71.6°: einmal ein Hinweis, mit beiden Normstellen."""
        (hinweis,) = schief(self.loesung)
        self.assertTrue(hinweis.startswith("Die Platte «P3» trägt schief zu x und y: "), hinweis)
        self.assertIn("(SIA 262:2025, 4.3.2.6)", hinweis)
        self.assertIn("(4.3.2.5)", hinweis)

    def test_schief_ist_weder_x_noch_y(self):
        """Auch 180° ist x -- und zwei rechtwinklige Richtungen, gegen x gedreht, sind schief."""
        self.assertEqual([richtung(math.radians(w)).schief for w in (0, 90, 180, -90, 30, 120)],
                         [False, False, False, False, True, True])

    def test_stuecke_neben_ihresgleichen(self):
        """
        x1 bis x6 laufen in der schiefen Platte weiter: ihre zweiten Stücke
        folgen nach allen ersten, und gleiche erste Stücke stehen in einer
        Zeile, auch mit ungeteilten. x9 bis x14 enden am freien Rand, tragen
        nichts und fehlen.
        """
        namen = [z[0] for z in tabelle(self.loesung, "Eigengewicht", "Träger, je Meter ihrer Breite")]
        self.assertEqual(namen[:4], ["x1.1 … x3.1", "x4.1 … x8", "x15", "x1.2"])
        self.assertEqual(namen[9:12], ["y1 … y3", "y4", "y5 … y6"])

    def test_eingespannt_mit_dem_vorzeichen_der_platte(self):
        """
        L5 hält nur die Drehung: er trägt nichts, aber 102.6 kNm/m mit Zug
        unten -- so viel, wie y7 an ihm hat. Am eingespannten Rand L2 zieht
        es oben.
        """
        lager = {z[0]: z[1:] for z in tabelle(self.loesung, "Eigengewicht", "Lagerkräfte")}
        self.assertEqual(lager["L5 · Linienlager"], ["0.0", "0.0", "102.6"])
        self.assertEqual(lager["L2 · Linienlager"], ["61.8", "20.6", "-24.8"])
        self.assertEqual(lager["S1 · Stütze"], ["6.9", "–", "–"])


if __name__ == "__main__":
    unittest.main()
