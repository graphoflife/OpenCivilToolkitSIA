"""
opencivil/durchstanzen/schnitt.py -- der Nachweisschnitt um die gestützte Fläche.

VERANTWORTUNG:
Aus der gestützten Fläche -- einer Stütze oder dem Ende oder der Ecke einer
Wand --, ihrer Lage in der Platte, den Aussparungen und dem Abstand des
Schnitts der Nachweisschnitt nach SIA 262:2025, 4.3.6.2.2 und 4.3.6.2.3:
welche Teile von ihm zählen, seine wirksame Länge u, die Fläche, die er
umschliesst, und der Schwerpunkt seiner zählenden Teile. Mit der Fläche
zieht der Nachweis die Lasten darin ab (4.3.6.2.6) und rechnet ``b`` für k_e
(4.3.6.2.4), mit dem Schwerpunkt die Exzentrizität e_u. Die Abminderung für
Momente selbst, k_e, ist Sache des Nachweises.

DER SCHNITT (Figur 22):
Im Abstand ``a`` um die gestützte Fläche -- ``d_v/2``, beim äusseren Schnitt
``d_v,out/2`` --, um ihre konvexe Hülle: bei konkaver Geometrie ist der
Umfang zu minimieren (Figur 22c). Eine Stütze ist ein konvexer Kern mit
einem Radius (:class:`Stuetzenflaeche`): ein Rechteck hat den Radius null,
eine Rundstütze einen Punkt als Kern. Ihr Schnitt besteht aus Strecken
parallel zu den Seiten des Kerns und Bögen um seine Ecken (:func:`rundum`).
An einem Wandende und einer Wandecke läuft er um das Ende bzw. um die
äussere Ecke (Figur 23b und c).

WAS NICHT ZÄHLT (Figur 23), kumulativ:

- An grossen gestützten Flächen zählt von einer geraden Strecke des Schnitts
  nur, was höchstens 1.5·d_v von einer Ecke entfernt liegt (Figur 23a bis c).
  Eine Strecke weiss darum, wie weit sie von jedem Ende her zählt
  (:class:`Strecke`); wo eine Wand weiterläuft, zählt sie von dort her nicht.
- Am Plattenrand endet der Schnitt, wenn er dadurch kürzer wird (Figur
  22d). Gerechnet werden die möglichen Schnitte -- der geschlossene und die,
  die zu einem oder zu beiden Rändern laufen --, und es gilt der kürzeste
  (:func:`nachweisschnitt`). Was ausserhalb der Platte liegt, zählt nie.
- Hinter einer Aussparung, die näher als 5·d_v am Schnitt liegt, zählt nicht,
  was zwischen den beiden Strahlen von der Stützenachse an ihr vorbei liegt
  (Figur 23d).

GERECHNET:
Mit Teilstücken von höchstens :data:`TEILSTUECK`: jedes zählt oder nicht, je
nach seiner Mitte. Die Länge ist damit auf Bruchteile eines Millimeters
genau, auch wo Rand, Ecke und Aussparung zusammentreffen, und kein Fall
braucht eine eigene Formel.

EINHEITEN:
m und rad.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Iterator, List, Optional, Sequence, Tuple, Union

from opencivil.querschnitt.geometrie import TOLERANZ, abstand_zur_strecke, flaeche

Punkt = Tuple[float, float]

#: Wie lang ein Teilstück des Schnitts höchstens ist, in m.
TEILSTUECK = 1e-3

#: In wie viele Schritte ein Viertelkreis zerfällt, wo eine Fläche gerechnet wird.
FEIN = 64

#: Wie weit von einer Ecke eine gerade Strecke des Schnitts zählt, in d_v
#: (SIA 262:2025, 4.3.6.2.3, Figur 23a bis c).
ECKENBEREICH = 1.5

#: Wie nahe eine Aussparung dem Schnitt sein muss, damit sie ihn mindert, in
#: d_v (SIA 262:2025, 4.3.6.2.3, Figur 23d).
AUSSPARUNGSABSTAND = 5.0


# ===========================================================================
# Die Stücke des Schnitts
# ===========================================================================


@dataclass(frozen=True)
class Strecke:
    """
    Ein gerades Stück des Schnitts, von ``a`` nach ``b``. Es zählt, was
    höchstens ``zaehlt_a`` von ``a`` oder ``zaehlt_b`` von ``b`` entfernt
    liegt: neben einer Ecke 1.5·d_v (Figur 23), wo eine Wand weiterläuft
    null, sonst unbegrenzt.
    """

    a: Punkt
    b: Punkt
    zaehlt_a: float = math.inf
    zaehlt_b: float = math.inf

    @property
    def laenge(self) -> float:
        return math.dist(self.a, self.b)

    def teile(self) -> Iterator[Tuple[Punkt, Punkt, bool]]:
        """Die Teilstücke, je mit Anfang, Ende und ob es neben einer Ecke liegt und darum zählt."""
        L = self.laenge
        n = max(1, math.ceil(L / TEILSTUECK))
        for i in range(n):
            s0, s1 = L * i / n, L * (i + 1) / n
            s = 0.5 * (s0 + s1)
            yield (_auf(self.a, self.b, s0 / L if L else 0.0),
                   _auf(self.a, self.b, s1 / L if L else 0.0),
                   s <= self.zaehlt_a or L - s <= self.zaehlt_b)

    def punkte(self) -> List[Punkt]:
        return [self.a, self.b]


@dataclass(frozen=True)
class Bogen:
    """Ein Kreisbogen um ``mitte``, gegen den Uhrzeigersinn von ``von`` bis ``bis`` (rad)."""

    mitte: Punkt
    radius: float
    von: float
    bis: float

    @property
    def laenge(self) -> float:
        return self.radius * (self.bis - self.von)

    def punkt(self, winkel: float) -> Punkt:
        return (self.mitte[0] + self.radius * math.cos(winkel),
                self.mitte[1] + self.radius * math.sin(winkel))

    def teile(self) -> Iterator[Tuple[Punkt, Punkt, bool]]:
        n = max(1, math.ceil(self.laenge / TEILSTUECK))
        for i in range(n):
            w0 = self.von + (self.bis - self.von) * i / n
            w1 = self.von + (self.bis - self.von) * (i + 1) / n
            yield self.punkt(w0), self.punkt(w1), True

    def punkte(self, schritte: int = 16) -> List[Punkt]:
        n = max(1, math.ceil(schritte * (self.bis - self.von) / (math.pi / 2)))
        return [self.punkt(self.von + (self.bis - self.von) * i / n) for i in range(n + 1)]


Stueck = Union[Strecke, Bogen]


def _auf(a: Punkt, b: Punkt, t: float) -> Punkt:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


@dataclass(frozen=True)
class Halbebene:
    """Die Seite einer Geraden, auf der die Platte liegt: ``n · p <= c``."""

    n: Punkt
    c: float

    def enthaelt(self, p: Punkt) -> bool:
        return self.n[0] * p[0] + self.n[1] * p[1] <= self.c + TOLERANZ


# ===========================================================================
# Die gestützte Fläche
# ===========================================================================


@dataclass(frozen=True)
class Stuetzenflaeche:
    """
    Eine Stütze: ein konvexer Kern -- Polygon gegen den Uhrzeigersinn, Strecke
    oder Punkt -- mit einem Radius darum. Ein Rechteck ist sein eigener Kern
    mit Radius null; eine Rundstütze ein Punkt mit dem halben Durchmesser.
    """

    kern: Tuple[Punkt, ...]
    radius: float = 0.0

    @property
    def achse(self) -> Punkt:
        """Die Stützenachse: der Schwerpunkt des Kerns."""
        if len(self.kern) < 3:
            n = len(self.kern)
            return (sum(p[0] for p in self.kern) / n, sum(p[1] for p in self.kern) / n)
        A = flaeche(self.kern)
        sx = sy = 0.0
        for (x1, y1), (x2, y2) in zip(self.kern, self.kern[1:] + self.kern[:1]):
            k = x1 * y2 - x2 * y1
            sx += (x1 + x2) * k
            sy += (y1 + y2) * k
        return (sx / (6.0 * A), sy / (6.0 * A))

    def umriss(self, schritte: int = 16) -> List[Punkt]:
        """Der Umriss der Stütze als Polygon -- fürs Bild und für Prüfungen."""
        return _polygon(rundum(self.kern, self.radius), schritte)

    def grenzen(self) -> Tuple[float, float, float, float]:
        """``(x_min, y_min, x_max, y_max)`` der Stütze."""
        xs = [p[0] for p in self.kern]
        ys = [p[1] for p in self.kern]
        r = self.radius
        return min(xs) - r, min(ys) - r, max(xs) + r, max(ys) + r


def rundum(kern: Sequence[Punkt], radius: float,
           zaehlt: Callable[[Punkt, Punkt], Tuple[float, float]] = lambda p, q: (math.inf, math.inf),
           ) -> List[Stueck]:
    """
    Der Rand des Kerns, um ``radius`` nach aussen gerückt: je Seite eine
    Strecke, je Ecke ein Bogen, gegen den Uhrzeigersinn. Ein Punkt gibt einen
    Kreis, eine Strecke zwei Strecken und zwei Halbkreise. ``zaehlt`` sagt je
    Seite ``p → q`` des Kerns, wie weit ihre Strecke von jedem Ende her zählt.
    """
    kern = list(kern)
    if len(kern) == 1:
        return [Bogen(kern[0], radius, 0.0, 2.0 * math.pi)]
    stuecke: List[Stueck] = []
    n = len(kern)
    for i in range(n):
        p, q, r = kern[i], kern[(i + 1) % n], kern[(i + 2) % n]
        n1, n2 = _normale(p, q), _normale(q, r)
        za, zb = zaehlt(p, q)
        stuecke.append(Strecke((p[0] + radius * n1[0], p[1] + radius * n1[1]),
                               (q[0] + radius * n1[0], q[1] + radius * n1[1]), za, zb))
        von = math.atan2(n1[1], n1[0])
        bis = math.atan2(n2[1], n2[0])
        while bis < von - 1e-12:
            bis += 2.0 * math.pi
        if bis - von > 1e-12:
            stuecke.append(Bogen(q, radius, von, bis))
    return stuecke


def _normale(p: Punkt, q: Punkt) -> Punkt:
    """Die Normale der Seite ``p → q`` nach aussen, für ein Polygon gegen den Uhrzeigersinn."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy)
    return (dy / L, -dx / L)


