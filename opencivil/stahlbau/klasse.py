"""
opencivil/stahlbau/klasse.py -- die Querschnittsklasse nach SIA 263:2013.

VERANTWORTUNG:
Die Regeln, nach denen ein Blech in eine Querschnittsklasse faellt: die
Grenzschlankheiten der Tabellen 5a (beidseitig gestuetzte Scheiben und das
Rundrohr) und 5b (einseitig gestuetzte) mit ``ε`` -- und fuer die Klasse 4
die mitwirkende Breite nach 4.5.3, mit den kleinsten Beulwerten der
Tabelle 9 -- im Kasten mit dem genaueren Abminderungsfaktor (70). Woher ``α`` und ``ψ`` kommen und wo ein Blech liegt, weiss der
Querschnitt (:mod:`opencivil.stahlbau.querschnitt`); hier stehen nur die
Formeln der Norm, jede an einer Stelle.

α UND ψ:
``α`` ist der Anteil der Breite, der plastisch gedrueckt ist, ``ψ`` das
Verhaeltnis der elastischen Spannungen an den Raendern, Druck positiv: 1 bei
gleichmaessigem Druck, -1 bei Biegung um die Mitte. Beim einseitig
gestuetzten Blech zaehlt dazu, welcher Rand staerker gedrueckt ist: der
freie (Tabelle 5b, mittlere Zeilen, ``k₁``) oder der gehaltene (untere,
``k₂``). Gedrueckt ist ganz, was ``α = 1`` und ``ψ = 1`` hat: dafuer nennt
Tabelle 5b eigene Grenzen, 14 ε statt 21 ε √k₁ = 13.8 ε.

AUSSERHALB DER BEREICHE -- nach Vorgabe, nicht nachgeschlagen:
``k₁`` gilt fuer ψ ≥ -3, ``k₂`` fuer ψ ≥ -1 und der kleinste Beulwert der
beidseitig gelenkig gelagerten Scheibe fuer ψ ≥ -1.2. Darunter gilt der Wert
am Rand des Bereichs: alle drei wachsen, je weiter ψ faellt -- der Randwert
liegt auf der sicheren Seite. Ebenso der Beulwert eines einseitig gehaltenen
Blechs fuer seine mitwirkende Breite: Tabelle 9 nennt ihn nur fuer ψ = 1, 0
und -1, und dort trifft ihn ``k₁`` oder ``k₂`` der Tabelle 5b auf 1 %. Und
(70) rechnet mit ψ nicht unter -3, wie ``k₁``.

DER KASTEN:
Fuer Kastentraeger sei die Naeherung ρ = 0.9/λ_p zu ungenau (4.5.3.4); dort
gilt (70). Ein Rechteckrohr ist ein Kasten -- und (70) gilt hier fuer jede
seiner Waende, nicht nur fuer den Druckflansch, den 5.6.4.3 nennt (nach
Vorgabe, nicht nachgeschlagen).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from opencivil.stahlprofile.bleche import Halterung

#: Wo die Grenzen stehen -- je Halterung ihre Tabelle (:attr:`Halterung.tabelle`).
REFERENZ_KLASSE = "SIA 263:2013, 4.3.1, Tabellen 5a und 5b"
REFERENZ_EPSILON = "SIA 263:2013, Tabelle 5b"
REFERENZ_BEULWERT = "SIA 263:2013, 4.5.3.7, Tabelle 9"
REFERENZ_BREITE = "SIA 263:2013, 4.5.3.2, (11); 4.5.3.3"
REFERENZ_KASTEN = "SIA 263:2013, 4.5.3.4; 5.6.4.3, (70)"

#: Ohne Grenze -- ein Blech, das nicht gedrueckt ist.
OHNE = math.inf


def epsilon(f_y: float) -> float:
    """``ε = √(235/f_y)``, ``f_y`` in N/mm² (Tabelle 5b, unten)."""
    return math.sqrt(235.0 / f_y)


@dataclass(frozen=True)
class Grenzen:
    """Die groesste Schlankheit ``c/t`` (beim Rohr ``D/t``) der Klassen 1, 2 und 3."""

    werte: Tuple[float, float, float]

    def klasse(self, schlankheit: float) -> int:
        """Die kleinste Klasse, deren Grenze die Schlankheit einhaelt -- sonst 4."""
        return next((i + 1 for i, g in enumerate(self.werte) if schlankheit <= g), 4)


def k_1(psi: float) -> float:
    """Beulwert, wenn der freie Rand gedrueckt ist (Tabelle 5b) -- siehe Dateikopf fuer ψ < -3."""
    psi = max(psi, -3.0)
    return 0.57 - 0.21 * psi + 0.07 * psi * psi


def k_2(psi: float) -> float:
    """Beulwert, wenn der gehaltene Rand gedrueckt ist (Tabelle 5b) -- siehe Dateikopf fuer ψ < -1."""
    psi = max(psi, -1.0)
    return 0.578 / (0.34 + psi) if psi >= 0.0 else 1.7 - 5.0 * psi + 17.1 * psi * psi


def grenzen(halterung: Halterung, eps: float, alpha: float, psi: Optional[float],
            frei_gedrueckt: bool = False) -> Grenzen:
    """
    Die Grenzen eines Blechs -- siehe Dateikopf. ``alpha`` null heisst
    plastisch nicht gedrueckt, ``psi`` ``None`` elastisch nicht gedrueckt:
    dort gilt keine Grenze der Klassen 1 und 2, hier keine der Klasse 3.
    """
    if halterung is Halterung.ROHR:
        e2 = eps * eps
        return Grenzen((50.0 * e2, 70.0 * e2, 90.0 * e2))
    if halterung is Halterung.BEIDSEITIG:
        if alpha <= 0.0:
            plastisch = (OHNE, OHNE)
        elif alpha > 0.5:
            plastisch = (396.0 * eps / (13.0 * alpha - 1.0), 456.0 * eps / (13.0 * alpha - 1.0))
        else:
            plastisch = (36.0 * eps / alpha, 41.5 * eps / alpha)
        if psi is None:
            elastisch = OHNE
        elif psi > -1.0:
            elastisch = 42.0 * eps / (0.67 + 0.33 * psi)
        else:
            elastisch = 62.0 * eps * (1.0 - psi) * math.sqrt(-psi)
        return Grenzen((*plastisch, elastisch))
    hoch = 1.0 if frei_gedrueckt else 1.5
    plastisch = (OHNE, OHNE) if alpha <= 0.0 else (9.0 * eps / alpha ** hoch, 10.0 * eps / alpha ** hoch)
    if psi is None:
        elastisch = OHNE
    elif psi >= 1.0:
        elastisch = 14.0 * eps
    else:
        elastisch = 21.0 * eps * math.sqrt(k_1(psi) if frei_gedrueckt else k_2(psi))
    return Grenzen((*plastisch, elastisch))


def beulwert(halterung: Halterung, psi: float, frei_gedrueckt: bool = False) -> float:
    """
    Der kleinste Beulwert ``k`` fuer die mitwirkende Breite (Tabelle 9):
    beidseitig gelenkig gelagert nach der Formel der Tabelle, einseitig nach
    ``k₁`` oder ``k₂`` -- siehe Dateikopf.
    """
    if halterung is Halterung.EINSEITIG:
        return k_1(psi) if frei_gedrueckt else k_2(psi)
    psi = max(psi, -1.2)
    return 16.0 / (math.sqrt((1.0 + psi) ** 2 + 0.112 * (1.0 - psi) ** 2) + 1.0 + psi)


def plattenschlankheit(b: float, t: float, eps: float, k: float) -> float:
    """Die bezogene Plattenschlankheit ``λ_p = (b/t) / (28.4 ε √k)`` (4.5.3.3)."""
    return b / t / (28.4 * eps * math.sqrt(k))


def abminderung(lambda_p: float) -> float:
    """Der Abminderungsfaktor ``ρ = 0.9/λ_p`` der mitwirkenden Breite (4.5.3.3), hoechstens 1."""
    return min(1.0, 0.9 / lambda_p)


def abminderung_kasten(lambda_p: float, psi: float) -> float:
    """
    Der Abminderungsfaktor einer beidseitig gestuetzten Wand im Kasten, (70),
    hoechstens 1 -- siehe Dateikopf.
    """
    psi = max(psi, -3.0)
    return min(1.0, (lambda_p - 0.055 * (3.0 + psi)) / (lambda_p * lambda_p))
