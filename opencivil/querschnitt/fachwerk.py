"""
opencivil/querschnitt/fachwerk.py -- das Fachwerk mit veraenderlicher Neigung.

VERANTWORTUNG:
Was ein Steg mit Buegeln bei einer Neigung der Druckdiagonalen aufnimmt
(:func:`fachwerk`), und welche Neigung den groessten Widerstand gibt
(:func:`beste_neigung`) -- fuer die Buegel einer Platte
(:mod:`opencivil.nachweis.querkraft`) wie fuer eine Schubwand des
gezeichneten Querschnitts (:mod:`opencivil.querschnitt.schubwaende`). Zwei
reine Funktionen, darum im Querschnitt: bis 2026-10-17 standen sie beim
Querkraftnachweis, und die Schubwaende holten sie von dort.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Buegelpunkt:
    """
    Was bei einer bestimmten Neigung der Druckdiagonalen aufnehmbar ist.

    Beide Anteile in N/m, also je Laufmeter -- wie ``V_Ed``.
    """

    alpha: int
    """Neigung der Druckdiagonalen in Grad."""

    V_Rd_s: float
    """Bügel: waechst, je flacher die Diagonale liegt."""

    V_Rd_c: float
    """Druckdiagonale: groesst bei 45°, faellt nach beiden Seiten."""

    @property
    def V_Rd(self) -> float:
        """Massgebend ist der kleinere der beiden -- eines von beiden versagt."""
        return min(self.V_Rd_s, self.V_Rd_c)


def fachwerk(
    *, alpha: int, a_sw_s: float, z: float, b_w: float,
    f_yd: float, f_cd: float, k_c: float,
) -> Buegelpunkt:
    """
    Fachwerkmodell mit veraenderlicher Neigung der Druckdiagonalen -- fuer die
    Buegel einer Platte wie fuer eine Schubwand der Querschnittsanalyse.

    Alles in SI-Basis: Flaechen in m^2, Laengen in m, Festigkeiten in Pa::

        V_Rd,s = A_sw/s · z · f_yd · cot(alpha)
        V_Rd,c = b_w · z · k_c · f_cd · sin(alpha) · cos(alpha)

    ``A_sw/s`` ist der Bewehrungsgehalt je Laenge in Laengsrichtung, ``z``
    der Hebelarm der inneren Kraefte, ``b_w`` die Breite des Stegs.
    """
    bogen = math.radians(alpha)
    return Buegelpunkt(
        alpha=alpha,
        V_Rd_s=a_sw_s * z * f_yd / math.tan(bogen),
        V_Rd_c=b_w * z * k_c * f_cd * math.sin(bogen) * math.cos(bogen),
    )


def beste_neigung(punkte: Sequence[Buegelpunkt]) -> Buegelpunkt:
    """
    Die Neigung mit dem groessten Widerstand.

    ``V_Rd,s`` waechst mit flacherer Diagonale, ``V_Rd,c`` faellt dabei --
    das Kleinere von beiden hat sein Groesstes dort, wo sich die beiden
    Aeste treffen. Gesucht wird ganzgradig; bei Gleichstand gilt die
    steilere Neigung, weil sie die Druckdiagonale weniger beansprucht.
    """
    return max(punkte, key=lambda q: (q.V_Rd, q.alpha))