def konvexe_huelle(punkte: Sequence[Punkt]) -> Tuple[Punkt, ...]:
    """Die konvexe Hülle gegen den Uhrzeigersinn -- bei weniger als drei Ecken die Punkte selbst."""
    p = sorted(set(punkte))
    if len(p) <= 2:
        return tuple(p)

    def kreuz(o: Punkt, a: Punkt, b: Punkt) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    unten: List[Punkt] = []
    for q in p:
        while len(unten) >= 2 and kreuz(unten[-2], unten[-1], q) <= 1e-15:
            unten.pop()
        unten.append(q)
    oben: List[Punkt] = []
    for q in reversed(p):
        while len(oben) >= 2 and kreuz(oben[-2], oben[-1], q) <= 1e-15:
            oben.pop()
        oben.append(q)
    return tuple(unten[:-1] + oben[:-1])


def _polygon(stuecke: Sequence[Stueck], schritte: int = 16) -> List[Punkt]:
    """Die Stücke als geschlossenes Polygon -- die Endpunkte, Bögen in feinen Schritten."""
    punkte: List[Punkt] = []
    for s in stuecke:
        neu = s.punkte(schritte) if isinstance(s, Bogen) else s.punkte()
        for q in neu:
            if not punkte or math.dist(punkte[-1], q) > 1e-12:
                punkte.append(q)
    if len(punkte) > 1 and math.dist(punkte[0], punkte[-1]) <= 1e-12:
        punkte.pop()
    return punkte


