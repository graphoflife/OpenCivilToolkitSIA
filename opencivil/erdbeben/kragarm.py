"""
opencivil/erdbeben/kragarm.py -- der Kern als Kragarm: Querkraft, Moment und Auslenkung.

VERANTWORTUNG:
Das ebene Modell des Ersatzkraftverfahrens (:mod:`.ersatzkraft`) je
Hauptrichtung: ein Kragarm, am Fuss eingespannt, die Kraefte waagrecht auf
der Hoehe der Decken. Querkraft und Moment unter jedem Geschoss
(:func:`querkraefte`, :func:`momente`) und, Geschoss fuer Geschoss, die
Auslenkung des Dachs unter den Gewichten (:func:`beitraege`) -- das u in
T_1 = 2 sqrt(u) (SIA 261:2020, 16.5.2.3, (40)). Die Herleitung schreibt
:mod:`.ersatzkraft`.

DIE AUSLENKUNG, nach dem Arbeitssatz::

    u = Integral M(z) a(z) / EI(z) dz      ueber die Hoehe, a(z) = H - z

M ist das Moment aus den Gewichten, a das aus einer Kraft 1 am Dach.
Zwischen zwei Decken greift keine Kraft an: beide laufen dort gerade, und EI
ist das des Geschosses -- es darf von Geschoss zu Geschoss wechseln, der
Kern oben duenner sein (Benutzer, 2026-11-27). Das Integral eines Geschosses
ist darum genau::

    Delta u_i = h_i / (6 EI_i) * (M_u (2 a_u + a_o) + M_o (a_u + 2 a_o))

u steht fuer unten, an der Decke darunter, o fuer oben, an seiner. Mit einem
EI ueber die ganze Hoehe gibt die Summe u = Summe W_i z_i^2 (3 H - z_i) /
(6 EI) -- so wurde bis 2026-11-27 gerechnet, mit allen Waenden ueber die
ganze Hoehe.

EINHEITEN:
SI-Basis: N, m, N m^2; u in m.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple


def querkraefte(kraefte: Sequence[float]) -> Tuple[float, ...]:
    """Je Geschoss, von unten, die Querkraft unter ihm: die Kraefte von dort bis oben."""
    return tuple(sum(kraefte[i:]) for i in range(len(kraefte)))


def momente(kraefte: Sequence[float], z: Sequence[float]) -> Tuple[float, ...]:
    """
    Je Geschoss, von unten, das Moment unter ihm, auf der Hoehe der Decke
    darunter: die Kraefte von dort bis oben, je mal ihr Abstand. Am Fuss ist
    es das Kippmoment M_0 -- der Kragarm ist dort eingespannt.
    """
    unten = (0.0, *z[:-1])
    return tuple(sum(F * (zj - unten[i]) for F, zj in zip(kraefte[i:], z[i:]))
                 for i in range(len(kraefte)))


@dataclass(frozen=True)
class Geschossbeitrag:
    """
    Was ein Geschoss zur Auslenkung des Dachs beitraegt -- SI. ``M`` ist das
    Moment aus den Gewichten, ``a`` das aus einer Kraft 1 am Dach, je unten
    und oben im Geschoss.
    """

    h: float
    EI: float
    M_u: float
    M_o: float
    a_u: float
    a_o: float

    @property
    def du(self) -> float:
        """Das Integral ueber das Geschoss -- genau, beide Momente laufen gerade."""
        return self.h / (6.0 * self.EI) * (self.M_u * (2.0 * self.a_u + self.a_o)
                                            + self.M_o * (self.a_u + 2.0 * self.a_o))


def beitraege(z: Sequence[float], W: Sequence[float],
              EI: Sequence[float]) -> Tuple[Geschossbeitrag, ...]:
    """
    Je Geschoss, von unten, sein Beitrag zur Auslenkung des Dachs: ``z`` die
    Hoehen der Decken ueber der Einspannung, ``W`` die Gewichte, waagrecht
    auf ihnen, ``EI`` die Biegesteifigkeit jedes Geschosses.
    """
    H = z[-1]
    unten = (0.0, *z[:-1])
    M = (*momente(W, z), 0.0)
    return tuple(Geschossbeitrag(h=z[i] - unten[i], EI=EI[i], M_u=M[i], M_o=M[i + 1],
                                 a_u=H - unten[i], a_o=H - z[i])
                 for i in range(len(z)))
