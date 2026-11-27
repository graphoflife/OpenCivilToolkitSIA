"""
opencivil/decke/fem/belastung.py -- die Lasten eines Falls auf den Knoten.

VERANTWORTUNG:
Je Lastfall, was auf jeden Knoten des Netzes drückt, in N nach unten, dazu
die ganze Last und was davon neben den Platten liegt. Die Flächen kommen
von :func:`~opencivil.decke.lasten.flaechen`, wie in der Streifenmethode:
eine Flächenlast, eine Einzellast über ihre Verteilfläche ``l_x × l_y``, das
Eigengewicht der Platten. Linienlasten und die Stege der Träger
(:func:`~opencivil.decke.lasten.stege`) liegen auf Linien des Netzes.

WIE EINE LAST AN DIE KNOTEN GEHT:
Was in einem Dreieck liegt, geht an seine drei Ecken nach den
Schwerpunktkoordinaten seiner Resultierenden -- eine gleichmässige Last
über das ganze Dreieck je zu einem Drittel. Was auf einem Stück einer
Linie liegt, geht je zur Hälfte an seine Enden. Das DKT legt w im Innern
nicht fest; die Last geht darum an die Ecken, als wäre w dort linear (nach
Vorgabe, nicht nachgeschlagen). Die Summe stimmt immer, und mit feinerem
Netz auch die Verteilung.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.fem.netz import Linie, Netz
from opencivil.decke.geometrie import Punkt
from opencivil.decke.lasten import DANEBEN, flaechen, kn, stege
from opencivil.decke.modell import Decke, Lastfall, Linienlast
from opencivil.stabwerk.system import Meldung


@dataclass
class Knotenlasten:
    """Je Knoten die Kraft nach unten in N -- und die Summen."""

    kraefte: List[float]
    summe: float = 0.0
    """Alle Lasten zusammen, in N."""

    daneben: float = 0.0
    """Was davon neben den Platten liegt, in N."""

    meldungen: List[Meldung] = field(default_factory=list)

    def mal(self, faktor: float) -> "Knotenlasten":
        return Knotenlasten([faktor * F for F in self.kraefte], faktor * self.summe, faktor * self.daneben)

    def plus(self, andere: "Knotenlasten") -> "Knotenlasten":
        return Knotenlasten([a + b for a, b in zip(self.kraefte, andere.kraefte)],
                            self.summe + andere.summe, self.daneben + andere.daneben)


class Raster:
    """Die Dreiecke des Netzes in Zellen der Netzweite -- damit eine Fläche nur die nahen schneidet."""

    def __init__(self, netz: Netz) -> None:
        self.netz = netz
        self.weite = netz.weite
        self.zellen: Dict[Tuple[int, int], List[int]] = {}
        for e, d in enumerate(netz.dreiecke):
            x0, y0, x1, y1 = _rahmen([netz.knoten[k] for k in d])
            for i in range(math.floor(x0 / self.weite), math.floor(x1 / self.weite) + 1):
                for j in range(math.floor(y0 / self.weite), math.floor(y1 / self.weite) + 1):
                    self.zellen.setdefault((i, j), []).append(e)

    def nahe(self, ecken: Sequence[Punkt]) -> List[int]:
        """Die Dreiecke, deren Rahmen den Rahmen von ``ecken`` trifft -- jedes einmal."""
        x0, y0, x1, y1 = _rahmen(ecken)
        gesehen = set()
        for i in range(math.floor(x0 / self.weite), math.floor(x1 / self.weite) + 1):
            for j in range(math.floor(y0 / self.weite), math.floor(y1 / self.weite) + 1):
                gesehen.update(self.zellen.get((i, j), ()))
        return sorted(gesehen)

    def bei(self, p: Punkt) -> Tuple[int, Tuple[float, float, float]]:
        """Das Dreieck, in dem ``p`` liegt, und die Schwerpunktkoordinaten dort -- ``(-1, …)``, wenn in keinem."""
        zelle = (math.floor(p[0] / self.weite), math.floor(p[1] / self.weite))
        for e in self.zellen.get(zelle, ()):
            l = schwerpunktkoordinaten(self.netz, e, p)
            if min(l) >= -1e-9:
                return e, l
        return -1, (0.0, 0.0, 0.0)


def _rahmen(ecken: Sequence[Punkt]) -> Tuple[float, float, float, float]:
    xs = [p[0] for p in ecken]
    ys = [p[1] for p in ecken]
    return min(xs), min(ys), max(xs), max(ys)


def schwerpunktkoordinaten(netz: Netz, e: int, p: Punkt) -> Tuple[float, float, float]:
    """``(λ_1, λ_2, λ_3)`` von ``p`` im Dreieck ``e``: je der Anteil seiner Ecke, zusammen eins."""
    (x1, y1), (x2, y2), (x3, y3) = (netz.knoten[k] for k in netz.dreiecke[e])
    det = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    l2 = ((p[0] - x1) * (y3 - y1) - (x3 - x1) * (p[1] - y1)) / det
    l3 = ((x2 - x1) * (p[1] - y1) - (p[0] - x1) * (y2 - y1)) / det
    return 1.0 - l2 - l3, l2, l3


def belasten(decke: Decke, netz: Netz, raster: Raster, lastfall: Lastfall) -> Knotenlasten:
    """Die Lasten des Lastfalls auf den Knoten."""
    heraus = Knotenlasten([0.0] * len(netz.knoten))
    nummer = {p.name: i for i, p in enumerate(decke.platten)}
    for f in flaechen(decke, lastfall, heraus.meldungen):
        if not f.q:
            continue
        if f.platte:
            gesamt = f.q * abs(geo.flaeche(f.ecken))
            getragen = 0.0
            for e, d in enumerate(netz.dreiecke):
                if netz.platte[e] == nummer[f.platte]:
                    F = f.q * netz.flaeche(e)
                    getragen += F
                    for k in d:
                        heraus.kraefte[k] += F / 3.0
        else:
            stuecke = geo.dreiecke(f.ecken)
            gesamt = f.q * sum(abs(geo.flaeche(s)) for s in stuecke)
            getragen = sum(_flaeche_verteilen(heraus.kraefte, netz, raster, s, f.q) for s in stuecke)
        _summe(heraus, f.name, "Die Last", gesamt, getragen)
    kanten = netz.kanten()
    for last in [*lastfall.lasten, *(stege(decke) if lastfall.eigengewicht else ())]:
        if isinstance(last, Linienlast) and last.wert and math.dist(last.a, last.b) > geo.TOLERANZ:
            linie = netz.auf_strecke(Linie(last.name, "linienlast", last.a, last.b), kanten)
            getragen = 0.0
            for p, q in linie.stuecke:
                F = last.wert * math.dist(netz.knoten[p], netz.knoten[q])
                getragen += F
                heraus.kraefte[p] += F / 2.0
                heraus.kraefte[q] += F / 2.0
            _summe(heraus, last.name, "Die Linienlast", last.wert * linie.laenge, getragen)
    return heraus


def _flaeche_verteilen(kraefte: List[float], netz: Netz, raster: Raster, stueck: Sequence[Punkt],
                       q: float) -> float:
    """Ein konvexes Stück mit ``q`` in N/m² auf die Ecken der Dreiecke, die es deckt -- zurück: was es trägt."""
    getragen = 0.0
    for e in raster.nahe(stueck):
        c = geo.schnitt(stueck, [netz.knoten[k] for k in netz.dreiecke[e]])
        if not c:
            continue
        A = abs(geo.flaeche(c))
        if A <= 0.0:
            continue
        F = q * A
        getragen += F
        for k, l in zip(netz.dreiecke[e], schwerpunktkoordinaten(netz, e, geo.schwerpunkt(c))):
            kraefte[k] += F * l
    return getragen


def _summe(heraus: Knotenlasten, name: str, was: str, gesamt: float, getragen: float) -> None:
    """Die Last zur Summe -- und was davon neben den Platten liegt, mit Meldung wie in der Streifenmethode."""
    heraus.summe += gesamt
    if abs(gesamt - getragen) > DANEBEN * abs(gesamt):
        heraus.daneben += gesamt - getragen
        heraus.meldungen.append(Meldung(
            f"{was} «{name}» liegt zum Teil neben den Platten: {kn(abs(gesamt - getragen))} kN "
            "trägt niemand.", (name,), fehler=False))
