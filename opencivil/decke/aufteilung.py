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
     geht alles in sie. Trägt keine, geht die Last trotzdem je zur Hälfte
     in die Streifen: dort fällt sie aus, die Probe zählt sie als nicht
     getragen, und das Bild zeigt die Stelle als «trägt nicht».
   * ``b`` ist die kleinere Spannweite der beiden Felder, in denen die
     Zelle liegt; eine Kragplatte zählt doppelt so lang.
   * Liegt die Zelle in einer Richtung höchstens ``b/4`` vor einem Lager,
     geht die Last in diese Richtung -- liegt sie in beiden so nahe, je zur
     Hälfte (die Ecken der Folie 31).
   * Sonst geht sie mehr in die Richtung mit dem kürzeren Feld: bei
     gleichen Feldern je zur Hälfte, ab dem Verhältnis :data:`GANZ_AB` der
     Spannweiten ganz, dazwischen geradlinig (:func:`in_der_mitte`;
     Benutzer, 2026-11-25). So springt der Anteil nicht, wenn eine
     Spannweite um ein Weniges wächst: 5 × 5.04 m und 5 × 5.06 m teilen
     fast gleich.

   Für die einfach gelagerte Rechteckplatte der Folie 31 -- Verhältnis 2
   -- ergibt das genau deren Aufteilung. Für andere Platten ist es eine
   Verallgemeinerung -- nach Vorgabe. Die Norm schreibt keine vor: nach der
   statischen Methode gilt jede, die im Gleichgewicht ist (SIA 262:2025,
   4.1.4.2.2).

WO LAST AUSFÄLLT:
Je Zelle, ob ihre Last auf einen Träger kommt, der nicht trägt: weil keine
Richtung trägt -- dann fehlt ein Lager oder ein Unterzug --, oder weil die
feste Aufteilung oder eine Zone Last in eine Richtung gibt, die nicht
trägt. Je Platte und Ursache steht das in einer grauen Meldung an der
Platte, mit der Fläche: es fehlt etwas, und der Rest rechnet (Benutzer,
2026-11-19). Eine Zone gilt dafür in den Zellen, deren Schwerpunkt in ihr
liegt.

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

from opencivil.core.latex import fest
from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Aufteilung, Decke, Platte
from opencivil.decke.streifen import AUF_NICHTS, Gruppe, Lage, Richtung, Streifen, Zerlegung
from opencivil.stabwerk.system import Meldung

#: So viel länger als die Gruppe reicht ein Anteil, der einen ganzen Streifen deckt, in m.
UEBERSTAND = 1.0

#: Ab diesem Verhältnis der Spannweiten geht die Mitte eines Felds ganz in die kürzere Richtung.
GANZ_AB = 1.5


@dataclass(frozen=True)
class Anteil:
    """Ein konvexes Vieleck (Gegenuhrzeigersinn) und der Faktor, mit dem die Last darauf in den Streifen geht."""

    ecken: Tuple[Punkt, ...]
    faktor: float


#: Fürs Bild ein Vieleck und sein Anteil in Richtung 1 -- ``None``, wo keine Richtung trägt.
Bildzelle = Tuple[Tuple[Punkt, ...], Optional[float]]


@dataclass(frozen=True)
class Zelle:
    """
    Wo sich der Streifen ``i`` der Richtung 1 und der Streifen ``j`` der
    Richtung 2 kreuzen: ihre Stücke in den Platten der Gruppe, deren
    Schwerpunkt und wo er auf den Trägern beider Richtungen liegt.
    """

    i: int
    j: int
    teile: Tuple[Tuple[Punkt, ...], ...]
    mitte: Punkt
    lage_1: Lage
    lage_2: Lage

    def flaeche_in(self, platte: Platte) -> float:
        """Wie viel von ihr in der Platte liegt -- jedes Stück liegt in einer, sein Schwerpunkt also auch."""
        return sum(abs(geo.flaeche(c)) for c in self.teile if geo.innen(geo.schwerpunkt(c), platte.ecken))


