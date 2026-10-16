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
Wer sucht -- der Loeser --, braucht dort null: eine Faser jenseits ihrer
Grenzdehnung traegt nicht, und die Suche bleibt im gueltigen Bereich. Wer
den Rand abfaehrt -- die genaue Resistenzlinie --, braucht das Gesetz stetig
bis an die Grenze: eine Faser genau auf ihr darf nicht an einer Rundung auf
null kippen. Das waehlt, wer das Gesetz baut, mit ``bricht``.

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

    Jenseits von ``eps_c2d`` null, wenn es ``bricht``, sonst ``f_cd``.
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

    bricht: bool = True
    """Jenseits von ``eps_c2d`` null -- siehe Dateikopf."""

    funktion: Funktion = field(init=False, repr=False, compare=False)

    @classmethod
    def mit_modul(cls, *, f_c: float, E_c: float, eps_c1d: float, eps_c2d: float,
                  bricht: bool = True) -> "Betongesetz":
        """Das Gesetz zum Modul ``E_c`` -- ``k_sigma`` aus :func:`k_sigma`, die eine Stelle."""
        return cls(f_cd=f_c, eps_c1d=eps_c1d, eps_c2d=eps_c2d, k_sigma=k_sigma(E_c, f_c),
                   bricht=bricht)

    def __post_init__(self) -> None:
        f, e1, e2 = self.f_cd, self.eps_c1d, self.eps_c2d
        k = max(K_SIGMA_MIN, self.k_sigma)
        jenseits = 0.0 if self.bricht else -f

        def sigma(eps: float) -> float:
            if eps >= 0.0:
                return 0.0
            if eps < -e2:
                return jenseits
            if eps <= -e1:
                return -f
            eta = -eps / e1
            return -f * (k * eta - eta * eta) / (1.0 + eta * (k - 2.0))
        _gebaut(self, sigma)

    def spannung(self, eps: float) -> float:
        """Spannung in N/m^2 zur Dehnung ``eps``. Zug positiv, also hier <= 0."""
        return self.funktion(eps)

    __call__ = spannung

    def latex(self, f: str = "f_{cd}") -> str:
        """Als Formel -- ``f`` ist das Zeichen der Festigkeit, ``f_{ck}`` bei charakteristischen Werten."""
        return (
            r"\sigma_c(\varepsilon_c) = \begin{cases}"
            rf" -{f} \cdot \dfrac{{k_\sigma\,\eta - \eta^2}}{{1 + (k_\sigma - 2)\,\eta}}"
            r" & 0 \le |\varepsilon_c| \le \varepsilon_{c1d},\ "
            r"\eta = \dfrac{|\varepsilon_c|}{\varepsilon_{c1d}} \\[2ex]"
            rf" -{f} & \varepsilon_{{c1d}} < |\varepsilon_c| \le \varepsilon_{{c2d}} \\[1ex]"
            r" 0 & \varepsilon_c > 0 \quad (\text{Zug, gerissen})"
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

    bricht: bool = True
    """Jenseits von ``eps_c2d`` null -- siehe Dateikopf."""

    funktion: Funktion = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        f, knick, grenze = self.f_cd, -self.eps_knick, -self.eps_c2d
        if self.bricht:
            def sigma(eps: float) -> float:
                if eps > knick or eps < grenze:
                    return 0.0
                return -f
        else:
            def sigma(eps: float) -> float:
                if eps > knick:
                    return 0.0  # Zug, oder zu wenig Stauchung fuer den Block
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
        zwischen dem Knick und, wenn er ``bricht``, ``-eps_c2d``.

        Der Block springt. In der Mitte einer Faser gelesen, springt darum auch
        N, sobald eine Faser den Knick ueberschreitet -- am Kastentraeger um
        gut 20 kN --, und keine Ebene trifft N_Ed genau. Ueber die Faser
        gemittelt, waechst N stetig.
        """
        unten, oben = min(eps_a, eps_b), max(eps_a, eps_b)
        knick = -self.eps_knick
        grenze = -self.eps_c2d if self.bricht else -math.inf
        if oben == unten:
            return self.funktion(unten)
        if oben <= knick and unten >= grenze:
            return -self.f_cd
        von, bis = max(unten, grenze), min(oben, knick)
        if bis <= von:
            return 0.0
        return -self.f_cd * (bis - von) / (oben - unten)

    def latex(self, f: str = "f_{cd}") -> str:
        """Als Formel -- ``f`` ist das Zeichen der Festigkeit, ``f_{ck}`` bei charakteristischen Werten."""
        return (
            r"\sigma_c(\varepsilon_c) = \begin{cases}"
            r" 0 & \varepsilon_c > -(1 - " + f"{BLOCKANTEIL}" + r") \cdot \varepsilon_{c2d} \\[1ex]"
            rf" -{f} & -\varepsilon_{{c2d}} \le \varepsilon_c \le -(1 - "
            + f"{BLOCKANTEIL}" + r") \cdot \varepsilon_{c2d}"
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

    bricht: bool = True
    """Jenseits von ``eps_ud`` null -- siehe Dateikopf."""

    funktion: Funktion = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        _gebaut(self, _stahlfunktion(self.E_s, self.f_yd, self.f_yd_druck, self.eps_ud,
                                     nur_zug=self.nur_zug, bricht=self.bricht))

    def spannung(self, eps: float) -> float:
        """Spannung in N/m^2 zur Dehnung ``eps``. Zug positiv."""
        return self.funktion(eps)

    __call__ = spannung

    @property
    def eps_yd(self) -> float:
        return self.f_yd / self.E_s

    def latex(self, zug: str = "f_{yd}", druck: str = "f_{yd}^{-}") -> str:
        """Als Formel -- ``zug`` und ``druck`` sind die Zeichen der Plateaus."""
        return (
            r"\sigma_s(\varepsilon_s) = \begin{cases}"
            rf" \min(E_s\,\varepsilon_s;\ {zug}) & \varepsilon_s \ge 0 \\[1ex]"
            rf" \max(E_s\,\varepsilon_s;\ -{druck}) & \varepsilon_s < 0"
            r" \end{cases}"
            r" \qquad |\varepsilon_s| \le \varepsilon_{ud}"
        )


def _stahlfunktion(E_s: float, f: float, f_druck: float, eps_u: float, *,
                   nur_zug: bool, bricht: bool) -> Funktion:
    """
    Die Funktion des Stahls, je Fall eine eigene: in der Schleife entscheidet
    sie nichts, was schon beim Bauen feststeht. Sind beide Plateaus gleich --
    bei den Normsorten --, rechnet sie mit dem Betrag.
    """
    if nur_zug:
        def sigma_zug(eps: float) -> float:
            if eps <= 0.0 or (bricht and eps > eps_u):
                return 0.0
            return min(eps * E_s, f)
        return sigma_zug
    if f_druck == f:
        if bricht:
            def sigma(eps: float) -> float:
                if abs(eps) > eps_u:
                    return 0.0
                return math.copysign(min(abs(eps) * E_s, f), eps)
            return sigma

        def sigma_stetig(eps: float) -> float:
            return math.copysign(min(abs(eps) * E_s, f), eps)
        return sigma_stetig

    def sigma_getrennt(eps: float) -> float:
        if bricht and abs(eps) > eps_u:
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
