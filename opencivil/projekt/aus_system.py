"""
opencivil/projekt/aus_system.py -- was eine Querschnittsanalyse aus einem Balkensystem nimmt.

VERANTWORTUNG:
Das ebene oder raeumliche Balkensystem einer Querschnittsanalyse und seine
Staebe (:class:`AusSystemEintrag`): alle, deren Querschnitt diese Analyse
ist, oder gewaehlte (:class:`Stabwahl`). Je Kombination werden ihre
massgebenden Stellen Lastfaelle der Analyse (Plan vom 2026-11-27, Schritt
12) -- gebaut in :mod:`opencivil.projekt.aufbau.aus_system`, gewaehlt in
:mod:`opencivil.stabwerk.stellen`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from opencivil.core.wahl import Wahl
from opencivil.projekt.eintraege import Beschreibung


class Stabwahl(Wahl):
    """Welche Staebe des Systems zaehlen."""

    MIT_QUERSCHNITT = "mit_querschnitt"
    GEWAEHLT = "gewaehlt"

    @property
    def beschriftung(self) -> str:
        return {Stabwahl.MIT_QUERSCHNITT: "alle mit diesem Querschnitt",
                Stabwahl.GEWAEHLT: "gewählte"}[self]

    @property
    def erklaerung(self) -> str:
        return {
            Stabwahl.MIT_QUERSCHNITT: "Jeder Stab des Systems, dessen Querschnitt diese "
                                      "Querschnittsanalyse ist – auch einer, der später dazukommt",
            Stabwahl.GEWAEHLT: "Nur die Stäbe, die hier gewählt sind – mit welchem Querschnitt "
                               "auch immer",
        }[self]


@dataclass
class AusSystemEintrag(Beschreibung):
    """
    Das Balkensystem einer Analyse und seine Staebe -- ohne System keines:
    dann hat die Analyse nur ihre eigenen Lastfaelle.
    """

    system: str = ""
    """Die Kennung eines ebenen (``r1``) oder raeumlichen (``u1``) Balkensystems; leer: keines."""

    stabwahl: Stabwahl = Stabwahl.MIT_QUERSCHNITT
    staebe: List[str] = field(default_factory=list)
    """Mit :attr:`Stabwahl.GEWAEHLT` die Kennungen der Linien (``L3``); sonst ohne Belang."""

    def bezuege(self) -> List[str]:
        """Das System, dessen Schnittgroessen die Analyse liest -- oder keines."""
        return [self.system] if self.system else []
