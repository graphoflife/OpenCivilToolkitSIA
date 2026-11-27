"""
opencivil/decke/fem/system.py -- das Gleichungssystem der Platte.

VERANTWORTUNG:
Aus der Decke und ihrem Netz: was die Lager halten, die Nummern der
Unbekannten, die Steifigkeit aus den Dreiecken und den Trägern, einmal
zerlegt für alle Fälle (:mod:`~opencivil.stabwerk.matrix`) -- und welche
Teile der Decke sich frei bewegen könnten.

LAGER:
Ein Linienlager, das vertikal hält, hält auf jedem seiner Knoten ``w`` --
und damit auch die Neigung längs: ``w`` ist auf ihm überall null. Hält es
die Drehung, ist auch die Neigung quer zu ihm null; nur die Drehung allein
hält ein Rand an einer Symmetrieachse. Eine Stütze hält ``w`` ihres
Knotens, nicht seine Neigung: sie ist ein Punkt (Plan vom 2026-11-27).
Hält ein Knoten eine Neigung schief zu x und y, rechnet er in eigenen
Achsen, die erste längs dieser Richtung (:attr:`System.achsen`); hält er
zwei, ist er ganz eingespannt.

DIE NUMMERN:
Die Knoten in der umgekehrten Cuthill-McKee-Folge
(:func:`~opencivil.stabwerk.matrix.nummerierung`), je Knoten ``w`` und
die beiden Neigungen; was ein Lager hält, hat keine Nummer.

BEWEGLICH:
Hält ein Teil der Decke -- Dreiecke, die über Knoten oder Träger
zusammenhängen -- nicht genug, um nicht wegzukippen, fällt beim Zerlegen
ein Pivot weg. Der ganze Teil trägt dann nichts (:attr:`System.beweglich`),
und der Rest rechnet weiter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

from opencivil.decke.fem.element import (
    Dreieck, Matrix, balken, balken_in_der_platte, steifigkeit_des_traegers,
)
from opencivil.decke.fem.netz import Netz, kante
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Decke
from opencivil.stabwerk.matrix import Profilmatrix, Zerlegung, nummerierung

#: Zwei Richtungen gelten als eine, wenn der Sinus ihres Winkels kleiner ist.
PARALLEL = 1e-6


@dataclass
class Halt:
    """Was die Lager an einem Knoten halten: ``w`` und die Richtungen, in denen die Neigung null ist."""

    w: bool = False
    richtungen: List[Punkt] = field(default_factory=list)

    def neigung(self, d: Punkt) -> None:
        if all(abs(d[0] * e[1] - d[1] * e[0]) > PARALLEL for e in self.richtungen):
            self.richtungen.append(d)


@dataclass(frozen=True)
class Balkenstueck:
    """Ein Stück eines Trägers zwischen zwei Knoten: von ``u_p`` bis ``u_q`` m ab seinem Anfang."""

    traeger: str
    p: int
    q: int
    u_p: float
    u_q: float
    K4: Matrix
    """Die Steifigkeit über ``(w_p, w'_p, w_q, w'_q)``, ``w'`` längs des Trägers."""

    richtung: Punkt
    EI: float