# ===========================================================================
# Die Kandidaten: der geschlossene Schnitt und die zum Rand
# ===========================================================================


@dataclass(frozen=True)
class Kandidat:
    """
    Ein möglicher Schnitt: seine Stücke, die Platte, in der er gilt, das
    Polygon der Fläche, die er umschliesst, und wie er heisst.
    """

    name: str
    stuecke: Tuple[Stueck, ...]
    platte: Tuple[Halbebene, ...]
    umschlossen: Tuple[Punkt, ...]
    raender: int = 0
    """Zu wie vielen Plattenrändern er läuft."""


def kandidaten_stuetze(stuetze: Stuetzenflaeche, abstand: float, eckenbereich: float,
                       raender: Sequence[Halbebene] = ()) -> List[Kandidat]:
    """
    Die möglichen Schnitte um eine Stütze im Abstand ``abstand``: der
    geschlossene und, je Teilmenge der Plattenränder, der Schnitt, der zu
    diesen Rändern läuft (Figur 22d). Zum Rand verlängert wird der Kern: er
    reicht dann bis über den Rand hinaus, und was jenseits liegt, zählt nicht.

    Eine Strecke entlang einer Seite der Stütze zählt ``eckenbereich`` von
    jeder Ecke her (1.5·d_v, Figur 23a); eine, die zum Rand läuft, ganz --
    am freien Rand ballt sich keine Querkraft.
    """
    R = stuetze.radius + abstand
    raender = tuple(raender)
    eigene = set(stuetze.kern)

    def zaehlt(p: Punkt, q: Punkt) -> Tuple[float, float]:
        if p in eigene and q in eigene:
            return eckenbereich, eckenbereich
        return math.inf, math.inf

    ergebnis: List[Kandidat] = []
    teilmengen = [()] + [tuple(r for j, r in enumerate(raender) if maske & (1 << j))
                         for maske in range(1, 1 << len(raender))]
    for zum_rand in teilmengen:
        kern = list(stuetze.kern)
        for h in zum_rand:
            # Der Kern rückt weit über den Rand hinaus: was jenseits liegt,
            # zählt nicht, und so kommt kein Bogen mehr in die Platte.
            weit = _abstand_zum_rand(stuetze, h) + R + 1.0
            kern = kern + [(p[0] + weit * h.n[0], p[1] + weit * h.n[1]) for p in kern]
        stuecke = rundum(konvexe_huelle(kern), R, zaehlt)
        name = ("geschlossen" if not zum_rand
                else "zum Rand" if len(zum_rand) == 1 else "zu beiden Rändern")
        umschlossen = _abschneiden(_polygon(stuecke, FEIN), raender)
        ergebnis.append(Kandidat(name, tuple(stuecke), raender, tuple(umschlossen),
                                 len(zum_rand)))
    return ergebnis


