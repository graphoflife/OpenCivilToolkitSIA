"""
opencivil/fachwerkmodell/form.py -- das Verfahren SIMP: die steifste Form, und aus ihr ein Fachwerk.

VERANTWORTUNG:
Die Suche des Verfahrens SIMP, Schritt um Schritt, wie die der Ground
Structure Runde um Runde (:func:`schritte`): das Material verteilt sich
zur steifsten Form (:mod:`~opencivil.fachwerkmodell.simp`). Ist sie
fertig, oder hält jemand an, liest das Werkzeug aus ihr ein Fachwerk
(:mod:`~opencivil.fachwerkmodell.skelett`), und die Optimierung der
Ground Structure bestimmt seine Kräfte
(:func:`~opencivil.fachwerkmodell.suche.optimum`, danach ohne die dünnen
Stäbe, :func:`~opencivil.fachwerkmodell.suche.nachbearbeiten`).

FERTIG:
wenn sich in einem Schritt keine Dichte um mehr als :data:`GENUG` ändert
-- so hört auch die Quelle auf --, spätestens nach
:data:`HOECHSTENS_SCHRITTE` Schritten (nach Vorgabe, nicht nachgeschlagen).

DER ZUSTAND:
Zwischen zwei Anfragen die Dichten, zu welchem Modell und nach welchem
Schritt (:class:`Formzustand`); die Seite hält ihn wie den der Ground
Structure. Eine Anfrage rechnet Schritte, bis :data:`SEKUNDEN` um sind:
so zeigt die Seite die Form wachsen, gleich wie schnell sie rechnet. Was
herauskommt, hängt nicht daran -- jeder Schritt folgt nur aus den Dichten
davor. Das Netz bleibt hier im Speicher (:func:`_netz`).

DAS BILD DER FORM:
Je Feld des Rechtecks um die Scheiben ein Zeichen, Zeile um Zeile von
unten: «-», wo kein Element ist, sonst die gefilterte Dichte in
Fünfzehnteln, «0» bis «f» (:func:`formtext`). So steht sie kurz im
Projekt, und die Seite zeichnet sie.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import ClassVar, Optional, Sequence, Tuple

from opencivil.fachwerkmodell import simp, skelett
from opencivil.fachwerkmodell.modell import Modell
from opencivil.fachwerkmodell.simp import Netz, gefiltert
from opencivil.fachwerkmodell.suche import Suchergebnis, abdruck, nachbearbeiten, optimum
from opencivil.fachwerkmodell.verfahren import Verfahren

#: Wo das Verfahren nachzulesen ist und wo das Lesen der Form.
QUELLE = simp.QUELLE
QUELLE_SKELETT = skelett.QUELLE

#: Fertig, wenn sich keine Dichte in einem Schritt um mehr als so viel ändert.
GENUG = 0.01

#: Wie viele Schritte höchstens -- nach Vorgabe, nicht nachgeschlagen.
HOECHSTENS_SCHRITTE = 200

#: Wie lange eine Anfrage rechnet, in s -- nach Vorgabe.
SEKUNDEN = 1.0

#: Die Zeichen der Dichte im Bild der Form: «0» leer bis «f» voll.
STUFEN = "0123456789abcdef"


@dataclass(frozen=True)
class Formeinstellung:
    """Das Verfahren SIMP: seine vier Zahlen in SI."""

    verfahren: ClassVar[Verfahren] = Verfahren.SIMP
    zug_achsparallel: ClassVar[bool] = False
    """Den Schalter hat nur die Ground Structure: die Form kennt keine Richtung des Zugs."""

    weite: float
    """Die Netzweite h in m."""

    volumen: float
    """Der Anteil des Materials an der Fläche: 0.3 ist 30 %."""

    w_Z: float
    """Das Gewicht des Zugs im Fachwerk; Druck zählt 1."""

    N_min: float
    """Die kleinste Stabkraft als Teil der grössten: 0.01 ist 1 %."""


@dataclass(frozen=True)
class Formzustand:
    """Was von einer Anfrage zur nächsten geht."""

    abdruck: str
    schritt: int
    """Wie viele Schritte gerechnet sind."""

    dichte: Tuple[float, ...]
    """Je Element seine Dichte nach dem Schritt, ungefiltert -- in der Folge des Netzes."""


@dataclass(frozen=True)
class Formrunde:
    """Was eine Anfrage gibt."""

    zustand: Formzustand
    form: str
    """Das Bild der Form nach dem letzten Schritt (Dateikopf)."""

    elemente: int
    aenderung: float
    """Wie stark sich die Dichten im letzten Schritt höchstens änderten -- ohne Schritt unendlich."""

    fertig: bool
    ergebnis: Optional[Suchergebnis]
    """Das Fachwerk der Form -- nur, wenn sie fertig ist oder abgeschlossen wurde."""


def schritte(modell: Modell, einstellung: Formeinstellung, zustand: Optional[Formzustand],
             sekunden: float = SEKUNDEN, abschliessen: bool = False) -> Formrunde:
    """
    Die nächsten Schritte, bis ``sekunden`` um sind, mindestens einer -- von
    vorn, wenn ``zustand`` fehlt oder nicht zu Modell und Verfahren passt.
    Mit ``abschliessen`` keiner mehr: das Fachwerk der Form, wie sie ist,
    angehalten. Das Modell ist geprüft; wirft
    :class:`~opencivil.fachwerkmodell.simp.NetzFehler`.
    """
    n = _netz(modell, einstellung.weite)
    marke = abdruck(modell, einstellung)
    if (zustand is None or zustand.abdruck != marke or len(zustand.dichte) != len(n.elemente)
            or not all(0.0 <= d <= 1.0 for d in zustand.dichte)):
        x, nummer = (einstellung.volumen,) * len(n.elemente), 0
    else:
        x, nummer = zustand.dichte, zustand.schritt
    aenderung = math.inf
    ende = time.perf_counter() + sekunden
    while not abschliessen and nummer < HOECHSTENS_SCHRITTE:
        s = simp.schritt(n, x, einstellung.volumen)
        x, nummer, aenderung = s.dichte, nummer + 1, s.aenderung
        if aenderung < GENUG or time.perf_counter() >= ende:
            break
    fertig = not abschliessen and (aenderung < GENUG or nummer >= HOECHSTENS_SCHRITTE)
    form = formtext(n, x)
    ergebnis = None
    if fertig or abschliessen:
        ergebnis = _fachwerk(n, x, einstellung, Suchergebnis(
            fachwerk=None, abdruck=marke, runden=nummer, fertig=fertig, moeglich=0, im_modell=0,
            form=form))
    return Formrunde(zustand=Formzustand(marke, nummer, tuple(x)), form=form,
                     elemente=len(n.elemente), aenderung=aenderung, fertig=fertig, ergebnis=ergebnis)


def ganz_formen(modell: Modell, einstellung: Formeinstellung) -> Suchergebnis:
    """Schritt um Schritt bis zum Ende, wie die Seite sucht -- nur ohne Bild dazwischen."""
    return schritte(modell, einstellung, None, sekunden=math.inf).ergebnis


def _fachwerk(n: Netz, x: Sequence[float], einstellung: Formeinstellung,
              rahmen: Suchergebnis) -> Suchergebnis:
    """
    Das Fachwerk der Form mit den Dichten ``x``: die möglichen Stäbe aus
    ihren Mittellinien, die Kräfte aus der Optimierung -- in ``rahmen``,
    was es sonst sagt.
    """
    gs = skelett.moegliche_staebe(n, x)
    alle = range(len(gs.staebe))
    skala = max(map(abs, gs.last))
    opt = optimum(gs, alle, einstellung, skala)
    return Suchergebnis(fachwerk=nachbearbeiten(gs, alle, opt, einstellung, skala, True),
                        abdruck=rahmen.abdruck, runden=rahmen.runden, fertig=rahmen.fertig,
                        moeglich=len(gs.staebe), im_modell=len(gs.staebe), form=rahmen.form)


def formtext(n: Netz, x: Sequence[float]) -> str:
    """Das Bild der Form mit den Dichten ``x`` -- siehe Dateikopf."""
    stufe = {e: STUFEN[min(15, max(0, round(15.0 * r)))] for e, r in zip(n.elemente, gefiltert(n, x))}
    return "".join(stufe.get((i, j), "-") for j in range(n.zeilen) for i in range(n.spalten))


@lru_cache(maxsize=2)
def _netz(modell: Modell, weite: float) -> Netz:
    """Das Netz, aus dem Speicher, wenn es zu Modell und Netzweite schon gebaut ist."""
    return simp.netz(modell, weite)
