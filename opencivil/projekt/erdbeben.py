"""
opencivil/projekt/erdbeben.py -- ein Gebaeude im Erdbeben, wie die Oberflaeche es beschreibt.

VERANTWORTUNG:
Der :class:`ErdbebenEintrag`: Standort und Bauwerksklasse, die
Verhaltensbeiwerte je Richtung, woher die Grundschwingzeit kommt, ob Grund-
und Aufriss regelmaessig sind -- dazu die Geschosse
(:class:`GeschossEintrag`, von unten) und die Tragwaende
(:class:`TragwandEintrag`), je aus einer Querschnittsanalyse des Projekts.
Gerechnet wird in :mod:`opencivil.erdbeben.ersatzkraft`.

Die Vorgaben der Felder sind gesetzt, damit sich gleich etwas rechnen
laesst, und stehen in keiner Quelle: Zone Z1b, Baugrundklasse C,
Bauwerksklasse I, q = 1.5 -- der kleinste Wert fuer Stahlbeton ohne
Duktilitaet (SIA 262:2025, Tabelle 14) --, Grund- und Aufriss regelmaessig,
ein Geschoss von 3 m ohne Last und eine Wand ohne Querschnittsanalyse. Ohne
Last rechnet ein neues Gebaeude nichts, wie ein neuer Lastfall. psi_2 = 0.3
gilt fuer Wohn- und Bueroflaechen (SIA 260:2013, Anhang A, Tabelle 2), eta_EI
= 0.5 ist nach Vorgabe, nicht nachgeschlagen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Union

from opencivil.core.einheiten import KN, M, S
from opencivil.erdbeben.ersatzkraft import (
    Baugrundklasse, Bauwerksklasse, Erdbebenzone, Schwingzeit, Wandlage,
)
from opencivil.projekt.eintraege import BauteilEintrag, Beschreibung
from opencivil.projekt.lesen import bereich


@dataclass
class GeschossEintrag(Beschreibung):
    """Ein Geschoss ueber der Einspannung, von unten gezaehlt: Hoehe und Lasten."""

    IM_ORT = "Geschoss"

    name: str
    h: float = bereich(3.0, heisst="Höhe h", einheit=M, ueber=0.0)
    """Hoehe des Geschosses in m, von Decke zu Decke -- das unterste ab der Einspannung."""

    G_k: float = bereich(0.0, heisst="Ständige Last G_k", einheit=KN, ab=0.0)
    """Die staendige Last, die mit der Decke des Geschosses schwingt, in kN."""

    Q_k: float = bereich(0.0, heisst="Nutzlast Q_k", einheit=KN, ab=0.0)
    """Die Nutzlast des Geschosses in kN."""

    psi_2: float = bereich(0.3, heisst="ψ₂", ab=0.0, bis=1.0)
    """Der Beiwert fuer den quasi-staendigen Anteil der Nutzlast."""


@dataclass
class TragwandEintrag(Beschreibung):
    """
    Eine oder ``n`` gleiche Tragwaende: ihr Querschnitt aus einer
    Querschnittsanalyse, wie sie im Grundriss liegt, und welcher Anteil der
    ungerissenen Steifigkeit gilt.
    """

    IM_ORT = "Wand"

    name: str
    analyse: str = ""
    """Die Kennung der Querschnittsanalyse -- leer, solange keine gewaehlt ist."""

    lage: Wandlage = Wandlage.NULL
    """0 Grad: y der Analyse liegt in x des Gebaeudes; 90 Grad: in y."""

    n: int = bereich(1, heisst="Anzahl n", ab=1)
    """Wie viele gleiche Waende es gibt."""

    eta_EI: float = bereich(0.5, heisst="η_EI", ueber=0.0, bis=1.0)
    """Der Anteil der ungerissenen Biegesteifigkeit, der gilt."""


@dataclass
class ErdbebenEintrag(BauteilEintrag):
    """Ein Gebaeude im Erdbeben, nach dem Ersatzkraftverfahren (SIA 261:2020, 16.5.2)."""

    BEZEICHNUNG = "Erdbeben"
    STAMM = "Gebäude"

    kennung: str
    name: str

    zone: Erdbebenzone = Erdbebenzone.Z1B
    baugrund: Baugrundklasse = Baugrundklasse.C
    bauwerksklasse: Bauwerksklasse = Bauwerksklasse.I

    q_x: float = bereich(1.5, heisst="Verhaltensbeiwert q_x", ab=1.0)
    q_y: float = bereich(1.5, heisst="Verhaltensbeiwert q_y", ab=1.0)

    schwingzeit: Schwingzeit = Schwingzeit.WAENDE
    """Aus den Waenden (40) oder von Hand."""

    T1_x: float = bereich(0.5, heisst="Grundschwingzeit T₁ in x", einheit=S, ueber=0.0)
    T1_y: float = bereich(0.5, heisst="Grundschwingzeit T₁ in y", einheit=S, ueber=0.0)
    """Nur von Hand: die Grundschwingzeiten in s."""

    grundriss_regelmaessig: bool = True
    """Ob der Grundriss die Kriterien von 16.5.1.3 erfuellt -- das sagt der Benutzer."""

    aufriss_regelmaessig: bool = True
    """Ob der Aufriss die Kriterien von 16.5.1.4 erfuellt; das Gewicht prueft der Kern dazu."""

    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    geschosse: List[GeschossEintrag] = field(default_factory=list)
    """Von unten nach oben, ab der Einspannung."""

    waende: List[TragwandEintrag] = field(default_factory=list)

    @classmethod
    def neu(cls, kennung: str, name: str) -> "ErdbebenEintrag":
        """Ein frisches Gebaeude, wie die Oberflaeche es anlegt: ein Geschoss, eine Wand."""
        return cls(kennung=kennung, name=name, geschosse=[GeschossEintrag(name="Geschoss 1")],
                   waende=[TragwandEintrag(name="Wand 1")])

    def bezuege(self) -> List[str]:
        """Die Querschnittsanalysen, deren Querschnitt eine Wand nimmt."""
        return sorted({w.analyse for w in self.waende if w.analyse})

    def geschoss(self, name: str, *, h: float, G_k: float, Q_k: float = 0.0,
                 psi_2: float = 0.3) -> GeschossEintrag:
        """Ein Geschoss oben anfuegen -- h in m, Lasten in kN."""
        eintrag = GeschossEintrag(name=name, h=h, G_k=G_k, Q_k=Q_k, psi_2=psi_2)
        self.geschosse.append(eintrag)
        return eintrag

    def wand(self, name: str, analyse: str, *, lage: Union[Wandlage, str] = Wandlage.NULL,
             n: int = 1, eta_EI: float = 0.5) -> TragwandEintrag:
        """
        Eine Wand anfuegen -- ``analyse`` ist die Kennung einer
        Querschnittsanalyse, ``lage`` ein Wort wie in der Datei: ``"0"``
        oder ``"90"``.
        """
        eintrag = TragwandEintrag(name=name, analyse=analyse, lage=lage, n=n, eta_EI=eta_EI)
        self.waende.append(eintrag)
        return eintrag
