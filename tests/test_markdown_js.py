"""
Der Markdown-Zerleger der Oberflaeche (``web/js/markdown.js``), geprueft mit node.

Die Seite zeigt das Notizbuch mit einem eigenen Zerleger, ohne fremde
Bibliothek. Ob er liest, was Obsidian liest, pruefen hier feste Faelle -- und
jede Seite des Notizbuchs: jede zerlegt sich, und jeder Link einer erzeugten
Seite fuehrt zu einer Seite und zu ihrem Abschnitt.

Das Modul wird node als ``data:``-Adresse gegeben -- ohne Kopie, ohne
Zwischendatei. Ohne node wird uebersprungen.
"""

import base64
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from opencivil.notizbuch import tresor

WURZEL = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")

#: Was node tut: jede Seite zerlegen, dazu die Anker ihrer Ueberschriften
#: und jeden Link -- mit dem Anker so, wie die Seite ihn vergleicht.
PROGRAMM = r"""
const m = await import('data:text/javascript;base64,%s');
let eingabe = '';
for await (const stueck of process.stdin) eingabe += stueck;
const heraus = {};
const links = [];
const anker = [];
const sammeln = (knoten) => {
  if (Array.isArray(knoten)) return knoten.forEach(sammeln);
  if (!knoten || typeof knoten !== 'object') return;
  if (knoten.art === 'wiki') links.push({ziel: knoten.ziel, anker: knoten.anker ? m.anker(knoten.anker) : null});
  if (knoten.art === 'ueberschrift') anker.push(knoten.anker);
  if (knoten.art === 'text' && (knoten.text.includes('[[') || knoten.text.includes('$$'))) links.push({roh: knoten.text});
  Object.values(knoten).forEach(sammeln);
};
for (const [name, text] of Object.entries(JSON.parse(eingabe))) {
  try {
    const baum = m.zerlegen(text);
    links.length = 0;
    anker.length = 0;
    sammeln(baum.bloecke);
    heraus[name] = {baum, links: [...links], anker: [...anker]};
  } catch (fehler) {
    heraus[name] = {fehler: String(fehler.stack || fehler)};
  }
}
process.stdout.write(JSON.stringify(heraus));
"""


def zerlegt(texte: dict) -> dict:
    """Je Name: ``{baum, links, anker}`` -- oder ``{fehler}``."""
    modul = base64.b64encode((WURZEL / "web" / "js" / "markdown.js").read_bytes()).decode()
    lauf = subprocess.run(
        [NODE, "--input-type=module", "-e", PROGRAMM % modul],
        input=json.dumps(texte), capture_output=True, text=True, timeout=120)
    if lauf.returncode:
        raise AssertionError(lauf.stderr)
    return json.loads(lauf.stdout)


def T(text):
    return {"art": "text", "text": text}


def absatz(*inhalt):
    return {"art": "absatz", "inhalt": list(inhalt)}


def wiki(ziel, anker=None, text=None, einbetten=False):
    return {"art": "wiki", "einbetten": einbetten, "ziel": ziel, "anker": anker, "text": text}


def punkt(*bloecke, aufgabe=None):
    return {"aufgabe": aufgabe, "bloecke": list(bloecke)}


def liste(*punkte, geordnet=False, start=1):
    return {"art": "liste", "geordnet": geordnet, "start": start, "punkte": list(punkte)}