class System:
    """Die Platte als Gleichungssystem, zerlegt."""

    def __init__(self, decke: Decke, netz: Netz) -> None:
        self.decke = decke
        self.netz = netz
        self.halt = _halt(decke, netz)
        self.achsen: List[Optional[Tuple[Punkt, Punkt]]] = [_achsen(h) for h in self.halt]
        """Je Knoten ``None`` -- er rechnet in x und y -- oder seine Achsen: die erste gehalten."""

        self.dreiecke = [Dreieck([netz.knoten[k] for k in d], *_kennwerte(decke, netz.platte[e]))
                         for e, d in enumerate(netz.dreiecke)]
        self.balken = _balken(decke, netz)
        self.nummern = self._nummerieren()
        self.zahl = sum(1 for n in self.nummern for i in n if i >= 0)
        """Wie viele Unbekannte frei sind."""

        self.K = self._steifigkeit()
        self.zerlegung = Zerlegung(self.K)
        self.beweglich = self._beweglich()
        """Die Teile, die sich frei bewegen könnten, je als Menge ihrer Knoten."""

    # -- Unbekannte ---------------------------------------------------------------

    def _nummerieren(self) -> List[Tuple[int, int, int]]:
        n = len(self.netz.knoten)
        nachbarn: Dict[int, Set[int]] = {k: set() for k in range(n)}
        for gruppe in [*self.netz.dreiecke, *((b.p, b.q) for b in self.balken)]:
            for k in gruppe:
                nachbarn[k].update(x for x in gruppe if x != k)
        folge = nummerierung(list(range(n)), nachbarn)
        nummern: List[Tuple[int, int, int]] = [(-1, -1, -1)] * n
        zaehler = 0
        for k in folge:
            h = self.halt[k]
            frei = (not h.w, len(h.richtungen) < 1, len(h.richtungen) < 2)
            eigene = []
            for ja in frei:
                eigene.append(zaehler if ja else -1)
                zaehler += 1 if ja else 0
            nummern[k] = tuple(eigene)
        return nummern

    def unbekannte(self, knoten: Sequence[int]) -> List[int]:
        """Die Nummern der Unbekannten dieser Knoten, je drei -- -1, wo ein Lager hält."""
        return [i for k in knoten for i in self.nummern[k]]

    # -- Steifigkeit ----------------------------------------------------------

    def gedreht(self, K: Matrix, knoten: Sequence[int]) -> Matrix:
        """``K`` über ``(w, β_x, β_y)`` der ``knoten`` -- in den Achsen jedes Knotens (:attr:`achsen`)."""
        if all(self.achsen[k] is None for k in knoten):
            return K
        K = [list(zeile) for zeile in K]
        for i, k in enumerate(knoten):
            a = self.achsen[k]
            if a is None:
                continue
            (q00, q01), (q10, q11) = a
            x, y = 3 * i + 1, 3 * i + 2
            for zeile in K:
                zeile[x], zeile[y] = q00 * zeile[x] + q01 * zeile[y], q10 * zeile[x] + q11 * zeile[y]
            K[x], K[y] = ([q00 * a_ + q01 * b_ for a_, b_ in zip(K[x], K[y])],
                          [q10 * a_ + q11 * b_ for a_, b_ in zip(K[x], K[y])])
        return K

    def elemente(self) -> List[Tuple[Sequence[int], Matrix]]:
        """Jedes Dreieck und jedes Balkenstück: seine Knoten und seine Steifigkeit über ``(w, β_x, β_y)`` je Knoten."""
        heraus: List[Tuple[Sequence[int], Matrix]] = [(d, e.K) for d, e in zip(self.netz.dreiecke, self.dreiecke)]
        heraus += [((b.p, b.q), balken_in_der_platte(b.K4, b.richtung)) for b in self.balken]
        return heraus

    def _steifigkeit(self) -> Profilmatrix:
        elemente = [(self.unbekannte(knoten), self.gedreht(K, knoten)) for knoten, K in self.elemente()]
        K = Profilmatrix.aus_gruppen(self.zahl, ([i for i in nummern if i >= 0] for nummern, _ in elemente))
        erste, zeilen = K.erste, K.zeilen
        for nummern, Ke in elemente:
            for r, i in enumerate(nummern):
                if i < 0:
                    continue
                reihe = Ke[r]
                for s, j in enumerate(nummern):
                    if 0 <= j <= i:
                        zeilen[i][j - erste[i]] += reihe[s]
        return K

    # -- Beweglich ------------------------------------------------------------

    def _beweglich(self) -> List[Set[int]]:
        """Die zusammenhängenden Teile, in denen ein Pivot wegfiel."""
        if not self.zerlegung.singulaer:
            return []
        teil = list(range(len(self.netz.knoten)))

        def wurzel(k: int) -> int:
            while teil[k] != k:
                teil[k] = teil[teil[k]]
                k = teil[k]
            return k

        for gruppe in [*self.netz.dreiecke, *((b.p, b.q) for b in self.balken)]:
            for k in gruppe[1:]:
                a, b = wurzel(gruppe[0]), wurzel(k)
                if a != b:
                    teil[b] = a
        knoten_von = {i: k for k, nummern in enumerate(self.nummern) for i in nummern if i >= 0}
        wurzeln = {wurzel(knoten_von[i]) for i in self.zerlegung.singulaer}
        heraus: Dict[int, Set[int]] = {}
        for k in range(len(self.netz.knoten)):
            w = wurzel(k)
            if w in wurzeln:
                heraus.setdefault(w, set()).add(k)
        return list(heraus.values())

    # -- Lösen ----------------------------------------------------------------

    def loesen(self, kraefte: Sequence[float]) -> List[Tuple[float, float, float]]:
        """
        Je Knoten ``(w, β_x, β_y)`` in x und y, aus den Kräften nach unten in
        N je Knoten -- in einem beweglichen Teil null.
        """
        f = [0.0] * self.zahl
        for k, F in enumerate(kraefte):
            i = self.nummern[k][0]
            if i >= 0:
                f[i] = F
        x = self.zerlegung.loese(f)
        aus = {k for teil in self.beweglich for k in teil}
        heraus: List[Tuple[float, float, float]] = []
        for k, (i, j, l) in enumerate(self.nummern):
            if k in aus:
                heraus.append((0.0, 0.0, 0.0))
                continue
            w, b1, b2 = (x[n] if n >= 0 else 0.0 for n in (i, j, l))
            a = self.achsen[k]
            if a is not None:
                # In x und y zurück: β = Qᵀ · β_lokal.
                (q00, q01), (q10, q11) = a
                b1, b2 = q00 * b1 + q10 * b2, q01 * b1 + q11 * b2
            heraus.append((w, b1, b2))
        return heraus

    def reste(self, u: Sequence[Tuple[float, float, float]], kraefte: Sequence[float]) -> List[List[float]]:
        """
        Je Knoten ``K·u − f`` in x und y: was die Lager auf die Platte
        ausüben, nach unten positiv und als Moment zur Neigung -- an einem
        freien Knoten null bis auf Rundung.
        """
        heraus = [[0.0, 0.0, 0.0] for _ in u]
        for knoten, K in self.elemente():
            ue = [v for k in knoten for v in u[k]]
            for r, zeile in enumerate(K):
                heraus[knoten[r // 3]][r % 3] += sum(a * b for a, b in zip(zeile, ue))
        for k, F in enumerate(kraefte):
            heraus[k][0] -= F
        return heraus


def _kennwerte(decke: Decke, platte: int) -> Tuple[float, float, float]:
    p = decke.platten[platte]
    return p.E, p.h, p.nu


def _halt(decke: Decke, netz: Netz) -> List[Halt]:
    """Je Knoten, was die Linienlager und Stützen an ihm halten."""
    halt = [Halt() for _ in netz.knoten]
    for lager in decke.linienlager:
        linie = netz.linie("linienlager", lager.name)
        if linie is None:
            continue
        t = linie.richtung
        for k in linie.knoten:
            if lager.vertikal:
                halt[k].w = True
                halt[k].neigung(t)
            if lager.eingespannt:
                halt[k].neigung((-t[1], t[0]))
    for k in netz.stuetzen.values():
        halt[k].w = True
    return halt


def _achsen(h: Halt) -> Optional[Tuple[Punkt, Punkt]]:
    """Die Achsen eines Knotens, der genau eine Neigung hält, schief zu x und y -- sonst ``None``."""
    if len(h.richtungen) != 1:
        return None
    d = h.richtungen[0]
    if abs(d[0]) <= PARALLEL or abs(d[1]) <= PARALLEL:
        # Längs x oder y: die Achsen sind x und y, nur vielleicht vertauscht.
        return None if abs(d[0]) > PARALLEL else ((0.0, 1.0), (-1.0, 0.0))
    return (d, (-d[1], d[0]))


def _balken(decke: Decke, netz: Netz) -> List[Balkenstueck]:
    """
    Je Träger mit Höhe seine Stücke von Knoten zu Knoten
    (:func:`~opencivil.decke.fem.element.steifigkeit_des_traegers`), mit E
    und h der Platte neben dem Stück -- auf der Fuge zweier Platten der
    ersten. Ohne Höhe ist er kein Balken: er steckt in der Platte.
    """
    heraus: List[Balkenstueck] = []
    # Je Kante die erste Platte der Decke, an die sie grenzt -- nicht die des ersten Dreiecks:
    # deren Folge ist die des Netzes, und ein Träger auf der Fuge wechselte sonst von Stück zu Stück.
    an_kante: Dict[Tuple[int, int], int] = {}
    for e, (a, b, c) in enumerate(netz.dreiecke):
        for p, q in ((a, b), (b, c), (c, a)):
            k = kante(p, q)
            an_kante[k] = min(an_kante.get(k, netz.platte[e]), netz.platte[e])
    for u in decke.traeger:
        linie = netz.linie("traeger", u.name)
        if linie is None or u.hoehe <= 0.0:
            continue
        lage = dict(zip(linie.knoten, linie.u))
        for p, q in linie.stuecke:
            platte = decke.platten[an_kante[kante(p, q)]]
            EI = steifigkeit_des_traegers(platte.E, platte.h, u.breite, u.hoehe)
            L = lage[q] - lage[p]
            heraus.append(Balkenstueck(u.name, p, q, lage[p], lage[q], balken(L, EI), linie.richtung, EI))
    return heraus


