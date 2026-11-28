"""
opencivil/projekt/mauerwerk.py -- eine Mauerwerkswand, wie die Oberfläche sie beschreibt.

VERANTWORTUNG:
Der :class:`MauerwerkEintrag`: eine Wand in der Ansicht, gezeichnet aus
Knoten -- ihr Umriss, Türen und Fenster mit dem Sturz darüber --, dazu ihr
Mauerwerk, ihre Dicke, wie sie gemauert ist und wie ihre Ränder gehalten
sind. Als speicherbare Datenklasse wie das Fachwerkmodell
(:mod:`opencivil.projekt.fachwerkmodell`), mit dem Baukasten, der ohne
Oberfläche zeichnet. Gerechnet wird in :mod:`opencivil.mauerwerk`.

ALLES HÄNGT AN KNOTEN:
Der Umriss der Wand und jede Öffnung sind Umrisse aus Knoten. Liegen zwei
Ecken genau aufeinander, teilen sie einen Knoten
(:mod:`opencivil.projekt.netz`): wer ihn verschiebt, verschiebt beide.

KOORDINATEN UND EINHEITEN:
x nach rechts, y nach oben, in m -- wie in der Decke. Die Dicke der Wand
und die Masse eines Sturzes in mm, wie man sie auf dem Plan liest.
Umgerechnet wird beim Bauen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Sequence, Union

from opencivil.core.einheiten import M, MM
from opencivil.mauerwerk.modell import Halterung, Mauerung, Seitenrand, Stossfugen, Sturzart
from opencivil.projekt.eintraege import BauteilEintrag, Beschreibung
from opencivil.projekt.lesen import bereich, lesen, materialfeld
from opencivil.projekt.netz import Netz, neue_kennung

#: Ein Ort im Baukasten: die Kennung eines Knotens oder ``(x, y)`` in m.
Ort = Union[str, Sequence[float]]

#: Womit die Kennungen der Teile einer Wand beginnen.
VORSILBEN = {"waende": "W", "oeffnungen": "O"}


@dataclass
class WandknotenEintrag(Beschreibung):
    """Ein Punkt der Wand, in m."""

    kennung: str = ""
    x: float = bereich(0.0, heisst="x", einheit=M)
    y: float = bereich(0.0, heisst="y", einheit=M)


@dataclass
class WandEintrag(Beschreibung):
    """Der Umriss der Wand in der Ansicht."""

    kennung: str = ""
    knoten: List[str] = field(default_factory=list)


@dataclass
class OeffnungEintrag(Beschreibung):
    """Eine Türe oder ein Fenster, mit dem Sturz darüber."""

    kennung: str = ""
    knoten: List[str] = field(default_factory=list)
    sturz: Sturzart = Sturzart.BETON
    h_St: float = bereich(200.0, heisst="Sturzhöhe h_St", einheit=MM, ueber=0.0)
    a: float = bereich(150.0, heisst="Auflagerlänge a", einheit=MM, ueber=0.0)
    """Wie weit der Sturz auf jeder Seite auf dem Mauerwerk liegt."""


@dataclass
class MauerwerkEintrag(BauteilEintrag):
    """
    Eine Wand aus Mauerwerk. Ohne Regeln, die das ganze Projekt aufhielten:
    was ihrer Zeichnung fehlt, steht in ihren Meldungen, und die anderen
    Bauteile rechnen weiter.
    """

    BEZEICHNUNG = "Mauerwerk"
    STAMM = "Wand"
    ERSTE_MATERIALIEN = {"material": "mauerwerk"}

    kennung: str
    name: str
    material: str = materialfeld("mauerwerk")
    t: float = bereich(150.0, heisst="Dicke t_w", einheit=MM, ueber=0.0)
    mauerung: Mauerung = Mauerung.EINSTEIN
    stossfugen: Stossfugen = Stossfugen.NICHT_VOLLFUGIG
    kopf: Halterung = Halterung.GELENKIG
    fuss: Halterung = Halterung.GELENKIG
    links: Seitenrand = Seitenrand.FREI
    rechts: Seitenrand = Seitenrand.FREI
    knoten: List[WandknotenEintrag] = field(default_factory=list)
    waende: List[WandEintrag] = field(default_factory=list)
    oeffnungen: List[OeffnungEintrag] = field(default_factory=list)
    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    def materialien(self) -> List[str]:
        return [self.material] if self.material else []

    def lagen(self) -> dict:
        """Kennung -> ``(x, y)`` jedes Knotens, in m."""
        return {k.kennung: (k.x, k.y) for k in self.knoten}

    # -- Zeichnen ohne Oberfläche -------------------------------------------

    def netz(self) -> Netz:
        return Netz(self, neu=lambda kennung, x, y: WandknotenEintrag(kennung, x, y),
                    achsen=("x", "y"))

    def _knoten(self, netz: Netz, ort: Ort) -> str:
        return ort if isinstance(ort, str) else netz.an(float(ort[0]), float(ort[1]))

    def _anlegen(self, liste: str, cls: type, felder: dict, wo: str) -> Any:
        eintrag = lesen(cls, felder, f"Mauerwerk '{self.name}': {wo}",
                        cls(kennung=neue_kennung(self, VORSILBEN[liste],
                                                 (e.kennung for e in getattr(self, liste)))))
        getattr(self, liste).append(eintrag)
        return eintrag

    def wand(self, ecken: Sequence[Ort]) -> WandEintrag:
        """Der Umriss der Wand mit diesen Ecken."""
        netz = self.netz()
        return self._anlegen("waende", WandEintrag,
                             {"knoten": [self._knoten(netz, e) for e in ecken]}, "Wand")

    def oeffnung(self, ecken: Sequence[Ort], **felder: Any) -> OeffnungEintrag:
        """Eine Öffnung mit diesen Ecken -- ``sturz``, ``h_St`` und ``a`` in mm als Stichwort."""
        netz = self.netz()
        return self._anlegen("oeffnungen", OeffnungEintrag,
                             {"knoten": [self._knoten(netz, e) for e in ecken], **felder},
                             "Öffnung")


def rechteck(x0: float, y0: float, x1: float, y1: float) -> List[Sequence[float]]:
    """Die vier Ecken eines Rechtecks, wie die Werkzeuge «Wand» und «Öffnung» sie setzen."""
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
