"""
Der ganze Bericht gegen eine abgelegte Fassung.

Die übrigen Tests prüfen je eine Zusage: dass diese Zahl stimmt, dass jene
Zeile dasteht. Was sie nicht zeigen, ist die *Summe* — ändert ein Umbau
irgendwo eine Zahl, meldet sich nur, was zufällig ein Einzeltest abdeckt. Das
ist in diesem Werkzeug mehrfach passiert: eine Lagenrichtung verschob sich,
und die statische Höhe wanderte von 261 auf 249 mm, ohne dass eine einzige
Prüfung darauf zeigte.

Hier steht darum der vollständige Bericht des Beispielprojekts als Datei
daneben. Ändert sich irgendetwas daran, wird dieser Test rot und legt die
Ist-Fassung neben die Soll-Fassung. War die Änderung gewollt, übernimmt man
sie mit einem Befehl und sieht im git-Diff **genau**, was sich bewegt hat.

    python3 -m tests.test_schnappschuss --uebernehmen

Der Schnappschuss ist kein Ersatz für die Einzeltests: er sagt, *dass* sich
etwas geändert hat, nicht ob es richtig ist. Aber er lässt nichts durch.
"""

import os
import sys
import unittest
from pathlib import Path

ORDNER = Path(__file__).parent / "schnappschuss"

#: Feste Breite für den Konsolenbericht.
#:
#: `konsole._BREITE` liest beim Import die Terminalbreite -- unter einem
#: schmalen Fenster oder in einer Pipe bricht der Fliesstext anders um, und
#: ein Bytevergleich verglichen dann die Fenstergrösse statt der Rechnung.
BREITE = 100


def _loesung():
    """Das Beispielprojekt, vollständig gerechnet."""
    from opencivil.projekt import Projekt

    aufbau = Projekt.beispiel().aufbauen()
    return aufbau.werk.loese(*aufbau.alle_nachweisziele())


def berichte() -> dict:
    """Name der Datei auf ihren Inhalt -- die eine Stelle, die das erzeugt."""
    from opencivil.bericht import konsole
    from opencivil.bericht.latex_dokument import als_tex

    vorher, konsole._BREITE = konsole._BREITE, BREITE
    try:
        loesung = _loesung()
        return {
            "beispiel.txt": konsole.als_text(loesung, titel="Beispiel"),
            "beispiel.tex": als_tex(loesung, titel="Beispiel"),
        }
    finally:
        konsole._BREITE = vorher


def uebernehmen() -> None:
    """Die Ist-Fassung zur neuen Soll-Fassung machen."""
    ORDNER.mkdir(exist_ok=True)
    for name, inhalt in berichte().items():
        (ORDNER / name).write_text(inhalt, encoding="utf-8")
        print(f"geschrieben: {ORDNER / name}")


class TestSchnappschuss(unittest.TestCase):
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