@dataclass
class Aufteilungen:
    """Je ``(Feldstreifen, Gruppe)`` die Flächen mit Anteil -- und je Zelle, was automatisch entschieden wurde."""

    flaechen: Dict[Tuple[str, int], List[Anteil]]
    zellen: List[Bildzelle]
    """
    Fürs Bild, was automatisch entschieden wurde: Vieleck und Anteil in
    Richtung 1 -- ``None``, wo keine Richtung trägt --, je Streifen der
    Richtung 1 die Zellen gleichen Anteils zusammengelegt, wie die Last sie
    bekommt, geschnitten mit der Platte.
    """

    meldungen: List[Meldung]


def aufteilen(decke: Decke, zerlegung: Zerlegung) -> Aufteilungen:
    flaechen: Dict[Tuple[str, int], List[Anteil]] = {}
    bild: List[Bildzelle] = []
    meldungen: List[Meldung] = []
    zonen = [(z, geo.dreiecke(z.ecken)) for z in decke.zonen]
    for g, gruppe in enumerate(zerlegung.gruppen):
        r1, r2 = gruppe.richtungen
        streifen1, streifen2 = zerlegung.feldstreifen(r1), zerlegung.feldstreifen(r2)
        zellen = _zellen(zerlegung, gruppe, streifen1, streifen2)
        if decke.aufteilung is Aufteilung.FEST:
            grund = {(s.name, 1): [Anteil(tuple(_ganz(s, gruppe)), decke.anteil)] for s in streifen1}
            grund.update({(s.name, 2): [Anteil(tuple(_ganz(s, gruppe)), 1.0 - decke.anteil)] for s in streifen2})
        else:
            grund, neue = _automatisch(gruppe, streifen1, streifen2, zellen)
            bild.extend(neue)
        meldungen.extend(_ausfall(decke, gruppe, zellen))
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
    return Aufteilungen(flaechen, bild, meldungen)


def _ganz(s: Streifen, gruppe: Gruppe) -> List[Punkt]:
    """Das Band des Streifens, so lang, dass es die Gruppe ganz deckt."""
    lo, hi = math.inf, -math.inf
    for stueck in gruppe.stuecke:
        a, b = geo.bereich(stueck, s.richtung.n)
        lo, hi = min(lo, a), max(hi, b)
    return s.band(lo - UEBERSTAND, hi + UEBERSTAND)


def _zellen(zerlegung: Zerlegung, gruppe: Gruppe, streifen1: Sequence[Streifen],
            streifen2: Sequence[Streifen]) -> List[Zelle]:
    """Die Zellen, die in den Platten der Gruppe liegen, je mit der Lage ihres Schwerpunkts."""
    r1, r2 = gruppe.richtungen
    heraus: List[Zelle] = []
    for i, a in enumerate(streifen1):
        band = _ganz(a, gruppe)
        for j, b in enumerate(streifen2):
            zelle = geo.im_band(band, b.richtung.t, b.von, b.bis)
            teile = [tuple(c) for stueck in gruppe.stuecke if zelle for c in [geo.schnitt(zelle, stueck)] if c]
            flaeche = sum(abs(geo.flaeche(c)) for c in teile)
            if flaeche <= geo.TOLERANZ ** 2:
                continue
            mitte = (sum(geo.schwerpunkt(c)[0] * abs(geo.flaeche(c)) for c in teile) / flaeche,
                     sum(geo.schwerpunkt(c)[1] * abs(geo.flaeche(c)) for c in teile) / flaeche)
            heraus.append(Zelle(i, j, tuple(teile), mitte, lage(zerlegung, mitte, a, r1),
                                lage(zerlegung, mitte, b, r2)))
    return heraus


