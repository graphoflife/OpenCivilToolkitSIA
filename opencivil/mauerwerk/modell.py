"""
opencivil/mauerwerk/modell.py -- eine Mauerwerkswand in der Ansicht, in SI.

VERANTWORTUNG:
Was eine Wand rechnet: ihr Umriss in der Ansicht, ihre Öffnungen mit
Stürzen, wie sie über die Dicke gemauert ist und ob die Stossfugen
vollfugig vermauert sind, und wie ihre Ränder gehalten sind. Dazu die eine
Regel, wo die Pfeiler stehen (:func:`pfeiler`). Ihre Dicke ist eine
Vorgabe der Rechnung (:data:`~opencivil.mauerwerk.werk.VORGABEN`).

KOORDINATEN UND EINHEITEN:
In der Ansicht x nach rechts, y nach oben, in m -- wie im Zeichenfenster.
Die Norm nennt die Richtungen anders (SIA 266:2015, Figur 1): ihr x steht
senkrecht zu den Lagerfugen, also lotrecht, ihr y längs der Wand, ihr z
quer zu ihr. Die Herleitung spricht mit den Zeichen der Norm: N_x, f_xd.

RECHTECKE:
Eine Wand und eine Öffnung sind Rechtecke mit waagrechten und senkrechten
Seiten (:func:`rechteck`) -- gezeichnet als Umriss aus vier Ecken, wie die
Werkzeuge «Wand» und «Öffnung» sie setzen. Eine schräge Wandkrone, etwa die eines
Giebels, rechnet das Werkzeug noch nicht.

DIE PFEILER:
Zwischen zwei Öffnungen und zwischen einer Öffnung und dem Ende der Wand
steht ein Pfeiler, so breit wie der Abstand (:func:`pfeiler`). Öffnungen,
die sich in der Breite überdecken -- ein Fenster über einer Türe --, bilden
zusammen eine Lücke. Wo keine Öffnung ist, ist die ganze Wand ein Pfeiler.

DIE LASTEN:
Lotrecht, je Lastfall (:class:`Lastfall`): waagrechte Linienlasten und
Punktlasten in der Ansicht, nach unten positiv, mit ihrer Ausmitte quer zur
Wand -- positiv zur Seite, von der aus man die Ansicht sieht. Wie sie zu
den Pfeilern kommen, sagt :mod:`~opencivil.mauerwerk.lasten`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Mapping, Optional, Sequence, Tuple

from opencivil.core.wahl import Wahl
from opencivil.decke.geometrie import Punkt

#: Unter dieser Länge in m sind zwei Koordinaten gleich.
TOLERANZ = 1e-6


class Mauerung(Wahl):
    """Wie die Wand über ihre Dicke gemauert ist -- die Begriffe nach SIA 266:2015, 1.1."""

    EINSTEIN = "einstein"
    VERBAND = "verband"

    @property
    def beschriftung(self) -> str:
        return {Mauerung.EINSTEIN: "Einsteinmauerwerk", Mauerung.VERBAND: "Verbandmauerwerk"}[self]

    @property
    def erklaerung(self) -> str:
        return {Mauerung.EINSTEIN: "Die Wand ist so dick, wie ein Stein breit oder lang ist.",
                Mauerung.VERBAND: "Über die Dicke liegen mehrere Steine, die sich quer und längs "
                                  "überlappen – alle Bemessungswerte der Tabelle 7 mal 0.85."}[self]


class Stossfugen(Wahl):
    """Wie die Stossfugen vermauert sind -- die Begriffe nach SIA 266:2015, 1.1."""

    NICHT_VOLLFUGIG = "nicht_vollfugig"
    VOLLFUGIG = "vollfugig"

    @property
    def beschriftung(self) -> str:
        return {Stossfugen.NICHT_VOLLFUGIG: "nicht vollfugig",
                Stossfugen.VOLLFUGIG: "vollfugig"}[self]

    @property
    def erklaerung(self) -> str:
        return {Stossfugen.NICHT_VOLLFUGIG: "Die Stossfugen sind nicht ganz mit Mörtel gefüllt, "
                                            "etwa knirsch vermauert – f_yd der Tabelle 7.",
                Stossfugen.VOLLFUGIG: "Lager- und Stossfugen sind ganz mit Mörtel gefüllt – das "
                                      "grössere f_yd der Tabelle 7."}[self]


class Halterung(Wahl):
    """Wie Kopf oder Fuss der Wand gehalten sind."""

    GELENKIG = "gelenkig"
    EINGESPANNT = "eingespannt"

    @property
    def beschriftung(self) -> str:
        return {Halterung.GELENKIG: "gelenkig", Halterung.EINGESPANNT: "eingespannt"}[self]

    @property
    def erklaerung(self) -> str:
        return {Halterung.GELENKIG: "Die Wand kann sich hier drehen, etwa unter einer Decke, "
                                    "die nur aufliegt.",
                Halterung.EINGESPANNT: "Die Wand kann sich hier nicht drehen."}[self]


class Seitenrand(Wahl):
    """Wie ein senkrechter Rand der Wand gehalten ist -- links oder rechts."""

    FREI = "frei"
    GEHALTEN = "gehalten"

    @property
    def beschriftung(self) -> str:
        return {Seitenrand.FREI: "frei", Seitenrand.GEHALTEN: "gehalten"}[self]

    @property
    def erklaerung(self) -> str:
        return {Seitenrand.FREI: "Der Rand endet frei.",
                Seitenrand.GEHALTEN: "Eine Querwand oder ein Pfeiler hält den Rand quer zur "
                                     "Wand: er trägt Querlast über ein waagrechtes Gewölbe "
                                     "ab."}[self]


class Sturzart(Wahl):
    """Was über einer Öffnung trägt."""

    BETON = "beton"
    VORFABRIZIERT = "vorfabriziert"

    @property
    def beschriftung(self) -> str:
        return {Sturzart.BETON: "Betonsturz", Sturzart.VORFABRIZIERT: "vorfabriziert"}[self]

    @property
    def erklaerung(self) -> str:
        return {Sturzart.BETON: "Ein Sturz aus Stahlbeton, an Ort gegossen oder versetzt.",
                Sturzart.VORFABRIZIERT: "Ein vorfabrizierter Sturz, etwa ein Sturzbrett "
                                        "mit Mauerwerk darüber."}[self]


@dataclass(frozen=True)
class Rechteck:
    """Ein Rechteck mit waagrechten und senkrechten Seiten, in m."""

    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def breite(self) -> float:
        return self.x1 - self.x0

    @property
    def hoehe(self) -> float:
        return self.y1 - self.y0

    def enthaelt(self, r: "Rechteck") -> bool:
        """Ob ``r`` ganz darin liegt -- auf dem Rand zählt."""
        return (r.x0 >= self.x0 - TOLERANZ and r.x1 <= self.x1 + TOLERANZ
                and r.y0 >= self.y0 - TOLERANZ and r.y1 <= self.y1 + TOLERANZ)

    def ueberlappt(self, r: "Rechteck") -> bool:
        """Ob beide Fläche gemeinsam haben -- berühren sie sich nur am Rand, nicht."""
        return (min(self.x1, r.x1) - max(self.x0, r.x0) > TOLERANZ
                and min(self.y1, r.y1) - max(self.y0, r.y0) > TOLERANZ)


def rechteck(ecken: Sequence[Punkt]) -> Optional[Rechteck]:
    """
    Das Rechteck mit diesen vier Ecken, wenn sie eines mit waagrechten und
    senkrechten Seiten bilden -- sonst ``None``.
    """
    if len(ecken) != 4:
        return None
    for i, a in enumerate(ecken):
        b = ecken[(i + 1) % 4]
        if abs(a[0] - b[0]) > TOLERANZ and abs(a[1] - b[1]) > TOLERANZ:
            return None
    xs, ys = [p[0] for p in ecken], [p[1] for p in ecken]
    r = Rechteck(min(xs), min(ys), max(xs), max(ys))
    return r if r.breite > TOLERANZ and r.hoehe > TOLERANZ else None


@dataclass(frozen=True)
class Umriss:
    """Ein gezeichneter Umriss: sein Name und seine Ecken in m."""

    name: str
    ecken: Tuple[Punkt, ...]

    @property
    def rechteck(self) -> Optional[Rechteck]:
        return rechteck(self.ecken)


@dataclass(frozen=True)
class Oeffnung(Umriss):
    """Eine Türe oder ein Fenster, mit dem Sturz darüber -- ``h_St`` und ``a`` in m."""

    sturz: Sturzart = Sturzart.BETON
    h_St: float = 0.2
    """Wie hoch der Sturz ist."""

    a: float = 0.15
    """Wie weit er auf jeder Seite aufliegt."""

    def sturzflaeche(self) -> Optional[Rechteck]:
        """Der Sturz in der Ansicht -- ``None``, wenn die Öffnung kein Rechteck ist."""
        r = self.rechteck
        if r is None:
            return None
        return Rechteck(r.x0 - self.a, r.y1, r.x1 + self.a, r.y1 + self.h_St)


@dataclass(frozen=True)
class Pfeiler:
    """Ein Pfeiler zwischen Öffnungen oder am Ende der Wand, in m."""

    name: str
    x0: float
    x1: float
    y0: float
    y1: float
    links: Tuple[str, ...]
    """Die Öffnungen gleich links -- leer am linken Ende der Wand."""

    rechts: Tuple[str, ...]
    """Die Öffnungen gleich rechts -- leer am rechten Ende."""

    @property
    def b(self) -> float:
        """Die Pfeilerbreite."""
        return self.x1 - self.x0


@dataclass(frozen=True)
class Wandlast:
    """
    Eine lotrechte Last, nach unten positiv: ``Q`` in N, gleichmässig von
    ``x0`` bis ``x1`` in der Höhe ``y`` -- eine Punktlast mit ``x0 = x1``.
    ``e`` ist ihre Ausmitte in m (Dateikopf). ``name`` nennt sie in einer
    Meldung.
    """

    name: str
    x0: float
    x1: float
    y: float
    Q: float
    e: float = 0.0


@dataclass(frozen=True)
class Lastfall:
    """Ein Lastfall der Wand: seine Lasten, und ob er ihr Eigengewicht bekommt."""

    name: str
    lasten: Tuple[Wandlast, ...] = ()
    eigengewicht: bool = False


@dataclass(frozen=True)
class Kombination:
    """Je Lastfall, nach seinem Namen, ein Beiwert. Was nicht dasteht, zählt null."""

    name: str
    faktoren: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Wand:
    """Die ganze Wand -- jede Liste in der Folge der Beschreibung."""

    umrisse: Tuple[Umriss, ...] = ()
    oeffnungen: Tuple[Oeffnung, ...] = ()
    mauerung: Mauerung = Mauerung.EINSTEIN
    stossfugen: Stossfugen = Stossfugen.NICHT_VOLLFUGIG
    kopf: Halterung = Halterung.GELENKIG
    fuss: Halterung = Halterung.GELENKIG
    links: Seitenrand = Seitenrand.FREI
    rechts: Seitenrand = Seitenrand.FREI
    lastfaelle: Tuple[Lastfall, ...] = ()
    kombinationen: Tuple[Kombination, ...] = ()

    @property
    def verband(self) -> bool:
        return self.mauerung is Mauerung.VERBAND

    @property
    def vollfugig(self) -> bool:
        return self.stossfugen is Stossfugen.VOLLFUGIG

    @property
    def flaeche(self) -> Optional[Rechteck]:
        """Die Wand als Rechteck: ``None`` ohne genau einen rechteckigen Umriss."""
        return self.umrisse[0].rechteck if len(self.umrisse) == 1 else None


def pfeiler(wand: Rechteck, oeffnungen: Sequence[Oeffnung]) -> List[Pfeiler]:
    """
    Die Pfeiler der Wand, von links nach rechts -- P1, P2 … (Dateikopf).
    Gezählt werden nur Öffnungen, die Rechtecke sind.
    """
    flaechen = {o.name: o.rechteck for o in oeffnungen if o.rechteck is not None}
    luecken: List[Tuple[float, float, List[str]]] = []
    for name, r in sorted(flaechen.items(), key=lambda e: e[1].x0):
        if luecken and r.x0 < luecken[-1][1] - TOLERANZ:
            x0, x1, namen = luecken[-1]
            luecken[-1] = (x0, max(x1, r.x1), namen + [name])
        else:
            luecken.append((r.x0, r.x1, [name]))

    def am_rand(namen: List[str], x: float, seite: str) -> Tuple[str, ...]:
        """Die Öffnungen der Lücke, deren Seite ``seite`` -- «x0» oder «x1» -- bei ``x`` liegt."""
        return tuple(n for n in namen if abs(getattr(flaechen[n], seite) - x) <= TOLERANZ)

    ergebnis: List[Pfeiler] = []
    x, links = wand.x0, []
    for x0, x1, namen in [*luecken, (wand.x1, wand.x1, [])]:
        if x0 - x > TOLERANZ:
            ergebnis.append(Pfeiler(f"P{len(ergebnis) + 1}", x, x0, wand.y0, wand.y1,
                                    am_rand(links, x, "x1"), am_rand(namen, x0, "x0")))
        x, links = max(x, x1), namen
    return ergebnis