#: Eingabe und die Bloecke, die herauskommen muessen.
FAELLE = {
    "einfacher umbruch ist ein leerzeichen": ("Ein\nZwei", [absatz(T("Ein Zwei"))]),
    "harter umbruch": ("Ein  \nZwei", [absatz(T("Ein"), {"art": "umbruch"}, T("Zwei"))]),
    "ueberschrift mit anker": (
        "## Grössen und Masse",
        [{"art": "ueberschrift", "stufe": 2, "inhalt": [T("Grössen und Masse")],
          "anker": "grössen-und-masse"}]),
    "doppelte anker zaehlen weiter": (
        "# A\n\n# A",
        [{"art": "ueberschrift", "stufe": 1, "inhalt": [T("A")], "anker": "a"},
         {"art": "ueberschrift", "stufe": 1, "inhalt": [T("A")], "anker": "a-2"}]),
    "auszeichnung": (
        "**fett** und *kursiv* und `co*de` und ~~weg~~ und ==hier==",
        [absatz({"art": "fett", "inhalt": [T("fett")]}, T(" und "),
                {"art": "kursiv", "inhalt": [T("kursiv")]}, T(" und "),
                {"art": "code", "text": "co*de"}, T(" und "),
                {"art": "durch", "inhalt": [T("weg")]}, T(" und "),
                {"art": "markiert", "inhalt": [T("hier")]})]),
    "maskiert": ("f\\_cd kostet \\$5 \\*", [absatz(T("f_cd kostet $5 *"))]),
    "unterstrich im wort": ("f_cd und M_Ed", [absatz(T("f_cd und M_Ed"))]),
    "formel in der zeile": (
        "Mit $f_{cd}$ und 5$ und $a$5",
        [absatz(T("Mit "), {"art": "mathe", "latex": "f_{cd}"}, T(" und 5$ und $a$5"))]),
    "formel abgesetzt": ("$$\nf = 1\n$$", [{"art": "mathe", "latex": "f = 1"}]),
    "formel abgesetzt auf einer zeile": ("$$f = 1$$", [{"art": "mathe", "latex": "f = 1"}]),
    "wikilinks": (
        "[[Statische Höhe]] und [[Seite#Abschnitt|Text]]",
        [absatz(wiki("Statische Höhe"), T(" und "), wiki("Seite", "Abschnitt", "Text"))]),
    "eingebettete notiz": ("![[Seite]]", [absatz(wiki("Seite", einbetten=True))]),
    "link und bild": (
        "[Repo](https://x.y/a_b) ![Bild|200](Anhänge/a.png)",
        [absatz({"art": "link", "ziel": "https://x.y/a_b", "inhalt": [T("Repo")]}, T(" "),
                {"art": "bild", "ziel": "Anhänge/a.png", "alt": "Bild", "breite": 200})]),
    "adresse ohne klammern": (
        "Siehe https://graphoflife.github.io/x.",
        [absatz(T("Siehe "), {"art": "link", "ziel": "https://graphoflife.github.io/x",
                              "inhalt": [T("https://graphoflife.github.io/x")]}, T("."))]),
    "tabelle": (
        "| A | B |\n| --- | ---: |\n| $x$ | [[S\\|T]] |",
        [{"art": "tabelle", "ausrichtung": ["", "rechts"], "kopf": [[T("A")], [T("B")]],
          "zeilen": [[[{"art": "mathe", "latex": "x"}], [wiki("S", text="T")]]]}]),
    "callout": (
        "> [!info] Normstelle\n> SIA 262:2025, 2.4.2.3",
        [{"art": "callout", "typ": "info", "falten": "", "titel": [T("Normstelle")],
          "bloecke": [absatz(T("SIA 262:2025, 2.4.2.3"))]}]),
    "callout mit formel": (
        "> [!warning]-\n> $$\n> a\n> $$",
        [{"art": "callout", "typ": "warning", "falten": "-", "titel": [],
          "bloecke": [{"art": "mathe", "latex": "a"}]}]),
    "zitat": ("> Zitat", [{"art": "zitat", "bloecke": [absatz(T("Zitat"))]}]),
    "aufgaben": (
        "- [ ] offen\n- [x] erledigt",
        [liste(punkt(absatz(T("offen")), aufgabe=False),
               punkt(absatz(T("erledigt")), aufgabe=True))]),
    "nummeriert mit codeblock": (
        "1. Eins\n   ```\n   code\n   ```\n2. Zwei",
        [liste(punkt(absatz(T("Eins")), {"art": "code", "sprache": "", "text": "code"}),
               punkt(absatz(T("Zwei"))), geordnet=True)]),
    "verschachtelt": (
        "- a\n  - b", [liste(punkt(absatz(T("a")), liste(punkt(absatz(T("b"))))))]),
    "verschachtelt mit tabulator": (
        "- a\n\t- b", [liste(punkt(absatz(T("a")), liste(punkt(absatz(T("b"))))))]),
    "haengender einzug": (
        "- [ ] **A** b\n      c",
        [liste(punkt(absatz({"art": "fett", "inhalt": [T("A")]}, T(" b c")), aufgabe=False))]),
    "kopf": (
        '---\nerzeugt: abc\nart: formel\ntags: [formel]\nnormstelle: "SIA 262:2025, 4.4.2"\n'
        "liste:\n  - a\n  - b\n---\nText",
        {"kopf": {"erzeugt": "abc", "art": "formel", "tags": ["formel"],
                  "normstelle": "SIA 262:2025, 4.4.2", "liste": ["a", "b"]},
         "bloecke": [absatz(T("Text"))]}),
    "kommentare": (
        "Vor <!-- weg --> nach\n\n<!-- Ab hier von Hand -->\n%% auch weg %%\n\n%%\nmehr\n%%\nText",
        [absatz(T("Vor  nach")), absatz(T("Text"))]),
    "html bleibt text": ("<b>fett</b>", [absatz(T("<b>fett</b>"))]),
    "codeblock mit sprache": (
        "```python\nx = 1\n\ny = 2\n```",
        [{"art": "code", "sprache": "python", "text": "x = 1\n\ny = 2"}]),
    "eingerueckter code": (
        "Text\n\n    eingerückt\n      mehr",
        [absatz(T("Text")), {"art": "code", "sprache": "", "text": "eingerückt\n  mehr"}]),
    "linie": ("a\n\n---\n\nb", [absatz(T("a")), {"art": "linie"}, absatz(T("b"))]),
    "2. lage im absatz bleibt text": (
        "Gemessen an der\n2. Lage von oben", [absatz(T("Gemessen an der 2. Lage von oben"))]),
}


