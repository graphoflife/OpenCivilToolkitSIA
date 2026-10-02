"""
opencivil/querschnitt/schubwaende.py -- Querkraft und Torsion auf Schubwaende verteilt.

VERANTWORTUNG:
Eine Schubwand ist eine Linie im Querschnitt mit einer Dicke ``b_w`` und
Buegeln. Sie traegt eine Kraft entlang ihrer Achse; ihre Laenge ist der
Hebelarm ``z`` des Fachwerks. Hier wird ``(V_y, V_z, T)`` auf die Waende
verteilt, der Widerstand jeder Wand bestimmt und -- auf Wunsch -- die
Laengszugkraft, die das Druckfeld der Waende im Querschnitt weckt.

DIE VERTEILUNG, ELASTISCH:
Jede Wand wirkt wie eine Feder entlang ihrer Achse, ihre Steifigkeit ist
``k = b_w · l``: dicker und laenger heisst steifer. ``G`` kuerzt sich, solange
alle Waende aus demselben Beton sind.

1. **Querkraft.** Der Querschnitt verschiebt sich um ``u``, jede Wand wehrt
   sich mit ``V_i = k_i · (e_i · u)``. Aus ``Σ V_i · e_i = (V_y, V_z)`` folgt
   ``u`` -- zwei Gleichungen, ``K = Σ k_i · e_i · e_iᵀ``. Zwei gleiche Stege
   eines Kastens tragen so je die Haelfte.
2. **Versatz.** Die Wandkraefte aus 1 haben ein Moment ``ΔT`` um den
   Schwerpunkt -- die Querkraft greift im Schwerpunkt an, ihre Wirkungslinie
   in den Waenden liegt anderswo. Den Rest ``T - ΔT`` tragen die Zellen.
3. **Zellen nach Bredt.** Wo Waende eine geschlossene Flaeche umranden, laeuft
   ein Schubfluss rundum. Je Zelle ein unbekannter Fluss ``q_k``, dazu die
   Verdrillung ``θ`` (mit ``G`` multipliziert)::

       T - ΔT = Σ 2 · A_k · q_k                     Gleichgewicht
       ∮_k q_netto · ds / b_w = 2 · A_k · θ          je Zelle: alle drehen gleich

   In einer Wand zwischen zwei Zellen fliesst die Differenz der beiden.
   Zwei gleiche Kaesten mit gemeinsamer Mittelwand: dort fliesst nichts, und
   aussen ``T / (2 · A_gesamt)``. Ein einzelner Kasten: ``T / (2 · A_k)``.
4. **Ohne Zelle** traegt die Torsion ueber dieselben Federn, nun mit Drehung:
   ``V_i = k_i · (e_i · u + r_i · θ)`` mit dem Hebelarm ``r_i`` der Wand um den
   Schwerpunkt, aus ``(V_y, V_z, T)`` drei Gleichungen. Querkraft und
   Torsion laufen dann gemeinsam durch dieses System.

In jedem Fall gilt: die Wandkraefte ergeben ``V_y`` und ``V_z``, und ihr
Moment um den Schwerpunkt ist ``T``.

WIDERSTAND:
Je Wand das Fachwerk aus :func:`opencivil.nachweis.querkraft.fachwerk`, je
Laenge der Wand::

    v_Rd,s = A_sw/s · f_sd · cot α          v_Rd,c = b_w · k_c · f_cd · sin α · cos α

α ganzgradig zwischen den Grenzen, massgebend das groesste ``min``. Eine Wand,
die zwischen zwei Zellen in Stuecke zerfaellt, traegt je Stueck einen anderen
Fluss; nachgewiesen wird das staerkste Stueck.

VORZEICHEN:
y nach rechts, z nach oben; ``V_y``, ``V_z`` in Achsrichtung; ``T`` im
Gegenuhrzeigersinn. Der Fluss einer Wand zaehlt in ihrer Richtung, vom
Anfangs- zum Endpunkt. Einheiten in SI-Basis.

ANNAHMEN:
Federmodell, Bredt-Verteilung und die Laengszugkraft in der Wandmitte sind
nach Vorgabe eingebaut, nicht nachgeschlagen (TODO.md).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.nachweis.querkraft import beste_neigung, fachwerk
from opencivil.querschnitt.platte import druckfeldgrenzen

Punkt = Tuple[float, float]

#: Wann zwei Punkte im Graphen der Wandachsen derselbe Knoten sind, in Metern.
#: Gezeichnet wird auf Millimeter; ein Tausendstel davon fasst alles
#: Rundungsrauschen und trennt alles, was jemand absichtlich auseinanderlegt.
KNOTEN_TOLERANZ = 1e-6


class WandFehler(ValueError):
    """Eine Last, die die Waende nicht aufnehmen koennen -- mit dem Grund."""


@dataclass(frozen=True)
class Wand:
    """Eine Schubwand: Achse, Dicke, Buegel und die Festigkeiten dazu."""

    name: str
    von: Punkt
    bis: Punkt
    b_w: float
    """Dicke in m."""

    a_sw_s: float
    """Buegelquerschnitt je Laenge in Laengsrichtung, ``n · π⌀²/4 / s``, in m²/m."""

    f_sd: float
    """Fliessgrenze der Buegel in Pa."""

    f_cd: float
    """Druckfestigkeit des Betons der Wand in Pa."""

    k_c: float

    @property
    def laenge(self) -> float:
        return math.hypot(self.bis[0] - self.von[0], self.bis[1] - self.von[1])

    @property
    def richtung(self) -> Punkt:
        l = self.laenge
        return ((self.bis[0] - self.von[0]) / l, (self.bis[1] - self.von[1]) / l)

    @property
    def mitte(self) -> Punkt:
        return ((self.von[0] + self.bis[0]) / 2.0, (self.von[1] + self.bis[1]) / 2.0)

    @property
    def steifigkeit(self) -> float:
        return self.b_w * self.laenge


# ===========================================================================
# Zellen: der Graph der Wandachsen
# ===========================================================================


@dataclass(frozen=True)
class Stueck:
    """Ein Stueck einer Wand zwischen zwei Knoten des Graphen."""

    wand: int
    von: Punkt
    bis: Punkt

    @property
    def laenge(self) -> float:
        return math.hypot(self.bis[0] - self.von[0], self.bis[1] - self.von[1])

    @property
    def mitte(self) -> Punkt:
        return ((self.von[0] + self.bis[0]) / 2.0, (self.von[1] + self.bis[1]) / 2.0)


@dataclass(frozen=True)
class Zelle:
    """Eine geschlossene Flaeche, umrandet von Wandstuecken."""

    flaeche: float
    """``A_k``, umschlossen von den Wandachsen."""

    rand: Tuple[Tuple[int, int], ...]
    """Je Randstueck: (Index, +1 wenn die Zelle es in seiner Richtung umlaeuft)."""


@dataclass(frozen=True)
class Zellenmodell:
    """Die Waende als Graph: ihre Stuecke und die Zellen, die sie bilden."""

    stuecke: Tuple[Stueck, ...]
    zellen: Tuple[Zelle, ...]


def _auf_strecke(p: Punkt, a: Punkt, b: Punkt) -> Optional[float]:
    """Wo ``p`` auf der Strecke ``a``–``b`` liegt (0..1), oder nichts."""
    dy, dz = b[0] - a[0], b[1] - a[1]
    l2 = dy * dy + dz * dz
    t = ((p[0] - a[0]) * dy + (p[1] - a[1]) * dz) / l2
    if t < 0.0 or t > 1.0:
        return None
    naechst = (a[0] + t * dy, a[1] + t * dz)
    if math.hypot(p[0] - naechst[0], p[1] - naechst[1]) > KNOTEN_TOLERANZ:
        return None
    return t


def _kreuzung(a1: Punkt, a2: Punkt, b1: Punkt, b2: Punkt) -> Optional[Tuple[float, float]]:
    """Wo sich zwei Strecken im Innern beider kreuzen -- als Anteile auf beiden."""
    r = (a2[0] - a1[0], a2[1] - a1[1])
    s = (b2[0] - b1[0], b2[1] - b1[1])
    nenner = r[0] * s[1] - r[1] * s[0]
    if abs(nenner) < 1e-18:
        return None
    q = (b1[0] - a1[0], b1[1] - a1[1])
    t = (q[0] * s[1] - q[1] * s[0]) / nenner
    u = (q[0] * r[1] - q[1] * r[0]) / nenner
    if 1e-9 < t < 1 - 1e-9 and 1e-9 < u < 1 - 1e-9:
        return t, u
    return None


def zellen(waende: Sequence[Wand]) -> Zellenmodell:
    """
    Die Wandachsen als ebener Graph, und die Zellen darin.

    Knoten sind die Wandenden, die Stellen, an denen eine Wand auf einer
    anderen endet, und Kreuzungen. Dazwischen liegen die Stuecke. Ein Stueck,
    das zu keinem Kreis gehoert -- eine freie Wand, eine Bruecke zwischen zwei
    Kaesten --, gehoert zu keiner Zelle. Die Zellen sind die beschraenkten
    Flaechen des Graphen; gefunden, indem jeder Rand so umlaufen wird, dass die
    Flaeche links liegt.
    """
    # -- Stuecke: jede Wand an allen Knoten auf ihr geteilt -----------------
    teilungen: List[List[float]] = [[0.0, 1.0] for _ in waende]
    for i, w in enumerate(waende):
        for j, v in enumerate(waende):
            if i == j:
                continue
            for p in (v.von, v.bis):
                t = _auf_strecke(p, w.von, w.bis)
                if t is not None:
                    teilungen[i].append(t)
            if i < j:
                k = _kreuzung(w.von, w.bis, v.von, v.bis)
                if k is not None:
                    teilungen[i].append(k[0])
                    teilungen[j].append(k[1])
    stuecke: List[Stueck] = []
    for i, w in enumerate(waende):
        ts = sorted(set(round(t, 12) for t in teilungen[i]))
        punkte = [(w.von[0] + t * (w.bis[0] - w.von[0]),
                   w.von[1] + t * (w.bis[1] - w.von[1])) for t in ts]
        for a, b in zip(punkte, punkte[1:]):
            if math.hypot(b[0] - a[0], b[1] - a[1]) > KNOTEN_TOLERANZ:
                stuecke.append(Stueck(wand=i, von=a, bis=b))

    # -- Knoten zusammenfassen ----------------------------------------------
    knoten: List[Punkt] = []

    def knoten_von(p: Punkt) -> int:
        for k, q in enumerate(knoten):
            if math.hypot(p[0] - q[0], p[1] - q[1]) <= KNOTEN_TOLERANZ:
                return k
        knoten.append(p)
        return len(knoten) - 1

    kanten = [(knoten_von(s.von), knoten_von(s.bis)) for s in stuecke]

    # -- Bruecken entfernen: Kanten auf keinem Kreis (Tarjan) ---------------
    nachbarn: Dict[int, List[Tuple[int, int]]] = {}
    for e, (a, b) in enumerate(kanten):
        if a == b:
            continue
        nachbarn.setdefault(a, []).append((b, e))
        nachbarn.setdefault(b, []).append((a, e))
    bruecken = set()
    zeit = [0]
    ankunft: Dict[int, int] = {}
    tiefst: Dict[int, int] = {}

    def besuche(start: int) -> None:
        # Ohne Rekursion, damit grosse Zeichnungen keine Tiefe sprengen.
        ankunft[start] = tiefst[start] = zeit[0]
        zeit[0] += 1
        stapel = [(start, -1, iter(nachbarn.get(start, [])))]
        while stapel:
            u, ueber, weiter = stapel[-1]
            for v, e in weiter:
                if e == ueber:
                    continue
                if v not in ankunft:
                    ankunft[v] = tiefst[v] = zeit[0]
                    zeit[0] += 1
                    stapel.append((v, e, iter(nachbarn.get(v, []))))
                    break
                tiefst[u] = min(tiefst[u], ankunft[v])
            else:
                stapel.pop()
                if stapel:
                    eltern = stapel[-1][0]
                    tiefst[eltern] = min(tiefst[eltern], tiefst[u])
                    if tiefst[u] > ankunft[eltern]:
                        bruecken.add(ueber)

    for k in nachbarn:
        if k not in ankunft:
            besuche(k)

    # -- Flaechen umlaufen: an jedem Knoten die schaerfste Linkskurve ---------
    aus: Dict[int, List[Tuple[float, int, int, int]]] = {}
    for e, (a, b) in enumerate(kanten):
        if e in bruecken or a == b:
            continue
        for von, nach, richtung in ((a, b, +1), (b, a, -1)):
            winkel = math.atan2(knoten[nach][1] - knoten[von][1],
                                knoten[nach][0] - knoten[von][0])
            aus.setdefault(von, []).append((winkel, nach, e, richtung))
    for liste in aus.values():
        liste.sort()

    benutzt = set()
    gefunden: List[Zelle] = []
    for start in aus:
        for _, nach0, e0, r0 in aus[start]:
            if (e0, r0) in benutzt:
                continue
            rand: List[Tuple[int, int]] = []
            punkte: List[Punkt] = []
            von, nach, e, r = start, nach0, e0, r0
            while (e, r) not in benutzt:
                benutzt.add((e, r))
                rand.append((e, r))
                punkte.append(knoten[von])
                # Am Knoten «nach»: die Kante zurueck suchen, dann die naechste
                # im Uhrzeigersinn -- das ist die schaerfste Linkskurve.
                liste = aus[nach]
                zurueck = next(i for i, (_, z, ee, _) in enumerate(liste)
                               if ee == e and z == von)
                _, weiter, e, r = liste[zurueck - 1]
                von, nach = nach, weiter
            flaeche = 0.0
            for i in range(len(punkte)):
                y1, z1 = punkte[i]
                y2, z2 = punkte[(i + 1) % len(punkte)]
                flaeche += y1 * z2 - y2 * z1
            flaeche /= 2.0
            if flaeche > KNOTEN_TOLERANZ ** 2:
                gefunden.append(Zelle(flaeche=flaeche, rand=tuple(rand)))
    return Zellenmodell(stuecke=tuple(stuecke), zellen=tuple(gefunden))


# ===========================================================================
# Lineare Gleichungen -- wenige Unbekannte, ohne fremde Pakete
# ===========================================================================


def _loese(matrix: List[List[float]], rechts: List[float]) -> List[float]:
    """
    Gauss mit Spaltenpivot; regularisiert nur, wo es noetig ist.

    Eine Wandanordnung, die eine Richtung gar nicht steift -- nur parallele
    Waende --, gibt eine singulaere Matrix. Dann macht ein Hauch auf der
    Diagonale daraus die Loesung kleinster Laenge; ob sie die Last wirklich
    traegt, prueft der Aufrufer an der Probe. Sonst bleibt die Matrix, wie
    sie ist -- der Hauch verschoebe auch eine eindeutige Loesung.
    """
    x = _gauss(matrix, rechts)
    if x is not None:
        return x
    n = len(rechts)
    spur = sum(abs(matrix[i][i]) for i in range(n)) or 1.0
    gestuetzt = [[matrix[i][j] + (1e-12 * spur if i == j else 0.0) for j in range(n)]
                 for i in range(n)]
    return _gauss(gestuetzt, rechts, singulaer_erlaubt=True)


def _gauss(matrix: List[List[float]], rechts: List[float], *,
           singulaer_erlaubt: bool = False) -> Optional[List[float]]:
    """Gauss mit Spaltenpivot. ``None``, wenn ein Pivot verschwindet."""
    n = len(rechts)
    massstab = max((abs(x) for zeile in matrix for x in zeile), default=0.0) or 1.0
    a = [list(zeile) + [b] for zeile, b in zip(matrix, rechts)]
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(a[i][k]))
        a[k], a[p] = a[p], a[k]
        if abs(a[k][k]) <= 1e-12 * massstab:
            if not singulaer_erlaubt:
                return None
            continue
        for i in range(k + 1, n):
            f = a[i][k] / a[k][k]
            for j in range(k, n + 1):
                a[i][j] -= f * a[k][j]
    x = [0.0] * n
    for i in reversed(range(n)):
        s = a[i][n] - sum(a[i][j] * x[j] for j in range(i + 1, n))
        x[i] = s / a[i][i] if abs(a[i][i]) > 1e-12 * massstab else 0.0
    return x


# ===========================================================================
# Verteilung
# ===========================================================================


@dataclass(frozen=True)
class Verteilung:
    """Wie ``(V_y, V_z, T)`` auf die Waende faellt."""

    aus_querkraft: Tuple[float, ...]
    """Je Wand die Kraft entlang ihrer Achse aus der Verschiebung, in N."""

    fluss: Tuple[float, ...]
    """Je Stueck der Schubfluss entlang seiner Wand, in N/m -- alles zusammen."""

    versatz: float
    """``ΔT``: das Moment der Querkraftanteile um den Schwerpunkt, in Nm."""

    zellenfluss: Tuple[float, ...]
    """Je Zelle ihr Umlauf-Schubfluss ``q_k``, in N/m."""

    mit_drehung: bool
    """Ob die Torsion ueber die Federn lief (keine Zelle)."""


def _hebel(w: Wand, bezug: Punkt) -> float:
    """Moment einer Einheitskraft entlang der Wand um den Bezugspunkt."""
    e = w.richtung
    p = w.mitte
    return (p[0] - bezug[0]) * e[1] - (p[1] - bezug[1]) * e[0]


def verteilen(
    waende: Sequence[Wand], modell: Zellenmodell, *, V_y: float, V_z: float,
    T: float, bezug: Punkt,
) -> Verteilung:
    """
    ``(V_y, V_z, T)`` auf die Waende, nach dem Modell im Kopf dieser Datei.

    Wirft :class:`WandFehler`, wenn die Waende eine Komponente nicht tragen
    koennen -- etwa V_y bei lauter senkrechten Waenden, oder Torsion bei einer
    einzigen Wand.
    """
    if not waende:
        raise WandFehler("Es gibt keine Schubwand.")
    if modell.zellen:
        kraefte = _verschieben(waende, V_y, V_z)
        versatz = sum(V * _hebel(w, bezug) for V, w in zip(kraefte, waende))
        zellenfluss = _bredt(waende, modell, T - versatz)
        mit_drehung = False
    else:
        kraefte = _verschieben_und_drehen(waende, V_y, V_z, T, bezug)
        versatz = sum(V * _hebel(w, bezug) for V, w in zip(kraefte, waende))
        zellenfluss = ()
        mit_drehung = True

    fluss = []
    for i, s in enumerate(modell.stuecke):
        q = kraefte[s.wand] / waende[s.wand].laenge
        for k, zelle in enumerate(modell.zellen):
            for e, r in zelle.rand:
                if e == i:
                    q += r * zellenfluss[k]
        fluss.append(q)
    return Verteilung(aus_querkraft=tuple(kraefte), fluss=tuple(fluss),
                      versatz=versatz, zellenfluss=tuple(zellenfluss),
                      mit_drehung=mit_drehung)


def _pruefen(soll: Sequence[float], ist: Sequence[float], was: str) -> None:
    massstab = max(1.0, max(abs(x) for x in soll))
    for s, i in zip(soll, ist):
        if abs(s - i) > 1e-6 * massstab:
            raise WandFehler(was)


def _verschieben(waende: Sequence[Wand], V_y: float, V_z: float) -> List[float]:
    """Die Querkraft ueber eine reine Verschiebung: ``K·u = V``."""
    K = [[0.0, 0.0], [0.0, 0.0]]
    for w in waende:
        e, k = w.richtung, w.steifigkeit
        for a in range(2):
            for b in range(2):
                K[a][b] += k * e[a] * e[b]
    u = _loese(K, [V_y, V_z])
    kraefte = [w.steifigkeit * (w.richtung[0] * u[0] + w.richtung[1] * u[1])
               for w in waende]
    _pruefen((V_y, V_z),
             (sum(V * w.richtung[0] for V, w in zip(kraefte, waende)),
              sum(V * w.richtung[1] for V, w in zip(kraefte, waende))),
             "Die Querkraft quer zu allen Schubwänden kann keine Wand "
             "aufnehmen. Eine Wand in dieser Richtung zeichnen.")
    return kraefte


def _verschieben_und_drehen(waende: Sequence[Wand], V_y: float, V_z: float,
                            T: float, bezug: Punkt) -> List[float]:
    """Querkraft und Torsion ueber Verschiebung und Drehung: drei Gleichungen."""
    K = [[0.0] * 3 for _ in range(3)]
    for w in waende:
        g = (w.richtung[0], w.richtung[1], _hebel(w, bezug))
        for a in range(3):
            for b in range(3):
                K[a][b] += w.steifigkeit * g[a] * g[b]
    x = _loese(K, [V_y, V_z, T])
    kraefte = [w.steifigkeit * (w.richtung[0] * x[0] + w.richtung[1] * x[1]
                                + _hebel(w, bezug) * x[2]) for w in waende]
    ist = (sum(V * w.richtung[0] for V, w in zip(kraefte, waende)),
           sum(V * w.richtung[1] for V, w in zip(kraefte, waende)),
           sum(V * _hebel(w, bezug) for V, w in zip(kraefte, waende)))
    _pruefen((V_y, V_z), ist[:2],
             "Die Querkraft quer zu allen Schubwänden kann keine Wand "
             "aufnehmen. Eine Wand in dieser Richtung zeichnen.")
    _pruefen((T,), ist[2:],
             "Die Torsion braucht Schubwände, die eine Zelle umschliessen, "
             "oder mindestens drei Wände, die sich nicht in einem Punkt treffen.")
    return kraefte


def _bredt(waende: Sequence[Wand], modell: Zellenmodell, T: float) -> List[float]:
    """
    Die Umlauf-Schubfluesse der Zellen: Gleichgewicht und gleiche Verdrillung.

    Unbekannt sind ``q_0 … q_(n-1)`` und ``θ``. Je Zelle::

        Σ_Rand (l/b_w) · (q_k - q_Nachbar) - 2·A_k·θ = 0

    und dazu ``Σ 2·A_k·q_k = T``.
    """
    n = len(modell.zellen)
    seite: Dict[Tuple[int, int], int] = {}
    for k, zelle in enumerate(modell.zellen):
        for e, r in zelle.rand:
            seite[(e, r)] = k
    A = [[0.0] * (n + 1) for _ in range(n + 1)]
    for k, zelle in enumerate(modell.zellen):
        for e, r in zelle.rand:
            s = modell.stuecke[e]
            nachgiebig = s.laenge / waende[s.wand].b_w
            A[k][k] += nachgiebig
            nachbar = seite.get((e, -r))
            if nachbar is not None:
                A[k][nachbar] -= nachgiebig
        A[k][n] = -2.0 * zelle.flaeche
        A[n][k] = 2.0 * zelle.flaeche
    rechts = [0.0] * n + [T]
    return _loese(A, rechts)[:n]


# ===========================================================================
# Widerstand und Laengszugkraft
# ===========================================================================


@dataclass(frozen=True)
class Wandwiderstand:
    """Was eine Wand je Laenge aufnimmt, bei der guenstigsten Neigung."""

    alpha: int
    v_Rd_s: float
    """Buegel, in N/m Wandlaenge."""

    v_Rd_c: float
    """Druckdiagonale, in N/m Wandlaenge."""

    @property
    def v_Rd(self) -> float:
        return min(self.v_Rd_s, self.v_Rd_c)


def widerstand(w: Wand, *, alpha_min: int, alpha_max: int,
               zugkraft: bool) -> Wandwiderstand:
    """
    Der Widerstand einer Wand je Laenge: das Fachwerk mit dem Hebelarm eins,
    ganzgradig ueber α, massgebend das groesste ``min(v_Rd,s; v_Rd,c)``. Bei
    Normalzug gelten die gehobenen Grenzen der Platte.
    """
    von, bis = druckfeldgrenzen(alpha_min, alpha_max, zugkraft)
    punkte = [fachwerk(alpha=a, a_sw_s=w.a_sw_s, z=1.0, b_w=w.b_w,
                       f_yd=w.f_sd, f_cd=w.f_cd, k_c=w.k_c)
              for a in range(von, bis + 1)]
    beste = beste_neigung(punkte)
    return Wandwiderstand(alpha=beste.alpha, v_Rd_s=beste.V_Rd_s, v_Rd_c=beste.V_Rd_c)


@dataclass(frozen=True)
class Laengszug:
    """Die Zugkraft, die das Druckfeld der Waende in Laengsrichtung braucht."""

    N: float
    M_y: float
    M_z: float


def laengszug(modell: Zellenmodell, verteilung: Verteilung,
              neigungen: Sequence[int], bezug: Punkt) -> Laengszug:
    """
    ``ΔN = Σ |q|·l·cot α`` ueber alle Wandstuecke, je Stueck in seiner Mitte.

    Das Druckfeld einer Wand mit dem Fluss q braucht je Laenge den Zug
    ``q · cot α``, gleichmaessig ueber die Wand verteilt; seine Resultierende
    liegt in der Mitte -- dasselbe wie ``V · cot α / 2`` in jedem Gurt. Liegen
    die Mitten nicht im Schwerpunkt, gibt das auch Momente::

        ΔM_y = -Σ ΔN_i · (z_i - z_S)        ΔM_z = -Σ ΔN_i · (y_i - y_S)

    ``neigungen`` ist je Wand das α, das ihr Nachweis waehlt.
    """
    N = M_y = M_z = 0.0
    for s, q in zip(modell.stuecke, verteilung.fluss):
        kraft = abs(q) * s.laenge / math.tan(math.radians(neigungen[s.wand]))
        mitte = s.mitte
        N += kraft
        M_y -= kraft * (mitte[1] - bezug[1])
        M_z -= kraft * (mitte[0] - bezug[0])
    return Laengszug(N=N, M_y=M_y, M_z=M_z)
