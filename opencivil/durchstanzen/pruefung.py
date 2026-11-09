"""
opencivil/durchstanzen/pruefung.py -- was der Durchstanznachweis rechnet, ohne Herleitung.

VERANTWORTUNG:
Die Rechnung an einem Nachweisschnitt (:class:`Schnittpruefung`) und mit einer
Durchstanzbewehrung (:class:`Leistenpruefung`), je einmal. Die Suche nach
der Bewehrung und dem Stahlpilz fragt ihre Ergebnisse
(:mod:`.mit_bewehrung`), die Herleitung schreibt dieselben Zahlen
(:mod:`.herleitung`). Bis 2026-11-09 stand jede Bedingung zweimal, stumm für
die Suche und laut für die Herleitung, und der Schnitt um die Stütze, um die
Leisten und um den Pilz hatte je sein eigenes Werkzeug.

DIE GLEICHUNGEN (SIA 262:2025)::

    u        = k_e · u_red                                  4.3.6.2.3
    V_d,red  = V_d − q_d · A                                4.3.6.2.6
    V_Rd,c   = k_r · τ_cd · d_v · u                         (58)
    V_Rd,max = min[k_sys · k_r; 3.5] · τ_cd · d_v · u       (70), 4.3.6.5.9
    V_Rd,s   = ΣA_sw · k_e · σ_sd ≥ V_d − V_Rd,c            (66), (68)
    σ_sd     = E_s·ψ/6 · (1 + f_ctm/f_yd · d/⌀_sw) ≤ f_yd   (69)
    ΣA_sw · k_e · f_yd ≥ V_d / 2                            (67)

Im äusseren Schnitt (4.3.6.5.10) gilt (58) mit d_v,out. Die Anker stehen
senkrecht, sin β = 1.

EINHEITEN:
SI-Basis; Kräfte in N.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from opencivil.durchstanzen import produkte
from opencivil.durchstanzen.bewehrung import Vorschlag
from opencivil.durchstanzen.produkte import Stahlpilz
from opencivil.durchstanzen.schnitt import Auswertung, Nachweisschnitt, Punkt


def widerstand(k_r: float, tau_cd: float, d_v: float, u: float) -> float:
    """Gleichung (58)."""
    return k_r * tau_cd * d_v * u


def druckdiagonale(k_sys: float, k_r: float, tau_cd: float, d_v: float, u: float) -> float:
    """Gleichung (70), mit dem Faktor des Produkts anstelle der 2 (4.3.6.5.9)."""
    return min(k_sys * k_r, produkte.GRENZE) * tau_cd * d_v * u


def spannung(E_s: float, psi: float, f_ctm: float, f_yd: float, d: float, phi: float) -> float:
    """σ_sd nach Gleichung (69)."""
    return min(E_s * psi / 6.0 * (1.0 + f_ctm / f_yd * d / phi), f_yd)


@dataclass(frozen=True)
class Schnittpruefung:
    """
    Ein Nachweisschnitt und was aus ihm folgt: der wirksame Umfang, die
    Fläche darin, die Querkraft, die ihn kreuzt, und die Widerstände an ihm.
    Derselbe um die Stütze, um die äussersten Anker (Figur 26, mit d_v,out)
    und um einen Stahlpilz (4.3.6.6.2, mit seinem d_v).
    """

    schnitt: Nachweisschnitt
    d_v: float
    k_e: float
    V_d: float
    """Die Auflagerkraft."""

    q_d: float
    """Die Flächenlast, die innerhalb des Schnitts abgezogen wird."""

    @property
    def auswertung(self) -> Auswertung:
        return self.schnitt.massgebend

    @property
    def u_red(self) -> float:
        """Was vom Schnitt zählt (Figur 23)."""
        return self.schnitt.u

    @property
    def u(self) -> float:
        """Der wirksame Umfang."""
        return self.k_e * self.u_red

    @property
    def flaeche(self) -> float:
        """Die Fläche innerhalb des Schnitts, ohne Aussparungen."""
        return self.auswertung.flaeche_ohne_aussparungen

    @property
    def V_d_red(self) -> float:
        """Die Querkraft, die den Schnitt kreuzt."""
        return self.V_d - self.q_d * self.flaeche

    def V_Rd_c(self, k_r: float, tau_cd: float) -> float:
        return widerstand(k_r, tau_cd, self.d_v, self.u)

    def V_Rd_max(self, k_sys: float, k_r: float, tau_cd: float) -> float:
        return druckdiagonale(k_sys, k_r, tau_cd, self.d_v, self.u)


@dataclass(frozen=True)
class Leistenpruefung:
    """
    Eine Durchstanzbewehrung an ihrem Ort und die vier Nachweise mit ihr
    (4.3.6.5.1): ``innen`` ist der Schnitt um die gestützte Fläche -- Stütze
    oder Pilz --, ``aussen`` der um die äussersten Anker.
    """

    vorschlag: Vorschlag
    innen: Schnittpruefung
    aussen: Schnittpruefung
    k_r: float
    tau_cd: float
    sigma_sd: float
    f_yd: float
    k_sys: float

    @property
    def A_sw(self) -> float:
        return self.vorschlag.A_sw

    @property
    def V_Rd_c(self) -> float:
        return self.innen.V_Rd_c(self.k_r, self.tau_cd)

    @property
    def V_d_s(self) -> float:
        """Worauf die Bewehrung bemessen wird (66)."""
        return self.innen.V_d_red - self.V_Rd_c

    @property
    def V_Rd_s(self) -> float:
        """Was sie trägt (68)."""
        return self.A_sw * self.innen.k_e * self.sigma_sd

    @property
    def V_halb(self) -> float:
        return self.innen.V_d_red / 2.0

    @property
    def V_Rd_v(self) -> float:
        """Die Bewehrung an der Fliessgrenze (67)."""
        return self.A_sw * self.innen.k_e * self.f_yd

    @property
    def V_Rd_max(self) -> float:
        return self.innen.V_Rd_max(self.k_sys, self.k_r, self.tau_cd)

    @property
    def V_Rd_c_aussen(self) -> float:
        return self.aussen.V_Rd_c(self.k_r, self.tau_cd)

    @property
    def traegt(self) -> bool:
        """(66) und (67): die Bewehrung trägt, was der Beton nicht trägt, und fliessend die Hälfte."""
        return self.V_Rd_s >= self.V_d_s and self.V_Rd_v >= self.V_halb

    @property
    def aussen_reicht(self) -> bool:
        return self.V_Rd_c_aussen >= self.aussen.V_d_red

    @property
    def diagonale_haelt(self) -> bool:
        return self.V_Rd_max >= self.innen.V_d_red

    @property
    def reicht(self) -> bool:
        """Was mehr oder längere Leisten erreichen können -- die Druckdiagonale nicht."""
        return self.traegt and self.aussen_reicht


@dataclass(frozen=True)
class Pilzbefund:
    """Ein Stahlpilz, seine gestützte Fläche bis an die Enden der Stege und der Schnitt um sie."""

    pilz: Stahlpilz
    umriss: Tuple[Punkt, ...]
    pruefung: Schnittpruefung
    V_Rd_c: float
    """Der Widerstand um den Pilz, ohne Bewehrung."""

    @property
    def reicht(self) -> bool:
        return self.V_Rd_c >= self.pruefung.V_d_red
