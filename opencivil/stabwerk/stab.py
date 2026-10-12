"""
opencivil/stabwerk/stab.py -- der ebene Stab: Steifigkeit, Lasten, Bettung.

VERANTWORTUNG:
Was ein einzelner Stab zum System beitraegt, in seinen eigenen Achsen: die
Steifigkeitsmatrix, die Lasten als arbeitsgleiche Knotenkraefte, die
Bettung, und die Drehung in die Achsen des Systems. Zusammengebaut wird in
:mod:`~opencivil.stabwerk.system`.

DIE ACHSEN DES STABS:
``x`` laeuft vom Anfang zum Ende, ``y`` steht links davon -- ``x`` um 90° im
Gegenuhrzeigersinn gedreht --, Drehungen zaehlen im Gegenuhrzeigersinn. In
diesen Achsen ist die Steifigkeitsmatrix die des Lehrbuchs. Die gestrichelte
Faser liegt auf der anderen Seite, bei ``-y``: dorthin zeigt ``z`` der
Baustatik, und dort zieht ein positives Moment
(:mod:`~opencivil.stabwerk.verlauf`).

Je Ende drei Unbekannte, in dieser Folge::

    u   laengs, in x
    v   quer, in y
    θ   Drehung, im Gegenuhrzeigersinn

Euler-Bernoulli: eben bleibende Querschnitte, ohne Schubverformung. Laengs
ist der Stab linear, quer kubisch (Hermite) -- fuer einen Stab ohne Bettung
ist das die genaue Loesung, und die Knotenverschiebungen stimmen exakt.

ARBEITSGLEICHE LASTEN:
Eine Last zwischen den Knoten geht als die Knotenkraefte ins System, die an
denselben Verschiebungen dieselbe Arbeit leisten: ``f_i = ∫ N_i · p dx``.
Fuer diesen Stab sind das genau die Volleinspannkraefte mit umgekehrtem
Vorzeichen. Integriert wird nach Gauss-Legendre mit drei Punkten -- exakt
bis Grad fuenf, und eine lineare Last mal eine kubische Formfunktion hat
Grad vier. Ein verteiltes Moment ``m`` leistet Arbeit an der Drehung
``θ = v'``: ``f_i = ∫ N_i' · m dx``.

BETTUNG:
Ein Stab auf einem nachgiebigen Linienlager (Winkler) bekommt zu seiner
Steifigkeit ``k · ∫ Nᵀ N dx`` -- die konsistente Bettungsmatrix. Mit
kubischen Formfunktionen ist das eine Naeherung; das System teilt einen
gebetteten Stab darum in kurze Stuecke (:mod:`~opencivil.stabwerk.system`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple, Union

Matrix = List[List[float]]

#: Gauss-Legendre mit drei Punkten auf [-1, 1]: Stelle und Gewicht.
GAUSS3 = ((-math.sqrt(0.6), 5.0 / 9.0), (0.0, 8.0 / 9.0), (math.sqrt(0.6), 5.0 / 9.0))

#: Die Steifigkeitsmatrix in Zeichen -- fuer die Herleitung.
STEIFIGKEIT_LATEX = (
    r"\mathbf{k} = \begin{bmatrix}"
    r" \frac{EA}{L} & 0 & 0 & -\frac{EA}{L} & 0 & 0 \\"
    r" 0 & \frac{12EI}{L^3} & \frac{6EI}{L^2} & 0 & -\frac{12EI}{L^3} & \frac{6EI}{L^2} \\"
    r" 0 & \frac{6EI}{L^2} & \frac{4EI}{L} & 0 & -\frac{6EI}{L^2} & \frac{2EI}{L} \\"
    r" -\frac{EA}{L} & 0 & 0 & \frac{EA}{L} & 0 & 0 \\"
    r" 0 & -\frac{12EI}{L^3} & -\frac{6EI}{L^2} & 0 & \frac{12EI}{L^3} & -\frac{6EI}{L^2} \\"
    r" 0 & \frac{6EI}{L^2} & \frac{2EI}{L} & 0 & -\frac{6EI}{L^2} & \frac{4EI}{L}"
    r" \end{bmatrix}"
)

#: Die Drehung von den Achsen des Systems in die des Stabs.
DREHUNG_LATEX = (
    r"\mathbf{d} = \mathbf{T} \cdot \mathbf{d}_{glob} \qquad "
    r"\mathbf{T} = \begin{bmatrix} \mathbf{R} & \mathbf{0} \\ \mathbf{0} & \mathbf{R} \end{bmatrix}"
    r" \qquad \mathbf{R} = \begin{bmatrix} \cos\alpha & \sin\alpha & 0 \\"
    r" -\sin\alpha & \cos\alpha & 0 \\ 0 & 0 & 1 \end{bmatrix}"
)

#: Die Bettung in Zeichen -- quer und laengs.
BETTUNG_LATEX = (
    r"\mathbf{k}_{b} = \frac{k_{\perp} \cdot L}{420} \begin{bmatrix}"
    r" 156 & 22L & 54 & -13L \\ 22L & 4L^2 & 13L & -3L^2 \\"
    r" 54 & 13L & 156 & -22L \\ -13L & -3L^2 & -22L & 4L^2 \end{bmatrix}"
    r" \qquad \mathbf{k}_{b,\parallel} = \frac{k_{\parallel} \cdot L}{6}"
    r" \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}"
)

#: Die arbeitsgleichen Knotenkraefte in Zeichen.
LASTEN_LATEX = (
    r"f_i = \int_0^L N_i(x) \cdot p(x)\,\mathrm{d}x"
    r" + \int_0^L N_i'(x) \cdot m(x)\,\mathrm{d}x"
    r" + \sum_j N_i(a_j) \cdot P_j + \sum_j N_i'(a_j) \cdot M_j"
)


def nullmatrix(n: int, m: int = None) -> Matrix:
    return [[0.0] * (n if m is None else m) for _ in range(n)]


def steifigkeit(L: float, EA: float, EI: float) -> Matrix:
    """Die Steifigkeitsmatrix 6 × 6 in den Achsen des Stabs."""
    a = EA / L
    b12, b6, b4, b2 = 12.0 * EI / L ** 3, 6.0 * EI / L ** 2, 4.0 * EI / L, 2.0 * EI / L
    return [
        [a, 0.0, 0.0, -a, 0.0, 0.0],
        [0.0, b12, b6, 0.0, -b12, b6],
        [0.0, b6, b4, 0.0, -b6, b2],
        [-a, 0.0, 0.0, a, 0.0, 0.0],
        [0.0, -b12, -b6, 0.0, b12, -b6],
        [0.0, b6, b2, 0.0, -b6, b4],
    ]


def bettung(L: float, k_quer: float = 0.0, k_laengs: float = 0.0) -> Matrix:
    """
    Die konsistente Bettungsmatrix 6 × 6: ``k · ∫ Nᵀ N dx``, quer auf
    ``v`` und ``θ``, laengs auf ``u``. ``k`` in N/m je m Stab, also N/m².
    """
    k = nullmatrix(6)
    if k_laengs:
        f = k_laengs * L / 6.0
        for i, j, w in ((0, 0, 2.0), (0, 3, 1.0), (3, 0, 1.0), (3, 3, 2.0)):
            k[i][j] += f * w
    if k_quer:
        f = k_quer * L / 420.0
        werte = (
            (156.0, 22.0 * L, 54.0, -13.0 * L),
            (22.0 * L, 4.0 * L * L, 13.0 * L, -3.0 * L * L),
            (54.0, 13.0 * L, 156.0, -22.0 * L),
            (-13.0 * L, -3.0 * L * L, -22.0 * L, 4.0 * L * L),
        )
        stellen = (1, 2, 4, 5)
        for p, i in enumerate(stellen):
            for q, j in enumerate(stellen):
                k[i][j] += f * werte[p][q]
    return k


def summe(*matrizen: Matrix) -> Matrix:
    n = len(matrizen[0])
    return [[sum(m[i][j] for m in matrizen) for j in range(n)] for i in range(n)]


def drehung(c: float, s: float) -> Matrix:
    """``T`` mit ``d = T · d_glob``: je Ende ``u = c·U + s·W``, ``v = -s·U + c·W``, ``θ = Θ``."""
    T = nullmatrix(6)
    for o in (0, 3):
        T[o][o], T[o][o + 1] = c, s
        T[o + 1][o], T[o + 1][o + 1] = -s, c
        T[o + 2][o + 2] = 1.0
    return T


def mal(A: Matrix, x: Sequence[float]) -> List[float]:
    return [sum(a * b for a, b in zip(zeile, x)) for zeile in A]


def transponiert_mal(A: Matrix, x: Sequence[float]) -> List[float]:
    """``Aᵀ · x``."""
    n = len(A[0])
    return [sum(A[i][j] * x[i] for i in range(len(A))) for j in range(n)]


# ===========================================================================
# Formfunktionen
# ===========================================================================


def formfunktionen(x: float, L: float) -> Tuple[float, ...]:
    """
    ``(N1, N2, H1, H2, H3, H4)`` an der Stelle ``x``: laengs linear, quer
    nach Hermite -- je eine Funktion zu ``u1, u2`` und ``v1, θ1, v2, θ2``.
    """
    t = x / L
    t2, t3 = t * t, t * t * t
    return (1.0 - t, t,
            1.0 - 3.0 * t2 + 2.0 * t3, L * (t - 2.0 * t2 + t3),
            3.0 * t2 - 2.0 * t3, L * (t3 - t2))


def ableitungen(x: float, L: float) -> Tuple[float, float, float, float]:
    """``(H1', H2', H3', H4')`` nach ``x`` -- die Drehung ``θ = v'`` je Einheitsverschiebung."""
    t = x / L
    return ((6.0 * t * t - 6.0 * t) / L, 1.0 - 4.0 * t + 3.0 * t * t,
            (6.0 * t - 6.0 * t * t) / L, 3.0 * t * t - 2.0 * t)


