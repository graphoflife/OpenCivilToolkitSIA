"""
opencivil/stabwerk/verlauf.py -- Schnittgroessen und Biegelinien laengs eines Stabs, eben und im Raum.

VERANTWORTUNG:
Aus dem, was :mod:`~opencivil.stabwerk.system` an den Enden jedes Teilstabs
findet -- Kraefte und Verschiebungen --, und aus seinen Lasten die Verlaeufe
dazwischen: Normalkraft, Querkraefte, Torsionsmoment, Biegemomente,
Verschiebungen und Verdrehungen. Dazu die groessten und kleinsten Werte und
wo sie liegen.

EIN STAB AUS EBENEN TEILEN:
Ein Stab besteht aus drei ebenen Teilen (:mod:`opencivil.stabwerk3d.stab`):
der Biegung in seiner x-z-Ebene samt Laengskraft, der Biegung in seiner
x-y-Ebene und der Torsion. Jeder Teil rechnet fuer sich
(:func:`ebener_verlauf`), dann werden sie zusammengesetzt. Die drei Teile
springen an denselben Stellen, weil jede Last in allen dreien steht. In der
Ebene sind die beiden letzten null.

VORZEICHEN EINES EBENEN TEILS:
Wie man sie von Hand rechnet: ``N > 0`` ist Zug; ``M > 0`` zieht an der
gestrichelten Faser, der rechten Seite des Teils vom Anfang zum Ende
gesehen; ``V = dM/dx + m`` (``m`` ein verteiltes Moment im
Gegenuhrzeigersinn). Ein Einfeldtraeger unter Last nach unten hat also ein
positives Feldmoment und links eine positive Querkraft.

Aus den Kraeften ``s`` auf die Enden (in den Achsen des Teils, y links,
Gegenuhrzeigersinn) folgt am Anfang::

    N(0) = -s_u      V(0) = s_v      M(0) = -s_θ

und mit den Lasten ``p_x``, ``p_y`` und ``m`` laengs des Stabs::

    dN/dx = -p_x     dV/dx = p_y     dM/dx = V - m

Eine Einzelkraft laesst N um ``-P_x`` und V um ``+P_y`` springen, ein
Einzelmoment M um ``-M``.

VORZEICHEN DES STABS -- M_z NACH VORGABE, NICHT NACHGESCHLAGEN:
In den Achsen des Stabs. ``N > 0`` ist Zug, ``T > 0`` dreht im Rechtssinn
um die nach aussen zeigende Normale des Schnitts. ``M_y > 0`` zieht an der
Faser auf der Seite +z, ``M_z > 0`` an der auf der Seite +y: beide Ebenen
wie die eines ebenen Teils, mit ``V_z = dM_y/dx`` und ``V_y = dM_z/dx``, wo
kein verteiltes Moment liegt. Die Spannung im Querschnitt ist damit
``σ = N/A + M_y·z/I_y + M_z·y/I_z``; die Rechtsschraube gaebe ``M_z`` das
andere Vorzeichen. In der Ebene liegt z auf der gestrichelten Faser: ``N``,
``V_z`` und ``M_y`` sind ``N``, ``V`` und ``M`` von Hand.

Verschiebungen ``u``, ``v``, ``w`` in x, y und z des Stabs, Verdrehungen
``theta_x``, ``theta_y``, ``theta_z`` im Rechtssinn um diese Achsen; dazu
``ux``, ``uy``, ``uz`` in den Achsen des Systems und die Durchbiegungen
``f_y`` und ``f_z`` gegen die Sehne zwischen den Stabenden.

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
Gesucht wird an genau diesen Stellen, nicht im Raster der Bilder. Ueber
alle Staebe eines Falls fasst :func:`grenzwerte` zusammen: den kleinsten,
den groessten und den massgebenden Wert, den mit dem groessten Betrag --
bei gleichem Betrag den positiven. Bericht und Bildschirm zeigen dieselben.
Die groesste Verschiebung ist ebenso genau: ihr Quadrat ``u² + v² + w²``
ist ein Polynom (:meth:`Stabverlauf.groesste_verschiebung`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Mapping, Sequence, Tuple

from opencivil.stabwerk import stab as st
from opencivil.stabwerk3d import stab as st3
from opencivil.stabwerk3d.raum import Vektor, im_system, mal, minus

#: Die Schnittgroessen eines Stabs -- ihre Extremstellen kommen in die Proben.
SCHNITTGROESSEN = ("N", "V_y", "V_z", "T", "M_y", "M_z")

#: Was ein Intervall als Polynom traegt, ausser den Lasten.
POLYNOME = SCHNITTGROESSEN + ("u", "v", "w", "theta_x", "theta_y", "theta_z")

#: In der Ebene heissen die Groessen eines Stabs wie von Hand -- je Zeichen
#: sein Feld im Verlauf: z liegt auf der gestrichelten Faser, y steht
#: senkrecht auf der Ebene.
IN_DER_EBENE = {"N": "N", "V": "V_z", "M": "M_y", "w": "f_z", "phi": "theta_y"}


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
class EbenesIntervall:
    """Ein Stueck eines ebenen Teils ohne Laststelle -- alles darauf Polynome in x ab dem Stabanfang."""

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


@dataclass
class Intervall:
    """Ein Stueck eines Stabs ohne Laststelle -- alles darauf Polynome in x ab dem Stabanfang."""

    x0: float
    x1: float
    N: Polynom
    V_y: Polynom
    V_z: Polynom
    T: Polynom
    M_y: Polynom
    M_z: Polynom
    u: Polynom
    v: Polynom
    w: Polynom
    theta_x: Polynom
    theta_y: Polynom
    theta_z: Polynom
    p_y: Polynom = field(default_factory=lambda: NULL)
    p_z: Polynom = field(default_factory=lambda: NULL)
    """Die Querlast samt Bettung in y und z des Stabs."""


def nach_betrag(wert: float) -> Tuple[float, float]:
    """Wonach der massgebende Wert gewaehlt wird: nach dem Betrag, bei gleichem der positive."""
    return abs(wert), wert


@dataclass(frozen=True)
class Extrem:
    """Der kleinste und der groesste Wert einer Groesse, je mit Stelle: ``(x, Wert)``."""

    kleinst: Tuple[float, float]
    groesst: Tuple[float, float]

    @property
    def massgebend(self) -> Tuple[float, float]:
        """Der der beiden, der massgebend ist (:func:`nach_betrag`)."""
        return max((self.kleinst, self.groesst), key=lambda w: nach_betrag(w[1]))


@dataclass(frozen=True)
class Grenzwert:
    """Ein Wert ueber alle Staebe eines Falls: an welchem Stab, wo darauf und wie gross."""

    stab: str
    x: float
    wert: float


@dataclass(frozen=True)
class Grenzwerte:
    """Der kleinste, der groesste und der massgebende Wert einer Groesse ueber alle Staebe."""

    kleinst: Grenzwert
    groesst: Grenzwert
    massgebend: Grenzwert


def grenzwerte(extreme: Mapping[str, Extrem]) -> Grenzwerte:
    """
    Aus den Extremwerten je Stab die ueber alle: der kleinste, der groesste
    und der massgebende (:attr:`Extrem.massgebend`) -- bei gleichem Wert der
    des ersten Stabs.
    """
    def je_stab(wahl: Callable[[Extrem], Tuple[float, float]]) -> List[Grenzwert]:
        return [Grenzwert(stab, *wahl(e)) for stab, e in extreme.items()]

    return Grenzwerte(
        kleinst=min(je_stab(lambda e: e.kleinst), key=lambda g: g.wert),
        groesst=max(je_stab(lambda e: e.groesst), key=lambda g: g.wert),
        massgebend=max(je_stab(lambda e: e.massgebend), key=lambda g: nach_betrag(g.wert)))


@dataclass
class Stabverlauf:
    """Ein Stab von Anfang bis Ende -- ueber alle seine Teilstaebe."""

    stab: str
    L: float
    anfang: Vektor
    achsen: Tuple[Vektor, Vektor, Vektor]
    intervalle: List[Intervall] = field(default_factory=list)

    def bei(self, x: float, links: bool = False) -> Dict[str, float]:
        """
        Die Werte an der Stelle ``x`` -- an einer Sprungstelle rechts davon,
        mit ``links`` links davon.
        """
        kandidaten = [i for i in self.intervalle if i.x0 <= x <= i.x1]
        if not kandidaten:
            kandidaten = [min(self.intervalle, key=lambda i: min(abs(i.x0 - x), abs(i.x1 - x)))]
        return self._werte(kandidaten[0] if links else kandidaten[-1], x)

    def sehne(self, groesse: str) -> Polynom:
        """Die Gerade zwischen den Werten von ``v`` oder ``w`` an den Stabenden."""
        erstes, letztes = self.intervalle[0], self.intervalle[-1]
        return Polynom.durch(0.0, getattr(erstes, groesse)(0.0),
                             self.L, getattr(letztes, groesse)(self.L))

    def _polynom(self, teil: Intervall, groesse: str) -> Polynom:
        if groesse == "f_y":
            return teil.v - self.sehne("v")
        if groesse == "f_z":
            return teil.w - self.sehne("w")
        return getattr(teil, groesse)

    def _werte(self, teil: Intervall, x: float) -> Dict[str, float]:
        werte = {"x": x}
        for groesse in POLYNOME + ("f_y", "f_z"):
            werte[groesse] = self._polynom(teil, groesse)(x)
        werte["ux"], werte["uy"], werte["uz"] = im_system(
            self.achsen, (werte["u"], werte["v"], werte["w"]))
        return werte

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
        """Wo eine Schnittgroesse im Innern eines Stuecks extrem ist."""
        return [x for teil in self.intervalle for groesse in SCHNITTGROESSEN
                for x in getattr(teil, groesse).ableitung().nullstellen(teil.x0, teil.x1)]

    def extrem(self, groesse: str) -> Extrem:
        """
        Kleinster und groesster Wert einer Groesse mit Stelle: einer
        Schnittgroesse, einer Verschiebung oder Verdrehung oder von ``f_y``
        und ``f_z``, der Durchbiegung gegen die Sehne.
        """
        return self._extrem(lambda teil: self._polynom(teil, groesse))

    def groesste_verschiebung(self) -> Tuple[float, float]:
        """Wo sich der Stab am weitesten verschiebt, und wie weit, in m -- ``(x, Betrag)``."""
        x, quadrat = self._extrem(lambda t: t.u * t.u + t.v * t.v + t.w * t.w).groesst
        return x, math.sqrt(max(quadrat, 0.0))

    def _extrem(self, polynom: Callable[[Intervall], Polynom]) -> Extrem:
        """Kleinster und groesster Wert eines Polynoms je Stueck: an den Grenzen und wo es flach ist."""
        werte = []
        for teil in self.intervalle:
            p = polynom(teil)
            stellen = [teil.x0, teil.x1] + p.ableitung().nullstellen(teil.x0, teil.x1)
            werte.extend((x, p(x)) for x in stellen)
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
                stab=t.stab.name, L=t.L_stab, achsen=t.achsen,
                anfang=minus(t.a.punkt, mal(t.x0, t.achsen[0])))

        def ebene(zuordnung, lasten, **steifigkeit):
            return ebener_verlauf(L=t.L, x0=t.x0, s=st3.eben(teil.s, zuordnung),
                                  d=st3.eben(teil.d, zuordnung), lasten=lasten, **steifigkeit)

        # Die Laengskraft gehoert der Ebene z; die Torsion ist ein Teil ohne
        # Biegung, ihr Torsionsmoment und ihre Verdrehung stehen dort, wo
        # sonst N und u stehen.
        z = ebene(st3.EBENE_Z, teil.lasten.z, EA=t.EA, EI=t.EI_y, k_quer=t.k_z,
                  k_laengs=t.k_x, laengs=t.laengs, biegung=t.biegung_z)
        y = ebene(st3.EBENE_Y, teil.lasten.y, EI=t.EI_z, k_quer=t.k_y,
                  laengs=False, biegung=t.biegung_y)
        drillung = ebene(st3.TORSION, teil.lasten.t, EA=t.GI_T,
                         laengs=t.torsion, biegung=False)
        verlauf.intervalle.extend(_zusammen(*teile) for teile in zip(z, y, drillung))
    for verlauf in heraus.values():
        verlauf.intervalle.sort(key=lambda i: (i.x0, i.x1))
    return heraus


def ebener_verlauf(*, L: float, x0: float, s: Sequence[float], d: Sequence[float],
                   lasten: Sequence[st.Teillast], EA: float = 0.0, EI: float = 0.0,
                   k_quer: float = 0.0, k_laengs: float = 0.0, laengs: bool = True,
                   biegung: bool = True) -> List[EbenesIntervall]:
    """
    Die Intervalle eines ebenen Teils der Laenge ``L``, in x ab dem Anfang
    seines Stabs (``x0``) -- aus den Kraeften ``s`` und Verschiebungen ``d``
    seiner Enden und seinen Lasten. ``EA`` gilt nur, wenn er sich dehnt
    (``laengs``), ``EI`` nur, wenn er sich biegt (``biegung``): sonst bleiben
    ``u`` und ``theta`` die des Anfangs.
    """
    strecken = [l for l in lasten if isinstance(l, st.Strecke) and l.b > l.a]
    punkte = [l for l in lasten if isinstance(l, st.Punkt)]
    grenzen = sorted({0.0, L} | {g for l in strecken for g in (l.a, l.b) if 0.0 < g < L}
                     | {p.a for p in punkte if 0.0 < p.a < L})

    # Die Biegelinie der Enden -- fuer die Bettung.
    if k_quer:
        hermite = _hermite(L, d[1], d[2], d[4], d[5])
    if k_laengs:
        gerade = Polynom.durch(0.0, d[0], L, d[3])

    N0, V0, M0 = -s[0], s[1], -s[2]
    for p in punkte:
        if p.a == 0.0:
            N0, V0, M0 = N0 - p.Px, V0 + p.Py, M0 - p.M
    u0, v0, th0 = d[0], d[1], d[2]
    heraus: List[EbenesIntervall] = []
    for xa, xb in zip(grenzen, grenzen[1:]):
        if xb - xa <= 1e-12 * L:
            continue
        px, py, m = NULL, NULL, NULL
        for l in strecken:
            if l.a <= xa and l.b >= xb:
                px = px + Polynom.durch(l.a, l.px_a, l.b, l.px_b)
                py = py + Polynom.durch(l.a, l.py_a, l.b, l.py_b)
                m = m + Polynom.durch(l.a, l.m_a, l.b, l.m_b)
        if k_quer:
            py = py + (-k_quer) * hermite
        if k_laengs:
            px = px + (-k_laengs) * gerade
        if not laengs:
            px = NULL
        if not biegung:
            py, m = NULL, NULL
        N = Polynom((N0,)) - px.stammfunktion(xa)
        V = Polynom((V0,)) + py.stammfunktion(xa)
        M = Polynom((M0,)) + (V - m).stammfunktion(xa)
        if not laengs:
            N = NULL
        if not biegung:
            V, M = NULL, NULL
        u, theta = Polynom((u0,)), Polynom((th0,))
        if laengs:
            u = u + (N * (1.0 / EA)).stammfunktion(xa)
        if biegung:
            theta = theta + (M * (1.0 / EI)).stammfunktion(xa)
        v = Polynom((v0,)) + theta.stammfunktion(xa)
        heraus.append(EbenesIntervall(xa, xb, N, V, M, u, v, theta, py))
        N0, V0, M0 = N(xb), V(xb), M(xb)
        u0, v0, th0 = u(xb), v(xb), theta(xb)
        for p in punkte:
            if p.a == xb and xb < L:
                N0, V0, M0 = N0 - p.Px, V0 + p.Py, M0 - p.M
    return [_verschoben(i, x0) for i in heraus]


def _zusammen(z: EbenesIntervall, y: EbenesIntervall, t: EbenesIntervall) -> Intervall:
    """Die drei ebenen Teile eines Stuecks als eines -- mit der Zuordnung aus :mod:`~opencivil.stabwerk3d.stab`."""
    return Intervall(z.x0, z.x1, N=z.N, V_y=y.V, V_z=z.V, T=t.N, M_y=z.M, M_z=y.M,
                     u=z.u, v=-y.v, w=-z.v, theta_x=t.u, theta_y=z.theta, theta_z=-y.theta,
                     p_y=-y.p_y, p_z=-z.p_y)


def _hermite(L: float, v1: float, t1: float, v2: float, t2: float) -> Polynom:
    """Die kubische Biegelinie aus den Enden -- die Form, mit der die Bettung gerechnet wurde."""
    a = Polynom((0.0, 1.0 / L))
    eins = Polynom((1.0,))
    h1 = eins - 3.0 * a * a + 2.0 * a * a * a
    h2 = L * (a - 2.0 * a * a + a * a * a)
    h3 = 3.0 * a * a - 2.0 * a * a * a
    h4 = L * (a * a * a - a * a)
    return v1 * h1 + t1 * h2 + v2 * h3 + t2 * h4


def _verschoben(i: EbenesIntervall, um: float) -> EbenesIntervall:
    """Dasselbe Intervall in x ab dem Anfang des ganzen Stabs."""
    if not um:
        return i
    return EbenesIntervall(i.x0 + um, i.x1 + um, *(_schieben(p, um) for p in
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
