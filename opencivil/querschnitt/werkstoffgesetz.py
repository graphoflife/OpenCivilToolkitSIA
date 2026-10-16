"""
opencivil/querschnitt/werkstoffgesetz.py -- Spannungs-Dehnungs-Beziehungen.

VERANTWORTUNG:
Jedes Werkstoffgesetz ist ein Objekt, das rechnet und sich selbst als Formel
schreibt -- dieselben Werte, dieselben Aeste. Beton: die
Parabel-Rechteck-Beziehung (SIA 262:2025, 4.2.1.6, :class:`Betongesetz`), der
Spannungsblock 0.85·x (:class:`Spannungsblock`), linear ohne Zug
(:class:`BetonElastisch`) und ungerissen (:class:`BetonUngerissen`).
Betonstahl: bilinear, auf Zug und Druck getrennt begrenzt, oder nur auf Zug
(:class:`Stahlgesetz`, 4.2.2.4).

Bis 2026-10-16 rechneten Funktionen im Loeser, und gedruckt wurden Klassen
mit Platzhaltern oder Formeln von Hand. Jenseits von eps_c2d und beim
gedrueckten Stahl stand in der Herleitung etwas anderes, als gerechnet wurde.

JENSEITS DER GRENZDEHNUNG:
Null: eine Faser jenseits ihrer Bruchstauchung oder Bruchdehnung traegt
nicht, und eine Suche bleibt im gueltigen Bereich. Auf der Grenze selbst
gilt das Gesetz -- auch um eine Rundung darueber (:data:`RUNDUNG`): wer den
Rand abfaehrt, die genaue Resistenzlinie, legt eine Lage genau auf ``eps_ud``,
und die darf nicht an der letzten Stelle auf null kippen. Bis 2026-10-16
hielt der Loeser die Grenze hart und die Linie gar nicht -- zwei Gesetze fuer
eines.

VORZEICHEN (im ganzen Querschnittsmodul gleich):
    Dehnung   eps > 0  =  Zug
    Spannung  sig > 0  =  Zug

SCHNELL:
Die Gesetze laufen in der Faserintegration hunderttausendfach. Jedes baut
darum einmal seine Funktion (``funktion``) mit blanken SI-Zahlen; die Fasern
rufen sie unmittelbar, ohne den Umweg ueber ``__call__``
(:mod:`opencivil.querschnitt.fasern`). Wer ``funktion`` aendert, misst: ein
``max()`` statt eines Vergleichs kostete 28 ms je Platte.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

Funktion = Callable[[float], float]

#: Um so viel darf eine Dehnung ueber ihrer Grenze liegen und gilt noch als auf
#: ihr: eine Rundung. Ein Milliardstel Promille -- weit unter allem, was eine
#: Eingabe oder eine Suche unterscheidet, weit ueber der letzten Stelle.
RUNDUNG = 1e-12


#: Kleiner rechnet die Parabel ``k_sigma`` nicht. Darunter haette ihr Nenner
#: ``1 + (k_sigma - 2)·eta`` im ansteigenden Ast eine Nullstelle, bei
#: ``eta = 1/(2 - k_sigma)`` -- die Spannung spraenge dort ins Unendliche und
#: wechselte das Vorzeichen. So weit kommt es mit dem kriechweichen Modul:
#: ``E_cm/(1 + phi)`` mit charakteristischen Werten und ``phi = 2`` gibt
#: ``k_sigma = 0.93``. Mit 1 ist der Beton bis ``f_c`` bei ``eps_c1d`` linear.
#: Nach Vorgabe, nicht nachgeschlagen (``notizbuch/Notizen/TODO.md``).
K_SIGMA_MIN = 1.0

#: Dieselbe Regel als Formel, fuer die Herleitung -- mit ``@E_c`` und ``@f_c``.
K_SIGMA_LATEX = r"\max\left(1;\ \frac{@E_c}{400 \cdot @f_c}\right)"


def k_sigma(E_c: float, f_c: float) -> float:
    """Der Beiwert der Parabel zum Modul ``E_c``: ``E_c/(400·f_c)``, nie unter 1."""
    return max(K_SIGMA_MIN, E_c / (400.0 * f_c)) if f_c > 0 else K_SIGMA_MIN


#: Die Seite im Notizbuch fuer den Stahl der Handrechnung, der nur Zug traegt.
STAHL_NUR_ZUG = "Betonstahl nur auf Zug"

#: Was jenseits der Bruchstauchung gilt -- als Fall in der Formel der Parabel.
_JENSEITS_BETON = (r" 0 & |\varepsilon_c| > \varepsilon_{c2d} \quad "
                   r"(\text{jenseits der Bruchstauchung}) \\[1ex]")


def _gebaut(gesetz, funktion: Funktion) -> None:
    """Legt die Funktion an ein eingefrorenes Gesetz -- einmal, beim Bauen."""
    object.__setattr__(gesetz, "funktion", funktion)


@dataclass(frozen=True)
class Betongesetz:
    """
    Parabel-Rechteck-Beziehung nach SIA 262:2025, 4.2.1.6.

    Mit ``eta = |eps| / eps_c1d`` gilt fuer den Druckbereich::

                  k_sigma * eta - eta^2
        sig = f_cd -----------------------      für 0 <= |eps| <= eps_c1d
                  1 + (k_sigma - 2) * eta

        sig = f_cd                              für eps_c1d < |eps| <= eps_c2d

    Jenseits von ``eps_c2d`` null -- siehe Dateikopf.
    """

    #: Die Seite im Notizbuch -- gleich, wer das Gesetz unter welchem Titel
    #: aufschreibt.
    NAME = "Parabel-Rechteck-Beziehung des Betons"

    f_cd: float
    """Festigkeit in N/m^2 (positiver Betrag) -- je nach Werkstoffsatz
    ``f_cd`` oder ``f_ck``."""

    eps_c1d: float
    """Dehnung am Ende des ansteigenden Astes (positiver Betrag)."""

    eps_c2d: float
    """Bruchdehnung (positiver Betrag)."""

    k_sigma: float
    """Gerechnet wird mit mindestens :data:`K_SIGMA_MIN` -- siehe dort."""

    funktion: Funktion = field(init=False, repr=False, compare=False)

    @classmethod
    def mit_modul(cls, *, f_c: float, E_c: float, eps_c1d: float,
                  eps_c2d: float) -> "Betongesetz":
        """Das Gesetz zum Modul ``E_c`` -- ``k_sigma`` aus :func:`k_sigma`, die eine Stelle."""
        return cls(f_cd=f_c, eps_c1d=eps_c1d, eps_c2d=eps_c2d, k_sigma=k_sigma(E_c, f_c))

    def __post_init__(self) -> None:
        f, e1, grenze = self.f_cd, self.eps_c1d, -(self.eps_c2d + RUNDUNG)
        k = max(K_SIGMA_MIN, self.k_sigma)

        def sigma(eps: float) -> float:
            if eps >= 0.0:
                return 0.0
            if eps < grenze:
                return 0.0
            if eps <= -e1:
                return -f
            eta = -eps / e1
            return -f * (k * eta - eta * eta) / (1.0 + eta * (k - 2.0))
        _gebaut(self, sigma)

    def spannung(self, eps: float) -> float:
        """Spannung in N/m^2 zur Dehnung ``eps``. Zug positiv, also hier <= 0."""
        return self.funktion(eps)

    __call__ = spannung

    @property
    def seite(self) -> str:
        """Die Seite im Notizbuch."""
        return self.NAME

    def latex(self, f: str = "f_{cd}") -> str:
        """Als Formel -- ``f`` ist das Zeichen der Festigkeit, ``f_{ck}`` bei charakteristischen Werten."""
        return (
            r"\sigma_c(\varepsilon_c) = \begin{cases}"
            rf" -{f} \cdot \dfrac{{k_\sigma\,\eta - \eta^2}}{{1 + (k_\sigma - 2)\,\eta}}"
            r" & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ "
            r"\eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex]"
            rf" -{f} & \varepsilon_{{c1d}} < |\varepsilon_c| \le \varepsilon_{{c2d}} \\[1ex]"
            + _JENSEITS_BETON
            + r" 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen})"
            r" \end{cases}"
        )


#: Anteil der Druckzonenhoehe, ueber den der Spannungsblock wirkt. Steht hier
#: und nirgends sonst: die Handrechnung der Platte, ihr Duktilitaetsnachweis,
#: das Diagramm der Werkstoffgesetze und der gezeichnete Querschnitt meinen
#: alle denselben Block.
BLOCKANTEIL = 0.85


@dataclass(frozen=True)
class Spannungsblock:
    """
    Der vereinfachte, rechteckige Spannungsverlauf des Betons.

    Unterhalb von ``(1 - 0.85) * eps_c2d`` keine Spannung, darueber
    durchgehend ``f_cd``. Liegt der gedrueckte Rand bei ``eps_c2d`` -- im
    Bruchzustand --, ist das genau der Block der Hoehe ``0.85 x``, mit dem die
    Handrechnung rechnet. Als Gesetz gilt er auch dort, wo der Rand nicht bei
    ``eps_c2d`` liegt; so setzt ihn die Interaktionslinie des gezeichneten
    Querschnitts ein.

    Die Normstelle des Blocks ist offen (``notizbuch/Notizen/TODO.md``); sie
    wird nicht erfunden.
    """

    #: Die Seite im Notizbuch, wie bei :attr:`Betongesetz.NAME`.
    NAME = "Spannungsblock des Betons"

    f_cd: float
    """Festigkeit des Blocks in N/m^2 (positiver Betrag) -- je nach
    Werkstoffsatz ``f_cd`` oder ``f_ck``."""

    eps_c2d: float
    """Bruchdehnung (positiver Betrag)."""

    funktion: Funktion = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        f, knick, grenze = self.f_cd, -self.eps_knick, -(self.eps_c2d + RUNDUNG)

        def sigma(eps: float) -> float:
            if eps > knick or eps < grenze:
                return 0.0  # Zug, zu wenig Stauchung fuer den Block, oder zerdrueckt
            return -f
        _gebaut(self, sigma)

    @property
    def eps_knick(self) -> float:
        """Ab dieser Stauchung (Betrag) setzt der Block ein."""
        return (1.0 - BLOCKANTEIL) * self.eps_c2d

    def spannung(self, eps: float) -> float:
        """Spannung in N/m^2 zur Dehnung ``eps``. Zug positiv, also hier <= 0."""
        return self.funktion(eps)

    __call__ = spannung

    def mittel(self, eps_a: float, eps_b: float) -> float:
        """
        Die mittlere Spannung, wenn die Dehnung linear von ``eps_a`` nach
        ``eps_b`` laeuft -- genau: ``f_cd`` mal der Anteil, der im Block liegt,
        zwischen dem Knick und ``-eps_c2d``.

        Der Block springt. In der Mitte einer Faser gelesen, springt darum auch
        N, sobald eine Faser den Knick ueberschreitet -- am Kastentraeger um
        gut 20 kN --, und keine Ebene trifft N_Ed genau. Ueber die Faser
        gemittelt, waechst N stetig.
        """
        unten, oben = min(eps_a, eps_b), max(eps_a, eps_b)
        knick = -self.eps_knick
        if oben == unten:
            return self.funktion(unten)
        if oben <= knick and unten >= -(self.eps_c2d + RUNDUNG):
            return -self.f_cd
        von, bis = max(unten, -self.eps_c2d), min(oben, knick)
        if bis <= von:
            return 0.0
        return -self.f_cd * (bis - von) / (oben - unten)

    @property
    def seite(self) -> str:
        """Die Seite im Notizbuch."""
        return self.NAME

    def latex(self, f: str = "f_{cd}") -> str:
        """Als Formel -- ``f`` ist das Zeichen der Festigkeit, ``f_{ck}`` bei charakteristischen Werten."""
        return (
            r"\sigma_c(\varepsilon_c) = \begin{cases}"
            r" 0 & \varepsilon_c > -(1 - " + f"{BLOCKANTEIL}" + r") \cdot \varepsilon_{c2d} \\[1ex]"
            rf" -{f} & -\varepsilon_{{c2d}} \le \varepsilon_c \le -(1 - "
            + f"{BLOCKANTEIL}" + r") \cdot \varepsilon_{c2d}"
            + r" \\[1ex] 0 & \varepsilon_c < -\varepsilon_{c2d} \quad "
            r"(\text{jenseits der Bruchstauchung})"
            r" \end{cases}"
        )


@dataclass(frozen=True)
class Stahlgesetz:
    """
    Bilineare Beziehung ohne Verfestigung nach SIA 262:2025, 4.2.2.4.

    Zug und Druck werden getrennt begrenzt, weil ``f_yd`` und ``f_yd^-`` in der
    Sortentabelle unterschiedlich sein duerfen. ``nur_zug``: der gedrueckte
    Stahl traegt nichts -- so laesst die Handrechnung die Druckbewehrung weg.
    """

    #: Die Seite im Notizbuch, wie bei :attr:`Betongesetz.NAME`.
    NAME = "Bilineare Beziehung des Betonstahls"

    E_s: float
    """Elastizitaetsmodul in N/m^2."""

    f_yd: float
    """Fliessgrenze auf Zug in N/m^2 -- je nach Werkstoffsatz ``f_yd`` oder ``f_yk``."""

    f_yd_druck: float
    """Fliessgrenze auf Druck in N/m^2 (positiver Betrag)."""

    eps_ud: float
    """Grenzdehnung (positiver Betrag)."""

    nur_zug: bool = False
    """Der gedrueckte Stahl traegt nichts."""

    funktion: Funktion = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        _gebaut(self, _stahlfunktion(self.E_s, self.f_yd, self.f_yd_druck, self.eps_ud,
                                     nur_zug=self.nur_zug))

    def spannung(self, eps: float) -> float:
        """Spannung in N/m^2 zur Dehnung ``eps``. Zug positiv."""
        return self.funktion(eps)

    __call__ = spannung

    @property
    def eps_yd(self) -> float:
        return self.f_yd / self.E_s

    @property
    def seite(self) -> str:
        """Die Seite im Notizbuch -- der Stahl nur auf Zug hat seine eigene."""
        return STAHL_NUR_ZUG if self.nur_zug else self.NAME

    def latex(self, zug: str = "f_{yd}", druck: str = "f_{yd}^{-}") -> str:
        """Als Formel -- ``zug`` und ``druck`` sind die Zeichen der Plateaus."""
        if self.nur_zug:
            return (
                r"\sigma_s(\varepsilon_s) = \begin{cases}"
                rf" \min(E_s\,\varepsilon_s;\ {zug}) & 0 < \varepsilon_s \le \varepsilon_{{ud}} \\[1ex]"
                r" 0 & \varepsilon_s \le 0 \quad (\text{gedrückt: weggelassen})"
                r" \\[1ex] 0 & \varepsilon_s > \varepsilon_{ud} \quad (\text{jenseits der Bruchdehnung})"
                r" \end{cases}"
            )
        return (
            r"\sigma_s(\varepsilon_s) = \begin{cases}"
            rf" \min(E_s\,\varepsilon_s;\ {zug}) & 0 \le \varepsilon_s \le \varepsilon_{{ud}} \\[1ex]"
            rf" \max(E_s\,\varepsilon_s;\ -{druck}) & -\varepsilon_{{ud}} \le \varepsilon_s < 0"
            r" \\[1ex] 0 & |\varepsilon_s| > \varepsilon_{ud} \quad (\text{jenseits der Bruchdehnung})"
            r" \end{cases}"
        )


def _stahlfunktion(E_s: float, f: float, f_druck: float, eps_ud: float, *,
                   nur_zug: bool) -> Funktion:
    """
    Die Funktion des Stahls, je Fall eine eigene: in der Schleife entscheidet
    sie nichts, was schon beim Bauen feststeht. Sind beide Plateaus gleich --
    bei den Normsorten --, rechnet sie mit dem Betrag.
    """
    grenze = eps_ud + RUNDUNG
    if nur_zug:
        def sigma_zug(eps: float) -> float:
            if eps <= 0.0 or eps > grenze:
                return 0.0
            return min(eps * E_s, f)
        return sigma_zug
    if f_druck == f:
        def sigma(eps: float) -> float:
            if abs(eps) > grenze:
                return 0.0
            return math.copysign(min(abs(eps) * E_s, f), eps)
        return sigma

    def sigma_getrennt(eps: float) -> float:
        if abs(eps) > grenze:
            return 0.0
        if eps >= 0.0:
            return min(eps * E_s, f)
        return -min(-eps * E_s, f_druck)
    return sigma_getrennt


@dataclass(frozen=True)
class BetonElastisch:
    """
    Beton ohne Zugfestigkeit, im Druck linear bis ``f_c``, dann waagrecht --
    fuer den gerissenen Gebrauchszustand.

    ``E_c`` ist bereits der wirksame Modul, ``E_cm/(1+phi)``, falls Kriechen
    zaehlt; ``f_c`` die Festigkeit aus dem Werkstoffsatz, im Gebrauchszustand
    ``f_ck``. Linear und nicht als Parabel: im Gebrauchszustand liegt die
    Betonspannung weit unter der Festigkeit, und dort ist die Parabel eine
    Gerade. Die Grenze steht trotzdem da, damit eine Druckzone, die doch
    einmal so weit kommt, nicht mehr aufnimmt, als der Beton hergibt. Ohne
    ``f_c`` bleibt das Gesetz unbegrenzt linear -- fuer Rechnungen, die mit
    Festigkeiten nichts zu tun haben.
    """

    NAME = "Beton linear, ohne Zug"

    E_c: float
    f_c: float = math.inf

    funktion: Funktion = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        E_c, grenze = self.E_c, -self.f_c

        # Ein Vergleich und nicht max(): das Gesetz laeuft je Nachweisfall
        # rund siebzigtausend Mal, und der Funktionsaufruf kostete doppelt so
        # viel wie die Rechnung selbst.
        def sigma(eps: float) -> float:
            if eps > 0.0:
                return 0.0
            s = E_c * eps
            return s if s > grenze else grenze
        _gebaut(self, sigma)

    def spannung(self, eps: float) -> float:
        return self.funktion(eps)

    __call__ = spannung

    @property
    def seite(self) -> str:
        """Die Seite im Notizbuch."""
        return self.NAME

    def latex(self, E: str = "E_{c,eff}", f: str = "f_{ck}") -> str:
        """Als Formel -- ``E`` der Modul, ``f`` die Festigkeit, bei der es waagrecht wird."""
        return (
            r"\sigma_c(\varepsilon_c) = \begin{cases}"
            rf" \max\left({E} \cdot \varepsilon_c;\ -{f}\right) & \varepsilon_c \le 0 \\[1ex]"
            r" 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen})"
            r" \end{cases}"
        )


@dataclass(frozen=True)
class BetonUngerissen:
    """
    Beton linear in beiden Richtungen -- der ungerissene Vergleichszustand.

    Ohne Abminderung im Zug und ohne Abbruch bei ``f_ct``. Das ist Absicht:
    gebraucht wird die *Steifigkeit* des ungerissenen Querschnitts, und wo er
    reisst, sagt das Rissmoment -- oberhalb davon gilt die Linie gerissen,
    dieser Zustand steht dort nur noch zum Vergleich. Ein Gesetz, das bei
    ``f_ct`` abfiele, waere ausserdem nicht mehr monoton, und die Bisektion
    des Loesers braucht Monotonie.
    """

    NAME = "Beton ungerissen, in Druck und Zug"

    E_c: float

    funktion: Funktion = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        E_c = self.E_c

        def sigma(eps: float) -> float:
            return E_c * eps
        _gebaut(self, sigma)

    def spannung(self, eps: float) -> float:
        return self.funktion(eps)

    __call__ = spannung

    @property
    def seite(self) -> str:
        """Die Seite im Notizbuch."""
        return self.NAME

    def latex(self, E: str = "E_{c,eff}") -> str:
        """Als Formel -- ``E`` ist der Modul."""
        return rf"\sigma_c = {E} \cdot \varepsilon_c"


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
