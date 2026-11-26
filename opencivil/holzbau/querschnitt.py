"""
opencivil/holzbau/querschnitt.py -- ein gezeichneter Querschnitt aus Holz.

VERANTWORTUNG:
Was Kennzahlen und Nachweise eines Holzquerschnitts
(:mod:`opencivil.nachweis.qa_holz`) aus der Zeichnung brauchen, ohne
Rechenwerk und ohne Herleitung, in mm: die Polygone mit ihrem Gewicht, die
Ausdehnung, je Achse den Abstand der weitesten Faser, den Schnitt, an dem
eine Querkraft die groesste Schubspannung weckt, und beim Rechteck den
Beiwert der Torsion.

LINEAR (SIA 265:2012, 4.1.2):
Die Spannungen sind elastisch, am Bruttoquerschnitt, wie die Werte der
Analyse. y und z gelten als Hauptachsen, wie beim Stahl
(:mod:`opencivil.stahlbau.querschnitt`): eine Biegung um y hat ihre
Nulllinie waagrecht. Die Biegespannung je Achse ist die an der weitesten
Faser -- beim Rechteck M/W; bei einem Querschnitt, dessen Fasern ungleich
weit vom Schwerpunkt liegen, auf der sicheren Seite (nach Vorgabe, nicht
nachgeschlagen).

SCHUB AUS QUERKRAFT:
``τ = V·S/(I·b)`` nach Jourawski, auf dem Schnitt quer zur Querkraft, auf
dem ``S/b`` am groessten ist -- gesucht zwischen je zwei Ecken auf
:data:`TEILE` Schnitten und im Schwerpunkt. Beim Rechteck ist das die
Mitte, mit ``τ = 1.5·V/A``.

SCHUB AUS TORSION:
Nur fuer ein Rechteck, die Seiten parallel zu y und z
(:attr:`Holzquerschnitt.rechteck`): ``τ_tor = T/W_T`` mit ``W_T = k_2·h·b²``,
``b`` die kurze Seite, ``k_2`` aus den Reihen von Saint-Venant
(:func:`k_2`). Fuer einen anderen Querschnitt gibt es keine solche Formel;
dort weist das Werkzeug Torsion nicht nach (nach Vorgabe, nicht
nachgeschlagen).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cached_property
from typing import Optional, Tuple

from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.geometrie import Punkt

#: Auf so vielen Schnitten zwischen zwei Ecken sucht der Schub seine Stelle.
TEILE = 64

#: Wie genau ein Rechteck seine Seiten parallel zu y und z haben muss, relativ zu seiner Groesse.
PARALLEL = 1e-9

#: Die Reihen von Saint-Venant enden, wo ihr Glied kleiner ist als das.
GLIED = 1e-15


@dataclass(frozen=True)
class Schubschnitt:
    """Der Schnitt mit dem groessten ``S/b``: ``S`` in mm³, ``b`` und ``lage`` in mm."""

    S: float
    b: float
    lage: float
    """Wo er liegt: ``z`` fuer eine Querkraft in z, ``y`` fuer eine in y."""

    @property
    def faktor(self) -> float:
        """``S/b`` in mm² -- mal ``V/I`` gibt das ``τ``."""
        return self.S / self.b


@dataclass(frozen=True)
class Holzquerschnitt:
    """
    Die Polygone eines Holzquerschnitts, je mit ihrem Gewicht -- +1 mit Holz,
    -1 fuer eine Aussparung darin --, und sein Schwerpunkt, in mm.
    """

    polygone: Tuple[Tuple[Tuple[Punkt, ...], float], ...]
    y_S: float
    z_S: float

    @classmethod
    def aus(cls, zeichnung) -> "Holzquerschnitt":
        """Aus der Zeichnung einer Analyse (:class:`~opencivil.querschnitt.analyse.Zeichnung`)."""
        polygone = tuple((tuple(tuple(p) for p in punkte), zeichnung.gewicht(i))
                         for i, punkte in enumerate(zeichnung.punkte)
                         if zeichnung.gewicht(i) != 0.0)
        return cls(polygone, zeichnung.brutto.y_S, zeichnung.brutto.z_S)

    # -- Ausdehnung --------------------------------------------------------------------

    @cached_property
    def ausdehnung(self) -> Tuple[float, float, float, float]:
        """``(y_min, y_max, z_min, z_max)`` des Holzes."""
        punkte = [p for punkte, gewicht in self.polygone if gewicht > 0.0 for p in punkte]
        ys, zs = [p[0] for p in punkte], [p[1] for p in punkte]
        return min(ys), max(ys), min(zs), max(zs)

    def faser(self, achse: str) -> float:
        """Wie weit die weiteste Faser einer Biegung um ``achse`` vom Schwerpunkt liegt."""
        y_min, y_max, z_min, z_max = self.ausdehnung
        if achse == "y":
            return max(z_max - self.z_S, self.z_S - z_min)
        return max(y_max - self.y_S, self.y_S - y_min)

    def hoehe(self, achse: str) -> float:
        """Die Hoehe einer Biegung um ``achse``: in z um y, in y um z."""
        y_min, y_max, z_min, z_max = self.ausdehnung
        return z_max - z_min if achse == "y" else y_max - y_min

    def breite(self, achse: str) -> float:
        """Die Breite quer dazu."""
        return self.hoehe("z" if achse == "y" else "y")

    @cached_property
    def rechteck(self) -> bool:
        """Ob der Querschnitt ein einziges Rechteck ist, die Seiten parallel zu y und z."""
        if len(self.polygone) != 1:
            return False
        punkte, gewicht = self.polygone[0]
        if gewicht < 0.0 or len(punkte) != 4:
            return False
        groesse = max(self.hoehe("y"), self.hoehe("z"))
        for (y1, z1), (y2, z2) in zip(punkte, punkte[1:] + punkte[:1]):
            if abs(y2 - y1) > PARALLEL * groesse and abs(z2 - z1) > PARALLEL * groesse:
                return False
        return True

    # -- Schub aus Querkraft ------------------------------------------------------------

    def schubschnitt(self, richtung: str) -> Optional[Schubschnitt]:
        """
        Der Schnitt quer zu einer Querkraft in ``richtung`` ("y" oder "z"),
        auf dem ``S/b`` am groessten ist -- ``None``, wo keiner Holz trifft.
        """
        return self._schnitte[richtung]

    @cached_property
    def _schnitte(self):
        return {r: self._suchen(r) for r in ("y", "z")}

    def _suchen(self, richtung: str) -> Optional[Schubschnitt]:
        i = 1 if richtung == "z" else 0
        normale = (0.0, 1.0) if richtung == "z" else (1.0, 0.0)
        schwer = self.z_S if richtung == "z" else self.y_S
        ecken = sorted({p[i] for punkte, _ in self.polygone for p in punkte})
        stellen = {schwer} - set(ecken)
        for a, b in zip(ecken, ecken[1:]):
            stellen.update(a + (b - a) * k / TEILE for k in range(1, TEILE))
        bester: Optional[Schubschnitt] = None
        for v in sorted(stellen):
            if not ecken[0] < v < ecken[-1]:
                continue
            S, b = self._schnitt(normale, v, schwer)
            if b > 0.0 and (bester is None or abs(S) / b > bester.faktor):
                bester = Schubschnitt(abs(S), b, v)
        return bester

    def _schnitt(self, normale: Tuple[float, float], v: float,
                 schwer: float) -> Tuple[float, float]:
        """Das statische Moment jenseits von ``n·p = v`` um die Schwerachse und die Breite dort."""
        S = b = 0.0
        for punkte, gewicht in self.polygone:
            A, s_y, s_z = geo.jenseits(punkte, normale, v)
            S += gewicht * ((s_z if normale[1] else s_y) - schwer * A)
            b += gewicht * sum(bis - von for von, bis in geo.schnitt_mit_gerade(punkte, normale, v))
        return S, b

    # -- Torsion des Rechtecks -----------------------------------------------------------

    @property
    def seiten(self) -> Tuple[float, float]:
        """Die kurze und die lange Seite des Rechtecks, ``(b, h)``."""
        a, c = self.hoehe("z"), self.hoehe("y")
        return min(a, c), max(a, c)


def k_2(verhaeltnis: float) -> float:
    """
    Der Beiwert ``k_2`` in ``W_T = k_2·h·b²`` eines Rechtecks mit
    ``h/b = verhaeltnis ≥ 1`` -- aus den Reihen von Saint-Venant fuer
    ``I_T = β·h·b³`` und die groesste Schubspannung, ``τ = c·T·b/I_T``, in der
    Mitte der langen Seite: ``k_2 = β/c``. 0.208 beim Quadrat, gegen 1/3 beim
    schmalen Rechteck.
    """
    beta = 1.0 / 3.0 * (1.0 - 192.0 / math.pi ** 5 / verhaeltnis
                        * _reihe(lambda n: math.tanh(n * math.pi * verhaeltnis / 2.0) / n ** 5))
    c = 1.0 - 8.0 / math.pi ** 2 * _reihe(
        lambda n: _sech(n * math.pi * verhaeltnis / 2.0) / n ** 2)
    return beta / c


def _reihe(glied) -> float:
    """Die Summe ueber die ungeraden ``n``, bis ein Glied kleiner ist als :data:`GLIED`."""
    summe, n = 0.0, 1
    while True:
        g = glied(n)
        summe += g
        if abs(g) < GLIED:
            return summe
        n += 2


def _sech(x: float) -> float:
    """``1/cosh x`` -- auch fuer grosse ``x``, wo ``cosh`` ueberliefe."""
    e = math.exp(-x)
    return 2.0 * e / (1.0 + e * e)


def starke_achse(I_y: float, I_z: float) -> str:
    """
    Die Achse mit dem groesseren Traegheitsmoment, gleich gross y: nur eine
    Biegung um sie kann den Stab kippen lassen. Beim Rechteck die um die
    lange Seite.
    """
    return "y" if I_y >= I_z else "z"
