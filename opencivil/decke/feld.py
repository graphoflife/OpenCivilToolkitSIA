"""
opencivil/decke/feld.py -- die Schnittkräfte der Platte an einer Stelle.

VERANTWORTUNG:
Aus den Trägern eines Falls, was an einer Stelle der Platte wirkt: die
Momente ``m_x``, ``m_y``, ``m_xy`` je Meter, die Querkräfte ``v_x``,
``v_y`` je Meter und daraus die erforderlichen Biegewiderstände. Dazu die
Lastverteilelemente über Stützen und unter Einzellasten.

VOM STREIFEN ZUR PLATTE:
Ein Streifen der Breite ``b`` in Richtung ``n`` trägt mit dem Moment ``M``
und der Querkraft ``V``; je Meter sind das ``m = M/b`` und ``v = V/b``, in
seiner Richtung ``n``. In den Achsen x, y wird daraus mit dem Winkel ``φ``
von ``n`` gegen x -- die Transformation der Stahlbeton II, 7.2 Platten,
Folie 14, rückwärts gelesen, mit ``m_n = m`` und ``m_t = m_nt = 0``::

    m_x  = m · cos²φ
    m_y  = m · sin²φ
    m_xy = m · sinφ · cosφ

Ein Streifen in x trägt also nur ``m_x``, einer in y nur ``m_y``; ein
schiefer Streifen trägt mit ``m_η`` auch ein Drillmoment ``m_xy``. An einer
Stelle zählen alle Streifen, die über sie gehen -- je Richtung ein
Feldstreifen und jeder Unterzug, in dessen Fläche sie liegt.

BIEGEWIDERSTÄNDE:
Nach der linearisierten Normalmomenten-Fliessbedingung, ``k = k' = 1``
(Folien 9 und 10) -- in der Norm SIA 262:2025, 4.3.2.6, (34), als Näherung
für Bewehrung in x und y und nicht zu grosse Drillmomente. Weicht die
Hauptbeanspruchung deutlich von der Bewehrung ab, etwa bei schiefen
Streifen, verlangt 4.3.2.5, das zu beachten::

    m_x,u  ≥  m_x + |m_xy|      m'_x,u ≥ −m_x + |m_xy|
    m_y,u  ≥  m_y + |m_xy|      m'_y,u ≥ −m_y + |m_xy|

Was negativ herauskommt, braucht keine Bewehrung: null.

LASTVERTEILELEMENTE (Folie 38):
Über einer Stütze tragen die Streifen in den Stützenbereich ``l_x × l_y``,
als läge dort eine gleichmässige Pressung. Damit die Stützenkraft ``Q``
als Punkt hineinpasst, braucht der Bereich zusätzlich::

    m'_x,u ≥ Q/8 · l_x/l_y          m_x,u ≥ (1/(2π) − 1/8) · Q · l_x/l_y
    m'_y,u ≥ Q/8 · l_y/l_x          m_y,u ≥ (1/(2π) − 1/8) · Q · l_y/l_x

Unter einer Einzellast gilt dasselbe mit vertauschten Seiten: die
gleichmässige Last ist dort, wo die Streifen sie tragen, und der Punkt,
wo die Last angreift.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Punktlast
from opencivil.decke.rechnung import Ergebnis, Fallergebnis
from opencivil.decke.traeger import wert

#: Der positive Widerstand je Last eins im Lastverteilelement: ``1/(2π) − 1/8``, auf der Folie 0.034.
POSITIV_JE_LAST = 1.0 / (2.0 * math.pi) - 1.0 / 8.0


@dataclass(frozen=True)
class Schnittkraefte:
    """An einer Stelle: Momente in Nm/m, Querkräfte in N/m."""

    mx: float = 0.0
    my: float = 0.0
    mxy: float = 0.0
    vx: float = 0.0
    vy: float = 0.0

    @property
    def v0(self) -> float:
        """Die Hauptquerkraft ``√(v_x² + v_y²)``."""
        return math.hypot(self.vx, self.vy)

    def __add__(self, andere: "Schnittkraefte") -> "Schnittkraefte":
        return Schnittkraefte(self.mx + andere.mx, self.my + andere.my, self.mxy + andere.mxy,
                              self.vx + andere.vx, self.vy + andere.vy)


@dataclass(frozen=True)
class Widerstaende:
    """Die erforderlichen Biegewiderstände in Nm/m: unten (positiv) und oben (gestrichen)."""

    mxu: float
    myu: float
    mxu_oben: float
    myu_oben: float


def in_xy(m: float, v: float, n: Punkt) -> Schnittkraefte:
    """Moment und Querkraft je Meter eines Streifens in Richtung ``n`` -- in den Achsen x, y."""
    c, s = n
    return Schnittkraefte(m * c * c, m * s * s, m * s * c, v * c, v * s)


def an_stelle(ergebnis: Ergebnis, fall: Fallergebnis, p: Punkt) -> Schnittkraefte:
    """
    Die Schnittkräfte an der Stelle ``p``: je Richtung der Feldstreifen, in
    dem sie liegt, und jeder Unterzug, in dessen Fläche sie liegt. An der
    Grenze zweier Feldstreifen zählt der mit dem grösseren ``τ``.
    """
    heraus = Schnittkraefte()
    zerlegung = ergebnis.zerlegung
    for r in zerlegung.richtungen:
        tau = geo.skalar(p, r.t)
        feld = zerlegung.feldstreifen(r)
        streifen = next((s for s in feld if s.von <= tau < s.bis), None)
        if streifen is None and feld and abs(tau - max(s.bis for s in feld)) <= geo.TOLERANZ:
            streifen = max(feld, key=lambda s: s.bis)
        if streifen is not None:
            heraus = heraus + _beitrag(fall, streifen, p)
    for u in zerlegung.unterzuege:
        if geo.innen(p, u.gebiet):
            heraus = heraus + _beitrag(fall, u, p)
    return heraus


def _beitrag(fall: Fallergebnis, streifen, p: Punkt) -> Schnittkraefte:
    s = geo.skalar(p, streifen.richtung.n)
    for t in streifen.traeger:
        if t.s0 - geo.TOLERANZ <= s <= t.s1 + geo.TOLERANZ:
            ergebnis = fall.traeger.get(t.name)
            if ergebnis is None:
                return Schnittkraefte()
            lokal = min(max(s - t.s0, 0.0), t.L)
            return in_xy(wert(ergebnis.stuecke, "M", lokal) / streifen.breite,
                         wert(ergebnis.stuecke, "V", lokal) / streifen.breite, streifen.richtung.n)
    return Schnittkraefte()


def widerstaende(k: Schnittkraefte) -> Widerstaende:
    """Die erforderlichen Biegewiderstände nach der linearisierten Fliessbedingung, ``k = 1``."""
    d = abs(k.mxy)
    return Widerstaende(max(0.0, k.mx + d), max(0.0, k.my + d), max(0.0, -k.mx + d), max(0.0, -k.my + d))


# ===========================================================================
# Lastverteilelemente
# ===========================================================================


@dataclass(frozen=True)
class Lastverteilelement:
    """
    Ein Lastverteilelement ``lx × ly`` um ``ort``: was es zusätzlich an
    Biegewiderstand braucht, in Nm/m -- ``oben`` für negative, ``unten`` für
    positive Momente, je in x und y.
    """

    name: str
    art: str
    """``stuetze`` oder ``einzellast``."""

    ort: Punkt
    lx: float
    ly: float
    Q: float
    """Die Kraft, die es bündelt, in N: die Stützenkraft nach oben, die Einzellast nach unten positiv."""

    @property
    def ecken(self) -> List[Punkt]:
        return geo.achsrechteck(self.ort, self.lx, self.ly)

    def zusatz(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        ``((oben_x, unten_x), (oben_y, unten_y))``: das zusätzliche negative
        Moment (≤ 0) und das zusätzliche positive (≥ 0), je Richtung.
        """
        # Eine Einzellast ist eine Stütze, die nach unten zieht: oben und unten tauschen.
        gestuetzt = self.Q if self.art == "stuetze" else -self.Q
        heraus = []
        for verhaeltnis in (self.lx / self.ly, self.ly / self.lx):
            werte = (-gestuetzt * verhaeltnis / 8.0, POSITIV_JE_LAST * gestuetzt * verhaeltnis)
            heraus.append((min(werte), max(werte)))
        return heraus[0], heraus[1]


