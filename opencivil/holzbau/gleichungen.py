"""
opencivil/holzbau/gleichungen.py -- die Gleichungen von SIA 265:2012, 4.2, ohne Rechenwerk.

VERANTWORTUNG:
Die Zahlen der Nachweise eines Holzquerschnitts und eines Holzstabs, in
N/mm², mm und ohne Einheit -- die Herleitungen schreiben
:mod:`opencivil.nachweis.qa_holz` und
:mod:`opencivil.nachweis.qa_holz_stabilitaet`, mit denselben Funktionen:

* der Hoehenbeiwert ``k_h`` des Brettschichtholzes (3.4.2.3, (5));
* Biegung und Normalkraft: (6) und (10) allein, (14) ohne Normalkraft, (21)
  mit Zug, (22) mit Druck (:func:`biegung_normalkraft`);
* Schub und Torsion: (23), (24) und (25) (:func:`schub_torsion`);
* Knicken: die relative Schlankheit nach (34) und ``k_c`` nach (30) und
  (31); Kippen: ``λ_rel,m`` nach (40) mit (41) und ``k_m`` nach (39); je
  Achse (29) mit Druck allein, (37) mit Druck und Biegung, (38) mit Biegung
  allein (:func:`stabachse`).

DER ERFUELLUNGSGRAD:
Wie beim Stahl: die Normalkraft bleibt, Momente und Querkraefte wachsen mit
``λ``, bis die Gleichung aufgeht -- ``α = λ``. Ohne Moment, oder wo schon
die Normalkraft allein nicht traegt, ist es ihr Verhaeltnis, ``f/σ``. In
(25) wachsen Querkraft und Torsion zusammen.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

REFERENZ_K_H = "SIA 265:2012, 3.4.2.3, (5)"
REFERENZ_6 = "SIA 265:2012, 4.2.1.1, (6)"
REFERENZ_10 = "SIA 265:2012, 4.2.2.1, (10)"
REFERENZ_14 = "SIA 265:2012, 4.2.3.1, (14)"
REFERENZ_21 = "SIA 265:2012, 4.2.4.1, (21)"
REFERENZ_22 = "SIA 265:2012, 4.2.4.2, (22)"
REFERENZ_23 = "SIA 265:2012, 4.2.5.1, (23)"
REFERENZ_24 = "SIA 265:2012, 4.2.5.2, (24)"
REFERENZ_25 = "SIA 265:2012, 4.2.5.3, (25)"
REFERENZ_29 = "SIA 265:2012, 4.2.8.1, (29)"
REFERENZ_K_C = "SIA 265:2012, 4.2.8.2, (30) und (31); 4.2.8.3"
REFERENZ_SCHLANKHEIT = "SIA 265:2012, 4.2.8.4"
REFERENZ_LAMBDA = "SIA 265:2012, 4.2.8.4, (34); Anhang B"
REFERENZ_37 = "SIA 265:2012, 4.2.8.5, (37)"
REFERENZ_38 = "SIA 265:2012, 4.2.9.1, (38)"
REFERENZ_K_M = "SIA 265:2012, 4.2.9.2, (39)"
REFERENZ_KIPPEN = "SIA 265:2012, 4.2.9.3, (40) und (41)"

#: Je Gleichung ihre Stelle.
REFERENZEN = {"(6)": REFERENZ_6, "(10)": REFERENZ_10, "(14)": REFERENZ_14,
              "(21)": REFERENZ_21, "(22)": REFERENZ_22, "(23)": REFERENZ_23,
              "(24)": REFERENZ_24, "(25)": REFERENZ_25, "(29)": REFERENZ_29,
              "(37)": REFERENZ_37, "(38)": REFERENZ_38}

#: Ab dieser Hoehe in mm gilt k_h = 1 (3.4.2.3).
K_H_AB = 600.0

#: Groesser wird k_h nicht (5).
K_H_HOECHSTENS = 1.1

#: Bis zu dieser relativen Schlankheit knickt ein Stab nicht: k_c = 1 (4.2.8.2).
LAMBDA_0 = 0.3


def k_h(h: float) -> float:
    """``(600/h)^0.1 ≤ 1.1`` bei Brettschichtholz unter 600 mm Hoehe, ``h`` in mm -- sonst 1."""
    return 1.0 if h >= K_H_AB else min((K_H_AB / h) ** 0.1, K_H_HOECHSTENS)


# ===========================================================================
# Biegung und Normalkraft
# ===========================================================================


@dataclass(frozen=True)
class Biegung:
    """
    Biegung und Normalkraft in einem Lastfall: welche Gleichung, ihre beiden
    Anteile und der Erfuellungsgrad.
    """

    gleichung: str
    """``(6)``, ``(10)``, ``(14)``, ``(21)`` oder ``(22)``."""

    n: float
    """Der Anteil der Normalkraft: ``σ/f``, in (22) ``(σ_c/f_c)²``."""

    m: float
    """Der Anteil der Biegung: ``σ_m,y/f_m,y + σ_m,z/f_m,z``."""

    alpha: float

    @property
    def nur_normalkraft(self) -> bool:
        """Ob ``α`` das Verhaeltnis der Normalkraft ist: ohne Moment, oder sie traegt nicht."""
        return self.m == 0.0 or self.n >= 1.0


def biegung_normalkraft(sigma_N: float, sigma_m_y: float, sigma_m_z: float, *, f_t: float,
                        f_c: float, f_m_y: float, f_m_z: float) -> Optional[Biegung]:
    """
    Die Gleichung, die der Lastfall braucht -- ``sigma_N`` positiv Zug, die
    Biegespannungen als Betrag; ``None`` ohne Normalkraft und Moment.
    """
    m = sigma_m_y / f_m_y + sigma_m_z / f_m_z
    if sigma_N > 0.0:
        verhaeltnis = sigma_N / f_t
        gleichung, n = ("(21)" if m else "(6)"), verhaeltnis
    elif sigma_N < 0.0:
        verhaeltnis = -sigma_N / f_c
        gleichung, n = ("(22)", verhaeltnis ** 2) if m else ("(10)", verhaeltnis)
    elif m:
        verhaeltnis, gleichung, n = 0.0, "(14)", 0.0
    else:
        return None
    if m == 0.0 or n >= 1.0:
        return Biegung(gleichung, n, m, 1.0 / verhaeltnis)
    return Biegung(gleichung, n, m, (1.0 - n) / m)


# ===========================================================================
# Schub und Torsion
# ===========================================================================


@dataclass(frozen=True)
class Schub:
    """Schub und Torsion in einem Lastfall: welche Gleichung, ihre Anteile, der Erfuellungsgrad."""

    gleichung: str
    """``(23)``, ``(24)`` oder ``(25)``."""

    v: float
    """``τ_d/f_v,d`` -- in (25) im Quadrat."""

    t: float
    """``τ_tor,d/f_v,d``."""

    alpha: float


def schub_torsion(tau: float, tau_tor: float, f_v: float) -> Optional[Schub]:
    """
    (23) ohne Torsion, (24) ohne Querkraft, sonst (25) -- als Betraege;
    ``None`` ohne beides. In (25) wachsen beide mit ``λ``:
    ``λ·t + λ²·v² = 1``.
    """
    v, t = tau / f_v, tau_tor / f_v
    if v == 0.0 and t == 0.0:
        return None
    if t == 0.0:
        return Schub("(23)", v, t, 1.0 / v)
    if v == 0.0:
        return Schub("(24)", v, t, 1.0 / t)
    return Schub("(25)", v, t, (-t + math.sqrt(t * t + 4.0 * v * v)) / (2.0 * v * v))


# ===========================================================================
# Knicken und Kippen
# ===========================================================================


def lambda_rel(lam: float, f_c_0_k: float, E_0_05: float) -> float:
    """(34): ``λ/π · √(f_c,0,k/E_0,05)``."""
    return lam / math.pi * math.sqrt(f_c_0_k / E_0_05)


def k_c(lambda_rel_: float, beta_c: float) -> float:
    """(30) mit (31) -- eins bis ``λ_rel = 0.3``."""
    if lambda_rel_ <= LAMBDA_0:
        return 1.0
    k = 0.5 * (1.0 + beta_c * (lambda_rel_ - LAMBDA_0) + lambda_rel_ ** 2)
    return 1.0 / (k + math.sqrt(k * k - lambda_rel_ ** 2))


def sigma_m_crit(a: float, b: float, h: float, E_0_05: float) -> float:
    """(41): das Rechteck ``b × h`` zwischen Halterungen im Abstand ``a``, in mm und N/mm²."""
    return 0.75 * E_0_05 * b * b / (a * h)


def lambda_rel_m(f_m_k: float, sigma_crit: float) -> float:
    """(40): ``√(f_m,k/σ_m,crit)``."""
    return math.sqrt(f_m_k / sigma_crit)


def k_m(lambda_rel_m_: float) -> float:
    """(39): eins bis 0.75, dann eine Gerade bis 1.4, darueber ``1/λ²``."""
    if lambda_rel_m_ <= 0.75:
        return 1.0
    if lambda_rel_m_ <= 1.4:
        return 1.56 - 0.75 * lambda_rel_m_
    return 1.0 / lambda_rel_m_ ** 2


@dataclass(frozen=True)
class Stabachse:
    """
    Der Nachweis eines Stabs fuer eine Hauptachse: (29) mit Druck allein,
    (37) mit Druck und Biegung, (38) mit Biegung allein -- die Anteile und
    der Erfuellungsgrad.
    """

    gleichung: str
    druck: float
    """``σ_c,0,d/(k_c·f_c,0,d)`` -- null in (38)."""

    biegung: float
    """``σ_m,d/(k_m·f_m,d)``."""

    alpha: float

    @property
    def nur_druck(self) -> bool:
        """Ob ``α`` das Verhaeltnis der Druckkraft ist: ohne Moment, oder sie traegt nicht."""
        return self.biegung == 0.0 or self.druck >= 1.0


def stabachse(sigma_c: float, sigma_m: float, *, f_c: float, f_m: float, k_c_: float = 1.0,
              k_m_: float = 1.0) -> Optional[Stabachse]:
    """
    Der Nachweis fuer eine Achse, ``sigma_c`` als Betrag des Drucks: (29)
    ohne Moment, (37) mit, (38) ohne Druck. ``None`` ohne beides. Die Achsen
    gelten je fuer sich (4.2.8.5).
    """
    druck = sigma_c / (k_c_ * f_c)
    biegung = sigma_m / (k_m_ * f_m)
    if druck == 0.0 and biegung == 0.0:
        return None
    gleichung = "(38)" if not druck else "(37)" if biegung else "(29)"
    if biegung == 0.0 or druck >= 1.0:
        return Stabachse(gleichung, druck, biegung, 1.0 / druck)
    return Stabachse(gleichung, druck, biegung, (1.0 - druck) / biegung)
