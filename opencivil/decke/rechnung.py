"""
opencivil/decke/rechnung.py -- die Streifenmethode, Fall für Fall.

VERANTWORTUNG:
Die ganze Rechnung einer Decke: zerlegen (:mod:`~opencivil.decke.streifen`),
die Last aufteilen (:mod:`~opencivil.decke.aufteilung`), je Lastfall auf die
Streifen legen (:mod:`~opencivil.decke.lasten`), und dann je Lastfall und
Kombination die Träger rechnen -- von unten nach oben:

1. die Feldstreifen (Stufe 0),
2. die Unterzüge, nach Stufe aufsteigend. Was ein Streifen in einen
   Unterzug gibt, liegt auf diesem als Last -- mit umgekehrtem Vorzeichen
   die Pressung, mit der dieser ihn trägt, über die Fläche, die beide
   teilen (Stahlbeton II, 7.2 Platten, Folie 33: «Anschliessend werden die
   Reaktionen des Flächenlagers als Belastung auf den versteckten Unterzug
   aufgebracht»).
3. Was in Linienlager und Stützen geht, sind die Lagerkräfte der Decke.

Am Ende eine Probe: alle Lagerkräfte zusammen sind die Last, abzüglich
dessen, was neben den Platten liegt oder auf einem Streifen, der nicht trägt.

DIE LAGERKRÄFTE:
Eine Stütze bekommt die Summe der Kräfte aller Träger auf ihr. Ein
Linienlager bekommt von jedem Träger, der es kreuzt, dessen Kraft --
gleichmässig verteilt über das Stück des Lagers, über das der Träger geht --
und bei Einspannung dessen Moment ebenso: ein Verlauf in kN/m und kNm/m
längs des Lagers.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.aufteilung import Aufteilungen, aufteilen
from opencivil.decke.geometrie import Punkt
from opencivil.decke.lasten import Belastung, belasten, kombiniert
from opencivil.decke.modell import Decke
from opencivil.decke.streifen import (
    LINIENLAGER, STUETZE, UNTERZUG, Auflager, Streifen, Traeger, Zerlegung, pressung, zerlegen,
)
from opencivil.decke.traeger import Einzellast, Streckenlast, Stueck, Teillast, statik
from opencivil.stabwerk.system import Meldung

#: Unter diesem Anteil der Last gilt die Probe als erfüllt.
PROBE = 1e-6


@dataclass(frozen=True)
class Lagerkraft:
    """Was ein Lager auf einen Träger ausübt: ``F`` nach oben in N, ``C`` im Gegenuhrzeigersinn in Nm."""

    auflager: Auflager
    F: float
    C: float


@dataclass
class Traegerergebnis:
    traeger: Traeger
    lasten: List[Teillast]
    """Was auf ihm liegt, ohne seine Lagerkräfte -- in m ab seinem Anfang."""

    lagerkraefte: List[Lagerkraft]
    stuecke: List[Stueck]
    """Querkraft und Moment längs des Trägers, für den ganzen Streifen (N, Nm)."""


@dataclass(frozen=True)
class Wandkraft:
    """Was ein Träger in ein Linienlager gibt -- gleichmässig über das Stück ``a → b``."""

    traeger: str
    a: Punkt
    b: Punkt
    F: float
    """Nach unten auf das Lager, in N."""

    C: float
    """Das Einspannmoment, in Nm -- positiv, wenn es den Träger im Gegenuhrzeigersinn hält."""

    @property
    def laenge(self) -> float:
        return math.hypot(self.b[0] - self.a[0], self.b[1] - self.a[1])

    @property
    def je_meter(self) -> Tuple[float, float]:
        """``(r, m)``: Kraft in N/m und Moment in Nm/m."""
        return self.F / self.laenge, self.C / self.laenge


@dataclass
class Fallergebnis:
    name: str
    summe: float
    """Die ganze Last, in N."""

    daneben: float
    """Was davon neben den Platten liegt."""

    traeger: Dict[str, Traegerergebnis] = field(default_factory=dict)
    stuetzen: Dict[str, List[Tuple[str, float]]] = field(default_factory=dict)
    """Je Stütze, was jeder Träger auf ihr in sie gibt, in N."""

    linienlager: Dict[str, List[Wandkraft]] = field(default_factory=dict)
    nicht_getragen: float = 0.0
    """Was auf Trägern liegt, die nicht tragen."""

    meldungen: List[Meldung] = field(default_factory=list)

    def stuetzenkraft(self, name: str) -> float:
        return sum(F for _, F in self.stuetzen.get(name, ()))

    def wandkraft(self, name: str) -> float:
        return sum(w.F for w in self.linienlager.get(name, ()))

    @property
    def lagerkraft(self) -> float:
        """Alle Kräfte in Linienlager und Stützen zusammen."""
        return (sum(self.stuetzenkraft(n) for n in self.stuetzen)
                + sum(self.wandkraft(n) for n in self.linienlager))

    @property
    def fehlbetrag(self) -> float:
        """Was die Lager weniger tragen, als auf den Trägern liegt -- null bis auf Rundung."""
        return self.summe - self.daneben - self.nicht_getragen - self.lagerkraft


@dataclass
class Ergebnis:
    decke: Decke
    zerlegung: Zerlegung
    aufteilungen: Optional[Aufteilungen]
    faelle: List[Fallergebnis]
    meldungen: List[Meldung]

    def fall(self, name: str) -> Fallergebnis:
        for f in self.faelle:
            if f.name == name:
                return f
        raise KeyError(f"Einen Fall «{name}» gibt es nicht. Bekannt: {', '.join(f.name for f in self.faelle)}.")


def rechnen(decke: Decke) -> Ergebnis:
    """Die Decke nach der Streifenmethode, je Lastfall und Kombination."""
    zerlegung = zerlegen(decke)
    meldungen = list(zerlegung.meldungen)
    if any(m.fehler for m in meldungen):
        return Ergebnis(decke, zerlegung, None, [], meldungen)
    aufteilungen = aufteilen(decke, zerlegung)
    meldungen.extend(aufteilungen.meldungen)
    belastungen = {lf.name: belasten(decke, zerlegung, aufteilungen, lf) for lf in decke.lastfaelle}
    faelle = [fall(name, b, zerlegung) for name, b in belastungen.items()]
    faelle.extend(fall(k.name, kombiniert(belastungen, k), zerlegung) for k in decke.kombinationen)
    for f in faelle:
        if abs(f.fehlbetrag) > PROBE * max(abs(f.summe), 1.0):
            f.meldungen.append(Meldung(
                f"Die Probe geht nicht auf: die Lager tragen {f.lagerkraft / 1e3:.6g} kN, "
                f"auf den Trägern liegen {(f.summe - f.daneben - f.nicht_getragen) / 1e3:.6g} kN."))
    return Ergebnis(decke, zerlegung, aufteilungen, faelle, meldungen)


def fall(name: str, belastung: Belastung, zerlegung: Zerlegung) -> Fallergebnis:
    """Ein Lastfall oder eine Kombination: alle Träger, von den Feldstreifen zu den Unterzügen."""
    heraus = Fallergebnis(name, belastung.summe, belastung.daneben, meldungen=list(belastung.meldungen))
    uebertragen: Dict[str, List[Teillast]] = {}
    for streifen in sorted(zerlegung.streifen, key=lambda s: s.stufe):
        lasten = belastung.je_streifen.get(streifen.name, []) + uebertragen.get(streifen.name, [])
        if not lasten:
            continue
        if not streifen.traeger:
            heraus.nicht_getragen += sum(_summe(l) for l in lasten)
            heraus.meldungen.append(Meldung(f"Auf «{streifen.name}» liegt Last, aber er liegt auf keiner Platte.",
                                            (streifen.name,)))
            continue
        for traeger, lokal in auf_traeger(streifen, lasten):
            gesamt = sum(_summe(l) for l in lokal)
            if not lokal or not any(_summe(l) or (isinstance(l, Einzellast) and l.C) for l in lokal):
                continue
            if not traeger.balken.stabil:
                heraus.nicht_getragen += gesamt
                heraus.meldungen.append(Meldung(
                    f"Der Streifen «{traeger.name}» trägt nicht -- {_warum(traeger)} "
                    f"{gesamt / 1e3:.3g} kN fallen aus.", (traeger.name,)))
                continue
            kraefte = [Lagerkraft(a, F, C) for a, (F, C) in
                       zip(traeger.auflager, traeger.balken.lagerkraefte(lokal))]
            stuecke = statik(traeger.L, lokal + gegenkraefte(kraefte))
            heraus.traeger[traeger.name] = Traegerergebnis(traeger, lokal, kraefte, stuecke)
            for k in kraefte:
                _weitergeben(k, traeger, zerlegung, heraus, uebertragen)
    return heraus


def auf_traeger(streifen: Streifen, lasten: Sequence[Teillast]) -> List[Tuple[Traeger, List[Teillast]]]:
    """
    Die Lasten eines Streifens (in ``s`` seiner Richtung) auf seine Träger,
    in m ab deren Anfang. Was zwischen oder hinter den Trägern liegt -- an
    einem schiefen Rand ein Zwickel --, kommt als Einzellast an das nächste
    Ende.
    """
    je: Dict[str, List[Teillast]] = {t.name: [] for t in streifen.traeger}

    def ans_naechste_ende(s: float, P: float) -> None:
        t = streifen.traeger_bei(s)
        je[t.name].append(Einzellast(min(max(s - t.s0, 0.0), t.L), P))

    for l in lasten:
        if isinstance(l, Einzellast):
            t = streifen.traeger_bei(l.a)
            je[t.name].append(Einzellast(min(max(l.a - t.s0, 0.0), t.L), l.P, l.C))
            continue
        frei = [(l.a, l.b)]
        for t in streifen.traeger:
            a, b = max(l.a, t.s0), min(l.b, t.s1)
            if b > a:
                je[t.name].append(Streckenlast(a - t.s0, b - t.s0, l.bei(a), l.bei(b)))
                frei = [(x, y) for p, q in frei for x, y in ((p, min(q, a)), (max(p, b), q)) if y > x]
        for a, b in frei:
            if b - a > 1e-12:
                teil = Streckenlast(a, b, l.bei(a), l.bei(b))
                if teil.summe:
                    ans_naechste_ende(a + _schwerpunkt(teil), teil.summe)
    return [(t, je[t.name]) for t in streifen.traeger]


def gegenkraefte(kraefte: Sequence[Lagerkraft]) -> List[Teillast]:
    """
    Die Lagerkräfte als Lasten auf den Träger: ein Linienlager als Punkt, ein
    Flächenlager als gleichmässige Pressung über seine Fläche -- nach oben,
    also negativ.
    """
    heraus: List[Teillast] = []
    for k in kraefte:
        if k.auflager.pressung:
            heraus.extend(p.mal(-k.F) for p in k.auflager.pressung)
            if k.C:
                heraus.append(Einzellast(k.auflager.s, 0.0, k.C))
        else:
            heraus.append(Einzellast(k.auflager.s, -k.F, k.C))
    return heraus


def _weitergeben(k: Lagerkraft, traeger: Traeger, zerlegung: Zerlegung, heraus: Fallergebnis,
                 uebertragen: Dict[str, List[Teillast]]) -> None:
    """Die Kraft eines Lagers auf den Träger geht, umgekehrt, in das, worauf er liegt."""
    a = k.auflager
    if not (k.F or k.C):
        return
    if a.art == LINIENLAGER:
        heraus.linienlager.setdefault(a.name, []).append(Wandkraft(traeger.name, a.strecke[0], a.strecke[1],
                                                                   k.F, k.C))
    elif a.art == STUETZE:
        heraus.stuetzen.setdefault(a.name, []).append((traeger.name, k.F))
    elif a.art == UNTERZUG:
        unterzug = zerlegung[a.name]
        if a.kontakt:
            lasten = [p.mal(k.F) for p in pressung(a.kontakt, unterzug.richtung.n)]
        else:
            streifen = zerlegung[traeger.streifen]
            punkt = streifen.richtung.punkt(traeger.s0 + a.s, streifen.mitte)
            lasten = [Einzellast(geo.skalar(punkt, unterzug.richtung.n), k.F)]
        uebertragen.setdefault(a.name, []).extend(lasten)


def _summe(l: Teillast) -> float:
    return l.summe if isinstance(l, Streckenlast) else l.P


def _schwerpunkt(l: Streckenlast) -> float:
    """Wo die Resultierende einer Streckenlast liegt, ab ihrem Anfang."""
    L = l.b - l.a
    if abs(l.p_a + l.p_b) <= 1e-300:
        return 0.5 * L
    return L * (l.p_a + 2.0 * l.p_b) / (3.0 * (l.p_a + l.p_b))


def _warum(traeger: Traeger) -> str:
    hoehe = [a for a in traeger.auflager if a.vertikal]
    if not traeger.auflager:
        return "er liegt auf nichts."
    if not hoehe:
        return "nichts hält ihn in der Höhe."
    return f"er liegt nur auf «{hoehe[0].name}», und nichts hält seine Drehung."
