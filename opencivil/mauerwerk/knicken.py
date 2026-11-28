"""
opencivil/mauerwerk/knicken.py -- ein Pfeiler unter Normalkraft nach Theorie 2. Ordnung.

VERANTWORTUNG:
Der Beiwert k_N eines Pfeilers (SIA 266:2015, 4.3.1.3, Gl. (11)): die
grösste Normalkraft, bezogen auf l_w · t_w · f_xd, unter der die verformte
Wand im Gleichgewicht steht (4.3.1.1) und ihre Ausmitte nirgends die Grenze
der Figur 4 überschreitet (:func:`k_N`). Dazu der Zustand unter der
Normalkraft der Bemessung: wie weit die Wand ausweicht und wo. Und unter
einer festen Normalkraft die grösste Querlast, die die Wand so trägt -- das
lotrechte Druckgewölbe (4.3.4.2, Figur 11, :func:`querlast`).

DAS MODELL:
Ein Streifen der Wand von Fuss bis Kopf, beide waagrecht gehalten (4.3), die
Normalkraft über die ganze Höhe gleich. Gelenkig gehalten greift sie dort mit
ihrer Ausmitte an; eingespannt dreht sich die Wand dort nicht, und die
Ausmitte ergibt sich -- wie in den Fällen der Tabelle 9 und des Anhangs A.
Die Ausmitte in der Höhe x ist e(x) = e_u + (e_o − e_u) · x/h + w(x), w die
Auslenkung der Wand. Ihre Krümmung -w'' folgt aus der Ausmitte nach Figur 3:

    χ · h_Ed² / t = 4.1 · tan(2.4 e/t) · [1 + tan²(2.4 e/t)],
    h_Ed = π √(B_yd / N_xd)                      (Figur 19)

bis e = 0.375 t; dort ist das Moment am Ende (Figur 3), und mehr Ausmitte
lässt Figur 4 nicht zu: höchstens 0.375 t und nach Gl. (6) höchstens
(1 − N_xd/(l_w t_w f_xd)) · t/2.

Eine Querlast q, gleichmässig über die Höhe, gibt dazu das Moment eines
einfachen Balkens, q · x · (h − x)/2 je Meter, also die Ausmitte
q · x · (h − x)/(2 N) je Meter Wand. Ein eingespannter Rand nimmt sein
Moment wie ohne Querlast über seine Ausmitte auf, die das Gleichgewicht
bestimmt.

B_yd = E_xd · I_y, wie in Gl. (8) -- nach Vorgabe, nicht nachgeschlagen:
4.3.1.3 nennt B_yd, ohne es festzulegen. So sind auch die Kurven der Figur 5
gerechnet: die Rechnung hier trifft sie bis e/t = 0.30 auf etwa 0.006
(tests/test_mauerwerk_nachweise.py), mit dem Faktor √(1 − N/(2 A f)) der
Figur 3 lägen sie bis 20 % tiefer. Die Kurve e/t = 0.35 der Figur 5 liegt
dagegen fast doppelt so hoch, wie Figur 3 und 4 es zulassen; die Kurven der
Figur 19 stimmen mit beiden überein. Gerechnet wird nach Figur 3 und 4.

GERECHNET WIRD IN TEILEN DER DICKE:
Alle Längen durch t_w, die Normalkraft als n = N/(l_w t_w f_xd). Dann hängt
alles nur noch an h_w/t_w, den Ausmitten in t_w und E_xd/f_xd, für
Standardmauerwerk 1000 (4.2.1.4) -- k_N ist für jeden Pfeiler derselbe
Beiwert, wie breit er auch ist. Die Querlast heisst dort
λ = q · h_w²/(t_w² · f_xd), q je m² Wand; ihre Ausmitte in Dicken ist
λ · ξ · (1 − ξ)/(2 n), ξ = x/h_w.

DIE SUCHE (nach Vorgabe, nicht nachgeschlagen):
Die Wand in :data:`TEILE` Stücke geteilt, je Knoten das Gleichgewicht w'' =
−χ(e) als finite Differenz, gelöst nach Newton. n wächst in Schritten, jedes
Gleichgewicht vom vorigen aus. Eine Stufe gilt, wenn das Gleichgewicht
besteht, nicht gekippt ist -- die Determinante der Ableitung behält das
Vorzeichen, das sie bei kleiner Last hat -- und die Ausmitte nirgends über
der Grenze liegt. Hält eine Stufe nicht, wird der Schritt halbiert, bis er
kleiner ist als :data:`GENAU`. Erreicht die Ausmitte 0.375 t, endet die
Rechnung dort: ein Gelenk, das sich bei kleiner Normalkraft weiter drehen
dürfte (4.3.1.1), zählt sie nicht -- auf der sicheren Seite.

Die Querlast sucht :func:`querlast` ebenso: erst die Normalkraft bis n wie
bei k_N, dann wächst λ in Schritten, die sich halbieren, bis die Wand kein
Gleichgewicht mehr findet oder ihre Ausmitte die Grenze erreicht. Die
Schritte messen sich an λ_1 = 8 · n · Grenze(n), der Querlast, die eine
mittig belastete, gelenkig gehaltene Wand nach Theorie 1. Ordnung trägt.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional, Sequence, Tuple

#: In so viele gleiche Stücke ist die Höhe geteilt.
TEILE = 40

#: Die grösste Ausmitte in Teilen der Dicke: dort ist das Moment am Ende (Figur 3, Figur 4).
PLATEAU = 0.375

#: Bis zu dieser Ausmitte gilt die Formel der Figur 3 in der Rechnung -- darüber
#: bricht ein Schritt ab, statt dem Tangens nahe π/2 zu folgen.
FORMELGRENZE = 0.6

#: Der erste Schritt in n, und wie genau k_N am Ende ist.
SCHRITT = 0.02
GENAU = 2e-5

#: Der erste Schritt der Querlast und wie genau sie am Ende ist, beide in λ_1;
#: weiter als bis zum Vielfachen :data:`QUER_HOECHSTENS` sucht sie nicht.
QUER_SCHRITT = 0.1
QUER_GENAU = 1e-4
QUER_HOECHSTENS = 20.0

#: Wo die Regeln stehen.
REFERENZ_FIGUR_3 = "SIA 266:2015, 4.3.1.1, Figur 3"
REFERENZ_GRENZE = "SIA 266:2015, 4.3.1.1, Gl. (6), Figur 4"
REFERENZ_K_N = "SIA 266:2015, 4.3.1.3, Gl. (11)"
REFERENZ_GEWOELBE = "SIA 266:2015, 4.3.4.2, Figur 11"


def g(u: float) -> float:
    """χ · h_Ed²/t zu einer Ausmitte von ``u`` Dicken -- Figur 3, ungerade fortgesetzt."""
    a = math.tan(2.4 * abs(u))
    return math.copysign(4.1 * a * (1.0 + a * a), u)


def _dg(u: float) -> float:
    """Die Ableitung von :func:`g` nach u."""
    a = math.tan(2.4 * abs(u))
    return 4.1 * 2.4 * (1.0 + a * a) * (1.0 + 3.0 * a * a)


def grenze(n: float) -> float:
    """Die grösste Ausmitte in Dicken unter n: Figur 4 0.375, Gl. (6) höchstens (1 − n)/2."""
    return min(PLATEAU, (1.0 - n) / 2.0)


@dataclass(frozen=True)
class Zustand:
    """Ein Gleichgewicht der Wand: unter n die Ausmitte je Knoten, von unten nach oben."""

    n: float
    e: Tuple[float, ...]

    @property
    def stelle(self) -> int:
        """Der Knoten mit der grössten Ausmitte."""
        return max(range(len(self.e)), key=lambda i: abs(self.e[i]))

    @property
    def e_max(self) -> float:
        """Die grösste Ausmitte, mit Vorzeichen."""
        return self.e[self.stelle]

    @property
    def hoehe(self) -> float:
        """Wo sie liegt: der Anteil der Höhe ab dem Fuss, 0 bis 1."""
        return self.stelle / (len(self.e) - 1)

    @property
    def e_u(self) -> float:
        return self.e[0]

    @property
    def e_o(self) -> float:
        return self.e[-1]


#: Was k_N begrenzt.
DRUCK = "druck"
"""Die ganze Druckfestigkeit: k_N = 1 -- Gl. (7)."""

AUSMITTE = "ausmitte"
"""Die Ausmitte erreicht die Grenze der Figur 4."""

STABILITAET = "stabilitaet"
"""Darüber gibt es kein Gleichgewicht mehr, oder es kippt."""


@dataclass(frozen=True)
class Knickergebnis:
    """Was die Rechnung findet -- ``bei_n_d`` der Zustand unter n_d, ``None`` darüber."""

    k_N: float
    grund: str
    """:data:`DRUCK`, :data:`AUSMITTE` oder :data:`STABILITAET`."""

    grenzzustand: Optional[Zustand]
    """Der letzte Zustand, der hielt -- ``None``, wenn schon keine Last hält."""

    bei_n_d: Optional[Zustand] = None


@dataclass(frozen=True)
class Querergebnis:
    """Was die Suche nach der Querlast findet -- siehe :func:`querlast`."""

    lam: float
    """Die grösste Querlast als λ = q · h_w²/(t_w² · f_xd), null, wenn schon n allein nicht hält."""

    grund: str
    """:data:`AUSMITTE` oder :data:`STABILITAET`: was über ihr nicht mehr hielt."""

    grenzzustand: Optional[Zustand]
    """Der letzte Zustand, der hielt -- ``None``, wenn schon n allein nicht hält."""


class _Wand:
    """Die Gleichungen einer Wand in Dicken: Höhe ``ht``, Ränder unten und oben."""

    def __init__(self, ht: float, e_u: Optional[float], e_o: Optional[float], E_f: float) -> None:
        self.ht = ht
        self.e_u = e_u
        self.e_o = e_o
        self.E_f = E_f
        self.d = ht / TEILE
        self.offen = [r for r, e in (("u", e_u), ("o", e_o)) if e is None]
        """Die eingespannten Ränder: ihre Ausmitte ist unbekannt."""

    def ausmitten(self, w: Sequence[float], p_u: float, p_o: float,
                  quer: float = 0.0) -> List[float]:
        """Je Knoten die Ausmitte -- ``quer`` ist λ/(2 n), die Querlast (Dateikopf)."""
        return [p_u + (p_o - p_u) * i / TEILE + quer * i * (TEILE - i) / TEILE ** 2 + w[i]
                for i in range(TEILE + 1)]

    def loesen(self, n: float, start: Optional[Tuple[List[float], float, float]],
               quer: float = 0.0) -> Optional[Tuple[List[float], float, float, int]]:
        """
        Das Gleichgewicht unter n nach Newton, von ``start`` aus -- ``(w, p_u,
        p_o, Vorzeichen der Determinante)`` oder ``None``, wenn es keines findet.
        ``quer`` wie bei :meth:`ausmitten`: es hängt nicht an w, die Ableitung
        bleibt dieselbe.
        """
        m = TEILE - 1
        d2 = self.d * self.d
        c = 12.0 * n / (math.pi ** 2 * self.E_f)
        if start is None:
            w, p_u, p_o = [0.0] * (TEILE + 1), self.e_u or 0.0, self.e_o or 0.0
        else:
            w, p_u, p_o = list(start[0]), start[1], start[2]
        for _ in range(40):
            e = self.ausmitten(w, p_u, p_o, quer)
            if any(abs(x) >= FORMELGRENZE for x in e):
                return None
            chi = [c * g(x) for x in e]
            dchi = [c * _dg(x) for x in e]
            F = [(w[i - 1] - 2.0 * w[i] + w[i + 1]) / d2 + chi[i] for i in range(1, TEILE)]
            G = [(2.0 * w[1] / d2 + chi[0]) if r == "u" else (2.0 * w[m] / d2 + chi[TEILE])
                 for r in self.offen]
            # Die Ableitung: dreibandig in w, dazu je eingespannten Rand eine Spalte und eine Zeile.
            diag = [-2.0 / d2 + dchi[i] for i in range(1, TEILE)]
            neben = 1.0 / d2
            piv = [0.0] * m
            fak = [0.0] * m
            piv[0] = diag[0]
            for i in range(1, m):
                if piv[i - 1] == 0.0:
                    return None
                fak[i] = neben / piv[i - 1]
                piv[i] = diag[i] - fak[i] * neben
            if piv[-1] == 0.0:
                return None

            def aufloesen(rechts: List[float]) -> List[float]:
                y = list(rechts)
                for i in range(1, m):
                    y[i] -= fak[i] * y[i - 1]
                z = [0.0] * m
                z[-1] = y[-1] / piv[-1]
                for i in range(m - 2, -1, -1):
                    z[i] = (y[i] - neben * z[i + 1]) / piv[i]
                return z

            z = aufloesen(F)
            spalten = [aufloesen([dchi[i] * ((1.0 - i / TEILE) if r == "u" else i / TEILE)
                                  for i in range(1, TEILE)]) for r in self.offen]
            # Das Schur-Komplement der Ränder: S = D − C X, rechts −G + C z.
            k = len(self.offen)
            S = [[0.0] * k for _ in range(k)]
            rechts = [0.0] * k
            for a, r in enumerate(self.offen):
                j = 0 if r == "u" else m - 1
                for b in range(k):
                    S[a][b] = (dchi[0 if r == "u" else TEILE] if a == b else 0.0) \
                        - 2.0 / d2 * spalten[b][j]
                rechts[a] = -G[a] + 2.0 / d2 * z[j]
            if k == 0:
                det_s, dp = 1.0, []
            elif k == 1:
                det_s = S[0][0]
                if det_s == 0.0:
                    return None
                dp = [rechts[0] / det_s]
            else:
                det_s = S[0][0] * S[1][1] - S[0][1] * S[1][0]
                if det_s == 0.0:
                    return None
                dp = [(rechts[0] * S[1][1] - S[0][1] * rechts[1]) / det_s,
                      (S[0][0] * rechts[1] - S[1][0] * rechts[0]) / det_s]
            dw = [-z[i] - sum(spalten[b][i] * dp[b] for b in range(k)) for i in range(m)]
            for i in range(m):
                w[i + 1] += dw[i]
            for b, r in enumerate(self.offen):
                if r == "u":
                    p_u += dp[b]
                else:
                    p_o += dp[b]
            schritt = max([abs(x) for x in dw + dp], default=0.0)
            if not all(math.isfinite(x) for x in dw + dp):
                return None
            if schritt < 1e-11:
                negativ = sum(1 for x in piv if x < 0.0) + (1 if det_s < 0.0 else 0)
                return w, p_u, p_o, (-1) ** negativ
        return None


def k_N(ht: float, e_u: Optional[float], e_o: Optional[float], E_f: float = 1000.0,
        n_d: Optional[float] = None) -> Knickergebnis:
    """
    Der Beiwert k_N einer Wand von ``ht`` Dicken Höhe -- Ausmitten ``e_u`` am
    Fuss und ``e_o`` am Kopf in Dicken, ``None`` für einen eingespannten
    Rand; ``E_f`` = E_xd/f_xd. Mit ``n_d`` auch der Zustand unter dieser
    Last, wenn sie hält. Siehe Dateikopf.
    """
    ergebnis = _k_N(round(ht, 9), _gerundet(e_u), _gerundet(e_o), round(E_f, 9),
                    None if n_d is None else round(n_d, 9))
    return ergebnis


def _gerundet(e: Optional[float]) -> Optional[float]:
    return None if e is None else round(e, 9)


@lru_cache(maxsize=512)
def _k_N(ht: float, e_u: Optional[float], e_o: Optional[float], E_f: float,
         n_d: Optional[float]) -> Knickergebnis:
    """Die Rechnung hinter :func:`k_N`, je Fall einmal: die Zeichnung fragt nach jeder Eingabe."""
    wand = _Wand(ht, e_u, e_o, E_f)
    ohne_last = Zustand(0.0, tuple(wand.ausmitten([0.0] * (TEILE + 1), e_u or 0.0, e_o or 0.0)))
    if max(abs(x) for x in ohne_last.e) > grenze(0.0):
        return Knickergebnis(0.0, AUSMITTE, None, None)
    # Das Vorzeichen der Determinante unter kleiner Last: das stabile Gleichgewicht.
    anfang = wand.loesen(1e-6, None)
    if anfang is None:
        return Knickergebnis(0.0, STABILITAET, None, None)
    vorzeichen = anfang[3]
    stand = anfang[:3]
    n_ok, zustand_ok, grund = 0.0, ohne_last, STABILITAET
    bei_n_d: Optional[Zustand] = ohne_last if n_d is not None and n_d <= 0.0 else None
    # n_d wird einmal eigens versucht; hält es nicht, liegt es über k_N.
    n_d_offen = n_d is not None and bei_n_d is None
    schritt = SCHRITT
    while schritt >= GENAU:
        n = min(1.0, n_ok + schritt)
        # Auch wenn ein Schritt genau auf n_d fällt: dann ist er der Versuch.
        versuch_n_d = n_d_offen and n_ok < n_d <= n
        if versuch_n_d:
            n, n_d_offen = n_d, False
        loesung = wand.loesen(n, stand)
        zustand = None if loesung is None or loesung[3] != vorzeichen \
            else Zustand(n, tuple(wand.ausmitten(*loesung[:3])))
        if zustand is None or abs(zustand.e_max) > grenze(n) + 1e-12:
            # Was zuletzt nicht hielt, begrenzt k_N: die Schritte enden an der Grenze.
            grund = STABILITAET if zustand is None else AUSMITTE
            if not versuch_n_d:
                schritt /= 2.0
            continue
        n_ok, zustand_ok, stand = n, zustand, loesung[:3]
        if versuch_n_d:
            bei_n_d = zustand
        if n >= 1.0:
            return Knickergebnis(1.0, DRUCK, zustand_ok, bei_n_d)
    return Knickergebnis(n_ok, grund, zustand_ok, bei_n_d)


def querlast(ht: float, e_u: Optional[float], e_o: Optional[float], E_f: float, n: float,
             richtung: int) -> Querergebnis:
    """
    Die grösste Querlast der Wand von ``ht`` Dicken Höhe unter der festen
    Normalkraft ``n`` -- Ausmitten und ``E_f`` wie bei :func:`k_N`,
    ``richtung`` +1, wenn die Querlast zur Seite positiver Ausmitten drückt,
    sonst −1. Siehe Dateikopf.
    """
    return _querlast(round(ht, 9), _gerundet(e_u), _gerundet(e_o), round(E_f, 9), round(n, 9),
                     1 if richtung >= 0 else -1)


@lru_cache(maxsize=512)
def _querlast(ht: float, e_u: Optional[float], e_o: Optional[float], E_f: float, n: float,
              richtung: int) -> Querergebnis:
    """Die Rechnung hinter :func:`querlast`, je Fall einmal."""
    if n <= 0.0:
        return Querergebnis(0.0, STABILITAET, None)
    ohne = _k_N(ht, e_u, e_o, E_f, n)
    if ohne.bei_n_d is None:
        return Querergebnis(0.0, ohne.grund, None)
    wand = _Wand(ht, e_u, e_o, E_f)
    anfang = wand.loesen(1e-6, None)
    if anfang is None:
        return Querergebnis(0.0, STABILITAET, None)
    vorzeichen = anfang[3]
    e = ohne.bei_n_d.e
    p_u, p_o = e[0], e[-1]
    stand = ([x - p_u - (p_o - p_u) * i / TEILE for i, x in enumerate(e)], p_u, p_o)
    lam_1 = 8.0 * n * grenze(n)
    mu_ok, zustand_ok, grund = 0.0, ohne.bei_n_d, STABILITAET
    schritt = QUER_SCHRITT
    while schritt >= QUER_GENAU:
        mu = mu_ok + schritt
        if mu > QUER_HOECHSTENS:
            break
        quer = richtung * mu * lam_1 / (2.0 * n)
        loesung = wand.loesen(n, stand, quer)
        zustand = None if loesung is None or loesung[3] != vorzeichen \
            else Zustand(n, tuple(wand.ausmitten(*loesung[:3], quer)))
        if zustand is None or abs(zustand.e_max) > grenze(n) + 1e-12:
            grund = STABILITAET if zustand is None else AUSMITTE
            schritt /= 2.0
            continue
        mu_ok, zustand_ok, stand = mu, zustand, loesung[:3]
    return Querergebnis(mu_ok * lam_1, grund, zustand_ok)
