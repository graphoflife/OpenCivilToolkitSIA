"""
Das Notizbuch: jede Formel auf einer Seite, die heisst, wie die Formel heisst.

Eine Seite ist dann verlaesslich, wenn ihr Name nur an der Formel haengt --
nicht am Fall, an der Sorte, an der Lage oder an der Reihenfolge. Sonst
waere die Theorie, die unter der Linie von Hand steht, beim naechsten Lauf
an der falschen Formel. Darum diese Pruefungen ueber die ganze Sammlung.
"""

import re
import unittest
from collections import defaultdict
from dataclasses import replace

from opencivil.bericht import formelsammlung as fs
from opencivil.core.berechnung import Eingaben, Formel
from opencivil.core.einheiten import MM, Groesse
from opencivil.core.latex import Formelzeile
from opencivil.core.protokoll import GleichungBlock, Protokoll, codestelle_aus
from opencivil.core.wert import WertDef
from opencivil.notizbuch.namen import (
    HOECHSTENS, NamensFehler, seitenname, sortierschluessel, vergleichsname,
)
from opencivil.projekt import Projekt

DIESES = __name__


def _wert(name: str, si: float = 1.0):
    return WertDef(f"t.{name}", name, MM, beschreibung=f"Länge {name}").belegen(
        Groesse.aus_si(si, MM))


def hilfsfunktion(p: Protokoll) -> None:
    p.formel(_wert("c", 0.003), "@a + @b", {"a": _wert("a"), "b": _wert("b")},
             titel="Summe")


#: Eine Lambda auf Modulebene: ihre Codestelle ist das Modul.
ZWEIMAL = lambda a: 2 * a  # noqa: E731


class Schreiber:
    def methode(self, p: Protokoll) -> None:
        p.ansatz("c = a + b", titel="Ansatz der Summe")


class TestCodestelle(unittest.TestCase):
    def test_aus_namen(self):
        self.assertEqual(codestelle_aus("m", "f"), "m:f")
        self.assertEqual(codestelle_aus("m", "K.f"), "m:K.f")
        self.assertEqual(codestelle_aus("m", "f.<locals>.g"), "m:f")
        self.assertEqual(codestelle_aus("m", "f.<locals>.<lambda>"), "m:f")
        self.assertEqual(codestelle_aus("m", "K.<lambda>"), "m:K")
        self.assertEqual(codestelle_aus("m", "<lambda>"), "m")
        self.assertEqual(codestelle_aus("m", "<module>"), "m")

    def test_funktion_und_methode(self):
        p = Protokoll()
        hilfsfunktion(p)
        Schreiber().methode(p)
        self.assertEqual([b.codestelle for b in p.bloecke],
                         [f"{DIESES}:hilfsfunktion", f"{DIESES}:Schreiber.methode"])

    def test_die_allgemeine_formel_meint_ihre_funktion(self):
        """Geschrieben wird in ``Formel.rechne`` -- gemeint ist die Funktion."""
        aus = WertDef("t.c", "c", MM)
        formel = Formel("t.c", ausgabe=aus, eingaben={"a": "t.a"}, vorlage="2 \\cdot @a",
                        funktion=ZWEIMAL)
        p = Protokoll()
        formel.rechne(Eingaben({"a": _wert("a")}), p)
        self.assertEqual(p.bloecke[0].codestelle, DIESES)

    def test_uebernehmen_und_sammeln_behalten_sie(self):
        p = Protokoll()
        hilfsfunktion(p)
        p.bloecke[0].thema = "Probe"
        kopie = Protokoll()
        kopie.anfuegen(*p.bloecke)
        self.assertEqual(kopie.bloecke[0].codestelle, f"{DIESES}:hilfsfunktion")
        self.assertEqual(fs._symbolisch(kopie.bloecke[0]).codestelle,
                         f"{DIESES}:hilfsfunktion")

    def test_aendert_keinen_vergleich(self):
        """Gleiche Bloecke bleiben gleich, auch wenn sie anderswo entstanden."""
        self.assertEqual(GleichungBlock("x", codestelle="a:b", name="A"),
                         GleichungBlock("x", codestelle="c:d", name="B"))


class TestEingaben(unittest.TestCase):
    def test_nur_die_platzhalter_der_vorlage(self):
        a, b, c = _wert("a"), _wert("b"), _wert("c")
        zeile = Formelzeile.bauen(c, "@a + @a", {"a": a, "b": b})
        self.assertEqual([(n, w.id) for n, w in zeile.eingaben], [("a", "t.a")])

    def test_ohne_vorlage_keine(self):
        self.assertEqual(Formelzeile.bauen(_wert("a")).eingaben, ())

    def test_aendern_keinen_vergleich(self):
        a = _wert("a")
        zeile = Formelzeile.bauen(a, "@a", {"a": a})
        self.assertEqual(zeile, replace(zeile, eingaben=()))


