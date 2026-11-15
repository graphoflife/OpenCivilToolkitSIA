"""
opencivil/stabwerk3d/modell.py -- was gerechnet wird: das raeumliche Stabwerk in SI.

VERANTWORTUNG:
Die Eingabe des Rechenkerns, ohne Oberflaeche und ohne Projekt: Knoten,
Staebe, Lager, Lasten, Lastfaelle und Kombinationen, alles in N, m und rad.
Gerechnet wird in :mod:`~opencivil.stabwerk3d.system`. Was nicht vom Raum
abhaengt, kommt aus der Ebene (:mod:`opencivil.stabwerk.modell`): wie eine
Richtung gehalten ist (:class:`Halt`), die Arten der Lasten, Lastfall und
Kombination.

DIE ACHSEN DES SYSTEMS:
``x`` und ``y`` waagrecht, ``z`` nach oben, ein Rechtssystem; Drehungen im
Rechtssinn um ihre Achse. Verschiebungen und Lagerkraefte sind positiv
entlang dieser Achsen. Liegt ein Rahmen in der x-z-Ebene, sieht man ihn wie
im 2D-Balkensystem: x nach rechts, z nach oben -- ``y`` zeigt dann vom
Betrachter weg, und eine Drehung im Gegenuhrzeigersinn ist eine um ``-y``.

LASTEN MIT RICHTUNG:
Eine Kraftlast ist positiv in ihrer Richtung (:class:`Richtung`):
«senkrecht» nach unten, wie die Schwerkraft, in x, y oder z des Systems,
oder laengs, quer y oder quer z in den Achsen des Stabs
(:mod:`~opencivil.stabwerk3d.stab`). Eine Momentlast dreht im Rechtssinn um
ihre Richtung -- laengs ist sie ein Torsionsmoment. Lasten in Richtungen des
Systems gelten je Meter Stab -- oder, mit ``projiziert``, je Meter seiner
Projektion auf die Ebene senkrecht zur Richtung, wie Schnee auf einem
geneigten Dach.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import List, Optional, Sequence, Tuple, Union

from opencivil.core.wahl import Wahl
from opencivil.stabwerk.modell import FREI, Halt, Kombination, Lastart, Lastfall
from opencivil.stabwerk3d.raum import Vektor


class Richtung(Wahl):
    """Wohin eine Kraftlast zeigt -- oder um welche Achse eine Momentlast dreht --, wenn ihr Wert positiv ist."""

    SENKRECHT = "senkrecht"
    X = "x"
    Y = "y"
    Z = "z"
    LAENGS = "laengs"
    QUER_Y = "quer_y"
    QUER_Z = "quer_z"

    @property
    def beschriftung(self) -> str:
        return {
            Richtung.SENKRECHT: "↓ senkrecht",
            Richtung.X: "in x",
            Richtung.Y: "in y",
            Richtung.Z: "in z",
            Richtung.LAENGS: "längs zum Stab",
            Richtung.QUER_Y: "quer, in y des Stabs",
            Richtung.QUER_Z: "quer, in z des Stabs",
        }[self]

    @property
    def im_system(self) -> bool:
        """Ob sie in den Achsen des Systems liegt -- und nicht in denen des Stabs."""
        return self not in (Richtung.LAENGS, Richtung.QUER_Y, Richtung.QUER_Z)

    def vektor(self, achsen: Sequence[Vektor]) -> Vektor:
        """Die Richtung als Einheitsvektor im System, fuer einen Stab mit den Achsen ``(x, y, z)``."""
        return {
            Richtung.SENKRECHT: (0.0, 0.0, -1.0),
            Richtung.X: (1.0, 0.0, 0.0),
            Richtung.Y: (0.0, 1.0, 0.0),
            Richtung.Z: (0.0, 0.0, 1.0),
            Richtung.LAENGS: achsen[0],
            Richtung.QUER_Y: achsen[1],
            Richtung.QUER_Z: achsen[2],
        }[self]

    def projektion(self, achsen: Sequence[Vektor]) -> float:
        """
        Laenge der Projektion je Meter Stab, auf die Ebene senkrecht zu dieser
        Richtung -- in der Ebene ``|cos α|`` fuer senkrecht, ``|sin α|`` fuer
        waagrecht.
        """
        e, x = self.vektor(achsen), achsen[0]
        kosinus = sum(a * b for a, b in zip(e, x))
        return math.sqrt(max(0.0, 1.0 - kosinus * kosinus))


@dataclass(frozen=True)
class Knoten:
    name: str
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Lager:
    """Ein Lager an einem Knoten -- je Richtung des Systems frei, fest oder Feder."""

    name: str
    knoten: str
    x: Halt = FREI
    """In N/m, wenn Feder."""

    y: Halt = FREI
    z: Halt = FREI
    phi_x: Halt = FREI
    """In Nm/rad, wenn Feder."""

    phi_y: Halt = FREI
    phi_z: Halt = FREI

    @property
    def verschiebungen(self) -> Tuple[Halt, Halt, Halt]:
        return (self.x, self.y, self.z)

    @property
    def drehungen(self) -> Tuple[Halt, Halt, Halt]:
        return (self.phi_x, self.phi_y, self.phi_z)


@dataclass(frozen=True)
class Stab:
    """
    Eine Linie des Systems -- ein Stab, der traegt, oder nur ein Linienlager.

    ``drehung`` ist der Drehwinkel β seiner Achsen um x, in rad. Die
    Linienlager halten laengs und quer in y und z des Stabs: frei, fest oder
    eine Bettung in N/m². Ein Gelenk loest am Stabende alle drei Momente,
    wie ein Kugelgelenk; mit Gelenken an beiden Enden traegt der Stab keine
    Torsion (:mod:`~opencivil.stabwerk3d.system`).
    """

    name: str
    a: str
    b: str
    EA: float = 0.0
    """N."""

    EI_y: float = 0.0
    """Nm² -- Biegung um y, in der x-z-Ebene des Stabs."""

    EI_z: float = 0.0
    """Nm² -- Biegung um z, in der x-y-Ebene des Stabs."""

    GI_T: float = 0.0
    """Nm² -- Torsion."""

    drehung: float = 0.0
    traegt: bool = True
    gelenk_a: bool = False
    gelenk_b: bool = False
    laengs: Halt = FREI
    quer_y: Halt = FREI
    quer_z: Halt = FREI


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

    richtung: Richtung = Richtung.SENKRECHT
    von: float = 0.0
    bis: Optional[float] = None
    projiziert: bool = False

    def mal(self, faktor: float) -> "Stablast":
        return replace(self, wert_a=self.wert_a * faktor,
                       wert_b=None if self.wert_b is None else self.wert_b * faktor)


@dataclass(frozen=True)
class Knotenlast:
    """Eine Last an einem Knoten, in den Achsen des Systems: N und Nm."""

    knoten: str
    F: Vektor = (0.0, 0.0, 0.0)
    M: Vektor = (0.0, 0.0, 0.0)

    def mal(self, faktor: float) -> "Knotenlast":
        return replace(self, F=tuple(f * faktor for f in self.F),
                       M=tuple(m * faktor for m in self.M))


Last = Union[Stablast, Knotenlast]


@dataclass
class System:
    knoten: List[Knoten] = field(default_factory=list)
    staebe: List[Stab] = field(default_factory=list)
    lager: List[Lager] = field(default_factory=list)
    lastfaelle: List[Lastfall] = field(default_factory=list)
    kombinationen: List[Kombination] = field(default_factory=list)
