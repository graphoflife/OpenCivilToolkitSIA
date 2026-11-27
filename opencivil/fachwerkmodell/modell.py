"""
opencivil/fachwerkmodell/modell.py -- die Scheibe eines Fachwerkmodells, in SI.

VERANTWORTUNG:
Was ein Fachwerkmodell rechnet: Umrisse aus Ecken -- Scheiben, die
zusammen das Material bilden, und Löcher, die es dort wegnehmen --, Lager
an Punkten, je fest in x, in y oder in beiden (:class:`Halt`), und
Punktlasten in jeder Richtung. Dazu die eine Regel, wo Material ist
(:meth:`Modell.im_material`): in einer Scheibe, ihr Rand zählt dazu, und
nicht im Innern eines Lochs -- sein Rand ist noch Material. Ein Lager am
Rand eines Lochs steht also auf der Scheibe.

KEIN MATERIAL, KEINE DICKE:
Ohne Bemessung hängen Fachwerk und Kräfte nur von Form, Lagern und Lasten
ab (Plan vom 2026-11-27, Entscheid 11). Ein Satz Lasten je Modell; wer
einen zweiten Lastfall will, kopiert es.

KOORDINATEN UND EINHEITEN:
x nach rechts, y nach oben, in m; Kräfte in N, ``F_x`` nach rechts, ``F_y``
nach oben. Die Beschreibung (:mod:`opencivil.projekt.fachwerkmodell`) gibt
die senkrechte Kraft nach unten positiv an, wie das Balkensystem;
umgerechnet wird beim Bauen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from opencivil.core.wahl import Wahl
from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt


class Halt(Wahl):
    """In welchen Richtungen ein Lager die Scheibe hält."""

    XY = "xy"
    X = "x"
    Y = "y"

    @property
    def x(self) -> bool:
        """Ob es waagrecht hält."""
        return self is not Halt.Y

    @property
    def y(self) -> bool:
        """Ob es senkrecht hält."""
        return self is not Halt.X

    @property
    def beschriftung(self) -> str:
        return {Halt.XY: "x und y", Halt.X: "nur x", Halt.Y: "nur y"}[self]

    @property
    def erklaerung(self) -> str:
        return {Halt.XY: "Fest in x und in y – ein festes Lager.",
                Halt.X: "Fest nur in x – in y verschieblich.",
                Halt.Y: "Fest nur in y – in x verschieblich, wie ein Rollenlager auf "
                        "waagrechtem Grund."}[self]


@dataclass(frozen=True)
class Umriss:
    """Eine Scheibe oder ein Loch: ihr Name und ihre Ecken in m."""

    name: str
    ecken: Tuple[Punkt, ...]


@dataclass(frozen=True)
class Lager:
    """Ein Lager an einem Punkt der Scheibe, in m."""

    name: str
    ort: Punkt
    halt: Halt


@dataclass(frozen=True)
class Last:
    """Eine Punktlast in N: ``F_x`` nach rechts, ``F_y`` nach oben."""

    name: str
    ort: Punkt
    F_x: float
    F_y: float


@dataclass(frozen=True)
class Modell:
    """Die ganze Scheibe -- jede Liste in der Folge der Beschreibung."""

    scheiben: Tuple[Umriss, ...] = ()
    loecher: Tuple[Umriss, ...] = ()
    lager: Tuple[Lager, ...] = ()
    lasten: Tuple[Last, ...] = ()

    def in_scheibe(self, p: Punkt) -> bool:
        """Ob ``p`` in einer Scheibe liegt -- auf ihrem Rand zählt."""
        return any(geo.innen(p, s.ecken) for s in self.scheiben)

    def loch_bei(self, p: Punkt) -> Optional[Umriss]:
        """Das Loch, in dessen Innern ``p`` liegt -- auf seinem Rand liegt es in keinem."""
        return next((l for l in self.loecher
                     if geo.innen(p, l.ecken) and not geo.auf_rand(p, l.ecken)), None)

    def im_material(self, p: Punkt) -> bool:
        """Ob bei ``p`` Material ist: in einer Scheibe und in keinem Loch."""
        return self.in_scheibe(p) and self.loch_bei(p) is None
