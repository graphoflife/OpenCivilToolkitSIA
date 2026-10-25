"""
opencivil/querschnitt/biegung.py -- wie ein gezeichneter Querschnitt biegt.

VERANTWORTUNG:
Ein gezeichneter Querschnitt biegt schief (:data:`SCHIEF`): unter reiner
Biegung kippt die Nulllinie, bis kein Moment um die andere Achse bleibt, und
jede Seite kann gezogen werden. Oder er biegt «einachsig» um y
(:data:`EINACHSIG`): die Nulllinie bleibt waagrecht, ``M_z`` und ``V_y``
zaehlen nicht, und gezogen wird nur unten oder oben -- wie bei der Platte.

Was davon abhaengt, steht hier, je einmal: welche Momente und Querkraefte
zaehlen, der Betrag des Moments, welche Seiten ein Nachweis ziehen laesst,
ob die Zugrichtung feststeht und welcher Bruchzustand zu einer Einwirkung
gehoert. Gewaehlt wird einmal, im Aufbau der Analyse
(:attr:`~opencivil.querschnitt.analyse.Querschnittsanalyse.biegung`). Bis
2026-10-25 fragten 17 Dateien ein ``einachsig`` ab, und die Regel fuer den
Bruchzustand stand dreimal da, der Betrag des Moments viermal.

Wo eine Herleitung je Art anders lautet -- die Spannung am ungerissenen
Querschnitt, der Riss der Spannung-Dehnung-Analyse --, fragt sie
:attr:`Biegung.einachsig`.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from opencivil.querschnitt.zugseite import UM_Y, Zugseite


class Biegung(ABC):
    """Wie ein gezeichneter Querschnitt biegt -- siehe Dateikopf."""

    einachsig: bool
    """Ob die Nulllinie waagrecht bleibt -- fuer die Herleitungen, die je Art anders lauten."""

    zugseiten: Tuple[Zugseite, ...]
    """
    Die Seiten, die je ein Nachweis ziehen laesst -- einachsig nur unten und
    oben, um z wird dann nicht nachgewiesen. Ihre Namen, «Zug unten», sind
    die der Faelle; die Kennungen «Zug_unten».
    """

    @abstractmethod
    def momente(self, M_y: float, M_z: float) -> Tuple[Tuple[str, float], ...]:
        """Die Momente, die zaehlen, je mit ihrer Achse: ``(("y", M_y), ("z", M_z))``."""

    def wirkt(self, M_y: float, M_z: float) -> Tuple[float, float]:
        """``(M_y, M_z)``, wie nachgewiesen -- was nicht zaehlt, ist null."""
        zaehlt = dict(self.momente(M_y, M_z))
        return zaehlt.get("y", 0.0), zaehlt.get("z", 0.0)

    def betrag(self, M_y: float, M_z: float) -> float:
        """Der Betrag des Moments, das zaehlt -- einachsig ``|M_y|``."""
        return math.hypot(*self.wirkt(M_y, M_z))

    @abstractmethod
    def querkraft_y(self, V_y: float) -> float:
        """Die Querkraft in y, wie nachgewiesen -- einachsig null."""

    @abstractmethod
    def neigung(self, M_y: float) -> Optional[float]:
        """
        Die Zugrichtung, wenn sie feststeht: einachsig die der Seite, die
        ``M_y`` zieht -- bei ``M_y = 0`` die untere. Sonst ``None``: dann wird
        sie gesucht.
        """

    def bruchpunkt(self, q: Any, N: float, M_y: float, M_z: float):
        """
        Der Bruchzustand des Querschnitts ``q`` bei ``N``, der zum Moment
        ``(M_y, M_z)`` gehoert: auf dem Faecher der festen Zugrichtung, sonst
        in der Richtung des Moments gesucht
        (:meth:`~opencivil.querschnitt.interaktion.Querschnitt.in_richtung`).
        ``None``, wenn N jenseits der reinen Zug- oder Druckkraft liegt.
        """
        psi = self.neigung(M_y)
        if psi is None:
            return q.in_richtung(N, M_y, M_z)
        return q.bei_normalkraft(psi, N)

    def bei_reiner_biegung(self, q: Any, seite: Zugseite):
        """Der Bruchzustand bei N = 0, der diese Seite zieht."""
        return self.bruchpunkt(q, 0.0, *seite.moment)


class Schief(Biegung):
    """Schiefe Biegung: die Nulllinie kippt, jede Seite kann gezogen werden."""

    einachsig = False
    zugseiten = tuple(Zugseite)

    def momente(self, M_y: float, M_z: float) -> Tuple[Tuple[str, float], ...]:
        return (("y", M_y), ("z", M_z))

    def querkraft_y(self, V_y: float) -> float:
        return V_y

    def neigung(self, M_y: float) -> Optional[float]:
        return None


class Einachsig(Biegung):
    """Biegung um y allein: die Nulllinie bleibt waagrecht, M_z und V_y zaehlen nicht."""

    einachsig = True
    zugseiten = UM_Y

    def momente(self, M_y: float, M_z: float) -> Tuple[Tuple[str, float], ...]:
        return (("y", M_y),)

    def querkraft_y(self, V_y: float) -> float:
        return 0.0

    def neigung(self, M_y: float) -> Optional[float]:
        return Zugseite.aus_moment(M_y).psi


SCHIEF = Schief()
EINACHSIG = Einachsig()
