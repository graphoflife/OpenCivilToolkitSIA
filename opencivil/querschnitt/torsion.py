"""
opencivil/querschnitt/torsion.py -- das Torsionstraegheitsmoment eines gezeichneten Querschnitts.

VERANTWORTUNG:
``I_T`` nach St. Venant fuer die Polygone einer Querschnittsanalyse, mit
Aussparungen und Hohlraeumen, numerisch. Ein 3D-Balkensystem braucht es,
wenn ein Stab seinen Querschnitt aus einer Analyse nimmt
(:class:`~opencivil.stabwerk.stabquerschnitt.AusAnalyse`): die Vorlagen der
Stabquerschnitte haben Formeln dafuer, ein beliebiges Polygon nicht. Am
Bruttoquerschnitt ohne Bewehrung, wie ``A`` und ``I``.

DIE SPANNUNGSFUNKTION VON PRANDTL:
Im Material gilt ∇²φ = −2, am aeusseren Rand φ = 0. Am Rand eines
Hohlraums ist φ fest, φ_k, und hinaus fliesst so viel, wie er Flaeche hat:
∮ ∂φ/∂n ds = −2·A_k. Dann ist::

    I_T = 2·∫ φ dA + 2·Σ φ_k·A_k

Getrennte Teile tragen je fuer sich. Liegt eines im Hohlraum eines anderen,
zaehlt es zu dessen Flaeche A_k, hat aber seinen eigenen Rand mit φ = 0.

DAS GITTER:
Ein Rechteckgitter ueber den Umriss, die laengere Seite in :data:`TEILUNG`
Zellen. Seine Linien laufen durch jede achsparallele Kante: Rechteck, T und
Hohlkasten liegen genau auf Zellraendern. Je Zelle mit Material ein Wert φ
in ihrer Mitte (finite Volumen). Durch die Kante zwischen zwei Zellen
fliesst ihre Laenge, geteilt durch den Abstand der Mitten, mal den
Unterschied in φ; liegt der Rand dazwischen, zaehlt der Abstand bis zu ihm,
genau geschnitten, auch an einer schraegen Kante. So bleibt die Matrix
symmetrisch, und der Fehler faellt mit dem Quadrat der Zellgroesse (Gibou,
Fedkiw, Cheng und Kang, J. Comput. Phys. 176, 2002). Ein Hohlraum ist ein
einziger Knoten, seine Last 2·A_k. Geloest mit konjugierten Gradienten, die
Diagonale als Vorkonditionierer; ``I_T`` ist dann Last mal Loesung.

ZWEI GITTER UND RICHARDSON:
Eine Wand mit n Zellen ueber ihre Dicke rechnet um 2/n² zu steif. Darum ein
zweites Gitter, jede Zelle halbiert, und I_T = (4·I_fein − I_grob)/3: das
hebt den quadratischen Fehler auf. Liegen die beiden mehr als
:data:`ABWEICHUNG` auseinander, ist das grobe Gitter fuer eine Wand zu grob
-- meist fuer eine duenne schraege. Dann dasselbe feiner, solange das feine
Gitter nicht mehr als :data:`ZELLEN_HOECHSTENS` Zellen mit Material und
:data:`GITTER_HOECHSTENS` Zellen im Ganzen bekaeme.

Wie genau, zeigt ``tests/test_torsion.py``: Rechteck, Dreieck, Kreis und
Rohr auf ein Promille, ein duenner Hohlkasten wie nach Bredt, bis auf das,
was seine Wanddicke dazugibt.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, Iterator, List, Optional, Sequence, Set, Tuple

from opencivil.querschnitt.geometrie import TOLERANZ, Punkt

#: In so viele Zellen teilt das grobe Gitter die laengere Seite des Umrisses.
TEILUNG = 30

#: So weit duerfen die beiden Gitter auseinanderliegen, relativ zum feinen.
ABWEICHUNG = 0.05

#: Mehr Zellen mit Material bekommt das feine Gitter nicht -- so viele
#: Unbekannte hat die Rechnung hoechstens.
ZELLEN_HOECHSTENS = 25_000

#: Mehr Zellen im Ganzen bekommt das feine Gitter nicht: eine duenne schraege
#: Wand fuellt nur wenige davon, eingeteilt wird aber jede.
GITTER_HOECHSTENS = 250_000

#: Die konjugierten Gradienten hoeren auf, wenn das Residuum so klein ist, relativ zur Last.
GENAUIGKEIT = 1e-9

#: Naeher liegt keine Mitte am Rand, relativ zu ihrer Zelle -- sonst wuechse
#: der Fluss dorthin ohne Grenze.
NAEHE = 0.01

Strecke = Tuple[float, float]


@dataclass(frozen=True)
class Gitterlauf:
    """``I_T`` auf einem Gitter -- wie fein es war und wie die Rechnung lief."""

    spalten: int
    """Zellen in y."""

    zeilen: int
    """Zellen in z."""

    zellen: int
    """Davon mit Material: so viele Unbekannte, dazu eine je Hohlraum."""

    hohlraeume: Tuple[float, ...]
    """Die Flaeche jedes Hohlraums auf diesem Gitter, in mm²."""

    I_T: float
    """In mm⁴."""

    schritte: int
    """So viele Schritte brauchten die konjugierten Gradienten."""


@dataclass(frozen=True)
class Torsion:
    """``I_T`` eines Querschnitts -- und die beiden Gitter, aus denen es kommt."""

    grob: Gitterlauf
    fein: Gitterlauf

    @property
    def I_T(self) -> float:
        """Nach Richardson aus beiden Gittern, in mm⁴."""
        return (4.0 * self.fein.I_T - self.grob.I_T) / 3.0


def torsion(polygone: Sequence[Sequence[Punkt]], traegt: Sequence[bool],
            eltern: Sequence[Optional[int]]) -> Torsion:
    """
    ``I_T`` der Polygone, in mm, wie sie die Zeichnung einer Analyse fuehrt:
    je Polygon, ob es Material hat, und in welchem es liegt. Material ist,
    wo das innerste Polygon Material hat.
    """
    umriss = _Umriss(polygone, traegt, eltern)
    ys, zs = _gitter(polygone)
    grob = _lauf(umriss, ys, zs)
    while True:
        ys, zs = _halbiert(ys), _halbiert(zs)
        fein = _lauf(umriss, ys, zs)
        if (abs(grob.I_T - fein.I_T) <= ABWEICHUNG * fein.I_T
                or 4 * fein.zellen > ZELLEN_HOECHSTENS
                or 4 * fein.spalten * fein.zeilen > GITTER_HOECHSTENS):
            return Torsion(grob, fein)
        grob = fein


# ===========================================================================
# Wo Material ist
# ===========================================================================


def _kanten(p: Sequence[Punkt]) -> Iterator[Tuple[Punkt, Punkt]]:
    return zip(p, list(p[1:]) + [p[0]])


class _Umriss:
    """Die Polygone, befragt entlang einer Geraden: wo dort Material ist."""

    def __init__(self, polygone: Sequence[Sequence[Punkt]], traegt: Sequence[bool],
                 eltern: Sequence[Optional[int]]) -> None:
        self.kanten = [list(_kanten(p)) for p in polygone]
        self.traegt = list(traegt)
        self.tiefe = []
        for e in eltern:
            t = 0
            while e is not None:
                t, e = t + 1, eltern[e]
            self.tiefe.append(t)

    def waagrecht(self, z: float) -> List[Strecke]:
        """Die Strecken in y mit Material auf der Geraden auf Hoehe ``z``."""
        return self._strecken(z, 0)

    def lotrecht(self, y: float) -> List[Strecke]:
        """Die Strecken in z mit Material auf der Geraden bei ``y``."""
        return self._strecken(y, 1)

    def _strecken(self, c: float, laengs: int) -> List[Strecke]:
        """
        Wo die Gerade die Kanten schneidet -- eine Ecke auf ihr zaehlt zur
        Seite darunter --, und dazwischen, ob das innerste Polygon traegt.
        """
        quer = 1 - laengs
        schnitte = []
        for k, kanten in enumerate(self.kanten):
            for a, b in kanten:
                if (a[quer] > c) != (b[quer] > c):
                    u = a[laengs] + (c - a[quer]) * (b[laengs] - a[laengs]) / (b[quer] - a[quer])
                    schnitte.append((u, k))
        schnitte.sort()
        innen: Set[int] = set()
        strecken: List[Strecke] = []
        anfang = None
        i = 0
        while i < len(schnitte):
            u = schnitte[i][0]
            while i < len(schnitte) and schnitte[i][0] == u:
                innen ^= {schnitte[i][1]}
                i += 1
            material = bool(innen) and self.traegt[max(innen, key=self.tiefe.__getitem__)]
            if material and anfang is None:
                anfang = u
            elif not material and anfang is not None:
                strecken.append((anfang, u))
                anfang = None
        return strecken


def _darin(strecken: Sequence[Strecke], u: float) -> Optional[Strecke]:
    """Die Strecke, in deren Innern ``u`` liegt."""
    return next(((a, b) for a, b in strecken if a < u < b), None)


# ===========================================================================
# Das Gitter
# ===========================================================================


def _gitter(polygone: Sequence[Sequence[Punkt]]) -> Tuple[List[float], List[float]]:
    """Die Gitterlinien in y und z: durch jede achsparallele Kante, dazwischen gleich geteilt."""
    ecken = [q for p in polygone for q in p]
    unten = [min(q[i] for q in ecken) for i in (0, 1)]
    oben = [max(q[i] for q in ecken) for i in (0, 1)]
    zelle = max(o - u for o, u in zip(oben, unten)) / TEILUNG
    linien = []
    for i in (0, 1):
        feste = sorted([unten[i], oben[i]] + [a[i] for p in polygone for a, b in _kanten(p)
                                              if abs(a[i] - b[i]) <= TOLERANZ])
        punkte = [feste[0]]
        for w in feste[1:]:
            if w - punkte[-1] > TOLERANZ:
                punkte.append(w)
        teil = [punkte[0]]
        for a, b in zip(punkte, punkte[1:]):
            n = max(1, math.ceil((b - a) / zelle - 1e-9))
            teil += [a + (b - a) * (k + 1) / n for k in range(n - 1)] + [b]
        linien.append(teil)
    return linien[0], linien[1]


def _halbiert(linien: Sequence[float]) -> List[float]:
    """Jede Zelle halbiert."""
    neu = [linien[0]]
    for a, b in zip(linien, linien[1:]):
        neu += [(a + b) / 2.0, b]
    return neu


# ===========================================================================
# Ein Lauf auf einem Gitter
# ===========================================================================


def _lauf(umriss: _Umriss, ys: Sequence[float], zs: Sequence[float]) -> Gitterlauf:
    """Die Zellen einteilen, das Gleichungssystem aufstellen und loesen."""
    zellen = _Zellen(umriss, ys, zs)
    system = _System(zellen)
    phi, schritte = _gradienten(system.diagonale, system.kanten, system.last)
    return Gitterlauf(spalten=zellen.nx, zeilen=zellen.nz, zellen=len(system.nummer),
                      hohlraeume=tuple(system.flaechen),
                      I_T=sum(b * x for b, x in zip(system.last, phi)), schritte=schritte)


class _Zellen:
    """
    Die Zellen eines Gitters, zeilenweise gezaehlt, ``k = j·nx + i``. Eine
    Zelle hat Material, wenn ihre Mitte darin liegt; ueber Kanten verbunden,
    bilden solche Zellen einen Teil.
    """

    def __init__(self, umriss: _Umriss, ys: Sequence[float], zs: Sequence[float]) -> None:
        nx, nz = self.nx, self.nz = len(ys) - 1, len(zs) - 1
        self.yc = [(a + b) / 2.0 for a, b in zip(ys, ys[1:])]
        self.zc = [(a + b) / 2.0 for a, b in zip(zs, zs[1:])]
        self.dy = [b - a for a, b in zip(ys, ys[1:])]
        self.dz = [b - a for a, b in zip(zs, zs[1:])]
        zeilen = [umriss.waagrecht(z) for z in self.zc]
        spalten = [umriss.lotrecht(y) for y in self.yc]
        #: Je Zelle die Strecke in y mit Material, in der ihre Mitte liegt; ohne Material None.
        self.waagrecht = [_darin(zeilen[k // nx], self.yc[k % nx]) for k in range(nx * nz)]
        #: Dasselbe in z. Liegt die Mitte genau auf einem Rand, ist die Strecke ein Punkt.
        self.lotrecht: List[Optional[Strecke]] = []
        for k, w in enumerate(self.waagrecht):
            z = self.zc[k // nx]
            self.lotrecht.append(None if w is None else _darin(spalten[k % nx], z) or (z, z))
        #: Je Zelle mit Material die Nummer ihres Teils, sonst -1.
        self.teil = [-1] * (nx * nz)
        self.teile = 0
        for k, w in enumerate(self.waagrecht):
            if w is not None and self.teil[k] < 0:
                for m in self.fuellen([k], lambda m: self.waagrecht[m] is not None):
                    self.teil[m] = self.teile
                self.teile += 1
        self.rand = [k for k in range(nx * nz) if k % nx in (0, nx - 1) or k // nx in (0, nz - 1)]

    def flaeche(self, k: int) -> float:
        """Die Flaeche von Zelle ``k``, in mm²."""
        return self.dy[k % self.nx] * self.dz[k // self.nx]

    def hohlraeume(self, t: int) -> List[Set[int]]:
        """
        Die Hohlraeume von Teil ``t``: was nicht zu ihm gehoert und den Rand
        des Gitters nicht erreicht -- samt einem anderen Teil darin.
        """
        def fremd(m: int) -> bool:
            return self.teil[m] != t
        gesehen = self.fuellen([k for k in self.rand if fremd(k)], fremd)
        raeume: List[Set[int]] = []
        for k in range(len(self.teil)):
            if fremd(k) and k not in gesehen:
                raeume.append(self.fuellen([k], fremd))
                gesehen |= raeume[-1]
        return raeume

    def fuellen(self, start: Sequence[int], frei: Callable[[int], bool]) -> Set[int]:
        """Die Zellen, die von ``start`` aus ueber Kanten erreichbar sind, nur durch freie."""
        gesehen, stapel = set(start), list(start)
        while stapel:
            for m in self._nachbarn(stapel.pop()):
                if m not in gesehen and frei(m):
                    gesehen.add(m)
                    stapel.append(m)
        return gesehen

    def _nachbarn(self, k: int) -> Iterator[int]:
        i, j = k % self.nx, k // self.nx
        if i + 1 < self.nx:
            yield k + 1
        if i > 0:
            yield k - 1
        if j + 1 < self.nz:
            yield k + self.nx
        if j > 0:
            yield k - self.nx


class _System:
    """
    Das Gleichungssystem auf den Zellen: eine Unbekannte je Zelle mit
    Material, dann eine je Hohlraum. Die Matrix als Diagonale und
    Kopplungen, symmetrisch.
    """

    def __init__(self, zellen: _Zellen) -> None:
        z = self.zellen = zellen
        self.nummer = {k: p for p, k in enumerate(k for k, t in enumerate(z.teil) if t >= 0)}
        #: Je Teil: die Zellen seiner Hohlraeume, zur Unbekannten ihres Hohlraums.
        self.hohlraum_von: List[Dict[int, int]] = []
        #: Die Flaeche jedes Hohlraums, in der Folge der Unbekannten.
        self.flaechen: List[float] = []
        for t in range(z.teile):
            hohl: Dict[int, int] = {}
            for raum in z.hohlraeume(t):
                hohl.update(dict.fromkeys(raum, len(self.nummer) + len(self.flaechen)))
                self.flaechen.append(sum(z.flaeche(m) for m in raum))
            self.hohlraum_von.append(hohl)
        self.diagonale = [0.0] * (len(self.nummer) + len(self.flaechen))
        self.kanten: List[Tuple[int, int, float]] = []
        for j in range(z.nz):
            self._reihe(range(j * z.nx, (j + 1) * z.nx), z.yc, z.dy, z.waagrecht, z.dz[j])
        for i in range(z.nx):
            self._reihe(range(i, z.nx * z.nz, z.nx), z.zc, z.dz, z.lotrecht, z.dy[i])
        self.last = [2.0 * z.flaeche(k) for k in self.nummer] + [2.0 * f for f in self.flaechen]

    def _reihe(self, reihe: Sequence[int], mitten: Sequence[float], groessen: Sequence[float],
               strecken: Sequence[Optional[Strecke]], kante: float) -> None:
        """
        Die Kanten zwischen den Zellen einer Zeile oder Spalte, auch die an
        ihren Enden. Mitten, Groessen und Strecken gelten entlang der Reihe,
        ``kante`` ist die Laenge jeder Kante quer dazu.
        """
        teil = self.zellen.teil
        for n in range(-1, len(reihe)):
            k = reihe[n] if n >= 0 else None
            m = reihe[n + 1] if n + 1 < len(reihe) else None
            hat_k = k is not None and teil[k] >= 0
            hat_m = m is not None and teil[m] >= 0
            if hat_k and hat_m:
                self._koppeln(self.nummer[k], self.nummer[m], kante / (mitten[n + 1] - mitten[n]))
                continue
            if hat_k:
                self._zum_rand(k, m, kante, strecken[k][1] - mitten[n], groessen[n])
            if hat_m:
                self._zum_rand(m, k, kante, mitten[n + 1] - strecken[m][0], groessen[n + 1])

    def _zum_rand(self, k: int, m: Optional[int], kante: float, abstand: float,
                  zelle: float) -> None:
        """Von Zelle ``k`` zum Rand hin, hinter dem ``m`` liegt: aussen φ = 0, sonst sein Hohlraum."""
        h = self.hohlraum_von[self.zellen.teil[k]].get(m) if m is not None else None
        self._koppeln(self.nummer[k], h, kante / max(abstand, NAEHE * zelle))

    def _koppeln(self, p: int, q: Optional[int], g: float) -> None:
        """Leitwert ``g`` zwischen den Unbekannten ``p`` und ``q``, ohne ``q`` zu φ = 0."""
        self.diagonale[p] += g
        if q is not None:
            self.diagonale[q] += g
            self.kanten.append((p, q, g))


def _gradienten(diagonale: Sequence[float], kanten: Sequence[Tuple[int, int, float]],
                last: Sequence[float]) -> Tuple[List[float], int]:
    """
    ``A·x = last`` mit konjugierten Gradienten, ``A`` aus Diagonale und
    Kopplungen, die Diagonale als Vorkonditionierer.
    """
    n = len(last)
    x = [0.0] * n
    if n == 0:
        return x, 0
    r = list(last)
    kehr = [1.0 / d for d in diagonale]
    z = [a * b for a, b in zip(r, kehr)]
    p = list(z)
    rz = sum(a * b for a, b in zip(r, z))
    grenze = GENAUIGKEIT ** 2 * sum(b * b for b in last)
    hoechstens = 10 * n + 100
    for schritt in range(1, hoechstens + 1):
        q = [d * v for d, v in zip(diagonale, p)]
        for a, b, g in kanten:
            q[a] -= g * p[b]
            q[b] -= g * p[a]
        alpha = rz / sum(a * b for a, b in zip(p, q))
        x = [a + alpha * b for a, b in zip(x, p)]
        r = [a - alpha * b for a, b in zip(r, q)]
        if sum(a * a for a in r) <= grenze:
            return x, schritt
        z = [a * b for a, b in zip(r, kehr)]
        rz, alt = sum(a * b for a, b in zip(r, z)), rz
        p = [a + rz / alt * b for a, b in zip(z, p)]
    raise ArithmeticError(f"Die Torsion konvergiert nicht in {hoechstens} Schritten.")
