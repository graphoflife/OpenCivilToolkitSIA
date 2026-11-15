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
lang und höchstens ``schritt`` (:func:`elementlaenge`,
:func:`~opencivil.stabwerk.stab.stuecke`):
die Stäbe des Stabwerks, längs mit linearem, quer mit kubischem Ansatz und
konsistent verteilter Bettung (:func:`opencivil.stabwerk.stab.steifigkeit`,
:func:`~opencivil.stabwerk.stab.bettung`). Quer darf die Bettung über eine
Strecke linear wachsen -- so steht die Abminderung am Terrain genau im
Modell, ohne Stufen. Gelöst wird mit dem Profillöser des Stabwerks
(:mod:`opencivil.stabwerk.matrix`). N, M und V folgen danach je Element aus
den Kräften an seinen Enden und der Bettung dazwischen, für den Ansatz genau
integriert -- wie im Balkensystem (:func:`~opencivil.stabwerk.verlauf.ebener_verlauf`),
nicht aus der Krümmung eines Elements, die eine Ordnung ungenauer wäre. Am
eingespannten Kopf ist das Moment die Kraft auf das oberste Element: die
Reaktion.

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

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from opencivil.stabwerk import stab as st
from opencivil.stabwerk.matrix import Profilmatrix, Zerlegung
from opencivil.stabwerk.verlauf import EbenesIntervall, ebener_verlauf

#: So lang ist ein Element höchstens, in m -- so dicht lesen die Nachweise
#: die Verläufe, in jeder Tiefe. Wo die Bettung steif ist, sind die Elemente
#: kürzer (:func:`elementlaenge`).
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
        n = st.stuecke(s.unten - s.oben, schritt)
        z += [s.oben + (s.unten - s.oben) * i / n for i in range(1, n + 1)]
    return z


def elementlaenge(strecken: Sequence[Strecke], EA: float, EI: float) -> float:
    """
    Wie lang ein Element höchstens ist: :data:`SCHRITT`, und so kurz, wie es
    der gebettete Stab für die steifste Bettung längs oder quer verlangt
    (:func:`~opencivil.stabwerk.stab.schritt`) -- dieselbe Regel wie im
    Balkensystem.
    """
    beta = max(max(st.abklingen_quer(max(s.quer), EI), st.abklingen_laengs(s.laengs, EA))
               for s in strecken)
    return st.schritt(beta, SCHRITT)


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
    elemente = [_element(b - a, EA=EA, laengs=s.laengs) for s, a, b in zip(je, z, z[1:])]
    K = Profilmatrix.aus_gruppen(n, [(i, i + 1) for i in range(n - 1)])
    for i, k in enumerate(elemente):
        K.addiere_block((i, i + 1), _auf(k, LAENGS))
    K.addiere(n - 1, n - 1, fussfeder)
    f = [0.0] * n
    f[0] = N_kopf
    w = _loese(K, f)
    teile = [_verlauf(z[i + 1] - z[i], k, (w[i], 0.0, 0.0, w[i + 1], 0.0, 0.0), EA=EA,
                      k_laengs=s.laengs, biegung=False)
             for i, (s, k) in enumerate(zip(je, elemente))]
    # Das Stabwerk zählt Zug positiv, der Pfahl Druck.
    N = [-teile[0].N(0.0)] + [-t.N(t.x1) for t in teile]
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
    elemente = [_element(b - a, EI=EI, quer=kk) for kk, a, b in zip(k, z, z[1:])]
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
    for i, element in enumerate(elemente):
        block = _auf(element, QUER)
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
    teile = [_verlauf(z[i + 1] - z[i], element, (0.0, y[i], phi[i], 0.0, y[i + 1], phi[i + 1]),
                      EI=EI, k_quer=k[i], laengs=False)
             for i, element in enumerate(elemente)]
    M = [teile[0].M(0.0)] + [t.M(t.x1) for t in teile]
    V = [teile[0].V(0.0)] + [t.V(t.x1) for t in teile]
    q = [oben * yi for (oben, _), yi in zip(k, y)] + [k[-1][1] * y[-1]]
    return Quer(z=z, y=y, theta=[-p for p in phi], M=M, V=V, q=q)


def _element(l: float, *, EA: float = 0.0, EI: float = 0.0, laengs: float = 0.0,
             quer: Tuple[float, float] = (0.0, 0.0)) -> st.Matrix:
    """Ein Element der Länge ``l``: Steifigkeit und Bettung des Stabwerks, 6 × 6."""
    return st.summe(st.steifigkeit(l, EA, EI), st.bettung(l, quer, laengs))


def _auf(k: st.Matrix, stellen: Sequence[int]) -> List[List[float]]:
    """Ein Element, nur auf den Unbekannten ``stellen``."""
    return [[k[i][j] for j in stellen] for i in stellen]


def _verlauf(l: float, k: st.Matrix, d: Sequence[float], **verlauf) -> EbenesIntervall:
    """
    Ein Element der Länge ``l`` mit der Matrix ``k`` als Teil eines Stabs, in
    x ab seinem oberen Ende: aus den Kräften an seinen Enden -- ``k · d``,
    eine Last trägt es nicht -- und seiner Bettung
    (:func:`~opencivil.stabwerk.verlauf.ebener_verlauf`). y des Pfahls ist v
    des Stabs, φ = dy/dz seine Drehung.
    """
    (teil,) = ebener_verlauf(L=l, x0=0.0, s=st.mal(k, d), d=d, lasten=(), **verlauf)
    return teil


def _loese(K: Profilmatrix, f: Sequence[float]) -> List[float]:
    zerlegt = Zerlegung(K)
    if zerlegt.singulaer:
        raise ValueError("Der Pfahl ist nicht gehalten: keine Bettung und keine Feder am Fuss.")
    return zerlegt.loese(f)