def _abstand_zum_rand(stuetze: Stuetzenflaeche, h: Halbebene) -> float:
    """Wie weit die Stütze vom Rand entfernt ist -- in Richtung seiner Normalen."""
    return max(0.0, min(h.c - (h.n[0] * p[0] + h.n[1] * p[1]) for p in stuetze.kern)
               - stuetze.radius)


def kandidat_wandende(dicke: float, abstand: float, d_v: float) -> Kandidat:
    """
    Der Schnitt um das Ende einer Wand der Dicke ``dicke`` (Figur 23b): das
    Ende liegt bei x = 0, die Wand läuft nach +x weiter. Entlang der Wand zählt
    er 1.5·d_v vom Ende her, um das Ende ganz.
    """
    a, t = abstand, dicke
    L = ECKENBEREICH * d_v
    lang = L + 2.0 * d_v
    stuecke = (
        Strecke((lang, -t / 2 - a), (0.0, -t / 2 - a), zaehlt_a=0.0, zaehlt_b=L),
        Bogen((0.0, -t / 2), a, math.pi, 1.5 * math.pi) if a > 0 else None,
        Strecke((-a, -t / 2), (-a, t / 2)),
        Bogen((0.0, t / 2), a, 0.5 * math.pi, math.pi) if a > 0 else None,
        Strecke((0.0, t / 2 + a), (lang, t / 2 + a), zaehlt_a=L, zaehlt_b=0.0),
    )
    stuecke = tuple(s for s in stuecke if s is not None)
    umschlossen = _polygon([
        Strecke((L, -t / 2 - a), (0.0, -t / 2 - a)),
        *([Bogen((0.0, -t / 2), a, math.pi, 1.5 * math.pi)] if a > 0 else []),
        Strecke((-a, -t / 2), (-a, t / 2)),
        *([Bogen((0.0, t / 2), a, 0.5 * math.pi, math.pi)] if a > 0 else []),
        Strecke((0.0, t / 2 + a), (L, t / 2 + a)),
    ], FEIN)
    return Kandidat("um das Wandende", stuecke, (), tuple(_rechtsrum(umschlossen)))


