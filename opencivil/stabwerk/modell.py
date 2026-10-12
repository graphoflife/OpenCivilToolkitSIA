"""
opencivil/stabwerk/modell.py -- was gerechnet wird: das ebene Stabwerk in SI.

VERANTWORTUNG:
Die Eingabe des Rechenkerns, ohne Oberflaeche und ohne Projekt: Knoten,
Staebe, Lager, Lasten, Lastfaelle und Kombinationen, alles in N, m und rad.
Aus der Beschreibung eines Balkensystems baut sie
:mod:`opencivil.projekt.balkensystem`; gerechnet wird in
:mod:`~opencivil.stabwerk.system`.

DIE ACHSEN DES SYSTEMS:
``x`` nach rechts, ``z`` nach oben, Drehungen im Gegenuhrzeigersinn.
Verschiebungen und Lagerkraefte sind positiv entlang dieser Achsen; eine
Lagerkraft nach oben ist positiv.

LASTEN MIT RICHTUNG:
Eine Kraftlast traegt ihre Richtung und ist positiv in Pfeilrichtung
(:class:`Lastrichtung`): «senkrecht» nach unten, wie die Schwerkraft,
«waagrecht» nach rechts, «quer» zur gestrichelten Faser des Stabs, «laengs»
vom Anfang zum Ende. Momentlasten drehen im Gegenuhrzeigersinn. Senkrechte und
waagrechte Lasten gelten je Meter Stab -- oder, mit ``projiziert``, je Meter
der Projektion, wie Schnee auf einem geneigten Dach.

HALT:
Ein Lager haelt je Richtung fest (:data:`FEST`), federnd (eine Zahl) oder
gar nicht (``None``) -- dieselbe Wahl fuer die Linienlager eines Stabs, quer
und laengs. Eine Feder in N/m bzw. Nm/rad, eine Bettung in N/m je m Stab.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

#: Fest gehalten -- eine Richtung ohne Verschiebung.
FEST = math.inf


class Lastrichtung(str, Enum):
    """Wohin eine Kraftlast zeigt, wenn ihr Wert positiv ist."""

    SENKRECHT = "senkrecht"
    WAAGRECHT = "waagrecht"
    QUER = "quer"
    LAENGS = "laengs"

    @property
    def im_system(self) -> bool:
        """Ob sie in den Achsen des Systems liegt -- und nicht in denen des Stabs."""
        return self in (Lastrichtung.SENKRECHT, Lastrichtung.WAAGRECHT)

    def vektor(self, c: float, s: float) -> Tuple[float, float]:
        """
        Die Richtung als Einheitsvektor ``(x, z)`` im System, fuer einen Stab
        mit ``(c, s) = (cos α, sin α)``. Quer heisst zur gestrichelten Faser:
        ``(s, -c)``, die rechte Seite des Stabs.
        """
        return {
            Lastrichtung.SENKRECHT: (0.0, -1.0),
            Lastrichtung.WAAGRECHT: (1.0, 0.0),
            Lastrichtung.QUER: (s, -c),
            Lastrichtung.LAENGS: (c, s),
        }[self]

    def projektion(self, c: float, s: float) -> float:
        """Laenge der Projektion je Meter Stab -- senkrecht auf die Waagrechte, waagrecht auf die Senkrechte."""
        return abs(c) if self is Lastrichtung.SENKRECHT else abs(s)


class Lastart(str, Enum):
    """Was fuer eine Last auf einem Stab liegt."""

    LINIENLAST = "linienlast"
    """Kraft je Laenge, von ``wert_a`` nach ``wert_b`` linear -- gleichmaessig oder als Dreieck."""

    EINZELLAST = "einzellast"
    MOMENT = "moment"
    """Ein Einzelmoment, im Gegenuhrzeigersinn."""

    LINIENMOMENT = "linienmoment"
    """Moment je Laenge, linear."""

    @property
    def verteilt(self) -> bool:
        return self in (Lastart.LINIENLAST, Lastart.LINIENMOMENT)

    @property
    def kraft(self) -> bool:
        return self in (Lastart.LINIENLAST, Lastart.EINZELLAST)


@dataclass(frozen=True)
class Knoten:
    name: str
    x: float
    z: float


Halt = Optional[float]
"""``None`` frei, :data:`FEST` fest, sonst eine Federsteifigkeit."""


@dataclass(frozen=True)
class Lager:
    """Ein Lager an einem Knoten -- je Richtung frei, fest oder Feder."""

    name: str
    knoten: str
    x: Halt = None
    """In N/m, wenn Feder."""

    z: Halt = None
    phi: Halt = None
    """In Nm/rad, wenn Feder."""


@dataclass(frozen=True)
class Stab:
    """
    Eine Linie des Systems -- ein Stab, der traegt, oder nur ein Linienlager.

    ``quer`` und ``laengs`` sind die Linienlager: frei, fest oder eine
    Bettung in N/m². Die Gelenke gelten fuer das Moment am Ende.
    """

    name: str
    a: str
    b: str
    EA: float = 0.0
    """N."""

    EI: float = 0.0
    """Nm²."""

    traegt: bool = True
    gelenk_a: bool = False
    gelenk_b: bool = False
    quer: Halt = None
    laengs: Halt = None


@dataclass(frozen=True)
class Stablast:
    """
    Eine Last auf einem Stab. Stellen in m ab seinem Anfang; ``bis = None``
    heisst bis zum Ende. Einzellast und Einzelmoment stehen bei ``von``.
    Werte in N/m, N, Nm oder Nm/m, positiv in ihrer Richtung.
    """

    stab: str
    art: Lastart
    wert_a: float
    wert_b: Optional[float] = None
    """Am Ende des belasteten Bereichs -- ``None``: wie am Anfang."""

    richtung: Lastrichtung = Lastrichtung.SENKRECHT
    von: float = 0.0
    bis: Optional[float] = None
    projiziert: bool = False

    def mal(self, faktor: float) -> "Stablast":
        return replace(self, wert_a=self.wert_a * faktor,
                       wert_b=None if self.wert_b is None else self.wert_b * faktor)


@dataclass(frozen=True)
class Knotenlast:
    """Eine Last an einem Knoten, in den Achsen des Systems: N, N, Nm."""

    knoten: str
    Fx: float = 0.0
    Fz: float = 0.0
    M: float = 0.0

    def mal(self, faktor: float) -> "Knotenlast":
        return replace(self, Fx=self.Fx * faktor, Fz=self.Fz * faktor, M=self.M * faktor)


Last = Union[Stablast, Knotenlast]


@dataclass
class Lastfall:
    name: str
    lasten: List[Last] = field(default_factory=list)


@dataclass
class Kombination:
    """Eine Kombination: je Lastfall ein Beiwert. Was nicht dasteht, zaehlt null."""

    name: str
    faktoren: Dict[str, float] = field(default_factory=dict)


@dataclass
class System:
    knoten: List[Knoten] = field(default_factory=list)
    staebe: List[Stab] = field(default_factory=list)
    lager: List[Lager] = field(default_factory=list)
    lastfaelle: List[Lastfall] = field(default_factory=list)
    kombinationen: List[Kombination] = field(default_factory=list)

    def kombiniert(self, kombination: Kombination) -> Lastfall:
        """
        Eine Kombination als Lastfall: jede Last ihres Lastfalls mal dessen
        Beiwert. So laeuft sie durch dieselbe Rechnung wie ein Lastfall --
        und weil alles linear ist, ist das Ergebnis die Summe der mit ihren
        Beiwerten gewichteten Lastfaelle.
        """
        nach_name = {f.name: f for f in self.lastfaelle}
        lasten: List[Last] = []
        for name, faktor in kombination.faktoren.items():
            fall = nach_name.get(name)
            if fall is None or not faktor:
                continue
            lasten.extend(last.mal(faktor) for last in fall.lasten)
        return Lastfall(kombination.name, lasten)
