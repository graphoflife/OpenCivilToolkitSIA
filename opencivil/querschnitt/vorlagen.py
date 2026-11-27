"""
opencivil/querschnitt/vorlagen.py -- Querschnitte zum Anfangen.

VERANTWORTUNG:
Vier Vorlagen -- Rechteck, T-Balken, Hohlkasten, Kreis. Jede kennt ihre
Masse samt Vorgabe -- der Kreis auch, wie viele Staebe er hat -- und baut
daraus :class:`Teile` in mm, den Ursprung unten links: die Polygone, auf Wunsch die Bewehrung und die Schubwaende, und fuer
die Skizze im Zeichenfenster die Masslinien.

Die Vorlagen stehen nur hier. :meth:`QuerschnittsanalyseEintrag.neu` baut
seine frische Analyse aus dem Rechteck, und die Oberflaeche fragt nach ihnen:
``vorlage`` fuer die Skizze, waehrend man tippt, ``vorlage_einsetzen`` zum
Einsetzen. Vorher stand das Rechteck zweimal da, in Python und in JS.

Was eine Vorlage nicht sagt, kommt aus den Vorgaben der Eintraege -- der
Stahl, die Buegel einer Schubwand, ihre Schnitte. Eine Vorlage ist ein
Anfang, kein Entwurf.

DAS MASS:
Ein :class:`Mass` steht fuer die Vorlagen hier und die der Stabquerschnitte
(:mod:`opencivil.stabwerk.querschnitte`). Seine Grenze ist ein
:class:`~opencivil.core.bereich.Bereich` wie die eines Feldes: derselbe
Satz, dieselbe Angabe fuer die Maske. Bis 2026-11-20 hatte jede Seite ihre
eigene Klasse, ihren eigenen Satz und im Fenster ihren eigenen Mindestwert --
1 hier, 0 beim Stab.

DIE UMRISSE:
Rechteck, T und Kreis zeichnet auch das Balkensystem fuer seine
Stabquerschnitte (:mod:`opencivil.stabwerk.querschnitte`). Ihre Umrisse und
was an einem T nicht geht, stehen darum hier, einmal fuer beide
(:func:`rechteckpunkte`, :func:`t_punkte`, :func:`t_pruefen`,
:func:`kreispunkte`). Bis 2026-10-25 standen sie in beiden Katalogen, und
ein Steg so breit wie der Flansch galt im einen als T, im anderen nicht.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

from opencivil.core.bereich import Bereich
from opencivil.core.einheiten import EINHEITSLOS, MM, Einheit

Punkt = Tuple[float, float]

#: Ecken eines Kreises. Sie liegen auf dem Kreis; was das an Flaeche kostet,
#: rechnet die Geometrie wie bei jedem anderen Polygon.
KREISECKEN = 48


@dataclass(frozen=True)
class Mass:
    """
    Ein Mass einer Vorlage: eine Laenge in mm, wo ``einheit`` nichts anderes
    sagt -- oder, ``ganzzahlig``, eine Anzahl, wie die der Staebe im Kreis.
    Jedes ist groesser als null; was die Masse untereinander verlangen,
    prueft die Vorlage.
    """

    schluessel: str
    symbol: str
    """Wie es in der Skizze heisst -- leer, wo es dort nicht steht."""

    beschriftung: str
    vorgabe: float
    einheit: Einheit = MM
    ganzzahlig: bool = False
    pfeil: float = 0.0
    """Um wie viel ein Pfeil am Feld den Wert aendert -- 0: um 1 bei einer Anzahl, sonst um 10."""

    @property
    def heisst(self) -> str:
        """Wie es an der Maske und in einer Meldung heisst: «Breite b»."""
        return " ".join(filter(None, (self.beschriftung, self.symbol)))

    @property
    def bereich(self) -> Bereich:
        return Bereich(self.heisst, self.einheit, ueber=0.0)

    @property
    def schritt(self) -> float:
        """Um wie viel ein Pfeil am Feld den Wert aendert -- siehe :attr:`pfeil`."""
        return self.pfeil or (1.0 if self.ganzzahlig else 10.0)

    def grund(self, wert: float) -> str:
        """Was an ``wert`` nicht geht, als Satz mit Punkt -- leer, wenn er geht."""
        if not math.isfinite(wert):
            return f"{self.heisst} muss eine Zahl sein, nicht {wert:g}."
        if self.ganzzahlig and not float(wert).is_integer():
            return (f"{self.heisst} muss eine ganze Zahl sein, "
                    f"angegeben ist {self.bereich.zahl(wert)}.")
        return self.bereich.grund(wert)

    def als_dict(self) -> Dict[str, Any]:
        """
        Fuer den Katalog: wie es heisst, seine Vorgabe, der Schritt der
        Pfeile und, was die Maske wie bei einem Feld braucht (``angabe``:
        Einheit, Grenze, Satz, bei einer Anzahl ``ganz``).
        """
        angabe = self.bereich.angabe()
        if self.ganzzahlig:
            angabe["ganz"] = True
        return {"schluessel": self.schluessel, "symbol": self.symbol,
                "beschriftung": self.beschriftung, "heisst": self.heisst,
                "vorgabe": self.vorgabe, "schritt": self.schritt, "angabe": angabe}


#: Der Achsabstand der Staebe vom Rand -- ein Mass jeder Vorlage hier. Auch
#: die Schubwaende enden auf seiner Hoehe.
RANDABSTAND = Mass("randabstand", "", "Achsabstand", 50.0)


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

    bleche: List[dict] = field(default_factory=list)
    """Je Profilblech ``punkte``, seine Linie -- nur in der Skizze einer Blechverbunddecke."""

    masslinien: List[dict] = field(default_factory=list)
    """Nur fuer die Skizze: ``von``, ``bis``, ``text`` und ``seite``
    ('unten', 'oben', 'links', 'rechts') -- wohin sie neben dem Bauteil steht."""

    def als_dict(self) -> dict:
        return asdict(self)


def masslinie(von: Punkt, bis: Punkt, name: str, wert: float, seite: str) -> dict:
    """Eine Masslinie der Skizze, «b = 300», auf der ``seite`` neben dem Bauteil -- auch fuer ein Stahlprofil."""
    return {"von": von, "bis": bis, "text": f"{name} = {wert:g}", "seite": seite}


def kreispunkte(mitte: Punkt, radius: float, ecken: int = KREISECKEN) -> List[Punkt]:
    """
    ``ecken`` Punkte, gleich verteilt auf einem Kreis, der erste rechts, auf
    Tausendstel gerundet: die Ecken eines Kreises als Vieleck -- oder die
    Staebe darin.
    """
    return [(round(mitte[0] + radius * math.cos(2 * math.pi * k / ecken), 3),
             round(mitte[1] + radius * math.sin(2 * math.pi * k / ecken), 3))
            for k in range(ecken)]


def rechteckpunkte(b: float, h: float, y: float = 0.0, z: float = 0.0) -> List[Punkt]:
    """Ein Rechteck ``b`` breit und ``h`` hoch, die Ecke unten links in ``(y, z)``."""
    return [(y, z), (y + b, z), (y + b, z + h), (y, z + h)]


def t_punkte(b: float, h: float, b_w: float, h_f: float) -> List[Punkt]:
    """Ein T, der Flansch oben und mittig ueber dem Steg -- der Ursprung unten links."""
    y0 = (b - b_w) / 2
    return [(y0, 0.0), (y0 + b_w, 0.0), (y0 + b_w, h - h_f), (b, h - h_f), (b, h),
            (0.0, h), (0.0, h - h_f), (y0, h - h_f)]


def t_pruefen(b: float, h: float, b_w: float, h_f: float) -> Optional[str]:
    """
    Was an einem T nicht geht -- ``None``, wenn alles geht. Ein Steg so breit
    wie der Flansch gaebe ein Rechteck mit doppelten Ecken: dafuer gibt es das
    Rechteck.
    """
    if b_w >= b:
        return "Der Steg b_w muss schmaler sein als der Flansch b."
    if h_f >= h:
        return "Der Flansch h_f muss dünner sein als die Höhe h."
    return None


# ===========================================================================
# Die vier Vorlagen
# ===========================================================================


def _rechteck(m: Mapping[str, float], r: float) -> Teile:
    b, h = m["b"], m["h"]
    return Teile(
        polygone=[{"punkte": rechteckpunkte(b, h), "aussparung": False}],
        stablinien=[
            {"von": (r, r), "bis": (b - r, r), "art": "anzahl", "anzahl": 3.0, "durchmesser": 20.0},
            {"von": (r, h - r), "bis": (b - r, h - r), "art": "anzahl", "anzahl": 2.0,
             "durchmesser": 12.0},
        ],
        # Eine Wand ueber die ganze Breite: der Steg ist der Querschnitt.
        schubwaende=[{"von": (b / 2, r), "bis": (b / 2, h - r), "dicke": b}],
        masslinien=[masslinie((0.0, 0.0), (b, 0.0), "b", b, "unten"),
                    masslinie((0.0, 0.0), (0.0, h), "h", h, "links")],
    )


def _rechteck_pruefen(m: Mapping[str, float], r: float) -> Optional[str]:
    if 2 * r >= min(m["b"], m["h"]):
        return "Der Achsabstand der Stäbe muss kleiner sein als die halbe Breite und Höhe."
    return None


def _tbalken(m: Mapping[str, float], r: float) -> Teile:
    b, h, bw, hf = m["b"], m["h"], m["b_w"], m["h_f"]
    y0 = (b - bw) / 2
    return Teile(
        polygone=[{"punkte": t_punkte(b, h, bw, hf), "aussparung": False}],
        stablinien=[
            {"von": (y0 + r, r), "bis": (y0 + bw - r, r), "art": "anzahl", "anzahl": 3.0,
             "durchmesser": 20.0},
            {"von": (r, h - r), "bis": (b - r, h - r), "art": "teilung", "teilung": 150.0,
             "durchmesser": 12.0},
        ],
        # Der Steg bis in die Mitte des Flanschs.
        schubwaende=[{"von": (b / 2, r), "bis": (b / 2, h - hf / 2), "dicke": bw}],
        masslinien=[masslinie((0.0, h), (b, h), "b", b, "oben"),
                    masslinie((0.0, 0.0), (0.0, h), "h", h, "links"),
                    masslinie((y0, 0.0), (y0 + bw, 0.0), "b_w", bw, "unten"),
                    masslinie((b, h - hf), (b, h), "h_f", hf, "rechts")],
    )


def _tbalken_pruefen(m: Mapping[str, float], r: float) -> Optional[str]:
    grund = t_pruefen(m["b"], m["h"], m["b_w"], m["h_f"])
    if grund:
        return grund
    if 2 * r >= m["b_w"] or r >= m["h_f"]:
        return "Der Achsabstand der Stäbe muss im Steg und im Flansch Platz haben."
    return None


def _hohlkasten(m: Mapping[str, float], r: float) -> Teile:
    b, h, t = m["b"], m["h"], m["t"]
    halb = t / 2
    return Teile(
        polygone=[
            {"punkte": rechteckpunkte(b, h), "aussparung": False},
            {"punkte": rechteckpunkte(b - 2 * t, h - 2 * t, t, t), "aussparung": True},
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
        masslinien=[masslinie((0.0, 0.0), (b, 0.0), "b", b, "unten"),
                    masslinie((0.0, 0.0), (0.0, h), "h", h, "links"),
                    masslinie((b - t, h), (b, h), "t", t, "oben")],
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
        staebe=[{"lage": p, "durchmesser": 16.0}
                for p in kreispunkte(mitte, d / 2 - r, int(m["n"]))],
        masslinien=[masslinie((0.0, 0.0), (d, 0.0), "D", d, "unten")],
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

    def bauen(self, masse: Optional[Mapping[str, float]] = None,
              randabstand: float = RANDABSTAND.vorgabe,
              bewehrung: bool = True, schubwaende: bool = True) -> Teile:
        """
        Die Teile zu diesen Massen -- was fehlt, nach Vorgabe. ``randabstand``
        ist der Achsabstand der Staebe vom Rand. Ohne ``bewehrung`` keine
        Staebe und Linien, ohne ``schubwaende`` keine Waende. Passen die
        Masse nicht zueinander, ein ``ValueError`` mit dem Grund.
        """
        werte = {m.schluessel: float((masse or {}).get(m.schluessel, m.vorgabe))
                 for m in self.masse}
        waende = schubwaende and self.hat_waende
        # Auch die Waende enden auf der Hoehe der Staebe.
        mit_rand = bewehrung or waende
        for m, wert in [*((m, werte[m.schluessel]) for m in self.masse),
                        *([(RANDABSTAND, randabstand)] if mit_rand else [])]:
            grund = m.grund(wert)
            if grund:
                raise ValueError(grund)
        grund = self.pruefen(werte, randabstand if mit_rand else 0.0)
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
            (Mass("b", "b", "Breite", 300.0), Mass("h", "h", "Höhe", 600.0)),
            _rechteck, _rechteck_pruefen),
    Vorlage("tbalken", "T-Balken",
            (Mass("b", "b", "Flanschbreite", 1200.0), Mass("h", "h", "Höhe", 700.0),
             Mass("b_w", "b_w", "Stegbreite", 300.0), Mass("h_f", "h_f", "Flanschdicke", 200.0)),
            _tbalken, _tbalken_pruefen),
    Vorlage("hohlkasten", "Hohlkasten",
            (Mass("b", "b", "Breite", 1200.0), Mass("h", "h", "Höhe", 800.0),
             Mass("t", "t", "Wanddicke", 200.0)),
            _hohlkasten, _hohlkasten_pruefen),
    Vorlage("kreis", "Kreis",
            (Mass("D", "D", "Durchmesser", 500.0),
             Mass("n", "n", "Anzahl Stäbe", 8.0, EINHEITSLOS, ganzzahlig=True)),
            _kreis, _kreis_pruefen, hat_waende=False),
)


def vorlage(schluessel: str) -> Vorlage:
    """Die Vorlage zu einem Schluessel -- ``ValueError``, wenn es sie nicht gibt."""
    for v in VORLAGEN:
        if v.schluessel == schluessel:
            return v
    bekannt = ", ".join(v.schluessel for v in VORLAGEN)
    raise ValueError(f"Keine Vorlage '{schluessel}' (bekannt sind: {bekannt}).")
