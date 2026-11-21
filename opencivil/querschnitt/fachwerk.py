"""
opencivil/querschnitt/fachwerk.py -- das Fachwerk mit veraenderlicher Neigung.

VERANTWORTUNG:
Das Druckfeld eines Stegs mit Buegeln, an einer Stelle: was er bei einer
Neigung der Druckdiagonalen aufnimmt (:func:`fachwerk`), zwischen welchen
Neigungen gesucht wird (:data:`ALPHA_MIN`, :data:`ALPHA_MAX`, bei Normalzug
gehoben, :func:`druckfeldgrenzen`), mit welchem ``k_c`` (:data:`K_C`) --
und welche Neigung den groessten Widerstand gibt (:func:`guenstigste`).
Fuer die Buegel einer Platte (:mod:`opencivil.nachweis.querkraft_buegel`),
eine Schubwand des gezeichneten Querschnitts
(:mod:`opencivil.querschnitt.schubwaende`) und die Wendel eines Pfahls
(:mod:`opencivil.pfahl.innen_quer`).

Bis 2026-10-17 standen die beiden Funktionen beim Querkraftnachweis, und
die Schubwaende holten sie von dort. Bis 2026-11-21 standen die Grenzen und
``k_c`` bei der Platte, sieben Module holten sie dort, und die Suche stand
dreimal da, einmal je Nutzer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence, Tuple

#: Vorgabe fuer die Neigung der Druckdiagonalen, in Grad: 30° ist im
#: Normalfall die untere Grenze (SIA 262:2025, 4.3.3.3.3), 45° die obere der
#: Norm (4.3.3.3.2, Gl. (42)).
ALPHA_MIN = 30
ALPHA_MAX = 45

#: Bei einer Normalzugkraft steilt sich die Druckdiagonale auf. Beide Grenzen
#: werden dann auf mindestens diesen Wert gehoben (SIA 262:2025, 4.3.3.3.3).
ALPHA_ZUG = 40

#: Vorgabe fuer den Abminderungsbeiwert der Betondruckfestigkeit in der
#: Druckdiagonalen: der Wert fuer Stege, deren Druckfeld die Bewehrung schief
#: kreuzt (SIA 262:2025, 4.2.1.7).
K_C = 0.55

#: Wo die Grenzen der Neigung und k_c stehen -- fuer die Platte, die
#: Querschnittsanalyse und den Pfahl.
REFERENZ_ALPHA_MIN = "SIA 262:2025, 4.3.3.3.3"
REFERENZ_ALPHA_MAX = "SIA 262:2025, 4.3.3.3.2, (42)"
REFERENZ_K_C = "SIA 262:2025, 4.2.1.7"


@dataclass(frozen=True)
class Buegelpunkt:
    """
    Was bei einer bestimmten Neigung der Druckdiagonalen aufnehmbar ist.

    Bei der Platte in N/m, je Laufmeter wie ihr ``V_Ed``; bei einer Schubwand
    in N, fuer die ganze Wand.
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


def druckfeldgrenzen(alpha_min: int, alpha_max: int, zugkraft: bool) -> Tuple[int, int]:
    """
    Die beiden Grenzwinkel der Druckdiagonalen in Grad, angepasst an das
    Vorzeichen von ``N_Ed``.

    Bei Normalzug steilt sich die Druckdiagonale auf: ``alpha_min`` ist dann
    mindestens 40°, und ``alpha_max`` wird notfalls mitgehoben, damit der
    Bereich nicht leer wird (SIA 262:2025, 4.3.3.3.3). Bis 2026-11-14 wurde
    ``alpha_min`` auf genau 40° gesetzt -- auch von 42° herunter.
    """
    if not zugkraft:
        return alpha_min, alpha_max
    return max(alpha_min, ALPHA_ZUG), max(alpha_max, ALPHA_ZUG)


@dataclass(frozen=True)
class Neigungssuche:
    """Was :func:`guenstigste` findet."""

    alpha_min: int
    alpha_max: int
    """Die verwendeten Grenzen; bei Normalzug angehoben."""

    punkte: Tuple[Buegelpunkt, ...]
    """Der Widerstand je ganzem Grad zwischen den beiden."""

    massgebend: Buegelpunkt
    """Der Punkt mit dem groessten Widerstand."""


def guenstigste(punkt: Callable[[int], Buegelpunkt], *, alpha_min: int, alpha_max: int,
                zugkraft: bool) -> Neigungssuche:
    """
    Die Neigung mit dem groessten Widerstand, ganzgradig zwischen den
    Grenzen, die eine Normalzugkraft hebt (:func:`druckfeldgrenzen`).
    ``punkt`` ist das Fachwerk des Nutzers bei einer Neigung in Grad -- die
    Buegel einer Platte je Laufmeter, eine Schubwand, eine Wendel.
    Zwischenwerte sind eine Genauigkeit, die das Fachwerkmodell nicht
    hergibt.
    """
    von, bis = druckfeldgrenzen(alpha_min, alpha_max, zugkraft)
    punkte = tuple(punkt(alpha) for alpha in range(von, bis + 1))
    return Neigungssuche(alpha_min=von, alpha_max=bis, punkte=punkte,
                         massgebend=beste_neigung(punkte))
