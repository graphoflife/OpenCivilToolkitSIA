"""
opencivil/decke/modell.py -- was gerechnet wird: die Decke in SI.

VERANTWORTUNG:
Die Eingabe des Rechenkerns, ohne Oberfläche und ohne Projekt: Platten,
Lager, Stützen, versteckte Unterzüge, Zonen der Lastaufteilung, Lasten,
Lastfälle und Kombinationen -- alles in N, m und rad. Gerechnet wird in
:mod:`~opencivil.decke.rechnung`.

DIE ACHSEN:
``x`` nach rechts, ``y`` nach oben, im Grundriss. Lasten wirken nach unten
und sind dann positiv; eine Lagerkraft nach oben ist positiv.

RICHTUNGEN DER LASTABTRAGUNG:
Jede Platte trägt in zwei Richtungen, Winkel gegen die x-Achse -- im
Rechteck ``0`` und ``π/2``, in einer schiefen Platte etwa parallel zu ihren
Rändern. Die erste heisst «Richtung 1», die zweite «Richtung 2»; ein Anteil
gilt immer für Richtung 1, der Rest geht in Richtung 2. Grenzen zwei Platten
mit derselben Richtung aneinander, laufen ihre Streifen durch.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Tuple, Union

from opencivil.core.wahl import Wahl
from opencivil.decke.geometrie import Punkt

#: Die Breite eines Streifens höchstens, in m -- ein Vorschlag.
STREIFENBREITE = 0.25

#: Die Seiten der Fläche, über die eine Einzellast verteilt wird, in m -- ein Vorschlag.
VERTEILBREITE = 1.0


class Aufteilung(Wahl):
    """Wie die Last ausserhalb der gezeichneten Zonen auf die beiden Richtungen geht."""

    AUTOMATISCH = "automatisch"
    """Nach dem Muster der randnahen Lastabtragung -- siehe :mod:`~opencivil.decke.aufteilung`."""

    FEST = "fest"
    """Überall derselbe Anteil in Richtung 1."""


@dataclass(frozen=True)
class Platte:
    name: str
    ecken: Tuple[Punkt, ...]
    h: float
    """Dicke in m."""

    E: float
    """Elastizitätsmodul in N/m² -- er zählt nur, wo Platten verschieden steif sind."""

    wichte: float
    """Gewicht je Volumen in N/m³, für das Eigengewicht."""

    richtungen: Tuple[float, float] = (0.0, math.pi / 2.0)
    """Richtung 1 und 2 der Lastabtragung, rad gegen die x-Achse."""


@dataclass(frozen=True)
class Linienlager:
    """
    Eine Wand oder ein Unterzug unter der Platte, als Linie. ``vertikal``:
    sie hält die Platte in der Höhe; ``eingespannt``: sie hält ihre Drehung.
    Beides zusammen ist eine Einspannung, nur ``eingespannt`` eine
    Symmetrieachse.
    """

    name: str
    a: Punkt
    b: Punkt
    vertikal: bool = True
    eingespannt: bool = False


@dataclass(frozen=True)
class Stuetze:
    """
    Eine Stütze, ``bx × by`` gross. Die Streifen und Unterzüge über ihr
    liegen auf dem Stützenbereich ``lx × ly`` mit gleichmässiger Pressung --
    ohne Angabe so breit wie die Unterzüge über ihr, mindestens so gross wie
    die Stütze (:func:`~opencivil.decke.streifen.stuetzenbereich`).
    """

    name: str
    ort: Punkt
    bx: float
    by: float
    lx: Optional[float] = None
    ly: Optional[float] = None


@dataclass(frozen=True)
class Unterzug:
    """
    Ein versteckter Unterzug: ein Streifen der Breite ``breite`` von ``a``
    nach ``b``, so dick wie die Platte. Streifen quer dazu liegen auf ihm,
    ein Unterzug mit kleinerer ``stufe`` ebenso; er selbst liegt auf Lagern,
    Stützen und Unterzügen höherer Stufe.
    """

    name: str
    a: Punkt
    b: Punkt
    breite: float
    stufe: int = 1


@dataclass(frozen=True)
class Zone:
    """Ein Gebiet mit eigener Lastaufteilung: ``anteil`` geht in Richtung 1, der Rest in Richtung 2."""

    name: str
    ecken: Tuple[Punkt, ...]
    anteil: float


@dataclass(frozen=True)
class Flaechenlast:
    """
    Eine gleichmässige Flächenlast in N/m², nach unten positiv -- auf dem
    gezeichneten Vieleck ``ecken`` oder auf der ganzen Platte ``platte``.
    """

    name: str
    wert: float
    ecken: Tuple[Punkt, ...] = ()
    platte: str = ""

    def mal(self, faktor: float) -> "Flaechenlast":
        return replace(self, wert=self.wert * faktor)


@dataclass(frozen=True)
class Linienlast:
    """Eine gleichmässige Linienlast in N/m von ``a`` nach ``b``, nach unten positiv."""

    name: str
    a: Punkt
    b: Punkt
    wert: float

    def mal(self, faktor: float) -> "Linienlast":
        return replace(self, wert=self.wert * faktor)


@dataclass(frozen=True)
class Punktlast:
    """
    Eine Einzellast in N, nach unten positiv. Die Streifen tragen sie als
    gleichmässige Last auf der Fläche ``lx × ly`` um ``ort``; was das an
    Biegewiderstand kostet, sagt das Lastverteilelement
    (:mod:`~opencivil.decke.feld`).
    """

    name: str
    ort: Punkt
    wert: float
    lx: float = VERTEILBREITE
    ly: float = VERTEILBREITE

    def mal(self, faktor: float) -> "Punktlast":
        return replace(self, wert=self.wert * faktor)


Last = Union[Flaechenlast, Linienlast, Punktlast]


@dataclass
class Lastfall:
    name: str
    lasten: List[Last] = field(default_factory=list)
    eigengewicht: bool = False
    """Ob das Eigengewicht der Platten dazugehört."""


@dataclass
class Kombination:
    """Je Lastfall ein Beiwert. Was nicht dasteht, zählt null."""

    name: str
    faktoren: Dict[str, float] = field(default_factory=dict)


@dataclass
class Decke:
    platten: List[Platte] = field(default_factory=list)
    linienlager: List[Linienlager] = field(default_factory=list)
    stuetzen: List[Stuetze] = field(default_factory=list)
    unterzuege: List[Unterzug] = field(default_factory=list)
    zonen: List[Zone] = field(default_factory=list)
    lastfaelle: List[Lastfall] = field(default_factory=list)
    kombinationen: List[Kombination] = field(default_factory=list)
    streifenbreite: float = STREIFENBREITE
    aufteilung: Aufteilung = Aufteilung.AUTOMATISCH
    anteil: float = 0.5
    """Bei fester Aufteilung: der Anteil in Richtung 1."""
