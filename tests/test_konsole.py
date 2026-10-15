"""
Die App «Python»: die Sitzung, das Zeichenmodul, die Pakete und der Dienst.

Geprüft unter CPython -- im Browser läuft dieselbe Datei in Pyodide. Nur das
Nachladen der Pakete gibt es hier nicht; dass die richtigen gemeint sind,
zeigt :func:`gebraucht`.
"""

import asyncio
import json
import unittest

from opencivil.konsole import pakete, zeichnen
from opencivil.konsole.dienst import bearbeite_json
from opencivil.konsole.sitzung import Sitzung

try:
    import numpy
except ImportError:  # pragma: no cover -- nicht überall installiert
    numpy = None


def texte(lauf, art):
    return [e["text"] for e in lauf.ereignisse if e["art"] == art]


class TestSitzung(unittest.TestCase):
    def setUp(self):
        self.sitzung = Sitzung()

    def test_ausgabe_der_reihe_nach(self):
        lauf = self.sitzung.ausfuehren(
            "print('a')\nimport sys\nprint('b', file=sys.stderr)\nprint('c')")
        self.assertTrue(lauf.fehlerfrei)
        self.assertEqual([(e["art"], e["text"]) for e in lauf.ereignisse],
                         [("ausgabe", "a\n"), ("fehlerausgabe", "b\n"), ("ausgabe", "c\n")])

    def test_der_namensraum_bleibt(self):
        """Was Skript A anlegt, sieht Skript B -- eine Sitzung für alle."""
        self.sitzung.ausfuehren("a = 3", name="Skript A")
        lauf = self.sitzung.ausfuehren("print(a * 2)", name="Skript B")
        self.assertEqual(texte(lauf, "ausgabe"), ["6\n"])

    def test_die_konsole_zeigt_den_wert_der_letzten_zeile(self):
        self.sitzung.ausfuehren("a = 3")
        lauf = self.sitzung.ausfuehren("b = a + 1\nb * 10", eingabe=True)
        self.assertEqual(texte(lauf, "wert"), ["40"])
        # Ein Skript zeigt ihn nicht -- wie python skript.py.
        self.assertEqual(texte(self.sitzung.ausfuehren("b * 10"), "wert"), [])
        # Und None steht nicht da.
        self.assertEqual(texte(self.sitzung.ausfuehren("print", eingabe=True), "wert"),
                         ["<built-in function print>"])
        self.assertEqual(self.sitzung.ausfuehren("None", eingabe=True).ereignisse, [])

    def test_ein_fehler_nennt_skript_und_zeile(self):
        lauf = self.sitzung.ausfuehren("def f(x):\n    return 1 / x\n\nf(0)", name="Skript 1")
        self.assertFalse(lauf.fehlerfrei)
        fehler = texte(lauf, "fehler")[0]
        self.assertIn('File "Skript 1", line 4', fehler)
        self.assertIn("return 1 / x", fehler)
        self.assertIn("ZeroDivisionError", fehler)
        # Die Rahmen der Sitzung selbst stehen nicht darin.
        self.assertNotIn("sitzung.py", fehler)

    def test_ein_syntaxfehler(self):
        lauf = self.sitzung.ausfuehren("x = (", name="Skript 1")
        self.assertIn("SyntaxError", texte(lauf, "fehler")[0])
        self.assertIn('"Skript 1", line 1', texte(lauf, "fehler")[0])

    def test_was_vor_dem_fehler_kam_bleibt(self):
        lauf = self.sitzung.ausfuehren("print('vorher')\nraise ValueError('kaputt')")
        self.assertEqual(texte(lauf, "ausgabe"), ["vorher\n"])
        self.assertIn("ValueError: kaputt", texte(lauf, "fehler")[0])

    def test_input_geht_nicht(self):
        fehler = texte(self.sitzung.ausfuehren("input('Zahl?')"), "fehler")[0]
        self.assertIn("input() geht hier nicht", fehler)
        self.assertNotIn("sitzung.py", fehler)

    def test_ein_fehlendes_paket_sagt_was_beiliegt(self):
        fehler = texte(self.sitzung.ausfuehren("import gibtesnicht"), "fehler")[0]
        self.assertIn("ModuleNotFoundError", fehler)
        self.assertIn("gibtesnicht liegt hier nicht bei", fehler)

    def test_zuruecksetzen_leert(self):
        self.sitzung.ausfuehren("a = 1")
        self.sitzung.zuruecksetzen()
        self.assertEqual(self.sitzung.variablen(), [])
        self.assertIn("NameError", texte(self.sitzung.ausfuehren("a"), "fehler")[0])

    def test_opencivil_geht(self):
        lauf = self.sitzung.ausfuehren(
            "from opencivil.core.einheiten import Groesse, KN\nprint(Groesse(1500, KN))")
        self.assertTrue(lauf.fehlerfrei, lauf.ereignisse)


