"""
opencivil/fachwerkmodell/nachrechnung.py -- ein gefundenes Fachwerk, nachgerechnet.

VERANTWORTUNG:
Was die Rechnung an einem Fachwerk prüft, das die Suche gefunden hat und
das im Projekt steht (:func:`nachrechnen`): an jedem Knoten die Summe der
Stabkräfte und Lasten -- wo ein Lager hält, nimmt es sie auf, sonst muss
sie null sein --, die Kräfte der Lager und das Ziel der Optimierung,
``V = Σ l · (w_Z · N⁺ + N⁻)``. Ihr wird nichts geglaubt, was sich
nachrechnen lässt: das Gleichgewicht folgt aus den Stäben, wie sie
dastehen.

WAS OFFEN BLEIBT:
Geht das Gleichgewicht nicht auf, steht je Last, die es nicht trägt, was
offen bleibt -- eine Last neben jedem Stab, eine Scheibe, deren Teil kein
Lager hat. Die Grenze ist ein Millionstel der grössten Last (nach Vorgabe).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.fachwerkmodell.modell import Lager, Last, Modell
from opencivil.fachwerkmodell.suche import OFFEN_HOECHSTENS, W_DRUCK, Fachwerk


@dataclass(frozen=True)
class Lagerkraft:
    """Was ein Lager aufnimmt, in N: ``R_x`` nach rechts, ``R_y`` nach oben."""

    lager: Lager
    R_x: float
    R_y: float


@dataclass(frozen=True)
class Nachrechnung:
    """Was die Rechnung am Fachwerk fand."""

    fachwerk: Fachwerk
    laengen: Tuple[float, ...]
    """Je Stab in m."""

    lagerkraefte: Tuple[Lagerkraft, ...]
    offen: Tuple[Tuple[Optional[Last], Punkt, float], ...]
    """Wo das Gleichgewicht nicht aufgeht: die Last dort -- oder keine --, der Ort und der Betrag in N."""

    V: float
    """``Σ l · (w_Z · N⁺ + N⁻)`` in N·m."""

    w_Z: float

    @property
    def im_gleichgewicht(self) -> bool:
        return not self.offen


def nachrechnen(modell: Modell, fachwerk: Fachwerk, w_Z: float) -> Nachrechnung:
    """Siehe Dateikopf."""
    knoten = fachwerk.knoten
    laengen = tuple(math.dist(knoten[a], knoten[b]) for a, b, _ in fachwerk.staebe)
    summe: Dict[int, List[float]] = {k: [0.0, 0.0] for k in range(len(knoten))}
    for (a, b, N), l in zip(fachwerk.staebe, laengen):
        # Ein Stab unter Zug zieht jeden seiner Knoten zum andern hin.
        cx, cy = (knoten[b][0] - knoten[a][0]) / l, (knoten[b][1] - knoten[a][1]) / l
        summe[a][0] += N * cx
        summe[a][1] += N * cy
        summe[b][0] -= N * cx
        summe[b][1] -= N * cy
    # Lasten an Orten ohne Knoten bekommen einen eigenen Platz: dort trägt nichts.
    orte = list(knoten)
    lasten_an: Dict[int, List[Last]] = {}
    for f in modell.lasten:
        k = _platz(orte, f.ort)
        if k is None:
            k = len(orte)
            orte.append(f.ort)
            summe[k] = [0.0, 0.0]
        summe[k][0] += f.F_x
        summe[k][1] += f.F_y
        lasten_an.setdefault(k, []).append(f)
    kraefte = []
    gehalten = set()
    for lager in modell.lager:
        k = _platz(orte, lager.ort)
        R = [0.0, 0.0]
        if k is not None:
            for r, haelt in ((0, lager.halt.x), (1, lager.halt.y)):
                if haelt and (k, r) not in gehalten:
                    R[r] = -summe[k][r]
                    gehalten.add((k, r))
        kraefte.append(Lagerkraft(lager, R[0], R[1]))
    grenze = OFFEN_HOECHSTENS * max((math.hypot(f.F_x, f.F_y) for f in modell.lasten), default=1.0)
    offen = []
    for k, (sx, sy) in summe.items():
        rx = 0.0 if (k, 0) in gehalten else sx
        ry = 0.0 if (k, 1) in gehalten else sy
        betrag = math.hypot(rx, ry)
        if betrag > grenze:
            last = lasten_an.get(k, [None])[0]
            offen.append((last, orte[k], betrag))
    V = math.fsum(l * (w_Z * N if N > 0.0 else -W_DRUCK * N)
                  for (_, _, N), l in zip(fachwerk.staebe, laengen))
    return Nachrechnung(fachwerk=fachwerk, laengen=laengen, lagerkraefte=tuple(kraefte),
                        offen=tuple(offen), V=V, w_Z=w_Z)


def _platz(orte: List[Punkt], p: Punkt) -> Optional[int]:
    return next((k for k, q in enumerate(orte)
                 if abs(p[0] - q[0]) <= geo.TOLERANZ and abs(p[1] - q[1]) <= geo.TOLERANZ), None)
