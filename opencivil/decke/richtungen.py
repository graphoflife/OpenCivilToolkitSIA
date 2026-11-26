"""
opencivil/decke/richtungen.py -- die zwei Richtungen, die eine Platte selbst wählt.

VERANTWORTUNG:
Für jede Platte mit ``von_selbst`` (:class:`~opencivil.decke.modell.Platte`)
Richtung 1 und 2 der Lastabtragung, entlang ihrer Ränder -- bevor die Decke
in Streifen zerfällt (:func:`~opencivil.decke.rechnung.rechnen`). Die übrigen
Platten behalten ihre Richtungen, wie der Benutzer sie gab.

DIE REGEL:
* Platten, die von selbst wählen und aneinanderstossen -- ein Stück Rand
  gemeinsam haben, nicht nur eine Ecke --, bekommen dieselben Richtungen,
  damit ihre Streifen über die Fuge laufen. Eine Platte mit Richtungen von
  Hand ändert nichts an denen daneben.
* Richtung 1 läuft parallel zu den meisten Metern Rand; ein Rand quer dazu
  zählt mit, denn Richtung 2 steht rechtwinklig auf ihr. Es zählt der Rand
  einer Gruppe nach aussen, keine Fuge in ihr. Richtung 1 liegt über −45°
  bis 45° gegen x; bei gleich vielen Metern gilt die näher an x.
* Nach Vorgabe, nicht nachgeschlagen: die Norm lässt jede Aufteilung der
  Last zu, die im Gleichgewicht ist (SIA 262:2025, 4.1.4.2.2). Geplant war
  der nach Länge gewichtete Mittelwert der Randrichtungen. Er legte die
  Streifen eines Trapezes mit einem schiefen Rand schief zu allen Rändern:
  unten 6 m, oben 4 m, 5 m hoch, auf −4.9° statt auf 0°.
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Dict, List, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Decke, Platte

#: So nahe liegen zwei Ränder einer Fuge mindestens beieinander, in m -- und so lang ist sie mindestens.
FUGE = 1e-6

#: Unter diesem Winkel laufen zwei Ränder gleich, in rad -- wie :data:`~opencivil.decke.streifen.PARALLEL`.
GLEICH = 1e-6

Kante = Tuple[Punkt, Punkt]


def festgelegt(decke: Decke) -> Decke:
    """Die Decke, in der jede Platte mit ``von_selbst`` ihre Richtungen gewählt hat -- die übrigen, wie sie sind."""
    selbst = [i for i, p in enumerate(decke.platten) if p.von_selbst]
    if not selbst:
        return decke
    richtungen: Dict[int, Tuple[float, float]] = {}
    for gruppe in _gruppen([decke.platten[i] for i in selbst]):
        platten = [decke.platten[selbst[j]] for j in gruppe]
        richtungen.update({selbst[j]: entlang(raender(platten)) for j in gruppe})
    return replace(decke, platten=[replace(p, richtungen=richtungen[i]) if i in richtungen else p
                                   for i, p in enumerate(decke.platten)])


def entlang(raender: Sequence[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Richtung 1 und 2 in rad zu Rändern, je ``(Winkel, Länge)``: Richtung 1
    parallel zu den meisten Metern -- ein Rand quer dazu zählt mit --, über
    −45° bis 45°; bei gleich vielen Metern die näher an x. Ohne Rand x und y.
    """
    meter: List[List[float]] = []
    for winkel, laenge in raender:
        w = math.pi / 4.0 - (math.pi / 4.0 - winkel) % (math.pi / 2.0)
        gleich = next((m for m in meter if _abstand(m[0], w) < GLEICH), None)
        if gleich is None:
            meter.append([w, laenge])
        else:
            gleich[1] += laenge
    if not meter:
        return 0.0, math.pi / 2.0
    w, _ = max(meter, key=lambda m: (round(m[1], 9), -abs(m[0]), m[0]))
    return w, w + math.pi / 2.0


def raender(platten: Sequence[Platte]) -> List[Tuple[float, float]]:
    """Je Rand der Platten sein Winkel in rad und seine Länge nach aussen, in m -- was in einer Fuge liegt, zählt nicht."""
    kanten = [_kanten(p) for p in platten]
    heraus = []
    for i, eigene in enumerate(kanten):
        for a, b in eigene:
            fuge = sum(gemeinsam((a, b), k) for j, andere in enumerate(kanten) if j != i for k in andere)
            if math.dist(a, b) - fuge > FUGE:
                heraus.append((math.atan2(b[1] - a[1], b[0] - a[0]), math.dist(a, b) - fuge))
    return heraus


def gemeinsam(k: Kante, m: Kante) -> float:
    """Wie lang zwei Ränder aufeinander liegen, in m -- null, wenn sie sich nur kreuzen oder an einer Ecke treffen."""
    (a, b), (c, d) = k, m
    laenge = math.dist(a, b)
    if laenge <= FUGE:
        return 0.0
    n = ((b[0] - a[0]) / laenge, (b[1] - a[1]) / laenge)
    if any(abs((p[0] - a[0]) * n[1] - (p[1] - a[1]) * n[0]) > FUGE for p in (c, d)):
        return 0.0
    s, t = sorted((p[0] - a[0]) * n[0] + (p[1] - a[1]) * n[1] for p in (c, d))
    ueber = min(laenge, t) - max(0.0, s)
    return ueber if ueber > FUGE else 0.0


def _gruppen(platten: Sequence[Platte]) -> List[List[int]]:
    """Die Platten, die aneinanderstossen, je in einer Gruppe -- als Stellen in ``platten``, in ihrer Folge."""
    kanten = [_kanten(p) for p in platten]
    gruppen: List[List[int]] = []
    for i in range(len(platten)):
        nachbarn = [g for g in gruppen if any(_stossen(kanten[i], kanten[j]) for j in g)]
        gruppen = [g for g in gruppen if g not in nachbarn] + [sorted([i, *(j for g in nachbarn for j in g)])]
    return sorted(gruppen)


def _stossen(a: Sequence[Kante], b: Sequence[Kante]) -> bool:
    return any(gemeinsam(k, m) > 0.0 for k in a for m in b)


def _kanten(p: Platte) -> List[Kante]:
    ecken = geo.bereinigt(list(p.ecken))
    return list(zip(ecken, ecken[1:] + ecken[:1]))


def _abstand(v: float, w: float) -> float:
    """Wie weit zwei Winkel auseinander liegen, über 90° gefaltet -- −45° und 45° sind derselbe."""
    return abs((v - w + math.pi / 4.0) % (math.pi / 2.0) - math.pi / 4.0)