class TestVariablen(unittest.TestCase):
    def test_was_der_beobachter_zeigt(self):
        sitzung = Sitzung()
        sitzung.ausfuehren("import math\n"
                           "def f(): pass\n"
                           "class K: pass\n"
                           "_versteckt = 1\n"
                           "zahl = 3.5\n"
                           "Liste = [1, 2, 3]\n"
                           "text = 'x' * 500\n")
        variablen = sitzung.variablen()
        # Nach Namen, ohne Module, Funktionen, Klassen und Unterstriche.
        self.assertEqual([v["name"] for v in variablen], ["Liste", "text", "zahl"])
        liste, text, zahl = variablen
        self.assertEqual((liste["typ"], liste["groesse"], liste["wert"]), ("list", "3", "[1, 2, 3]"))
        self.assertEqual((zahl["typ"], zahl["groesse"], zahl["wert"]), ("float", "", "3.5"))
        # Lange Werte gekürzt -- in der Zeile mehr als beim Darüberfahren.
        self.assertTrue(text["wert"].endswith("…"))
        self.assertLessEqual(len(text["wert"]), 120)
        self.assertEqual(len(text["lang"]), 502)

    @unittest.skipIf(numpy is None, "numpy ist hier nicht installiert")
    def test_ein_feld_zeigt_form_und_typ(self):
        sitzung = Sitzung()
        sitzung.ausfuehren("import numpy as np\nm = np.zeros((2, 3))")
        (m,) = sitzung.variablen()
        self.assertEqual((m["typ"], m["groesse"]), ("ndarray float64", "2×3"))


