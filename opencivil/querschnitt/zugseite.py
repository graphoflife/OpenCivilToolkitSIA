"""
opencivil/querschnitt/zugseite.py -- welche Seite ein Moment zieht.

VERANTWORTUNG:
Die Zugseite eines gezeichneten Querschnitts: unten, oben, links oder
rechts -- dazu die Zugrichtung als Winkel, die Achse, um die gebogen wird,
und wie die beiden Raender heissen. Eine Wahl fuer sich, in einem eigenen
Modul: die Beschreibung des Projekts, die Nachweise und die Analysen fragen
sie, und keiner von ihnen soll dafuer die Spannung-Dehnung-Analyse laden.
Bis 2026-10-17 stand sie in der Schnittanalyse des gezeichneten Querschnitts.
"""

from __future__ import annotations

import math
from typing import Tuple

from opencivil.core.wahl import Wahl


class Zugseite(Wahl):
    """Die Seite, die ein positives Moment zieht -- und die Richtung, die dazu gehoert."""

    UNTEN = "unten"
    OBEN = "oben"
    LINKS = "links"
    RECHTS = "rechts"

    @property
    def beschriftung(self) -> str:
        return f"Zug {self.value}"

    @property
    def psi(self) -> float:
        """Die Zugrichtung als Winkel, wie :class:`~opencivil.querschnitt.interaktion.Querschnitt` sie nimmt."""
        return {Zugseite.UNTEN: -math.pi / 2.0, Zugseite.OBEN: math.pi / 2.0,
                Zugseite.LINKS: math.pi, Zugseite.RECHTS: 0.0}[self]

    @property
    def moment(self) -> Tuple[float, float]:
        """
        Ein Moment von eins, das diese Seite zieht, als ``(M_y, M_z)``: M_y > 0
        zieht unten, M_z > 0 links -- wie
        :meth:`~opencivil.querschnitt.interaktion.Querschnitt.neigung_fuer`.
        """
        return {Zugseite.UNTEN: (1.0, 0.0), Zugseite.OBEN: (-1.0, 0.0),
                Zugseite.LINKS: (0.0, 1.0), Zugseite.RECHTS: (0.0, -1.0)}[self]

    @property
    def um_y(self) -> bool:
        """Ob die Biegung um die y-Achse geht -- Zug unten oder oben."""
        return self in (Zugseite.UNTEN, Zugseite.OBEN)

    @property
    def raender(self) -> Tuple[str, str]:
        """Wie die beiden Raender heissen: der gedrueckte und der gezogene."""
        return {Zugseite.UNTEN: ("oben", "unten"), Zugseite.OBEN: ("unten", "oben"),
                Zugseite.LINKS: ("rechts", "links"),
                Zugseite.RECHTS: ("links", "rechts")}[self]