def kandidat_wandecke(dicke: float, abstand: float, d_v: float) -> Kandidat:
    """
    Der Schnitt um die äussere Ecke zweier Wände der Dicke ``dicke`` (Figur
    23c): die Ecke liegt im Ursprung, die Wände laufen nach +x und nach +y,
    die Platte liegt aussen. Entlang jeder Wand zählt er 1.5·d_v von der Ecke.
    """
    a = abstand
    L = ECKENBEREICH * d_v
    lang = L + 2.0 * d_v
    stuecke = tuple(s for s in (
        Strecke((-a, lang), (-a, 0.0), zaehlt_a=0.0, zaehlt_b=L),
        Bogen((0.0, 0.0), a, math.pi, 1.5 * math.pi) if a > 0 else None,
        Strecke((0.0, -a), (lang, -a), zaehlt_a=L, zaehlt_b=0.0),
    ) if s is not None)
    umschlossen = _polygon([
        Strecke((L, 0.0), (0.0, 0.0)),
        Strecke((0.0, 0.0), (0.0, L)),
        Strecke((0.0, L), (-a, L)),
        Strecke((-a, L), (-a, 0.0)),
        *([Bogen((0.0, 0.0), a, math.pi, 1.5 * math.pi)] if a > 0 else []),
        Strecke((0.0, -a), (L, -a)),
    ], FEIN)
    return Kandidat("um die Wandecke", stuecke, (), tuple(_rechtsrum(umschlossen)))


def _rechtsrum(punkte: Sequence[Punkt]) -> List[Punkt]:
    """Das Polygon gegen den Uhrzeigersinn."""
    punkte = list(punkte)
    return punkte if flaeche(punkte) >= 0.0 else punkte[::-1]


def _abschneiden(polygon: Sequence[Punkt], halbebenen: Sequence[Halbebene]) -> List[Punkt]:
    """Das Polygon, auf die Halbebenen beschnitten (Sutherland-Hodgman)."""
    ergebnis = list(polygon)
    for h in halbebenen:
        if not ergebnis:
            break
        neu: List[Punkt] = []
        for i, p in enumerate(ergebnis):
            q = ergebnis[(i + 1) % len(ergebnis)]
            fp = h.n[0] * p[0] + h.n[1] * p[1] - h.c
            fq = h.n[0] * q[0] + h.n[1] * q[1] - h.c
            if fp <= 0.0:
                neu.append(p)
            if (fp < 0.0 < fq) or (fq < 0.0 < fp):
                t = fp / (fp - fq)
                neu.append(_auf(p, q, t))
        ergebnis = neu
    return ergebnis


# ===========================================================================
# Aussparungen
# ===========================================================================


@dataclass(frozen=True)
class Schatten:
    """
    Was eine Aussparung vom Schnitt wegnimmt: der Winkelbereich zwischen den
    beiden Strahlen von der Stützenachse an ihr vorbei (Figur 23d), gegen den
    Uhrzeigersinn von ``von`` bis ``bis``.
    """

    von: float
    bis: float

    def enthaelt(self, winkel: float) -> bool:
        w = (winkel - self.von) % (2.0 * math.pi)
        return w <= (self.bis - self.von) + 1e-12


