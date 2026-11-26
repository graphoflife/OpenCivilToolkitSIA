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
   teilen (Stahlbeton II, 7.2 Platten, Folie 33: die Pressung des
   Flächenlagers wird zur Last des versteckten Unterzugs).
3. Was in Linienlager und Stützen geht, sind die Lagerkräfte der Decke.

Am Ende eine Probe: alle Lagerkräfte zusammen sind die Last, abzüglich
dessen, was neben den Platten liegt oder auf einem Streifen, der nicht trägt.

DIE LAGERKRÄFTE:
Eine Stütze bekommt die Summe der Kräfte aller Träger auf ihr. Ein
Linienlager bekommt von jedem Träger, der es kreuzt, dessen Kraft --
gleichmässig verteilt über das Stück des Lagers, über das der Träger geht --
und bei Einspannung dessen Moment ebenso: ein Verlauf in kN/m und kNm/m
längs des Lagers, das Moment mit dem Vorzeichen der Platte
(:func:`lagerverlauf`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.aufteilung import Aufteilungen, aufteilen
from opencivil.decke.geometrie import Punkt
from opencivil.decke.lasten import Belastung, belasten, kn, kombiniert
from opencivil.decke.modell import Decke, Linienlager
from opencivil.decke.streifen import (
    LINIENLAGER, STUETZE, UNTERZUG, Auflager, Streifen, Traeger, Warum, Zerlegung, pressung, zerlegen,
)
from opencivil.decke.traeger import GLEICH, Einzellast, Streckenlast, Teillast, statik, wert
from opencivil.stabwerk.system import Meldung
from opencivil.stabwerk.verlauf import EbenesIntervall

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
    stuecke: List[EbenesIntervall]
    """Querkraft und Moment längs des Trägers, für den ganzen Streifen (N, Nm) -- aus :func:`statik`."""

    @property
    def last(self) -> float:
        """Was auf ihm liegt, zusammen, in N."""
        return sum(_summe(l) for l in self.lasten)

    def beidseits(self, s: float) -> Tuple[float, float]:
        """``M`` knapp vor und knapp nach der Stelle ``s``, in Nm -- vor seinem Anfang und nach seinem Ende null."""
        vor = wert(self.stuecke, "M", s, links=True) if s > GLEICH else 0.0
        nach = wert(self.stuecke, "M", s) if s < self.traeger.L - GLEICH else 0.0
        return vor, nach


@dataclass(frozen=True)
class Wandkraft:
    """Was ein Träger in ein Linienlager gibt -- gleichmässig über das Stück ``a → b``."""

    traeger: str
    a: Punkt
    b: Punkt
    F: float
    """Nach unten auf das Lager, in N."""

    vor: float
    nach: float
    """
    Hält das Lager die Drehung, das Moment des Trägers knapp vor und knapp
    nach ihm, in Nm, ``M > 0`` zieht unten -- vor seinem Anfang und nach
    seinem Ende null. Was das Lager hält, ist der Unterschied. Ein Lager,
    das die Drehung nicht hält, hält kein Moment: dann beide null.
    """

    n: Punkt
    """Die Richtung des Trägers: in ihr liegt ``nach`` hinter dem Lager."""

    @property
    def laenge(self) -> float:
        return math.hypot(self.b[0] - self.a[0], self.b[1] - self.a[1])

    @property
    def r(self) -> float:
        """Die Kraft je Meter des Lagers, in N/m."""
        return self.F / self.laenge


@dataclass(frozen=True)
class Ausfall(Meldung):
    """
    Was in einem Fall ausfaellt, weil Streifen nicht tragen: der ganze Satz
    in ``text`` -- «… 80 kN fallen aus.» --, dazu ``grund`` ohne die Kraft
    und die Kraft ``F`` in N. Ueber die Faelle gesammelt
    (:meth:`Ergebnis.fallmeldungen`), steht der Grund einmal und die Kraft
    je Fall dahinter. Grau: es fehlt ein Lager oder ein Unterzug, und der
    Rest rechnet (Benutzer, 2026-11-19).
    """

    fehler: bool = False
    grund: str = ""
    F: float = 0.0


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

    def fallmeldungen(self) -> List[Meldung]:
        """
        Was die Faelle melden, jede Meldung einmal, vorn die Faelle, in denen
        sie steht: «In allen Fällen: …», sonst ««LF 1», «GZT»: …». Ein
        :class:`Ausfall` aus demselben Grund in mehreren Faellen steht einmal,
        die Kraft je Fall dahinter: «… Es fallen aus: «g» 80 kN, «GZT»
        228 kN.» Bis 2026-11-20 stand jede Meldung je Fall -- in vier
        Lastfaellen und drei Kombinationen siebenmal derselbe Satz (Benutzer).
        """
        je: Dict[tuple, Tuple[Meldung, List[Tuple[str, Meldung]]]] = {}
        for f in self.faelle:
            for m in f.meldungen:
                schluessel = (("ausfall", m.grund, m.elemente) if isinstance(m, Ausfall)
                              else ("satz", m.text, m.fehler))
                je.setdefault(schluessel, (m, []))[1].append((f.name, m))
        heraus = []
        for m, wo in je.values():
            if isinstance(m, Ausfall) and len(wo) > 1:
                kraefte = ", ".join(f"«{name}» {kn(a.F)} kN" for name, a in wo)
                heraus.append(replace(m, text=f"{m.grund} Es fallen aus: {kraefte}."))
                continue
            namen = [name for name, _ in wo]
            vorn = ("In allen Fällen" if 1 < len(namen) == len(self.faelle)
                    else ", ".join(f"«{n}»" for n in namen))
            heraus.append(replace(m, text=f"{vorn}: {m.text}"))
        return heraus


def rechnen(decke: Decke) -> Ergebnis:
    """Die Decke nach der Streifenmethode, je Lastfall und Kombination."""
    zerlegung = zerlegen(decke)
    meldungen = list(zerlegung.meldungen)
    # Ohne Streifen ist nichts zu rechnen: noch keine Platte, oder es gäbe zu viele.
    if not zerlegung.streifen or any(m.haelt_an for m in meldungen):
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
    """
    Ein Lastfall oder eine Kombination: alle Träger, von den Feldstreifen zu
    den Unterzügen. Was auf Trägern liegt, die nicht tragen, sagt eine
    Meldung je Grund -- bis 2026-11-19 eine je Träger, und eine Platte ohne
    Lager gab je Fall vierzig gleiche Zeilen. Ebenso eine für alle Streifen
    mit Last, die auf keiner Platte liegen (bis 2026-11-20 eine je Streifen).
    """
    heraus = Fallergebnis(name, belastung.summe, belastung.daneben, meldungen=list(belastung.meldungen))
    uebertragen: Dict[str, List[Teillast]] = {}
    ausfall: Dict[Warum, List[Tuple[str, float]]] = {}
    ohne_platte: List[str] = []
    for streifen in sorted(zerlegung.streifen, key=lambda s: s.stufe):
        lasten = belastung.je_streifen.get(streifen.name, []) + uebertragen.get(streifen.name, [])
        if not lasten:
            continue
        if not streifen.traeger:
            heraus.nicht_getragen += sum(_summe(l) for l in lasten)
            ohne_platte.append(streifen.name)
            continue
        for traeger, lokal in auf_traeger(streifen, lasten):
            gesamt = sum(_summe(l) for l in lokal)
            if not lokal or not any(_summe(l) or (isinstance(l, Einzellast) and l.C) for l in lokal):
                continue
            if not traeger.balken.stabil:
                heraus.nicht_getragen += gesamt
                ausfall.setdefault(traeger.warum_nicht(), []).append((traeger.name, gesamt))
                continue
            kraefte = [Lagerkraft(a, F, C) for a, (F, C) in
                       zip(traeger.auflager, traeger.balken.lagerkraefte(lokal))]
            ergebnis = Traegerergebnis(traeger, lokal, kraefte, statik(traeger.L, lokal + gegenkraefte(kraefte)))
            heraus.traeger[traeger.name] = ergebnis
            for k in kraefte:
                _weitergeben(k, ergebnis, zerlegung, heraus, uebertragen)
    if ohne_platte:
        wer = (f"Auf «{ohne_platte[0]}» liegt Last, aber er liegt" if len(ohne_platte) == 1
               else f"Auf {len(ohne_platte)} Streifen liegt Last, aber sie liegen")
        heraus.meldungen.append(Meldung(f"{wer} auf keiner Platte.", tuple(ohne_platte)))
    for warum, traeger in ausfall.items():
        namen = tuple(n for n, _ in traeger)
        grund = (f"Der Streifen «{namen[0]}» trägt nicht – {warum.einer}" if len(namen) == 1
                 else f"{len(namen)} Streifen tragen nicht – {warum.mehrere}")
        F = sum(F for _, F in traeger)
        heraus.meldungen.append(Ausfall(f"{grund} {kn(F)} kN fallen aus.", namen, grund=grund, F=F))
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


def _weitergeben(k: Lagerkraft, ergebnis: Traegerergebnis, zerlegung: Zerlegung, heraus: Fallergebnis,
                 uebertragen: Dict[str, List[Teillast]]) -> None:
    """Die Kraft eines Lagers auf den Träger geht, umgekehrt, in das, worauf er liegt."""
    a, traeger = k.auflager, ergebnis.traeger
    if not (k.F or k.C):
        return
    if a.art == LINIENLAGER:
        vor, nach = ergebnis.beidseits(a.s) if a.eingespannt else (0.0, 0.0)
        heraus.linienlager.setdefault(a.name, []).append(Wandkraft(
            traeger.name, a.strecke[0], a.strecke[1], k.F, vor, nach, zerlegung[traeger.streifen].richtung.n))
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


def lagerverlauf(lager: Linienlager, kraefte: Sequence[Wandkraft]) -> List[Tuple[float, float, float, float]]:
    """
    Längs eines Linienlagers, was die Träger in es geben: Stufen
    ``(u_a, u_b, r, m)`` von seinem Anfang bis zu seinem Ende, ``u`` in m ab
    ``lager.a``, ``r`` nach unten in N/m und ``m`` in Nm/m: das Moment, das
    es hält, mit dem Vorzeichen der Platte -- negativ, wo es oben zieht, wie
    herum das Lager auch gezeichnet ist (:func:`_gehalten`). Wo zwei Träger
    dasselbe Stück tragen, zählen beide; ein schiefer gibt quer zum Lager
    cos² seines Winkels weiter, wie die Platte (Folie 14).
    """
    L = math.dist(lager.a, lager.b)
    e = ((lager.b[0] - lager.a[0]) / L, (lager.b[1] - lager.a[1]) / L)
    links = (-e[1], e[0])

    def u(p: Punkt) -> float:
        return geo.skalar((p[0] - lager.a[0], p[1] - lager.a[1]), e)

    stuecke = []
    for w in kraefte:
        cos = geo.skalar(w.n, links)
        vor, nach = (M * abs(cos) / w.laenge for M in (w.vor, w.nach))
        # Was hinter dem Lager liegt, «nach», liegt links von a → b, wenn der Träger nach links läuft.
        seiten = (nach, vor) if cos > 0.0 else (vor, nach)
        stuecke.append((*sorted((u(w.a), u(w.b))), w.r, *seiten))
    stellen: List[float] = []
    for x in sorted([0.0, L, *(x for s in stuecke for x in s[:2])]):
        if not stellen or x - stellen[-1] > geo.TOLERANZ:
            stellen.append(x)
    heraus = []
    for ua, ub in zip(stellen, stellen[1:]):
        mitte = 0.5 * (ua + ub)
        auf = [s for s in stuecke if s[0] <= mitte <= s[1]]
        heraus.append((ua, ub, sum(s[2] for s in auf),
                       _gehalten(sum(s[3] for s in auf), sum(s[4] for s in auf))))
    return heraus


def _gehalten(links: float, rechts: float) -> float:
    """
    Was ein Lager an Moment hält, je Meter, wenn die Platte links von ihm
    mit ``links`` an ihm zieht und rechts mit ``rechts``: den Unterschied,
    mit dem Vorzeichen der Seite, die stärker zieht. An einem Rand ist die
    andere Seite null -- dann ist es das Moment der Platte dort.
    """
    return links - rechts if abs(links) >= abs(rechts) else rechts - links


def spitzen(stufen: Sequence[Tuple[float, float, float, float]]) -> Tuple[float, float]:
    """Aus den Stufen eines Linienlagers (:func:`lagerverlauf`): je der Wert von ``r`` und ``m`` mit dem grössten Betrag."""
    return (max((r for _, _, r, _ in stufen), key=abs, default=0.0),
            max((m for *_, m in stufen), key=abs, default=0.0))


def _summe(l: Teillast) -> float:
    return l.summe if isinstance(l, Streckenlast) else l.P


def _schwerpunkt(l: Streckenlast) -> float:
    """Wo die Resultierende einer Streckenlast liegt, ab ihrem Anfang."""
    L = l.b - l.a
    if abs(l.p_a + l.p_b) <= 1e-300:
        return 0.5 * L
    return L * (l.p_a + 2.0 * l.p_b) / (3.0 * (l.p_a + l.p_b))

