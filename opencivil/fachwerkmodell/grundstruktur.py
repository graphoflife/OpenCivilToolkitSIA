"""
opencivil/fachwerkmodell/grundstruktur.py -- die Knoten und die möglichen Stäbe einer Scheibe.

VERANTWORTUNG:
Die Grundstruktur des Verfahrens Ground Structure (He, Gilbert & Song
2019): Knoten in einem Raster der Weite h, soweit sie im Material liegen,
dazu jeder Punkt eines Lagers und einer Last und jede Ecke eines Umrisses
(:func:`grundstruktur`). Zwischen je zwei Knoten ein möglicher Stab, wenn
er ganz im Material liegt -- auf dem Rand eines Lochs zählt, quer durch
sein Inneres nicht; ein Stück auf einem Rand nur, wo auf einer Seite
Material ist: unter einer Türe, deren Schwelle auf dem Rand der Scheibe
liegt, ist keines. Liefe ein Stab über einen dritten Knoten, fällt er weg:
aus zwei kürzeren ist er schon da, und doppelt trüge er dieselbe Kraft auf
zwei Wegen.

DAS GLEICHGEWICHT:
Je Knoten zwei Richtungen, x und y; wo ein Lager hält, fällt die Richtung
weg -- dort nimmt es die Kraft. Die übrigen sind die Zeilen des
Gleichgewichts (:attr:`Grundstruktur.zeilen`): an jeder ist die Summe der
Stabkräfte gleich der Last, mit umgekehrtem Vorzeichen
(:meth:`Grundstruktur.spalte`).

DIE GRENZE:
Mehr als :data:`HOECHSTENS_KNOTEN` Knoten sucht das Werkzeug nicht: die
möglichen Stäbe wachsen mit dem Quadrat der Knoten, bei 300 Knoten sind es
gegen 17 000. Die Grenze ist nach Vorgabe, nicht nachgeschlagen.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cached_property
from math import gcd
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.fachwerkmodell.modell import Modell
from opencivil.fachwerkmodell.optimierung import Spalte

#: Wie viele Knoten die Grundstruktur höchstens hat -- nach Vorgabe, nicht nachgeschlagen.
HOECHSTENS_KNOTEN = 600

#: Ab wie vielen Punkten im Rechteck um die Scheibe das Raster gar nicht erst gelegt wird.
HOECHSTENS_RASTERPUNKTE = 200_000

#: Wie weit neben einem Stück auf einem Rand nach Material gesucht wird, in m:
#: weit über der Rundung der Geometrie, weit unter jedem Mass einer Scheibe.
NEBEN_DEM_RAND = 100 * geo.TOLERANZ

#: Wie weit ein waagrechter oder senkrechter Stab von seiner Richtung abweichen
#: darf, bezogen auf seine Länge -- nur so weit, wie Rundung reicht (nach Vorgabe).
ACHSPARALLEL = 1e-9


class ZuVieleKnoten(Exception):
    """Das Raster ist zu fein: der Satz sagt, wie viele Knoten es gäbe und was zu tun ist."""


@dataclass(frozen=True)
class Grundstruktur:
    """Knoten, mögliche Stäbe und die Zeilen des Gleichgewichts einer Scheibe."""

    modell: Modell
    knoten: Tuple[Punkt, ...]
    """In m: zuerst das Raster, Zeile um Zeile von unten, dann Lager, Lasten und Ecken."""

    staebe: Tuple[Tuple[int, int], ...]
    """Je möglicher Stab seine zwei Knoten."""

    laengen: Tuple[float, ...]
    zeilen: Dict[Tuple[int, int], int]
    """``(knoten, richtung)`` -> Zeile des Gleichgewichts; Richtung 0 ist x, 1 ist y."""

    last: Tuple[float, ...]
    """Je Zeile die Last in N."""

    weite: float
    aufschlag: Tuple[float, ...] = ()
    """
    Je Stab, wie viel mal mehr er in der Optimierung kostet, als seine Länge
    sagt -- leer, wenn jeder nur seine Länge kostet. Das Verfahren SIMP
    verteuert so, was neben seiner Form liegt
    (:mod:`~opencivil.fachwerkmodell.skelett`).
    """

    @cached_property
    def kosten(self) -> Tuple[float, ...]:
        """Je Stab, was er je Einheit Kraft in der Optimierung kostet: seine Länge, mit dem Aufschlag."""
        if not self.aufschlag:
            return self.laengen
        return tuple(l * a for l, a in zip(self.laengen, self.aufschlag))

    @cached_property
    def spalten(self) -> Tuple[Spalte, ...]:
        """
        Je Stab, was er mit der Kraft 1 (Zug) zu den Zeilen gibt: an seinem
        ersten Knoten seine Richtung zum zweiten negativ, am zweiten positiv --
        dort, wo kein Lager hält.
        """
        spalten = []
        for (a, b), l in zip(self.staebe, self.laengen):
            pa, pb = self.knoten[a], self.knoten[b]
            cx, cy = (pb[0] - pa[0]) / l, (pb[1] - pa[1]) / l
            spalten.append(tuple(
                (self.zeilen[(k, r)], w)
                for (k, r), w in (((a, 0), -cx), ((a, 1), -cy), ((b, 0), cx), ((b, 1), cy))
                if (k, r) in self.zeilen))
        return tuple(spalten)

    @cached_property
    def achsparallel(self) -> Tuple[bool, ...]:
        """Je Stab, ob er waagrecht oder senkrecht liegt (:func:`liegt_achsparallel`)."""
        return tuple(liegt_achsparallel(self.knoten[a], self.knoten[b]) for a, b in self.staebe)

    def knoten_bei(self, p: Punkt) -> Optional[int]:
        """Der Knoten an ``p`` -- ein Lager oder eine Last steht genau auf einem."""
        return next((k for k, q in enumerate(self.knoten) if _gleich(p, q)), None)


def grundstruktur(modell: Modell, weite: float, drin: Optional[Callable[[Punkt], bool]] = None,
                  liegt: Optional[Callable[[Punkt, Punkt], bool]] = None) -> Grundstruktur:
    """
    Die Grundstruktur der Scheibe mit der Rasterweite ``weite`` in m. Das
    Modell ist geprüft (:func:`~opencivil.fachwerkmodell.pruefen.pruefen`):
    es hat eine Scheibe, Lager und Lasten, alle im Material.
    Wirft :class:`ZuVieleKnoten`, wenn das Raster zu fein ist.

    ``drin`` sagt, wo ein Knoten liegen darf, ``liegt``, ob ein Stab von
    einem Punkt zum andern -- ohne beide im Material. Das Verfahren SIMP
    gibt so nur, was in seiner Form liegt
    (:mod:`~opencivil.fachwerkmodell.skelett`).
    """
    umrisse = [u.ecken for u in (*modell.scheiben, *modell.loecher)]
    knoten, raster, ursprung = _knoten(modell, weite, drin or modell.im_material)
    staebe = _staebe(knoten, raster, ursprung, weite,
                     liegt or (lambda a, b: im_material(modell, umrisse, a, b)))
    return aus_staeben(modell, knoten, staebe, weite)


def aus_staeben(modell: Modell, knoten: Sequence[Punkt], staebe: Sequence[Tuple[int, int]],
                weite: float, aufschlag: Sequence[float] = ()) -> Grundstruktur:
    """
    Eine Grundstruktur aus gegebenen Knoten und Stäben -- so liest auch das
    Verfahren SIMP sein Fachwerk (:mod:`~opencivil.fachwerkmodell.skelett`),
    mit einem ``aufschlag`` je Stab (:attr:`Grundstruktur.aufschlag`).
    Jedes Lager und jede Last steht genau auf einem Knoten.
    """
    laengen = tuple(math.dist(knoten[a], knoten[b]) for a, b in staebe)
    halt: Dict[int, Tuple[bool, bool]] = {}
    for lager in modell.lager:
        k = _bei(knoten, lager.ort)
        hx, hy = halt.get(k, (False, False))
        halt[k] = (hx or lager.halt.x, hy or lager.halt.y)
    zeilen: Dict[Tuple[int, int], int] = {}
    for k in range(len(knoten)):
        for r in (0, 1):
            if not halt.get(k, (False, False))[r]:
                zeilen[(k, r)] = len(zeilen)
    last = [0.0] * len(zeilen)
    for f in modell.lasten:
        k = _bei(knoten, f.ort)
        for r, wert in ((0, f.F_x), (1, f.F_y)):
            if (k, r) in zeilen:
                last[zeilen[(k, r)]] += wert
    return Grundstruktur(modell=modell, knoten=tuple(knoten), staebe=tuple(map(tuple, staebe)),
                         laengen=laengen, zeilen=zeilen, last=tuple(last), weite=weite,
                         aufschlag=tuple(aufschlag))


def liegt_achsparallel(p: Punkt, q: Punkt) -> bool:
    """Ob ein Stab von ``p`` nach ``q`` waagrecht oder senkrecht liegt -- bis auf :data:`ACHSPARALLEL`."""
    dx, dy = abs(q[0] - p[0]), abs(q[1] - p[1])
    return min(dx, dy) <= ACHSPARALLEL * math.hypot(dx, dy)


def _gleich(p: Punkt, q: Punkt) -> bool:
    return abs(p[0] - q[0]) <= geo.TOLERANZ and abs(p[1] - q[1]) <= geo.TOLERANZ


def _bei(knoten: Sequence[Punkt], p: Punkt) -> int:
    return next(k for k, q in enumerate(knoten) if _gleich(p, q))


def _knoten(modell: Modell, weite: float, drin: Callable[[Punkt], bool]
            ) -> Tuple[List[Punkt], List[Optional[Tuple[int, int]]], Punkt]:
    """
    Die Knoten, je Knoten sein Platz im Raster ``(i, j)`` -- ``None`` für
    die übrigen -- und der Punkt ``(0, 0)`` des Rasters: die Ecke unten
    links des Rechtecks um die Scheiben. Ein Lager, eine Last oder eine
    Ecke auf einem Rasterpunkt gibt ihm ihre genauen Koordinaten.
    """
    xs = [p[0] for s in modell.scheiben for p in s.ecken]
    ys = [p[1] for s in modell.scheiben for p in s.ecken]
    x0, y0 = min(xs), min(ys)
    nx = int(math.floor((max(xs) - x0) / weite + 1e-9))
    ny = int(math.floor((max(ys) - y0) / weite + 1e-9))
    if (nx + 1) * (ny + 1) > HOECHSTENS_RASTERPUNKTE:
        raise ZuVieleKnoten(_zu_viele(modell, weite, f"weit über {HOECHSTENS_KNOTEN}"))
    knoten: List[Punkt] = []
    raster: List[Optional[Tuple[int, int]]] = []
    for j in range(ny + 1):
        for i in range(nx + 1):
            p = (x0 + i * weite, y0 + j * weite)
            if drin(p):
                knoten.append(p)
                raster.append((i, j))
    platz = {r: k for k, r in enumerate(raster)}
    besondere = [l.ort for l in modell.lager] + [f.ort for f in modell.lasten]
    besondere += [p for u in (*modell.scheiben, *modell.loecher) for p in u.ecken]
    for p in besondere:
        if len(knoten) > HOECHSTENS_KNOTEN or not drin(p):
            continue
        auf = platz.get((round((p[0] - x0) / weite), round((p[1] - y0) / weite)))
        if auf is not None and _gleich(p, knoten[auf]):
            knoten[auf] = p
        elif not any(_gleich(p, q) for q in knoten[len(platz):]):
            knoten.append(p)
            raster.append(None)
    if len(knoten) > HOECHSTENS_KNOTEN:
        raise ZuVieleKnoten(_zu_viele(modell, weite, str(len(knoten)) if len(platz) > HOECHSTENS_KNOTEN
                                      else f"über {HOECHSTENS_KNOTEN}"))
    return knoten, raster, (x0, y0)


def _zu_viele(modell: Modell, weite: float, anzahl: str) -> str:
    """Der Satz, wenn das Raster zu fein ist -- mit einer Rasterweite, die passt, auf 5 cm genau."""
    flaeche = sum(abs(geo.flaeche(s.ecken)) for s in modell.scheiben)
    passt = max(math.ceil(20.0 * math.sqrt(flaeche / HOECHSTENS_KNOTEN)) / 20.0, weite + 0.05)
    return (f"Mit der Rasterweite {weite:g} m lägen {anzahl} Knoten in der Scheibe – mehr als "
            f"{HOECHSTENS_KNOTEN} sucht das Werkzeug nicht. Bitte die Rasterweite mindestens "
            f"{passt:g} m wählen.")


def _staebe(knoten: Sequence[Punkt], raster: Sequence[Optional[Tuple[int, int]]],
            ursprung: Punkt, weite: float, liegt: Callable[[Punkt, Punkt], bool]) -> List[Tuple[int, int]]:
    """Je zwei Knoten ein Stab, wenn kein dritter auf ihm liegt und er ganz im Material ist (``liegt``)."""
    n = len(knoten)
    besondere = [k for k in range(n) if raster[k] is None]
    im_raster = {r: k for k, r in enumerate(raster) if r is not None}
    staebe = []
    for a in range(n):
        for b in range(a + 1, n):
            ra, rb = raster[a], raster[b]
            if ra is not None and rb is not None:
                if gcd(abs(ra[0] - rb[0]), abs(ra[1] - rb[1])) != 1:
                    continue
            elif _rasterknoten_auf(knoten, a, b, im_raster, ursprung, weite):
                continue
            if any(_auf_innen(knoten[k], knoten[a], knoten[b]) for k in besondere if k not in (a, b)):
                continue
            if liegt(knoten[a], knoten[b]):
                staebe.append((a, b))
    return staebe


def _auf_innen(p: Punkt, a: Punkt, b: Punkt) -> bool:
    """Ob ``p`` auf der Strecke ``a → b`` liegt, nicht an ihren Enden."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    l2 = dx * dx + dy * dy
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2
    if not 0.0 < t < 1.0:
        return False
    return abs((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / math.sqrt(l2) <= geo.TOLERANZ \
        and min(math.dist(p, a), math.dist(p, b)) > geo.TOLERANZ


def _rasterknoten_auf(knoten: Sequence[Punkt], ka: int, kb: int,
                      im_raster: Dict[Tuple[int, int], int], ursprung: Punkt, weite: float) -> bool:
    """
    Ob ein Knoten des Rasters auf der Strecke von Knoten ``ka`` zu ``kb``
    liegt, ausser den beiden selbst: geprüft, wo sie die Linien des Rasters
    quer zu ihrer längeren Richtung kreuzt.
    """
    a, b = knoten[ka], knoten[kb]
    x0, y0 = ursprung
    dx, dy = b[0] - a[0], b[1] - a[1]
    waagrecht = abs(dx) >= abs(dy)
    s0, s1 = ((a[0] - x0) / weite, (b[0] - x0) / weite) if waagrecht \
        else ((a[1] - y0) / weite, (b[1] - y0) / weite)
    for s in range(math.floor(min(s0, s1)), math.ceil(max(s0, s1)) + 1):
        if waagrecht:
            i, quer = s, a[1] + (x0 + s * weite - a[0]) / dx * dy
            j = round((quer - y0) / weite)
            daneben = abs(y0 + j * weite - quer)
        else:
            j, quer = s, a[0] + (y0 + s * weite - a[1]) / dy * dx
            i = round((quer - x0) / weite)
            daneben = abs(x0 + i * weite - quer)
        k = im_raster.get((i, j))
        if k is not None and k not in (ka, kb) and daneben <= geo.TOLERANZ \
                and _auf_innen(knoten[k], a, b):
            return True
    return False


def im_material(modell: Modell, umrisse: Sequence[Sequence[Punkt]], a: Punkt, b: Punkt) -> bool:
    """
    Ob die Strecke ``a → b`` ganz im Material liegt: geteilt, wo sie einen
    Rand trifft, liegt jedes Stück ganz innen, ganz aussen oder auf einem
    Rand -- seine Mitte sagt, welches. Ein Stück auf einem Rand braucht
    Material auf einer Seite, :data:`NEBEN_DEM_RAND` daneben.
    """
    stellen = {0.0, 1.0}
    for ecken in umrisse:
        stellen.update(geo.schnittstellen(a, b, ecken))
    folge = sorted(stellen)
    dx, dy = b[0] - a[0], b[1] - a[1]
    quer = NEBEN_DEM_RAND / math.hypot(dx, dy)
    for t0, t1 in zip(folge, folge[1:]):
        if t1 - t0 < 1e-12:
            continue
        t = 0.5 * (t0 + t1)
        m = (a[0] + t * dx, a[1] + t * dy)
        if not modell.im_material(m):
            return False
        if any(geo.auf_rand(m, ecken) for ecken in umrisse) and not any(
                modell.im_material((m[0] - s * quer * dy, m[1] + s * quer * dx)) for s in (1, -1)):
            return False
    return True
