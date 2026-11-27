"""
opencivil/fachwerkmodell/werk.py -- das Fachwerkmodell im Rechenwerk.

VERANTWORTUNG:
Was ein Fachwerkmodell im Rechenwerk anmeldet: eine Prozedur, die sein
Modell prüft (:mod:`~opencivil.fachwerkmodell.pruefen`) und die Herleitung
schreibt (:mod:`~opencivil.fachwerkmodell.herleitung`). Es liest nichts von
aussen -- kein Material, keine Dicke (Plan vom 2026-11-27, Entscheid 11).

DAS ERGEBNIS:
kommt als Befund in die Lösung (:class:`Fachwerkbefund`); Zeichnung und
Zusammenfassung lesen es dort. Ein Modell, dem etwas fehlt, ist ein Befund
mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from opencivil.core.berechnung import Ausfuehrung, Eingaben, Prozedur
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.wert import WertDef
from opencivil.fachwerkmodell import herleitung
from opencivil.fachwerkmodell.modell import Modell
from opencivil.fachwerkmodell.pruefen import pruefen
from opencivil.stabwerk.system import Meldung

#: Unter welchem Thema seine Herleitung in der Formelsammlung steht.
THEMA = "Fachwerkmodell"

#: Solange kein Verfahren das Fachwerk sucht -- ein Hinweis, wenn sonst nichts fehlt.
OHNE_VERFAHREN = ("Noch ohne Verfahren: geprüft sind Scheibe, Lager und Lasten, ein Fachwerk "
                  "sucht das Werkzeug noch nicht.")


@dataclass
class Fachwerkbefund:
    """Was die Rechnung fand: das Modell und die Meldungen -- die der Beschreibung zuerst."""

    modell: Modell
    meldungen: List[Meldung]

    @property
    def haelt_an(self) -> bool:
        """Ob eine Meldung die Suche nach einem Fachwerk aufhält."""
        return any(m.haelt_an for m in self.meldungen)


class FachwerkProzedur(Prozedur):
    """Das ganze Fachwerkmodell, geprüft und aufgeschrieben."""

    def __init__(self, system: "Fachwerksystem", **kwargs) -> None:
        super().__init__(**kwargs)
        self.system = system

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        return self.system.rechnen_und_schreiben(p)


class Fachwerksystem(Rechenobjekt):
    """Ein Fachwerkmodell, fertig für das Rechenwerk."""

    WAS = "Fachwerkmodell"

    def __init__(self, *, name: str, kennung: str, praefix: str, modell: Modell,
                 meldungen: Sequence[Meldung]) -> None:
        """``meldungen`` sind die der Beschreibung: ein Verweis ins Leere, eine doppelte Kennung."""
        self.name = name
        self.kennung = kennung
        self.id = praefix
        self.modell = modell
        self.meldungen = list(meldungen)
        self.definitionen: Dict[str, WertDef] = {}
        self.rechnung = FachwerkProzedur(
            self, id=f"{self.id}.rechnung", ausgaben=[], bezuege=[], titel="Fachwerkmodell",
            abschnitt=self.abschnitt())
        """Die Prozedur, die das Modell rechnet -- ihr Befund ist der :class:`Fachwerkbefund`."""
        self.berechnungen = [self.rechnung]

    def abschnitt(self) -> Abschnitt:
        return Abschnitt(f"Fachwerkmodell: {self.name}", self.id, thema=THEMA)

    def ziele(self) -> List[str]:
        """Was ein Lauf rechnen muss: das Modell."""
        return [self.rechnung.id]

    def rechnen_und_schreiben(self, p: Protokoll) -> Ausfuehrung:
        """Das Modell geprüft, die Herleitung geschrieben."""
        meldungen = self.meldungen + pruefen(self.modell)
        if not any(m.haelt_an for m in meldungen):
            meldungen.append(Meldung(OHNE_VERFAHREN, fehler=False))
        befund = Fachwerkbefund(self.modell, meldungen)
        herleitung.schreiben(p, befund)
        return Ausfuehrung({}, befund=befund)
