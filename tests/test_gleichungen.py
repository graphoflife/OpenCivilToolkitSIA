"""
Analytische Gleichungen: lesen, rechnen, setzen -- und das Blatt im Projekt.

Geprueft wird, was der Formeleditor (MathLive) schreibt, und was daraus in
der Herleitung steht. Und dass nichts, was der Benutzer tippt, ungefiltert
bis zu KaTeX kommt.
"""

import math
import unittest

from opencivil.core.einheiten import GRAD, KN, M, MM, MPA, Groesse
from opencivil.gleichungen.ausdruck import (
    AusdruckFehler, anzeigeeinheit, blattname, einheit_aus_text, lesen, namen,
    rechnen, setzen,
)
from opencivil.projekt import Projekt
from opencivil.projekt.gleichungen import (
    GleichungsblattEintrag, GleichungszeileEintrag as Zeile,
)
from opencivil.web import dienst


def wert(latex: str, **werte) -> Groesse:
    gelesen = lesen(latex)
    return rechnen(gelesen.ausdruck, werte)


def vorlage(latex: str) -> str:
    ausdruck = lesen(latex).ausdruck
    return setzen(ausdruck, {n: n for n in namen(ausdruck)})


class TestLesenUndRechnen(unittest.TestCase):
    def test_zahlen(self):
        for latex, erwartet in ((r"3", 3.0), (r"3.5", 3.5), (r"3{,}5", 3.5),
                                (r"-2", -2.0), (r"3{,}5\cdot10^{-3}", 0.0035)):
            with self.subTest(latex=latex):
                self.assertAlmostEqual(wert(latex).si, erwartet)

    def test_punkt_vor_strich_und_klammern(self):
        self.assertEqual(wert(r"1+2\cdot3").si, 7)
        self.assertEqual(wert(r"\left(1+2\right)\cdot3").si, 9)
        self.assertEqual(wert(r"2^{3}").si, 8)
        self.assertEqual(wert(r"-2^{2}").si, -4)
        self.assertEqual(wert(r"\frac{1}{4}").si, 0.25)
        self.assertEqual(wert(r"8/2/2").si, 2)

    def test_implizites_mal(self):
        """``2a`` und ``ab`` sind Produkte -- wie auf Papier."""
        a, b = Groesse(3, M), Groesse(2, M)
        self.assertEqual(wert(r"2a", a=a).in_einheit(M), 6)
        self.assertEqual(wert(r"ab", a=a, b=b).in_einheit(M ** 2), 6)
        self.assertEqual(wert(r"2\left(a+b\right)", a=a, b=b).in_einheit(M), 10)

    def test_namen_mit_index_und_griechisch(self):
        self.assertEqual(lesen(r"f_{cd}=1").name.latex, "f_{cd}")
        self.assertEqual(lesen(r"A_s=1").name.latex, "A_{s}")
        self.assertEqual(lesen(r"\sigma_{s,adm}=1").name.latex, r"\sigma_{s,adm}")
        self.assertEqual(namen(lesen(r"\alpha\cdot\beta_{1}").ausdruck),
                         [r"\alpha", r"\beta_{1}"])

    def test_der_name_eines_projektwerts(self):
        """Der Vorschlag im Blatt: ohne Sorte und Fall, und nur, was der Leser annimmt."""
        self.assertEqual(blattname(r"f_{cd,\text{C30/37}}"), "f_{cd}")
        self.assertEqual(blattname(r"k_{\sigma}"), r"k_{\sigma}")
        self.assertEqual(blattname(r"\varnothing_{1,y,g}"), "")
        self.assertEqual(blattname(r"M_{Rd,x}^{+}"), "")

    def test_einheiten(self):
        self.assertEqual(wert(r"3\mathrm{m}+20\mathrm{cm}").in_einheit(M), 3.2)
        q = wert(r"5\mathrm{kN}/\mathrm{m}^{2}")
        self.assertAlmostEqual(q.si, 5000.0)
        self.assertEqual(anzeigeeinheit(q).name, "kN/m^2")
        self.assertAlmostEqual(wert(r"30^{\circ}").si, math.radians(30))
        self.assertAlmostEqual(wert(r"5\%").si, 0.05)

    def test_funktionen(self):
        self.assertAlmostEqual(wert(r"\sin\left(30^{\circ}\right)").si, 0.5)
        self.assertAlmostEqual(wert(r"\cos\left(\pi\right)").si, -1.0)
        self.assertAlmostEqual(wert(r"\ln\left(e\right)", e=Groesse(math.e)).si, 1.0)
        self.assertAlmostEqual(wert(r"\log\left(1000\right)").si, 3.0)
        self.assertAlmostEqual(wert(r"\sqrt{16\mathrm{m}^{2}}").in_einheit(M), 4.0)
        self.assertAlmostEqual(wert(r"\sqrt[3]{27}").si, 3.0)
        self.assertAlmostEqual(wert(r"\sqrt[3]{-8}").si, -2.0)
        self.assertEqual(wert(r"\min\left(3\mathrm{m},2\mathrm{m}\right)").in_einheit(M), 2)
        self.assertEqual(wert(r"\left|3-5\right|").si, 2)
        self.assertEqual(wert(r"2|3-5|").si, 4)
        winkel = wert(r"\arctan\left(1\right)")
        self.assertEqual(winkel.anzeige, GRAD)
        self.assertAlmostEqual(winkel.in_einheit(GRAD), 45.0)

    def test_definition_und_auswertung(self):
        self.assertEqual(lesen(r"b=2a").name.latex, "b")
        self.assertIsNone(lesen(r"a\cdot b=").name)
        self.assertIsNone(lesen(r"a\cdot b").name)
        self.assertEqual(lesen(r"b:=2a").name.latex, "b")
        self.assertEqual(lesen(r"b\coloneq2a").name.latex, "b")


