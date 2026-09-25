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


def _voll():
    """
    Jeder Nachweis einmal laut -- und die Fälle, die das Beispiel nie zeigt.

    Erhöhte Anforderung mit allen Schaltern, häufige und quasi-ständige
    Lastfälle abgeleitet und eigene, Bügel, ein Knickfall; eine zweite Platte
    mit x aussen, die im Feld nicht aufgeht und deren Stahl unter Dauerlast
    fliesst; eine dritte ohne x-Bewehrung. Gebaut über die Fassade, wie ein
    Benutzer es in Python täte.
    """
    from opencivil.projekt import Projekt

    p = Projekt("Jeder Nachweis einmal")
    p.beton("C30/37")
    p.stahl("B500B")
    decke = p.platte("Decke", h=300, x=[18, 12], x_zulage=[12, 0], y=[12, 12],
                     rissanforderung="erhoeht", duktilitaet=True, sproede=True,
                     zwaengung=True, zwaengung_biegung=True)
    decke.querkraftbewehrung.durchmesser = 8.0
    decke.einwirkung("Feld", M_Ed=150, V_Ed=80)
    decke.einwirkung("Feld mit Druck", M_Ed=120, N_Ed=-300)
    decke.einwirkung("Stütze", M_Ed=-60, V_Ed=60)
    decke.haeufig.aus_tragsicherheit = True
    decke.haeufig.lastfall("Gebrauch", M_Ed=90)
    decke.quasistaendig.aus_tragsicherheit = True
    decke.quasistaendig.lastfall("Dauerlast", M_Ed=70)
    decke.knickfall("Wand", N_Ed=-800, M_Ed_1=20, laenge=3.0)

    dach = p.platte("Dach", h=200, x=[10, 10], y=[8, 8], x_innen=False)
    dach.einwirkung("Feld", M_Ed=80)
    dach.quasistaendig.lastfall("Dauerlast", M_Ed=40)

    ohne = p.platte("Ohne x", h=250, x=[0, 0], y=[12, 12])
    ohne.einwirkung("Feld", M_Ed=30, V_Ed=20)
    return p


def projekte() -> dict:
    """Name auf Projekt -- die Projekte, deren Bericht festgehalten wird."""
    from opencivil.projekt import Projekt

    return {"beispiel": Projekt.beispiel(), "voll": _voll()}


def _loesung(projekt):
    aufbau = projekt.aufbauen()
    return aufbau, aufbau.werk.loese(*aufbau.alle_nachweisziele())


def berichte() -> dict:
    """Name der Datei auf ihren Inhalt -- die eine Stelle, die das erzeugt."""
    from opencivil.bericht import konsole
    from opencivil.bericht.latex_dokument import als_tex

    vorher, konsole._BREITE = konsole._BREITE, BREITE
    try:
        dateien = {}
        for name, projekt in projekte().items():
            titel = name.capitalize()
            aufbau, loesung = _loesung(projekt)
            dateien[f"{name}.txt"] = konsole.als_text(loesung, titel=titel,
                                                      aufbau=aufbau)
            dateien[f"{name}.tex"] = als_tex(loesung, titel=titel, aufbau=aufbau)
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
        for projekt in projekte().values():
            aufbau, _ = _loesung(projekt)
            for feld, eintraege in aufbau.nachweise_je_feld():
                if any(not u.still for n in eintraege.values() for u in n.urteile):
                    gezeigt.add(feld)
        self.assertEqual(set(Aufbau.NACHWEISFELDER) - gezeigt, set())

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
