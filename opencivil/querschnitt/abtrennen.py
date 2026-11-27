"""
opencivil/querschnitt/abtrennen.py -- was ein Schnitt vom Querschnitt abtrennt.

VERANTWORTUNG:
Ein Schnitt ist eine Strecke quer durch den gezeichneten Querschnitt, mit
einem Pfeil zu einer ihrer Seiten. Abgetrennt ist, was auf der Seite des
Pfeils an der Strecke liegt und mit dem Rest nur ueber sie zusammenhaengt
(:func:`abtrennen`): beim Plattenbalken der Flansch neben dem Steg, bei einer
Aufdopplung der Aufbeton ueber der Fuge, beim Verbundtraeger die Platte ueber
dem Profil. Dazu die Laenge ``b_i``, ueber die der Schnitt Material von
Material trennt, und welche Staebe und welche Stuecke einer verschmierten
Linie im abgetrennten Teil liegen (:class:`Abgetrennt`).

WIE GETEILT WIRD:
In Streifen parallel zum Schnitt, ihre Grenzen auf jeder Ecke und auf der
Geraden des Schnitts. Zwischen zwei Grenzen liegt keine Ecke, jede Kante
quert einen Streifen ganz: je Streifen zerfaellt der Querschnitt in Trapeze,
jedes aus dem Material des innersten Polygons dort -- wie in den Fasern,
wo ein Polygon im anderen dieses ersetzt. Zwei Trapeze haengen zusammen, wo
sie ein Stueck Rand gemeinsam haben, laenger als
:data:`~opencivil.querschnitt.geometrie.TOLERANZ`; ein Punkt genuegt nicht,
wie bei :func:`~opencivil.querschnitt.geometrie.beruehren`. Auf der Geraden
des Schnitts zaehlt nur, was ausserhalb der Strecke liegt: auf ihr trennt
er.

So gilt jede Lage der Strecke ohne Sonderfall -- an einer Ecke, laengs
einer Kante, laengs der Grenze zweier Polygone, ueber den Rand hinaus.
Endet sie im Material oder geht sie nur durch eine Wand eines Kastens,
haengt der Teil jenseits noch am Rest: dann trennt sie nichts ab, und der
Satz dazu sagt es (:data:`NICHT_GETRENNT`).

``b_i`` ist die Laenge, auf der beidseits der Strecke Material liegt -- ueber
eine Aussparung oder den Rand hinaus zaehlt sie nicht.

EINHEITEN:
Die der Punkte, wie in :mod:`~opencivil.querschnitt.geometrie` -- in der
Zeichnung Millimeter.

Ein gezeichneter Schnitt mit Name und Kennung ist ein :class:`Schnitt`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Tuple, Union

from opencivil.querschnitt.geometrie import TOLERANZ, Punkt, flaeche

#: Warum ein Schnitt nichts abtrennt -- Satzteile ohne Punkt, fuer die
#: Zeichnung und die Herleitung.
OHNE_LAENGE = "er hat keine Länge"
OHNE_MATERIAL = "er trennt nirgends Material von Material – er muss durch den Querschnitt gehen"
NICHT_GETRENNT = ("der Teil auf der Seite des Pfeils hängt noch ausserhalb der Strecke am Rest "
                  "– sie muss ganz durch den Querschnitt gehen")


#: Wie eine Richtung im Bild heisst, je Achtel des Kreises ab y, gegen den
#: Uhrzeigersinn -- z zeigt nach oben.
RICHTUNGEN = ("nach rechts", "nach rechts oben", "nach oben", "nach links oben", "nach links",
              "nach links unten", "nach unten", "nach rechts unten")


@dataclass(frozen=True)
class Stueck:
    """Ein Trapez des abgetrennten Teils, aus dem Material eines Polygons -- Ecken in der Ebene."""

    polygon: int
    """Der Index des Polygons, dessen Material hier gilt -- das innerste."""

    punkte: Tuple[Punkt, ...]


@dataclass(frozen=True)
class Abgetrennt:
    """
    Was ein Schnitt abtrennt: die Stuecke aus Material, die Laenge ``b_i`` und
    die Lage des Schnitts, um Punkte und Strecken zuzuordnen.
    """

    stuecke: Tuple[Stueck, ...]
    breite: float
    """``b_i``: wie lang der Schnitt Material von Material trennt."""

    von: Punkt
    t: Punkt
    """Die Richtung der Strecke, ein Einheitsvektor."""

    n: Punkt
    """Die Seite des Pfeils, ein Einheitsvektor senkrecht zur Strecke."""

    laenge: float

    @property
    def flaeche(self) -> float:
        """Die Flaeche des abgetrennten Teils."""
        return sum(abs(flaeche(s.punkte)) for s in self.stuecke)

    @property
    def polygone(self) -> Tuple[int, ...]:
        """Die Polygone, von denen etwas abgetrennt ist, in ihrer Folge."""
        return tuple(sorted({s.polygon for s in self.stuecke}))

    def _uw(self, p: Punkt) -> Tuple[float, float]:
        d = (p[0] - self.von[0], p[1] - self.von[1])
        return (d[0] * self.t[0] + d[1] * self.t[1], d[0] * self.n[0] + d[1] * self.n[1])

    def auf_dem_schnitt(self, p: Punkt) -> bool:
        """Ob ``p`` auf der Strecke liegt -- ein Stab dort zaehlt zum Rest."""
        u, w = self._uw(p)
        return abs(w) <= TOLERANZ and -TOLERANZ <= u <= self.laenge + TOLERANZ

    def enthaelt(self, p: Punkt) -> bool:
        """Ob ``p`` im abgetrennten Teil liegt, auf seinem Rand -- nicht auf dem Schnitt."""
        if self.auf_dem_schnitt(p):
            return False
        return any(_im_trapez(p, s.punkte) for s in self.stuecke)

    def strecke_teilen(self, a: Punkt, b: Punkt) -> List[Tuple[Punkt, Punkt]]:
        """
        Die Teile der Strecke ``a``–``b`` im abgetrennten Teil. Geteilt wird
        nur am Schnitt: anderswo grenzt der abgetrennte Teil an kein Material
        des Rests.
        """
        (u_a, w_a), (u_b, w_b) = self._uw(a), self._uw(b)
        teile = [(a, b)]
        if (w_a > TOLERANZ and w_b < -TOLERANZ) or (w_a < -TOLERANZ and w_b > TOLERANZ):
            anteil = w_a / (w_a - w_b)
            if -TOLERANZ <= u_a + anteil * (u_b - u_a) <= self.laenge + TOLERANZ:
                c = (a[0] + anteil * (b[0] - a[0]), a[1] + anteil * (b[1] - a[1]))
                teile = [(a, c), (c, b)]
        return [(p, q) for p, q in teile
                if self.enthaelt(((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0))]


def _im_trapez(p: Punkt, ecken: Sequence[Punkt]) -> bool:
    """Ob ``p`` im konvexen Vieleck ``ecken`` liegt, Rand eingeschlossen."""
    vorzeichen = 0
    n = len(ecken)
    for i in range(n):
        a, b = ecken[i], ecken[(i + 1) % n]
        laenge = math.hypot(b[0] - a[0], b[1] - a[1])
        if laenge <= TOLERANZ:
            continue
        kreuz = ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / laenge
        if abs(kreuz) <= TOLERANZ:
            continue
        seite = 1 if kreuz > 0 else -1
        if vorzeichen and seite != vorzeichen:
            return False
        vorzeichen = seite
    return True


@dataclass
class _Trapez:
    """Ein Trapez eines Streifens, in den Koordinaten des Schnitts: u laengs, w quer."""

    streifen: int
    unten: float
    oben: float
    links: Tuple[float, float]
    """u des linken Rands unten und oben."""

    rechts: Tuple[float, float]
    polygon: int


def _ebenen(wert_w: Sequence[float]) -> List[float]:
    """
    Die Grenzen der Streifen: jedes w einer Ecke und die Gerade des Schnitts,
    naeher als :data:`TOLERANZ` beieinander als eine -- die Null bleibt null.
    """
    ebenen: List[float] = []
    for w in sorted(set(wert_w) | {0.0}):
        if ebenen and w - ebenen[-1] <= TOLERANZ:
            if w == 0.0:
                ebenen[-1] = 0.0
            continue
        ebenen.append(w)
    return ebenen


def _streifen(uw: Sequence[Sequence[Punkt]], tiefe: Sequence[int], traegt: Sequence[bool],
              unten: float, oben: float, k: int) -> List[Optional[_Trapez]]:
    """
    Die Trapeze eines Streifens, von links nach rechts -- je Abschnitt
    zwischen zwei Kanten eines, ``None``, wo dort kein Material liegt und der
    Abschnitt breiter ist als :data:`TOLERANZ`. Ein Abschnitt ohne Breite
    zwischen zwei Kanten, die aufeinander liegen, faellt weg: die Trapeze
    beiderseits beruehren sich.
    """
    mitte = (unten + oben) / 2.0
    kanten: List[Tuple[float, float, float, int]] = []
    for i, ecken in enumerate(uw):
        for j in range(len(ecken)):
            (u_a, w_a), (u_b, w_b) = ecken[j], ecken[(j + 1) % len(ecken)]
            if (w_a - mitte) * (w_b - mitte) >= 0.0:
                continue
            neigung = (u_b - u_a) / (w_b - w_a)
            kanten.append((u_a + (mitte - w_a) * neigung, u_a + (unten - w_a) * neigung,
                           u_a + (oben - w_a) * neigung, i))
    kanten.sort()
    innen = [False] * len(uw)
    folge: List[Optional[_Trapez]] = []
    for links, rechts in zip(kanten, kanten[1:]):
        innen[links[3]] = not innen[links[3]]
        if rechts[0] - links[0] <= TOLERANZ:
            continue
        drin = [i for i, ja in enumerate(innen) if ja]
        innerstes = max(drin, key=lambda i: tiefe[i]) if drin else None
        if innerstes is None or not traegt[innerstes]:
            folge.append(None)
        else:
            folge.append(_Trapez(k, unten, oben, (links[1], links[2]),
                                 (rechts[1], rechts[2]), innerstes))
    return folge


def _lage(von: Punkt, bis: Punkt, links: bool) -> Optional[Tuple[Punkt, Punkt, float]]:
    """
    Richtung ``t`` und Seite ``n`` der Strecke, je ein Einheitsvektor, und
    ihre Laenge -- ``n`` links von ihr, in ihrer Richtung gesehen, oder
    rechts. Ohne Laenge nichts.
    """
    laenge = math.hypot(bis[0] - von[0], bis[1] - von[1])
    if laenge <= TOLERANZ:
        return None
    t = ((bis[0] - von[0]) / laenge, (bis[1] - von[1]) / laenge)
    return t, ((-t[1], t[0]) if links else (t[1], -t[0])), laenge


def abtrennen(polygone: Sequence[Sequence[Punkt]], traegt: Sequence[bool],
              eltern: Sequence[Optional[int]], von: Punkt, bis: Punkt, *,
              links: bool = True) -> Union[Abgetrennt, str]:
    """
    Was die Strecke von ``von`` nach ``bis`` abtrennt -- auf ihrer linken
    Seite, in Richtung ``von`` → ``bis`` gesehen, sonst auf der rechten. Trennt
    sie nichts ab, ein Satzteil, warum. ``traegt`` sagt je Polygon, ob es
    Material hat, ``eltern``, in welchem es liegt
    (:func:`~opencivil.querschnitt.geometrie.verschachteln`).
    """
    lage = _lage(von, bis, links)
    if lage is None:
        return OHNE_LAENGE
    t, n, laenge = lage

    def nach_uw(p: Punkt) -> Punkt:
        d = (p[0] - von[0], p[1] - von[1])
        w = d[0] * n[0] + d[1] * n[1]
        return (d[0] * t[0] + d[1] * t[1], 0.0 if abs(w) <= TOLERANZ else w)

    uw = [[nach_uw(p) for p in ecken] for ecken in polygone]
    tiefe = []
    for i in range(len(polygone)):
        j, d = i, 0
        while eltern[j] is not None:
            j, d = eltern[j], d + 1
        tiefe.append(d)
    ebenen = _ebenen([w for ecken in uw for _, w in ecken])

    # -- Je Streifen die Trapeze; nebeneinander haengen sie zusammen ---------
    trapeze: List[_Trapez] = []
    je_streifen: List[List[int]] = []
    gruppe: Dict[int, int] = {}

    def finde(i: int) -> int:
        while gruppe[i] != i:
            gruppe[i] = gruppe[gruppe[i]]
            i = gruppe[i]
        return i

    def verbinden(a: int, b: int) -> None:
        ga, gb = finde(a), finde(b)
        if ga != gb:
            gruppe[max(ga, gb)] = min(ga, gb)

    for k, (unten, oben) in enumerate(zip(ebenen, ebenen[1:])):
        hier: List[int] = []
        vorher: Optional[int] = None
        for trapez in _streifen(uw, tiefe, traegt, unten, oben, k):
            if trapez is None:
                vorher = None
                continue
            i = len(trapeze)
            trapeze.append(trapez)
            gruppe[i] = i
            hier.append(i)
            if vorher is not None:
                verbinden(vorher, i)
            vorher = i
        je_streifen.append(hier)

    # -- Uebereinander: ueber ein gemeinsames Stueck Rand, am Schnitt nur ausserhalb
    abgetrennt_an: List[int] = []
    rest_an: List[int] = []
    breite = 0.0
    for k in range(len(je_streifen) - 1):
        am_schnitt = ebenen[k + 1] == 0.0
        for a in je_streifen[k]:
            ta = trapeze[a]
            for b in je_streifen[k + 1]:
                tb = trapeze[b]
                von_u = max(ta.links[1], tb.links[0])
                bis_u = min(ta.rechts[1], tb.rechts[0])
                if bis_u - von_u <= TOLERANZ:
                    continue
                if not am_schnitt:
                    verbinden(a, b)
                    continue
                gedeckt = max(0.0, min(bis_u, laenge) - max(von_u, 0.0))
                if (bis_u - von_u) - gedeckt > TOLERANZ:
                    verbinden(a, b)
                if gedeckt > TOLERANZ:
                    breite += gedeckt
                    rest_an.append(a)
                    abgetrennt_an.append(b)

    if not abgetrennt_an:
        return OHNE_MATERIAL
    gruppen = {finde(i) for i in abgetrennt_an}
    if gruppen & {finde(i) for i in rest_an}:
        return NICHT_GETRENNT

    def zurueck(u: float, w: float) -> Punkt:
        return (von[0] + u * t[0] + w * n[0], von[1] + u * t[1] + w * n[1])

    stuecke = []
    for i, tr in enumerate(trapeze):
        if finde(i) not in gruppen:
            continue
        ecken: List[Punkt] = []
        for u, w in ((tr.links[0], tr.unten), (tr.rechts[0], tr.unten),
                     (tr.rechts[1], tr.oben), (tr.links[1], tr.oben)):
            p = zurueck(u, w)
            if not ecken or math.hypot(p[0] - ecken[-1][0], p[1] - ecken[-1][1]) > TOLERANZ:
                ecken.append(p)
        if len(ecken) > 1 and math.hypot(ecken[0][0] - ecken[-1][0],
                                         ecken[0][1] - ecken[-1][1]) <= TOLERANZ:
            ecken.pop()
        if len(ecken) >= 3:
            stuecke.append(Stueck(polygon=tr.polygon, punkte=tuple(ecken)))
    return Abgetrennt(stuecke=tuple(stuecke), breite=breite, von=von, t=t, n=n, laenge=laenge)


@dataclass(frozen=True)
class Schnitt:
    """
    Ein Schnitt der Zeichnung: die Strecke von ``von`` nach ``bis``, in mm,
    der Pfeil links von ihr, in ihrer Richtung gesehen -- mit ``links``
    falsch rechts.
    """

    name: str
    kennung: str
    von: Punkt
    bis: Punkt
    links: bool

    def abtrennen(self, polygone: Sequence[Sequence[Punkt]], traegt: Sequence[bool],
                  eltern: Sequence[Optional[int]]) -> Union[Abgetrennt, str]:
        """Was er von diesen Polygonen abtrennt -- siehe :func:`abtrennen`."""
        return abtrennen(polygone, traegt, eltern, self.von, self.bis, links=self.links)

    def nichts_abgetrennt(self, grund: str) -> str:
        """Der Satz, dass er nichts abtrennt, mit dem Grund -- ueberall derselbe."""
        return f"{self.name} trennt nichts ab: {grund}."

    def pfeil(self, links: bool) -> str:
        """
        Wohin sein Pfeil auf dieser Seite zeigt, in Worten -- «nach oben»,
        «nach rechts unten» (:data:`RICHTUNGEN`): fuer den Schalter der
        Seite. Links und rechts der Richtung, in der er gezeichnet ist, sieht
        man im Bild nicht mehr. Ohne Laenge leer.
        """
        lage = _lage(self.von, self.bis, links)
        if lage is None:
            return ""
        n = lage[1]
        return RICHTUNGEN[round(math.atan2(n[1], n[0]) / (math.pi / 4)) % 8]


def aus_schnitt(s: Mapping) -> Schnitt:
    """
    Ein Schnitt der Beschreibung, wie
    :meth:`~opencivil.projekt.querschnittsanalyse.QuerschnittsanalyseEintrag.elemente`
    ihn gibt.
    """
    return Schnitt(name=s["name"], kennung=s["kennung"], von=tuple(s["von"]),
                   bis=tuple(s["bis"]), links=s["seite"] == "links")
