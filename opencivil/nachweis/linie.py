"""
opencivil/nachweis/linie.py -- Geometrie einer geschlossenen M-N-Linie.

VERANTWORTUNG:
Punkt-in-Linie, Schnitte mit einer Geraden, kuerzester Abstand. Reine
Geometrie -- von Beton, Stahl und Norm weiss dieser Baustein nichts.

WARUM EIGENSTAENDIG:
Es gibt zwei Resistenzlinien: die punktweise aus Dehnungsebenen aufgebaute
(:mod:`opencivil.nachweis.dehnungsfaecher`) und das Polygon aus der
Handrechnung (:mod:`opencivil.nachweis.handrechnung`). Beide werden auf genau
dieselbe Art ausgewertet. Laege die Geometrie bei einer der beiden, muesste die
andere sie entweder einbinden -- was einen Ring ergaebe -- oder nachbauen. Das
zweite waere der Anfang vom Auseinanderlaufen.

DIE ACHSE IST EIN WERT:
Ob ein Widerstand bei festgehaltener Normalkraft (waagrecht) oder bei
festgehaltenem Moment (senkrecht) gesucht wird, steckt in :class:`Achse`.
Vorher stand dieselbe Unterscheidung vierfach da -- als Funktionspaar
``..._bei_N``/``..._bei_M``, als ``positiv``-Schalter, als Zeichenkette ``"M"``
und als Enum-Mitglied -- und wurde an sechs Stellen abgefragt. Jetzt gibt es
sie einmal, und die Funktionen hier kennen nur noch *eine* Achse und ihre
Gegenachse.

VORZEICHEN:
    N > 0   Zug
    M > 0   Zug an der Unterseite
Ein Punkt ist alles, was ``N`` und ``M`` hat; die Linie ist eine Folge solcher
Punkte, deren letzter mit dem ersten verbunden gedacht wird.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol, Sequence, Tuple

from opencivil.core.einheiten import KN, KNM, Einheit


class Punkt(Protocol):
    """Alles, was eine Normalkraft und ein Moment hat."""

    N: float
    M: float


@dataclass(frozen=True)
class Stelle:
    """Ein schlichter Punkt der M-N-Ebene -- etwa eine Einwirkung."""

    N: float
    M: float


@dataclass(frozen=True)
class Achse:
    """
    Eine der beiden Achsen der M-N-Ebene, samt allem, was sie unterscheidet.

    ``name`` ist zugleich der Feldname eines :class:`Punkt` -- damit kommt
    :meth:`von` ohne Fallunterscheidung aus.
    """

    name: str
    """``"M"`` oder ``"N"``."""

    gegen_name: str
    einheit: Einheit
    beschriftung: str

    widerstand: str
    """Ausgeschrieben, weil die Fugenform sich nicht anhaengen laesst:
    "Momentenwiderstand", nicht "Momentswiderstand"."""

    def von(self, punkt: Punkt) -> float:
        """Der Wert dieses Punktes auf dieser Achse."""
        return getattr(punkt, self.name)

    @property
    def gegen(self) -> "Achse":
        """Die andere Achse -- die bei einem Schnitt festgehalten wird."""
        return ACHSEN[self.gegen_name]


MOMENT = Achse("M", "N", KNM, "Moment", "Momentenwiderstand")
NORMALKRAFT = Achse("N", "M", KN, "Normalkraft", "Normalkraftwiderstand")

#: Nachschlagewerk fuer :attr:`Achse.gegen`. Nach den Konstanten gefuellt,
#: weil eine eingefrorene Datenklasse sich nicht selbst referenzieren kann.
ACHSEN: Dict[str, Achse] = {"M": MOMENT, "N": NORMALKRAFT}


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


def _schnittpunkte(linie: Sequence[Punkt], achse: Achse, fest: float):
    """
    Alle Kanten, die die Gerade ``achse.gegen = fest`` schneiden.

    Liefert Tripel ``(Wert auf achse, Punkt a, Punkt b)``. Die einzige Stelle,
    an der ueber die Linie gelaufen wird -- alles Weitere waehlt daraus aus.
    """
    lauf = achse.gegen
    anzahl = len(linie)
    for i in range(anzahl):
        a, b = linie[i], linie[(i + 1) % anzahl]
        la, lb = lauf.von(a), lauf.von(b)
        if (la > fest) != (lb > fest) and lb != la:
            ga, gb = achse.von(a), achse.von(b)
            yield ga + (fest - la) * (gb - ga) / (lb - la), a, b


def schnitte(linie: Sequence[Punkt], achse: Achse, fest: float) -> List[float]:
    """Alle Werte auf ``achse``, bei denen ``achse.gegen = fest`` die Linie trifft."""
    return [wert for wert, _, _ in _schnittpunkte(linie, achse, fest)]


def kante(
    linie: Sequence[Punkt], achse: Achse, fest: float, positiv: bool
) -> Optional[Tuple[float, Punkt, Punkt]]:
    """
    Der aeusserste Schnittpunkt -- mit den beiden Eckpunkten, zwischen denen er liegt.

    Die Eckpunkte braucht die Mitschrift: dort soll stehen, *zwischen welchen
    beiden* interpoliert wurde, nicht bloss das Ergebnis. Sonst waere die Zahl
    wieder nicht von Hand nachvollziehbar -- und genau darum geht es hier.
    """
    treffer = list(_schnittpunkte(linie, achse, fest))
    if not treffer:
        return None
    return max(treffer, key=lambda t: t[0]) if positiv else min(treffer, key=lambda t: t[0])


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