def schatten(aussparung: Sequence[Punkt], achse: Punkt) -> Schatten:
    """
    Der Winkelbereich, den die Aussparung von der Achse aus verdeckt: der
    kleinste Bogen, der die Richtungen zu allen ihren Ecken enthält.
    """
    winkel = sorted(math.atan2(p[1] - achse[1], p[0] - achse[0]) % (2.0 * math.pi)
                    for p in aussparung)
    # Die grösste Lücke zwischen zwei Richtungen liegt ausserhalb.
    luecken = [(winkel[(i + 1) % len(winkel)] - w) % (2.0 * math.pi) for i, w in enumerate(winkel)]
    i = max(range(len(luecken)), key=lambda j: luecken[j])
    von = winkel[(i + 1) % len(winkel)]
    bis = von + (2.0 * math.pi - luecken[i])
    return Schatten(von, bis)


def abstand_zum_schnitt(aussparung: Sequence[Punkt], stuecke: Sequence[Stueck]) -> float:
    """Der kleinste Abstand zwischen der Aussparung und dem Schnitt -- auf 1 cm genau genügt."""
    kanten = list(zip(aussparung, list(aussparung[1:]) + list(aussparung[:1])))
    bester = math.inf
    for s in stuecke:
        punkte = s.punkte(64) if isinstance(s, Bogen) else [
            _auf(s.a, s.b, i / max(1, math.ceil(s.laenge / 0.01)))
            for i in range(max(1, math.ceil(s.laenge / 0.01)) + 1)]
        for p in punkte:
            for a, b in kanten:
                bester = min(bester, abstand_zur_strecke(p, a, b))
    return bester


# ===========================================================================
# Auswerten
# ===========================================================================


@dataclass(frozen=True)
class Linienzug:
    """Ein Stück des Schnitts fürs Bild: seine Punkte und ob es zählt."""

    punkte: Tuple[Punkt, ...]
    zaehlt: bool


@dataclass(frozen=True)
class Auswertung:
    """
    Was ein Kandidat ergibt. Längen in m: in der Platte, was davon an Ecken
    grosser Flächen und hinter Aussparungen nicht zählt, und die wirksame
    Länge ``u``. Dazu die umschlossene Fläche, ohne Aussparungen, der
    Schwerpunkt der zählenden Teile und die Linien fürs Bild.
    """

    kandidat: Kandidat
    in_der_platte: float
    an_ecken: float
    hinter_aussparungen: float
    flaeche: float
    flaeche_ohne_aussparungen: float
    schwerpunkt: Punkt
    linien: Tuple[Linienzug, ...]

    @property
    def u(self) -> float:
        return self.in_der_platte - self.an_ecken - self.hinter_aussparungen


def auswerten(kandidat: Kandidat, *, d_v: float, achse: Punkt,
              aussparungen: Sequence[Sequence[Punkt]] = ()) -> Auswertung:
    """
    Welche Teile des Kandidaten zählen -- in der Platte, neben einer Ecke und
    nicht hinter einer Aussparung, die näher als 5·d_v liegt.
    """
    nahe = [a for a in aussparungen
            if abstand_zum_schnitt(a, kandidat.stuecke) < AUSSPARUNGSABSTAND * d_v]
    schatten_ = [schatten(a, achse) for a in nahe]
    in_platte = an_ecken = hinter = 0.0
    sx = sy = s_l = 0.0
    linien: List[Linienzug] = []
    for stueck in kandidat.stuecke:
        lauf: List[Punkt] = []
        zaehlt_lauf: Optional[bool] = None
        for p, q, neben_ecke in stueck.teile():
            m = (0.5 * (p[0] + q[0]), 0.5 * (p[1] + q[1]))
            l = math.dist(p, q)
            drin = all(h.enthaelt(m) for h in kandidat.platte)
            verdeckt = drin and neben_ecke and any(
                s.enthaelt(math.atan2(m[1] - achse[1], m[0] - achse[0])) for s in schatten_)
            if drin:
                in_platte += l
                if not neben_ecke:
                    an_ecken += l
                elif verdeckt:
                    hinter += l
            zaehlt = drin and neben_ecke and not verdeckt
            if zaehlt:
                sx += l * m[0]
                sy += l * m[1]
                s_l += l
            if not drin:
                if lauf:
                    linien.append(Linienzug(tuple(lauf), bool(zaehlt_lauf)))
                lauf, zaehlt_lauf = [], None
                continue
            if zaehlt_lauf is None or zaehlt_lauf != zaehlt:
                if lauf:
                    linien.append(Linienzug(tuple(lauf + [p]), bool(zaehlt_lauf)))
                lauf, zaehlt_lauf = [p], zaehlt
            lauf.append(q)
        if lauf:
            linien.append(Linienzug(tuple(_vereinfacht(lauf)), bool(zaehlt_lauf)))
    A = abs(flaeche(kandidat.umschlossen)) if len(kandidat.umschlossen) >= 3 else 0.0
    ohne = A - sum(_ueberlappung(a, kandidat.umschlossen) for a in aussparungen)
    schwerpunkt = (sx / s_l, sy / s_l) if s_l > 0.0 else achse
    return Auswertung(kandidat, in_platte, an_ecken, hinter, A, max(0.0, ohne), schwerpunkt,
                      tuple(Linienzug(tuple(_vereinfacht(l.punkte)), l.zaehlt) for l in linien))


