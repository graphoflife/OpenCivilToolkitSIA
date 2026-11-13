"""
opencivil/decke/lasten.py -- die Lasten eines Lastfalls auf den Streifen.

VERANTWORTUNG:
Aus den Lasten eines Lastfalls, was jeder Streifen trägt: eine Last je
Länge längs seiner Achse, genau integriert über seine Breite. Je Stelle geht
der Anteil seiner Richtung in ihn (:mod:`~opencivil.decke.aufteilung`) --
liegt die Stelle in einem Unterzug derselben Richtung, in diesen.

FLÄCHEN:
Alles wird zu Flächen mit gleichmässiger Last: eine Flächenlast auf ihrem
Vieleck oder ihrer Platte, das Eigengewicht auf jeder Platte, eine
Einzellast auf ihrer Verteilfläche ``lx × ly`` und eine Linienlast auf einem
Band von :data:`LINIENBREITE`. Eine Fläche wird in konvexe Stücke zerlegt,
mit den Stücken der Platten geschnitten, mit dem Band jedes Streifens und
seinen Anteilen. Ein konvexes Stück ist quer zur Achse linear breit
(:func:`~opencivil.decke.geometrie.breite`): die Last darauf ist eine
lineare Last je Länge, ohne Näherung.

LINIENLASTEN:
Eine Linienlast liegt auf einem Band von 1 mm. Wo die Linie im Innern liegt,
je zur Hälfte zu beiden Seiten -- auf einer Grenze zwischen zwei Streifen
trägt also jeder die Hälfte, keiner das Doppelte. Liegt sie auf dem Rand
einer Platte, ganz auf der Seite der Platte. Ein Millimeter verschiebt
nichts, was man in den Ergebnissen sähe.

WAS DANEBEN LIEGT:
Was ausserhalb der Platten liegt, trägt nichts; die Summe steht in
:attr:`Belastung.daneben`, und eine Meldung nennt die Last.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.aufteilung import Aufteilungen
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Decke, Flaechenlast, Kombination, Lastfall, Linienlast, Punktlast
from opencivil.decke.streifen import Streifen, Zerlegung
from opencivil.decke.traeger import Streckenlast, Teillast
from opencivil.stabwerk.system import Meldung

#: Wie breit das Band einer Linienlast ist, in m.
LINIENBREITE = 1e-3

#: Unter diesem Anteil der Last gilt eine Last als ganz auf den Platten.
DANEBEN = 1e-9


@dataclass
class Belastung:
    """Je Streifen seine Lasten, in ``s = p·n`` seiner Richtung -- und die Summen."""

    je_streifen: Dict[str, List[Teillast]] = field(default_factory=dict)
    summe: float = 0.0
    """Alle Lasten zusammen, in N."""

    daneben: float = 0.0
    """Was davon neben den Platten liegt, in N."""

    meldungen: List[Meldung] = field(default_factory=list)

    def hinzu(self, name: str, last: Teillast) -> None:
        self.je_streifen.setdefault(name, []).append(last)


def kombiniert(belastungen: Dict[str, Belastung], kombination: Kombination) -> Belastung:
    """Eine Kombination: jede Last ihres Lastfalls mal dessen Beiwert -- alles ist linear."""
    heraus = Belastung()
    for name, faktor in kombination.faktoren.items():
        b = belastungen.get(name)
        if b is None or not faktor:
            continue
        for streifen, lasten in b.je_streifen.items():
            for last in lasten:
                heraus.hinzu(streifen, last.mal(faktor))
        heraus.summe += faktor * b.summe
        heraus.daneben += faktor * b.daneben
    return heraus


def belasten(decke: Decke, zerlegung: Zerlegung, aufteilungen: Aufteilungen, lastfall: Lastfall) -> Belastung:
    """Die Lasten des Lastfalls auf den Streifen."""
    heraus = Belastung()
    platten = [p.ecken for p in decke.platten]
    for name, vieleck, q in flaechen(decke, lastfall, heraus.meldungen):
        if not q:
            continue
        stuecke = geo.dreiecke(vieleck)
        gesamt = q * sum(abs(geo.flaeche(s)) for s in stuecke)
        getragen = 0.0
        for g, gruppe in enumerate(zerlegung.gruppen):
            for platte in gruppe.stuecke:
                for stueck in stuecke:
                    c = geo.schnitt(stueck, platte)
                    if c:
                        getragen += q * abs(geo.flaeche(c))
                        _verteilen(heraus, zerlegung, aufteilungen, g, c, q)
        heraus.summe += gesamt
        if abs(gesamt - getragen) > DANEBEN * abs(gesamt):
            heraus.daneben += gesamt - getragen
            heraus.meldungen.append(Meldung(
                f"Die Last «{name}» liegt zum Teil neben den Platten: {abs(gesamt - getragen) / 1e3:.3g} kN "
                "trägt niemand.", (name,), fehler=False))
    for last in lastfall.lasten:
        if isinstance(last, Linienlast) and last.wert:
            for vieleck in linienband(last.a, last.b, platten):
                q = last.wert / LINIENBREITE
                gesamt = q * abs(geo.flaeche(vieleck))
                getragen = 0.0
                for g, gruppe in enumerate(zerlegung.gruppen):
                    for platte in gruppe.stuecke:
                        c = geo.schnitt(vieleck, platte)
                        if c:
                            getragen += q * abs(geo.flaeche(c))
                            _verteilen(heraus, zerlegung, aufteilungen, g, c, q)
                heraus.summe += gesamt
                if abs(gesamt - getragen) > DANEBEN * abs(gesamt):
                    heraus.daneben += gesamt - getragen
                    heraus.meldungen.append(Meldung(
                        f"Die Linienlast «{last.name}» liegt zum Teil neben den Platten: "
                        f"{abs(gesamt - getragen) / 1e3:.3g} kN trägt niemand.", (last.name,), fehler=False))
    return heraus


def flaechen(decke: Decke, lastfall: Lastfall, meldungen: List[Meldung]) -> List[Tuple[str, List[Punkt], float]]:
    """Die Flächen des Lastfalls mit ihrer Last in N/m² -- ohne die Linienlasten."""
    heraus: List[Tuple[str, List[Punkt], float]] = []
    nach_name = {p.name: p for p in decke.platten}
    for last in lastfall.lasten:
        if isinstance(last, Flaechenlast):
            if last.platte:
                platte = nach_name.get(last.platte)
                if platte is None:
                    meldungen.append(Meldung(f"Die Last «{last.name}» liegt auf der Platte «{last.platte}», "
                                             "die es nicht gibt.", (last.name,)))
                    continue
                heraus.append((last.name, list(platte.ecken), last.wert))
            elif len(geo.bereinigt(last.ecken)) >= 3:
                heraus.append((last.name, list(last.ecken), last.wert))
            else:
                meldungen.append(Meldung(f"Die Flächenlast «{last.name}» hat keine Fläche.", (last.name,),
                                         fehler=False))
        elif isinstance(last, Punktlast):
            if last.lx > 0.0 and last.ly > 0.0:
                heraus.append((last.name, geo.achsrechteck(last.ort, last.lx, last.ly),
                               last.wert / (last.lx * last.ly)))
            else:
                meldungen.append(Meldung(f"Die Einzellast «{last.name}» braucht eine Verteilfläche.",
                                         (last.name,)))
    if lastfall.eigengewicht:
        for p in decke.platten:
            heraus.append((f"Eigengewicht {p.name}", list(p.ecken), p.wichte * p.h))
    return heraus


def linienband(a: Punkt, b: Punkt, platten: Sequence[Sequence[Punkt]]) -> List[List[Punkt]]:
    """
    Das Band einer Linienlast, in Stücken: wo die Linie im Innern liegt,
    beidseits je halb so breit; wo eine Seite ausserhalb aller Platten
    liegt, ganz auf der anderen.
    """
    laenge = math.hypot(b[0] - a[0], b[1] - a[1])
    if laenge <= geo.TOLERANZ:
        return []
    links = (-(b[1] - a[1]) / laenge, (b[0] - a[0]) / laenge)
    stellen = sorted({u for p in platten for u in geo.schnittstellen(a, b, p)})
    seiten: List[Tuple[float, float, Tuple[float, float]]] = []
    for u0, u1 in zip(stellen, stellen[1:]):
        if (u1 - u0) * laenge <= geo.TOLERANZ:
            continue
        m = (a[0] + 0.5 * (u0 + u1) * (b[0] - a[0]), a[1] + 0.5 * (u0 + u1) * (b[1] - a[1]))
        innen = [any(geo.innen((m[0] + z * LINIENBREITE * links[0], m[1] + z * LINIENBREITE * links[1]), p)
                     for p in platten) for z in (1.0, -1.0)]
        quer = (-0.5, 0.5) if innen[0] == innen[1] else ((0.0, 1.0) if innen[0] else (-1.0, 0.0))
        if seiten and seiten[-1][2] == quer:
            seiten[-1] = (seiten[-1][0], u1, quer)
        else:
            seiten.append((u0, u1, quer))
    heraus = []
    for u0, u1, (z0, z1) in seiten:
        p0 = (a[0] + u0 * (b[0] - a[0]), a[1] + u0 * (b[1] - a[1]))
        p1 = (a[0] + u1 * (b[0] - a[0]), a[1] + u1 * (b[1] - a[1]))
        heraus.append(geo.gegen_uhrzeiger([
            (p0[0] + z0 * LINIENBREITE * links[0], p0[1] + z0 * LINIENBREITE * links[1]),
            (p1[0] + z0 * LINIENBREITE * links[0], p1[1] + z0 * LINIENBREITE * links[1]),
            (p1[0] + z1 * LINIENBREITE * links[0], p1[1] + z1 * LINIENBREITE * links[1]),
            (p0[0] + z1 * LINIENBREITE * links[0], p0[1] + z1 * LINIENBREITE * links[1])]))
    return heraus


def _verteilen(heraus: Belastung, zerlegung: Zerlegung, aufteilungen: Aufteilungen, g: int,
               stueck: Sequence[Punkt], q: float) -> None:
    """Ein konvexes Stück mit ``q`` in N/m², auf einer Platte der Gruppe ``g``, auf die Streifen beider Richtungen."""
    for r in zerlegung.gruppen[g].richtungen:
        lo, hi = geo.bereich(stueck, r.t)
        for streifen in zerlegung.feldstreifen(r):
            if streifen.bis <= lo or streifen.von >= hi:
                continue
            for anteil in aufteilungen.flaechen.get((streifen.name, g), ()):
                c = geo.schnitt(stueck, anteil.ecken)
                if not c:
                    continue
                verlauf = geo.breite(c, r.n)
                f = q * anteil.faktor
                for (sa, wa), (sb, wb) in zip(verlauf, verlauf[1:]):
                    if sb > sa:
                        _zuordnen(heraus, zerlegung, streifen, Streckenlast(sa, sb, f * wa, f * wb))


def _zuordnen(heraus: Belastung, zerlegung: Zerlegung, streifen: Streifen, last: Streckenlast) -> None:
    """In den Feldstreifen -- oder, wo er in einem Unterzug seiner Richtung liegt, in diesen."""
    rest = [last]
    for u in zerlegung.parallele.get(streifen.name, ()):
        lo, hi = u.laengs
        weiter = []
        for l in rest:
            for a, b, ziel in ((l.a, min(l.b, lo), weiter), (max(l.a, lo), min(l.b, hi), None),
                               (max(l.a, hi), l.b, weiter)):
                if b - a <= 1e-12:
                    continue
                stueck = Streckenlast(a, b, l.bei(a), l.bei(b))
                if ziel is None:
                    heraus.hinzu(u.name, stueck)
                else:
                    ziel.append(stueck)
        rest = weiter
    for l in rest:
        heraus.hinzu(streifen.name, l)

