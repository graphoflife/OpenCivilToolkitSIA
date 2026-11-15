"""
opencivil/stabwerk/system.py -- das Stabwerk, eben und im Raum: Unbekannte, Zusammenbau, Loesen.

VERANTWORTUNG:
Aus einem System -- eben (:mod:`opencivil.stabwerk.modell`) oder im Raum
(:mod:`opencivil.stabwerk3d.modell`) -- die Unbekannten, die
Steifigkeitsmatrix und je Lastfall und Kombination die rechte Seite -- und
nach dem Loesen Verschiebungen, Stabendkraefte und Lagerkraefte. Wie die
Schnittgroessen laengs der Staebe verlaufen, rechnet
:mod:`~opencivil.stabwerk.verlauf` aus dem, was hier herauskommt.

EBEN UND IM RAUM:
Gerechnet wird immer im Raum, mit den Staeben aus
:mod:`opencivil.stabwerk3d.stab`. Was die Ebene anders macht, sagt ihre
Art (:mod:`~opencivil.stabwerk.art`): in welchen Richtungen sich ein Ort
verschiebt und um welche Achsen er sich dreht, ob ein Stab sich auch quer
zur Ebene biegt und Torsion traegt, wie seine Achsen liegen. Was aus der
Ebene hinausfuehrte, ist keine Unbekannte und kein Lager -- es gibt es
nicht. Die Ergebnisse stehen in den Achsen der Art: eben ``(u_x, u_z, φ)``
und ``(R_x, R_z, M)``, wie von Hand.

ORTE UND TEILSTAEBE:
Gerechnet wird an Orten, nicht an Knoten. Ein Ort ist ein Knoten der
Beschreibung -- oder ein Punkt im Innern eines Stabs, wo er geteilt ist:

* Liegt ein Knoten auf einem Stab, nicht an dessen Ende, ist er mit ihm
  verbunden (T-Stoss); der Stab wird dort geteilt. Linien, die sich ohne
  Knoten kreuzen, sind nicht verbunden -- dazu ein Hinweis.
* Ein gebetteter Stab wird in kurze Stuecke geteilt, so dass jedes hoechstens
  ``1/(2β)`` lang ist, quer ``β = (k/(4EI))^(1/4)``, laengs ``β = √(k/EA)``:
  dann weicht die kubische Naeherung um weniger als ein Promille ab.
  Hoechstens :data:`TEILE_HOECHSTENS`.

Zwischen zwei Orten liegt ein Teilstab -- ein Stab im Sinn von
:mod:`~opencivil.stabwerk3d.stab`.

UNBEKANNTE:
Je Ort seine Verschiebungen und Drehungen, weniger was festgehalten ist --
als Richtungen: ein Lager haelt in den Achsen des Systems, ein festes
Linienlager laengs oder quer zu seinem Stab, also auch schief. Je Ort eine
orthonormale Basis aus den festen Richtungen und dem, was frei bleibt;
unbekannt sind nur die freien, moeglichst entlang der Achsen der Art.

GELENKE -- IM RAUM NACH VORGABE, NICHT NACHGESCHLAGEN:
Ein Gelenk am Stabende gibt dem Stab dort eigene Drehungen als Unbekannte,
mit der Steifigkeit ``4EI/L`` des Stabs; der Knoten dreht sich davon
unabhaengig. In der Ebene ist es eine. Im Raum loest das Gelenk alle drei
Momente, wie ein Kugelgelenk: Drehungen um y und z des Stabs, und um x, wenn
er Torsion traegt. Mit Gelenken an beiden Enden traegt er keine: er drehte
sich sonst frei um seine Achse. Ein Fachwerk aus lauter gelenkig
angeschlossenen Staeben rechnet so im Raum wie in der Ebene; ein Moment um
die Achse eines solchen Stabs hat keinen Halt und ist ein Fehler.

DREHUNG OHNE STEIFIGKEIT:
Ein Ort hat Drehsteifigkeit um die Achsen, die ein starr angeschlossener
Stab, eine Drehfeder oder eine Einspannung halten -- um die uebrigen nicht,
in der Ebene etwa, wenn er nur an Gelenken haengt. Diese Drehungen sind
gestrichen und null gesetzt, und die Ausgabe sagt es (:data:`UNBESTIMMT`).
Erkannt wird das an der Verbindung, nicht an einer Zahl. Greift dort ein
Moment an, ist das ein Fehler -- nichts koennte es aufnehmen.

Die Torsion haelt einen Knoten nur, wenn etwas das andere Ende des Stabs
haelt. Haelt nichts, dreht sich der Stab mit dem Knoten um seine Achse: Das
System ist beweglich, und die Meldung sagt, dass sich dabei nichts
verschiebt. Ein einfacher Balken im Raum auf zwei gelenkigen Lagern braucht
darum an einem Ende eine Gabel -- ein Lager, das die Drehung um seine Achse
festhaelt.

FESTE LINIENLAGER:
Liegt ein Stab quer in z fest auf, biegt er sich nicht in seiner
x-z-Ebene: seine Verschiebung in z ist an jedem Ort null, und wo er ohne
Gelenk anschliesst, auch die Drehung um seine y-Achse. Seine Lasten in
dieser Ebene gehen geradewegs ins Lager; er selbst hat dort keine Querkraft
und kein Moment. Quer in y und laengs ebenso; die Torsion traegt er weiter.
Das ist der Grenzfall einer unendlich steifen Bettung -- und genau.

MELDUNGEN:
Was nicht zu rechnen ist, wird gemeldet, nicht geworfen: ein bewegliches
System, ein Stab ohne Laenge, eine Last hinter dem Stabende. Das Balkensystem
zeigt die Meldungen an den Elementen; der Rest des Projekts rechnet weiter.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from opencivil.stabwerk import stab as st
from opencivil.stabwerk.art import Art, Werte
from opencivil.stabwerk.matrix import Profilmatrix, Zerlegung, nummerierung
from opencivil.stabwerk.modell import Lastfall, kombiniert
from opencivil.stabwerk3d import stab as st3
from opencivil.stabwerk3d.modell import Knotenlast, Stab, Stablast, System
from opencivil.stabwerk3d.raum import (
    ACHSEN, NULL, TOLERANZ, Vektor, addiere, betrag, im_system, in_achsen, kreuzen, mal, minus,
    orthonormal, plus, punkt, skalar, stelle_auf,
)

__all__ = ["SUMMEN", "UNBESTIMMT", "Ergebnis", "Fall", "Meldung", "Ort", "Teilstab", "rechnen"]

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


# ===========================================================================
# Was gerechnet wird und was herauskommt
# ===========================================================================


@dataclass
class Ort:
    """Ein Punkt des Systems mit Unbekannten -- ein Knoten oder ein Punkt in einem Stab."""

    name: str
    x: float
    y: float
    z: float
    knoten: Optional[str] = None
    """Der Knoten der Beschreibung -- ``None`` im Innern eines Stabs."""

    stab: Optional[str] = None
    stelle: float = 0.0
    """Bei einem inneren Ort: wo auf welchem Stab, in m ab seinem Anfang."""

    zwang: List[Vektor] = field(default_factory=list)
    """Die Richtungen, in denen er nicht verschoben wird -- wie gesammelt."""

    drehzwang: List[Vektor] = field(default_factory=list)
    """Die Achsen, um die er nicht gedreht wird -- wie gesammelt."""

    steif: List[Vektor] = field(default_factory=list)
    """Die Achsen, um die ihn etwas steif haelt: Staebe und Drehfedern -- wie gesammelt."""

    fest: List[Vektor] = field(default_factory=list)
    frei: List[Vektor] = field(default_factory=list)
    """Orthonormal: die festen und die freien Richtungen der Verschiebung."""

    dreh_fest: List[Vektor] = field(default_factory=list)
    dreh_frei: List[Vektor] = field(default_factory=list)
    offen: List[Vektor] = field(default_factory=list)
    """Orthonormal: die Drehachsen -- fest, frei und ohne Steifigkeit, also gestrichen."""

    verschiebung: List[int] = field(default_factory=list)
    """Je freie Richtung die Nummer ihrer Unbekannten."""

    drehung: List[int] = field(default_factory=list)
    """Je freie Drehachse die Nummer ihrer Unbekannten."""

    feder: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    """Federn in x, y und z des Systems, N/m."""

    drehfeder: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    """Drehfedern um x, y und z des Systems, Nm/rad."""

    @property
    def punkt(self) -> Vektor:
        return (self.x, self.y, self.z)

    @property
    def gehalten(self) -> bool:
        """Ob hier eine Lagerkraft entsteht: etwas Festes oder eine Feder."""
        return bool(self.fest or self.dreh_fest or any(self.feder) or any(self.drehfeder))


@dataclass
class Teilstab:
    """Ein Stueck eines Stabs zwischen zwei Orten."""

    stab: Stab
    nummer: int
    x0: float
    x1: float
    a: Ort
    b: Ort
    achsen: Tuple[Vektor, Vektor, Vektor]
    L_stab: float = 0.0
    """Die Laenge des ganzen Stabs."""

    k_y: float = 0.0
    k_z: float = 0.0
    k_x: float = 0.0
    """Die Bettung quer in y und z und laengs, N/m²."""

    biegung_y: bool = True
    """Ob er sich in seiner x-y-Ebene biegt -- nicht, wenn er quer in y fest aufliegt, und nicht in der Ebene."""

    biegung_z: bool = True
    """Ob er sich in seiner x-z-Ebene biegt -- nicht, wenn er quer in z fest aufliegt."""

    laengs: bool = True
    """Ob er sich dehnt -- nicht, wenn er laengs fest aufliegt."""

    torsion: bool = True
    """Ob er Torsion traegt -- nicht mit Gelenken an beiden Enden, und nicht in der Ebene."""

    gelenk_a: bool = False
    gelenk_b: bool = False
    gelenkindizes: Dict[Tuple[str, int], int] = field(default_factory=dict)
    """Je Ende (``a``, ``b``) und Achse des Stabs (0, 1, 2) die Nummer seiner Drehung am Gelenk."""

    k: List[List[float]] = field(default_factory=list)
    abbildung: List[List[Tuple[int, float]]] = field(default_factory=list)
    """Je lokale Unbekannte (u, v, w, θx, θy, θz am Anfang, dann am Ende): ``[(Nummer, Beiwert)]``."""

    @property
    def L(self) -> float:
        return self.x1 - self.x0

    @property
    def EA(self) -> float:
        return self.stab.EA

    @property
    def EI_y(self) -> float:
        return self.stab.EI_y

    @property
    def EI_z(self) -> float:
        return self.stab.EI_z

    @property
    def GI_T(self) -> float:
        return self.stab.GI_T

    @property
    def gesperrt(self) -> Tuple[int, ...]:
        """
        Die lokalen Unbekannten der Teile, die er nicht traegt: wo ein festes
        Linienlager alles nimmt, die Torsion zwischen zwei Gelenken -- und in
        der Ebene, was aus ihr hinausfuehrte.
        """
        teile = ((self.laengs, (0, 6)), (self.biegung_y, (1, 5, 7, 11)),
                 (self.biegung_z, (2, 4, 8, 10)), (self.torsion, (3, 9)))
        return tuple(i for traegt, indizes in teile if not traegt for i in indizes)

    def lokal(self, x: Sequence[float]) -> List[float]:
        """Die Verschiebungen seiner Enden, in seinen Achsen, aus der Loesung ``x``."""
        return [sum(b * x[i] for i, b in eintrag) for eintrag in self.abbildung]

    def bettungsmatrix(self) -> List[List[float]]:
        return st3.bettung(self.L, self.k_y, self.k_z, self.k_x)


@dataclass
class Teilergebnis:
    """Was ein Teilstab in einem Fall tut -- in seinen Achsen."""

    teil: Teilstab
    lasten: st3.Lasten
    f: List[float]
    """Die arbeitsgleichen Knotenkraefte seiner Lasten."""

    d: List[float]
    """Die Verschiebungen seiner Enden."""

    s: List[float]
    """Die Kraefte auf seine Enden: ``k · d - f``."""


@dataclass
class Fall:
    """
    Ein Lastfall oder eine Kombination, gerechnet. Verschiebungen und Kraefte
    in den Achsen der Art: erst je Achse eine Verschiebung oder Kraft, dann
    je Drehachse eine Drehung oder ein Moment.
    """

    name: str
    kombination: bool
    F: List[float]
    x: List[float]
    teile: List[Teilergebnis]
    verschiebungen: Dict[str, Werte]
    """Je Ort -- auch die inneren --, eben ``(u_x, u_z, φ)``, im Raum ``(u_x, u_y, u_z, φ_x, φ_y, φ_z)``."""

    lagerkraefte: Dict[str, Werte]
    """Je gehaltenen Ort ``(R_x, R_z, M)`` oder ``(R_x, R_y, R_z, M_x, M_y, M_z)``, auf das Tragwerk wirkend."""

    linienlast: Dict[str, Werte]
    """Je fest aufliegenden Stab, was seine Lasten geradewegs ins Lager geben -- Kraft und Moment um den Ursprung."""

    bettung: Dict[str, Werte]
    """Je gebetteten Stab die Summe der Bettungskraefte auf das Tragwerk -- ebenso."""

    lastsumme: Werte
    gleichgewicht: Werte
    """Was in den Summen der Kraefte und der Momente um den Ursprung uebrig bleibt -- null bis auf Rundung."""


@dataclass
class Ergebnis:
    art: Art
    meldungen: List[Meldung] = field(default_factory=list)
    orte: Dict[str, Ort] = field(default_factory=dict)
    teilstaebe: List[Teilstab] = field(default_factory=list)
    unbekannte: List[str] = field(default_factory=list)
    """Je Unbekannte ein Name, fuer die Herleitung: ``u_x(K1)``, ``φ(K2)``, ``θ_y(L3, Ende)``."""

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
        """Die Knoten, deren Drehung um eine Achse gestrichen ist."""
        return [o.knoten for o in self.orte.values() if o.offen and o.knoten]


def _laenge(a, b) -> float:
    return betrag(minus(punkt(b), punkt(a)))


def _name(zeichen: str, ort: str, richtung: Vektor, achsen: Sequence[Tuple[str, Vektor]]) -> str:
    """``u_x(K1)`` oder ``φ(K1)`` entlang einer Achse der Art, sonst mit der Richtung in ihren Achsen."""
    werte = [skalar(richtung, a) for _, a in achsen]
    nicht_null = [i for i, w in enumerate(werte) if w != 0.0]
    if len(nicht_null) == 1 and werte[nicht_null[0]] > 0.0:
        achse = achsen[nicht_null[0]][0]
        return f"{zeichen}_{achse}({ort})" if achse else f"{zeichen}({ort})"
    return f"{zeichen}({ort}; {', '.join(f'{w:.3f}' for w in werte)})"


def _hat_festes_linienlager(stab_: Stab) -> bool:
    return stab_.laengs.fest or stab_.quer_y.fest or stab_.quer_z.fest


def _traegt_torsion(stab_: Stab) -> bool:
    """Ob ein Stab Torsion traegt: nicht mit Gelenken an beiden Enden -- siehe Dateikopf."""
    return not (stab_.gelenk_a and stab_.gelenk_b)


# ===========================================================================
# Die Rechnung
# ===========================================================================


def rechnen(system: Any, art: Art) -> Ergebnis:
    """Ein System dieser Art, gerechnet -- oder, wo das nicht geht, die Meldungen dazu."""
    return _Rechnung(art.im_raum(system), art).ergebnis


class _Rechnung:
    def __init__(self, system: System, art: Art) -> None:
        self.system = system
        self.art = art
        self.ergebnis = Ergebnis(art)
        self.meldungen = self.ergebnis.meldungen
        self.knoten = {k.name: k for k in system.knoten}
        self.staebe = {s.name: s for s in system.staebe}
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
        faelle += [(kombiniert(system.lastfaelle, k), True) for k in system.kombinationen]
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
        for (fall, kombination), (F, teile_f, je_stab, knotenlasten) in zip(faelle, rechte):
            x = zerlegung.loese(F)
            self.ergebnis.faelle.append(
                self._auswerten(fall, kombination, F, x, teile_f, je_stab, knotenlasten))

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
                if min(getattr(stab_, s) for s in self.art.steifigkeiten) <= 0.0:
                    self._melden(f"{stab_.name}: {self.art.ohne_steifigkeit}", stab_.name)
                    continue
                tragende.append(stab_)
            elif any(h.feder > 0.0 for h in (stab_.laengs, stab_.quer_y, stab_.quer_z)):
                self._melden(f"{stab_.name}: ein federndes Linienlager braucht einen Stab, "
                             f"der darauf liegt.", stab_.name)
        if not tragende and self.ergebnis.gueltig:
            self._melden("Kein Stab – es gibt nichts zu rechnen. Eine Linie wird "
                         "zum Stab, sobald sie Querschnitt und Material hat.")
        self.tragende = tragende
        return self.ergebnis.gueltig

    def _geometrie(self, stab_: Stab):
        """Anfang, Laenge und Achsen eines Stabs -- ``None``, wenn er keine Laenge hat."""
        a, b = self.knoten.get(stab_.a), self.knoten.get(stab_.b)
        if a is None or b is None or _laenge(a, b) <= TOLERANZ:
            return None
        return (punkt(a), *self.art.achsen(a, b, stab_.drehung))

    # -- Orte und Teilstaebe ---------------------------------------------

    def _ort(self, name: str) -> Ort:
        orte = self.ergebnis.orte
        if name not in orte:
            k = self.knoten[name]
            orte[name] = Ort(name=name, x=k.x, y=k.y, z=k.z, knoten=name)
        return orte[name]

    def _orte_und_teile(self) -> None:
        knoten = list(self.knoten.values())
        for stab_ in self.tragende:
            a, b = self.knoten[stab_.a], self.knoten[stab_.b]
            anfang, L, achsen = self._geometrie(stab_)
            stellen = [(0.0, self._ort(a.name)), (L, self._ort(b.name))]
            for k in knoten:
                if k.name in (a.name, b.name):
                    continue
                t = stelle_auf(a, b, k)
                if t is not None:
                    stellen.append((t, self._ort(k.name)))
            stellen.sort(key=lambda e: e[0])
            k_y, k_z, k_x = stab_.quer_y.feder, stab_.quer_z.feder, stab_.laengs.feder
            # Wie schnell die Biegelinie auf der Bettung abklingt, je Richtung.
            abklingen = [(k / (4.0 * EI)) ** 0.25 for k, EI in ((k_y, stab_.EI_z), (k_z, stab_.EI_y))
                         if k > 0.0] + ([math.sqrt(k_x / stab_.EA)] if k_x > 0.0 else [])
            nummer = 0
            for (x0, o0), (x1, o1) in zip(stellen, stellen[1:]):
                teile = max([1] + [math.ceil(2.0 * beta * (x1 - x0)) for beta in abklingen])
                if teile > TEILE_HOECHSTENS:
                    self._melden(f"{stab_.name}: die Bettung ist so steif, dass {teile} Stücke "
                                 f"nötig wären; gerechnet mit {TEILE_HOECHSTENS}. Die Biegelinie "
                                 f"ist dort nur genähert.", stab_.name, fehler=False)
                    teile = TEILE_HOECHSTENS
                punkte = [(x0, o0)]
                for i in range(1, teile):
                    t = x0 + (x1 - x0) * i / teile
                    name = f"{stab_.name}·{len(self.ergebnis.orte)}"
                    p = plus(anfang, mal(t, achsen[0]))
                    ort = Ort(name=name, x=p[0], y=p[1], z=p[2], stab=stab_.name, stelle=t)
                    self.ergebnis.orte[name] = ort
                    punkte.append((t, ort))
                punkte.append((x1, o1))
                for (p0, q0), (p1, q1) in zip(punkte, punkte[1:]):
                    self.ergebnis.teilstaebe.append(Teilstab(
                        stab=stab_, nummer=nummer, x0=p0, x1=p1, a=q0, b=q1, achsen=achsen,
                        L_stab=L, k_y=k_y, k_z=k_z, k_x=k_x,
                        biegung_y=self.art.raeumlich and not stab_.quer_y.fest,
                        biegung_z=not stab_.quer_z.fest,
                        laengs=not stab_.laengs.fest,
                        torsion=self.art.raeumlich and _traegt_torsion(stab_),
                        gelenk_a=stab_.gelenk_a and p0 == 0.0,
                        gelenk_b=stab_.gelenk_b and p1 == L))
                    nummer += 1
        # Kreuzen sich zwei Staebe ohne Knoten, sind sie nicht verbunden.
        for i, s1 in enumerate(self.tragende):
            for s2 in self.tragende[i + 1:]:
                if kreuzen(self.knoten[s1.a], self.knoten[s1.b],
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
            for i, (verschiebung, drehung) in enumerate(zip(lager.verschiebungen,
                                                            lager.drehungen)):
                if verschiebung.fest:
                    ort.zwang.append(ACHSEN[i])
                if drehung.fest:
                    ort.drehzwang.append(ACHSEN[i])
                ort.feder[i] += verschiebung.feder
                ort.drehfeder[i] += drehung.feder
        # Feste Linienlager: an jedem Ort des Stabs, oder -- ohne Stab -- an
        # jedem Ort, der auf der Linie liegt.
        for stab_ in self.system.staebe:
            richtungen = [i for i, halt in enumerate((stab_.laengs, stab_.quer_y, stab_.quer_z))
                          if halt.fest]
            geometrie = self._geometrie(stab_)
            if not richtungen or geometrie is None:
                continue
            achsen = geometrie[2]
            a, b = self.knoten[stab_.a], self.knoten[stab_.b]
            for ort in orte.values():
                if (ort.stab == stab_.name or ort.knoten in (stab_.a, stab_.b)
                        or (ort.knoten and stelle_auf(a, b, ort) is not None)):
                    ort.zwang.extend(achsen[i] for i in richtungen)
        verschiebungen = [a for _, a in self.art.verschiebungen]
        for ort in orte.values():
            ort.fest = orthonormal(ort.zwang)
            ort.frei = in_achsen(orthonormal(verschiebungen, gegen=ort.fest), verschiebungen)

    def _drehungen(self) -> None:
        """Je Ort die Drehachsen: fest, frei -- oder ohne Steifigkeit, also gestrichen."""
        for t in self.ergebnis.teilstaebe:
            ex, ey, ez = t.achsen
            for ort, gelenk in ((t.a, t.gelenk_a), (t.b, t.gelenk_b)):
                if gelenk:
                    continue
                if t.torsion:
                    ort.steif.append(ex)
                for biegt, fest, achse in ((t.biegung_z, t.stab.quer_z.fest, ey),
                                           (t.biegung_y, t.stab.quer_y.fest, ez)):
                    if biegt:
                        ort.steif.append(achse)
                    elif fest:
                        # Quer fest aufgelegt und starr angeschlossen: der Stab
                        # dreht sich um diese Achse nicht, also auch der Ort nicht.
                        ort.drehzwang.append(achse)
        drehungen = [a for _, a in self.art.drehungen]
        for ort in self.ergebnis.orte.values():
            ort.steif.extend(ACHSEN[i] for i in range(3) if ort.drehfeder[i])
            ort.dreh_fest = orthonormal(ort.drehzwang)
            steif = orthonormal(ort.steif, gegen=ort.dreh_fest)
            ort.dreh_frei = in_achsen(steif, drehungen)
            ort.offen = in_achsen(orthonormal(drehungen, gegen=[*ort.dreh_fest, *steif]),
                                  drehungen)

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
            if t.gelenk_a:
                an_ort[t.a.name].append((t, "a"))
            if t.gelenk_b:
                an_ort[t.b.name].append((t, "b"))
        namen = self.ergebnis.unbekannte
        for name in folge:
            ort = orte[name]
            for richtung in ort.frei:
                ort.verschiebung.append(len(namen))
                namen.append(_name("u", ort.name, richtung, self.art.verschiebungen))
            for achse in ort.dreh_frei:
                ort.drehung.append(len(namen))
                namen.append(_name("φ", ort.name, achse, self.art.drehungen))
            for t, ende in an_ort[name]:
                wort = "Anfang" if ende == "a" else "Ende"
                for achse, traegt in ((0, t.torsion), (1, t.biegung_z), (2, t.biegung_y)):
                    if traegt:
                        t.gelenkindizes[ende, achse] = len(namen)
                        namen.append(self.art.gelenk.format(stab=t.stab.name, ende=wort,
                                                            achse="xyz"[achse]))
        for t in self.ergebnis.teilstaebe:
            t.abbildung = [*_ende(t, "a"), *_ende(t, "b")]
            k = st.summe(st3.steifigkeit(t.L, t.EA, t.EI_y, t.EI_z, t.GI_T), t.bettungsmatrix())
            for i in t.gesperrt:
                for j in range(12):
                    k[i][j] = k[j][i] = 0.0
            t.k = k

    # -- Zusammenbau --------------------------------------------------------

    def _zusammenbauen(self) -> None:
        n = len(self.ergebnis.unbekannte)
        gruppen = [sorted({i for eintrag in t.abbildung for i, _ in eintrag})
                   for t in self.ergebnis.teilstaebe]
        for ort in self.ergebnis.orte.values():
            gruppen += [ort.verschiebung, ort.drehung]
        K = Profilmatrix.aus_gruppen(n, gruppen)
        for t in self.ergebnis.teilstaebe:
            beitrag: Dict[Tuple[int, int], float] = {}
            for l in range(12):
                for m in range(12):
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
            for federn, indizes, richtungen in ((ort.feder, ort.verschiebung, ort.frei),
                                                (ort.drehfeder, ort.drehung, ort.dreh_frei)):
                if not any(federn):
                    continue
                paare = list(zip(indizes, richtungen))
                for p, (ip, qp) in enumerate(paare):
                    for iq, qq in paare[:p + 1]:
                        K.addiere(ip, iq, sum(f * a * b for f, a, b in zip(federn, qp, qq)))
        self.K = self.ergebnis.K = K

    # -- Lasten -------------------------------------------------------------

    def _stablasten(self, fall: Lastfall, melden: bool = True) -> Dict[str, st3.Lasten]:
        """
        Je Stab seine Lasten in seinen Achsen, ueber die ganze Laenge gezaehlt
        -- auch je Linie ohne Stab, die fest aufliegt.
        """
        melde = self._melden if melden else (lambda *_, **__: None)
        je_stab: Dict[str, st3.Lasten] = {}
        for last in fall.lasten:
            if not isinstance(last, Stablast):
                continue
            stab_ = self.staebe.get(last.stab)
            if stab_ is None:
                melde(f"Eine Last im Fall «{fall.name}» liegt auf «{last.stab}», den es "
                      f"nicht gibt.")
                continue
            geometrie = self._geometrie(stab_)
            if geometrie is None:
                continue
            _, L, achsen = geometrie
            teil = st3.lokal(last, L, achsen)
            if isinstance(teil, str):
                melde(f"{stab_.name}, Lastfall «{fall.name}»: {teil}", stab_.name)
                continue
            if not stab_.traegt and not _hat_festes_linienlager(stab_):
                melde(f"{stab_.name} ist kein Stab: eine Last darauf trägt nichts. Die "
                      f"Linie braucht Querschnitt und Material.", stab_.name)
                continue
            if stab_.traegt and not _traegt_torsion(stab_) and teil.mit_torsion:
                melde(f"{stab_.name}, Lastfall «{fall.name}»: das Moment um die Stabachse hat "
                      f"keinen Halt. Mit Gelenken an beiden Enden trägt der Stab keine Torsion.",
                      stab_.name)
                continue
            je_stab.setdefault(stab_.name, st3.Lasten()).dazu(teil)
        return je_stab

    def _rechte_seite(self, fall: Lastfall, melden: bool = True):
        F = [0.0] * len(self.ergebnis.unbekannte)
        je_stab = self._stablasten(fall, melden)
        melde = self._melden if melden else (lambda *_, **__: None)
        teile_f = []
        for t in self.ergebnis.teilstaebe:
            lasten = st3.aufteilen(je_stab.get(t.stab.name, st3.Lasten()), t.x0, t.x1,
                                   ende=t.x1 == t.L_stab)
            f = st3.knotenlasten(t.L, lasten)
            for i in t.gesperrt:
                f[i] = 0.0
            for l, eintrag in enumerate(t.abbildung):
                for i, b in eintrag:
                    F[i] += b * f[l]
            teile_f.append((lasten, f))
        knotenlasten: Dict[str, Tuple[Vektor, Vektor]] = {}
        for last in fall.lasten:
            if not isinstance(last, Knotenlast):
                continue
            ort = self.ergebnis.orte.get(last.knoten)
            if ort is None:
                melde(f"Knotenlast am Knoten {last.knoten} (Fall «{fall.name}»): dort ist "
                      f"kein Stab, der sie aufnimmt.", last.knoten)
                continue
            if any(abs(skalar(last.M, r)) > 1e-9 * betrag(last.M) for r in ort.offen):
                melde(f"Moment am Knoten {last.knoten} (Fall «{fall.name}»): alle Stäbe "
                      f"sind dort gelenkig angeschlossen, nichts nimmt es auf.", last.knoten)
                continue
            kraft, moment = knotenlasten.get(ort.name, (NULL, NULL))
            knotenlasten[ort.name] = (plus(kraft, last.F), plus(moment, last.M))
            for i, q in zip(ort.verschiebung, ort.frei):
                F[i] += skalar(q, last.F)
            for i, r in zip(ort.drehung, ort.dreh_frei):
                F[i] += skalar(r, last.M)
        return F, teile_f, je_stab, knotenlasten

    # -- Beweglich ----------------------------------------------------------

    def _beweglich(self, zerlegung: Zerlegung) -> None:
        x = zerlegung.bewegung().x
        gross = max(abs(v) for v in x) or 1.0

        def bewegt_sich(indizes) -> bool:
            return any(abs(x[i]) > 1e-6 * gross for i in indizes)

        bewegt: List[str] = []
        verschoben = False
        for ort in self.ergebnis.orte.values():
            name = ort.knoten or ort.stab
            verschoben = verschoben or bewegt_sich(ort.verschiebung)
            if name not in bewegt and bewegt_sich(ort.verschiebung + ort.drehung):
                bewegt.append(name)
        for t in self.ergebnis.teilstaebe:
            if t.stab.name not in bewegt and bewegt_sich(t.gelenkindizes.values()):
                bewegt.append(t.stab.name)
        self.ergebnis.beweglich = bewegt
        liste = ", ".join(bewegt[:-1]) + (" und " if len(bewegt) > 1 else "") + bewegt[-1] \
            if bewegt else "ein Teil"
        if verschoben:
            rat = "Es fehlt ein Lager, ein Stab oder ein Gelenk ist zu viel."
        else:
            # Nur im Raum: in der Ebene haelt jede Drehung ein Stab mit 4EI/L.
            rat = ("Dabei verschiebt sich nichts: Stäbe drehen sich um ihre Achse, und nichts "
                   "hält sie dagegen. Das behebt ein Lager, das diese Drehung festhält – oder "
                   "ein Gelenk an beiden Enden: dann trägt der Stab keine Torsion.")
        self._melden(
            f"Das System ist beweglich – die Steifigkeitsmatrix ist singulär und lässt sich "
            f"nicht invertieren. Ohne Widerstand bewegen sich: {liste}. {rat}", *bewegt)

    # -- Auswerten ----------------------------------------------------------

    def _auswerten(self, fall: Lastfall, kombination: bool, F: List[float], x: List[float],
                   teile_f, je_stab: Dict[str, st3.Lasten], knotenlasten) -> Fall:
        """Alles im Raum gerechnet -- und in den Achsen der Art abgegeben."""
        orte = self.ergebnis.orte
        art = self.art
        verschiebungen = {}
        for name, ort in orte.items():
            u, phi = NULL, NULL
            for i, q in zip(ort.verschiebung, ort.frei):
                u = plus(u, mal(x[i], q))
            for i, r in zip(ort.drehung, ort.dreh_frei):
                phi = plus(phi, mal(x[i], r))
            verschiebungen[name] = art.werte(u, phi)
        teile: List[Teilergebnis] = []
        summen: Dict[str, List[float]] = {name: [0.0] * 6 for name in orte}
        bettung: Dict[str, List[float]] = {}
        for t, (lasten, f) in zip(self.ergebnis.teilstaebe, teile_f):
            d = t.lokal(x)
            kd = st.mal(t.k, d)
            s = [kd[i] - f[i] for i in range(12)]
            teile.append(Teilergebnis(teil=t, lasten=lasten, f=f, d=d, s=s))
            for ort, o, gelenk in ((t.a, 0, t.gelenk_a), (t.b, 6, t.gelenk_b)):
                summe = summen[ort.name]
                # Am Gelenk geht kein Moment in den Knoten.
                summe[:3] = plus(summe[:3], im_system(t.achsen, s[o:o + 3]))
                if not gelenk:
                    summe[3:] = plus(summe[3:], im_system(t.achsen, s[o + 3:o + 6]))
            if t.k_y or t.k_z or t.k_x:
                # Was die Bettung auf das Tragwerk gibt: -k_b · d, in den
                # Achsen des Systems und als Moment um den Ursprung. Die
                # arbeitsgleichen Kraefte haben genau die Resultierende der
                # verteilten -- die Formfunktionen bilden x exakt ab.
                fb = [-v for v in st.mal(t.bettungsmatrix(), d)]
                b = bettung.setdefault(t.stab.name, [0.0] * 6)
                for ort, o in ((t.a, 0), (t.b, 6)):
                    addiere(b, ort.punkt, im_system(t.achsen, fb[o:o + 3]),
                            im_system(t.achsen, fb[o + 3:o + 6]))
        lager: Dict[str, Tuple[Vektor, Vektor]] = {}
        for name, ort in orte.items():
            if not ort.gehalten:
                continue
            kraft, moment = knotenlasten.get(name, (NULL, NULL))
            lager[name] = (minus(summen[name][:3], kraft), minus(summen[name][3:], moment))
        linienlast = self._ins_linienlager(je_stab)
        lastsumme = self._summe_der_lasten(je_stab, knotenlasten)
        rest = list(lastsumme)
        for name, (kraft, moment) in lager.items():
            addiere(rest, orte[name].punkt, kraft, moment)
        for werte in (*linienlast.values(), *bettung.values()):
            for i in range(6):
                rest[i] += werte[i]

        def sechs(werte: Sequence[float]) -> Werte:
            return art.werte(werte[:3], werte[3:])

        return Fall(name=fall.name, kombination=kombination, F=F, x=x, teile=teile,
                    verschiebungen=verschiebungen,
                    lagerkraefte={k: art.werte(*v) for k, v in lager.items()},
                    linienlast={k: sechs(v) for k, v in linienlast.items()},
                    bettung={k: sechs(v) for k, v in bettung.items()},
                    lastsumme=sechs(lastsumme), gleichgewicht=sechs(rest))

    def _ins_linienlager(self, je_stab: Dict[str, st3.Lasten]) -> Dict[str, List[float]]:
        """
        Was fest aufliegende Staebe geradewegs ins Lager geben: ihre Lasten
        in den festen Richtungen, mit umgekehrtem Vorzeichen -- als Kraft auf
        das Tragwerk und Moment um den Ursprung. Eine Linie ohne Stab gibt
        alles hinein.
        """
        heraus: Dict[str, List[float]] = {}
        for name, lasten in je_stab.items():
            stab_ = self.staebe[name]
            if not _hat_festes_linienlager(stab_):
                continue
            anfang, _, achsen = self._geometrie(stab_)
            alles = not stab_.traegt
            werte = st3.resultierende(lasten, anfang, achsen,
                                      laengs=stab_.laengs.fest or alles,
                                      quer_y=stab_.quer_y.fest or alles,
                                      quer_z=stab_.quer_z.fest or alles, torsion=alles)
            heraus[name] = [-w for w in werte]
        return heraus

    def _summe_der_lasten(self, je_stab: Dict[str, st3.Lasten],
                          knotenlasten: Dict[str, Tuple[Vektor, Vektor]]) -> List[float]:
        """Alle Lasten des Falls als Kraft auf das Tragwerk und Moment um den Ursprung."""
        summe = [0.0] * 6
        for name, (kraft, moment) in knotenlasten.items():
            addiere(summe, self.ergebnis.orte[name].punkt, kraft, moment)
        for name, lasten in je_stab.items():
            anfang, _, achsen = self._geometrie(self.staebe[name])
            for i, w in enumerate(st3.resultierende(lasten, anfang, achsen)):
                summe[i] += w
        return summe


def _ende(t: Teilstab, ende: str) -> List[List[Tuple[int, float]]]:
    """Wie u, v, w und θx, θy, θz eines Stabendes an den Unbekannten haengen."""
    ort, gelenk = (t.a, t.gelenk_a) if ende == "a" else (t.b, t.gelenk_b)

    def anteile(achse: Vektor, indizes: Sequence[int], richtungen: Sequence[Vektor]):
        heraus = []
        for i, q in zip(indizes, richtungen):
            b = skalar(achse, q)
            if abs(b) > 1e-14:
                heraus.append((i, b))
        return heraus

    verschiebungen = [anteile(achse, ort.verschiebung, ort.frei) for achse in t.achsen]
    if gelenk:
        drehungen = [[(t.gelenkindizes[ende, i], 1.0)] if (ende, i) in t.gelenkindizes else []
                     for i in range(3)]
    else:
        drehungen = [anteile(achse, ort.drehung, ort.dreh_frei) for achse in t.achsen]
    return verschiebungen + drehungen