def _vereinfacht(punkte: Sequence[Punkt], toleranz: float = 2e-4) -> List[Punkt]:
    """
    Fast gerade Folgen von Punkten auf ihre Ecken gekürzt -- fürs Bild genügt
    das. Nach Douglas und Peucker: kein weggelassener Punkt liegt weiter als
    ``toleranz`` von der Linie, die bleibt. Bis 2026-10-30 wurde nur mit dem
    nächsten Punkt verglichen, und ein Bogen wurde zum Vieleck.
    """
    punkte = list(punkte)
    if len(punkte) <= 2:
        return punkte
    behalten = [False] * len(punkte)
    behalten[0] = behalten[-1] = True
    offen = [(0, len(punkte) - 1)]
    while offen:
        a, b = offen.pop()
        weitester, j = toleranz, None
        for i in range(a + 1, b):
            d = abstand_zur_strecke(punkte[i], punkte[a], punkte[b])
            if d > weitester:
                weitester, j = d, i
        if j is not None:
            behalten[j] = True
            offen += [(a, j), (j, b)]
    return [p for p, ja in zip(punkte, behalten) if ja]


def _ueberlappung(aussparung: Sequence[Punkt], umschlossen: Sequence[Punkt]) -> float:
    """Wie viel der Aussparung in der umschlossenen Fläche liegt -- die ist konvex."""
    if len(umschlossen) < 3:
        return 0.0
    umschlossen = _rechtsrum(umschlossen)
    halbebenen = []
    for p, q in zip(umschlossen, umschlossen[1:] + umschlossen[:1]):
        nx, ny = _normale(p, q)
        halbebenen.append(Halbebene((nx, ny), nx * p[0] + ny * p[1]))
    teil = _abschneiden(list(aussparung), halbebenen)
    return abs(flaeche(teil)) if len(teil) >= 3 else 0.0


@dataclass(frozen=True)
class Nachweisschnitt:
    """Der massgebende Schnitt -- der kürzeste der Kandidaten -- und alle, die gerechnet wurden."""

    massgebend: Auswertung
    alle: Tuple[Auswertung, ...] = field(default_factory=tuple)

    @property
    def u(self) -> float:
        return self.massgebend.u


def nachweisschnitt(kandidaten: Sequence[Kandidat], *, d_v: float, achse: Punkt,
                    aussparungen: Sequence[Sequence[Punkt]] = ()) -> Nachweisschnitt:
    """
    Alle Kandidaten ausgewertet; es gilt der mit der kleinsten wirksamen Länge
    (Figur 22d). Sind zwei gleich lang -- die Stütze steht am Rand --, heisst
    er nach dem, der zum Rand läuft.
    """
    alle = tuple(auswerten(k, d_v=d_v, achse=achse, aussparungen=aussparungen)
                 for k in kandidaten)
    kuerzeste = min(a.u for a in alle)
    massgebend = max((a for a in alle if a.u <= kuerzeste + 1e-6), key=lambda a: a.kandidat.raender)
    return Nachweisschnitt(massgebend, alle)
