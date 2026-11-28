"""
opencivil/durchstanzen/bereiche.py -- Bereiche der Platte mit eigener Dicke.

VERANTWORTUNG:
Ein :class:`Plattenbereich` -- sein Umriss, seine Dicke und auf welcher
Seite der Platte seine Stufe liegt -- und was die Stelle von allen zusammen
wissen muss (:class:`Dicken`): welche Bereiche die Stütze umschliessen, was
jenseits einer Stufe liegt, welche statische Höhe wo gilt. Die Platte
behält ihre Dicke h; ein Bereich gilt in seinem Umriss statt ihr, dicker
oder dünner. Bereiche dürfen ineinander liegen -- es gilt der innerste --,
aber sich nicht teilweise überdecken und die Stütze nicht schneiden; das
prüft der Aufbau (:mod:`opencivil.projekt.aufbau.durchstanzen`).

DIE SEITE DER STUFE (SIA 262:2025, 4.3.6.2.7, Figur 24):
Um die Stütze liegt die Druckseite der Platte auf der Seite der Stütze --
bei der Decke unten, bei der Bodenplatte oben. Ein Bereich ist dicker oder
dünner auf einer der beiden Seiten (:class:`Seite`):

- zur Stütze hin -- auf der Druckseite, wie ein Stützenkopf unter einer
  Decke (Figur 24a): die Zugseite läuft eben durch;
- Gegenseite -- auf der Zugseite, wie eine Vertiefung unter einer
  Bodenplatte (Figur 24c): die Zugbewehrung folgt der Oberfläche.

DIE STATISCHE HÖHE:
Die Zugbewehrung liegt überall c_nom unter der Oberfläche der Zugseite: in
einem Bereich ist d um so viel grösser oder kleiner als in der Platte, wie
er dicker oder dünner ist, d_B = d + (h_B − h). Welche Seite sich dabei
verschiebt, zählt erst für einen Riss, der über eine Stufe läuft
(:meth:`Dicken.wirksam`): er beginnt auf der Druckseite des einen Bereichs
und endet an der Zugbewehrung eines anderen. Je Bereich steht darum, um wie
viel seine Druckseite und seine Zugseite gegenüber der Platte versetzt sind
(:class:`Versatz`) -- ineinander liegende Bereiche je gegenüber dem, in dem
sie liegen.

EINHEITEN:
m.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Sequence, Tuple

from opencivil.core.wahl import Wahl
from opencivil.durchstanzen.schnitt import Punkt
from opencivil.querschnitt.geometrie import (
    Beziehung, beziehung, flaeche, konvexe_huelle, lage, verschachteln,
)


class Seite(Wahl):
    """Auf welcher Seite der Platte die Stufe eines Bereichs liegt -- siehe Dateikopf."""

    STUETZE = "stuetze"
    GEGENSEITE = "gegenseite"

    @property
    def beschriftung(self) -> str:
        return "zur Stütze hin" if self is Seite.STUETZE else "Gegenseite"

    @property
    def figur(self) -> str:
        """Die Figur der Norm, die die Stufe zeigt."""
        return "Figur 24a" if self is Seite.STUETZE else "Figur 24c"

    @property
    def titel(self) -> str:
        """Was die Stellung heisst, in einem Satz -- für den Schalter."""
        if self is Seite.STUETZE:
            return "Die Stufe liegt auf der Seite der Stütze, wie ein Stützenkopf"
        return "Die Stufe liegt gegenüber der Stütze, wie eine Vertiefung"


@dataclass(frozen=True)
class Plattenbereich:
    """Ein Bereich mit eigener Dicke: Name, Ecken in m, Dicke und die Seite der Stufe."""

    name: str
    """Wie Zeichnung und Herleitung ihn nennen -- «B1»."""

    ecken: Tuple[Punkt, ...]
    h: float
    seite: Seite

    @property
    def titel(self) -> str:
        """«Bereich B1» -- so steht er in Sätzen."""
        return f"Bereich {self.name}"

    @property
    def huelle(self) -> Tuple[Punkt, ...]:
        """Die konvexe Hülle gegen den Uhrzeigersinn -- um sie läuft ein Schnitt (Figur 22c)."""
        return konvexe_huelle(self.ecken)

    def enthaelt(self, punkte: Sequence[Punkt]) -> bool:
        """Ob alle ``punkte`` in ihm liegen -- auf seinem Rand zählt als darin."""
        return all(lage(p, self.ecken) >= 0 for p in punkte)


@dataclass(frozen=True)
class Versatz:
    """
    Um wie viel die Druckseite und die Zugseite eines Bereichs gegenüber der
    Platte nach aussen versetzt sind, in m -- negativ, wo er dünner ist.
    Die Summe ist, um wie viel er dicker ist als die Platte.
    """

    druck: float = 0.0
    zug: float = 0.0


PLATTE = Versatz()


@dataclass(frozen=True)
class Dicken:
    """
    Die Platte und ihre Bereiche: wo welche Dicke gilt -- siehe Dateikopf.
    ``h`` und ``d`` sind die der Platte, ausserhalb aller Bereiche.
    """

    h: float
    d: float
    bereiche: Tuple[Plattenbereich, ...] = ()
    eltern: Dict[str, Optional[Plattenbereich]] = field(init=False, repr=False, compare=False)
    """Je Bereich der kleinste, der ihn ganz enthält; ``None``: die Platte."""

    def __post_init__(self) -> None:
        bereiche = tuple(self.bereiche)
        object.__setattr__(self, "bereiche", bereiche)
        # Teilweise überdeckte Bereiche weist schon der Aufbau ab.
        eltern = verschachteln([b.ecken for b in bereiche], [b.titel for b in bereiche])
        object.__setattr__(self, "eltern", {
            b.name: (None if i is None else bereiche[i]) for b, i in zip(bereiche, eltern)})

    def aussen(self, bereich: Plattenbereich) -> Optional[Plattenbereich]:
        """Was jenseits seiner Stufe liegt: der Bereich, in dem er liegt -- ``None``: die Platte."""
        return self.eltern[bereich.name]

    def vorfahren(self, bereich: Plattenbereich) -> Tuple[Plattenbereich, ...]:
        """Die Bereiche, in denen er liegt, der innerste zuerst."""
        kette = []
        aussen = self.aussen(bereich)
        while aussen is not None:
            kette.append(aussen)
            aussen = self.aussen(aussen)
        return tuple(kette)

    def h_von(self, bereich: Optional[Plattenbereich]) -> float:
        return self.h if bereich is None else bereich.h

    def d_von(self, bereich: Optional[Plattenbereich]) -> float:
        """Die statische Höhe im Bereich: d der Platte, verschoben um den Unterschied der Dicke."""
        return self.d + self.h_von(bereich) - self.h

    def versatz(self, bereich: Optional[Plattenbereich]) -> Versatz:
        """Wie weit Druck- und Zugseite des Bereichs gegenüber der Platte versetzt sind."""
        if bereich is None:
            return PLATTE
        aussen = self.aussen(bereich)
        v, mehr = self.versatz(aussen), bereich.h - self.h_von(aussen)
        if bereich.seite is Seite.STUETZE:
            return Versatz(v.druck + mehr, v.zug)
        return Versatz(v.druck, v.zug + mehr)

    def dicker(self, bereich: Plattenbereich) -> bool:
        """Ob der Bereich dicker ist als das, was jenseits seiner Stufe liegt."""
        return bereich.h > self.h_von(self.aussen(bereich)) + 1e-9

    def um(self, umriss: Sequence[Punkt]) -> Tuple[Plattenbereich, ...]:
        """Die Bereiche, die den Umriss ganz umschliessen, der innerste zuerst."""
        um = [b for b in self.bereiche
              if beziehung(umriss, b.ecken) is Beziehung.ERSTES_IM_ZWEITEN]
        return tuple(sorted(um, key=lambda b: abs(flaeche(b.ecken))))

    def wirksam(self, start: Optional[Plattenbereich],
                reicht: Callable[[float, Plattenbereich], bool]) -> Optional[Plattenbereich]:
        """
        Wo die Zugbewehrung liegt, an der ein Riss endet, der auf der
        Druckseite von ``start`` beginnt: in ``start`` selbst -- ausser
        ``start`` ist auf der Gegenseite dicker und reicht nicht weit genug,
        ``reicht(d_v, bereich)`` ist falsch. Dann endet der Riss jenseits
        seiner Stufe, wo die Zugbewehrung höher liegt, und es gilt, was dort
        liegt. Die Druckseite ist dabei dieselbe: eine Stufe auf der
        Gegenseite versetzt nur die Zugseite. Nach Vorgabe, nicht
        nachgeschlagen (:mod:`.stufen`).
        """
        bereich = start
        while (bereich is not None and bereich.seite is Seite.GEGENSEITE and self.dicker(bereich)
               and not reicht(self.d_von(bereich), bereich)):
            bereich = self.aussen(bereich)
        return bereich

