"""
opencivil/nachweis/linie.py -- Geometrie einer geschlossenen M-N-Linie.

VERANTWORTUNG:
Punkt-in-Linie, Schnitte mit einer Waagrechten oder Senkrechten, kuerzester
Abstand. Reine Geometrie -- von Beton, Stahl und Norm weiss dieser Baustein
nichts.

WARUM EIGENSTAENDIG:
Es gibt zwei Resistenzlinien: die punktweise aus Dehnungsebenen aufgebaute
(:mod:`opencivil.nachweis.biegung_normalkraft`) und das Polygon aus der
Handrechnung (:mod:`opencivil.nachweis.handrechnung`). Beide werden auf genau
dieselbe Art ausgewertet. Laege die Geometrie bei einer der beiden, muesste die
andere sie entweder einbinden -- was einen Ring ergaebe -- oder nachbauen. Das
zweite waere der Anfang vom Auseinanderlaufen.

VORZEICHEN:
    N > 0   Zug
    M > 0   Zug an der Unterseite
Ein Punkt ist alles, was ``N`` und ``M`` hat; die Linie ist eine Folge solcher
Punkte, deren letzter mit dem ersten verbunden gedacht wird.
"""

from __future__ import annotations

import math
from typing import List, Protocol, Sequence, Tuple


class Punkt(Protocol):
    """Alles, was eine Normalkraft und ein Moment hat."""

    N: float
    M: float


def innerhalb(N: float, M: float, linie: Sequence[Punkt]) -> bool:
    """Punkt-in-Polygon nach dem Strahlverfahren."""
    innen = False
    anzahl = len(linie)
    for i in range(anzahl):
        a, b = linie[i], linie[(i + 1) % anzahl]
        if (a.M > M) != (b.M > M):
            if b.M != a.M:
                schnitt = a.N + (M - a.M) * (b.N - a.N) / (b.M - a.M)
                if N < schnitt:
                    innen = not innen
    return innen


def schnitte_bei_N(linie: Sequence[Punkt], N: float) -> List[float]:
    """Alle Momente, bei denen die Linie die Waagrechte N = const schneidet."""
    treffer: List[float] = []
    anzahl = len(linie)
    for i in range(anzahl):
        a, b = linie[i], linie[(i + 1) % anzahl]
        if (a.N > N) != (b.N > N) and b.N != a.N:
            treffer.append(a.M + (N - a.N) * (b.M - a.M) / (b.N - a.N))
    return treffer


def schnitte_bei_M(linie: Sequence[Punkt], M: float) -> List[float]:
    """Alle Normalkraefte, bei denen die Linie die Senkrechte M = const schneidet."""
    treffer: List[float] = []
    anzahl = len(linie)
    for i in range(anzahl):
        a, b = linie[i], linie[(i + 1) % anzahl]
        if (a.M > M) != (b.M > M) and b.M != a.M:
            treffer.append(a.N + (M - a.M) * (b.N - a.N) / (b.M - a.M))
    return treffer


def kante_bei_N(linie: Sequence[Punkt], N: float, positiv: bool
                ) -> Tuple[float, Punkt, Punkt] | None:
    """
    Wie :func:`schnitte_bei_N`, gibt aber die Kante mit zurueck.

    Gebraucht fuer die Mitschrift: dort soll stehen, *zwischen welchen beiden
    Eckpunkten* interpoliert wurde, nicht bloss das Ergebnis. Sonst waere die
    Zahl wieder nicht von Hand nachvollziehbar -- und genau darum geht es hier.
    """
    bester = None
    anzahl = len(linie)
    for i in range(anzahl):
        a, b = linie[i], linie[(i + 1) % anzahl]
        if (a.N > N) != (b.N > N) and b.N != a.N:
            M = a.M + (N - a.N) * (b.M - a.M) / (b.N - a.N)
            if bester is None or (M > bester[0] if positiv else M < bester[0]):
                bester = (M, a, b)
    return bester


def kante_bei_M(linie: Sequence[Punkt], M: float, positiv: bool
                ) -> Tuple[float, Punkt, Punkt] | None:
    """Dasselbe fuer die Senkrechte M = const."""
    bester = None
    anzahl = len(linie)
    for i in range(anzahl):
        a, b = linie[i], linie[(i + 1) % anzahl]
        if (a.M > M) != (b.M > M) and b.M != a.M:
            N = a.N + (M - a.M) * (b.N - a.N) / (b.M - a.M)
            if bester is None or (N > bester[0] if positiv else N < bester[0]):
                bester = (N, a, b)
    return bester


def ohne_wiederholungen(linie: Sequence, toleranz: float = 1e-7) -> List:
    """
    Entfernt aufeinanderfolgende Punkte, die auf dieselbe Stelle fallen.

    Solange saemtliche Bewehrung fliesst und der Beton gerissen ist, aendert
    eine Drehung der Dehnungsebene nichts an N und M -- am reinen Zug entstehen
    so dutzende deckungsgleiche Punkte, und an der Nahtstelle der beiden Faecher
    liegt der Punkt des reinen Drucks doppelt vor. Fuer die Geometrie sind das
    entartete Segmente: Punkt-in-Polygon und Schnittsuche stolpern darueber, und
    gezeichnet ergeben sie Nullflaechen.
    """
    if not linie:
        return []
    bezug_n = max(abs(p.N) for p in linie) or 1.0
    bezug_m = max(abs(p.M) for p in linie) or 1.0

    def verschieden(a, b) -> bool:
        return (abs(a.N - b.N) / bezug_n > toleranz
                or abs(a.M - b.M) / bezug_m > toleranz)

    gefiltert = [linie[0]]
    for punkt in linie[1:]:
        if verschieden(punkt, gefiltert[-1]):
            gefiltert.append(punkt)
    # Auch der Ringschluss darf nicht doppelt sein.
    while len(gefiltert) > 2 and not verschieden(gefiltert[-1], gefiltert[0]):
        gefiltert.pop()
    return gefiltert


def naechster_punkt(
    N: float, M: float, linie: Sequence[Punkt], N_ref: float, M_ref: float
) -> Tuple[float, Tuple[float, float]]:
    """
    Kuerzester Abstand zur Linie im normierten Diagramm.

    Ohne Normierung waere der Abstand von der Wahl der Einheiten abhaengig --
    kN und kNm lassen sich nicht sinnvoll gegeneinander aufrechnen.
    """
    px, py = N / N_ref, M / M_ref
    bester = float("inf")
    stelle = (linie[0].N, linie[0].M)

    for i in range(len(linie)):
        a, b = linie[i], linie[(i + 1) % len(linie)]
        ax, ay = a.N / N_ref, a.M / M_ref
        bx, by = b.N / N_ref, b.M / M_ref
        dx, dy = bx - ax, by - ay
        laenge = dx * dx + dy * dy
        t = (0.0 if laenge == 0.0
             else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / laenge)))
        qx, qy = ax + t * dx, ay + t * dy
        abstand = math.hypot(px - qx, py - qy)
        if abstand < bester:
            bester = abstand
            stelle = (qx * N_ref, qy * M_ref)
    return bester, stelle
