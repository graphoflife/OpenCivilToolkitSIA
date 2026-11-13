"""
opencivil/decke/streifen.py -- die Decke in Streifen zerlegt.

VERANTWORTUNG:
Aus der :class:`~opencivil.decke.modell.Decke` die Streifen der
Streifenmethode: je Richtung der Lastabtragung ein Satz paralleler
Feldstreifen, dazu die versteckten Unterzüge als Streifen eigener Breite.
Jeder Streifen zerfällt in Träger -- Stücke, die über Platten
durchlaufen -- und jeder Träger weiss, worauf er liegt.

DIE STREIFEN EINER RICHTUNG:
Alle Platten, die in einer Richtung tragen, bilden ihre Familie; über sie
hinweg laufen die Streifen dieser Richtung durch. Quer zur Richtung wird
die Familie an festen Stellen geteilt -- an den Ecken der Platten, an den
Rändern paralleler Unterzüge, an den Enden der Lager, an den Rändern der
Stützenbereiche und der Unterzüge, die quer liegen. Was dazwischen liegt,
wird in gleich breite Streifen von höchstens
:attr:`~opencivil.decke.modell.Decke.streifenbreite` geteilt. So liegt
keine Ecke im Innern eines Streifens, und ein Lager, ein Unterzug, ein
Stützenbereich überdeckt einen Streifen ganz oder gar nicht.

WORAUF EIN TRÄGER LIEGT:
* Auf einem **Linienlager**, das ihn quer schneidet -- als Punkt; es hält
  die Höhe, die Drehung oder beides.
* Auf einem **Unterzug höherer Stufe**, den seine Achse quer kreuzt; die
  Feldstreifen haben Stufe 0. Ein Flächenlager mit gleichmässiger Pressung
  über die Fläche, die beide teilen (Stahlbeton II, 7.2 Platten, Folie 33).
* Auf einer **Stütze**, deren Stützenbereich seine Achse kreuzt -- ebenso
  ein Flächenlager (Folie 36: «Lastverteilelemente als Flächenlager mit
  gleichmässiger Pressung»).

Liegen zwei davon an derselben Stelle -- die eine in der Fläche der
anderen --, trägt das erste in dieser Folge: Linienlager, Unterzug (höhere
Stufe zuerst), Stütze. So liegt in der Musterlösung des Kolloquiums 4 der
Unterzug in x-Richtung über der Stütze auf den Unterzügen in y-Richtung,
und erst diese auf der Stütze.

Ein Unterzug parallel zu einer Richtung nimmt in seiner Fläche deren
Lastanteil auf; quer liegende Streifen laufen über ihn hinweg und legen
ihren Anteil auf ihn (:mod:`~opencivil.decke.lasten`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Aufteilung, Decke, Platte, Stuetze, Unterzug
from opencivil.decke.traeger import Balken, Halt, Streckenlast
from opencivil.stabwerk.system import Meldung

#: Wie nahe zwei Teilungsstellen quer liegen dürfen, in m -- näher gelten sie als eine.
TEILUNG = 1e-3

#: So weit über sein Ende hinaus sucht ein Träger seine Lager, in m.
RAND = 1e-4

#: Mehr Streifen rechnet die Decke nicht -- sonst warten Benutzer und Browser zu lange.
STREIFEN_HOECHSTENS = 4000

#: Unter diesem Winkel gelten zwei Richtungen als parallel, in rad.
PARALLEL = 1e-6

LINIENLAGER, UNTERZUG, STUETZE = "linienlager", "unterzug", "stuetze"


# ===========================================================================
# Richtungen
# ===========================================================================


@dataclass(frozen=True)
class Richtung:
    """Eine Richtung der Lastabtragung: Winkel in [0, π), ``n`` längs, ``t`` quer."""

    winkel: float
    n: Punkt
    t: Punkt
    name: str

    def parallel(self, andere: "Richtung") -> bool:
        return abs(math.sin(self.winkel - andere.winkel)) < PARALLEL

    def punkt(self, s: float, tau: float) -> Punkt:
        """Der Punkt mit ``p·n = s`` und ``p·t = τ``."""
        return (s * self.n[0] + tau * self.t[0], s * self.n[1] + tau * self.t[1])


def richtung(winkel: float) -> Richtung:
    """Die Richtung zu einem Winkel -- auf [0, π) gebracht; ``x`` und ``y`` heissen so."""
    w = math.fmod(winkel, math.pi)
    if w < 0.0:
        w += math.pi
    if w > math.pi - PARALLEL or w < PARALLEL:
        w = 0.0
    if abs(w - math.pi / 2.0) < PARALLEL:
        w = math.pi / 2.0
    n, t = geo.richtung(w)
    if w == 0.0:
        name = "x"
    elif w == math.pi / 2.0:
        name = "y"
    else:
        name = f"{math.degrees(w):.4g}°"
    return Richtung(w, n, t, name)


def richtung_der_strecke(a: Punkt, b: Punkt) -> Richtung:
    return richtung(math.atan2(b[1] - a[1], b[0] - a[0]))


# ===========================================================================
# Lager, Träger, Streifen
# ===========================================================================


@dataclass(frozen=True)
class Auflager:
    """
    Worauf ein Träger an einer Stelle liegt. ``s`` in m ab dem Anfang des
    Trägers -- bei einem Flächenlager der Schwerpunkt der Fläche, die beide
    teilen (``kontakt``). Dort drückt das Lager mit ``pressung``, je Kraft
    eins: ein Verlauf über ``s``, dessen Integral eins ist.
    """

    s: float
    vertikal: bool
    eingespannt: bool
    art: str
    name: str
    kontakt: Tuple[Punkt, ...] = ()
    strecke: Tuple[Punkt, ...] = ()
    """Bei einem Linienlager: das Stück von ihm, über das der Streifen geht."""

    pressung: Tuple[Streckenlast, ...] = ()

    @property
    def bereich(self) -> Tuple[float, float]:
        """Von wo bis wo das Lager drückt, in ``s`` des Trägers."""
        if not self.pressung:
            return (self.s, self.s)
        return (min(p.a for p in self.pressung), max(p.b for p in self.pressung))


@dataclass
class Lage:
    """Wo eine Stelle auf ihrem Träger liegt -- für die Aufteilung der Last."""

    traegt: bool
    spannweite: float
    """Die Spannweite des Felds, in dem sie liegt; bei einer Kragplatte das Doppelte ihrer Länge."""

    abstand: float
    """Bis zum nächsten Lager, das die Höhe hält -- null in seiner Fläche."""


@dataclass
class Traeger:
    """Ein Stück eines Streifens, das von einem Ende zum anderen durchläuft."""

    name: str
    streifen: str
    s0: float
    s1: float
    """Anfang und Ende in ``s = p·n`` der Richtung des Streifens."""

    abschnitte: Tuple[Tuple[float, float, float], ...]
    """``(von, bis, EI)`` in m ab dem Anfang und Nm²."""

    auflager: List[Auflager]
    _balken: Optional[Balken] = field(default=None, repr=False)

    @property
    def L(self) -> float:
        return self.s1 - self.s0

    @property
    def balken(self) -> Balken:
        if self._balken is None:
            self._balken = Balken(self.L, self.abschnitte,
                                  [Halt(a.s, a.vertikal, a.eingespannt) for a in self.auflager])
        return self._balken

    def lage(self, s: float) -> Lage:
        """Spannweite und Abstand zum Lager an der Stelle ``s`` (m ab dem Anfang)."""
        hoehe = [a for a in self.auflager if a.vertikal]
        if not self.balken.stabil or not hoehe:
            return Lage(False, math.inf, math.inf)
        abstand = min(max(a.bereich[0] - s, s - a.bereich[1], 0.0) for a in hoehe)
        # Je Stelle, was dort ist: «h» hält die Höhe, «d» nur die Drehung, «e» ist ein freies Ende.
        stellen = [(a.s, "h" if a.vertikal else "d") for a in self.auflager] + [(0.0, "e"), (self.L, "e")]
        links = max((st for st in stellen if st[0] <= s), key=lambda st: (st[0], st[1] != "e"),
                    default=(0.0, "e"))
        rechts = min((st for st in stellen if st[0] > s), key=lambda st: (st[0], st[1] == "e"),
                     default=(self.L, "e"))
        arten = {links[1], rechts[1]}
        if arten == {"h"}:
            weite = rechts[0] - links[0]
        elif "h" in arten:
            # Kragarm oder Feld bis zu einer Symmetrieachse: die Hälfte eines doppelt so langen Felds.
            weite = 2.0 * (rechts[0] - links[0])
        else:
            weite = math.inf
        return Lage(True, weite if weite > 1e-9 else math.inf, abstand)


@dataclass
class Streifen:
    """
    Ein Streifen: quer von ``von`` bis ``bis`` in ``τ = p·t``. Ein
    Feldstreifen hat Stufe 0; ein Unterzug seine Stufe, seinen Eintrag und
    sein Gebiet -- das Rechteck, das er belegt.
    """

    name: str
    richtung: Richtung
    von: float
    bis: float
    stufe: int = 0
    unterzug: Optional[Unterzug] = None
    gebiet: Tuple[Punkt, ...] = ()
    traeger: List[Traeger] = field(default_factory=list)

    @property
    def breite(self) -> float:
        return self.bis - self.von

    @property
    def mitte(self) -> float:
        return 0.5 * (self.von + self.bis)

    @property
    def laengs(self) -> Tuple[float, float]:
        """Wie weit der Streifen längs reicht -- ein Unterzug über sein Gebiet, ein Feldstreifen unbegrenzt."""
        if self.gebiet:
            return geo.bereich(self.gebiet, self.richtung.n)
        return (-math.inf, math.inf)

    def band(self, s_von: float, s_bis: float) -> List[Punkt]:
        """Das Rechteck des Streifens von ``s_von`` bis ``s_bis``, im Gegenuhrzeigersinn."""
        r = self.richtung
        return [r.punkt(s_von, self.von), r.punkt(s_bis, self.von),
                r.punkt(s_bis, self.bis), r.punkt(s_von, self.bis)]

    def traeger_bei(self, s: float) -> Optional[Traeger]:
        """Der Träger, auf dem ``s = p·n`` liegt -- sonst der nächste."""
        if not self.traeger:
            return None
        return min(self.traeger, key=lambda t: max(t.s0 - s, s - t.s1, 0.0))


@dataclass
class Gruppe:
    """Platten mit denselben zwei Richtungen -- für sie gilt eine Aufteilung der Last."""

    richtungen: Tuple[Richtung, Richtung]
    platten: List[Platte]
    stuecke: List[List[Punkt]]
    """Die Platten in konvexen Stücken."""


@dataclass
class Zerlegung:
    richtungen: List[Richtung]
    streifen: List[Streifen]
    gruppen: List[Gruppe]
    stuetzenbereiche: Dict[str, List[Punkt]]
    parallele: Dict[str, List[Streifen]]
    """Je Feldstreifen die Unterzüge in seiner Richtung, in deren Breite er liegt."""

    meldungen: List[Meldung]

    def __post_init__(self) -> None:
        self._nach_name = {s.name: s for s in self.streifen}

    def __getitem__(self, name: str) -> Streifen:
        return self._nach_name[name]

    def feldstreifen(self, r: Richtung) -> List[Streifen]:
        return [s for s in self.streifen if s.stufe == 0 and s.richtung.parallel(r)]

    @property
    def unterzuege(self) -> List[Streifen]:
        return [s for s in self.streifen if s.stufe > 0]

    @property
    def traeger(self) -> List[Traeger]:
        return [t for s in self.streifen for t in s.traeger]


def richtungen_der_platte(p: Platte) -> Tuple[Richtung, Richtung]:
    return richtung(p.richtungen[0]), richtung(p.richtungen[1])


def stuetzenbereich(stuetze: Stuetze, unterzuege: Sequence[Unterzug]) -> List[Punkt]:
    """
    Die Fläche ``lx × ly``, über die die Stütze trägt. Ohne Angabe ein
    Quadrat, so breit wie der breiteste Unterzug über ihr und mindestens so
    gross wie die Stütze -- in der Musterlösung des Kolloquiums 4 die
    1 m × 1 m, wo sich die Unterzüge kreuzen. Nach Vorgabe, nicht
    nachgeschlagen: Folie 39 lässt die Grösse frei.
    """
    seite = max([stuetze.bx, stuetze.by] + [u.breite for u in unterzuege
                                            if _lang(u) and geo.innen(stuetze.ort, geo.rechteck(u.a, u.b, u.breite))])
    return geo.achsrechteck(stuetze.ort, stuetze.lx or seite, stuetze.ly or seite)


def _lang(u: Unterzug) -> bool:
    return math.hypot(u.b[0] - u.a[0], u.b[1] - u.a[1]) > geo.TOLERANZ


# ===========================================================================
# Zerlegen
# ===========================================================================


def zerlegen(decke: Decke) -> Zerlegung:
    """Die Streifen, ihre Träger und deren Lager -- oder, was dem im Weg steht."""
    meldungen = pruefen(decke)
    if any(m.fehler for m in meldungen):
        return Zerlegung([], [], [], {}, {}, meldungen)
    stuecke = {p.name: geo.dreiecke(p.ecken) for p in decke.platten}
    gruppen: List[Gruppe] = []
    for p in decke.platten:
        r1, r2 = richtungen_der_platte(p)
        gruppe = next((g for g in gruppen if g.richtungen[0].parallel(r1) and g.richtungen[1].parallel(r2)), None)
        if gruppe is None:
            gruppe = Gruppe((r1, r2), [], [])
            gruppen.append(gruppe)
        gruppe.platten.append(p)
        gruppe.stuecke.extend(stuecke[p.name])
    richtungen: List[Richtung] = []
    for g in gruppen:
        for r in g.richtungen:
            if not any(r.parallel(q) for q in richtungen):
                richtungen.append(r)
    bereiche = {s.name: stuetzenbereich(s, decke.unterzuege) for s in decke.stuetzen}
    unterzuege = [_unterzug(u) for u in decke.unterzuege]
    feld: List[Streifen] = []
    for r in richtungen:
        platten = [p for p in decke.platten if any(r.parallel(q) for q in richtungen_der_platte(p))]
        feld.extend(_feldstreifen(r, platten, decke, unterzuege, bereiche, stuecke))
    if len(feld) > STREIFEN_HOECHSTENS:
        meldungen.append(Meldung(f"Das gäbe {len(feld)} Streifen -- mehr als {STREIFEN_HOECHSTENS}. "
                                 "Bitte die Streifenbreite grösser wählen."))
        return Zerlegung(richtungen, [], gruppen, bereiche, {}, meldungen)
    namen = {s.name for s in feld}
    for u in unterzuege:
        if u.name in namen:
            meldungen.append(Meldung(f"Der Unterzug «{u.name}» heisst wie ein Feldstreifen -- bitte umbenennen.",
                                     (u.name,)))
    if any(m.fehler for m in meldungen):
        return Zerlegung(richtungen, [], gruppen, bereiche, {}, meldungen)
    for s in feld:
        platten = [p for p in decke.platten if any(s.richtung.parallel(q) for q in richtungen_der_platte(p))]
        s.traeger = _traeger(s, platten, decke, unterzuege, bereiche, stuecke)
    for u in unterzuege:
        u.traeger = _traeger(u, decke.platten, decke, unterzuege, bereiche, stuecke)
        if not u.traeger:
            meldungen.append(Meldung(f"Der Unterzug «{u.name}» liegt auf keiner Platte.", (u.name,), fehler=False))
    parallele = {s.name: [u for u in unterzuege if u.richtung.parallel(s.richtung)
                          and u.von - TEILUNG <= s.von and s.bis <= u.bis + TEILUNG] for s in feld}
    return Zerlegung(richtungen, feld + sorted(unterzuege, key=lambda u: u.stufe), gruppen, bereiche,
                     parallele, meldungen)


def _unterzug(u: Unterzug) -> Streifen:
    r = richtung_der_strecke(u.a, u.b)
    tau = geo.skalar(u.a, r.t)
    return Streifen(u.name, r, tau - u.breite / 2.0, tau + u.breite / 2.0, u.stufe, u,
                    tuple(geo.rechteck(u.a, u.b, u.breite)))


def _feldstreifen(r: Richtung, platten: Sequence[Platte], decke: Decke, unterzuege: Sequence[Streifen],
                  bereiche: Dict[str, List[Punkt]], stuecke: Dict[str, List[List[Punkt]]]) -> List[Streifen]:
    """Die Feldstreifen einer Richtung, nach ihrer Lage quer geordnet und nummeriert."""
    unten, oben = math.inf, -math.inf
    teilung: List[float] = []
    for p in platten:
        lo, hi = geo.bereich(p.ecken, r.t)
        unten, oben = min(unten, lo), max(oben, hi)
        teilung.extend(geo.skalar(e, r.t) for e in p.ecken)
    for u in unterzuege:
        if u.richtung.parallel(r):
            teilung.extend((u.von, u.bis))
        else:
            teilung.extend(geo.bereich(u.gebiet, r.t))
    for w in decke.linienlager:
        teilung.extend((geo.skalar(w.a, r.t), geo.skalar(w.b, r.t)))
    for b in bereiche.values():
        teilung.extend(geo.bereich(b, r.t))
    stellen = [unten]
    for tau in sorted(t for t in teilung if unten < t < oben):
        if tau - stellen[-1] > TEILUNG and oben - tau > TEILUNG:
            stellen.append(tau)
    stellen.append(oben)
    baender: List[Tuple[float, float]] = []
    for a, b in zip(stellen, stellen[1:]):
        anzahl = max(1, math.ceil((b - a) / decke.streifenbreite - 1e-9))
        baender.extend((a + (b - a) * i / anzahl, a + (b - a) * (i + 1) / anzahl) for i in range(anzahl))
    # Nummeriert von links nach rechts, x-Streifen von unten nach oben.
    if r.t[0] < 0.0:
        baender.reverse()
    trenner = "" if r.name in ("x", "y") else " "
    return [Streifen(f"{r.name}{trenner}{i + 1}", r, a, b) for i, (a, b) in enumerate(baender)]


def _traeger(streifen: Streifen, platten: Sequence[Platte], decke: Decke, unterzuege: Sequence[Streifen],
             bereiche: Dict[str, List[Punkt]], stuecke: Dict[str, List[List[Punkt]]]) -> List[Traeger]:
    """Wo der Streifen über Platten läuft, ein Träger je zusammenhängendes Stück -- mit Steifigkeit und Lagern."""
    r = streifen.richtung
    lo, hi = streifen.laengs
    teile: List[Tuple[float, float, Platte]] = []
    for p in platten:
        for d in stuecke[p.name]:
            c = geo.im_band(d, r.t, streifen.von, streifen.bis)
            if c and streifen.gebiet:
                c = geo.schnitt(c, streifen.gebiet)
            if c:
                a, b = geo.bereich(c, r.n)
                teile.append((max(a, lo), min(b, hi), p))
    heraus: List[Traeger] = []
    for s0, s1 in geo.vereinigt([(a, b) for a, b, _ in teile if b > a]):
        if s1 - s0 <= RAND:
            continue
        heraus.append(Traeger("", streifen.name, s0, s1,
                              _abschnitte(streifen, s0, s1, [t for t in teile if t[0] < s1 and t[1] > s0]),
                              _auflager(streifen, s0, s1, decke, unterzuege, bereiche)))
    for i, t in enumerate(heraus):
        t.name = streifen.name if len(heraus) == 1 else f"{streifen.name}.{i + 1}"
    return heraus


def _abschnitte(streifen: Streifen, s0: float, s1: float,
                teile: Sequence[Tuple[float, float, Platte]]) -> Tuple[Tuple[float, float, float], ...]:
    """
    Die Biegesteifigkeit ``E · b · h³/12`` längs der Achse: je Platte, über
    die die Achse läuft. Wo sie neben den Platten läuft -- an einem schiefen
    Rand --, gilt die der nächsten.
    """
    r = streifen.richtung
    a, b = r.punkt(s0, streifen.mitte), r.punkt(s1, streifen.mitte)
    stuecke = []
    for p in {id(t[2]): t[2] for t in teile}.values():
        EI = p.E * streifen.breite * p.h ** 3 / 12.0
        for u0, u1 in geo.strecke_im_vieleck(a, b, p.ecken):
            stuecke.append((u0 * (s1 - s0), u1 * (s1 - s0), EI))
    if not stuecke:
        groesste = max(teile, key=lambda t: t[1] - t[0])[2]
        return ((0.0, s1 - s0, groesste.E * streifen.breite * groesste.h ** 3 / 12.0),)
    stuecke.sort()
    heraus = []
    for i, (von, bis, EI) in enumerate(stuecke):
        von = 0.0 if i == 0 else heraus[-1][1]
        bis = s1 - s0 if i == len(stuecke) - 1 else max(bis, von)
        heraus.append((von, bis, EI))
    return tuple(heraus)


def _auflager(streifen: Streifen, s0: float, s1: float, decke: Decke, unterzuege: Sequence[Streifen],
              bereiche: Dict[str, List[Punkt]]) -> List[Auflager]:
    r = streifen.richtung
    band = streifen.band(s0 - RAND, s1 + RAND)
    achse = (r.punkt(s0 - RAND, streifen.mitte), r.punkt(s1 + RAND, streifen.mitte))
    L = s1 - s0
    kandidaten: List[Tuple[Tuple[int, int], Auflager]] = []
    for w in decke.linienlager:
        if not (w.vertikal or w.eingespannt) or richtung_der_strecke(w.a, w.b).parallel(r):
            continue
        teil = geo.strecke_in_konvex(w.a, w.b, band)
        if teil is None:
            continue
        p0, p1 = (_zwischen(w.a, w.b, u) for u in teil)
        if math.hypot(p1[0] - p0[0], p1[1] - p0[1]) <= geo.TOLERANZ:
            continue
        s = 0.5 * (geo.skalar(p0, r.n) + geo.skalar(p1, r.n)) - s0
        kandidaten.append(((0, 0), Auflager(min(max(s, 0.0), L), w.vertikal, w.eingespannt, LINIENLAGER,
                                            w.name, strecke=(p0, p1))))
    for u in unterzuege:
        if u.stufe > streifen.stufe and not u.richtung.parallel(r):
            lager = _flaechenlager(streifen, s0, L, achse, u.gebiet, UNTERZUG, u.name)
            if lager:
                kandidaten.append(((1, -u.stufe), lager))
    for st in decke.stuetzen:
        lager = _flaechenlager(streifen, s0, L, achse, bereiche[st.name], STUETZE, st.name)
        if lager:
            kandidaten.append(((2, 0), lager))
    kandidaten.sort(key=lambda k: k[0])
    gewaehlt: List[Auflager] = []
    for _, lager in kandidaten:
        if not any(_an_derselben_stelle(lager, g) for g in gewaehlt):
            gewaehlt.append(lager)
    return sorted(gewaehlt, key=lambda a: a.s)


def _zwischen(a: Punkt, b: Punkt, u: float) -> Punkt:
    return (a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]))


def _flaechenlager(streifen: Streifen, s0: float, L: float, achse: Tuple[Punkt, Punkt],
                   gebiet: Sequence[Punkt], art: str, name: str) -> Optional[Auflager]:
    """
    Ein Flächenlager, wenn die Achse des Streifens das Gebiet kreuzt -- mit
    Pressung über die Fläche, die beide auf dem Träger teilen, und dort, wo
    ihr Schwerpunkt liegt. Liegt die Fläche ganz hinter seinem Ende, ein
    Punkt dort.
    """
    teil = geo.strecke_in_konvex(achse[0], achse[1], gebiet)
    laenge = math.hypot(achse[1][0] - achse[0][0], achse[1][1] - achse[0][1])
    if teil is None or (teil[1] - teil[0]) * laenge <= geo.TOLERANZ:
        return None
    r = streifen.richtung
    kontakt = geo.schnitt(streifen.band(s0, s0 + L), gebiet)
    if not kontakt:
        s = geo.skalar(_zwischen(achse[0], achse[1], 0.5 * (teil[0] + teil[1])), r.n) - s0
        return Auflager(min(max(s, 0.0), L), True, False, art, name)
    s = geo.skalar(geo.schwerpunkt(kontakt), r.n) - s0
    return Auflager(min(max(s, 0.0), L), True, False, art, name, kontakt=tuple(kontakt),
                    pressung=tuple(pressung(kontakt, r.n, s0)))


def pressung(kontakt: Sequence[Punkt], n: Punkt, s0: float = 0.0) -> List[Streckenlast]:
    """
    Eine gleichmässige Pressung je Kraft eins auf dem konvexen ``kontakt``,
    als Last je Länge längs ``n``, in ``s = p·n - s0``. Ihr Integral ist
    eins, ihr Schwerpunkt der des Kontakts.
    """
    verlauf = geo.breite(kontakt, n)
    flaeche = abs(geo.flaeche(kontakt))
    return [Streckenlast(sa - s0, sb - s0, wa / flaeche, wb / flaeche)
            for (sa, wa), (sb, wb) in zip(verlauf, verlauf[1:]) if sb > sa]


def _an_derselben_stelle(a: Auflager, b: Auflager) -> bool:
    """Ob zwei Lager an derselben Stelle liegen -- das eine in der Fläche des anderen."""
    if abs(a.s - b.s) <= 1e-6:
        return True
    return any(lo - 1e-6 <= x.s <= hi + 1e-6 for x, (lo, hi) in ((a, b.bereich), (b, a.bereich)))


# ===========================================================================
# Prüfen
# ===========================================================================


def pruefen(decke: Decke) -> List[Meldung]:
    """Was die Zerlegung aufhält -- Fehler -- und was auffällt -- Hinweise."""
    heraus: List[Meldung] = []
    if not decke.platten:
        heraus.append(Meldung("Die Decke hat keine Platte."))
    if not decke.streifenbreite > 0.0:
        heraus.append(Meldung("Die Streifenbreite muss grösser als null sein."))
    stuecke: Dict[str, List[List[Punkt]]] = {}
    for p in decke.platten:
        if len(geo.bereinigt(p.ecken)) < 3 or abs(geo.flaeche(p.ecken)) <= geo.TOLERANZ:
            heraus.append(Meldung(f"Die Platte «{p.name}» hat keine Fläche.", (p.name,)))
            continue
        try:
            stuecke[p.name] = geo.dreiecke(p.ecken)
        except ValueError:
            heraus.append(Meldung(f"Der Rand der Platte «{p.name}» schneidet sich selbst.", (p.name,)))
            continue
        if not p.h > 0.0:
            heraus.append(Meldung(f"Die Platte «{p.name}» braucht eine Dicke.", (p.name,)))
        if not p.E > 0.0:
            heraus.append(Meldung(f"Der Beton der Platte «{p.name}» braucht einen Elastizitätsmodul.", (p.name,)))
        r1, r2 = richtungen_der_platte(p)
        if abs(math.sin(r1.winkel - r2.winkel)) < math.sin(math.radians(5.0)):
            heraus.append(Meldung(f"Die zwei Richtungen der Platte «{p.name}» liegen weniger als 5° "
                                  "auseinander -- sie tragen dann kaum anders als eine.", (p.name,)))
    namen = list(stuecke)
    for i, a in enumerate(namen):
        for b in namen[i + 1:]:
            if _ueberlappen(stuecke[a], stuecke[b]):
                heraus.append(Meldung(f"Die Platten «{a}» und «{b}» überlappen sich.", (a, b)))
    for w in decke.linienlager:
        if math.hypot(w.b[0] - w.a[0], w.b[1] - w.a[1]) <= geo.TOLERANZ:
            heraus.append(Meldung(f"Das Linienlager «{w.name}» hat keine Länge.", (w.name,)))
        elif not (w.vertikal or w.eingespannt):
            heraus.append(Meldung(f"Das Linienlager «{w.name}» hält weder Höhe noch Drehung -- "
                                  "es trägt nichts.", (w.name,), fehler=False))
    for s in decke.stuetzen:
        if not (s.bx > 0.0 and s.by > 0.0):
            heraus.append(Meldung(f"Die Stütze «{s.name}» braucht eine Grösse.", (s.name,)))
        if (s.lx is not None and not s.lx > 0.0) or (s.ly is not None and not s.ly > 0.0):
            heraus.append(Meldung(f"Der Stützenbereich von «{s.name}» braucht eine Grösse.", (s.name,)))
    for u in decke.unterzuege:
        if not _lang(u):
            heraus.append(Meldung(f"Der Unterzug «{u.name}» hat keine Länge.", (u.name,)))
        if not u.breite > 0.0:
            heraus.append(Meldung(f"Der Unterzug «{u.name}» braucht eine Breite.", (u.name,)))
        if u.stufe < 1:
            heraus.append(Meldung(f"Die Stufe des Unterzugs «{u.name}» beginnt bei 1.", (u.name,)))
    gueltig = [u for u in decke.unterzuege if _lang(u) and u.breite > 0.0]
    for i, a in enumerate(gueltig):
        for b in gueltig[i + 1:]:
            if richtung_der_strecke(a.a, a.b).parallel(richtung_der_strecke(b.a, b.b)) and _ueberlappen(
                    [geo.rechteck(a.a, a.b, a.breite)], [geo.rechteck(b.a, b.b, b.breite)]):
                heraus.append(Meldung(f"Die Unterzüge «{a.name}» und «{b.name}» liegen parallel "
                                      "übereinander.", (a.name, b.name)))
    zonen = {}
    for z in decke.zonen:
        if not 0.0 <= z.anteil <= 1.0:
            heraus.append(Meldung(f"Der Anteil der Zone «{z.name}» liegt nicht zwischen 0 und 100 %.", (z.name,)))
        try:
            zonen[z.name] = geo.dreiecke(z.ecken)
        except ValueError:
            heraus.append(Meldung(f"Der Rand der Zone «{z.name}» schneidet sich selbst.", (z.name,)))
    namen = list(zonen)
    for i, a in enumerate(namen):
        for b in namen[i + 1:]:
            if _ueberlappen(zonen[a], zonen[b]):
                heraus.append(Meldung(f"Die Zonen «{a}» und «{b}» überlappen sich.", (a, b)))
    if decke.aufteilung is Aufteilung.FEST and not 0.0 <= decke.anteil <= 1.0:
        heraus.append(Meldung("Der feste Anteil liegt nicht zwischen 0 und 100 %."))
    return heraus


def _ueberlappen(a: Sequence[Sequence[Punkt]], b: Sequence[Sequence[Punkt]]) -> bool:
    """Ob sich zwei Flächen aus konvexen Stücken mehr als berühren."""
    for p in a:
        for q in b:
            stueck = geo.schnitt(p, geo.gegen_uhrzeiger(q))
            if stueck and abs(geo.flaeche(stueck)) > 1e-6:
                return True
    return False
