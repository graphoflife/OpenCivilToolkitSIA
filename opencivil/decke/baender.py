"""
opencivil/decke/baender.py -- die Bänder, die eine Decke selbst legt.

VERANTWORTUNG:
Bei automatischer Aufteilung legt die Rechnung Bänder -- versteckte
Unterzüge (:class:`~opencivil.decke.modell.Unterzug` mit ``von_selbst``),
so breit wie :attr:`~opencivil.decke.modell.Decke.bandbreite` --, wo
Streifen sonst ohne Lager enden oder eine Stütze nur die Streifen fände,
die über sie laufen. Das geschieht, bevor die Decke in Streifen zerfällt
(:func:`~opencivil.decke.rechnung.rechnen`). Bei fester Aufteilung legt sie
keine: dort gilt, was der Benutzer gibt.

WO BÄNDER LIEGEN:
1. **Über Stützen**: durch die Mitte jeder Stütze, in den zwei Richtungen
   der Platte, auf der sie steht -- über alle Stützen auf dieser Linie bis
   zum nächsten Lager quer dazu, einer Wand oder einem Unterzug, oder bis
   zum Rand der Platte. Steht die Stütze näher am Rand als eine halbe
   Bandbreite, rückt das Band nach innen, bis es ganz in der Platte liegt;
   die Mitte der Stütze bleibt darin.
2. **An offenen Rändern**: wo die Streifen einer Platte enden, ohne dass
   ein Linienlager sie hält -- an einem freien Rand, am Rand eines Lochs, an
   einer Platte mit anderen Richtungen. Das Band liegt innen am Rand, längs
   dazu, und reicht beidseits bis zum nächsten Lager: einer Wand, einer
   Stütze, einem Band über Stützen, einem Unterzug.

Die Bänder liegen unter allen Unterzügen des Benutzers, mit den Stufen
:data:`~opencivil.decke.baender.STUFE_RAND` und
:data:`~opencivil.decke.baender.STUFE_STUETZE` zwischen den Feldstreifen (0)
und dessen Stufen (ab 1): ein Band liegt auf einem Unterzug, nie trägt es
einen -- und ein Band am Rand liegt auf einem über Stützen.

Ein Band liegt auf mindestens zwei Lagern, die die Höhe halten. Als Kragarm
legt die Rechnung keines: auf einer eingespannten Wand trägt die Platte
selbst als Kragplatte. Ein Band am Rand legt sie nur, wo die Streifen quer
zum Rand sonst schon ein Lager haben -- das Band gibt ihnen das zweite. Eine
Platte, die nur in einer Richtung trägt, bekommt an ihren freien Rändern
darum keines; zwei Bänder dort nähmen ihr die ganze Last ab. Ein offener
Rand, kürzer als ein Band breit, bekommt keines. Liegt schon ein Unterzug
des Benutzers oder ein anderes Band längs auf dem Weg, ersetzt es das Band.
Über eine Wand längs läuft keines: es endet, wo sie beginnt -- dort trägt
die Wand selbst.

Liegt eine Platte nur auf zwei Wänden über Eck, findet kein Band zwei
Lager: sie trüge nur mit Drillmomenten, und die rechnet die
Streifenmethode nicht. Wo die Last dann ausfällt, sagt
:mod:`~opencivil.decke.aufteilung`.

Nach Vorgabe, nicht nachgeschlagen: Lage, Stufe und Breite der Bänder. Die
Norm lässt jede Aufteilung der Last zu, die im Gleichgewicht ist
(SIA 262:2025, 4.1.4.2.2).
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Dict, Iterator, List, Optional, Sequence, Tuple, Union

from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Aufteilung, Decke, Linienlager, Platte, Stuetze, Unterzug
from opencivil.decke.richtungen import FUGE, Kante, kanten
from opencivil.decke.streifen import (
    STUETZE, Richtung, nach_richtungen, pruefen, richtung, richtungen_der_platte,
    traeger_eines_unterzugs, ueberlappen,
)

#: Die Stufe eines Bands an einem offenen Rand und die eines Bands über
#: Stützen -- unter jeder Stufe, die der Benutzer gibt.
STUFE_RAND, STUFE_STUETZE = 0.25, 0.5

#: So nahe an einer Richtung der Platte, in rad, läuft ein Band am Rand in
#: ihr: auf den Millimeter gerundete Ecken legen es nicht schief zu den
#: Streifen. Ebenso nahe gilt ein Unterzug als längs zum Band.
WINKEL = 1e-3

#: Was längs eines Bands als dieselbe Stelle gilt, in m.
NAH = 1e-6

#: Wie dick die Scheibe quer durch eine Stütze ist, in der ein Band sieht,
#: wie breit die Platte dort ist, in m.
SCHEIBE = 1e-3

#: Ein Lager eines Bands: wo es liegt, von wo bis wo es drückt -- in ``s``
#: der Richtung des Bands -- und seine Art.
Lager = Tuple[float, float, float, str]

Stuecke = Dict[str, List[List[Punkt]]]


def gelegt(decke: Decke) -> Decke:
    """
    Die Decke mit den Bändern, die sie selbst legt -- unverändert bei fester
    Aufteilung, ohne Platte oder wenn ihre Geometrie nicht stimmt: das sagt
    dann die Zerlegung.
    """
    if (decke.aufteilung is not Aufteilung.AUTOMATISCH or not decke.platten
            or any(m.haelt_an for m in pruefen(decke))):
        return decke
    stuecke = {p.name: geo.dreiecke(p.ecken) for p in decke.platten}
    namen = _namen(decke)
    baender: List[Unterzug] = []

    def mit_baendern() -> Decke:
        return replace(decke, unterzuege=[*decke.unterzuege, *baender])

    for stuetze in decke.stuetzen:
        for r in _richtungen_bei(stuetze, decke, stuecke):
            band = _ueber_stuetze(stuetze, r, mit_baendern(), stuecke)
            if band is not None:
                baender.append(replace(band, name=next(namen)))
    for paar, platten in nach_richtungen(decke.platten):
        eigene = {p.name: stuecke[p.name] for p in platten}
        for a, b in offene_raender(platten, decke):
            if not _quer_gehalten(a, b, paar, mit_baendern(), eigene, stuecke):
                continue
            band = _am_rand(a, b, paar, mit_baendern(), stuecke)
            if band is not None:
                baender.append(replace(band, name=next(namen)))
    return mit_baendern() if baender else decke


def art(band: Unterzug) -> str:
    """Wo ein Band liegt, in Worten: «über Stützen» oder «am Rand»."""
    return "über Stützen" if band.stufe == STUFE_STUETZE else "am Rand"


def offene_raender(platten: Sequence[Platte], decke: Decke) -> List[Kante]:
    """
    Wo die Streifen der Platten ``platten`` -- einer Gruppe mit denselben
    Richtungen -- ohne Lager enden: die Stücke ihrer Ränder ohne
    Linienlager darauf und ohne eine Platte der Gruppe daneben, je
    ``(a, b)`` mit der Platte links, mindestens so lang wie ein Band breit.
    """
    heraus: List[Kante] = []
    for p in platten:
        for k in kanten(p):
            gedeckt = [x for q in platten if q is not p for m in kanten(q) if (x := geo.deckung(k, m, FUGE))]
            gedeckt += [x for w in decke.linienlager if w.vertikal or w.eingespannt
                        if (x := geo.deckung(k, (w.a, w.b), FUGE))]
            laenge, bis = math.dist(*k), 0.0
            for von, weiter in [*geo.vereinigt(gedeckt), (laenge, laenge)]:
                if von - bis >= decke.bandbreite:
                    heraus.append((_auf(k, bis), _auf(k, von)))
                bis = max(bis, weiter)
    return heraus


def _ueber_stuetze(stuetze: Stuetze, r: Richtung, decke: Decke, stuecke: Stuecke) -> Optional[Unterzug]:
    """
    Das Band über der Stütze in Richtung ``r``, über alle Stützen auf seinem
    Weg bis zum nächsten anderen Lager oder zum Rand der Platte -- ``None``,
    wo schon eines über ihr liegt oder es nicht zwei Lager fände.
    """
    if any(_laengs_zu(u, r.winkel) and geo.innen(stuetze.ort, geo.rechteck(u.a, u.b, u.breite))
           for u in decke.unterzuege if _lang(u)):
        return None
    s = geo.skalar(stuetze.ort, r.n)
    tau = _in_der_platte(geo.skalar(stuetze.ort, r.t), s, r, decke.bandbreite, stuecke)
    weit = _ueber_platten(r, tau, decke.bandbreite, stuecke, s)
    if weit is None:
        return None
    lager = [x for je in _lager(_band(r, tau, weit, decke.bandbreite, STUFE_STUETZE), decke, stuecke)
             for x in je if x[3] != STUETZE]
    laengs = _bis_zum_lager(lager, _waende_laengs(r, tau, decke), s - NAH, s + NAH, weit)
    return _gepruft(_band(r, tau, laengs, decke.bandbreite, STUFE_STUETZE), decke, stuecke) if laengs else None


def _in_der_platte(tau: float, s: float, r: Richtung, breite: float, stuecke: Stuecke) -> float:
    """
    Wo ein Band in Richtung ``r`` über der Stütze bei ``(s, tau)`` quer liegt:
    durch ihre Mitte -- steht sie näher am Rand als eine halbe Bandbreite,
    so weit innen, dass es ganz in der Platte liegt, die Mitte noch darin.
    Ist die Platte dort schmaler als das Band, mitten über ihr.
    """
    teile = [geo.bereich(c, r.t) for dreiecke in stuecke.values() for d in dreiecke
             if (c := geo.im_band(d, r.n, s - SCHEIBE, s + SCHEIBE))]
    lo, hi = next(((a, b) for a, b in geo.vereinigt(teile) if a - NAH <= tau <= b + NAH), (tau, tau))
    if hi - lo <= breite:
        return 0.5 * (lo + hi)
    return min(max(tau, lo + breite / 2.0), hi - breite / 2.0)


def _am_rand(a: Punkt, b: Punkt, richtungen: Tuple[Richtung, Richtung], decke: Decke,
             stuecke: Stuecke) -> Optional[Unterzug]:
    """
    Das Band am offenen Rand ``a → b`` (die Platte links), innen an ihm und
    beidseits bis zum nächsten Lager -- ``None``, wo es nicht zwei fände.
    Liegt der Rand fast in einer Richtung der Platte (:data:`WINKEL`), läuft
    das Band genau in ihr.
    """
    winkel = math.atan2(b[1] - a[1], b[0] - a[0])
    r = richtung(next((q.winkel for q in richtungen if abs(math.sin(q.winkel - winkel)) < WINKEL), winkel))
    links = (-(b[1] - a[1]), b[0] - a[0])
    seite = 1.0 if geo.skalar(links, r.t) > 0.0 else -1.0
    tau = geo.skalar(((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0), r.t) + seite * decke.bandbreite / 2.0
    s0, s1 = sorted((geo.skalar(a, r.n), geo.skalar(b, r.n)))
    weit = _ueber_platten(r, tau, decke.bandbreite, stuecke, 0.5 * (s0 + s1))
    if weit is None:
        return None
    lager = [x for je in _lager(_band(r, tau, weit, decke.bandbreite, STUFE_RAND), decke, stuecke) for x in je]
    laengs = _bis_zum_lager(lager, _waende_laengs(r, tau, decke), s0 + NAH, s1 - NAH, weit)
    return _gepruft(_band(r, tau, laengs, decke.bandbreite, STUFE_RAND), decke, stuecke) if laengs else None


def _bis_zum_lager(lager: Sequence[Lager], waende: Sequence[Tuple[float, float]], von: float, bis: float,
                   weit: Tuple[float, float]) -> Optional[Tuple[float, float]]:
    """
    Das Stück ``von → bis``, beidseits verlängert über das nächste Lager
    hinweg, bis es ganz auf ihm liegt -- ohne Lager bis ``weit``, zum Rand
    der Platte. Über eine Wand längs (``waende``) läuft es nicht: es endet,
    wo sie beginnt; liegt sie schon unter dem Stück selbst, ``None``.
    """
    if any(w0 < bis - NAH and w1 > von + NAH for w0, w1 in waende):
        return None
    vorn = max((x for x in lager if x[0] <= von), key=lambda x: x[0], default=None)
    hinten = min((x for x in lager if x[0] >= bis), key=lambda x: x[0], default=None)
    return (max([vorn[1] if vorn else weit[0], *(w1 for _, w1 in waende if w1 <= von + NAH)]),
            min([hinten[2] if hinten else weit[1], *(w0 for w0, _ in waende if w0 >= bis - NAH)]))


def _waende_laengs(r: Richtung, tau: float, decke: Decke) -> List[Tuple[float, float]]:
    """
    Von wo bis wo, in ``s`` von ``r``, Wände längs im Weg eines Bands quer
    bei ``tau`` liegen -- auch auf seinem Rand.
    """
    halb = decke.bandbreite / 2.0 + NAH
    return [(min(s), max(s)) for w in decke.linienlager
            if w.vertikal and _laengs_zu(w, r.winkel) and all(abs(geo.skalar(p, r.t) - tau) <= halb
                                                               for p in (w.a, w.b))
            for s in [(geo.skalar(w.a, r.n), geo.skalar(w.b, r.n))]]


def _quer_gehalten(a: Punkt, b: Punkt, richtungen: Tuple[Richtung, Richtung], decke: Decke,
                   eigene: Stuecke, stuecke: Stuecke) -> bool:
    """
    Ob die Streifen, die am Rand ``a → b`` enden, sonst ein Lager haben:
    ein Feldstreifen quer durch die Mitte des Rands, über die Platten
    ``eigene`` der Gruppe, wie die Zerlegung ihn lagerte.
    """
    winkel = math.atan2(b[1] - a[1], b[0] - a[0])
    mitte = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    breite = decke.streifenbreite
    for r in richtungen:
        if abs(math.sin(r.winkel - winkel)) < WINKEL:
            continue
        tau = geo.skalar(mitte, r.t)
        weit = _ueber_platten(r, tau, breite, eigene, geo.skalar(mitte, r.n))
        if weit is None:
            continue
        streifen = Unterzug("", r.punkt(weit[0], tau), r.punkt(weit[1], tau), breite, 0)
        if any(x.vertikal for t in traeger_eines_unterzugs(streifen, decke, stuecke) for x in t.auflager):
            return True
    return False


def _gepruft(band: Unterzug, decke: Decke, stuecke: Stuecke) -> Optional[Unterzug]:
    """Das Band, wenn kein Unterzug längs auf seinem Weg liegt und jedes Stück auf zwei Lagern liegt -- sonst ``None``."""
    if not _lang(band) or _ueberdeckt(band, decke.unterzuege):
        return None
    lager = _lager(band, decke, stuecke)
    zwei = all(len(je) >= 2 and max(x[0] for x in je) - min(x[0] for x in je) > NAH for je in lager)
    return band if lager and zwei else None


def _lager(band: Unterzug, decke: Decke, stuecke: Stuecke) -> List[List[Lager]]:
    """Je Träger des Bands die Lager, die seine Höhe halten -- wie die Zerlegung sie fände."""
    return [[(t.s0 + a.s, t.s0 + a.bereich[0], t.s0 + a.bereich[1], a.art) for a in t.auflager if a.vertikal]
            for t in traeger_eines_unterzugs(band, decke, stuecke)]


def _ueber_platten(r: Richtung, tau: float, breite: float, stuecke: Stuecke,
                   bei: float) -> Optional[Tuple[float, float]]:
    """
    Wie weit ein Band quer bei ``tau`` längs über die Platten reicht, in
    ``s`` von ``r`` -- das Stück, in dem ``bei`` liegt; ``None``, wenn dort
    keine Platte ist.
    """
    teile = [geo.bereich(c, r.n) for dreiecke in stuecke.values() for d in dreiecke
             if (c := geo.im_band(d, r.t, tau - breite / 2.0, tau + breite / 2.0))]
    return next(((a, b) for a, b in geo.vereinigt(teile) if a - NAH <= bei <= b + NAH), None)


def _richtungen_bei(stuetze: Stuetze, decke: Decke, stuecke: Stuecke) -> List[Richtung]:
    """Die Richtungen der Platten, auf denen die Stütze steht -- parallele einmal."""
    flaeche = geo.achsrechteck(stuetze.ort, stuetze.bx, stuetze.by)
    heraus: List[Richtung] = []
    for p in decke.platten:
        if geo.innen(stuetze.ort, p.ecken) or any(geo.schnitt(d, flaeche) for d in stuecke[p.name]):
            heraus.extend(r for r in richtungen_der_platte(p) if not any(r.parallel(q) for q in heraus))
    return heraus


def _ueberdeckt(band: Unterzug, andere: Sequence[Unterzug]) -> bool:
    """Ob ein Unterzug längs auf dem Weg des Bands liegt -- dann ersetzt er es."""
    flaeche = [geo.rechteck(band.a, band.b, band.breite)]
    w = _winkel(band)
    return any(_laengs_zu(u, w) and ueberlappen(flaeche, [geo.rechteck(u.a, u.b, u.breite)])
               for u in andere if _lang(u))


def _band(r: Richtung, tau: float, laengs: Tuple[float, float], breite: float, stufe: float) -> Unterzug:
    """Ein Band in Richtung ``r``, quer bei ``tau``, längs über ``laengs`` -- noch ohne Namen."""
    return Unterzug("", r.punkt(laengs[0], tau), r.punkt(laengs[1], tau), breite, stufe, von_selbst=True)


def _namen(decke: Decke) -> Iterator[str]:
    """B1, B2, … -- ohne die Namen, die schon ein Teil der Decke trägt."""
    vergeben = {x.name for liste in (decke.platten, decke.linienlager, decke.stuetzen, decke.unterzuege,
                                     decke.zonen) for x in liste}
    vergeben |= {last.name for lf in decke.lastfaelle for last in lf.lasten}
    i = 0
    while True:
        i += 1
        if f"B{i}" not in vergeben:
            yield f"B{i}"


def _auf(k: Kante, s: float) -> Punkt:
    """Der Punkt ``s`` Meter nach dem Anfang des Rands ``k``."""
    (a, b), u = k, s / math.dist(*k)
    return (a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]))


def _winkel(u: Union[Unterzug, Linienlager]) -> float:
    return math.atan2(u.b[1] - u.a[1], u.b[0] - u.a[0])


def _laengs_zu(u: Union[Unterzug, Linienlager], winkel: float) -> bool:
    """Ob ``u`` in ``winkel`` läuft, bis auf :data:`WINKEL`."""
    return abs(math.sin(_winkel(u) - winkel)) < WINKEL


def _lang(u: Unterzug) -> bool:
    return math.dist(u.a, u.b) > geo.TOLERANZ
