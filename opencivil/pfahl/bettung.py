"""
opencivil/pfahl/bettung.py -- der Pfahl als gebetteter Stab.

VERANTWORTUNG:
Löst den Pfahl als Stab auf Federn, längs und quer getrennt:

- längs ein Zug-Druck-Stab mit Federn am Mantel und, wo der Fuss trägt,
  einer am Fuss: die Setzung w(z) und die Normalkraft N(z) (:func:`laengs`);
- quer ein Biegebalken auf einer Bettung: die Verschiebung y(z), die
  Verdrehung, das Moment M(z), die Querkraft V(z) und die Bettungskraft
  (:func:`quer`).

Die Federn je Meter Pfahl kommen als :class:`Strecke` von aussen; was sie
bedeuten, sagt :mod:`.steifigkeit`. Hier wird nur gerechnet.

DAS VERFAHREN:
Finite Elemente mit Knoten an jeder Grenze einer Strecke, dazwischen gleich
lang und höchstens ``schritt``: die Stäbe des Stabwerks, längs mit linearem,
quer mit kubischem Ansatz und konsistent verteilter Bettung
(:func:`opencivil.stabwerk.stab.steifigkeit`, :func:`~opencivil.stabwerk.stab.bettung`).
Quer darf die Bettung über eine Strecke linear wachsen -- so steht die
Abminderung am Terrain genau im Modell, ohne Stufen. Gelöst wird mit dem
Profillöser des Stabwerks (:mod:`opencivil.stabwerk.matrix`). N, M
und V folgen danach aus dem Gleichgewicht der Bettungskräfte, Element für
Element und für den Ansatz genau integriert -- nicht aus der Krümmung eines
Elements, die eine Ordnung ungenauer wäre. Am eingespannten Kopf ist das
Moment die Reaktion, die das Gleichgewicht am freien Fuss schliesst.

VORZEICHEN:
z zählt vom Pfahlkopf nach unten. Längs: w positiv nach unten, N positiv als
Druck. Quer: y in Richtung der Kopfkraft H; das Kopfmoment M_0 dreht wie eine
Kraft H, die über dem Kopf angreift (M_0 = H·e), und die Verdrehung θ wie
diese Kraft -- so verrichten H an y und M_0 an θ Arbeit. Es gilt V = dM/dz,
am Kopf V = H und M = M_0.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from opencivil.stabwerk import stab as st
from opencivil.stabwerk.matrix import Profilmatrix, Zerlegung

#: So lang ist ein Element höchstens, in m.
SCHRITT = 0.1

#: Die Unbekannten eines Elements in der Folge des Stabwerks, mit z als x des
#: Stabs: längs u1, u2 -- quer v1, θ1, v2, θ2, hier y und φ = dy/dz.
LAENGS, QUER = (0, 3), (1, 2, 4, 5)


@dataclass(frozen=True)
class Strecke:
    """
    Ein Stück des Pfahls von ``oben`` bis ``unten`` (m unter dem Kopf).
    ``laengs`` ist die Feder am Mantel je Meter Pfahl (Schubspannung mal
    Umfang je Setzung), gleich über das Stück; ``quer`` die Bettung je Meter
    Pfahl (k_s · D) oben und unten, dazwischen linear -- alle in N/m².
    """

    oben: float
    unten: float
    laengs: float
    quer: Tuple[float, float]

    def quer_bei(self, z: float) -> float:
        """Die Bettung quer in der Tiefe ``z`` des Stücks."""
        oben, unten = self.quer
        return oben + (unten - oben) * (z - self.oben) / (self.unten - self.oben)


@dataclass(frozen=True)
class Laengs:
    """Setzung und Normalkraft je Knoten, dazu die Kraft der Feder am Fuss."""

    z: List[float]
    w: List[float]
    N: List[float]
    fusskraft: float


@dataclass(frozen=True)
class Quer:
    """Verschiebung, Verdrehung, Moment, Querkraft und Bettungskraft je Knoten."""

    z: List[float]
    y: List[float]
    theta: List[float]
    M: List[float]
    V: List[float]
    q: List[float]
    """
    Bettungskraft je Meter Pfahl, N/m: die Bettung mal y -- an der Grenze
    zweier Strecken mit der unteren.
    """


def knoten(strecken: Sequence[Strecke], schritt: float = SCHRITT) -> List[float]:
    """Die Knoten: jede Grenze einer Strecke, dazwischen gleich weit, höchstens ``schritt``."""
    z = [strecken[0].oben]
    for s in strecken:
        n = max(1, math.ceil((s.unten - s.oben) / schritt - 1e-9))
        z += [s.oben + (s.unten - s.oben) * i / n for i in range(1, n + 1)]
    return z


def _strecke_je_element(strecken: Sequence[Strecke], z: Sequence[float]) -> List[Strecke]:
    je = []
    k = 0
    for a, b in zip(z, z[1:]):
        mitte = 0.5 * (a + b)
        while strecken[k].unten < mitte:
            k += 1
        je.append(strecken[k])
    return je


def laengs(strecken: Sequence[Strecke], EA: float, fussfeder: float, N_kopf: float,
           schritt: float = SCHRITT) -> Laengs:
    """
    Der Stab längs unter der Kopfkraft ``N_kopf`` (Druck positiv), mit der
    Feder ``fussfeder`` (N/m) am Fuss -- null, wo der Fuss nicht trägt.
    """
    z = knoten(strecken, schritt)
    je = _strecke_je_element(strecken, z)
    n = len(z)
    K = Profilmatrix.aus_gruppen(n, [(i, i + 1) for i in range(n - 1)])
    for i, s in enumerate(je):
        K.addiere_block((i, i + 1), _element(z[i + 1] - z[i], LAENGS, EA=EA, laengs=s.laengs))
    K.addiere(n - 1, n - 1, fussfeder)
    f = [0.0] * n
    f[0] = N_kopf
    w = _loese(K, f)
    N = [N_kopf]
    for i, s in enumerate(je):
        l = z[i + 1] - z[i]
        N.append(N[-1] - s.laengs * l * 0.5 * (w[i] + w[i + 1]))
    return Laengs(z=z, w=w, N=N, fusskraft=fussfeder * w[-1])


def quer(strecken: Sequence[Strecke], EI: float, H: float, M_0: float, *, eingespannt: bool,
         schritt: float = SCHRITT) -> Quer:
    """
    Der Balken quer unter H und M_0 am Kopf, der Fuss frei. ``eingespannt``:
    der Kopf dreht sich nicht, M_0 zählt dann nicht -- das Moment am Kopf ist
    die Reaktion.
    """
    z = knoten(strecken, schritt)
    # Je Element die Bettung oben und unten.
    k = [(s.quer_bei(a), s.quer_bei(b))
         for s, a, b in zip(_strecke_je_element(strecken, z), z, z[1:])]
    n = len(z)
    # Unbekannte je Knoten: y und φ = dy/dz; am eingespannten Kopf ohne φ.
    nummer: List[Tuple[int, int]] = []
    zaehler = 0
    for i in range(n):
        iy = zaehler
        zaehler += 1
        if i == 0 and eingespannt:
            iphi = -1
        else:
            iphi = zaehler
            zaehler += 1
        nummer.append((iy, iphi))
    gruppen = [[u for u in (*nummer[i], *nummer[i + 1]) if u >= 0] for i in range(n - 1)]
    K = Profilmatrix.aus_gruppen(zaehler, gruppen)
    for i, (oben, unten) in enumerate(k):
        block = _element(z[i + 1] - z[i], QUER, EI=EI, quer=(oben, unten))
        frei = [(p, u) for p, u in enumerate((*nummer[i], *nummer[i + 1])) if u >= 0]
        K.addiere_block([u for _, u in frei], [[block[p][q] for q, _ in frei] for p, _ in frei])
    f = [0.0] * zaehler
    f[nummer[0][0]] = H
    if not eingespannt:
        # M_0 = H·e: die Kraft H in der Höhe e über dem Kopf leistet an φ die
        # Arbeit −H·e.
        f[nummer[0][1]] = -M_0
    x = _loese(K, f)
    y = [x[iy] for iy, _ in nummer]
    phi = [x[iphi] if iphi >= 0 else 0.0 for _, iphi in nummer]
    M, V = _schnittkraefte(z, k, y, phi, H, 0.0 if eingespannt else M_0)
    if eingespannt:
        # Das Moment am Kopf schliesst das Gleichgewicht am freien Fuss.
        M = [m - M[-1] for m in M]
    q = [oben * yi for (oben, _), yi in zip(k, y)] + [k[-1][1] * y[-1]]
    return Quer(z=z, y=y, theta=[-p for p in phi], M=M, V=V, q=q)


def _element(l: float, stellen: Sequence[int], *, EA: float = 0.0, EI: float = 0.0,
             laengs: float = 0.0, quer: Tuple[float, float] = (0.0, 0.0)) -> List[List[float]]:
    """Ein Element der Länge ``l``: Steifigkeit und Bettung des Stabwerks, auf ``stellen``."""
    k = st.summe(st.steifigkeit(l, EA, EI), st.bettung(l, quer, laengs))
    return [[k[i][j] for j in stellen] for i in stellen]


def _schnittkraefte(z: Sequence[float], k: Sequence[Tuple[float, float]], y: Sequence[float],
                    phi: Sequence[float], H: float, M_0: float) -> Tuple[List[float], List[float]]:
    """
    V und M von oben nach unten aus dem Gleichgewicht: je Element die
    Bettungskraft und ihr Moment um das untere Ende, für den kubischen Ansatz
    genau integriert.
    """
    M, V = [M_0], [H]
    for i, (oben, unten) in enumerate(k):
        l = z[i + 1] - z[i]
        y1, p1, y2, p2 = y[i], l * phi[i], y[i + 1], l * phi[i + 1]
        kraft = l / 60.0 * (oben * (21 * y1 + 3 * p1 + 9 * y2 - 2 * p2)
                            + unten * (9 * y1 + 2 * p1 + 21 * y2 - 3 * p2))
        moment = l * l / 60.0 * (oben * (16 * y1 + 2 * p1 + 4 * y2 - p2)
                                 + unten * (5 * y1 + p1 + 5 * y2 - p2))
        M.append(M[-1] + V[-1] * l - moment)
        V.append(V[-1] - kraft)
    return M, V


def _loese(K: Profilmatrix, f: Sequence[float]) -> List[float]:
    zerlegt = Zerlegung(K)
    if zerlegt.singulaer:
        raise ValueError("Der Pfahl ist nicht gehalten: keine Bettung und keine Feder am Fuss.")
    return zerlegt.loese(f)
