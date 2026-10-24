"""
opencivil/stabwerk/verlauf.py -- Schnittgroessen und Biegelinie laengs eines Stabs.

VERANTWORTUNG:
Aus dem, was :mod:`~opencivil.stabwerk.system` an den Enden jedes Teilstabs
findet -- Kraefte und Verschiebungen --, und aus seinen Lasten die Verlaeufe
dazwischen: Normalkraft, Querkraft, Moment, Laengs- und Querverschiebung.
Dazu die groessten und kleinsten Werte und wo sie liegen.

VORZEICHEN DER BAUSTATIK:
Die Schnittgroessen stehen, wie man sie von Hand rechnet: ``N > 0`` ist Zug;
``M > 0`` zieht an der gestrichelten Faser, der rechten Seite des Stabs vom
Anfang zum Ende gesehen -- bei einem Stab von links nach rechts unten;
``V = dM/dx + m`` (``m`` ein verteiltes Moment im Gegenuhrzeigersinn). Ein
Einfeldtraeger unter Last nach unten hat also ein positives Feldmoment und
links eine positive Querkraft.

Aus den Kraeften ``s`` auf die Enden (in den Achsen des Stabs, y links,
Gegenuhrzeigersinn) folgt am Anfang::

    N(0) = -s_u      V(0) = s_v      M(0) = -s_θ

und mit den Lasten ``p_x``, ``p_y`` und ``m`` laengs des Stabs::

    dN/dx = -p_x     dV/dx = p_y     dM/dx = V - m

Eine Einzelkraft laesst N um ``-P_x`` und V um ``+P_y`` springen, ein
Einzelmoment M um ``-M``.

STUECKWEISE POLYNOME:
Zwischen zwei Laststellen sind die Lasten linear -- also V quadratisch, M
kubisch, die Biegelinie vom fuenften Grad. Gerechnet wird darum genau, mit
Polynomen (:class:`Polynom`), nicht an Stuetzstellen. Ein gebetteter Teilstab
traegt dazu ``-k · v(x)`` mit der kubischen Biegelinie seiner Enden; dort ist
es die Naeherung, mit der auch gerechnet wurde.

Die Biegelinie folgt aus ``v'' = M/EI`` und ``u' = N/EA``, je Teilstab von
seinem Anfang aus -- Verschiebung und Drehung dort sind die der Loesung, am
Ende trifft sie die des Endes (eine Probe in den Tests).

EXTREMWERTE:
Ein Moment ist dort am groessten, wo ``dM/dx = V - m`` null wird, oder an
einer Grenze: einem Stabende, einer Laststelle -- dort auf beiden Seiten.
Gesucht wird an genau diesen Stellen, nicht im Raster der Bilder.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from opencivil.stabwerk import stab as st


class Polynom:
    """``k[0] + k[1]·x + k[2]·x² + …`` -- mit Grad, so hoch es sein muss."""

    __slots__ = ("k",)

    def __init__(self, k: Sequence[float] = (0.0,)) -> None:
        k = list(k) or [0.0]
        while len(k) > 1 and k[-1] == 0.0:
            k.pop()
        self.k: Tuple[float, ...] = tuple(k)

    @classmethod
    def durch(cls, x0: float, y0: float, x1: float, y1: float) -> "Polynom":
        """Die Gerade durch zwei Punkte -- waagrecht, wo sie zusammenfallen."""
        if x1 == x0:
            return cls((y0,))
        m = (y1 - y0) / (x1 - x0)
        return cls((y0 - m * x0, m))

    def __call__(self, x: float) -> float:
        wert = 0.0
        for k in reversed(self.k):
            wert = wert * x + k
        return wert

    def __add__(self, anderes: "Polynom") -> "Polynom":
        n = max(len(self.k), len(anderes.k))
        a = self.k + (0.0,) * (n - len(self.k))
        b = anderes.k + (0.0,) * (n - len(anderes.k))
        return Polynom([p + q for p, q in zip(a, b)])

    def __neg__(self) -> "Polynom":
        return Polynom([-k for k in self.k])

    def __sub__(self, anderes: "Polynom") -> "Polynom":
        return self + (-anderes)

    def __mul__(self, anderes) -> "Polynom":
        if isinstance(anderes, Polynom):
            k = [0.0] * (len(self.k) + len(anderes.k) - 1)
            for i, a in enumerate(self.k):
                for j, b in enumerate(anderes.k):
                    k[i + j] += a * b
            return Polynom(k)
        return Polynom([k * anderes for k in self.k])

    __rmul__ = __mul__

    def stammfunktion(self, ab: float) -> "Polynom":
        """``∫_ab^x p(ξ) dξ`` -- null bei ``x = ab``."""
        k = [0.0] + [c / (i + 1) for i, c in enumerate(self.k)]
        roh = Polynom(k)
        return roh - Polynom((roh(ab),))

    def ableitung(self) -> "Polynom":
        return Polynom([i * c for i, c in enumerate(self.k)][1:] or [0.0])

    def nullstellen(self, a: float, b: float, stellen: int = 48) -> List[float]:
        """Wo es in ``(a, b)`` das Vorzeichen wechselt -- abgetastet und halbiert."""
        if len(self.k) <= 1 or b <= a:
            return []
        heraus = []
        xs = [a + (b - a) * i / stellen for i in range(stellen + 1)]
        ws = [self(x) for x in xs]
        for (x0, w0), (x1, w1) in zip(zip(xs, ws), zip(xs[1:], ws[1:])):
            if w0 == 0.0 and a < x0 < b:
                heraus.append(x0)
            elif w0 * w1 < 0.0:
                lo, hi, wl = x0, x1, w0
                for _ in range(60):
                    mitte = 0.5 * (lo + hi)
                    wm = self(mitte)
                    if wm * wl <= 0.0:
                        hi = mitte
                    else:
                        lo, wl = mitte, wm
                heraus.append(0.5 * (lo + hi))
        return heraus


NULL = Polynom((0.0,))


@dataclass
class Intervall:
    """Ein Stueck eines Stabs ohne Laststelle -- alles darauf Polynome in x ab dem Stabanfang."""

    x0: float
    x1: float
    N: Polynom
    V: Polynom
    M: Polynom
    u: Polynom
    """Laengs, in x des Stabs."""

    v: Polynom
    """Quer, in y des Stabs -- links positiv."""

    theta: Polynom
    p_y: Polynom = field(default_factory=lambda: NULL)
    """Die Querlast samt Bettung -- fuer das, was ins Linienlager geht."""


@dataclass(frozen=True)
class Extrem:
    """Der kleinste und der groesste Wert einer Groesse, je mit Stelle."""

    kleinst: Tuple[float, float]
    groesst: Tuple[float, float]


@dataclass
class Stabverlauf:
    """Ein Stab von Anfang bis Ende -- ueber alle seine Teilstaebe."""

    stab: str
    L: float
    c: float
    s: float
    x_a: float
    z_a: float
    intervalle: List[Intervall] = field(default_factory=list)

    def bei(self, x: float, links: bool = False) -> Dict[str, float]:
        """
        Die Werte an der Stelle ``x`` -- an einer Sprungstelle rechts davon,
        mit ``links`` links davon.
        """
        kandidaten = [i for i in self.intervalle if i.x0 <= x <= i.x1]
        if not kandidaten:
            kandidaten = [min(self.intervalle, key=lambda i: min(abs(i.x0 - x), abs(i.x1 - x)))]
        teil = kandidaten[0] if links else kandidaten[-1]
        return self._werte(teil, x)

    def _werte(self, teil: Intervall, x: float) -> Dict[str, float]:
        u, v = teil.u(x), teil.v(x)
        return {"x": x, "N": teil.N(x), "V": teil.V(x), "M": teil.M(x), "u": u, "v": v,
                "ux": self.c * u - self.s * v, "uz": self.s * u + self.c * v,
                "w": -(v - self.sehne(x)), "phi": teil.theta(x)}

    def sehne(self, x: float) -> float:
        """Die Querverschiebung der Sehne zwischen den Stabenden -- fuer die relative Durchbiegung."""
        va = self.intervalle[0].v(self.intervalle[0].x0)
        vb = self.intervalle[-1].v(self.intervalle[-1].x1)
        return va + (vb - va) * x / self.L

    def proben(self, je_stab: int = 24) -> List[Dict[str, float]]:
        """
        Werte zum Zeichnen: an beiden Seiten jeder Grenze und dazwischen so
        dicht, dass ein Stab rund ``je_stab`` Stuecke hat.
        """
        heraus = []
        for teil in self.intervalle:
            n = max(1, math.ceil(je_stab * (teil.x1 - teil.x0) / self.L))
            for i in range(n + 1):
                heraus.append(self._werte(teil, teil.x0 + (teil.x1 - teil.x0) * i / n))
        for x in self.extremstellen():
            heraus.append(self.bei(x))
        heraus.sort(key=lambda w: w["x"])
        return heraus

    def extremstellen(self) -> List[float]:
        """Wo ein Moment, eine Querkraft oder eine Normalkraft im Innern eines Stuecks extrem ist."""
        stellen = []
        for teil in self.intervalle:
            for p in (teil.M.ableitung(), teil.V.ableitung(), teil.N.ableitung()):
                stellen.extend(p.nullstellen(teil.x0, teil.x1))
        return stellen

    def extrem(self, groesse: str) -> Extrem:
        """
        Kleinster und groesster Wert von ``N``, ``V``, ``M``, ``w`` (der
        Durchbiegung gegen die Sehne) oder ``phi`` (der Verdrehung des
        Querschnitts, im Gegenuhrzeigersinn), mit Stelle.
        """
        werte = []
        neigung = (self.intervalle[-1].v(self.L) - self.intervalle[0].v(0.0)) / self.L
        for teil in self.intervalle:
            if groesse == "w":
                # w ist extrem, wo die Biegelinie so steil ist wie die Sehne.
                stellen = [teil.x0, teil.x1] + (
                    teil.theta - Polynom((neigung,))).nullstellen(teil.x0, teil.x1)
                werte.extend((x, self._werte(teil, x)["w"]) for x in stellen)
                continue
            funktion = teil.theta if groesse == "phi" else getattr(teil, groesse)
            stellen = [teil.x0, teil.x1] + funktion.ableitung().nullstellen(teil.x0, teil.x1)
            werte.extend((x, funktion(x)) for x in stellen)
        return Extrem(kleinst=min(werte, key=lambda w: w[1]),
                      groesst=max(werte, key=lambda w: w[1]))


def verlaeufe(fall) -> Dict[str, Stabverlauf]:
    """Je Stab sein Verlauf in diesem Fall -- aus den Teilstaeben, der Reihe nach."""
    heraus: Dict[str, Stabverlauf] = {}
    for teil in fall.teile:
        t = teil.teil
        verlauf = heraus.get(t.stab.name)
        if verlauf is None:
            verlauf = heraus[t.stab.name] = Stabverlauf(
                stab=t.stab.name, L=t.L_stab, c=t.c, s=t.s,
                x_a=t.a.x - t.c * t.x0, z_a=t.a.z - t.s * t.x0)
        verlauf.intervalle.extend(teilverlauf(teil))
    for verlauf in heraus.values():
        verlauf.intervalle.sort(key=lambda i: (i.x0, i.x1))
    return heraus


def teilverlauf(teil) -> List[Intervall]:
    """
    Die Intervalle eines Teilstabs, in x ab dem Anfang seines Stabs -- aus
    den Kraeften und Verschiebungen seiner Enden und seinen Lasten.
    """
    t = teil.teil
    L, x0 = t.L, t.x0
    s, d = teil.s, teil.d
    strecken = [l for l in teil.lasten if isinstance(l, st.Strecke) and l.b > l.a]
    punkte = [l for l in teil.lasten if isinstance(l, st.Punkt)]
    grenzen = sorted({0.0, L} | {g for l in strecken for g in (l.a, l.b) if 0.0 < g < L}
                     | {p.a for p in punkte if 0.0 < p.a < L})

    # Die Biegelinie der Enden -- fuer die Bettung.
    if t.k_quer:
        hermite = _hermite(L, d[1], d[2], d[4], d[5])
    if t.k_laengs:
        gerade = Polynom.durch(0.0, d[0], L, d[3])

    N0, V0, M0 = -s[0], s[1], -s[2]
    for p in punkte:
        if p.a == 0.0:
            N0, V0, M0 = N0 - p.Px, V0 + p.Py, M0 - p.M
    u0, v0, th0 = d[0], d[1], d[2]
    heraus: List[Intervall] = []
    for xa, xb in zip(grenzen, grenzen[1:]):
        if xb - xa <= 1e-12 * L:
            continue
        px, py, m = NULL, NULL, NULL
        for l in strecken:
            if l.a <= xa and l.b >= xb:
                px = px + Polynom.durch(l.a, l.px_a, l.b, l.px_b)
                py = py + Polynom.durch(l.a, l.py_a, l.b, l.py_b)
                m = m + Polynom.durch(l.a, l.m_a, l.b, l.m_b)
        if t.k_quer:
            py = py + (-t.k_quer) * hermite
        if t.k_laengs:
            px = px + (-t.k_laengs) * gerade
        if not t.laengs:
            px = NULL
        if not t.biegung:
            py, m = NULL, NULL
        N = Polynom((N0,)) - px.stammfunktion(xa)
        V = Polynom((V0,)) + py.stammfunktion(xa)
        M = Polynom((M0,)) + (V - m).stammfunktion(xa)
        if not t.laengs:
            N = NULL
        if not t.biegung:
            V, M = NULL, NULL
        u = Polynom((u0,)) + (N * (1.0 / t.EA)).stammfunktion(xa)
        theta = Polynom((th0,)) + (M * (1.0 / t.EI)).stammfunktion(xa)
        v = Polynom((v0,)) + theta.stammfunktion(xa)
        heraus.append(Intervall(xa, xb, N, V, M, u, v, theta, py))
        N0, V0, M0 = N(xb), V(xb), M(xb)
        u0, v0, th0 = u(xb), v(xb), theta(xb)
        for p in punkte:
            if p.a == xb and xb < L:
                N0, V0, M0 = N0 - p.Px, V0 + p.Py, M0 - p.M
    return [_verschoben(i, x0) for i in heraus]


def _hermite(L: float, v1: float, t1: float, v2: float, t2: float) -> Polynom:
    """Die kubische Biegelinie aus den Enden -- die Form, mit der die Bettung gerechnet wurde."""
    a = Polynom((0.0, 1.0 / L))
    eins = Polynom((1.0,))
    h1 = eins - 3.0 * a * a + 2.0 * a * a * a
    h2 = L * (a - 2.0 * a * a + a * a * a)
    h3 = 3.0 * a * a - 2.0 * a * a * a
    h4 = L * (a * a * a - a * a)
    return v1 * h1 + t1 * h2 + v2 * h3 + t2 * h4


def _verschoben(i: Intervall, um: float) -> Intervall:
    """Dasselbe Intervall in x ab dem Anfang des ganzen Stabs."""
    if not um:
        return i
    return Intervall(i.x0 + um, i.x1 + um, *(_schieben(p, um) for p in
                                             (i.N, i.V, i.M, i.u, i.v, i.theta, i.p_y)))


def _schieben(p: Polynom, um: float) -> Polynom:
    """``q(x) = p(x - um)``."""
    heraus = NULL
    potenz = Polynom((1.0,))
    verschoben = Polynom((-um, 1.0))
    for k in p.k:
        heraus = heraus + k * potenz
        potenz = potenz * verschoben
    return heraus
