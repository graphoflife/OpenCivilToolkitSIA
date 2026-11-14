"""
opencivil/decke/aufteilung.py -- welcher Teil der Last in welche Richtung geht.

VERANTWORTUNG:
An jeder Stelle einer Platte geht ein Anteil der Last in ihre Richtung 1,
der Rest in Richtung 2 (Stahlbeton II, 7.2 Platten, Folien 29 bis 31).
Hier steht, welcher -- als Flächen mit Anteil, je Feldstreifen und je Gruppe
von Platten mit denselben Richtungen. :mod:`~opencivil.decke.lasten` legt
die Last darauf.

DREI QUELLEN, IN DIESER FOLGE:
1. **Gezeichnete Zonen** gehen vor: dort gilt ihr Anteil.
2. Sonst, bei **fester Aufteilung**, überall derselbe Anteil.
3. Sonst, **automatisch**, nach dem Muster der Folie 31 -- was nahe an einem
   Rand liegt, geht auf kürzestem Weg in dessen Lager. Gerechnet wird je
   Zelle, wo sich ein Streifen der einen und einer der anderen Richtung
   kreuzen:

   * Trägt nur eine Richtung -- der Streifen der anderen ist beweglich --,
     geht alles in sie.
   * ``b`` ist die kleinere Spannweite der beiden Felder, in denen die
     Zelle liegt; eine Kragplatte zählt doppelt so lang.
   * Liegt die Zelle in einer Richtung höchstens ``b/4`` vor einem Lager,
     geht die Last in diese Richtung -- liegt sie in beiden so nahe, je zur
     Hälfte (die Ecken der Folie 31).
   * Sonst geht sie in die Richtung mit dem kürzeren Feld, bei gleichen
     Feldern je zur Hälfte.

   Für die einfach gelagerte Rechteckplatte der Folie 31 ergibt das genau
   deren Aufteilung. Für andere Platten ist es eine Verallgemeinerung --
   nach Vorgabe. Die Norm schreibt keine vor: nach der statischen Methode
   gilt jede, die im Gleichgewicht ist (SIA 262:2025, 4.1.4.2.2).

FLÄCHEN MIT ANTEIL:
Ein :class:`Anteil` ist ein konvexes Vieleck und ein Faktor: die Last
darauf, mal den Faktor, geht in den Streifen. Eine Zone wird abgezogen und
hinzugefügt -- ihr Faktor ist der Unterschied zum Grundanteil darunter --,
darum dürfen sich Zonen nicht überlappen.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Aufteilung, Decke
from opencivil.decke.streifen import Gruppe, Lage, Richtung, Streifen, Zerlegung
from opencivil.stabwerk.system import Meldung

#: So viel länger als die Gruppe reicht ein Anteil, der einen ganzen Streifen deckt, in m.
UEBERSTAND = 1.0

#: Zwei Spannweiten, die weniger als so viel auseinanderliegen, gelten als gleich.
GLEICHE_SPANNWEITE = 0.01


@dataclass(frozen=True)
class Anteil:
    """Ein konvexes Vieleck (Gegenuhrzeigersinn) und der Faktor, mit dem die Last darauf in den Streifen geht."""

    ecken: Tuple[Punkt, ...]
    faktor: float


@dataclass
class Aufteilungen:
    """Je ``(Feldstreifen, Gruppe)`` die Flächen mit Anteil -- und je Zelle, was automatisch entschieden wurde."""

    flaechen: Dict[Tuple[str, int], List[Anteil]]
    zellen: List[Tuple[Tuple[Punkt, ...], float]]
    """
    Fürs Bild, was automatisch entschieden wurde: Vieleck und Anteil in
    Richtung 1 -- je Streifen der Richtung 1 die Zellen gleichen Anteils
    zusammengelegt, wie die Last sie bekommt, geschnitten mit der Platte.
    """

    meldungen: List[Meldung]


def aufteilen(decke: Decke, zerlegung: Zerlegung) -> Aufteilungen:
    flaechen: Dict[Tuple[str, int], List[Anteil]] = {}
    zellen: List[Tuple[Tuple[Punkt, ...], float]] = []
    meldungen: List[Meldung] = []
    zonen = [(z, geo.dreiecke(z.ecken)) for z in decke.zonen]
    for g, gruppe in enumerate(zerlegung.gruppen):
        r1, r2 = gruppe.richtungen
        streifen1, streifen2 = zerlegung.feldstreifen(r1), zerlegung.feldstreifen(r2)
        if decke.aufteilung is Aufteilung.FEST:
            grund = {(s.name, 1): [Anteil(tuple(_ganz(s, gruppe)), decke.anteil)] for s in streifen1}
            grund.update({(s.name, 2): [Anteil(tuple(_ganz(s, gruppe)), 1.0 - decke.anteil)] for s in streifen2})
        else:
            grund, neue_zellen, ohne = _automatisch(zerlegung, gruppe, streifen1, streifen2)
            zellen.extend(neue_zellen)
            meldungen.extend(Meldung(
                f"Platte {name}: an {n} Stellen trägt keine der beiden Richtungen -- dort fehlt ein "
                "Lager oder ein Unterzug.", (name,)) for name, n in ohne.items())
        for (name, nummer), anteile in grund.items():
            heraus = list(anteile)
            for zone, stuecke in zonen:
                soll = zone.anteil if nummer == 1 else 1.0 - zone.anteil
                for stueck in stuecke:
                    for a in anteile:
                        c = geo.schnitt(stueck, a.ecken)
                        if c and abs(soll - a.faktor) > 0.0:
                            heraus.append(Anteil(tuple(c), soll - a.faktor))
            flaechen[(name, g)] = heraus
    return Aufteilungen(flaechen, zellen, meldungen)


def _ganz(s: Streifen, gruppe: Gruppe) -> List[Punkt]:
    """Das Band des Streifens, so lang, dass es die Gruppe ganz deckt."""
    lo, hi = math.inf, -math.inf
    for stueck in gruppe.stuecke:
        a, b = geo.bereich(stueck, s.richtung.n)
        lo, hi = min(lo, a), max(hi, b)
    return s.band(lo - UEBERSTAND, hi + UEBERSTAND)


def _automatisch(zerlegung: Zerlegung, gruppe: Gruppe, streifen1: Sequence[Streifen],
                 streifen2: Sequence[Streifen]):
    """
    Die Zellen der Gruppe, je mit ihrem Anteil in Richtung 1 -- und daraus je
    Streifen die Flächen, Zellen gleichen Anteils längs des Streifens
    zusammengelegt. Fürs Bild dieselben Flächen der Richtung 1, geschnitten
    mit der Platte. Dazu je Platte, an wie vielen Zellen keine Richtung trägt.
    """
    r1, r2 = gruppe.richtungen
    anteil: Dict[Tuple[int, int], float] = {}
    ohne: Dict[str, int] = {}
    for i, a in enumerate(streifen1):
        band = _ganz(a, gruppe)
        for j, b in enumerate(streifen2):
            zelle = geo.im_band(band, b.richtung.t, b.von, b.bis)
            if not zelle:
                continue
            teile = [c for stueck in gruppe.stuecke for c in [geo.schnitt(zelle, stueck)] if c]
            if not teile:
                continue
            flaeche = sum(abs(geo.flaeche(c)) for c in teile)
            if flaeche <= geo.TOLERANZ ** 2:
                continue
            mitte = (sum(geo.schwerpunkt(c)[0] * abs(geo.flaeche(c)) for c in teile) / flaeche,
                     sum(geo.schwerpunkt(c)[1] * abs(geo.flaeche(c)) for c in teile) / flaeche)
            wert = _anteil_bei(zerlegung, mitte, (a, r1), (b, r2))
            if wert is None:
                # Jedes Teil liegt in einem Stück einer Platte -- sein Schwerpunkt also in ihr.
                for p in gruppe.platten:
                    if any(geo.innen(geo.schwerpunkt(c), p.ecken) for c in teile):
                        ohne[p.name] = ohne.get(p.name, 0) + 1
                wert = 0.5
            anteil[(i, j)] = wert
    grund: Dict[Tuple[str, int], List[Anteil]] = {}
    for i, a in enumerate(streifen1):
        grund[(a.name, 1)] = _zusammengelegt(_ganz(a, gruppe), streifen2,
                                             [(j, anteil[(i, j)]) for j in range(len(streifen2)) if (i, j) in anteil])
    for j, b in enumerate(streifen2):
        grund[(b.name, 2)] = _zusammengelegt(_ganz(b, gruppe), streifen1,
                                             [(i, 1.0 - anteil[(i, j)]) for i in range(len(streifen1))
                                              if (i, j) in anteil])
    zellen = [(tuple(c), teil.faktor) for a in streifen1 for teil in grund[(a.name, 1)]
              for stueck in gruppe.stuecke if (c := geo.schnitt(stueck, teil.ecken))]
    return grund, zellen, ohne


def _zusammengelegt(band: Sequence[Punkt], quer: Sequence[Streifen],
                    folge: Sequence[Tuple[int, float]]) -> List[Anteil]:
    """
    Die Zellen längs eines Streifens, die nebeneinanderliegenden mit gleichem
    Anteil zu einer: das Band, geschnitten mit den Streifen quer von der
    ersten bis zur letzten.
    """
    heraus: List[Anteil] = []
    lauf: List[Tuple[int, float]] = []

    def abschliessen() -> None:
        if not lauf:
            return
        erste, letzte = quer[lauf[0][0]], quer[lauf[-1][0]]
        von, bis = min(erste.von, letzte.von), max(erste.bis, letzte.bis)
        c = geo.im_band(band, erste.richtung.t, von, bis)
        if c:
            heraus.append(Anteil(tuple(geo.gegen_uhrzeiger(c)), lauf[0][1]))

    # Die Streifen einer Richtung liegen lückenlos nebeneinander, der Nummer nach.
    for k, wert in folge:
        if lauf and (wert != lauf[-1][1] or k != lauf[-1][0] + 1):
            abschliessen()
            lauf = []
        lauf.append((k, wert))
    abschliessen()
    return heraus


def _anteil_bei(zerlegung: Zerlegung, p: Punkt, a: Tuple[Streifen, Richtung],
                b: Tuple[Streifen, Richtung]) -> Optional[float]:
    """Der Anteil in Richtung 1 an der Stelle ``p`` -- ``None``, wenn keine Richtung trägt."""
    la, lb = lage(zerlegung, p, *a), lage(zerlegung, p, *b)
    if not la.traegt and not lb.traegt:
        return None
    if not lb.traegt:
        return 1.0
    if not la.traegt:
        return 0.0
    kurz = min(la.spannweite, lb.spannweite)
    nah_a = la.abstand <= kurz / 4.0 + geo.TOLERANZ
    nah_b = lb.abstand <= kurz / 4.0 + geo.TOLERANZ
    if nah_a and nah_b:
        return 0.5
    if nah_a or nah_b:
        return 1.0 if nah_a else 0.0
    if abs(la.spannweite - lb.spannweite) <= GLEICHE_SPANNWEITE * kurz:
        return 0.5
    return 1.0 if la.spannweite < lb.spannweite else 0.0


def lage(zerlegung: Zerlegung, p: Punkt, streifen: Streifen, r: Richtung) -> Lage:
    """
    Wo ``p`` auf dem trägt, was dort die Last in Richtung ``r`` übernimmt:
    ein Unterzug in dieser Richtung, in dessen Fläche ``p`` liegt, sonst der
    Feldstreifen.
    """
    traeger_von = next((u for u in zerlegung.parallele.get(streifen.name, ())
                        if geo.innen(p, u.gebiet)), streifen)
    s = geo.skalar(p, r.n)
    t = traeger_von.traeger_bei(s)
    if t is None:
        return Lage(False, math.inf, math.inf)
    return t.lage(min(max(s - t.s0, 0.0), t.L))
