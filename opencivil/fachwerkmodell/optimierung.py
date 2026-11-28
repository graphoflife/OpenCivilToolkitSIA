"""
opencivil/fachwerkmodell/optimierung.py -- das leichteste Fachwerk im Gleichgewicht, als lineare Optimierung.

VERANTWORTUNG:
Zu gegebenen Stäben die Kräfte, die die Lasten im Gleichgewicht zu den
Lagern tragen und dabei die kleinste Summe aus Kraft mal Länge haben -- Zug
mit seinem Gewicht, Druck mit seinem (:func:`optimieren`). Gelöst mit einem
primal-dualen Innere-Punkte-Verfahren nach Mehrotra, je Schritt mit dem
Gleichungslöser der Stabwerke (:class:`~opencivil.stabwerk.matrix.Zerlegung`)
in einem Profil, das die Folge nach Cuthill-McKee schmal hält.

DIE AUFGABE:

    min  Σ l_i · (w_Z · q⁺_i + w_D · q⁻_i) + M · Σ (r⁺_k + r⁻_k)
    mit  B · (q⁺ − q⁻) + r⁺ − r⁻ = f   und allen Unbekannten ≥ 0

Je Stab eine Spalte von B: an seinen zwei Knoten die Richtung von einem
zum andern, wo kein Lager hält (:class:`Gleichgewicht`). ``q⁺ − q⁻`` ist
seine Kraft, Zug positiv. Ein Stab, der keinen Zug tragen darf, hat kein
``q⁺``: seine Kraft ist ``−q⁻``. ``r⁺ − r⁻`` ist der Rest: was sich mit diesen
Stäben nicht ins Gleichgewicht bringen lässt. Er kostet ``M`` je Einheit,
mehr als jeder Weg durch die Stäbe, und ist null, wo ein Gleichgewicht
geht. Wo keins geht, bleibt er stehen und sagt, wo -- statt dass das
Verfahren nicht zu Ende kommt. Zugleich hält er die Gleichungen lösbar, auch
an einem Knoten, an dem kein Stab mehr hängt.

DIE VIRTUELLEN VERSCHIEBUNGEN:
Die dualen Unbekannten ``u``, je Zeile eine, sind ein Feld virtueller
Verschiebungen. Ein Stab ``i`` mit der Dehnung ``b_iᵀ · u / l_i`` über w_Z
oder unter −w_D machte das Fachwerk leichter: danach sucht die Suche
(:mod:`~opencivil.fachwerkmodell.suche`) die Stäbe, die sie zufügt.

OHNE ZUSATZ AUF DER DIAGONALE:
Eine kleine Zahl auf der Diagonale, gegen eine singuläre Matrix, liess das
Verfahren an einer Wand mit 0.25 m Raster nach 80 Schritten mit einem Rest
von 10⁻⁵ stehen (2026-11-27): die Richtung passte nicht mehr genau zu den
Gleichungen. Der Rest ``r`` macht dasselbe richtig -- er gehört zur
Aufgabe, und die Richtung bleibt genau.
"""

from __future__ import annotations

from dataclasses import dataclass
from operator import mul
from typing import Dict, List, Optional, Sequence, Set, Tuple

from opencivil.stabwerk.matrix import Profilmatrix, Zerlegung, nummerierung

#: Wie genau gelöst wird: der Rest des Gleichgewichts, der dualen Bedingungen
#: und der Abstand der beiden Zielwerte, je bezogen -- nach Vorgabe.
GENAUIGKEIT = 1e-8

#: Wie viele Schritte das Verfahren höchstens macht -- nach Vorgabe.
HOECHSTENS = 100

#: Welchen Teil des Wegs zum Rand ein Schritt geht -- nach Vorgabe.
SCHRITTANTEIL = 0.995

#: Eine Spalte von B: je Zeile, in der der Stab steht, ihr Wert.
Spalte = Tuple[Tuple[int, float], ...]


@dataclass(frozen=True)
class Optimum:
    """Was die Optimierung fand -- in den Einheiten von ``f`` und der Kosten."""

    q: Tuple[float, ...]
    """Je Stab seine Kraft, Zug positiv."""

    u: Tuple[float, ...]
    """Je Zeile die virtuelle Verschiebung."""

    rest: Tuple[float, ...]
    """Je Zeile, was sich nicht ins Gleichgewicht bringen liess -- null, wo es ging."""

    ziel: float
    """Σ l · (w_Z · q⁺ + w_D · q⁻), ohne den Rest."""

    schritte: int
    geloest: bool
    """Ob die :data:`GENAUIGKEIT` erreicht ist."""


