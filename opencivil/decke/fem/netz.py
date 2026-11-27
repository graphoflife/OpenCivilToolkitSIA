"""
opencivil/decke/fem/netz.py -- das Dreiecksnetz einer Decke.

VERANTWORTUNG:
Aus den Platten einer Decke ein Netz aus Dreiecken, nicht weiter als
:attr:`~opencivil.decke.modell.Decke.netzweite`, das allem folgt, was die
Rechnung an einer Linie oder einem Punkt braucht: den Rändern der Platten,
den Linienlagern, den Trägern und den Linienlasten als Kanten, den Stützen
als Knoten. Wo keine Platte liegt, ist ein Loch.

WIE ES ENTSTEHT:
1. Alle Linien werden an ihren Kreuzungen und an den Stützen auf ihnen
   geteilt; was neben den Platten liegt, fällt weg.
2. Jedes Stück bekommt Knoten in gleichen Abständen, höchstens die
   Netzweite ``h`` auseinander.
3. Ins Innere kommt ein Gitter gleichseitiger Dreiecke der Weite ``h``,
   ohne die Punkte näher als :data:`ABSTAND` · ``h`` an einer Linie.
4. Über alle Punkte eine Delaunay-Triangulierung
   (:mod:`~opencivil.decke.fem.delaunay`). Fehlt danach ein Stück einer
   Linie als Kante, wird es in der Mitte geteilt, bis es da ist -- der
   Umkreis eines kurzen Stücks hat keinen fremden Punkt mehr.
5. Ein Dreieck gehört zu der Platte, in der sein Schwerpunkt liegt; eines
   in keiner fällt weg, mit ihm die Knoten, die nur ihm gehörten.
6. Die Knoten des Gitters rücken ein paarmal in die Mitte ihrer Nachbarn
   (:data:`GLAETTEN`), solange kein Dreieck kippt -- das gleicht aus, wo
   das Gitter schief an eine Linie stösst.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.fem.delaunay import Triangulierung, orientierung
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Decke, Linienlast
from opencivil.stabwerk.system import Meldung

#: So nahe an einer Linie bleibt kein Punkt des Gitters, als Teil der Netzweite.
ABSTAND = 0.55

#: So oft rücken die Knoten des Gitters in die Mitte ihrer Nachbarn.
GLAETTEN = 3

#: Kürzer wird ein Stück einer Linie beim Teilen nicht, als Teil der Netzweite.
KUERZESTES = 1.0 / 64.0

#: Was als derselbe Punkt gilt, in m.
GLEICH = 1e-7


@dataclass
class Linie:
    """
    Eine Linie der Decke im Netz: ein Linienlager, ein Träger oder eine
    Linienlast, von ``a`` nach ``b``. ``knoten`` sind die Knoten auf ihr,
    nach ``u`` -- der Stelle in m ab ``a`` --, und ``stuecke`` die Paare
    benachbarter Knoten, zwischen denen das Netz eine Kante hat: über ein
    Loch hinweg keine.
    """

    name: str
    art: str
    a: Punkt
    b: Punkt
    knoten: List[int] = field(default_factory=list)
    u: List[float] = field(default_factory=list)
    stuecke: List[Tuple[int, int]] = field(default_factory=list)

    @property
    def laenge(self) -> float:
        return math.dist(self.a, self.b)

    @property
    def richtung(self) -> Punkt:
        L = self.laenge
        return ((self.b[0] - self.a[0]) / L, (self.b[1] - self.a[1]) / L)


@dataclass
class Netz:
    """
    Die Knoten in m, die Dreiecke im Gegenuhrzeigersinn und je Dreieck die
    Nummer seiner Platte in der Decke. ``linien`` nach Art und Name
    (:meth:`linie`), ``stuetzen``
    je Stütze ihr Knoten -- eine neben den Platten fehlt. ``trennkanten``
    sind die Kanten, über die hinweg die Momente und Querkräfte nicht
    gemittelt werden (:mod:`~opencivil.decke.fem.glaetten`): Lager, Träger,
    Linienlasten und Fugen zwischen Platten verschiedener Steifigkeit.
    """

    weite: float
    knoten: List[Punkt] = field(default_factory=list)
    dreiecke: List[Tuple[int, int, int]] = field(default_factory=list)
    platte: List[int] = field(default_factory=list)
    linien: Dict[Tuple[str, str], Linie] = field(default_factory=dict)
    stuetzen: Dict[str, int] = field(default_factory=dict)
    trennkanten: Set[Tuple[int, int]] = field(default_factory=set)
    meldungen: List[Meldung] = field(default_factory=list)

    def flaeche(self, e: int) -> float:
        a, b, c = (self.knoten[k] for k in self.dreiecke[e])
        return 0.5 * orientierung(a, b, c)

    def linie(self, art: str, name: str) -> Optional[Linie]:
        """Die Linie ``name`` der Art ``linienlager``, ``traeger`` oder ``linienlast`` -- ``None``, wenn sie keine Länge hat."""
        return self.linien.get((art, name))

    def kanten(self) -> Set[Tuple[int, int]]:
        """Jede Kante einmal, als ``(kleinere, grössere Nummer)``."""
        return {kante(p, q) for a, b, c in self.dreiecke for p, q in ((a, b), (b, c), (c, a))}

    def auf_strecke(self, linie: Linie, kanten: Optional[Set[Tuple[int, int]]] = None) -> Linie:
        """
        ``linie`` mit den Knoten auf ihr, nach der Stelle ``u`` ab ``a`` --
        und den Stücken, die Kanten des Netzes sind (``kanten``, ohne Angabe
        :meth:`kanten`).
        """
        kanten = self.kanten() if kanten is None else kanten
        L = linie.laenge
        e = linie.richtung
        auf = []
        for k, p in enumerate(self.knoten):
            u = (p[0] - linie.a[0]) * e[0] + (p[1] - linie.a[1]) * e[1]
            if -GLEICH <= u <= L + GLEICH and abs((p[0] - linie.a[0]) * e[1] - (p[1] - linie.a[1]) * e[0]) <= 1e-6:
                auf.append((u, k))
        auf.sort()
        linie.knoten = [k for _, k in auf]
        linie.u = [u for u, _ in auf]
        linie.stuecke = [(p, q) for p, q in zip(linie.knoten, linie.knoten[1:]) if kante(p, q) in kanten]
        return linie


def kante(a: int, b: int) -> Tuple[int, int]:
    return (a, b) if a < b else (b, a)


def schaetzung(decke: Decke, weite: float) -> int:
    """Wie viele Knoten das Netz etwa hätte: je Knoten zwei gleichseitige Dreiecke."""
    flaeche = sum(abs(geo.flaeche(list(p.ecken))) for p in decke.platten)
    return int(flaeche / (math.sqrt(3.0) / 2.0 * weite * weite)) + 1


def vernetzen(decke: Decke, weite: float) -> Netz:
    """Das Netz der Decke -- ihre Platten geprüft (:func:`~opencivil.decke.streifen.pruefen`)."""
    netz = Netz(weite)
    platten = [geo.gegen_uhrzeiger(geo.bereinigt(p.ecken)) for p in decke.platten]
    if not platten:
        return netz
    linien = _linien(decke)
    punkte = [s.ort for s in decke.stuetzen if any(geo.innen(s.ort, p) for p in platten)]
    stuecke = [s for s in _geteilt(_strecken(platten, linien), punkte)
               if any(geo.innen(_mitte(*s), p) for p in platten)]
    x0 = min(x for p in platten for x, _ in p)
    x1 = max(x for p in platten for x, _ in p)
    y0 = min(y for p in platten for _, y in p)
    y1 = max(y for p in platten for _, y in p)
    t = Triangulierung(x0, y0, x1, y1, gleich=GLEICH)
    zwang: List[Tuple[int, int]] = []
    fest: Set[int] = set()
    for p, q in stuecke:
        n = max(1, math.ceil(math.dist(p, q) / weite - 1e-9))
        nummern = [t.einfuegen((p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n))
                   for i in range(n + 1)]
        zwang.extend(zip(nummern, nummern[1:]))
        fest.update(nummern)
    fest.update(t.einfuegen(p) for p in punkte)
    raster = _Raster(weite)
    for p, q in stuecke:
        raster.strecke(p, q, ABSTAND * weite)
    for p in punkte:
        raster.strecke(p, p, ABSTAND * weite)
    for p in _gitter(platten, x0, y0, x1, y1, weite):
        if raster.frei(p, ABSTAND * weite):
            t.einfuegen(p)
    fehlend = _erzwingen(t, zwang, weite)
    fest.update(k for stueck in zwang for k in stueck)
    nummer = _uebernehmen(netz, t, platten)
    if fehlend:
        netz.meldungen.append(Meldung(
            f"Das Netz folgt {fehlend} Stücken einer Linie nicht genau – eine Ecke ist zu spitz.",
            fehler=False))
    _glaetten(netz, {nummer[k] for k in fest if k in nummer})
    _linien_finden(netz, linien)
    for s in decke.stuetzen:
        k = _knoten_bei(netz, s.ort)
        if k is not None:
            netz.stuetzen[s.name] = k
    netz.trennkanten = _trennkanten(netz, decke)
    return netz


# ===========================================================================
# Linien und Punkte
# ===========================================================================


def _linien(decke: Decke) -> List[Linie]:
    """Die Linien der Decke, die das Netz als Kanten braucht."""
    heraus = [Linie(l.name, "linienlager", l.a, l.b) for l in decke.linienlager]
    heraus += [Linie(u.name, "traeger", u.a, u.b) for u in decke.traeger]
    heraus += [Linie(last.name, "linienlast", last.a, last.b) for lf in decke.lastfaelle
               for last in lf.lasten if isinstance(last, Linienlast)]
    return [l for l in heraus if l.laenge > GLEICH]


def _strecken(platten: Sequence[Sequence[Punkt]], linien: Sequence[Linie]) -> List[Tuple[Punkt, Punkt]]:
    heraus = [(p[i], p[(i + 1) % len(p)]) for p in platten for i in range(len(p))]
    return heraus + [(l.a, l.b) for l in linien]


def _mitte(p: Punkt, q: Punkt) -> Punkt:
    return (0.5 * (p[0] + q[0]), 0.5 * (p[1] + q[1]))


def _geteilt(strecken: Sequence[Tuple[Punkt, Punkt]], punkte: Sequence[Punkt]) -> List[Tuple[Punkt, Punkt]]:
    """
    Die Strecken in Stücke, geteilt an jeder Kreuzung, an jedem Ende einer
    anderen auf ihnen und an jedem Punkt auf ihnen -- jedes Stück einmal.
    """
    stellen: List[List[float]] = [[0.0, 1.0] for _ in strecken]
    for i, (a, b) in enumerate(strecken):
        L = math.dist(a, b)
        if L <= GLEICH:
            continue
        for j in range(i + 1, len(strecken)):
            c, d = strecken[j]
            M = math.dist(c, d)
            if M <= GLEICH:
                continue
            kreuz = geo.kreuzung(a, b, c, d)
            if kreuz is not None:
                u, k = kreuz
                if -GLEICH / L <= u <= 1.0 + GLEICH / L and -GLEICH / M <= k <= 1.0 + GLEICH / M:
                    stellen[i].append(u)
                    stellen[j].append(k)
                continue
            # Parallel: nur, wenn sie auf einer Geraden liegen, teilen sich ihre Enden.
            for p in (c, d):
                u = _auf(p, a, b)
                if u is not None:
                    stellen[i].append(u)
            for p in (a, b):
                k = _auf(p, c, d)
                if k is not None:
                    stellen[j].append(k)
        for p in punkte:
            u = _auf(p, a, b)
            if u is not None:
                stellen[i].append(u)
    heraus: Dict[Tuple[Tuple[int, int], Tuple[int, int]], Tuple[Punkt, Punkt]] = {}
    for (a, b), us in zip(strecken, stellen):
        L = math.dist(a, b)
        if L <= GLEICH:
            continue
        folge: List[float] = []
        for u in sorted(min(max(u, 0.0), 1.0) for u in us):
            if not folge or (u - folge[-1]) * L > GLEICH:
                folge.append(u)
        folge[-1] = 1.0
        orte = [(a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1])) for u in folge]
        for p, q in zip(orte, orte[1:]):
            schluessel = tuple(sorted((_schluessel(p), _schluessel(q))))
            heraus.setdefault(schluessel, (p, q))
    return list(heraus.values())


def _auf(p: Punkt, a: Punkt, b: Punkt) -> Optional[float]:
    """Wo ``p`` auf der Strecke ``a → b`` liegt, als Parameter -- ``None``, wenn daneben."""
    L = math.dist(a, b)
    u = ((p[0] - a[0]) * (b[0] - a[0]) + (p[1] - a[1]) * (b[1] - a[1])) / (L * L)
    if not -GLEICH / L <= u <= 1.0 + GLEICH / L:
        return None
    q = (a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]))
    return u if math.dist(p, q) <= GLEICH else None


def _schluessel(p: Punkt) -> Tuple[int, int]:
    return (round(p[0] / GLEICH), round(p[1] / GLEICH))


# ===========================================================================
# Gitter und Triangulierung
# ===========================================================================


class _Raster:
    """Strecken in Zellen der Netzweite -- damit ein Punkt nur die nahen prüft."""

    def __init__(self, weite: float) -> None:
        self.weite = weite
        self.zellen: Dict[Tuple[int, int], List[Tuple[Punkt, Punkt]]] = {}

    def _zelle(self, p: Punkt) -> Tuple[int, int]:
        return (math.floor(p[0] / self.weite), math.floor(p[1] / self.weite))

    def strecke(self, p: Punkt, q: Punkt, rand: float) -> None:
        i0, j0 = self._zelle((min(p[0], q[0]) - rand, min(p[1], q[1]) - rand))
        i1, j1 = self._zelle((max(p[0], q[0]) + rand, max(p[1], q[1]) + rand))
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                self.zellen.setdefault((i, j), []).append((p, q))

    def frei(self, p: Punkt, abstand: float) -> bool:
        """Ob ``p`` mindestens ``abstand`` von jeder Strecke liegt."""
        return all(_abstand(p, a, b) >= abstand for a, b in self.zellen.get(self._zelle(p), ()))


def _abstand(p: Punkt, a: Punkt, b: Punkt) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    u = 0.0 if L2 <= 0.0 else min(max(((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2, 0.0), 1.0)
    return math.hypot(p[0] - a[0] - u * dx, p[1] - a[1] - u * dy)


def _gitter(platten: Sequence[Sequence[Punkt]], x0: float, y0: float, x1: float, y1: float,
            weite: float) -> Iterable[Punkt]:
    """Die Punkte eines Gitters gleichseitiger Dreiecke in den Platten -- Zeile um Zeile, hin und her."""
    hoehe = weite * math.sqrt(3.0) / 2.0
    zeilen = math.ceil((y1 - y0) / hoehe) + 1
    spalten = math.ceil((x1 - x0) / weite) + 2
    for j in range(zeilen):
        y = y0 + j * hoehe
        reihe = [x0 - weite + i * weite + (0.5 * weite if j % 2 else 0.0) for i in range(spalten)]
        for x in (reihe if j % 2 == 0 else reversed(reihe)):
            p = (x, y)
            if any(geo.innen(p, v) for v in platten):
                yield p


def _erzwingen(t: Triangulierung, zwang: List[Tuple[int, int]], weite: float) -> int:
    """
    Teilt jedes Stück einer Linie, das als Kante fehlt, in der Mitte, bis
    alle da sind -- ``zwang`` danach mit den geteilten Stücken -- und gibt
    zurück, wie viele es nicht wurden, weil sie kürzer als
    :data:`KUERZESTES` der Netzweite geworden wären. Ein neuer Punkt kann
    eine Kante nehmen, die schon da war; darum wird jede Runde alles geprüft.
    """
    for _ in range(40):
        kanten = t.kanten()
        neu: List[Tuple[int, int]] = []
        geteilt = False
        for a, b in zwang:
            p, q = t.punkte[a], t.punkte[b]
            if kante(a, b) in kanten or math.dist(p, q) < 2.0 * KUERZESTES * weite:
                neu.append((a, b))
                continue
            m = t.einfuegen(_mitte(p, q))
            neu += [(a, m), (m, b)]
            geteilt = True
        zwang[:] = neu
        if not geteilt:
            break
    kanten = t.kanten()
    return sum(1 for a, b in zwang if kante(a, b) not in kanten)


def _uebernehmen(netz: Netz, t: Triangulierung, platten: Sequence[Sequence[Punkt]]) -> Dict[int, int]:
    """Die Dreiecke in Platten ins Netz, ihre Knoten neu gezählt -- zurück: je Punkt der Triangulierung sein Knoten."""
    nummer: Dict[int, int] = {}
    for d in t.dreiecke():
        ecken = [t.punkte[k] for k in d]
        mitte = ((ecken[0][0] + ecken[1][0] + ecken[2][0]) / 3.0, (ecken[0][1] + ecken[1][1] + ecken[2][1]) / 3.0)
        platte = next((i for i, p in enumerate(platten) if geo.innen(mitte, p)), None)
        if platte is None:
            continue
        for k in d:
            if k not in nummer:
                nummer[k] = len(netz.knoten)
                netz.knoten.append(t.punkte[k])
        netz.dreiecke.append(tuple(nummer[k] for k in d))
        netz.platte.append(platte)
    return nummer


def _glaetten(netz: Netz, fest: Set[int]) -> None:
    """
    Jeder Knoten, der nicht auf einer Linie oder an einer Stütze liegt, rückt
    in die Mitte seiner Nachbarn -- nur, wenn danach jedes Dreieck um ihn
    noch richtig herum liegt.
    """
    um: Dict[int, List[int]] = {}
    nachbarn: Dict[int, Set[int]] = {}
    zahl: Dict[Tuple[int, int], int] = {}
    for e, (a, b, c) in enumerate(netz.dreiecke):
        for k, andere in ((a, (b, c)), (b, (c, a)), (c, (a, b))):
            um.setdefault(k, []).append(e)
            nachbarn.setdefault(k, set()).update(andere)
        for p, q in ((a, b), (b, c), (c, a)):
            zahl[kante(p, q)] = zahl.get(kante(p, q), 0) + 1
    # Auf dem Rand des Netzes -- einer Kante, die nur ein Dreieck hat -- bleibt jeder Knoten.
    rand = {k for ks, n in zahl.items() if n == 1 for k in ks}
    for _ in range(GLAETTEN):
        for k in range(len(netz.knoten)):
            if k in fest or k in rand:
                continue
            ns = nachbarn[k]
            neu = (sum(netz.knoten[n][0] for n in ns) / len(ns), sum(netz.knoten[n][1] for n in ns) / len(ns))
            alt = netz.knoten[k]
            netz.knoten[k] = neu
            if any(netz.flaeche(e) <= 1e-3 * netz.weite ** 2 for e in um[k]):
                netz.knoten[k] = alt


def _linien_finden(netz: Netz, linien: Sequence[Linie]) -> None:
    """Je Linie die Knoten auf ihr, nach der Stelle -- und die Stücke, die Kanten des Netzes sind."""
    kanten = netz.kanten()
    for l in linien:
        netz.linien[(l.art, l.name)] = netz.auf_strecke(l, kanten)


def _knoten_bei(netz: Netz, p: Punkt) -> Optional[int]:
    return next((k for k, q in enumerate(netz.knoten) if math.dist(p, q) <= 1e-6), None)


def _trennkanten(netz: Netz, decke: Decke) -> Set[Tuple[int, int]]:
    """Lager, Träger und Linienlasten -- und wo zwei Platten verschieden steif aneinanderstossen."""
    heraus = {kante(p, q) for l in netz.linien.values() for p, q in l.stuecke}
    seiten: Dict[Tuple[int, int], List[int]] = {}
    for e, (a, b, c) in enumerate(netz.dreiecke):
        for p, q in ((a, b), (b, c), (c, a)):
            seiten.setdefault(kante(p, q), []).append(e)
    for k, es in seiten.items():
        if len(es) == 2:
            p1, p2 = (decke.platten[netz.platte[e]] for e in es)
            if p1 is not p2 and (p1.h, p1.E, p1.nu) != (p2.h, p2.E, p2.nu):
                heraus.add(k)
    return heraus
