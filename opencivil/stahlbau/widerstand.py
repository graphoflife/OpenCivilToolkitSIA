"""
opencivil/stahlbau/widerstand.py -- was ein Stahlquerschnitt in einem Lastfall aufnimmt.

VERANTWORTUNG:
Zu einem Lastfall -- ``N``, die Momente ``M_y`` und ``M_z`` um den
Bezugspunkt, die Querkraefte ``V_y`` und ``V_z`` -- der Widerstand des
gezeichneten Querschnitts nach SIA 263:2013, ohne Herleitung, in N, mm und
N/mm² (:func:`rechnen`). Die Herleitung schreibt
:mod:`opencivil.nachweis.qa_stahl`. Der Reihe nach:

* grosse Querkraft mindert die Bleche, in denen sie steht (:func:`abmindern`);
* der plastische Zustand bei ``N_Ed`` in der Richtung des Moments
  (:func:`plastisch`) und der elastische, wenn (54) gerade aufgeht -- aus
  beiden die Klasse jedes Blechs;
* der Widerstand nach der Klasse, als Faktor auf das Moment: plastisch in den
  Klassen 1 und 2, elastisch nach (54) in Klasse 3, am wirksamen Querschnitt
  nach (60) in Klasse 4.

DER MASSSTAB:
Wie beim Stahlbeton (:mod:`opencivil.nachweis.schiefe_biegung`): die
Normalkraft bleibt, das Moment waechst in seiner Richtung, bis der
Widerstand erreicht ist -- ``α = M_Rd/M_Ed``. Ohne Moment ``N_Rd/N_Ed``.
Traegt schon die Normalkraft allein nicht, misst ``α`` sie: um welchen
Faktor sie kleiner sein muesste.

PLASTISCH, KLASSEN 1 UND 2 (5.1.1.2, 5.1.8):
Die Norm laesst jeden Spannungszustand zu, der im Gleichgewicht ist und
nirgends ``f_y`` ueberschreitet. Der groesste davon: jede Gruppe ganz
gezogen oder ganz gedrueckt, getrennt an einer geraden Nulllinie. Gesucht
wird die Nulllinie, bei der ``N = N_Ed`` ist und das Moment in die Richtung
der Einwirkung zeigt -- mit derselben Suche wie beim Stahlbeton
(:func:`~opencivil.core.suche.winkel_suchen`); einachsig liegt sie
waagrecht. Das ist das genaue Zusammenwirken, wo (44) bis (48) es naehern:
die Excel-Dateien des Benutzers rechnen mit (44), das auf der sicheren Seite
liegt.

ELASTISCH, KLASSE 3 (54):
``N/N_Rd + M_y/M_y,Rd + M_z/M_z,Rd ≤ 1`` mit ``N_Rd = f_y A/γ_M1`` (5.2.2)
und den elastischen Momenten bis zur weitesten Faser (52). Liegt der
Schwerpunkt des Querschnitts neben dem Bezugspunkt -- weil die Querkraft
einen Teil genommen hat --, zaehlt dazu ``e N`` wie in (60).

AM WIRKSAMEN QUERSCHNITT, KLASSE 4 (60):
``N/A_eff + (M_y + e_z N)/W_y,eff + (M_z + e_y N)/W_z,eff ≤ f_y/γ_M1``, als
Widerstaende geschrieben wie (54): ``A_eff`` und ``e`` vom wirksamen
Querschnitt bei Druck -- bei Zug der ganze --, ``W_eff`` von dem bei Biegung
zur Seite, die das Moment zieht. Ohne Moment (55). Mit mehreren Staehlen
zaehlt je Glied die Gruppe, die zuerst fliesst -- auf der sicheren Seite.
Ein Rundrohr der Klasse 4 rechnet das Werkzeug nicht: SIA 263 nennt dafuer
keine mitwirkende Breite (:attr:`Fall.rohr_klasse_4`).

DIE KLASSE JE LASTFALL -- nach Vorgabe, nicht nachgeschlagen:
``α`` je Blech aus der plastischen Nulllinie im Widerstand, ``ψ`` aus den
elastischen Spannungen, wenn (54) gerade aufgeht -- beide bei der
Normalkraft des Lastfalls, im Zustand, in dem der Querschnitt versagt. Ohne
Moment gleichmaessig gedrueckt oder gezogen. Wo eine frei gezeichnete Flaeche
gedrueckt ist, hoechstens Klasse 3 (:mod:`opencivil.stahlbau.querschnitt`).

QUERKRAFT (5.1.5.1, 5.1.7, 5.2.7, 5.3.6.1):
Uebersteigt ``V_Ed`` die Haelfte von ``V_Rd``, zaehlen die Bleche, in denen
die Querkraft steht (:func:`~opencivil.stahlbau.schub.streifen`), fuer
Normalkraft und Biegung nur noch mit ``1 - (V_Ed/V_Rd)²`` -- beim I der Steg
wie in (43), (53) und (61). Nach Vorgabe, nicht nachgeschlagen: dasselbe
fuer jedes Profil und jede Richtung, auch fuer die Normalkraft, und in den
Klassen 3 und 4 statt der Vergleichsspannung (5.2.7, 5.3.7). Plastisch ist
das ein Spannungszustand nach 5.1.1.2: mit ``τ = V_Ed/A_v`` liesse die
Vergleichsspannung (4.3.5.4) dem Blech ``√(1 - (V_Ed/V_Rd)²)`` seiner
Fliessgrenze -- mehr als ``1 - (V_Ed/V_Rd)²``. Den Querkraftwiderstand
tragen die Profile; ``V_Rd`` ist ihre Summe, und jedes mindert gleich. In
einem Querschnitt aus Rundrohren zaehlt die Resultierende aus ``V_y`` und
``V_z`` (:func:`querkraefte`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.suche import winkel_suchen
from opencivil.querschnitt.biegung import Biegung
from opencivil.querschnitt.geometrie import Punkt
from opencivil.querschnitt.interaktion import WINKEL_SCHRANKE
from opencivil.querschnitt.interaktion import Querschnitt as Faserquerschnitt
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stahlbau import schub
from opencivil.stahlbau.querschnitt import (
    DRUCK, ZUG, Blechzustand, Linie, Stahlquerschnitt, Stueck, Teil, Wirksam, normale,
)

REFERENZ_PLASTISCH = "SIA 263:2013, 5.1.1.2; 5.1.8"
REFERENZ_54 = "SIA 263:2013, 5.2.6, (54); 5.2.2; 5.2.3, (52)"
REFERENZ_60 = "SIA 263:2013, 5.3.5, (60); 4.5.3"
REFERENZ_55 = "SIA 263:2013, 5.3.2, (55)"
REFERENZ_QUERKRAFT = "SIA 263:2013, 5.1.5.1, (43); 5.1.7; 5.2.7; 5.3.6.1"

#: Ab welchem Anteil an ``V_Rd`` die Querkraft die Bleche mindert, in denen sie steht (5.1.5.1).
HALBE_QUERKRAFT = 0.5

#: Warum ein Rundrohr der Klasse 4 nicht gerechnet wird (:attr:`Fall.rohr_klasse_4`).
ROHR_KLASSE_4 = ("Ein Rundrohr der Klasse 4 rechnet das Werkzeug nicht – SIA 263 nennt dafür "
                 "keine mitwirkende Breite.")

#: Ab welchem Moment ein Lastfall als Biegung gilt, in N·mm -- wie beim
#: Stahlbeton (:data:`~opencivil.nachweis.schiefe_biegung.KEIN_MOMENT`, dort in Nm).
KEIN_MOMENT = 1e-3

# -- Querkraft -------------------------------------------------------------------


@dataclass(frozen=True)
class Querkraft:
    """Die Querkraft eines Lastfalls in einer Richtung und was die Profile in ihr tragen, in N."""

    richtung: str
    V_Ed: float
    V_Rd: float
    resultierend: bool = False
    """Ob es die Resultierende ist -- in einem Querschnitt aus Rundrohren (:func:`querkraefte`)."""

    def symbol(self, index: str) -> str:
        """``V_{z,Ed}`` -- die Resultierende ``V_{Ed}``."""
        return f"V_{{{index}}}" if self.resultierend else f"V_{{{self.richtung},{index}}}"

    @property
    def name(self) -> str:
        """Wie sie im Text heisst: «Querkraft in z» oder «resultierende Querkraft»."""
        return "resultierende Querkraft" if self.resultierend else f"Querkraft in {self.richtung}"

    @property
    def gewicht(self) -> float:
        """
        Was die Bleche der Querkraft fuer Normalkraft und Biegung verlieren:
        ``(V_Ed/V_Rd)²``, hoechstens eins -- bis zur Haelfte von ``V_Rd`` nichts.
        """
        if self.V_Rd <= 0.0 or abs(self.V_Ed) <= HALBE_QUERKRAFT * self.V_Rd:
            return 0.0
        return min(1.0, (self.V_Ed / self.V_Rd) ** 2)


def querkraefte(stahl: Stahlquerschnitt, V_y: float, V_z: float,
                V_Rd: Dict[str, float]) -> List[Querkraft]:
    """
    Die Querkraefte eines Lastfalls, wie nachgewiesen: je Richtung, die einen
    Widerstand hat -- in einem Querschnitt aus lauter Rundrohren ihre
    Resultierende, denn ein Rundrohr traegt in jeder Richtung gleich; so
    rechnen auch die Excel-Dateien des Benutzers. Ohne Profil keine.
    """
    if "y" in V_Rd and all(schub.rund(t.flaeche.profil) for t in stahl.profile):
        return [Querkraft("z", math.hypot(V_y, V_z), V_Rd["z"], resultierend=True)]
    return [Querkraft(r, V, V_Rd[r]) for r, V in (("z", V_z), ("y", V_y)) if r in V_Rd]


@dataclass(frozen=True)
class Abgemindert:
    """Der Querschnitt fuer Normalkraft und Biegung, wie die Querkraft ihn laesst (Dateikopf)."""

    stahl: Stahlquerschnitt
    streifen: Tuple[Stueck, ...] = ()
    """
    Was die Querkraft nimmt, je Streifen mit negativem Gewicht -- beim
    Rundrohr dazu das Loch mit positivem.
    """

    weg: Dict[Tuple[int, str], float] = field(default_factory=dict)
    """Je Teil und Blech, welcher Anteil fuer Normalkraft und Biegung fehlt."""

    def rest(self, zustand: Blechzustand) -> float:
        """
        Wie viel von einem Blech noch zaehlt -- sein Streifen der wirksamen
        Breite nimmt nur diesen Rest.
        """
        return 1.0 - self.weg.get((self.stahl.teile.index(zustand.teil), zustand.blech.name), 0.0)


def abmindern(stahl: Stahlquerschnitt, querkraefte: Sequence[Querkraft]) -> Abgemindert:
    """
    Der Querschnitt ohne das, was die Querkraft je Richtung nimmt -- siehe
    Dateikopf. Steht sie in beiden Richtungen im selben Blech -- im
    Rundrohr --, nimmt sie zusammen hoechstens das ganze.
    """
    roh = [(stahl.teile.index(t), t.gruppe, name, q.gewicht * anteil, punkte, q)
           for q in querkraefte if q.gewicht > 0.0 for t in stahl.profile
           for name, anteil, punkte in schub.streifen(t.flaeche.profil, q.richtung)]
    weg: Dict[Tuple[int, str], float] = {}
    for i, _, name, w, _, _ in roh:
        if w > 0.0:
            weg[(i, name)] = weg.get((i, name), 0.0) + w
    # Was eine Querkraft nimmt, heisst nach Blech und Querkraft: «Steg, Querkraft in z».
    streifen = tuple(Stueck(g, -w / max(1.0, weg[(i, name)]), punkte, i, f"{name}, {q.name}")
                     for i, g, name, w, punkte, q in roh)
    return Abgemindert(stahl.mit(streifen) if streifen else stahl, streifen,
                       {k: min(1.0, v) for k, v in weg.items()})


# -- Plastisch -------------------------------------------------------------------


@dataclass(frozen=True)
class Plastisch:
    """
    Der plastische Zustand an einer Nulllinie: was die Spannungsbloecke
    tragen, in N und N·mm um den Bezugspunkt.
    """

    linie: Linie
    N: float
    M_y: float
    M_z: float


def plastisch(stahl: Stahlquerschnitt, f: Sequence[float], N: float, M_y: float, M_z: float,
              bezug: Punkt, neigung: Optional[float]) -> Optional[Plastisch]:
    """
    Der plastische Zustand bei ``N``, dessen Moment in die Richtung von
    ``(M_y, M_z)`` zeigt -- mit fester Zugrichtung ``neigung``, wo sie
    feststeht (:meth:`~opencivil.querschnitt.biegung.Biegung.neigung`).
    ``None``, wo ``N`` jenseits der reinen Zug- oder Druckkraft liegt.
    """
    if abs(N) > stahl.zugkraft(f):
        return None

    def bei(n: Tuple[float, float]) -> Plastisch:
        linie = Linie(n, stahl.nulllinie(n, f, N))
        return Plastisch(linie, *stahl.kraefte(linie, f, bezug))

    if neigung is not None:
        return bei((float(round(math.cos(neigung))), float(round(math.sin(neigung)))))
    ziel = math.atan2(M_z, M_y)

    def abweichung(winkel: float) -> Tuple[float, Plastisch]:
        zustand = bei((math.cos(winkel), math.sin(winkel)))
        if zustand.M_y == 0.0 and zustand.M_z == 0.0:
            return 0.0, zustand
        return math.remainder(math.atan2(zustand.M_z, zustand.M_y) - ziel, 2.0 * math.pi), zustand

    return winkel_suchen(abweichung, Faserquerschnitt.neigung_fuer(M_y, M_z),
                         schranke=WINKEL_SCHRANKE)


# -- Das lineare Zusammenwirken: (54) und (60) -------------------------------------


@dataclass(frozen=True)
class Glied:
    """
    Ein Moment in (54) oder (60): ``|λ·a + b|/R`` -- ``a`` das Moment der
    Einwirkung, ``b = e·N`` der Versatz, ``R`` der Widerstand nach dem
    Vorzeichen von ``λ·a + b``: ``plus`` fuer ein positives Moment.
    """

    achse: str
    a: float
    b: float
    plus: float
    minus: float

    def widerstand(self, faktor: float) -> float:
        return self.plus if faktor * self.a + self.b >= 0.0 else self.minus

    def anteil(self, faktor: float) -> float:
        return abs(faktor * self.a + self.b) / self.widerstand(faktor)


def nutzung(n: float, glieder: Sequence[Glied], faktor: float) -> float:
    """``n + Σ |λ a + b|/R`` -- die linke Seite von (54) und (60)."""
    return n + sum(g.anteil(faktor) for g in glieder)


def skala(n: float, glieder: Sequence[Glied]) -> Optional[float]:
    """
    Das groesste ``λ ≥ 0`` mit ``n + Σ |λ a + b|/R ≤ 1`` -- ``None``, wo
    schon ``λ = 0`` nicht reicht. Die Summe ist in ``λ`` konvex und
    stueckweise gerade: gesucht durch Halbieren, bis auf 1e-12 genau.
    """
    if nutzung(n, glieder, 0.0) > 1.0:
        return None
    if all(g.a == 0.0 for g in glieder):
        return math.inf
    unten, oben = 0.0, 1.0
    while nutzung(n, glieder, oben) <= 1.0:
        unten, oben = oben, 2.0 * oben
    while oben - unten > 1e-12 * oben:
        mitte = 0.5 * (unten + oben)
        unten, oben = (mitte, oben) if nutzung(n, glieder, mitte) <= 1.0 else (unten, mitte)
    return unten


@dataclass(frozen=True)
class Widerstaende:
    """
    Die Widerstaende eines Querschnitts fuer (54) oder (60), in N und N·mm:
    ``N_zug`` und ``N_druck`` als Betraege, je Zugseite das Moment -- und der
    Schwerpunkt, um den die Normalkraft wirkt, bei Zug und bei Druck.
    """

    N_zug: float
    N_druck: float
    M: Dict[Zugseite, float]
    zug: Punkt
    druck: Punkt

    def mitte(self, N: float) -> Punkt:
        return self.druck if N < 0.0 else self.zug

    def glieder(self, N: float, M_y: float, M_z: float, bezug: Punkt,
                einachsig: bool) -> List[Glied]:
        """
        Die Momente von (54) oder (60) um den Schwerpunkt: ``M + e N`` mit
        ``e`` gegen den Bezugspunkt.
        """
        mitte = self.mitte(N)
        e_y, e_z = mitte[0] - bezug[0], mitte[1] - bezug[1]
        glieder = [Glied("y", M_y, e_z * N, self.M[Zugseite.UNTEN], self.M[Zugseite.OBEN])]
        if not einachsig:
            glieder.append(Glied("z", M_z, e_y * N, self.M[Zugseite.LINKS],
                                 self.M[Zugseite.RECHTS]))
        return glieder

    def n(self, N: float) -> float:
        """``N/N_Rd`` mit dem Widerstand seines Vorzeichens."""
        return N / self.N_zug if N >= 0.0 else -N / self.N_druck


def elastische(stahl: Stahlquerschnitt, f: Sequence[float]) -> Widerstaende:
    """Die Widerstaende von (54): ``f_y A`` und je Achse ``f_y W_el`` bis zur weitesten Faser."""
    zug = stahl.zugkraft(f)
    um_y = stahl.elastisch((0.0, 1.0)).moment(f)[0]
    um_z = stahl.elastisch((1.0, 0.0)).moment(f)[0]
    w = stahl.werte()
    return Widerstaende(zug, zug, {Zugseite.UNTEN: um_y, Zugseite.OBEN: um_y,
                                   Zugseite.LINKS: um_z, Zugseite.RECHTS: um_z},
                        (w.y_S, w.z_S), (w.y_S, w.z_S))


def plastische(stahl: Stahlquerschnitt, f: Sequence[float]) -> Widerstaende:
    """
    Die Widerstaende der Klassen 1 und 2, je Achse fuer sich: ``f_y A`` und
    je Zugseite ``f_y W_pl`` bei ``N = 0`` -- fuer das Zusammenwirken im Stab
    (:mod:`opencivil.stahlbau.stabilitaet`).
    """
    zug = stahl.zugkraft(f)
    momente = {}
    for seite in Zugseite:
        n = normale(seite)
        W_pl = stahl.plastisch(n, stahl.nulllinie(n, f))
        momente[seite] = sum(f_g * w for f_g, w in zip(f, W_pl))
    w = stahl.werte()
    return Widerstaende(zug, zug, momente, (w.y_S, w.z_S), (w.y_S, w.z_S))


@dataclass(frozen=True)
class Gebogen:
    """Der wirksame Querschnitt bei Biegung zu einer Seite, in mm und mm⁴."""

    breiten: List[Wirksam]
    I: float
    abstand: float
    """Wie weit die Faser, die zuerst fliesst, von der Nulllinie liegt."""

    gruppe: int
    """In welcher Gruppe sie liegt."""


@dataclass(frozen=True)
class Wirksame:
    """Der wirksame Querschnitt fuer (60) -- bei Druck und je Zugseite bei Biegung."""

    widerstaende: Widerstaende
    druck: List[Wirksam]
    """Die mitwirkenden Breiten bei Druck."""

    A_eff: float
    biegung: Dict[Zugseite, Gebogen]


def wirksame(ab: Abgemindert, f: Sequence[float], eps: Sequence[float],
             seiten: Sequence[Zugseite]) -> Optional[Wirksame]:
    """Die Widerstaende von (60) -- ``None`` mit einem Rundrohr der Klasse 4."""
    stahl = ab.stahl
    gefunden = stahl.wirksamer(stahl.zustaende(DRUCK, DRUCK, eps), DRUCK, eps, ab.rest)
    if gefunden is None:
        return None
    druck, netto = gefunden
    momente: Dict[Zugseite, float] = {}
    biegung: Dict[Zugseite, Gebogen] = {}
    for seite in Zugseite:
        if seite not in seiten:
            momente[seite] = math.inf
            continue
        n = normale(seite)
        el = stahl.elastisch(n)
        zustaende = stahl.zustaende(Linie(n, stahl.nulllinie(n, f)), el.linie, eps)
        gebogen = stahl.wirksamer(zustaende, el.linie, eps, ab.rest)
        if gebogen is None:
            return None
        breiten, wirksam = gebogen
        e = wirksam.elastisch(n)
        momente[seite], g = e.moment(f)
        biegung[seite] = Gebogen(breiten, e.I, e.abstaende[g], g)
    brutto, w = stahl.werte(), netto.werte()
    return Wirksame(Widerstaende(stahl.zugkraft(f), netto.zugkraft(f), momente,
                                 (brutto.y_S, brutto.z_S), (w.y_S, w.z_S)),
                    druck, w.A, biegung)


def spannungslinie(stahl: Stahlquerschnitt, N: float, M_y: float, M_z: float, bezug: Punkt,
                   einachsig: bool, faktor: float) -> Linie:
    """
    Die Nulllinie der elastischen Spannungen bei ``λ``, y und z als
    Hauptachsen: ``σ = N/A - M_y (z - z_S)/I_y - M_z (y - y_S)/I_z`` mit den
    Momenten ``λ M + e N`` um den Schwerpunkt -- einachsig ohne ``M_z``.
    """
    werte = stahl.werte()
    y_S, z_S = werte.y_S, werte.z_S
    um_y = faktor * M_y + (z_S - bezug[1]) * N
    um_z = 0.0 if einachsig else faktor * M_z + (y_S - bezug[0]) * N
    g = (-um_z / werte.I_z, -um_y / werte.I_y)
    betrag = math.hypot(*g)
    if betrag == 0.0:
        return DRUCK if N < 0.0 else ZUG
    n = (g[0] / betrag, g[1] / betrag)
    return Linie(n, n[0] * y_S + n[1] * z_S - N / werte.A / betrag)


# -- Ein Lastfall ---------------------------------------------------------------------


@dataclass
class Fall:
    """Was ein Lastfall am Querschnitt ergibt -- siehe Dateikopf. Kraefte in N, Momente in N·mm."""

    N: float
    M_y: float
    M_z: float
    moment: float
    """Der Betrag des Moments, das zaehlt (:meth:`~opencivil.querschnitt.biegung.Biegung.betrag`)."""

    querkraefte: Tuple[Querkraft, ...]
    abgemindert: Abgemindert
    elastisch: Widerstaende
    zustaende: List[Blechzustand]
    freie: List[Teil]
    """Die frei gezeichneten Flaechen, die gedrueckt sind."""

    klasse: int
    plastisch: Optional[Plastisch] = None
    faktor_54: Optional[float] = None
    wirksam: Optional[Wirksame] = None
    glieder: List[Glied] = field(default_factory=list)
    """Die Momente von (54) oder (60), nach der Klasse."""

    alpha: Optional[float] = None
    """
    Der Erfuellungsgrad -- ``None``, wo schon die Normalkraft nicht traegt
    (dann :attr:`alpha_N`) oder ein Rundrohr der Klasse 4 nichts.
    """

    alpha_N: Optional[float] = None
    """Wo die Normalkraft allein nicht traegt: um welchen Faktor sie kleiner sein muesste."""

    @property
    def ohne_moment(self) -> bool:
        return self.moment <= KEIN_MOMENT

    @property
    def rohr_klasse_4(self) -> bool:
        return self.klasse == 4 and self.wirksam is None

    @property
    def n(self) -> float:
        """``N/N_Rd`` der Klasse -- in Klasse 4 mit dem wirksamen Querschnitt."""
        w = self.wirksam.widerstaende if self.klasse == 4 else self.elastisch
        return w.n(self.N)


def rechnen(stahl: Stahlquerschnitt, f: Sequence[float], eps: Sequence[float], N: float,
            M_y: float, M_z: float, querkraefte: Sequence[Querkraft], bezug: Punkt,
            biegung: Biegung) -> Fall:
    """
    Ein Lastfall am Querschnitt -- siehe Dateikopf. ``f`` je Gruppe die
    Fliessgrenze, mit der gerechnet wird, ``eps`` ihr ``ε``; ``M_y`` und
    ``M_z``, wie sie zaehlen (:meth:`~opencivil.querschnitt.biegung.Biegung.wirkt`).
    """
    ab = abmindern(stahl, querkraefte)
    el = elastische(ab.stahl, f)
    moment = biegung.betrag(M_y, M_z)
    gleichmaessig = DRUCK if N < 0.0 else ZUG
    if moment <= KEIN_MOMENT:
        fall = _fall(ab, el, eps, N, M_y, M_z, moment, querkraefte, gleichmaessig, gleichmaessig)
        if fall.klasse == 4:
            fall.wirksam = wirksame(ab, f, eps, ())
            if fall.wirksam is None:
                return fall
        fall.alpha = 1.0 / fall.n if N != 0.0 else math.inf
        return fall

    pl = plastisch(ab.stahl, f, N, M_y, M_z, bezug, biegung.neigung(M_y))
    glieder = el.glieder(N, M_y, M_z, bezug, biegung.einachsig)
    faktor = skala(el.n(N), glieder)
    linie_el = spannungslinie(ab.stahl, N, M_y, M_z, bezug, biegung.einachsig,
                              faktor if faktor is not None else 0.0)
    fall = _fall(ab, el, eps, N, M_y, M_z, moment, querkraefte,
                 pl.linie if pl is not None else gleichmaessig, linie_el)
    fall.plastisch, fall.faktor_54 = pl, faktor
    if fall.klasse <= 2:
        if pl is None:
            fall.alpha_N = 1.0 / el.n(N)
        else:
            fall.alpha = biegung.betrag(pl.M_y, pl.M_z) / moment
        return fall
    if fall.klasse == 4:
        fall.wirksam = wirksame(ab, f, eps, biegung.zugseiten)
        if fall.wirksam is None:
            return fall
        glieder = fall.wirksam.widerstaende.glieder(N, M_y, M_z, bezug, biegung.einachsig)
        faktor = skala(fall.n, glieder)
    fall.glieder = glieder
    if faktor is None:
        fall.alpha_N = 1.0 / nutzung(fall.n, glieder, 0.0)
    else:
        fall.alpha = faktor
    return fall


def _fall(ab: Abgemindert, el: Widerstaende, eps: Sequence[float], N: float, M_y: float,
          M_z: float, moment: float, querkraefte: Sequence[Querkraft], pl: Linie,
          linie_el: Linie) -> Fall:
    """
    Der Fall mit seinen Klassen: je Blech an den beiden Nulllinien,
    gedrueckte freie Flaechen hoechstens 3.
    """
    zustaende = ab.stahl.zustaende(pl, linie_el, eps)
    freie = ab.stahl.freie_gedrueckt(pl, linie_el)
    klasse = max([z.klasse for z in zustaende] + [3 for _ in freie], default=1)
    return Fall(N, M_y, M_z, moment, tuple(querkraefte), ab, el, zustaende, freie, klasse)