class TestSeitenname(unittest.TestCase):
    def test_tabelle(self):
        for text, name in [
            ("Bemessungswert der Betondruckfestigkeit", "Bemessungswert der Betondruckfestigkeit"),
            ("Probe: Normalkraft", "Probe – Normalkraft"),
            ("Werkstoffgesetze:Beton", "Werkstoffgesetze – Beton"),
            ("C30/37", "C30∕37"),
            ("a|b", "a¦b"),
            ("Nr. #3?", "Nr. 3"),
            ("  viel   Raum  ", "viel Raum"),
            ("[x]", "(x)"),
            ("Ende.", "Ende"),
            (".versteckt", "versteckt"),
        ]:
            with self.subTest(text=text):
                self.assertEqual(seitenname(text), name)
                self.assertEqual(seitenname(name), name)

    def test_nfc(self):
        zerlegt = "Bänder"          # a + Trema
        self.assertEqual(seitenname(zerlegt), "Bänder")

    def test_nie_still_kuerzen(self):
        with self.assertRaises(NamensFehler):
            seitenname("x" * (HOECHSTENS + 1))
        with self.assertRaises(NamensFehler):
            seitenname(" ?# ")

    def test_vergleich_und_sortierung(self):
        self.assertEqual(vergleichsname("Duktilität"), vergleichsname("DUKTILITÄT"))
        self.assertLess(sortierschluessel("Äquivalenter E-Modul"), sortierschluessel("Beton"))
        self.assertEqual(sortierschluessel("Grösse"), sortierschluessel("Grösse".upper()))


class TestNamenDerSammlung(unittest.TestCase):
    """Ueber jede Formel, die das Werkzeug schreibt."""

    @classmethod
    def setUpClass(cls):
        cls.namen = defaultdict(set)      # Schluessel -> Namen
        cls.seiten = defaultdict(set)     # Name -> Schluessel
        cls.stellen = defaultdict(set)    # Schluessel -> Codestellen
        cls.themen = set()
        for lauf in fs.laeufe():
            for b in lauf.alle_bloecke():
                if getattr(b, "thema", ""):
                    cls.themen.add(b.thema)
                if fs.in_sammlung(b):
                    s = fs._schluessel(b)
                    cls.namen[s].add(fs.formelname(b))
                    cls.seiten[fs.formelname(b)].add(s)
                    cls.stellen[s].add(b.codestelle)

    def test_eine_formel_ein_name(self):
        """Gleich in welchem Fall, auf welcher Seite, mit welchem Wertesatz."""
        mehrere = {min(n): (sorted(n), sorted(self.stellen[s]))
                   for s, n in self.namen.items() if len(n) > 1}
        self.assertEqual(mehrere, {}, "Hier fehlt im Code ein name=.")

    def test_eine_seite_eine_groesse(self):
        """Die Fassungen einer Seite rechnen dasselbe Zeichen."""
        for name, schluessel in self.seiten.items():
            zeichen = {s[1] for s in schluessel if s[0] == "formel"}
            with self.subTest(name=name):
                self.assertLessEqual(len(zeichen), 1, zeichen)

    def test_keine_formel_heisst_wie_ein_thema(self):
        themen = {vergleichsname(t) for t in self.themen}
        self.assertEqual([n for n in self.seiten if vergleichsname(n) in themen], [])

    def test_keine_sammelnamen(self):
        sammel = {"ansatz", "bedingung", "das verfahren", "formel"}
        self.assertEqual([n for n in self.seiten if vergleichsname(n) in sammel], [])

    def test_keine_namen_aus_dem_projekt(self):
        """Keine Sorte, keine Lage: die Seite gilt fuer jedes Projekt."""
        sorten = set()
        for projekt in (Projekt.beispiel(), Projekt.jeder_nachweis()):
            sorten |= {m[k] for m in projekt.als_dict()["materialien"]
                       for k in ("sorte", "name")}
        verboten = [seitenname(s) for s in sorten]
        for name in self.seiten:
            with self.subTest(name=name):
                self.assertFalse(any(s in name for s in verboten))
                self.assertIsNone(re.search(r"\d+\. Lage", name))

    def test_themen_taugen_als_seitennamen(self):
        for thema in self.themen:
            self.assertEqual(seitenname(thema), thema)

    def test_jede_formel_kennt_ihre_codestelle(self):
        ohne = [s for s, stellen in self.stellen.items() if "" in stellen]
        self.assertEqual(ohne, [])
        self.assertFalse(any(st.startswith("opencivil.core.protokoll")
                             for stellen in self.stellen.values() for st in stellen))

    def test_symbolisch_heisst_wie_das_original(self):
        for lauf in fs.laeufe():
            for b in lauf.alle_bloecke():
                if fs.in_sammlung(b):
                    self.assertEqual(fs.formelname(fs._symbolisch(b)), fs.formelname(b))


if __name__ == "__main__":
    unittest.main()
