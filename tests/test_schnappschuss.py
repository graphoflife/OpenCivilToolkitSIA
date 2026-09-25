"""
Der ganze Bericht gegen eine abgelegte Fassung.

Die übrigen Tests prüfen je eine Zusage: dass diese Zahl stimmt, dass jene
Zeile dasteht. Was sie nicht zeigen, ist die *Summe* — ändert ein Umbau
irgendwo eine Zahl, meldet sich nur, was zufällig ein Einzeltest abdeckt. Das
ist in diesem Werkzeug mehrfach passiert: eine Lagenrichtung verschob sich,
und die statische Höhe wanderte von 261 auf 249 mm, ohne dass eine einzige
Prüfung darauf zeigte.

Hier steht darum der vollständige Bericht als Datei daneben -- für das
Beispielprojekt und für ein zweites, das jeden Nachweis einmal laut führt.
Das Beispiel allein zeigte weder Duktilität noch Bügel, Knicken, Fliessen
oder erhöhte Anforderung; ein Umbau dort wäre blind geblieben. Ändert sich
irgendetwas, wird dieser Test rot und legt die Ist-Fassung neben die
Soll-Fassung. War die Änderung gewollt, übernimmt man sie mit einem Befehl und
sieht im git-Diff **genau**, was sich bewegt hat.

    python3 -m tests.test_schnappschuss --uebernehmen

Der Schnappschuss ist kein Ersatz für die Einzeltests: er sagt, *dass* sich
etwas geändert hat, nicht ob es richtig ist. Aber er lässt nichts durch.
"""

import functools
import re
import sys
import unittest
from pathlib import Path

ORDNER = Path(__file__).parent / "schnappschuss"
WURZEL = Path(__file__).resolve().parents[1]

#: Feste Breite für den Konsolenbericht.
#:
#: `konsole._BREITE` liest beim Import die Terminalbreite -- unter einem
#: schmalen Fenster oder in einer Pipe bricht der Fliesstext anders um, und
#: ein Bytevergleich verglichen dann die Fenstergrösse statt der Rechnung.
BREITE = 100


def _voll():
    """
    Jeder Nachweis einmal laut -- und die Fälle, die das Beispiel nie zeigt.

    Erhöhte Anforderung mit allen Schaltern und begrenzter rissaktiver
    Dicke, häufige und quasi-ständige Lastfälle abgeleitet und eigene, Bügel
    mit Stabzahl in y, ein Knickfall; eine zweite Platte mit x aussen, die im
    Feld nicht aufgeht und deren Stahl unter Dauerlast fliesst, dazu
    Querkraft ohne Bügel -- einmal über m_Rd, einmal darunter, mit Einlage;
    eine dritte ohne x-Bewehrung; eine vierte mit Querkraft ohne Einlage,
    einer Einwirkung, die am kürzesten Abstand gemessen wird, und ⌀40 in y
    unter der x-Bewehrung -- die fliesst bei x = h/2 nicht.
    Gebaut über die Fassade, wie ein Benutzer es in Python täte.
    """
    from opencivil.projekt import Projekt

    p = Projekt("Jeder Nachweis einmal")
    p.beton("C30/37")
    p.stahl("B500B")
    decke = p.platte("Decke", h=300, x=[18, 12], x_zulage=[12, 0], y=[12, 12],
                     rissanforderung="erhoeht", duktilitaet=True, sproede=True,
                     zwaengung=True, zwaengung_begrenzt=True,
                     zwaengung_biegung=True)
    decke.querkraftbewehrung.durchmesser = 8.0
    decke.querkraftbewehrung.abstand_y = None
    decke.querkraftbewehrung.anzahl_y = 5.0
    decke.einwirkung("Feld", M_Ed=150, V_Ed=80)
    decke.einwirkung("Feld mit Druck", M_Ed=120, N_Ed=-300)
    decke.einwirkung("Stütze", M_Ed=-60, V_Ed=60)
    decke.haeufig.aus_tragsicherheit = True
    decke.haeufig.lastfall("Gebrauch", M_Ed=90)
    decke.quasistaendig.aus_tragsicherheit = True
    decke.quasistaendig.lastfall("Dauerlast", M_Ed=70)
    decke.knickfall("Wand", N_Ed=-800, M_Ed_1=20, laenge=3.0)

    dach = p.platte("Dach", h=200, x=[10, 10], y=[8, 8], x_innen=False,
                    einlagenhoehe=40)
    dach.einwirkung("Feld", M_Ed=80, V_Ed=40)
    dach.einwirkung("Rand", M_Ed=20, V_Ed=30)
    dach.quasistaendig.lastfall("Dauerlast", M_Ed=40)

    ohne = p.platte("Ohne x", h=250, x=[0, 0], y=[12, 12])
    ohne.einwirkung("Feld", M_Ed=30, V_Ed=20)

    konsole = p.platte("Konsole", h=250, x=[12, 12], y=[40, 10])
    konsole.einwirkung("Feld", M_Ed=40, V_Ed=50)
    konsole.einwirkung("Schräg", M_Ed=30, N_Ed=-500).art = "naechster_Punkt"
    return p