# ===========================================================================
# Lasten in den Achsen des Stabs
# ===========================================================================


@dataclass(frozen=True)
class Strecke:
    """
    Eine Last auf ``[a, b]``, linear von ``a`` nach ``b``: Kraft je Laenge
    laengs (``px``) und quer (``py``) und ein Moment je Laenge (``m``, im
    Gegenuhrzeigersinn). In N/m und Nm/m; ``a`` und ``b`` in m ab dem
    Anfang des Stabs (oder Teilstabs).
    """

    a: float
    b: float
    px_a: float = 0.0
    px_b: float = 0.0
    py_a: float = 0.0
    py_b: float = 0.0
    m_a: float = 0.0
    m_b: float = 0.0

    def bei(self, x: float) -> Tuple[float, float, float]:
        """``(px, py, m)`` an der Stelle ``x`` innerhalb von ``[a, b]``."""
        t = (x - self.a) / (self.b - self.a) if self.b > self.a else 0.0
        return (self.px_a + t * (self.px_b - self.px_a),
                self.py_a + t * (self.py_b - self.py_a),
                self.m_a + t * (self.m_b - self.m_a))

    def ausschnitt(self, von: float, bis: float) -> "Strecke":
        """Der Teil auf ``[von, bis]``, in den Achsen ab ``von``."""
        a, b = max(self.a, von), min(self.b, bis)
        pa, pb = self.bei(a), self.bei(b)
        return Strecke(a - von, b - von, pa[0], pb[0], pa[1], pb[1], pa[2], pb[2])