class Gleichgewicht:
    """
    Die Gleichgewichtsbedingungen zu gegebenen Stäben: B, je Stab eine
    Spalte, in einer Folge der Zeilen, die das Profil der Normalmatrix
    schmal hält (:func:`~opencivil.stabwerk.matrix.nummerierung`).
    """

    def __init__(self, zeilen: int, spalten: Sequence[Spalte]) -> None:
        self.n = zeilen
        nachbarn: Dict[int, Set[int]] = {k: set() for k in range(zeilen)}
        for s in spalten:
            for k, _ in s:
                nachbarn[k].update(h for h, _ in s if h != k)
        self.platz = [0] * zeilen
        """Je Zeile ihr Platz in der Normalmatrix."""
        for p, k in enumerate(nummerierung(list(range(zeilen)), nachbarn)):
            self.platz[k] = p
        self.spalten = [tuple((self.platz[k], w) for k, w in s) for s in spalten]
        self.erste = Profilmatrix.aus_gruppen(
            zeilen, ([k for k, _ in s] for s in self.spalten)).erste
        # Je Stab, was er zur Normalmatrix B·D·Bᵀ beiträgt: (Zeile, Platz in
        # ihrem Profil, Produkt der zwei Werte) -- einmal gerechnet, in
        # jedem Schritt mit seinem d gebraucht.
        self.beitraege = []
        for s in self.spalten:
            teile = []
            for a, (k, wk) in enumerate(s):
                for h, wh in s[:a + 1]:
                    i, j = (k, h) if k >= h else (h, k)
                    teile.append((i, j - self.erste[i], wk * wh))
            self.beitraege.append(tuple(teile))

    def mal(self, q: Sequence[float]) -> List[float]:
        """``B · q``, in der Folge der Normalmatrix."""
        y = [0.0] * self.n
        for s, qi in zip(self.spalten, q):
            if qi:
                for k, w in s:
                    y[k] += w * qi
        return y

    def mal_transponiert(self, u: Sequence[float]) -> List[float]:
        """``Bᵀ · u``, ``u`` in der Folge der Normalmatrix."""
        return [sum(w * u[k] for k, w in s) for s in self.spalten]

    def normalmatrix(self, d: Sequence[float], d_rest: Sequence[float]) -> Profilmatrix:
        """``B · diag(d) · Bᵀ + diag(d_rest)``."""
        K = Profilmatrix(self.n, self.erste)
        z = K.zeilen
        for teile, di in zip(self.beitraege, d):
            for i, j, w in teile:
                z[i][j] += di * w
        for i, di in enumerate(d_rest):
            z[i][-1] += di
        return K