class TestFehler(unittest.TestCase):
    def fehler(self, latex: str, **werte) -> str:
        with self.assertRaises(AusdruckFehler) as kontext:
            wert(latex, **werte)
        return str(kontext.exception)

    def test_saetze(self):
        self.assertIn("nicht definiert", self.fehler(r"a+1"))
        self.assertIn("Einheiten", self.fehler(r"1\mathrm{m}+1\mathrm{kN}"))
        self.assertIn("Division durch null", self.fehler(r"\frac{1}{0}"))
        self.assertIn("ohne Einheit", self.fehler(r"\ln\left(3\mathrm{m}\right)"))
        self.assertIn("positive", self.fehler(r"\ln\left(-1\right)"))
        self.assertIn("negativen", self.fehler(r"\sqrt{-4}"))
        self.assertIn("unbekannt", self.fehler(r"3\mathrm{xy}"))
        self.assertIn("kein Name", self.fehler(r"a+b=3"))
        self.assertIn("Leerstelle", self.fehler(r"\frac{\placeholder{}}{2}"))
        self.assertIn("unvollständig", self.fehler(r"3+"))

    def test_fremde_befehle_kommen_nicht_durch(self):
        """Ein ``\\href`` erreicht KaTeX nie -- der Leser weist es ab."""
        for latex in (r"\href{javascript:alert(1)}{x}", r"\htmlClass{a}{x}",
                      r"\includegraphics{x}", r"x=\url{y}"):
            with self.subTest(latex=latex):
                with self.assertRaises(AusdruckFehler):
                    lesen(latex)

    def test_die_vorlage_schreibt_der_baum(self):
        """Nur Befehle, die der Baum selbst setzt -- nie, was getippt wurde."""
        self.assertEqual(vorlage(r"b=2a+1\mathrm{m}"), r"2 \cdot @a + 1\,\mathrm{m}")
        self.assertEqual(vorlage(r"\dfrac{a}{b}"), r"\frac{@a}{@b}")
        self.assertEqual(vorlage(r"a\times\left(b+c\right)"),
                         r"@a \cdot \left(@b + @c\right)")
        self.assertEqual(vorlage(r"a-\left(b-c\right)"), r"@a - \left(@b - @c\right)")
        self.assertEqual(vorlage(r"\sin\left(30^{\circ}\right)"),
                         r"\sin\left(30{}^{\circ}\right)")
        self.assertEqual(vorlage(r"5\mathrm{kN}/\mathrm{m}^{2}"),
                         r"5\,\mathrm{kN}/\mathrm{m}^{2}")


