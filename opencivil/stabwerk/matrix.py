"""
opencivil/stabwerk/matrix.py -- das Gleichungssystem eines Stabwerks.

VERANTWORTUNG:
Loest ``K · x = f`` fuer die Steifigkeitsmatrix eines Stabwerks: symmetrisch
und, solange das System haelt, positiv definit. Eine Zerlegung fuer alle
Lastfaelle; jeder ist danach nur noch eine Vorwaerts- und eine
Rueckwaertsrechnung.

IM PROFIL GESPEICHERT:
Ein Stab koppelt nur die Unbekannten seiner beiden Enden. In jeder Zeile von
K steht darum links der Diagonale wenig, und was links der ersten Zahl einer
Zeile steht, bleibt beim Zerlegen null. Gespeichert wird je Zeile nur das
Stueck von der ersten belegten Spalte bis zur Diagonale -- das Profil --,
und zerlegt wird darin. Bei 600 Unbekannten und einer Bandbreite von 30 sind
das Millisekunden; dicht gerechnet waeren es Sekunden, im Browser mehr.

DIE NUMMERIERUNG:
Wie schmal das Profil ist, haengt an der Reihenfolge der Unbekannten.
:func:`nummerierung` ordnet die Knoten nach der umgekehrten
Cuthill-McKee-Folge: Breitensuche von einem Randknoten aus, Nachbarn mit
kleinem Grad zuerst, am Ende umgedreht. Nachbarn liegen danach nahe
beieinander, gleich in welcher Reihenfolge sie gezeichnet wurden.

SINGULAER:
Ist das System beweglich, wird ein Pivot null -- bis auf Rundung. Als null
gilt ``d_i <= SCHRANKE · K_ii``: gemessen an der Steifigkeit derselben
Unbekannten, nicht an einer festen Zahl, damit die Einheiten nicht zaehlen.
Dann wird nicht regularisiert -- eine Steifigkeit, die das System nicht hat,
waere erfunden --, sondern mit dieser Unbekannten festgehalten zu Ende
zerlegt. Daraus folgt die freie Bewegung (:meth:`Zerlegung.bewegung`): die
festgehaltene Unbekannte auf eins, die uebrigen aus ``K_FF · x_F = -K_Fs``.
Die Probe ``|K · x|`` sagt, ob es wirklich eine ist.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from operator import mul
from typing import (
    Hashable, Iterable, List, Mapping, Optional, Sequence, Tuple, TypeVar,
)

#: Unter diesem Anteil seiner eigenen Steifigkeit gilt ein Pivot als null.
#: Zehn Groessenordnungen: so weit liegen Dehn- und Biegesteifigkeit eines
#: schlanken Stabs nie auseinander, eine echte Bewegung aber immer -- dort
#: bleibt nur die Rundung, rund 1e-16.
SCHRANKE = 1e-10

H = TypeVar("H", bound=Hashable)


class Profilmatrix:
    """
    Eine symmetrische Matrix im Profil: je Zeile ``i`` die Werte der Spalten
    ``erste[i]`` bis ``i``. Was rechts der Diagonale steht, ist das Spiegelbild.
    """

    def __init__(self, n: int, erste: Sequence[int]) -> None:
        if len(erste) != n:
            raise ValueError("Je Zeile eine erste Spalte.")
        for i, m in enumerate(erste):
            if not 0 <= m <= i:
                raise ValueError(f"Zeile {i}: die erste Spalte {m} liegt nicht vor der Diagonale.")
        self.n = n
        self.erste: List[int] = list(erste)
        self.zeilen: List[List[float]] = [[0.0] * (i - m + 1) for i, m in enumerate(erste)]

    @classmethod
    def aus_gruppen(cls, n: int, gruppen: Iterable[Sequence[int]]) -> "Profilmatrix":
        """
        Das Profil, das Gruppen gekoppelter Unbekannter brauchen -- je Stab
        die seiner beiden Enden. Eine Unbekannte ohne Gruppe hat nur ihre
        Diagonale.
        """
        erste = list(range(n))
        for gruppe in gruppen:
            if not gruppe:
                continue
            kleinste = min(gruppe)
            for i in gruppe:
                if kleinste < erste[i]:
                    erste[i] = kleinste
        return cls(n, erste)

    def _platz(self, i: int, j: int) -> Tuple[int, int]:
        if j > i:
            i, j = j, i
        m = self.erste[i]
        if j < m:
            raise IndexError(f"({i}, {j}) liegt ausserhalb des Profils (Zeile {i} beginnt bei {m}).")
        return i, j - m

    def addiere(self, i: int, j: int, wert: float) -> None:
        """Addiert ``wert`` an ``(i, j)`` -- und damit an ``(j, i)``."""
        zeile, spalte = self._platz(i, j)
        self.zeilen[zeile][spalte] += wert

    def addiere_block(self, indizes: Sequence[int], block: Sequence[Sequence[float]]) -> None:
        """
        Addiert einen symmetrischen Block auf die Unbekannten ``indizes``,
        jedes Paar einmal. Die Indizes muessen verschieden sein -- sonst
        zaehlte ein Wert doppelt.
        """
        if len(set(indizes)) != len(indizes):
            raise ValueError("Ein Block braucht verschiedene Unbekannte.")
        for p, i in enumerate(indizes):
            reihe = block[p]
            for q in range(p + 1):
                wert = reihe[q]
                if wert:
                    self.addiere(i, indizes[q], wert)

    def wert(self, i: int, j: int) -> float:
        if j > i:
            i, j = j, i
        m = self.erste[i]
        return self.zeilen[i][j - m] if j >= m else 0.0

    def diagonale(self, i: int) -> float:
        return self.zeilen[i][-1]

    def mal(self, x: Sequence[float]) -> List[float]:
        """``K · x``."""
        y = [0.0] * self.n
        for i, zeile in enumerate(self.zeilen):
            m = self.erste[i]
            xi = x[i]
            summe = 0.0
            for k, wert in enumerate(zeile[:-1]):
                j = m + k
                summe += wert * x[j]
                y[j] += wert * xi
            y[i] += summe + zeile[-1] * xi
        return y

    @property
    def eintraege(self) -> int:
        """Wie viele Zahlen das Profil haelt -- ein Mass fuer die Arbeit."""
        return sum(len(z) for z in self.zeilen)


@dataclass(frozen=True)
class Bewegung:
    """
    Die freie Bewegung eines beweglichen Systems: eine Loesung von
    ``K · x = 0`` mit ``x_s = 1``.
    """

    index: int
    """Die Unbekannte, an der die Zerlegung keinen Halt mehr fand."""

    x: List[float]
    rest: float
    """``max|K · x|`` bezogen auf ``max K_ii · max|x|`` -- nahe null bei einer echten."""


class Zerlegung:
    """
    ``K = L · D · Lᵀ`` im Profil von ``K``.

    ``singulaer`` nennt die Unbekannten, an denen der Pivot null war; sie
    sind festgehalten, und ``loese`` setzt sie null. Wer rechnet, prueft
    vorher, ob die Liste leer ist.
    """

    def __init__(self, K: Profilmatrix) -> None:
        self.K = K
        n = K.n
        erste = K.erste
        self.L: List[List[float]] = [[] for _ in range(n)]
        self.D: List[float] = [0.0] * n
        self.singulaer: List[int] = []
        gestrichen = set()
        for i in range(n):
            mi = erste[i]
            a = K.zeilen[i]
            breite = i - mi
            u = [0.0] * breite          # L_ij · D_j
            li = [0.0] * breite         # L_ij
            for j in range(mi, i):
                if j in gestrichen:
                    continue
                mj = erste[j]
                ab = mj if mj > mi else mi
                s = a[j - mi]
                if ab < j:
                    s -= sum(map(mul, u[ab - mi:j - mi], self.L[j][ab - mj:j - mj]))
                u[j - mi] = s
                li[j - mi] = s / self.D[j]
            kii = a[breite]
            d = kii - sum(map(mul, u, li))
            if kii <= 0.0 or d <= SCHRANKE * kii:
                # Festgehalten: weiter zerlegt wird ohne diese Unbekannte.
                gestrichen.add(i)
                self.singulaer.append(i)
                self.D[i] = 1.0
                self.L[i] = [0.0] * breite
            else:
                self.D[i] = d
                self.L[i] = li
        self._gestrichen = gestrichen

    def loese(self, f: Sequence[float]) -> List[float]:
        """``x`` aus ``K · x = f``; festgehaltene Unbekannte sind null."""
        n = self.K.n
        erste = self.K.erste
        if len(f) != n:
            raise ValueError(f"Die rechte Seite hat {len(f)} statt {n} Zahlen.")
        y = [0.0] * n
        for i in range(n):
            if i in self._gestrichen:
                continue
            mi = erste[i]
            y[i] = f[i] - sum(map(mul, self.L[i], y[mi:i]))
        x = [y[i] / self.D[i] for i in range(n)]
        for r in range(n - 1, -1, -1):
            xr = x[r]
            if not xr:
                continue
            mr = erste[r]
            for k, lrk in enumerate(self.L[r]):
                if lrk:
                    x[mr + k] -= lrk * xr
        return x

    def bewegung(self) -> Optional[Bewegung]:
        """
        Die freie Bewegung an der ersten Unbekannten ohne Halt -- ``None``,
        wenn das System haelt.
        """
        if not self.singulaer:
            return None
        s = self.singulaer[0]
        K = self.K
        rechts = [-K.wert(i, s) if i not in self._gestrichen else 0.0 for i in range(K.n)]
        x = self.loese(rechts)
        x[s] = 1.0
        gross = max(abs(v) for v in x) or 1.0
        x = [v / gross for v in x]
        rest_ = K.mal(x)
        steif = max(K.diagonale(i) for i in range(K.n)) or 1.0
        return Bewegung(index=s, x=x, rest=max(abs(r) for r in rest_) / steif)


def _ebenen(start: H, nachbarn: Mapping[H, Iterable[H]]) -> List[List[H]]:
    """Die Ebenen der Breitensuche von ``start`` aus."""
    gesehen = {start}
    ebenen = [[start]]
    while True:
        naechste = []
        for k in ebenen[-1]:
            for n in nachbarn.get(k, ()):
                if n not in gesehen:
                    gesehen.add(n)
                    naechste.append(n)
        if not naechste:
            return ebenen
        ebenen.append(naechste)


def nummerierung(knoten: Sequence[H], nachbarn: Mapping[H, Iterable[H]]) -> List[H]:
    """
    Die Knoten in umgekehrter Cuthill-McKee-Folge -- je zusammenhaengendem
    Teil von einem Randknoten aus. Bei gleichem Grad entscheidet die
    Reihenfolge von ``knoten``; so ist die Folge fest.
    """
    position = {k: i for i, k in enumerate(knoten)}
    nach = {k: sorted(set(nachbarn.get(k, ())) & position.keys(), key=position.__getitem__)
            for k in knoten}
    grad = {k: len(nach[k]) for k in knoten}
    rang = lambda k: (grad[k], position[k])  # noqa: E731 -- kurz und nur hier

    def randknoten(start: H) -> H:
        # Ein Knoten moeglichst weit am Rand: von dort ist die Suche am tiefsten
        # und jede Ebene am schmalsten (George und Liu).
        knoten_, tiefe = start, -1
        while True:
            ebenen = _ebenen(knoten_, nach)
            if len(ebenen) - 1 <= tiefe:
                return knoten_
            tiefe = len(ebenen) - 1
            knoten_ = min(ebenen[-1], key=rang)

    besucht = set()
    folge: List[H] = []
    for kandidat in sorted(knoten, key=rang):
        if kandidat in besucht:
            continue
        start = randknoten(kandidat)
        besucht.add(start)
        schlange = deque([start])
        while schlange:
            k = schlange.popleft()
            folge.append(k)
            for n in sorted((n for n in nach[k] if n not in besucht), key=rang):
                besucht.add(n)
                schlange.append(n)
    folge.reverse()
    return folge


def dicht(K: Profilmatrix) -> List[List[float]]:
    """Die volle Matrix -- fuer die Herleitung kleiner Systeme und fuer Proben."""
    return [[K.wert(i, j) for j in range(K.n)] for i in range(K.n)]
