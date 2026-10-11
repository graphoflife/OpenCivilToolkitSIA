"""
Das Notizbuch: jede Formel auf einer Seite, die heisst, wie die Formel heisst.

Eine Seite ist dann verlaesslich, wenn ihr Name nur an der Formel haengt --
nicht am Fall, an der Sorte, an der Lage oder an der Reihenfolge. Sonst
waere die Theorie, die unter der Linie von Hand steht, beim naechsten Lauf
an der falschen Formel. Darum diese Pruefungen ueber die ganze Sammlung.
"""

import re
import tempfile
import unicodedata
import unittest
from collections import defaultdict
from dataclasses import replace
from pathlib import Path, PurePosixPath

from opencivil.bericht import formelsammlung as fs
from opencivil.core.berechnung import Eingaben, Formel
from opencivil.core.einheiten import MM, Groesse
from opencivil.core.latex import Formelzeile
from opencivil.core.protokoll import GleichungBlock, Protokoll, codestelle_aus
from opencivil.core.wert import WertDef
from opencivil.notizbuch.namen import (
    HOECHSTENS, NamensFehler, seitenname, sortierschluessel, vergleichsname,
)
from opencivil.notizbuch import tresor
from opencivil.notizbuch.tresor import LINIE, Seite, TresorFehler
from opencivil.projekt import Projekt
from opencivil.web import bruecke
from tests.test_schnappschuss import nur_katex_in

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
        self.assertEqual(fs.symbolisch(kopie.bloecke[0]).codestelle,
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
                    s = fs.schluessel(b)
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
                    self.assertEqual(fs.formelname(fs.symbolisch(b)), fs.formelname(b))



def _seite(name: str = "Probe", rumpf: str = "Formel", eigener_teil: bool = True) -> Seite:
    return Seite(pfad=f"Formeln/{name}.md", art="formel", rumpf=rumpf,
                 eigener_teil=eigener_teil)


class TestTresor(unittest.TestCase):
    """Was der Generator anfasst -- und was nie."""

    def setUp(self):
        self._ordner = tempfile.TemporaryDirectory()
        self.wurzel = Path(self._ordner.name)

    def tearDown(self):
        self._ordner.cleanup()

    def lauf(self, *seiten: Seite) -> tresor.Plan:
        plan = tresor.planen(seiten, self.wurzel)
        tresor.ausfuehren(plan, self.wurzel)
        return plan

    def datei(self, name: str = "Probe") -> Path:
        return self.wurzel / "Formeln" / f"{name}.md"

    def alles(self) -> dict:
        return {p: p.read_text(encoding="utf-8") for p in self.wurzel.rglob("*.md")}

    def test_zweimal_dasselbe(self):
        self.lauf(_seite())
        erst = self.alles()
        self.assertTrue(self.lauf(_seite()).nichts_zu_tun)
        self.assertEqual(self.alles(), erst)

    def test_die_pruefsumme_passt(self):
        self.lauf(_seite())
        datei = tresor.zerlegen(self.datei().read_text(encoding="utf-8"))
        self.assertTrue(datei.stimmt)
        self.assertEqual(datei.eigen, "")

    def test_der_eigene_teil_bleibt(self):
        self.lauf(_seite())
        theorie = "\n## Theorie\n\nVon Hand, mit $f_{cd}$.\n"
        self.datei().write_text(self.datei().read_text(encoding="utf-8") + theorie,
                                encoding="utf-8")
        self.lauf(_seite(rumpf="Neue Formel"))
        text = self.datei().read_text(encoding="utf-8")
        self.assertIn("Neue Formel", text)
        self.assertTrue(text.endswith(LINIE + "\n" + theorie))

    def test_oben_von_hand_geaendert_schreibt_nichts(self):
        self.lauf(_seite(), _seite("Andere"))
        self.datei().write_text(self.datei().read_text(encoding="utf-8").replace(
            "Formel", "Formel, von Hand"), encoding="utf-8")
        vorher = self.alles()
        plan = tresor.planen([_seite(rumpf="neu"), _seite("Andere", rumpf="neu")], self.wurzel)
        self.assertEqual(len(plan.fehler), 1)
        with self.assertRaises(TresorFehler):
            tresor.ausfuehren(plan, self.wurzel)
        self.assertEqual(self.alles(), vorher)

    def test_eine_notiz_von_hand_bleibt_unberuehrt(self):
        notiz = self.wurzel / "Notizen" / "Meine.md"
        notiz.parent.mkdir()
        notiz.write_text("# Meine\n\nText.\n", encoding="utf-8")
        self.lauf(_seite())
        self.assertEqual(notiz.read_text(encoding="utf-8"), "# Meine\n\nText.\n")

    def test_eine_notiz_mit_dem_namen_einer_seite_bricht_ab(self):
        notiz = self.wurzel / "Notizen" / "probe.md"
        notiz.parent.mkdir()
        notiz.write_text("Text.\n", encoding="utf-8")
        self.assertTrue(tresor.planen([_seite()], self.wurzel).fehler)

    def test_verwaist_ohne_theorie_faellt_weg(self):
        self.lauf(_seite(), _seite("Weg"))
        plan = self.lauf(_seite())
        self.assertEqual(plan.loeschen, ["Formeln/Weg.md"])
        self.assertFalse(self.datei("Weg").exists())

    def test_verwaist_mit_theorie_bleibt(self):
        self.lauf(_seite(), _seite("Weg"))
        weg = self.datei("Weg")
        weg.write_text(weg.read_text(encoding="utf-8") + "\nTheorie.\n", encoding="utf-8")
        plan = self.lauf(_seite())
        self.assertEqual(plan.verwaist, ["Formeln/Weg.md"])
        text = weg.read_text(encoding="utf-8")
        self.assertIn("[!warning] Verwaist", text)
        self.assertEqual(tresor.zerlegen(text).eigenschaften["verwaist"], "true")
        self.assertTrue(text.endswith("\nTheorie.\n"))
        self.assertTrue(self.lauf(_seite()).nichts_zu_tun)

    def test_ohne_eigenen_teil_keine_linie(self):
        self.lauf(_seite(eigener_teil=False))
        self.assertNotIn(LINIE, self.datei().read_text(encoding="utf-8"))

    def test_die_arbeitsdateien_von_obsidian_zaehlen_nicht(self):
        versteckt = self.wurzel / ".trash" / "Probe.md"
        versteckt.parent.mkdir()
        versteckt.write_text("Text.\n", encoding="utf-8")
        self.assertEqual(tresor.vorhandene(self.wurzel), {})


class TestFormelseiten(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seiten = {s.name: s for s in bruecke.notizbuch_seiten()}
        cls.namen = {e["name"] for e in bruecke.notizbuch_verzeichnis()["seiten"]}

    def test_jede_formel_hat_ihre_seite_mit_jeder_fassung(self):
        """Je Schluessel eine Fassung, gezeigt wie beim ersten Vorkommen."""
        gesehen = set()
        for lauf in fs.laeufe():
            for block in lauf.alle_bloecke():
                if fs.in_sammlung(block) and fs.schluessel(block) not in gesehen:
                    gesehen.add(fs.schluessel(block))
                    seite = self.seiten[fs.formelname(block)]
                    self.assertIn(fs.symbolisch(block).latex, seite.rumpf)

    def test_die_normstelle_steht_wie_im_code(self):
        for lauf in fs.laeufe():
            for block in lauf.alle_bloecke():
                if fs.in_sammlung(block) and block.referenz:
                    self.assertIn(block.referenz, self.seiten[fs.formelname(block)].rumpf)

    def test_jeder_link_fuehrt_zu_einer_seite(self):
        """Ausser in Code: ``Callable[[str], str]`` ist kein Link."""
        for name, seite in self.seiten.items():
            ohne_code = re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", seite.rumpf, flags=re.S))
            for ziel in re.findall(r"\[\[([^\]|#]+)", ohne_code):
                with self.subTest(seite=name, ziel=ziel):
                    self.assertIn(ziel, self.namen)

    def test_die_herkunft_ist_verlinkt(self):
        """f_cd braucht eta_fc: der Link steht in der Tabelle, und zurueck."""
        f_cd = self.seiten["Bemessungswert der Betondruckfestigkeit"].rumpf
        self.assertIn("[[Beiwert zur Berücksichtigung der Festigkeitsminderung]]", f_cd)
        eta = self.seiten["Beiwert zur Berücksichtigung der Festigkeitsminderung"].rumpf
        self.assertIn("## Gebraucht von\n\n- [[Bemessungswert der Betondruckfestigkeit]]",
                      eta)


class TestDasNotizbuchImRepo(unittest.TestCase):
    """Was fuer jede Seite gilt, erzeugt oder von Hand."""

    @classmethod
    def setUpClass(cls):
        cls.dateien = tresor.vorhandene(bruecke.NOTIZBUCH)

    def test_keine_verwaisten_seiten(self):
        verwaist = [p for p, text in self.dateien.items()
                    if tresor.zerlegen(text).eigenschaften.get("verwaist") == "true"]
        self.assertEqual(verwaist, [], "Theorie an die richtige Seite verschieben.")

    def test_jeder_name_einmal(self):
        namen = [vergleichsname(PurePosixPath(p).stem) for p in self.dateien]
        self.assertEqual(sorted(n for n in set(namen) if namen.count(n) > 1), [])

    def test_dateinamen_in_nfc(self):
        for pfad in self.dateien:
            self.assertEqual(unicodedata.normalize("NFC", pfad), pfad)

    def test_github_liefert_die_dateien_roh(self):
        """Ohne .nojekyll machte GitHub Pages aus jeder .md eine HTML-Seite."""
        self.assertTrue((bruecke.WURZEL / ".nojekyll").is_file())

    def test_nur_gewoehnliches_latex(self):
        """Obsidian setzt mit MathJax: kein Makro, das nur KaTeX kennt -- ausser als Code."""
        for pfad, text in self.dateien.items():
            ohne_code = re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", text, flags=re.S))
            with self.subTest(datei=pfad):
                self.assertEqual(nur_katex_in(ohne_code), set())

    def test_normstellen_nur_aus_dem_code(self):
        """Eine Normstelle in der Theorie muss eine sein, die der Code nennt."""
        bekannt = {b.referenz for lauf in fs.laeufe() for b in lauf.alle_bloecke()
                   if getattr(b, "referenz", "")}
        muster = re.compile(r"SIA 262(?::\d{4})?,? (?:Tabelle )?\d[\d.]*\d|"
                            r"SIA 262(?::\d{4})?,? Tabelle \d+")
        for pfad, text in self.dateien.items():
            eigen = tresor.zerlegen(text).eigen or ""
            for stelle in muster.findall(eigen):
                with self.subTest(datei=pfad, stelle=stelle):
                    self.assertIn(stelle, bekannt)



class TestHerleitungZeigtAufDieSeite(unittest.TestCase):
    """Der Link «Formel» an einer Gleichung der Herleitung fuehrt zu einer Seite."""

    def test_jede_formelseite_gibt_es(self):
        from opencivil.web.api import protokoll_liste

        def gehen(bloecke):
            for b in bloecke:
                if b.get("formelseite"):
                    yield b["formelseite"]
                yield from gehen(b.get("bloecke", []))

        aufbau = Projekt.beispiel().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.berichtsziele())
        gefunden = set(gehen(protokoll_liste(loesung.protokoll)))
        namen = {e["name"] for e in bruecke.notizbuch_verzeichnis()["seiten"]}
        self.assertGreater(len(gefunden), 30)
        self.assertEqual(gefunden - namen, set())



class TestBibliothek(unittest.TestCase):
    """Die Python-Seiten: aus den Docstrings, verlinkt, ohne offene Rolle."""

    @classmethod
    def setUpClass(cls):
        from opencivil.notizbuch.bibliothek import Bibliothek
        cls.bibliothek = Bibliothek.lesen()
        cls.seiten = {s.name: s.rumpf for s in cls.bibliothek.seiten({})}

    def test_jedes_modul_hat_seine_seite(self):
        for pfad in (bruecke.WURZEL / "opencivil").rglob("*.py"):
            if "__pycache__" in pfad.parts:
                continue
            teile = pfad.relative_to(bruecke.WURZEL).with_suffix("").parts
            name = ".".join(teile[:-1] if teile[-1] == "__init__" else teile)
            self.assertIn(name, self.seiten)

    def test_keine_rolle_bleibt_offen(self):
        self.assertEqual(self.bibliothek.offen, [],
                         "Im Docstring den Namen voll angeben: :class:`~opencivil.x.Y`.")

    def test_eingerueckt_unter_einer_ueberschrift_ist_code(self):
        seite = self.seiten["opencivil.nachweis.dehnungsfaecher"]
        self.assertIn("## VORZEICHEN\n\n```\nN > 0   Zug\n", seite)

    def test_schwanz_einer_ueberschrift_beginnt_den_absatz(self):
        seite = self.seiten["opencivil.nachweis.querkraft"]
        self.assertIn("## MIT BUEGELN\n\nFachwerkmodell, siehe "
                      "[[opencivil.nachweis.querkraft#buegelwiderstand|buegelwiderstand]]:\n\n```\n",
                      seite)

    def test_eingerueckt_nach_text_setzt_den_absatz_fort(self):
        seite = self.seiten["opencivil.core.rechenwerk"]
        self.assertIn("**Rueckwaerts** -- \"Ich will diesen Wert. Was ist dafuer noetig?\"\n"
                      "[[opencivil.core.rechenwerk#Rechenwerk.loese|Rechenwerk.loese]] verfolgt",
                      seite)

    def test_klammer_gehoert_zur_ueberschrift(self):
        self.assertIn("## VORZEICHEN (wie in der ganzen Querschnittsanalyse)",
                      self.seiten["opencivil.querschnitt.interaktion"])

    def test_nur_python_ist_python(self):
        """Formeln in einem Docstring sind kein Python, ein Aufruf schon."""
        querkraft = self.seiten["opencivil.nachweis.querkraft"]
        self.assertIn("## OHNE BUEGEL\n\n\n```\nV_Rd = k_d", querkraft)
        self.assertIn("```python\nwerk = Rechenwerk()", self.seiten["opencivil.core.rechenwerk"])

    def test_maskiert_was_markdown_anders_liest(self):
        from opencivil.notizbuch.bibliothek import _maskieren
        self.assertEqual(_maskieren("a|b $5 <i> 50%% x==y [[z]]", am_anfang=False),
                         "a\\|b \\$5 \\<i> 50\\%\\% x\\=\\=y \\[\\[z]]")
        self.assertEqual(_maskieren("# kein Titel", am_anfang=True), "\\# kein Titel")

    def test_formeln_stehen_bei_ihrem_modul(self):
        alle = {s.name: s.rumpf for s in bruecke.notizbuch_seiten()}
        self.assertIn("[[Bemessungswert der Betondruckfestigkeit]]",
                      alle["opencivil.material.beton"])
        self.assertIn("[[opencivil.querschnitt.platte#protokoll_statische_hoehe|"
                      "protokoll_statische_hoehe]]", alle["Statische Höhe"])


if __name__ == "__main__":
    unittest.main()
