"""
opencivil/stabwerk/system.py -- das ganze Stabwerk: Unbekannte, Zusammenbau, Loesen.

VERANTWORTUNG:
Aus dem :class:`~opencivil.stabwerk.modell.System` die Unbekannten, die
Steifigkeitsmatrix und je Lastfall und Kombination die rechte Seite -- und
nach dem Loesen Verschiebungen, Stabendkraefte und Lagerkraefte. Wie die
Schnittgroessen laengs der Staebe verlaufen, rechnet
:mod:`~opencivil.stabwerk.verlauf` aus dem, was hier herauskommt.

ORTE UND TEILSTAEBE:
Gerechnet wird an Orten, nicht an Knoten. Ein Ort ist ein Knoten der
Beschreibung -- oder ein Punkt im Innern eines Stabs, wo er geteilt ist:

* Liegt ein Knoten auf einem Stab, nicht an dessen Ende, ist er mit ihm
  verbunden (T-Stoss); der Stab wird dort geteilt. Linien, die sich ohne
  Knoten kreuzen, sind nicht verbunden -- dazu ein Hinweis.
* Ein gebetteter Stab wird in kurze Stuecke geteilt, so dass jedes hoechstens
  ``1/(2β)`` lang ist, ``β = (k/(4EI))^(1/4)``: dann weicht die kubische
  Naeherung um weniger als ein Promille ab. Hoechstens :data:`TEILE_HOECHSTENS`.

Zwischen zwei Orten liegt ein Teilstab -- ein Stab im Sinn von
:mod:`~opencivil.stabwerk.stab`.

UNBEKANNTE:
Je Ort zwei Verschiebungen und eine Drehung, weniger was festgehalten ist.
Feste Richtungen kommen von Lagern -- in x und z -- und von festen
Linienlagern, quer oder laengs zur Linie, also auch schief. Je Ort wird darum
eine orthonormale Basis gebildet: die festen Richtungen, und was frei bleibt;
unbekannt sind nur die freien.

Ein Gelenk am Stabende gibt dem Stab dort seine eigene Drehung -- eine
Unbekannte mehr, mit der Steifigkeit ``4EI/L`` des Stabs. Der Knoten dreht
sich davon unabhaengig.

DREHUNG OHNE STEIFIGKEIT:
Haengt ein Knoten nur an Gelenken, ohne Drehfeder und ohne Einspannung, hat
seine Drehung keine Steifigkeit: ihre Zeile in K waere null. Sie wird
gestrichen und null gesetzt, und die Ausgabe sagt «Verdrehung nicht
bestimmbar, da keine Steifigkeit» (:data:`UNBESTIMMT`). Erkannt wird das an
der Verbindung, nicht an einer Zahl: welche Stabenden ohne Gelenk dort
haengen. Greift an einem solchen Knoten ein Moment an, ist das ein Fehler --
nichts koennte es aufnehmen.

FESTE LINIENLAGER:
Liegt ein Stab quer fest auf, biegt er sich nicht: seine Querverschiebung
ist an jedem Ort null, und wo er ohne Gelenk anschliesst, auch die Drehung.
Seine Querlasten gehen geradewegs ins Lager; er selbst hat keine Querkraft
und kein Moment. Laengs fest dasselbe fuer die Normalkraft. Das ist der
Grenzfall einer unendlich steifen Bettung -- und genau.

MELDUNGEN:
Was nicht zu rechnen ist, wird gemeldet, nicht geworfen: ein bewegliches
System, ein Stab ohne Laenge, eine Last hinter dem Stabende. Das Balkensystem
zeigt die Meldungen an den Elementen; der Rest des Projekts rechnet weiter.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.stabwerk import stab as st
from opencivil.stabwerk.matrix import Profilmatrix, Zerlegung, nummerierung
from opencivil.stabwerk.modell import (
    Knotenlast, Lastart, Lastfall, Stab, Stablast, System,
)

#: Wie nahe ein Knoten an einem Stab liegen muss, um mit ihm verbunden zu
#: sein -- in m. Das Zeichenfenster rundet auf ein Millionstel.
TOLERANZ = 1e-6

#: In hoechstens so viele Stuecke wird ein gebetteter Stab geteilt.
TEILE_HOECHSTENS = 64

#: Was an einem Knoten steht, dessen Drehung gestrichen ist.
UNBESTIMMT = "Verdrehung nicht bestimmbar, da keine Steifigkeit"

#: Was unter den Lagerkraeften steht, wenn Linienlager oder Bettung dabei sind.
SUMMEN = "Bei Linienlagern und Bettung steht die Summe; ihr Moment um den Ursprung."


@dataclass(frozen=True)
class Meldung:
    """Was die Rechnung zu sagen hat -- ``fehler`` haelt sie auf, ein Hinweis nicht."""

    text: str
    elemente: Tuple[str, ...] = ()
    fehler: bool = True


@dataclass
class Ort:
    """Ein Punkt des Systems mit Unbekannten -- ein Knoten oder ein Punkt in einem Stab."""

    name: str
    x: float
    z: float
    knoten: Optional[str] = None
    """Der Knoten der Beschreibung -- ``None`` im Innern eines Stabs."""

    stab: Optional[str] = None
    stelle: float = 0.0
    """Bei einem inneren Ort: wo auf welchem Stab, in m ab seinem Anfang."""

    zwang: List[Tuple[float, float]] = field(default_factory=list)
    """Die Richtungen, in denen er festgehalten ist -- wie gesammelt."""

    fest: List[Tuple[float, float]] = field(default_factory=list)
    frei: List[Tuple[float, float]] = field(default_factory=list)
    """Orthonormal: die festen und die freien Richtungen."""

    verschiebung: List[int] = field(default_factory=list)
    """Je freie Richtung die Nummer ihrer Unbekannten."""

    drehung: str = "frei"
    """``frei``, ``fest`` oder ``unbestimmt``."""

    drehindex: Optional[int] = None
    feder_x: float = 0.0
    feder_z: float = 0.0
    feder_phi: float = 0.0
    dreh_fest: bool = False

    @property
    def gehalten(self) -> bool:
        """Ob hier eine Lagerkraft entsteht: etwas Festes oder eine Feder."""
        return bool(self.fest or self.dreh_fest or self.drehung == "fest"
                    or self.feder_x or self.feder_z or self.feder_phi)


@dataclass
class Teilstab:
    """Ein Stueck eines Stabs zwischen zwei Orten."""

    stab: Stab
    nummer: int
    x0: float
    x1: float
    a: Ort
    b: Ort
    c: float
    s: float
    L_stab: float = 0.0
    """Die Laenge des ganzen Stabs."""

    k_quer: float = 0.0
    k_laengs: float = 0.0
    biegung: bool = True
    """Ob er sich biegt -- nicht, wenn er quer fest aufliegt."""

    laengs: bool = True
    """Ob er sich dehnt -- nicht, wenn er laengs fest aufliegt."""

    gelenk_a: bool = False
    gelenk_b: bool = False
    gelenkindex_a: Optional[int] = None
    gelenkindex_b: Optional[int] = None
    k: List[List[float]] = field(default_factory=list)
    abbildung: List[List[Tuple[int, float]]] = field(default_factory=list)
    """Je lokale Unbekannte (u, v, θ am Anfang, dann am Ende): ``[(Nummer, Beiwert)]``."""

    @property
    def L(self) -> float:
        return self.x1 - self.x0

    @property
    def EA(self) -> float:
        return self.stab.EA

    @property
    def EI(self) -> float:
        return self.stab.EI

    def lokal(self, x: Sequence[float]) -> List[float]:
        """Die Verschiebungen seiner Enden, in seinen Achsen, aus der Loesung ``x``."""
        return [sum(b * x[i] for i, b in eintrag) for eintrag in self.abbildung]

    def bettungsmatrix(self) -> List[List[float]]:
        return st.bettung(self.L, self.k_quer, self.k_laengs)


@dataclass
class Teilergebnis:
    """Was ein Teilstab in einem Fall tut -- in seinen Achsen."""

    teil: Teilstab
    lasten: List[st.Teillast]
    f: List[float]
    """Die arbeitsgleichen Knotenkraefte seiner Lasten."""

    d: List[float]
    """Die Verschiebungen seiner Enden."""

    s: List[float]
    """Die Kraefte auf seine Enden: ``k · d - f``."""


@dataclass
class Fall:
    """Ein Lastfall oder eine Kombination, gerechnet."""

    name: str
    kombination: bool
    lasten: List  # die Lasten des Modells, wie sie wirken -- bei einer Kombination mit Beiwert
    F: List[float]
    x: List[float]
    teile: List[Teilergebnis]
    verschiebungen: Dict[str, Tuple[float, float, float]]
    """Je Ort ``(u_x, u_z, φ)`` -- auch die inneren."""

    lagerkraefte: Dict[str, Tuple[float, float, float]]
    """Je gehaltenen Ort ``(R_x, R_z, M)``, auf das Tragwerk wirkend."""

    linienlast: Dict[str, Tuple[float, float, float]]
    """Je fest aufliegenden Stab, was seine Lasten geradewegs ins Lager geben -- als Summe ``(F_x, F_z, M)``."""

    bettung: Dict[str, Tuple[float, float, float]]
    """Je gebetteten Stab die Summe der Bettungskraefte auf das Tragwerk."""

    lastsumme: Tuple[float, float, float]
    gleichgewicht: Tuple[float, float, float]
    """Was in ``ΣF_x``, ``ΣF_z`` und ``ΣM`` um den Ursprung uebrig bleibt -- null bis auf Rundung."""


@dataclass
class Ergebnis:
    meldungen: List[Meldung] = field(default_factory=list)
    orte: Dict[str, Ort] = field(default_factory=dict)
    teilstaebe: List[Teilstab] = field(default_factory=list)
    unbekannte: List[str] = field(default_factory=list)
    """Je Unbekannte ein Name, fuer die Herleitung: ``u_x(K1)``, ``φ(K2)``, ``φ(L3, Ende)``."""

    K: Optional[Profilmatrix] = None
    faelle: List[Fall] = field(default_factory=list)
    beweglich: List[str] = field(default_factory=list)
    """Was sich ohne Widerstand bewegt, wenn das System beweglich ist."""

    @property
    def gueltig(self) -> bool:
        return not any(m.fehler for m in self.meldungen)

    def fall(self, name: str) -> Fall:
        return next(f for f in self.faelle if f.name == name)

    def unbestimmt(self) -> List[str]:
        """Die Knoten, deren Drehung gestrichen ist."""
        return [o.knoten for o in self.orte.values() if o.drehung == "unbestimmt" and o.knoten]


# ===========================================================================
# Geometrie
# ===========================================================================


def _laenge(a, b) -> float:
    return math.hypot(b.x - a.x, b.z - a.z)


def _stelle_auf(stab_a, stab_b, p) -> Optional[float]:
    """Wo ``p`` auf der Strecke a-b liegt (m ab a) -- ``None``, wenn daneben oder an einem Ende."""
    dx, dz = stab_b.x - stab_a.x, stab_b.z - stab_a.z
    L = math.hypot(dx, dz)
    if L <= TOLERANZ:
        return None
    t = ((p.x - stab_a.x) * dx + (p.z - stab_a.z) * dz) / L
    if t <= TOLERANZ or t >= L - TOLERANZ:
        return None
    abstand = abs((p.x - stab_a.x) * dz - (p.z - stab_a.z) * dx) / L
    return t if abstand <= TOLERANZ else None


def _kreuzen(p1, p2, q1, q2) -> bool:
    """Ob sich zwei Strecken im Innern beider kreuzen."""
    r = (p2.x - p1.x, p2.z - p1.z)
    s = (q2.x - q1.x, q2.z - q1.z)
    nenner = r[0] * s[1] - r[1] * s[0]
    if abs(nenner) < 1e-12:
        return False
    t = ((q1.x - p1.x) * s[1] - (q1.z - p1.z) * s[0]) / nenner
    u = ((q1.x - p1.x) * r[1] - (q1.z - p1.z) * r[0]) / nenner
    eps = 1e-9
    return eps < t < 1 - eps and eps < u < 1 - eps


def _basis(vektoren: Sequence[Tuple[float, float]]) -> Tuple[List[Tuple[float, float]],
                                                             List[Tuple[float, float]]]:
    """Die festen Richtungen orthonormal -- und was frei bleibt, ebenso."""
    fest: List[Tuple[float, float]] = []
    for v in vektoren:
        w = list(v)
        for f in fest:
            p = w[0] * f[0] + w[1] * f[1]
            w = [w[0] - p * f[0], w[1] - p * f[1]]
        n = math.hypot(*w)
        if n > 1e-9:
            fest.append((w[0] / n, w[1] / n))
    if len(fest) >= 2:
        return fest[:2], []
    if not fest:
        return [], [(1.0, 0.0), (0.0, 1.0)]
    f = fest[0]
    # Die Achse, die am wenigsten fest ist, ohne ihren festen Teil -- eine
    # Rolle auf waagrechter Bahn bleibt frei in x, nicht in -x.
    kandidaten = []
    for e in ((1.0, 0.0), (0.0, 1.0)):
        p = e[0] * f[0] + e[1] * f[1]
        w = (e[0] - p * f[0], e[1] - p * f[1])
        kandidaten.append((math.hypot(*w), w))
    n, w = max(kandidaten, key=lambda k: k[0])
    return fest, [(w[0] / n, w[1] / n)]


# ===========================================================================
# Die Rechnung
# ===========================================================================


def rechnen(system: System) -> Ergebnis:
    """Das System, gerechnet -- oder, wo das nicht geht, die Meldungen dazu."""
    return _Rechnung(system).ergebnis


class _Rechnung:
    def __init__(self, system: System) -> None:
        self.system = system
        self.ergebnis = Ergebnis()
        self.meldungen = self.ergebnis.meldungen
        self.knoten = {k.name: k for k in system.knoten}
        if not self._pruefen():
            return
        self._orte_und_teile()
        if not self.ergebnis.gueltig:
            return
        self._halt()
        self._drehungen()
        self._unbekannte()
        self._zusammenbauen()
        faelle = [(f, False) for f in system.lastfaelle]
        faelle += [(system.kombiniert(k), True) for k in system.kombinationen]
        # Eine Kombination traegt Lasten ihrer Lastfaelle: was an ihnen nicht
        # stimmt, ist dort schon gemeldet.
        rechte = [self._rechte_seite(fall, melden=not kombination)
                  for fall, kombination in faelle]
        if not self.ergebnis.gueltig:
            return
        zerlegung = Zerlegung(self.K)
        if zerlegung.singulaer:
            self._beweglich(zerlegung)
            return
        for (fall, kombination), (F, teile_f, knotenlasten) in zip(faelle, rechte):
            x = zerlegung.loese(F)
            self.ergebnis.faelle.append(
                self._auswerten(fall, kombination, F, x, teile_f, knotenlasten))

    # -- Pruefen ----------------------------------------------------------

    def _melden(self, text: str, *elemente: str, fehler: bool = True) -> None:
        self.meldungen.append(Meldung(text, tuple(elemente), fehler))

    def _pruefen(self) -> bool:
        tragende = []
        for stab_ in self.system.staebe:
            a, b = self.knoten.get(stab_.a), self.knoten.get(stab_.b)
            if a is None or b is None:
                self._melden(f"{stab_.name}: der Knoten "
                             f"«{stab_.a if a is None else stab_.b}» fehlt.", stab_.name)
                continue
            if _laenge(a, b) <= TOLERANZ:
                self._melden(f"{stab_.name} hat die Länge null.", stab_.name)
                continue
            if stab_.traegt:
                if stab_.EA <= 0.0 or stab_.EI <= 0.0:
                    self._melden(f"{stab_.name}: Dehn- und Biegesteifigkeit müssen grösser "
                                 f"als null sein.", stab_.name)
                    continue
                tragende.append(stab_)
            else:
                for halt in (stab_.quer, stab_.laengs):
                    if halt.feder > 0.0:
                        self._melden(f"{stab_.name}: ein federndes Linienlager braucht einen "
                                     f"Stab, der darauf liegt.", stab_.name)
        if not tragende and self.ergebnis.gueltig:
            self._melden("Kein Stab – es gibt nichts zu rechnen. Eine Linie wird "
                         "zum Stab, sobald sie Querschnitt und Material hat.")
        self.tragende = tragende
        return self.ergebnis.gueltig

    # -- Orte und Teilstaebe ---------------------------------------------

    def _ort(self, name: str) -> Ort:
        orte = self.ergebnis.orte
        if name not in orte:
            k = self.knoten[name]
            orte[name] = Ort(name=name, x=k.x, z=k.z, knoten=name)
        return orte[name]

    def _orte_und_teile(self) -> None:
        knoten = list(self.knoten.values())
        for stab_ in self.tragende:
            a, b = self.knoten[stab_.a], self.knoten[stab_.b]
            L = _laenge(a, b)
            c, s = (b.x - a.x) / L, (b.z - a.z) / L
            stellen = [(0.0, self._ort(a.name)), (L, self._ort(b.name))]
            for k in knoten:
                if k.name in (a.name, b.name):
                    continue
                t = _stelle_auf(a, b, k)
                if t is not None:
                    stellen.append((t, self._ort(k.name)))
            stellen.sort(key=lambda e: e[0])
            k_quer, k_laengs = stab_.quer.feder, stab_.laengs.feder
            nummer = 0
            for (x0, o0), (x1, o1) in zip(stellen, stellen[1:]):
                teile = 1
                if k_quer > 0.0:
                    beta = (k_quer / (4.0 * stab_.EI)) ** 0.25
                    teile = max(teile, math.ceil(2.0 * beta * (x1 - x0)))
                if k_laengs > 0.0:
                    beta = math.sqrt(k_laengs / stab_.EA)
                    teile = max(teile, math.ceil(2.0 * beta * (x1 - x0)))
                if teile > TEILE_HOECHSTENS:
                    self._melden(f"{stab_.name}: die Bettung ist so steif, dass {teile} Stücke "
                                 f"nötig wären; gerechnet mit {TEILE_HOECHSTENS}. Die Biegelinie "
                                 f"ist dort nur genähert.", stab_.name, fehler=False)
                    teile = TEILE_HOECHSTENS
                punkte = [(x0, o0)]
                for i in range(1, teile):
                    t = x0 + (x1 - x0) * i / teile
                    name = f"{stab_.name}·{len(self.ergebnis.orte)}"
                    ort = Ort(name=name, x=a.x + c * t, z=a.z + s * t, stab=stab_.name, stelle=t)
                    self.ergebnis.orte[name] = ort
                    punkte.append((t, ort))
                punkte.append((x1, o1))
                for (p0, q0), (p1, q1) in zip(punkte, punkte[1:]):
                    self.ergebnis.teilstaebe.append(Teilstab(
                        stab=stab_, nummer=nummer, x0=p0, x1=p1, a=q0, b=q1, c=c, s=s,
                        L_stab=L, k_quer=k_quer, k_laengs=k_laengs,
                        biegung=not stab_.quer.fest, laengs=not stab_.laengs.fest,
                        gelenk_a=stab_.gelenk_a and p0 == 0.0,
                        gelenk_b=stab_.gelenk_b and p1 == L))
                    nummer += 1
        # Kreuzen sich zwei Staebe ohne Knoten, sind sie nicht verbunden.
        for i, s1 in enumerate(self.tragende):
            for s2 in self.tragende[i + 1:]:
                if _kreuzen(self.knoten[s1.a], self.knoten[s1.b],
                            self.knoten[s2.a], self.knoten[s2.b]):
                    self._melden(f"{s1.name} und {s2.name} kreuzen sich ohne Knoten – sie sind "
                                 f"dort nicht verbunden.", s1.name, s2.name, fehler=False)

    # -- Halt: Lager, Federn, feste Linienlager ---------------------------

    def _halt(self) -> None:
        orte = self.ergebnis.orte
        for lager in self.system.lager:
            ort = orte.get(lager.knoten)
            if ort is None:
                self._melden(f"{lager.name} am Knoten {lager.knoten}: dort ist kein Stab – das "
                             f"Lager hält nichts.", lager.name, fehler=False)
                continue
            for halt, richtung in ((lager.x, (1.0, 0.0)), (lager.z, (0.0, 1.0))):
                if halt.fest:
                    ort.zwang.append(richtung)
            ort.feder_x += lager.x.feder
            ort.feder_z += lager.z.feder
            ort.feder_phi += lager.phi.feder
            if lager.phi.fest:
                ort.dreh_fest = True
        # Feste Linienlager: an jedem Ort des Stabs, oder -- ohne Stab -- an
        # jedem Ort, der auf der Linie liegt.
        for stab_ in self.system.staebe:
            if not (stab_.quer.fest or stab_.laengs.fest):
                continue
            a, b = self.knoten.get(stab_.a), self.knoten.get(stab_.b)
            if a is None or b is None:
                continue
            L = _laenge(a, b)
            if L <= TOLERANZ:
                continue
            c, s = (b.x - a.x) / L, (b.z - a.z) / L
            betroffen = [o for o in orte.values()
                         if o.stab == stab_.name or o.knoten in (stab_.a, stab_.b)
                         or (o.knoten and _stelle_auf(a, b, o) is not None)]
            for ort in betroffen:
                if stab_.quer.fest:
                    ort.zwang.append((-s, c))
                if stab_.laengs.fest:
                    ort.zwang.append((c, s))
        for ort in orte.values():
            ort.fest, ort.frei = _basis(ort.zwang)

    def _drehungen(self) -> None:
        """Je Ort: frei, fest -- oder ohne Steifigkeit, also gestrichen."""
        steif: Dict[str, bool] = {name: False for name in self.ergebnis.orte}
        fest: Dict[str, bool] = {name: o.dreh_fest for name, o in self.ergebnis.orte.items()}
        for t in self.ergebnis.teilstaebe:
            for ort, gelenk in ((t.a, t.gelenk_a), (t.b, t.gelenk_b)):
                if gelenk:
                    continue
                if t.biegung:
                    steif[ort.name] = True
                else:
                    # Quer fest aufgelegt und starr angeschlossen: der Stab
                    # dreht sich nicht, also auch der Ort nicht.
                    fest[ort.name] = True
        for name, ort in self.ergebnis.orte.items():
            if fest[name]:
                ort.drehung = "fest"
            elif steif[name] or ort.feder_phi:
                ort.drehung = "frei"
            else:
                ort.drehung = "unbestimmt"

    # -- Unbekannte --------------------------------------------------------

    def _unbekannte(self) -> None:
        orte = self.ergebnis.orte
        nachbarn: Dict[str, set] = {name: set() for name in orte}
        for t in self.ergebnis.teilstaebe:
            nachbarn[t.a.name].add(t.b.name)
            nachbarn[t.b.name].add(t.a.name)
        folge = nummerierung(list(orte), nachbarn)
        an_ort: Dict[str, List[Tuple[Teilstab, str]]] = {name: [] for name in orte}
        for t in self.ergebnis.teilstaebe:
            if t.gelenk_a and t.biegung:
                an_ort[t.a.name].append((t, "a"))
            if t.gelenk_b and t.biegung:
                an_ort[t.b.name].append((t, "b"))
        namen = self.ergebnis.unbekannte
        for name in folge:
            ort = orte[name]
            for richtung in ort.frei:
                ort.verschiebung.append(len(namen))
                namen.append(_verschiebungsname(ort, richtung))
            if ort.drehung == "frei":
                ort.drehindex = len(namen)
                namen.append(f"φ({ort.name})")
            for t, ende in an_ort[name]:
                wort = "Anfang" if ende == "a" else "Ende"
                if ende == "a":
                    t.gelenkindex_a = len(namen)
                else:
                    t.gelenkindex_b = len(namen)
                namen.append(f"φ({t.stab.name}, {wort})")
        for t in self.ergebnis.teilstaebe:
            t.abbildung = [
                *_ende(t.a, t.c, t.s, t.gelenk_a, t.gelenkindex_a, t.biegung),
                *_ende(t.b, t.c, t.s, t.gelenk_b, t.gelenkindex_b, t.biegung),
            ]
            k = st.summe(st.steifigkeit(t.L, t.EA, t.EI), t.bettungsmatrix())
            for i in range(6):
                for j in range(6):
                    if (not t.biegung and (i in (1, 2, 4, 5) or j in (1, 2, 4, 5))) \
                            or (not t.laengs and (i in (0, 3) or j in (0, 3))):
                        k[i][j] = 0.0
            t.k = k

    # -- Zusammenbau --------------------------------------------------------

    def _zusammenbauen(self) -> None:
        n = len(self.ergebnis.unbekannte)
        gruppen = []
        for t in self.ergebnis.teilstaebe:
            gruppen.append(sorted({i for eintrag in t.abbildung for i, _ in eintrag}))
        for ort in self.ergebnis.orte.values():
            gruppen.append(ort.verschiebung)
        K = Profilmatrix.aus_gruppen(n, gruppen)
        for t in self.ergebnis.teilstaebe:
            beitrag: Dict[Tuple[int, int], float] = {}
            for l in range(6):
                for m in range(6):
                    klm = t.k[l][m]
                    if not klm:
                        continue
                    for i, bi in t.abbildung[l]:
                        for j, bj in t.abbildung[m]:
                            if i >= j:
                                beitrag[(i, j)] = beitrag.get((i, j), 0.0) + bi * klm * bj
            for (i, j), wert in beitrag.items():
                K.addiere(i, j, wert)
        for ort in self.ergebnis.orte.values():
            if ort.feder_x or ort.feder_z:
                for p, (ip, qp) in enumerate(zip(ort.verschiebung, ort.frei)):
                    for q, (iq, qq) in enumerate(zip(ort.verschiebung, ort.frei)):
                        if q > p:
                            continue
                        K.addiere(ip, iq, ort.feder_x * qp[0] * qq[0] + ort.feder_z * qp[1] * qq[1])
            if ort.feder_phi and ort.drehindex is not None:
                K.addiere(ort.drehindex, ort.drehindex, ort.feder_phi)
        self.K = self.ergebnis.K = K

    # -- Lasten -------------------------------------------------------------

    def _stablasten(self, fall: Lastfall, melden: bool = True) -> Dict[str, List[st.Teillast]]:
        """Je Stab seine Lasten in seinen Achsen, ueber die ganze Laenge gezaehlt."""
        staebe = {s.name: s for s in self.system.staebe}
        melde = self._melden if melden else (lambda *_, **__: None)
        je_stab: Dict[str, List[st.Teillast]] = {}
        for last in fall.lasten:
            if not isinstance(last, Stablast):
                continue
            stab_ = staebe.get(last.stab)
            if stab_ is None:
                melde(f"Eine Last im Fall «{fall.name}» liegt auf «{last.stab}», den es "
                      f"nicht gibt.")
                continue
            a, b = self.knoten.get(stab_.a), self.knoten.get(stab_.b)
            if a is None or b is None:
                continue
            L = _laenge(a, b)
            if L <= TOLERANZ:
                continue
            c, s = (b.x - a.x) / L, (b.z - a.z) / L
            teil = _lokal(last, L, c, s)
            if isinstance(teil, str):
                melde(f"{stab_.name}, Lastfall «{fall.name}»: {teil}", stab_.name)
                continue
            if not stab_.traegt and not (stab_.quer.fest or stab_.laengs.fest):
                melde(f"{stab_.name} ist kein Stab: eine Last darauf trägt nichts. Die "
                      f"Linie braucht Querschnitt und Material.", stab_.name)
                continue
            je_stab.setdefault(stab_.name, []).append(teil)
        return je_stab

    def _rechte_seite(self, fall: Lastfall, melden: bool = True):
        n = len(self.ergebnis.unbekannte)
        F = [0.0] * n
        je_stab = self._stablasten(fall, melden)
        melde = self._melden if melden else (lambda *_, **__: None)
        teile_f = []
        for t in self.ergebnis.teilstaebe:
            lasten = st.aufteilen(je_stab.get(t.stab.name, []), t.x0, t.x1,
                                  ende=t.x1 == t.L_stab)
            f = st.knotenlasten(t.L, lasten)
            if not t.biegung:
                for i in (1, 2, 4, 5):
                    f[i] = 0.0
            if not t.laengs:
                for i in (0, 3):
                    f[i] = 0.0
            for l, eintrag in enumerate(t.abbildung):
                for i, b in eintrag:
                    F[i] += b * f[l]
            teile_f.append((lasten, f))
        knotenlasten: Dict[str, Tuple[float, float, float]] = {}
        for last in fall.lasten:
            if not isinstance(last, Knotenlast):
                continue
            ort = self.ergebnis.orte.get(last.knoten)
            if ort is None:
                melde(f"Knotenlast am Knoten {last.knoten} (Fall «{fall.name}»): dort ist "
                      f"kein Stab, der sie aufnimmt.", last.knoten)
                continue
            if last.M and ort.drehung == "unbestimmt":
                melde(f"Moment am Knoten {last.knoten} (Fall «{fall.name}»): alle Stäbe "
                      f"sind dort gelenkig angeschlossen, nichts nimmt es auf.", last.knoten)
                continue
            alt = knotenlasten.get(ort.name, (0.0, 0.0, 0.0))
            knotenlasten[ort.name] = (alt[0] + last.Fx, alt[1] + last.Fz, alt[2] + last.M)
            for i, q in zip(ort.verschiebung, ort.frei):
                F[i] += q[0] * last.Fx + q[1] * last.Fz
            if ort.drehindex is not None:
                F[ort.drehindex] += last.M
        return F, teile_f, knotenlasten

    # -- Beweglich ----------------------------------------------------------

    def _beweglich(self, zerlegung: Zerlegung) -> None:
        bewegung = zerlegung.bewegung()
        x = bewegung.x
        gross = max(abs(v) for v in x) or 1.0
        bewegt, nur_drehung = [], []
        for ort in self.ergebnis.orte.values():
            verschoben = any(abs(x[i]) > 1e-6 * gross for i in ort.verschiebung)
            gedreht = ort.drehindex is not None and abs(x[ort.drehindex]) > 1e-6 * gross
            name = ort.knoten or ort.stab
            if (verschoben or gedreht) and name not in bewegt:
                bewegt.append(name)
                if not verschoben:
                    nur_drehung.append(name)
        for t in self.ergebnis.teilstaebe:
            for i in (t.gelenkindex_a, t.gelenkindex_b):
                if i is not None and abs(x[i]) > 1e-6 * gross and t.stab.name not in bewegt:
                    bewegt.append(t.stab.name)
        self.ergebnis.beweglich = bewegt
        liste = ", ".join(bewegt[:-1]) + (" und " if len(bewegt) > 1 else "") + bewegt[-1] \
            if bewegt else "ein Teil"
        self._melden(
            f"Das System ist beweglich – die Steifigkeitsmatrix ist singulär und lässt sich "
            f"nicht invertieren. Ohne Widerstand bewegen sich: {liste}. Es fehlt ein Lager, "
            f"ein Stab oder ein Gelenk ist zu viel.", *bewegt)

    # -- Auswerten ----------------------------------------------------------

    def _auswerten(self, fall: Lastfall, kombination: bool, F: List[float], x: List[float],
                   teile_f, knotenlasten) -> Fall:
        orte = self.ergebnis.orte
        verschiebungen = {}
        for name, ort in orte.items():
            ux = sum(x[i] * q[0] for i, q in zip(ort.verschiebung, ort.frei))
            uz = sum(x[i] * q[1] for i, q in zip(ort.verschiebung, ort.frei))
            phi = x[ort.drehindex] if ort.drehindex is not None else 0.0
            verschiebungen[name] = (ux, uz, phi)
        teile: List[Teilergebnis] = []
        summen: Dict[str, List[float]] = {name: [0.0, 0.0, 0.0] for name in orte}
        bettung: Dict[str, List[float]] = {}
        for t, (lasten, f) in zip(self.ergebnis.teilstaebe, teile_f):
            d = t.lokal(x)
            kd = st.mal(t.k, d)
            s = [kd[i] - f[i] for i in range(6)]
            teile.append(Teilergebnis(teil=t, lasten=lasten, f=f, d=d, s=s))
            for ort, o, gelenk in ((t.a, 0, t.gelenk_a), (t.b, 3, t.gelenk_b)):
                fx = t.c * s[o] - t.s * s[o + 1]
                fz = t.s * s[o] + t.c * s[o + 1]
                summe = summen[ort.name]
                summe[0] += fx
                summe[1] += fz
                if not gelenk:
                    summe[2] += s[o + 2]
            if t.k_quer or t.k_laengs:
                # Was die Bettung auf das Tragwerk gibt: -k_b · d, in den
                # Achsen des Systems und als Moment um den Ursprung. Die
                # arbeitsgleichen Kraefte haben genau die Resultierende der
                # verteilten -- die Formfunktionen bilden x exakt ab.
                kb = t.bettungsmatrix()
                fb = [-v for v in st.mal(kb, d)]
                b = bettung.setdefault(t.stab.name, [0.0, 0.0, 0.0])
                for ort, o in ((t.a, 0), (t.b, 3)):
                    gx = t.c * fb[o] - t.s * fb[o + 1]
                    gz = t.s * fb[o] + t.c * fb[o + 1]
                    b[0] += gx
                    b[1] += gz
                    b[2] += ort.x * gz - ort.z * gx + fb[o + 2]
        lagerkraefte = {}
        for name, ort in orte.items():
            if not ort.gehalten:
                continue
            last = knotenlasten.get(name, (0.0, 0.0, 0.0))
            rx, rz, rm = (summen[name][i] - last[i] for i in range(3))
            lagerkraefte[name] = (rx, rz, rm)
        linienlast = self._ins_linienlager(fall)
        lastsumme = _summe_der_lasten(self, fall)
        rest = list(lastsumme)
        for name, (rx, rz, rm) in lagerkraefte.items():
            ort = orte[name]
            rest[0] += rx
            rest[1] += rz
            rest[2] += ort.x * rz - ort.z * rx + rm
        for werte in list(linienlast.values()) + list(bettung.values()):
            for i in range(3):
                rest[i] += werte[i]
        return Fall(name=fall.name, kombination=kombination, lasten=list(fall.lasten),
                    F=F, x=x, teile=teile, verschiebungen=verschiebungen,
                    lagerkraefte=lagerkraefte,
                    linienlast={k: tuple(v) for k, v in linienlast.items()},
                    bettung={k: tuple(v) for k, v in bettung.items()},
                    lastsumme=tuple(lastsumme), gleichgewicht=tuple(rest))

    def _ins_linienlager(self, fall: Lastfall) -> Dict[str, List[float]]:
        """
        Was fest aufliegende Staebe geradewegs ins Lager geben: ihre Lasten
        quer (bzw. laengs), mit umgekehrtem Vorzeichen -- als Kraft auf das
        Tragwerk und Moment um den Ursprung.
        """
        heraus: Dict[str, List[float]] = {}
        staebe = {s.name: s for s in self.system.staebe}
        for last in fall.lasten:
            if not isinstance(last, Stablast):
                continue
            stab_ = staebe.get(last.stab)
            if stab_ is None or not (stab_.quer.fest or stab_.laengs.fest):
                continue
            a, b = self.knoten[stab_.a], self.knoten[stab_.b]
            L = _laenge(a, b)
            c, s = (b.x - a.x) / L, (b.z - a.z) / L
            teil = _lokal(last, L, c, s)
            if isinstance(teil, str):
                continue
            quer = stab_.quer.fest or not stab_.traegt
            laengs = stab_.laengs.fest or not stab_.traegt
            fx, fz, m = _resultierende(teil, a, c, s, quer=quer, laengs=laengs,
                                       moment=quer)
            summe = heraus.setdefault(stab_.name, [0.0, 0.0, 0.0])
            summe[0] -= fx
            summe[1] -= fz
            summe[2] -= m
        return heraus


def _verschiebungsname(ort: Ort, richtung: Tuple[float, float]) -> str:
    if richtung == (1.0, 0.0):
        return f"u_x({ort.name})"
    if richtung == (0.0, 1.0):
        return f"u_z({ort.name})"
    return f"u({ort.name}; {richtung[0]:.3f}, {richtung[1]:.3f})"


def _ende(ort: Ort, c: float, s: float, gelenk: bool, gelenkindex: Optional[int],
          biegung: bool) -> List[List[Tuple[int, float]]]:
    """Wie u, v und θ eines Stabendes an den Unbekannten haengen."""
    u, v = [], []
    for i, q in zip(ort.verschiebung, ort.frei):
        bu = c * q[0] + s * q[1]
        bv = -s * q[0] + c * q[1]
        if abs(bu) > 1e-14:
            u.append((i, bu))
        if abs(bv) > 1e-14:
            v.append((i, bv))
    if gelenk:
        theta = [(gelenkindex, 1.0)] if gelenkindex is not None else []
    else:
        theta = [(ort.drehindex, 1.0)] if ort.drehindex is not None else []
    return [u, v, theta]


def _lokal(last: Stablast, L: float, c: float, s: float):
    """
    Eine Last des Modells in den Achsen ihres Stabs -- oder ein Satz, warum
    nicht: eine Stelle ausserhalb des Stabs.
    """
    von = last.von
    bis = L if last.bis is None else last.bis
    if last.art.verteilt:
        if von < -TOLERANZ or bis > L + TOLERANZ or bis < von - TOLERANZ:
            return (f"die Last reicht von {von:g} bis {bis:g} m, der Stab ist aber "
                    f"{L:.3f} m lang.")
        von, bis = max(0.0, von), min(L, bis)
    elif von < -TOLERANZ or von > L + TOLERANZ:
        return f"die Last steht bei {von:g} m, der Stab ist aber {L:.3f} m lang."
    else:
        von = min(max(von, 0.0), L)
    wert_a = last.wert_a
    wert_b = last.wert_a if last.wert_b is None else last.wert_b
    if last.art.kraft:
        gx, gz = last.richtung.vektor(c, s)
        faktor = last.richtung.projektion(c, s) if (last.projiziert and last.richtung.im_system) else 1.0
        px, py = (c * gx + s * gz) * faktor, (-s * gx + c * gz) * faktor
        if last.art is Lastart.LINIENLAST:
            return st.Strecke(von, bis, px * wert_a, px * wert_b, py * wert_a, py * wert_b)
        return st.Punkt(von, Px=px * wert_a, Py=py * wert_a)
    if last.art is Lastart.LINIENMOMENT:
        return st.Strecke(von, bis, m_a=wert_a, m_b=wert_b)
    return st.Punkt(von, M=wert_a)


def _resultierende(teil, a, c: float, s: float, *, quer: bool = True, laengs: bool = True,
                   moment: bool = True) -> Tuple[float, float, float]:
    """
    Kraft ``(F_x, F_z)`` und Moment um den Ursprung einer Last in den Achsen
    eines Stabs, der bei ``a`` beginnt -- nur die gewaehlten Anteile.
    """
    def an(x: float, px: float, py: float, m: float, w: float) -> Tuple[float, float, float]:
        px, py = (px if laengs else 0.0), (py if quer else 0.0)
        gx, gz = (c * px - s * py) * w, (s * px + c * py) * w
        ox, oz = a.x + c * x, a.z + s * x
        return gx, gz, ox * gz - oz * gx + (m * w if moment else 0.0)

    if isinstance(teil, st.Punkt):
        return an(teil.a, teil.Px, teil.Py, teil.M, 1.0)
    halb, mitte = (teil.b - teil.a) / 2.0, (teil.a + teil.b) / 2.0
    summe = [0.0, 0.0, 0.0]
    if halb <= 0.0:
        return (0.0, 0.0, 0.0)
    for stelle, gewicht in st.GAUSS3:
        x = mitte + halb * stelle
        beitrag = an(x, *teil.bei(x), halb * gewicht)
        for i in range(3):
            summe[i] += beitrag[i]
    return tuple(summe)


def _summe_der_lasten(rechnung: _Rechnung, fall: Lastfall) -> List[float]:
    """Alle Lasten des Falls als Kraft auf das Tragwerk und Moment um den Ursprung."""
    summe = [0.0, 0.0, 0.0]
    staebe = {s.name: s for s in rechnung.system.staebe}
    for last in fall.lasten:
        if isinstance(last, Knotenlast):
            k = rechnung.knoten.get(last.knoten)
            if k is None:
                continue
            summe[0] += last.Fx
            summe[1] += last.Fz
            summe[2] += k.x * last.Fz - k.z * last.Fx + last.M
            continue
        stab_ = staebe.get(last.stab)
        if stab_ is None:
            continue
        a, b = rechnung.knoten.get(stab_.a), rechnung.knoten.get(stab_.b)
        if a is None or b is None:
            continue
        L = _laenge(a, b)
        if L <= TOLERANZ:
            continue
        c, s = (b.x - a.x) / L, (b.z - a.z) / L
        teil = _lokal(last, L, c, s)
        if isinstance(teil, str):
            continue
        fx, fz, m = _resultierende(teil, a, c, s)
        summe[0] += fx
        summe[1] += fz
        summe[2] += m
    return summe