class TestZeichnen(unittest.TestCase):
    def bilder(self, code):
        lauf = Sitzung().ausfuehren("import zeichnen as plt\n" + code)
        self.assertTrue(lauf.fehlerfrei, lauf.ereignisse)
        return [e["bild"] for e in lauf.ereignisse if e["art"] == "bild"]

    def test_eine_linie_kommt_am_ende_von_selbst(self):
        (bild,) = self.bilder("plt.plot([0, 1, 2], [0, 1, 4], 'r--o', label='q')\n"
                              "plt.title('T')\nplt.xlabel('x')\nplt.grid()\nplt.legend()")
        self.assertEqual((bild["titel"], bild["xlabel"], bild["gitter"], bild["legende"]),
                         ("T", "x", True, True))
        (reihe,) = bild["reihen"]
        self.assertEqual((reihe["art"], reihe["x"], reihe["y"]), ("linie", [0, 1, 2], [0, 1, 4]))
        self.assertEqual((reihe["farbe"], reihe["strich"], reihe["marke"], reihe["name"]),
                         ("red", "--", "o", "q"))

    def test_show_stellt_das_bild_zwischen_die_ausgaben(self):
        lauf = Sitzung().ausfuehren("import zeichnen as plt\nprint('vorher')\nplt.plot([1, 2])\n"
                                    "plt.show()\nprint('nachher')")
        self.assertEqual([e["art"] for e in lauf.ereignisse], ["ausgabe", "bild", "ausgabe"])

    def test_nur_y_zaehlt_ab_null(self):
        (bild,) = self.bilder("plt.plot([5, 6, 7])")
        self.assertEqual(bild["reihen"][0]["x"], [0, 1, 2])

    def test_balken_mit_namen(self):
        (bild,) = self.bilder("plt.bar(['A', 'B'], [3, 5])\nplt.bar(['B', 'C'], [1, 2])")
        self.assertEqual(bild["kategorien"], ["A", "B", "C"])
        self.assertEqual([r["x"] for r in bild["reihen"]], [[0, 1], [1, 2]])

    def test_luecken_und_farben(self):
        (bild,) = self.bilder("plt.plot([0, 1, 2], [1, float('nan'), None], color=(1, 0, 0))\n"
                              "plt.scatter([1], [2], c='k')")
        linie, punkte = bild["reihen"]
        self.assertEqual(linie["y"], [1, None, None])
        self.assertEqual(linie["farbe"], "rgb(255, 0, 0)")
        self.assertEqual((punkte["art"], punkte["farbe"], punkte["marke"]),
                         ("punkte", "black", "o"))

    def test_zwei_bilder_mit_figure(self):
        self.assertEqual(len(self.bilder("plt.plot([1])\nplt.figure()\nplt.plot([2])")), 2)

    def test_ein_leeres_bild_kommt_nicht(self):
        self.assertEqual(self.bilder("plt.title('nichts')\nplt.show()"), [])

    def test_unsinn_wird_gemeldet(self):
        for code, meldung in (("plt.plot([1, 2], [1])", "x hat 2 Werte, y hat 1"),
                              ("plt.plot([1], 'q')", "Formatzeichen 'q'"),
                              ("plt.plot(['a', 1], [1, 2])", "mischt Namen und Zahlen"),
                              ("plt.axhline(float('inf'))", "endlich"),
                              ("plt.savefig('a.png')", "savefig gibt es hier nicht")):
            with self.subTest(code=code):
                lauf = Sitzung().ausfuehren("import zeichnen as plt\n" + code)
                self.assertFalse(lauf.fehlerfrei)
                self.assertIn(meldung, texte(lauf, "fehler")[0])
                # Ein Fehler verwirft das angefangene Bild.
                self.assertFalse([e for e in lauf.ereignisse if e["art"] == "bild"])

    @unittest.skipIf(numpy is None, "numpy ist hier nicht installiert")
    def test_numpy_geht_hinein(self):
        (bild,) = self.bilder("import numpy as np\nx = np.linspace(0, 1, 3)\nplt.plot(x, x**2)")
        self.assertEqual(bild["reihen"][0]["y"], [0.0, 0.25, 1.0])


class TestPakete(unittest.TestCase):
    def test_importe(self):
        self.assertEqual(pakete.importe("import numpy as np\nfrom pandas import DataFrame\n"
                                        "import os.path\nfrom . import nah\n"
                                        "def f():\n    import numpy.linalg"),
                         ["numpy", "pandas", "os"])
        self.assertEqual(pakete.importe("x = ("), [])

    def test_geladen_wird_nur_was_beiliegt(self):
        beiliegend = pakete.mitgeliefert()
        self.assertEqual(beiliegend.get("numpy"), "numpy")
        self.assertEqual(beiliegend.get("dateutil"), "python-dateutil")
        self.assertEqual(pakete.gebraucht("import numpy\nimport scipy\nimport pandas"),
                         ["numpy", "pandas"])


class TestDienst(unittest.TestCase):
    def frage(self, anfrage, **rumpf):
        return json.loads(asyncio.run(bearbeite_json(anfrage, json.dumps(rumpf))))

    def test_ausfuehren_und_zuruecksetzen(self):
        antwort = self.frage("ausfuehren", code="a = 2\na + 1", name="K", eingabe=True)
        self.assertEqual(antwort["status"], 200)
        daten = antwort["daten"]
        self.assertEqual([e["text"] for e in daten["ereignisse"]], ["3"])
        self.assertIn("a", [v["name"] for v in daten["variablen"]])
        self.assertEqual(self.frage("zuruecksetzen")["daten"]["variablen"], [])

    def test_unbekannte_anfrage(self):
        self.assertEqual(self.frage("gibtesnicht")["status"], 404)


if __name__ == "__main__":
    unittest.main()