def optimieren(gl: Gleichgewicht, f: Sequence[float], kosten_zug: Sequence[Optional[float]],
               kosten_druck: Sequence[float], strafe: float) -> Optimum:
    """
    Die Kräfte der Stäbe mit dem kleinsten Ziel. ``f`` je Zeile die Last,
    ``kosten_zug`` und ``kosten_druck`` je Stab ``w_Z · l`` und ``w_D · l``
    -- ``None`` statt ``w_Z · l``, wo ein Stab keinen Zug tragen darf --,
    ``strafe`` das ``M`` des Rests. Am besten ist ``f`` so bezogen, dass
    seine grösste Zahl um 1 liegt.
    """
    m, n = len(gl.spalten), gl.n
    fp = [0.0] * n
    for k, w in enumerate(f):
        fp[gl.platz[k]] = w
    # Die Unbekannten, eine nach der andern: q⁺ der Stäbe, die Zug tragen
    # dürfen (``zug``), ab ``druck`` q⁻ jedes Stabs, ab ``plus`` r⁺ und ab
    # ``minus`` r⁻ je Zeile -- ``alle`` zusammen.
    zug = [i for i, k in enumerate(kosten_zug) if k is not None]
    druck = len(zug)
    plus = druck + m
    minus = plus + n
    alle = minus + n
    c = [*(kosten_zug[i] for i in zug), *kosten_druck, *([strafe] * (2 * n))]

    def je_stab(werte: Sequence[float]) -> List[float]:
        """Die Werte der Unbekannten q⁺, je Stab -- null, wo er keine hat."""
        v = [0.0] * m
        for i, w in zip(zug, werte):
            v[i] = w
        return v

    # Der Start: alle Kräfte 1, die dualen Bedingungen erfüllt mit y = 0.
    x = [1.0] * alle
    s = list(c)
    y = [0.0] * n
    norm_f = 1.0 + sum(map(abs, fp))
    norm_c = 1.0 + sum(map(abs, c[:plus]))
    geloest = False
    schritt = 0
    for schritt in range(HOECHSTENS + 1):
        q = [a - b for a, b in zip(je_stab(x[:druck]), x[druck:plus])]
        Bq = gl.mal(q)
        rp = [fk - bk - a + b for fk, bk, a, b in zip(fp, Bq, x[plus:minus], x[minus:])]
        Bty = gl.mal_transponiert(y)
        rd = ([c[j] - Bty[i] - s[j] for j, i in enumerate(zug)]
              + [c[druck + i] + Bty[i] - s[druck + i] for i in range(m)]
              + [c[plus + k] - y[k] - s[plus + k] for k in range(n)]
              + [c[minus + k] + y[k] - s[minus + k] for k in range(n)])
        cx = sum(map(mul, c, x))
        fy = sum(map(mul, fp, y))
        if (sum(map(abs, rp)) / norm_f < GENAUIGKEIT and sum(map(abs, rd)) / norm_c < GENAUIGKEIT
                and abs(cx - fy) / (1.0 + abs(cx)) < GENAUIGKEIT):
            geloest = True
            break
        if schritt == HOECHSTENS:
            break
        mu = sum(map(mul, x, s)) / alle
        d = [a / b for a, b in zip(x, s)]
        Z = Zerlegung(gl.normalmatrix([a + b for a, b in zip(je_stab(d[:druck]), d[druck:plus])],
                                      [d[plus + k] + d[minus + k] for k in range(n)]))

        def richtung(rxs: List[float]) -> Tuple[List[float], List[float], List[float]]:
            # Aus A·D·Aᵀ·Δy = rp + A·(D·rd − S⁻¹·rxs), dann Δs und Δx.
            t = [rxs[j] / s[j] - d[j] * rd[j] for j in range(alle)]
            At = gl.mal([a - b for a, b in zip(je_stab(t[:druck]), t[druck:plus])])
            dy = Z.loese([rp[k] - At[k] - t[plus + k] + t[minus + k] for k in range(n)])
            Btdy = gl.mal_transponiert(dy)
            ds = ([rd[j] - Btdy[i] for j, i in enumerate(zug)]
                  + [rd[druck + i] + Btdy[i] for i in range(m)]
                  + [rd[plus + k] - dy[k] for k in range(n)]
                  + [rd[minus + k] + dy[k] for k in range(n)])
            dx = [(rxs[j] - x[j] * ds[j]) / s[j] for j in range(alle)]
            return dx, dy, ds

        # Vorhersage ohne Zentrierung, dann die Korrektur nach Mehrotra.
        dxa, _, dsa = richtung([-a * b for a, b in zip(x, s)])
        ap, ad = _weite(x, dxa), _weite(s, dsa)
        mu_a = sum((x[j] + ap * dxa[j]) * (s[j] + ad * dsa[j]) for j in range(alle)) / alle
        sigma = (mu_a / mu) ** 3
        dx, dy, ds = richtung([sigma * mu - x[j] * s[j] - dxa[j] * dsa[j] for j in range(alle)])
        ap = min(1.0, SCHRITTANTEIL * _weite(x, dx))
        ad = min(1.0, SCHRITTANTEIL * _weite(s, ds))
        x = [a + ap * b for a, b in zip(x, dx)]
        y = [a + ad * b for a, b in zip(y, dy)]
        s = [a + ad * b for a, b in zip(s, ds)]
    q = tuple(a - b for a, b in zip(je_stab(x[:druck]), x[druck:plus]))
    rest = [a - b for a, b in zip(x[plus:minus], x[minus:])]
    return Optimum(
        q=q, u=tuple(y[gl.platz[k]] for k in range(n)), rest=tuple(rest[gl.platz[k]] for k in range(n)),
        ziel=sum(map(mul, c[:plus], x[:plus])), schritte=schritt, geloest=geloest)


def _weite(v: Sequence[float], dv: Sequence[float]) -> float:
    """Wie weit ein Schritt längs ``dv`` gehen kann, bis eine Zahl von ``v`` null wird -- höchstens 1."""
    a = 1.0
    for vi, dvi in zip(v, dv):
        if dvi < 0.0 and -vi / dvi < a:
            a = -vi / dvi
    return a