def projekte() -> dict:
    """Name auf Projekt -- die Projekte, deren Bericht festgehalten wird."""
    from opencivil.projekt import Projekt

    return {"beispiel": Projekt.beispiel(), "voll": _voll()}


def _loesung(projekt):
    aufbau = projekt.aufbauen()
    return aufbau, aufbau.werk.loese(*aufbau.alle_nachweisziele())


@functools.lru_cache(maxsize=None)
def _gerechnet() -> dict:
    """Name auf (Aufbau, Lösung) -- einmal je Lauf, die Tests teilen es."""
    return {name: _loesung(projekt) for name, projekt in projekte().items()}


@functools.lru_cache(maxsize=None)
def berichte() -> dict:
    """Name der Datei auf ihren Inhalt -- die eine Stelle, die das erzeugt."""
    from opencivil.bericht import konsole
    from opencivil.bericht.latex_dokument import als_tex
    from opencivil.bericht.markdown import als_markdown

    vorher, konsole._BREITE = konsole._BREITE, BREITE
    try:
        dateien = {}
        for name, (aufbau, loesung) in _gerechnet().items():
            titel = name.capitalize()
            dateien[f"{name}.txt"] = konsole.als_text(loesung, titel=titel,
                                                      aufbau=aufbau)
            dateien[f"{name}.tex"] = als_tex(loesung, titel=titel, aufbau=aufbau)
            dateien[f"{name}.md"] = als_markdown(loesung, titel=titel, aufbau=aufbau)
        return dateien
    finally:
        konsole._BREITE = vorher


def uebernehmen() -> None:
    """Die Ist-Fassung zur neuen Soll-Fassung machen."""
    ORDNER.mkdir(exist_ok=True)
    for name, inhalt in berichte().items():
        (ORDNER / name).write_text(inhalt, encoding="utf-8")
        print(f"geschrieben: {ORDNER / name}")
    # Die Ist-Fassungen sind damit Soll geworden; liegen blieben sie nur als
    # veralteter Vergleich.
    for ist in ORDNER.glob("*.ist"):
        ist.unlink()


class TestSchnappschuss(unittest.TestCase):
    def test_die_projekte_zeigen_jeden_nachweis(self):
        """
        Der Schnappschuss prüft nur, was in seinen Projekten vorkommt. Zusammen
        müssen sie darum jeden Nachweis einmal **laut** führen -- kommt ein
        neuer dazu, schlägt dieser Test an, bis ein Projekt ihn zeigt.
        """
        from opencivil.projekt import Aufbau

        gezeigt = set()
        for aufbau, _ in _gerechnet().values():
            for feld, eintraege in aufbau.nachweise_je_feld():
                if any(not u.still for n in eintraege.values() for u in n.urteile):
                    gezeigt.add(feld)
        self.assertEqual(set(Aufbau.NACHWEISFELDER) - gezeigt, set())

    def test_nur_gewoehnliches_latex(self):
        """
        Markdown und LaTeX-Dokument gehen an Leser, die nicht KaTeX sind:
        GitHub, Pandoc, pdflatex. Ein Makro, das nur die Oberflaeche kennt,
        stuende dort als Fehler. Welche das sind, sagt die Einstellung von
        KaTeX selbst -- dazu die, die erst ``trust`` freischaltet.
        """
        einstellung = (WURZEL / "web" / "js" / "mathe.js").read_text(encoding="utf-8")
        nur_katex = re.findall(r"'\\\\([a-zA-Z]+)':", einstellung)
        self.assertIn("diameter", nur_katex, "die Einstellung liess sich nicht lesen")
        nur_katex += ["htmlClass", "htmlId", "htmlStyle", "htmlData", "href", "url",
                      "includegraphics"]
        for name, inhalt in berichte().items():
            if name.endswith(".txt"):
                continue
            with self.subTest(datei=name):
                gefunden = set(re.findall(r"\\([a-zA-Z]+)", inhalt)) & set(nur_katex)
                self.assertEqual(gefunden, set())

    def test_der_bericht_ist_unveraendert(self):
        for name, ist in berichte().items():
            soll_datei = ORDNER / name
            with self.subTest(datei=name):
                self.assertTrue(
                    soll_datei.exists(),
                    f"{soll_datei} fehlt. Einmalig anlegen mit "
                    f"`python3 -m tests.test_schnappschuss --uebernehmen`.")
                soll = soll_datei.read_text(encoding="utf-8")
                if ist == soll:
                    continue
                # Die Ist-Fassung danebenlegen, damit man sie ansehen kann --
                # eine Meldung mit 2000 Zeilen Unterschied hilft niemandem.
                ist_datei = soll_datei.with_suffix(soll_datei.suffix + ".ist")
                ist_datei.write_text(ist, encoding="utf-8")
                self.fail(
                    f"Der Bericht hat sich geändert.\n"
                    f"  Soll: {soll_datei}\n"
                    f"  Ist:  {ist_datei}\n"
                    f"Ansehen mit `diff {soll_datei} {ist_datei}`.\n"
                    f"War die Änderung gewollt: "
                    f"`python3 -m tests.test_schnappschuss --uebernehmen`, "
                    f"dann im git-Diff prüfen, was sich bewegt hat.")


if __name__ == "__main__":
    if "--uebernehmen" in sys.argv:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        uebernehmen()
    else:
        unittest.main()
