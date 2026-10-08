"""
opencivil/querschnitt/vorlagen.py -- Querschnitte zum Anfangen.

VERANTWORTUNG:
Vier Vorlagen -- Rechteck, T-Balken, Hohlkasten, Kreis. Jede kennt ihre
Masse samt Vorgabe und baut daraus :class:`Teile` in mm, den Ursprung unten
links: die Polygone, auf Wunsch die Bewehrung und die Schubwaende, und fuer
die Skizze im Zeichenfenster die Masslinien.

Die Vorlagen stehen nur hier. :meth:`QuerschnittsanalyseEintrag.neu` baut
seine frische Analyse aus dem Rechteck, und die Oberflaeche fragt nach ihnen:
``vorlage`` fuer die Skizze, waehrend man tippt, ``vorlage_einsetzen`` zum
Einsetzen. Vorher stand das Rechteck zweimal da, in Python und in JS.

Was eine Vorlage nicht sagt, kommt aus den Vorgaben der Eintraege -- der
Stahl, die Buegel einer Schubwand, ihre Schnitte. Eine Vorlage ist ein
Anfang, kein Entwurf.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Callable, Dict, List, Mapping, Optional, Tuple

Punkt = Tuple[float, float]

#: Ecken eines Kreises. Sie liegen auf dem Kreis; was das an Flaeche kostet,
#: rechnet die Geometrie wie bei jedem anderen Polygon.
KREISECKEN = 48


@dataclass(frozen=True)
class Mass:
    """Ein Mass einer Vorlage, in mm."""

    schluessel: str
    beschriftung: str
    vorgabe: float


@dataclass
class Teile:
    """Was eine Vorlage baut -- in mm, der Ursprung unten links."""

    polygone: List[dict] = field(default_factory=list)
    """Je Polygon ``punkte`` und ``aussparung``."""

    staebe: List[dict] = field(default_factory=list)
    """Je Stab ``lage`` und ``durchmesser``."""

    stablinien: List[dict] = field(default_factory=list)
    """Je Linie ``von``, ``bis`` und die Felder, die von der Vorgabe abweichen."""

    schubwaende: List[dict] = field(default_factory=list)
    """Je Wand ``von``, ``bis`` und ``dicke``."""

    masslinien: List[dict] = field(default_factory=list)
    """Nur fuer die Skizze: ``von``, ``bis``, ``text`` und ``seite``
    ('unten', 'oben', 'links', 'rechts') -- wohin sie neben dem Bauteil steht."""

    def als_dict(self) -> dict:
        return asdict(self)


def _mass(von: Punkt, bis: Punkt, name: str, wert: float, seite: str) -> dict:
    return {"von": von, "bis": bis, "text": f"{name} = {wert:g}", "seite": seite}


def kreispunkte(mitte: Punkt, radius: float) -> List[Punkt]:
    """Ein Kreis als Vieleck mit :data:`KREISECKEN` Ecken, auf Tausendstel gerundet."""
    return [(round(mitte[0] + radius * math.cos(2 * math.pi * k / KREISECKEN), 3),
             round(mitte[1] + radius * math.sin(2 * math.pi * k / KREISECKEN), 3))
            for k in range(KREISECKEN)]


# ===========================================================================
# Die vier Vorlagen
# ===========================================================================


def _rechteck(m: Mapping[str, float], r: float) -> Teile:
    b, h = m["b"], m["h"]
    return Teile(
        polygone=[{"punkte": [(0.0, 0.0), (b, 0.0), (b, h), (0.0, h)], "aussparung": False}],
        stablinien=[
            {"von": (r, r), "bis": (b - r, r), "art": "anzahl", "anzahl": 3.0, "durchmesser": 20.0},
            {"von": (r, h - r), "bis": (b - r, h - r), "art": "anzahl", "anzahl": 2.0,
             "durchmesser": 12.0},
        ],
        # Eine Wand ueber die ganze Breite: der Steg ist der Querschnitt.
        schubwaende=[{"von": (b / 2, r), "bis": (b / 2, h - r), "dicke": b}],
        masslinien=[_mass((0.0, 0.0), (b, 0.0), "b", b, "unten"),
                    _mass((0.0, 0.0), (0.0, h), "h", h, "links")],
    )


def _rechteck_pruefen(m: Mapping[str, float], r: float) -> Optional[str]:
    if 2 * r >= min(m["b"], m["h"]):
        return "Der Achsabstand der Stäbe muss kleiner sein als die halbe Breite und Höhe."
    return None


def _tbalken(m: Mapping[str, float], r: float) -> Teile:
    b, h, bw, hf = m["b"], m["h"], m["b_w"], m["h_f"]
    y0 = (b - bw) / 2
    return Teile(
        polygone=[{"punkte": [(y0, 0.0), (y0 + bw, 0.0), (y0 + bw, h - hf), (b, h - hf), (b, h),
                              (0.0, h), (0.0, h - hf), (y0, h - hf)], "aussparung": False}],
        stablinien=[
            {"von": (y0 + r, r), "bis": (y0 + bw - r, r), "art": "anzahl", "anzahl": 3.0,
             "durchmesser": 20.0},
            {"von": (r, h - r), "bis": (b - r, h - r), "art": "teilung", "teilung": 150.0,
             "durchmesser": 12.0},
        ],
        # Der Steg bis in die Mitte des Flanschs.
        schubwaende=[{"von": (b / 2, r), "bis": (b / 2, h - hf / 2), "dicke": bw}],
        masslinien=[_mass((0.0, h), (b, h), "b", b, "oben"),
                    _mass((0.0, 0.0), (0.0, h), "h", h, "links"),
                    _mass((y0, 0.0), (y0 + bw, 0.0), "b_w", bw, "unten"),
                    _mass((b, h - hf), (b, h), "h_f", hf, "rechts")],
    )


def _tbalken_pruefen(m: Mapping[str, float], r: float) -> Optional[str]:
    if m["b_w"] >= m["b"]:
        return "Der Steg muss schmaler sein als der Flansch."
    if m["h_f"] >= m["h"]:
        return "Der Flansch muss dünner sein als der ganze Querschnitt."
    if 2 * r >= m["b_w"] or r >= m["h_f"]:
        return "Der Achsabstand der Stäbe muss im Steg und im Flansch Platz haben."
    return None


def _hohlkasten(m: Mapping[str, float], r: float) -> Teile:
    b, h, t = m["b"], m["h"], m["t"]
    halb = t / 2
    return Teile(
        polygone=[
            {"punkte": [(0.0, 0.0), (b, 0.0), (b, h), (0.0, h)], "aussparung": False},
            {"punkte": [(t, t), (b - t, t), (b - t, h - t), (t, h - t)], "aussparung": True},
        ],
        stablinien=[
            {"von": (r, r), "bis": (b - r, r), "art": "teilung", "teilung": 150.0,
             "durchmesser": 16.0},
            {"von": (r, h - r), "bis": (b - r, h - r), "art": "teilung", "teilung": 150.0,
             "durchmesser": 16.0},
        ],
        # Die Waende auf den Mittellinien, Ende an Ende: sie umschliessen die
        # Zelle, und die Torsion laeuft um sie herum.
        schubwaende=[
            {"von": (halb, halb), "bis": (b - halb, halb), "dicke": t},
            {"von": (b - halb, halb), "bis": (b - halb, h - halb), "dicke": t},
            {"von": (b - halb, h - halb), "bis": (halb, h - halb), "dicke": t},
            {"von": (halb, h - halb), "bis": (halb, halb), "dicke": t},
        ],
        masslinien=[_mass((0.0, 0.0), (b, 0.0), "b", b, "unten"),
                    _mass((0.0, 0.0), (0.0, h), "h", h, "links"),
                    _mass((b - t, h), (b, h), "t", t, "oben")],
    )


def _hohlkasten_pruefen(m: Mapping[str, float], r: float) -> Optional[str]:
    if 2 * m["t"] >= min(m["b"], m["h"]):
        return "Die Wände müssen dünner sein als die halbe Breite und Höhe."
    if r >= m["t"]:
        return "Der Achsabstand der Stäbe muss kleiner sein als die Wanddicke."
    return None


def _kreis(m: Mapping[str, float], r: float) -> Teile:
    d = m["D"]
    mitte = (d / 2, d / 2)
    return Teile(
        polygone=[{"punkte": kreispunkte(mitte, d / 2), "aussparung": False}],
        staebe=[{"lage": (round(mitte[0] + (d / 2 - r) * math.cos(k * math.pi / 4), 3),
                          round(mitte[1] + (d / 2 - r) * math.sin(k * math.pi / 4), 3)),
                 "durchmesser": 16.0} for k in range(8)],
        masslinien=[_mass((0.0, 0.0), (d, 0.0), "D", d, "unten")],
    )


def _kreis_pruefen(m: Mapping[str, float], r: float) -> Optional[str]:
    if 2 * r >= m["D"]:
        return "Der Achsabstand der Stäbe muss kleiner sein als der Radius."
    return None


@dataclass(frozen=True)
class Vorlage:
    """Eine Vorlage: ihre Masse und wie sie daraus Teile baut."""

    schluessel: str
    name: str
    masse: Tuple[Mass, ...]
    teile: Callable[[Mapping[str, float], float], Teile]
    pruefen: Callable[[Mapping[str, float], float], Optional[str]]
    hat_waende: bool = True

    def bauen(self, masse: Optional[Mapping[str, float]] = None, randabstand: float = 50.0,
              bewehrung: bool = True, schubwaende: bool = True) -> Teile:
        """
        Die Teile zu diesen Massen -- was fehlt, nach Vorgabe. ``randabstand``
        ist der Achsabstand der Staebe vom Rand. Ohne ``bewehrung`` keine
        Staebe und Linien, ohne ``schubwaende`` keine Waende. Passen die
        Masse nicht zueinander, ein ``ValueError`` mit dem Grund.
        """
        werte = {m.schluessel: float((masse or {}).get(m.schluessel, m.vorgabe))
                 for m in self.masse}
        for m in self.masse:
            if not math.isfinite(werte[m.schluessel]) or werte[m.schluessel] <= 0:
                raise ValueError(f"{m.beschriftung} muss grösser als null sein.")
        waende = schubwaende and self.hat_waende
        # Auch die Waende enden auf der Hoehe der Staebe.
        if (bewehrung or waende) and (not math.isfinite(randabstand) or randabstand <= 0):
            raise ValueError("Der Achsabstand der Stäbe muss grösser als null sein.")
        grund = self.pruefen(werte, randabstand if (bewehrung or waende) else 0.0)
        if grund:
            raise ValueError(grund)
        teile = self.teile(werte, randabstand)
        if not bewehrung:
            teile.staebe, teile.stablinien = [], []
        if not waende:
            teile.schubwaende = []
        return teile


VORLAGEN: Tuple[Vorlage, ...] = (
    Vorlage("rechteck", "Rechteck",
            (Mass("b", "Breite b", 300.0), Mass("h", "Höhe h", 600.0)),
            _rechteck, _rechteck_pruefen),
    Vorlage("tbalken", "T-Balken",
            (Mass("b", "Flanschbreite b", 1200.0), Mass("h", "Höhe h", 700.0),
             Mass("b_w", "Stegbreite b_w", 300.0), Mass("h_f", "Flanschdicke h_f", 200.0)),
            _tbalken, _tbalken_pruefen),
    Vorlage("hohlkasten", "Hohlkasten",
            (Mass("b", "Breite b", 1200.0), Mass("h", "Höhe h", 800.0),
             Mass("t", "Wanddicke t", 200.0)),
            _hohlkasten, _hohlkasten_pruefen),
    Vorlage("kreis", "Kreis", (Mass("D", "Durchmesser D", 500.0),),
            _kreis, _kreis_pruefen, hat_waende=False),
)


def vorlage(schluessel: str) -> Vorlage:
    """Die Vorlage zu einem Schluessel -- ``ValueError``, wenn es sie nicht gibt."""
    for v in VORLAGEN:
        if v.schluessel == schluessel:
            return v
    bekannt = ", ".join(v.schluessel for v in VORLAGEN)
    raise ValueError(f"Keine Vorlage '{schluessel}' (bekannt sind: {bekannt}).")
