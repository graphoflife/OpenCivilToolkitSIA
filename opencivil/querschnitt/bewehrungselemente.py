"""
opencivil/querschnitt/bewehrungselemente.py -- die gezeichnete Bewehrung, je nach Art.

VERANTWORTUNG:
Ein Bewehrungselement der Querschnittsanalyse ist ein Einzelstab
(:class:`Einzelstab`), eine Reihe gleicher Staebe auf einer Linie
(:class:`Stabreihe`) oder eine verschmierte Linie
(:class:`VerschmierteLinie`). Was je Art anders ist, steht in ihrer Klasse,
je einmal: wo ihre Staebe liegen, wie sie in den Tabellen der Herleitung
steht, wie sie in den Querschnitt eingeht
(:meth:`Bewehrungselement.als_bewehrung`) und welcher Durchmesser ihre
Rissbreite bestimmt. Welche Art eine Beschreibung ist, wird einmal
entschieden, beim Bauen (:func:`aus_stab`, :func:`aus_linie`).

Bis 2026-10-25 war ein Element ein Datensatz mit der Art als Text, und ein
Dutzend Weichen in fuenf Modulen fragten sie ab.

Koordinaten und Durchmesser in mm, Flaechen in mm² -- wie in der Zeichnung.
Erst :meth:`~Bewehrungselement.als_bewehrung` rechnet in Meter um.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, ClassVar, List, Mapping, Optional, Tuple

from opencivil.core.latex import Mathe, Zelle
from opencivil.material.basis import Baustoff
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.geometrie import Linienart, Punkt
from opencivil.querschnitt.interaktion import Bewehrung, linie_als_bewehrung

#: mm in m.
MM = 1e-3

#: Zu einem Punkt der Zeichnung der Werkstoff, der dort liegt und den der Stahl
#: verdraengt -- als Index, ohne Beton ``None``.
Verdraengt = Callable[[Punkt], Optional[int]]


@dataclass(frozen=True)
class Bewehrungselement(ABC):
    """Ein Bewehrungselement der Zeichnung -- siehe Dateikopf."""

    name: str
    kennung: str
    stahl: Baustoff
    von: Punkt
    bis: Punkt
    flaeche: float
    """Die ganze Stahlflaeche des Elements in mm²."""

    verschmiert: ClassVar[bool] = False
    """Ob der Stahl ueber eine Linie verteilt ist statt in Staeben."""

    @property
    def punkte(self) -> Tuple[Punkt, ...]:
        """Die Stabmitten -- verschmiert keine."""
        return ()

    @property
    def lage(self) -> Mathe:
        """Wo es liegt, fuer die Tabelle der Herleitung."""
        return Mathe(f"({self.von[0]:g};\\ {self.von[1]:g}) \\rightarrow "
                     f"({self.bis[0]:g};\\ {self.bis[1]:g})")

    @property
    @abstractmethod
    def menge(self) -> Zelle:
        """Wie viel Stahl es ist, fuer die Tabelle der Herleitung."""

    @property
    @abstractmethod
    def kurzmenge(self) -> Zelle:
        """Dasselbe kurz, fuer die Angaben ueber der Nachweistabelle."""

    @property
    def fiktiv(self) -> bool:
        """Ob sein :attr:`rissdurchmesser` erdacht ist statt gezeichnet."""
        return False

    @property
    @abstractmethod
    def rissdurchmesser(self) -> float:
        """Der Durchmesser, der die Rissbreite bestimmt."""

    @abstractmethod
    def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]:
        """Wie es in den Querschnitt eingeht, in Meter -- ``stahl`` ist der Index seines Stahls."""


def _staebe(punkte: Tuple[Punkt, ...], durchmesser: float, stahl: int,
            verdraengt: Verdraengt) -> List[Bewehrung]:
    einzeln = math.pi * durchmesser ** 2 / 4.0 * MM * MM
    return [Bewehrung(lage=(p[0] * MM, p[1] * MM), flaeche=einzeln, werkstoff=stahl,
                      verdraengt=verdraengt(p))
            for p in punkte]


@dataclass(frozen=True)
class Einzelstab(Bewehrungselement):
    """Ein Stab -- ``von`` und ``bis`` sind seine Mitte."""

    durchmesser: float

    @property
    def punkte(self) -> Tuple[Punkt, ...]:
        return (self.von,)

    @property
    def lage(self) -> Mathe:
        return Mathe(f"({self.von[0]:g};\\ {self.von[1]:g})")

    @property
    def menge(self) -> Zelle:
        return Mathe(rf"\varnothing {self.durchmesser:g}")

    kurzmenge = menge

    @property
    def rissdurchmesser(self) -> float:
        return self.durchmesser

    def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]:
        return _staebe(self.punkte, self.durchmesser, stahl, verdraengt)


@dataclass(frozen=True)
class Stabreihe(Bewehrungselement):
    """Gleiche Staebe auf einer Linie, nach Anzahl oder Teilung (:func:`~opencivil.querschnitt.geometrie.stablinie`)."""

    durchmesser: float
    linie: geo.Stablinie
    gewaehlt: Optional[float] = None
    """Nach Teilung der eingegebene Abstand -- nach Anzahl keiner."""

    @property
    def punkte(self) -> Tuple[Punkt, ...]:
        return self.linie.punkte

    @property
    def menge(self) -> Zelle:
        n = len(self.punkte)
        return Mathe(rf"{n} \varnothing {self.durchmesser:g}"
                     + (rf"\ @\ {self.linie.teilung:.1f}" if n > 1 else "")
                     + (rf"\ (\text{{gewählt }} {self.gewaehlt:g})"
                        if self.gewaehlt is not None else ""))

    @property
    def kurzmenge(self) -> Zelle:
        return Mathe(rf"{len(self.punkte)} \varnothing {self.durchmesser:g}")

    @property
    def rissdurchmesser(self) -> float:
        return self.durchmesser

    def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]:
        return _staebe(self.punkte, self.durchmesser, stahl, verdraengt)


@dataclass(frozen=True)
class VerschmierteLinie(Bewehrungselement):
    """
    Stahl, gleichmaessig ueber eine Linie verteilt: die Flaeche von Hand oder
    aus Staeben ⌀ im Abstand s ueber eine Laenge L.
    """

    aus_staeben: Optional[Tuple[float, float, float]] = None
    """⌀, s und L, aus denen die Flaeche kommt -- von Hand keine."""

    verschmiert = True

    @property
    def menge(self) -> Zelle:
        if self.aus_staeben is None:
            return "verschmiert"
        d, s, L = self.aus_staeben
        return Mathe(rf"\text{{verschmiert: }} \varnothing {d:g}\ @\ {s:g}"
                     rf"\ \text{{auf}}\ {L:.0f}")

    @property
    def kurzmenge(self) -> Zelle:
        return Mathe(rf"{self.flaeche:.0f}\,\mathrm{{mm}}^2")

    @property
    def fiktiv(self) -> bool:
        """Die Flaeche von Hand: ihr Durchmesser ist erdacht, nicht aus ⌀ und s."""
        return self.aus_staeben is None

    @property
    def rissdurchmesser(self) -> float:
        """
        Aus Staeben deren ⌀. Die Flaeche von Hand verteilt sich auf Staebe im
        Abstand :data:`~opencivil.querschnitt.geometrie.TEILUNG_VERSCHMIERT`
        (:func:`~opencivil.querschnitt.geometrie.aequivalenter_durchmesser`).
        """
        if self.aus_staeben is None:
            return geo.aequivalenter_durchmesser(self.flaeche, math.dist(self.von, self.bis))
        return self.aus_staeben[0]

    def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]:
        mitte = ((self.von[0] + self.bis[0]) / 2.0, (self.von[1] + self.bis[1]) / 2.0)
        return linie_als_bewehrung(
            (self.von[0] * MM, self.von[1] * MM), (self.bis[0] * MM, self.bis[1] * MM),
            self.flaeche * MM * MM, stahl, verdraengt(mitte))


def aus_stab(s: Mapping) -> Einzelstab:
    """Ein Stab der Beschreibung, wie :class:`~opencivil.querschnitt.analyse.Querschnittsanalyse` ihn bekommt."""
    lage, durchmesser = tuple(s["lage"]), s["durchmesser"]
    return Einzelstab(name=s["name"], kennung=s["kennung"], stahl=s["stahl"], von=lage,
                      bis=lage, flaeche=math.pi * durchmesser ** 2 / 4.0, durchmesser=durchmesser)


def aus_linie(l: Mapping, linie: geo.Stablinie) -> Bewehrungselement:
    """
    Eine Stablinie der Beschreibung mit ihren aufgeloesten Staeben ``linie``
    -- nach ihrer Art eine Reihe von Staeben oder eine verschmierte Linie.
    """
    kopf = dict(name=l["name"], kennung=l["kennung"], stahl=l["stahl"], von=tuple(l["von"]),
                bis=tuple(l["bis"]), flaeche=geo.linienflaeche(l, linie.laenge, len(linie.punkte)))
    art = Linienart(l["art"])
    if art is Linienart.FLAECHE:
        return VerschmierteLinie(
            **kopf, aus_staeben=((l["durchmesser"], l["teilung"], l["laenge"] or linie.laenge)
                                 if l["verschmiert"] == "staebe" else None))
    return Stabreihe(**kopf, durchmesser=l["durchmesser"], linie=linie,
                     gewaehlt=l["teilung"] if art is Linienart.TEILUNG else None)