class TestEinheiten(unittest.TestCase):
    def test_gewuenschte_einheit(self):
        for text, erwartet in (("kN/m^2", 1e3), ("N/mm2", 1e6), ("mm", 1e-3),
                               ("kNm", 1e3), ("m³", 1.0)):
            with self.subTest(text=text):
                self.assertAlmostEqual(einheit_aus_text(text).faktor, erwartet)
        self.assertIsNone(einheit_aus_text(""))
        # Aus dem Katalog, samt Beschriftung -- nicht «N/mm2».
        self.assertEqual(einheit_aus_text("N/mm2").beschriftung, "N/mm²")
        with self.assertRaises(AusdruckFehler):
            einheit_aus_text("parsec")

    def test_vorzug_nach_groesse(self):
        """
        Zusammengesetzt: 0.265 m liest sich als 265 mm, 5 kN/m² nicht als
        0.005 N/mm². Eine getippte Einheit bleibt, wie sie ist.
        """
        self.assertEqual(anzeigeeinheit(Groesse(0.265, M) * Groesse(1.0)).name, "m")
        self.assertEqual(
            anzeigeeinheit(Groesse(0.53, M) * Groesse(0.5, M) / Groesse(1, M)).name, "mm")
        self.assertEqual(anzeigeeinheit(Groesse(3, M) * Groesse(2, M)).name, "m^2")
        self.assertEqual(anzeigeeinheit(Groesse(5, KN) / Groesse(1, M) / Groesse(1, M)).name,
                         "kN/m^2")
        self.assertEqual(anzeigeeinheit(Groesse(30, MPA) * Groesse(1.0)).name, "MPa")
        with self.assertRaises(AusdruckFehler):
            anzeigeeinheit(Groesse(3, M), einheit_aus_text("kN"))


def projekt_mit_blatt(*zeilen) -> Projekt:
    projekt = Projekt.beispiel()
    projekt.gleichungen.append(GleichungsblattEintrag("g1", "Vorbemessung", list(zeilen)))
    return projekt


def gerechnet(projekt: Projekt):
    daten = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()}).daten
    return daten["gleichungen"]["g1"], daten