def lastverteilelemente(ergebnis: Ergebnis, fall: Fallergebnis) -> List[Lastverteilelement]:
    """Je Stütze mit Kraft und je Einzellast des Falls ein Lastverteilelement."""
    heraus: List[Lastverteilelement] = []
    for st in ergebnis.decke.stuetzen:
        Q = fall.stuetzenkraft(st.name)
        if not Q:
            continue
        lo_x, hi_x = geo.bereich(ergebnis.zerlegung.stuetzenbereiche[st.name], (1.0, 0.0))
        lo_y, hi_y = geo.bereich(ergebnis.zerlegung.stuetzenbereiche[st.name], (0.0, 1.0))
        heraus.append(Lastverteilelement(st.name, "stuetze", st.ort, hi_x - lo_x, hi_y - lo_y, Q))
    for last, faktor in _einzellasten(ergebnis, fall.name):
        heraus.append(Lastverteilelement(last.name, "einzellast", last.ort, last.lx, last.ly, faktor * last.wert))
    return heraus


def _einzellasten(ergebnis: Ergebnis, name: str) -> Sequence[Tuple[Punktlast, float]]:
    """Die Einzellasten eines Lastfalls oder einer Kombination, mit ihrem Beiwert."""
    decke = ergebnis.decke
    faelle = {lf.name: lf for lf in decke.lastfaelle}
    if name in faelle:
        anteile = {name: 1.0}
    else:
        kombination = next((k for k in decke.kombinationen if k.name == name), None)
        anteile = dict(kombination.faktoren) if kombination else {}
    return [(last, faktor) for lf_name, faktor in anteile.items() if faktor and lf_name in faelle
            for last in faelle[lf_name].lasten if isinstance(last, Punktlast)]