@dataclass(frozen=True)
class Punkt:
    """Eine Last an der Stelle ``a``: Kraefte ``Px``, ``Py`` in N, Moment ``M`` in Nm."""

    a: float
    Px: float = 0.0
    Py: float = 0.0
    M: float = 0.0


Teillast = Union[Strecke, Punkt]


def aufteilen(lasten: Sequence[Teillast], von: float, bis: float,
              *, ende: bool) -> List[Teillast]:
    """
    Die Lasten eines Stabs, die auf ``[von, bis]`` liegen -- in den Achsen
    dieses Stuecks. Eine Einzellast genau auf der Grenze zweier Stuecke
    gehoert dem ersten, dessen Ende sie ist; nur am letzten (``ende``)
    zaehlt auch das Ende des Stabs.
    """
    heraus: List[Teillast] = []
    for last in lasten:
        if isinstance(last, Punkt):
            if von <= last.a < bis or (ende and last.a == bis):
                heraus.append(Punkt(last.a - von, last.Px, last.Py, last.M))
        elif last.b > von and last.a < bis:
            heraus.append(last.ausschnitt(von, bis))
    return heraus


def knotenlasten(L: float, lasten: Sequence[Teillast]) -> List[float]:
    """
    Die arbeitsgleichen Knotenkraefte ``f`` (6) in den Achsen des Stabs --
    ``f_i = ∫ N_i·p + N_i'·m`` und die Einzellasten an ihren Stellen.
    """
    f = [0.0] * 6

    def an(x: float, px: float, py: float, m: float, gewicht: float = 1.0) -> None:
        n1, n2, h1, h2, h3, h4 = formfunktionen(x, L)
        d1, d2, d3, d4 = ableitungen(x, L)
        f[0] += gewicht * n1 * px
        f[3] += gewicht * n2 * px
        f[1] += gewicht * (h1 * py + d1 * m)
        f[2] += gewicht * (h2 * py + d2 * m)
        f[4] += gewicht * (h3 * py + d3 * m)
        f[5] += gewicht * (h4 * py + d4 * m)

    for last in lasten:
        if isinstance(last, Punkt):
            an(last.a, last.Px, last.Py, last.M)
            continue
        halb, mitte = (last.b - last.a) / 2.0, (last.a + last.b) / 2.0
        if halb <= 0.0:
            continue
        for stelle, gewicht in GAUSS3:
            x = mitte + halb * stelle
            an(x, *last.bei(x), gewicht=halb * gewicht)
    return f