@unittest.skipIf(NODE is None, "node fehlt -- der Zerleger der Oberflaeche bleibt ungeprueft")
class TestFaelle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ergebnis = zerlegt({name: text for name, (text, _) in FAELLE.items()})

    def test_jeder_fall(self):
        for name, (_, erwartet) in FAELLE.items():
            with self.subTest(fall=name):
                baum = self.ergebnis[name].get("baum")
                self.assertIsNotNone(baum, self.ergebnis[name].get("fehler"))
                if isinstance(erwartet, dict):
                    self.assertEqual(baum, erwartet)
                else:
                    self.assertEqual(baum["bloecke"], erwartet)


@unittest.skipIf(NODE is None, "node fehlt -- der Zerleger der Oberflaeche bleibt ungeprueft")
class TestDasGanzeNotizbuch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seiten = tresor.vorhandene(WURZEL / "notizbuch")
        texte = dict(cls.seiten)
        texte["../README.md"] = (WURZEL / "README.md").read_text(encoding="utf-8")
        for bericht in sorted((WURZEL / "tests" / "schnappschuss").glob("*.md")):
            texte[f"../tests/schnappschuss/{bericht.name}"] = bericht.read_text(encoding="utf-8")
        cls.ergebnis = zerlegt(texte)
        cls.namen = {Path(p).stem: p for p in cls.seiten}

    def test_jede_seite_zerlegt_sich(self):
        for name, ergebnis in self.ergebnis.items():
            with self.subTest(datei=name):
                self.assertNotIn("fehler", ergebnis, ergebnis.get("fehler"))

    def test_erzeugte_seiten_lassen_nichts_roh_stehen(self):
        """Kein ``[[`` und kein ``$$`` bleibt Text -- sonst haette der Zerleger etwas verfehlt."""
        for pfad, text in self.seiten.items():
            if tresor.zerlegen(text).erzeugt is None:
                continue
            with self.subTest(datei=pfad):
                self.assertEqual([l for l in self.ergebnis[pfad]["links"] if "roh" in l], [])

    def test_jeder_link_einer_erzeugten_seite_fuehrt_hin(self):
        for pfad, text in self.seiten.items():
            if tresor.zerlegen(text).erzeugt is None:
                continue
            for link in self.ergebnis[pfad]["links"]:
                if "roh" in link:
                    continue
                with self.subTest(datei=pfad, ziel=link["ziel"], anker=link["anker"]):
                    self.assertIn(link["ziel"], self.namen)
                    if link["anker"]:
                        self.assertIn(link["anker"],
                                      self.ergebnis[self.namen[link["ziel"]]]["anker"])


if __name__ == "__main__":
    unittest.main()