class TestBlatt(unittest.TestCase):
    def test_zeile_fuer_zeile(self):
        zeilen, daten = gerechnet(projekt_mit_blatt(
            Zeile(latex=r"a=3\mathrm{m}"), Zeile(latex=r"b=2a+1\mathrm{m}"),
            Zeile(latex=r"a\cdot b="), Zeile(latex=r"A=a\cdot b", einheit="cm^2")))
        self.assertEqual([z["ergebnis"] for z in zeilen],
                         [r"3\,\mathrm{m}", r"7\,\mathrm{m}", r"21\,\mathrm{m}^{2}",
                          r"210000\,\mathrm{cm}^{2}"])
        latex = [b["latex"] for b in daten["protokoll"] if b.get("art") == "gleichung"]
        self.assertIn(r"b = 2 \cdot a + 1\,\mathrm{m} = 2 \cdot 3\,\mathrm{m} + "
                      r"1\,\mathrm{m} = 7\,\mathrm{m}", latex)
        self.assertIn(r"a \cdot b = 3\,\mathrm{m} \cdot 7\,\mathrm{m} = 21\,\mathrm{m}^{2}",
                      latex)

    def test_neudefinition_gilt_ab_ihrer_zeile(self):
        zeilen, _ = gerechnet(projekt_mit_blatt(
            Zeile(latex=r"a=1"), Zeile(latex=r"a="), Zeile(latex=r"a=2"),
            Zeile(latex=r"a=")))
        self.assertEqual([z["ergebnis"] for z in zeilen][1::2], ["1", "2"])

    def test_ein_fehler_bleibt_bei_seiner_zeile(self):
        """... und bei denen, die sein Ergebnis brauchen -- mit Verweis."""
        zeilen, daten = gerechnet(projekt_mit_blatt(
            Zeile(latex=r"a=1\mathrm{m}"), Zeile(latex=r"a=a+1\mathrm{kN}"),
            Zeile(latex=r"b=2a"), Zeile(latex=r"c=3")))
        self.assertEqual(zeilen[1]["fehler"], "Einheiten passen nicht zusammen.")
        self.assertEqual(zeilen[2]["fehler"], "a: Fehler in Zeile 2.")
        self.assertEqual(zeilen[3]["ergebnis"], "3")
        # Die Platten rechnen weiter.
        self.assertTrue(daten["zusammenfassungen"]["q1"]["zeilen"])

    def test_projektwerte(self):
        zeilen, _ = gerechnet(projekt_mit_blatt(
            Zeile(art="projektwert", name=r"f_{cd}", wert_id="beton.b1.f_cd"),
            Zeile(art="projektwert", name=r"h", wert_id="querschnitt.q1.h"),
            Zeile(latex=r"N=f_{cd}\cdot h\cdot1\mathrm{m}", einheit="MN"),
            Zeile(art="projektwert", name=r"x", wert_id="gibt.es.nicht"),
            Zeile(art="projektwert", name=r"a+b", wert_id="beton.b1.f_cd"),
            Zeile(art="projektwert", name=r"y"), Zeile(latex=r"y="),
            Zeile(art="projektwert")))
        self.assertEqual(zeilen[0]["ergebnis"], r"20\,\mathrm{N}/\mathrm{mm}^{2}")
        self.assertEqual(zeilen[2]["ergebnis"], r"6\,\mathrm{MN}")
        self.assertEqual(zeilen[3]["fehler"], "Projektwert nicht verfügbar.")
        self.assertIn("Name fehlt", zeilen[4]["fehler"])
        self.assertEqual(zeilen[5]["fehler"], "Wert wählen.")
        self.assertEqual(zeilen[6]["fehler"], "y: Fehler in Zeile 6.")
        # Frisch angefuegt und leer: still, wie eine leere Formelzeile.
        self.assertEqual((zeilen[7]["fehler"], zeilen[7]["ergebnis"]), ("", ""))

    def test_im_bericht_und_in_der_ablage(self):
        projekt = projekt_mit_blatt(Zeile(latex=r"a=3\mathrm{m}"),
                                    Zeile(art="text", text="Nur ein Satz."))
        self.assertEqual(Projekt.aus_dict(projekt.als_dict()), projekt)
        bericht = projekt.rechnen().bericht()
        self.assertIn("Analytische Gleichungen – Vorbemessung", bericht)
        self.assertIn("Nur ein Satz.", bericht)

    def test_die_zeilen_stehen_in_der_werteliste(self):
        """
        Was die Zeilen ergeben, steht in der Loesung und in der Werteliste --
        das Ziel des Blatts, die Zahl der aufgegangenen Zeilen, nicht. Ein
        Projektwert behaelt die Herkunft des Originals.
        """
        projekt = projekt_mit_blatt(
            Zeile(latex=r"a=3\mathrm{m}"), Zeile(art="text", text="Satz."),
            Zeile(art="projektwert", name=r"h", wert_id="querschnitt.q1.h"),
            Zeile(latex=r"a+"))
        ergebnis = projekt.rechnen()
        werte = ergebnis.loesung.werte
        self.assertEqual(werte["gleichungen.g1.z001"].beschreibung, "Vorbemessung, Zeile 1")
        self.assertEqual(werte["gleichungen.g1.z003"].quelle, werte["querschnitt.q1.h"].quelle)
        self.assertNotIn("gleichungen.g1.z004", werte)
        bericht = ergebnis.bericht()
        self.assertIn("Vorbemessung, Zeile 3", bericht)
        self.assertNotIn("Zeilen ohne Fehler", bericht)

    def test_eine_neue_kennung_kennt_die_blaetter(self):
        projekt = projekt_mit_blatt()
        self.assertEqual(projekt.freie_kennung("g"), "g2")


if __name__ == "__main__":
    unittest.main()
