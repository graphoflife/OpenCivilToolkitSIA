"""
opencivil/projekt/fachwerkmodell.py -- ein Fachwerkmodell, wie die Oberfläche es beschreibt.

VERANTWORTUNG:
Der :class:`FachwerkmodellEintrag`: eine Scheibe aus Umrissen und Löchern,
Lager und Punktlasten, gezeichnet aus Knoten in der Ebene -- als
speicherbare Datenklasse wie die Decke (:mod:`opencivil.projekt.decke`).
Dazu der Baukasten, der ohne Oberfläche zeichnet. Gerechnet wird in
:mod:`opencivil.fachwerkmodell`.

ALLES HÄNGT AN KNOTEN:
Eine Scheibe und ein Loch sind Umrisse aus Knoten, ein Lager und eine
Last stehen an einem. Wo ein Lager an einer Ecke steht, teilt es ihren
Knoten: wer ihn verschiebt, verschiebt beide.

KEIN MATERIAL, KEINE LASTFÄLLE:
Ohne Bemessung hängen Fachwerk und Kräfte nur von Form, Lagern und Lasten
ab. Ein Satz Lasten je Modell; für einen zweiten Lastfall kopiert man es
(Plan vom 2026-11-27, Entscheid 11).

KOORDINATEN UND EINHEITEN:
x nach rechts, y nach oben, in m. Eine Last in kN, ``F_h`` nach rechts,
``F_v`` nach unten positiv -- wie im Balkensystem. Umgerechnet wird beim
Bauen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Sequence, Union

from opencivil.core.einheiten import KN, M
from opencivil.fachwerkmodell.modell import Halt
from opencivil.projekt.eintraege import BauteilEintrag, Beschreibung
from opencivil.projekt.lesen import bereich, lesen
from opencivil.projekt.netz import Netz, neue_kennung

#: Ein Ort im Baukasten: die Kennung eines Knotens oder ``(x, y)`` in m.
Ort = Union[str, Sequence[float]]

#: Womit die Kennungen der Teile eines Fachwerkmodells beginnen -- «A» wie Auflager.
VORSILBEN = {"scheiben": "S", "loecher": "L", "lager": "A", "lasten": "F"}


@dataclass
class ScheibenknotenEintrag(Beschreibung):
    """Ein Punkt der Scheibe, in m."""

    kennung: str = ""
    x: float = bereich(0.0, heisst="x", einheit=M)
    y: float = bereich(0.0, heisst="y", einheit=M)


@dataclass
class ScheibeEintrag(Beschreibung):
    """Ein Umriss der Scheibe -- liegen mehrere da, ist Material, wo eine von ihnen ist."""

    kennung: str = ""
    knoten: List[str] = field(default_factory=list)


@dataclass
class LochEintrag(Beschreibung):
    """Ein Loch: in seinem Innern ist kein Material, auf seinem Rand schon."""

    kennung: str = ""
    knoten: List[str] = field(default_factory=list)


@dataclass
class ScheibenlagerEintrag(Beschreibung):
    """Ein Lager an einem Knoten, fest in x, in y oder in beiden."""

    kennung: str = ""
    knoten: str = ""
    halt: Halt = Halt.XY


@dataclass
class ScheibenlastEintrag(Beschreibung):
    """Eine Punktlast an einem Knoten, in jeder Richtung."""

    kennung: str = ""
    knoten: str = ""
    F_h: float = bereich(0.0, heisst="F_h", einheit=KN)
    """Waagrecht, nach rechts positiv."""

    F_v: float = bereich(100.0, heisst="F_v", einheit=KN)
    """Senkrecht, nach unten positiv."""


@dataclass
class FachwerkmodellEintrag(BauteilEintrag):
    """
    Ein Fachwerkmodell: eine Scheibe aus Umrissen und Löchern an Lagern,
    mit Punktlasten. Ohne Regeln, die das ganze Projekt aufhielten: was
    ihm fehlt, steht in seinen Meldungen, und die anderen Bauteile rechnen
    weiter.
    """

    BEZEICHNUNG = "Fachwerkmodell"
    STAMM = "Fachwerkmodell"

    kennung: str
    name: str
    knoten: List[ScheibenknotenEintrag] = field(default_factory=list)
    scheiben: List[ScheibeEintrag] = field(default_factory=list)
    loecher: List[LochEintrag] = field(default_factory=list)
    lager: List[ScheibenlagerEintrag] = field(default_factory=list)
    lasten: List[ScheibenlastEintrag] = field(default_factory=list)
    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    def lagen(self) -> dict:
        """Kennung -> ``(x, y)`` jedes Knotens, in m."""
        return {k.kennung: (k.x, k.y) for k in self.knoten}

    # -- Zeichnen ohne Oberfläche -------------------------------------------

    def netz(self) -> Netz:
        return Netz(self, neu=lambda kennung, x, y: ScheibenknotenEintrag(kennung, x, y),
                    achsen=("x", "y"))

    def _knoten(self, netz: Netz, ort: Ort) -> str:
        return ort if isinstance(ort, str) else netz.an(float(ort[0]), float(ort[1]))

    def _anlegen(self, liste: str, cls: type, felder: dict, wo: str) -> Any:
        eintrag = lesen(cls, felder, f"Fachwerkmodell '{self.name}': {wo}",
                        cls(kennung=neue_kennung(self, VORSILBEN[liste],
                                                 (e.kennung for e in getattr(self, liste)))))
        getattr(self, liste).append(eintrag)
        return eintrag

    def scheibe(self, ecken: Sequence[Ort]) -> ScheibeEintrag:
        """Ein Umriss der Scheibe mit diesen Ecken."""
        netz = self.netz()
        return self._anlegen("scheiben", ScheibeEintrag,
                             {"knoten": [self._knoten(netz, e) for e in ecken]}, "Scheibe")

    def loch(self, ecken: Sequence[Ort]) -> LochEintrag:
        netz = self.netz()
        return self._anlegen("loecher", LochEintrag,
                             {"knoten": [self._knoten(netz, e) for e in ecken]}, "Loch")

    def lager_setzen(self, ort: Ort, halt: str = "xy") -> ScheibenlagerEintrag:
        """Ein Lager bei ``ort`` -- heisst nicht ``lager``, weil die Liste so heisst."""
        return self._anlegen("lager", ScheibenlagerEintrag,
                             {"knoten": self._knoten(self.netz(), ort), "halt": halt}, "Lager")

    def last(self, ort: Ort, **felder: Any) -> ScheibenlastEintrag:
        """Eine Punktlast bei ``ort`` -- ``F_h`` nach rechts, ``F_v`` nach unten, in kN."""
        return self._anlegen("lasten", ScheibenlastEintrag,
                             {"knoten": self._knoten(self.netz(), ort), **felder}, "Last")