def _automatisch(gruppe: Gruppe, streifen1: Sequence[Streifen], streifen2: Sequence[Streifen],
                 zellen: Sequence[Zelle]) -> Tuple[Dict[Tuple[str, int], List[Anteil]], List[Bildzelle]]:
    """
    Je Streifen die Flächen nach dem Anteil jeder Zelle, Zellen gleichen
    Anteils längs des Streifens zusammengelegt. Fürs Bild dieselben Flächen
    der Richtung 1, geschnitten mit der Platte -- ohne Anteil, wo keine
    Richtung trägt.
    """
    anteil = {(z.i, z.j): _anteil_bei(z.lage_1, z.lage_2) for z in zellen}
    # Wo keine Richtung trägt, je zur Hälfte: die Last fällt dort aus, und die Probe zählt sie.
    last = {k: 0.5 if w is None else w for k, w in anteil.items()}
    grund: Dict[Tuple[str, int], List[Anteil]] = {}
    bild: List[Bildzelle] = []
    for i, a in enumerate(streifen1):
        band, quer = _ganz(a, gruppe), [j for j in range(len(streifen2)) if (i, j) in anteil]
        grund[(a.name, 1)] = [Anteil(e, w) for e, w in
                              _zusammengelegt(band, streifen2, [(j, last[(i, j)]) for j in quer])]
        bild += [(tuple(c), w) for e, w in _zusammengelegt(band, streifen2, [(j, anteil[(i, j)]) for j in quer])
                 for stueck in gruppe.stuecke if (c := geo.schnitt(stueck, e))]
    for j, b in enumerate(streifen2):
        quer = [i for i in range(len(streifen1)) if (i, j) in anteil]
        grund[(b.name, 2)] = [Anteil(e, w) for e, w in
                              _zusammengelegt(_ganz(b, gruppe), streifen1, [(i, 1.0 - last[(i, j)]) for i in quer])]
    return grund, bild


def _ausfall(decke: Decke, gruppe: Gruppe, zellen: Sequence[Zelle]) -> List[Meldung]:
    """
    Je Platte und Ursache, wo Last ausfällt, eine graue Meldung an ihr: wo
    keine Richtung trägt, je Richtung warum; wo die feste Aufteilung oder
    eine Zone Last in eine Richtung gibt, die nicht trägt, wer und wie viel.
    """
    r1, r2 = gruppe.richtungen
    # Je (Platte, Ursache) die Fläche und je Richtung die Gründe, in der Folge ihres Auftretens.
    flaeche: Dict[Tuple[str, Optional[Tuple[str, str, float]]], float] = {}
    gruende: Dict[Tuple[str, Optional[Tuple[str, str, float]]], Dict[str, List[str]]] = {}

    def zaehlen(z: Zelle, ursache: Optional[Tuple[str, str, float]], *richtungen: Tuple[str, Lage]) -> None:
        for platte in gruppe.platten:
            A = z.flaeche_in(platte)
            if A <= 0.0:
                continue
            schluessel = (platte.name, ursache)
            flaeche[schluessel] = flaeche.get(schluessel, 0.0) + A
            for r, l in richtungen:
                liste = gruende.setdefault(schluessel, {}).setdefault(r, [])
                warum = (l.warum or AUF_NICHTS).platte
                if warum not in liste:
                    liste.append(warum)

    for z in zellen:
        if not z.lage_1.traegt and not z.lage_2.traegt:
            zaehlen(z, None, (r1.name, z.lage_1), (r2.name, z.lage_2))
            continue
        zone = next((zone for zone in decke.zonen if geo.innen(z.mitte, zone.ecken)), None)
        if zone is not None:
            wer, anteil = f"die Zone {zone.name}", zone.anteil
        elif decke.aufteilung is Aufteilung.FEST:
            wer, anteil = "die feste Aufteilung", decke.anteil
        else:
            continue
        if not z.lage_1.traegt and anteil > 0.0:
            zaehlen(z, (wer, r1.name, anteil), (r1.name, z.lage_1))
        if not z.lage_2.traegt and anteil < 1.0:
            zaehlen(z, (wer, r2.name, 1.0 - anteil), (r2.name, z.lage_2))
    heraus: List[Meldung] = []
    for (platte, ursache), A in flaeche.items():
        wo = _wo(gruende[(platte, ursache)])
        if ursache is None:
            text = (f"Platte {platte}: auf {fest(A, 2)} m² trägt keine Richtung – {wo}. Dort fällt die "
                    "Last aus; es fehlt ein Lager oder ein Unterzug.")
        else:
            wer, r, anteil = ursache
            text = (f"Platte {platte}: auf {fest(A, 2)} m² gibt {wer} {fest(100.0 * anteil, 0)} % der "
                    f"Last in {r}, aber {wo} – dieser Teil fällt aus.")
        heraus.append(Meldung(text, (platte,), fehler=False))
    return heraus


