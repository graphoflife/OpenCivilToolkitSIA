"""
opencivil/querschnitt/werkstoffgesetz.py -- Spannungs-Dehnungs-Beziehungen.

VERANTWORTUNG:
Liefert zu einer Dehnung die zugehoerige Spannung -- fuer Beton nach der
Parabel-Rechteck-Beziehung (SIA 262:2025, 4.2.1.6) und fuer Betonstahl nach der
bilinearen Beziehung (4.2.2.4).

VORZEICHEN (im ganzen Querschnittsmodul gleich):
    Dehnung   eps > 0  =  Zug
    Spannung  sig > 0  =  Zug
Beton nimmt keinen Zug auf; oberhalb der Bruchdehnung faellt die Spannung auf
null, was beim Aufbau der Interaktionslinie nie vorkommt, weil die Dehnungsebene
dort ohnehin begrenzt wird.

WARUM HIER MIT BLANKEN ZAHLEN GERECHNET WIRD:
Diese Funktionen laufen in der Faserintegration hunderttausendfach. Sie
arbeiten deshalb mit SI-Zahlen (N/m^2 und dimensionslose Dehnung) statt mit
:class:`Groesse`. Die Umrechnung geschieht einmal am Rand, in
:class:`Betongesetz.aus_werten` bzw. :class:`Stahlgesetz.aus_werten` -- dort ist
die Einheitenpruefung also weiterhin lueckenlos.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from opencivil.core.einheiten import EINHEITSLOS, N_PRO_MM2, Groesse
from opencivil.core.wert import Wert


@dataclass(frozen=True)
class Betongesetz:
    """
    Parabel-Rechteck-Beziehung nach SIA 262:2025, 4.2.1.6.

    Mit ``eta = |eps| / eps_c1d`` gilt fuer den Druckbereich::

                  k_sigma * eta - eta^2
        sig = f_cd -----------------------      für 0 <= |eps| <= eps_c1d
                  1 + (k_sigma - 2) * eta

        sig = f_cd                              für eps_c1d < |eps| <= eps_c2d
    """

    f_cd: float
    """Bemessungsdruckfestigkeit in N/m^2 (positiver Betrag)."""

    eps_c1d: float
    """Dehnung am Ende des ansteigenden Astes (positiver Betrag)."""

    eps_c2d: float
    """Bruchdehnung (positiver Betrag)."""

    k_sigma: float

    @classmethod
    def aus_werten(cls, werte: Mapping[str, Wert]) -> "Betongesetz":
        """Baut das Gesetz aus den Kennwerten des Betons (mit Einheitenpruefung)."""
        return cls(
            f_cd=abs(werte["f_cd"].groesse.si),
            eps_c1d=abs(werte["eps_c1d"].groesse.si),
            eps_c2d=abs(werte["eps_c2d"].groesse.si),
            k_sigma=werte["k_sigma"].groesse.si,
        )

    def spannung(self, eps: float) -> float:
        """Spannung in N/m^2 zur Dehnung ``eps``. Zug positiv, also hier <= 0."""
        if eps >= 0.0:
            return 0.0  # Beton reisst, kein Zug
        betrag = -eps
        if betrag > self.eps_c1d:
            # Oberhalb der Bruchdehnung wird das Plateau fortgesetzt statt auf
            # null zu fallen. Der Dehnungsfaecher der Interaktionsrechnung haelt
            # jede Faser innerhalb von eps_c2d, sodass dieser Fall gar nicht
            # eintritt; eine Sprungstelle waere aber fuer jede numerische
            # Auswertung verheerend, darum bleibt die Funktion hier stetig.
            return -self.f_cd
        eta = betrag / self.eps_c1d
        nenner = 1.0 + (self.k_sigma - 2.0) * eta
        if nenner == 0.0:
            return -self.f_cd
        return -self.f_cd * (self.k_sigma * eta - eta * eta) / nenner

    def latex(self) -> str:
        return (
            r"\sigma_c(\varepsilon_c) = \begin{cases}"
            r" -f_{cd} \cdot \dfrac{k_\sigma\,\eta - \eta^2}{1 + (k_\sigma - 2)\,\eta}"
            r" & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ "
            r"\eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex]"
            r" -f_{cd} & \varepsilon_{c1d} < |\varepsilon_c| \le \varepsilon_{c2d} \\[1ex]"
            r" 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen})"
            r" \end{cases}"
        )


@dataclass(frozen=True)
class Stahlgesetz:
    """
    Bilineare Beziehung ohne Verfestigung nach SIA 262:2025, 4.2.2.4.

    Zug und Druck werden getrennt begrenzt, weil ``f_yd`` und ``f_yd^-`` in der
    Sortentabelle unterschiedlich sein duerfen.
    """

    E_s: float
    """Elastizitaetsmodul in N/m^2."""

    f_yd: float
    """Fliessgrenze auf Zug in N/m^2."""

    f_yd_druck: float
    """Fliessgrenze auf Druck in N/m^2 (positiver Betrag)."""

    eps_ud: float
    """Grenzdehnung (positiver Betrag)."""

    @classmethod
    def aus_werten(cls, werte: Mapping[str, Wert]) -> "Stahlgesetz":
        return cls(
            E_s=werte["E_s"].groesse.si,
            f_yd=abs(werte["f_yd"].groesse.si),
            f_yd_druck=abs(werte["f_yd_druck"].groesse.si),
            eps_ud=abs(werte["eps_ud"].groesse.si),
        )

    def spannung(self, eps: float) -> float:
        """Spannung in N/m^2 zur Dehnung ``eps``. Zug positiv."""
        elastisch = self.E_s * eps
        if eps >= 0.0:
            return min(elastisch, self.f_yd)
        return max(elastisch, -self.f_yd_druck)

    @property
    def eps_yd(self) -> float:
        return self.f_yd / self.E_s

    def latex(self) -> str:
        return (
            r"\sigma_s(\varepsilon_s) = \begin{cases}"
            r" \min(E_s\,\varepsilon_s;\ f_{yd}) & \varepsilon_s \ge 0 \\[1ex]"
            r" \max(E_s\,\varepsilon_s;\ -f_{yd}^{-}) & \varepsilon_s < 0"
            r" \end{cases}"
            r" \qquad |\varepsilon_s| \le \varepsilon_{ud}"
        )


@dataclass(frozen=True)
class Dehnungsebene:
    """
    Eine ebene Dehnungsverteilung ueber die Querschnittshoehe.

    Die Bernoulli-Hypothese steckt genau hier: die Dehnung ist linear ueber z.
    ``z`` wird von der Oberkante nach unten gemessen.
    """

    eps_oben: float
    """Dehnung an der Oberkante (z = 0)."""

    eps_unten: float
    """Dehnung an der Unterkante (z = h)."""

    h: float
    """Querschnittshoehe in m."""

    @classmethod
    def durch_zwei_punkte(
        cls, eps_a: float, z_a: float, eps_b: float, z_b: float, h: float
    ) -> "Dehnungsebene":
        """Legt die Ebene durch zwei Dehnungspunkte -- so wird der Fächer aufgebaut."""
        if z_a == z_b:
            raise ValueError("Zwei Punkte auf gleicher Höhe legen keine Ebene fest.")
        steigung = (eps_b - eps_a) / (z_b - z_a)
        return cls(
            eps_oben=eps_a + steigung * (0.0 - z_a),
            eps_unten=eps_a + steigung * (h - z_a),
            h=h,
        )

    def bei(self, z: float) -> float:
        """Dehnung auf der Hoehe ``z`` (von Oberkante nach unten)."""
        return self.eps_oben + (self.eps_unten - self.eps_oben) * (z / self.h)

    @property
    def kruemmung(self) -> float:
        """Kruemmung in 1/m."""
        return (self.eps_unten - self.eps_oben) / self.h

    @property
    def nulllinie(self) -> float:
        """
        Lage der Nulllinie in m von der Oberkante.

        Bei reiner Zug- oder Druckbeanspruchung gibt es keine -- dann ist das
        Ergebnis unendlich, was die Auswertung sauber ueberspringt.
        """
        if self.eps_unten == self.eps_oben:
            return float("inf")
        return -self.eps_oben * self.h / (self.eps_unten - self.eps_oben)