def _wo(je_richtung: Dict[str, List[str]]) -> str:
    """«in x liegt sie nur auf «W3», …; in y liegt sie auf nichts» -- gleiche Gründe einmal, «in x und y»."""
    richtungen: Dict[str, List[str]] = {}
    for r, liste in je_richtung.items():
        for warum in liste:
            richtungen.setdefault(warum, []).append(r)
    return "; ".join(f"in {' und '.join(rs)} {warum}" for warum, rs in richtungen.items())


def _zusammengelegt(band: Sequence[Punkt], quer: Sequence[Streifen],
                    folge: Sequence[Tuple[int, Optional[float]]]) -> List[Bildzelle]:
    """
    Die Zellen längs eines Streifens, die nebeneinanderliegenden mit gleichem
    Anteil zu einer: das Band, geschnitten mit den Streifen quer von der
    ersten bis zur letzten -- je Vieleck und Anteil.
    """
    heraus: List[Bildzelle] = []
    lauf: List[Tuple[int, Optional[float]]] = []

    def abschliessen() -> None:
        if not lauf:
            return
        erste, letzte = quer[lauf[0][0]], quer[lauf[-1][0]]
        von, bis = min(erste.von, letzte.von), max(erste.bis, letzte.bis)
        c = geo.im_band(band, erste.richtung.t, von, bis)
        if c:
            heraus.append((tuple(geo.gegen_uhrzeiger(c)), lauf[0][1]))

    # Die Streifen einer Richtung liegen lückenlos nebeneinander, der Nummer nach.
    for k, wert in folge:
        if lauf and (wert != lauf[-1][1] or k != lauf[-1][0] + 1):
            abschliessen()
            lauf = []
        lauf.append((k, wert))
    abschliessen()
    return heraus


def _anteil_bei(la: Lage, lb: Lage) -> Optional[float]:
    """Der Anteil in Richtung 1, wo eine Stelle in ``la`` und ``lb`` liegt -- ``None``, wenn keine Richtung trägt."""
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
    return in_der_mitte(la.spannweite, lb.spannweite)


def in_der_mitte(spannweite_1: float, spannweite_2: float) -> float:
    """
    Der Anteil in Richtung 1 fern der Lager: je zur Hälfte bei gleichen
    Spannweiten, geradlinig mehr in die kürzere, ganz in sie ab dem
    Verhältnis :data:`GANZ_AB`. Ohne Feld -- unendlich -- in beiden
    Richtungen je zur Hälfte.
    """
    kurz, lang = sorted((spannweite_1, spannweite_2))
    verhaeltnis = lang / kurz if math.isfinite(kurz) else 1.0
    zur_kuerzeren = min(1.0, 0.5 + 0.5 * (verhaeltnis - 1.0) / (GANZ_AB - 1.0))
    return zur_kuerzeren if spannweite_1 <= spannweite_2 else 1.0 - zur_kuerzeren


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
        return Lage(False, math.inf, math.inf, AUF_NICHTS)
    return t.lage(min(max(s - t.s0, 0.0), t.L))
