"""
opencivil/spannungsanalyse/linie.py -- die Linien eines Querschnitts.

VERANTWORTUNG:
Die Momenten-Kruemmungs- und die Normalkraft-Dehnungs-Linie eines Paars von
Loesern, gerissen und ungerissen -- und was ein solches Paar dafuer bieten
muss (:class:`Paar`). Die Platte bietet es je Tragrichtung
(:class:`~opencivil.spannungsanalyse.platte.Loeserpaar`), der gezeichnete
Querschnitt je Zugseite
(:class:`~opencivil.spannungsanalyse.schnitt.Schnittpaar`); bis 2026-10-17
hiess es an den Funktionen dafuer ``paar: Any``.

DIE EBENEN:
Jede Linie fragt einen Zustand des Paars nach Ebenen: zu N und M, zu einer
Kruemmung bei N, zu einer Dehnung bei M (:class:`Ebenensuche`). Die Antwort
ist eine :class:`Dehnungsebene` in der Richtung ihres Loesers. Bei der
Platte und beim gezeichneten Querschnitt «einachsig» bleibt die Nulllinie
parallel zur Achse der Biegung (:class:`FesteNulllinie`); sonst kippt sie,
bis kein Moment um die andere Achse bleibt
(:class:`~opencivil.spannungsanalyse.schnitt.KippendeNulllinie`). Die Linie
selbst weiss davon nichts: sie liest Kraft und Verformung der Ebene.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import cached_property
from typing import (
    TYPE_CHECKING, Any, Callable, List, Mapping, NamedTuple, Optional, Protocol, Tuple,
)

from opencivil.core.suche import ILLINOIS_VON_VORN
from opencivil.nachweis.querschnittsloeser import Faserloeser
from opencivil.querschnitt.werkstoffgesetz import BLOCKANTEIL
from opencivil.querschnitt.gesetzwahl import Rechenwahl
from opencivil.spannungsanalyse.art import Analyseart

if TYPE_CHECKING:
    from opencivil.core.protokoll import Protokoll, Zwischenwerte
    from opencivil.core.wert import Wert
    from opencivil.querschnitt.fasern import Schnittkraefte

#: Wie die Loeser der Analysen suchen, bei der Platte wie am gezeichneten
#: Querschnitt: mit Illinois, jede Frage im ganzen Fenster -- eine Linie fragt
#: ihre Punkte in einer Reihenfolge, und keiner soll an ihr haengen. Wo ein
#: Gesetz springt, halbierend (:func:`~opencivil.nachweis.querschnittsloeser.wirksame_suche`):
#: dort faende Illinois auf einem flachen Stueck einen anderen Punkt. Bis
#: 2026-10-18 halbierten alle; so rechnen alle Analysen des Pruefprojekts in
#: 4.0 statt 5.2 s, die der Platte etwa fuenfmal schneller, und ihre Zahlen
#: bewegen sich erst ab der siebten Stelle (Benutzer, 2026-10-18).
SUCHE_DER_ANALYSEN = ILLINOIS_VON_VORN

#: Punkte des gerissenen Teils einer Linie -- vor dem Fliessen ein Drittel,
#: danach der Rest, denn dort waechst die Verformung am staerksten.
KURVENPUNKTE = 40

#: Punkte des ungerissenen Teils. Er ist beinahe gerade.
PUNKTE_UNGERISSEN = 10


# ===========================================================================
# Die Ebenen eines Zustands
# ===========================================================================


@dataclass(frozen=True)
class Dehnungsebene:
    """
    Eine Dehnungsebene eines Paars -- in der Richtung ihres Loesers, also
    senkrecht zu ihrer Nulllinie. Kippt die Nulllinie um :attr:`neigung`,
    zaehlen Moment und Kruemmung, wie sie zur Achse der Biegung stehen: das
    Moment um diese Achse und die Kruemmung senkrecht zu ihr.
    """

    loeser: Faserloeser
    """Der Querschnitt in der Richtung der Ebene."""

    eps_m: float
    chi: float
    """Dehnung am Arm null und Kruemmung senkrecht zur Nulllinie."""

    neigung: float = 0.0
    """Wie weit die Nulllinie gegen die Achse der Biegung gedreht ist, rad -- gegen den Uhrzeiger."""

    grenznamen: Tuple[str, ...] = ()
    """Je Grenze des Loesers, was sie ist -- fuer «massgebend»."""

    verfehlt: bool = False
    """
    Ob die Suche an einem Sprung des Spannungsblocks haengen blieb
    (:attr:`~opencivil.nachweis.querschnittsloeser.Ebene.verfehlt`). Eine
    Linie nimmt eine solche Ebene: sie fragt nach der Verformung, bei der ihre
    Kraft einen Wert durchlaeuft, und am Sprung ist das seine Stelle, auch wenn
    dort keine Ebene die Kraft genau erzeugt. Ein Bild dagegen braucht die
    Ebene selbst.
    """

    @cached_property
    def kraefte(self) -> "Schnittkraefte":
        """``N``, ``M`` und ``M_quer`` in der Richtung des Loesers."""
        return self.loeser.kraefte(self.eps_m, self.chi)

    @property
    def N(self) -> float:
        return self.kraefte.N

    @property
    def M(self) -> float:
        """Das Moment um die Achse der Biegung -- bei gekippter Nulllinie aus beiden Anteilen."""
        k = self.kraefte
        if self.neigung == 0.0:
            return k.M
        return k.M * math.cos(self.neigung) - k.M_quer * math.sin(self.neigung)

    @property
    def M_quer(self) -> float:
        """Das Moment um die andere Achse -- unter reiner Biegung null."""
        k = self.kraefte
        return k.M * math.sin(self.neigung) + k.M_quer * math.cos(self.neigung)

    @property
    def kruemmung(self) -> float:
        """Die Kruemmung senkrecht zur Achse der Biegung -- ueber sie laeuft die M-χ-Linie."""
        return self.chi if self.neigung == 0.0 else self.chi * math.cos(self.neigung)

    @property
    def eps_oben(self) -> float:
        """Die Dehnung am oberen Rand des Betons, dem gedrueckten bei positivem Moment."""
        return self.eps_m + self.chi * self.loeser.oben

    @property
    def eps_unten(self) -> float:
        return self.eps_m + self.chi * self.loeser.unten

    @property
    def fliesst(self) -> bool:
        """Ob eine Lage die Fliessdehnung erreicht -- jede die ihres eigenen Stahls."""
        oben = self.loeser.oben
        return any(self.eps_m + self.chi * (l.z + oben) >= l.stahl.eps_yd
                   for l in self.loeser.lagen)

    @property
    def massgebend(self) -> str:
        """Welche Grenzdehnung die Ebene erreicht -- die mit dem kleinsten Abstand."""
        bester, abstand = ("", 0.0), math.inf
        for g, name in zip(self.loeser.grenzen.grenzen, self.grenznamen):
            eps = self.eps_m + self.chi * g.arm
            for grenze in (g.eps_min, g.eps_max):
                if math.isfinite(grenze) and abs(eps - grenze) < abstand:
                    bester, abstand = (name, grenze), abs(eps - grenze)
        name, grenze = bester
        return f"{name} bei {grenze * 1e3:.2f} ‰".replace("-", "−")


class Ebenensuche(Protocol):
    """
    Wie ein Zustand eines Paars -- gerissen oder ungerissen -- zu seinen
    Ebenen kommt. Jede Frage hat ihre Ebene oder ``None``, wo es kein
    Gleichgewicht gibt; ``M`` ist das Moment um die Achse der Biegung,
    ``chi`` die Kruemmung senkrecht zu ihr.
    """

    def zu_kraeften(self, N: float, M: float) -> Optional[Dehnungsebene]:
        """Die Ebene, die ``N`` und ``M`` traegt -- auch eine verfehlte (siehe dort)."""

    def zur_kruemmung(self, chi: float, N: float) -> Optional[Dehnungsebene]:
        """Die Ebene mit der Kruemmung ``chi``, die ``N`` traegt."""

    def zur_dehnung(self, eps_m: float, M: float) -> Optional[Dehnungsebene]:
        """Die Ebene mit der Dehnung ``eps_m`` am Arm null, die ``M`` traegt."""


@dataclass(frozen=True)
class FesteNulllinie:
    """
    Die Ebenen in einer festen Richtung: die Nulllinie bleibt parallel zur
    Achse der Biegung, und jede Frage ist eine Suche des Loesers. So rechnet
    die Platte, so rechnet der gezeichnete Querschnitt «einachsig».
    """

    loeser: Faserloeser
    grenznamen: Tuple[str, ...] = ()

    def _ebene(self, eps_m: float, chi: float, *, verfehlt: bool = False) -> Dehnungsebene:
        return Dehnungsebene(loeser=self.loeser, eps_m=eps_m, chi=chi,
                             grenznamen=self.grenznamen, verfehlt=verfehlt)

    def zu_kraeften(self, N: float, M: float) -> Optional[Dehnungsebene]:
        e = self.loeser.loese(N_Ed=N, M_Ed=M)
        if not (e.konvergiert or e.verfehlt):
            return None
        return self._ebene(e.eps_m, e.chi, verfehlt=e.verfehlt)

    def zur_kruemmung(self, chi: float, N: float) -> Optional[Dehnungsebene]:
        eps_m = self.loeser.mitteldehnung(chi, N)
        return None if eps_m is None else self._ebene(eps_m, chi)

    def zur_dehnung(self, eps_m: float, M: float) -> Optional[Dehnungsebene]:
        chi = self.loeser.kruemmung(eps_m, M)
        return None if chi is None else self._ebene(eps_m, chi)


class Zustaende(NamedTuple):
    """Die beiden Zustaende eines Paars, je mit seiner Ebenensuche."""

    gerissen: Ebenensuche
    ungerissen: Ebenensuche


# ===========================================================================
# Was ein Paar bietet
# ===========================================================================


class Paar(Protocol):
    """
    Die beiden Loeser eines Querschnitts, gerissen und ungerissen, und was die
    Fragen und ihre Herleitung sonst von ihm wissen muessen. Was nur die Art
    des Bauteils weiss -- die Tiefe, den Riss, die Dehnung am Ende, den reinen
    Betonquerschnitt --, schreibt das Paar selbst in die Herleitung.
    """

    gerissen: Faserloeser
    ungerissen: Faserloeser
    """Die beiden Loeser in der Richtung des Paars -- fuer das Bild aus Randdehnungen."""

    wahl: Rechenwahl
    """Womit gerechnet wird -- Kriechzahl, Wertesatz, Rechenart."""

    ids: Mapping[str, str]
    """Kurzname -> Wert-ID der Eingaben, fuer die Herleitung."""

    staehle: Tuple[Any, ...]
    """Die Staehle der Bewehrung, jeder einmal -- fuer die Fliessdehnung."""

    E_cm: float
    """Der Modul des Betons -- daran misst sich der aequivalente Modul."""

    bezugsort: str
    """Wo die Mitteldehnung gilt -- dort greift N an."""

    def ebenen(self) -> Zustaende:
        """
        Wie die beiden Zustaende ihre Ebenen finden -- fuer jede Linie und
        jedes Bild neu: eine Suche, die bei der zuletzt gefundenen Neigung
        anfaengt, hinge sonst an dem, was vorher gerechnet wurde.
        """

    @property
    def I_c(self) -> float: ...

    @property
    def A_c(self) -> float: ...

    def rissmoment_bei(self, N: float) -> float: ...

    def rissnormalkraft_bei(self, M: float) -> float: ...

    def tiefe(self, w: "Zwischenwerte", ein: Callable[[str], "Wert"]) -> "Wert": ...

    def herleitung_riss(self, p: "Protokoll", w: "Zwischenwerte", linie: "Linie",
                        ein: Callable[[str], "Wert"], h: "Wert") -> None: ...

    def herleitung_dehnung_am_ende(self, p: "Protokoll", w: "Zwischenwerte",
                                   bruch: "Grenzzustand", oben: "Wert", unten: "Wert",
                                   h: "Wert") -> None: ...

    def herleitung_bezug(self, p: "Protokoll", w: "Zwischenwerte", momente: bool,
                         ein: Callable[[str], "Wert"], h: "Wert") -> "Wert": ...


# ===========================================================================
# Momenten-Kruemmungs- und Normalkraft-Dehnungs-Linie
# ===========================================================================


@dataclass(frozen=True)
class Linienpunkt:
    """
    Ein Punkt einer Linie: die Kraft -- ``M`` bzw. ``N`` --, die Verformung,
    die dort gilt -- ``chi`` bzw. ``eps_m`` --, und beide Zustaende zum
    Vergleich.
    """

    kraft: float
    verformung: float
    """Was gilt: ungerissen bis zum Riss, darueber gerissen."""

    gerissen: bool
    verformung_I: Optional[float]
    """
    Ungerissen -- ``None`` ueber dem Riss, wo der Beton dafuer Zug ohne
    Grenze braeuchte, und wo der Zustand keine Loesung hat.
    """

    verformung_II: Optional[float]
    """Gerissen, ohne Zugfestigkeit des Betons."""


@dataclass(frozen=True)
class Eckpunkt:
    """Ein benannter Punkt einer Linie."""

    kraft: float
    verformung: float


@dataclass(frozen=True)
class Grenzzustand(Eckpunkt):
    """Das Ende einer Linie -- und welche Grenzdehnung es bestimmt."""

    eps_oben: float = 0.0
    eps_unten: float = 0.0
    massgebend: str = ""
    ebene: Optional[Dehnungsebene] = field(default=None, compare=False, repr=False)
    """Die Ebene am Ende -- mit ihrer Richtung, fuer die Herleitung."""


@dataclass
class Linie:
    """
    ``M(chi)`` bei festgehaltener Normalkraft oder ``N(eps_m)`` bei
    festgehaltenem Moment -- welche, sagt :attr:`art`.
    """

    art: Analyseart
    fest: float
    """Was festgehalten wird: ``N`` in N oder ``M`` in Nm."""

    riss: float
    """Die Kraft, bei der der Querschnitt reisst: ``M_Riss(N)`` oder ``N_Riss(M)``."""

    punkte: List[Linienpunkt] = field(default_factory=list)
    bruch: Optional[Grenzzustand] = None
    fliessen: Optional[Eckpunkt] = None
    """Wo der Stahl der am staerksten gezogenen Lage zu fliessen beginnt."""

    hinweis: str = ""

    def hinweisen(self, satz: str) -> None:
        """Einen Satz vor die bisherigen Hinweise stellen."""
        self.hinweis = " ".join(filter(None, [satz, self.hinweis]))

    @property
    def tragfaehig(self) -> bool:
        return self.bruch is not None and self.bruch.kraft > 0.0

    @property
    def sprung(self) -> Optional[Tuple[Linienpunkt, Linienpunkt]]:
        """Die beiden Punkte des Risses: vor und nach dem Reissen, bei derselben Kraft."""
        for vor, nach in zip(self.punkte, self.punkte[1:]):
            if not vor.gerissen and nach.gerissen:
                return vor, nach
        return None


@dataclass(frozen=True)
class _Weg:
    """
    Wie eine Linie laeuft -- der einzige Unterschied zwischen M-chi und N-eps.

    ``ebene`` fuehrt von einer Verformung zur gerissenen Ebene oder zu
    ``None``, wo es kein Gleichgewicht gibt; ``kraft`` liest aus der Ebene die
    Kraft der Linie; ``verformung_I`` und ``verformung_II`` suchen zu einer
    Kraft die Verformung, ungerissen und gerissen.
    """

    ebene: Callable[[float], Optional[Dehnungsebene]]
    kraft: Callable[[Dehnungsebene], float]
    verformung_I: Callable[[float], Optional[float]]
    verformung_II: Callable[[float], Optional[float]]
    obergrenze: float
    """Eine Verformung, ueber der es sicher kein Gleichgewicht mehr gibt."""


def _grenze(gut: Callable[[float], bool], unten: float, oben: float) -> float:
    """Wo ``gut`` endet, zwischen ``unten`` (gut) und ``oben`` -- durch Halbieren."""
    if gut(oben):
        return oben
    for _ in range(60):
        if oben - unten <= 1e-12 * max(1.0, abs(oben)):
            break
        mitte = 0.5 * (unten + oben)
        if gut(mitte):
            unten = mitte
        else:
            oben = mitte
    return unten


def _linie(paar: Paar, weg: _Weg, art: Analyseart, fest: float,
           riss: float) -> Linie:
    """
    Die Linie von null bis zum Bruch: ungerissen bis ``riss``, dort der
    Sprung, darueber gerissen -- ueber die Verformung gerechnet, mit dem
    Fliessbeginn als Punkt der Linie.
    """
    linie = Linie(art=art, fest=fest, riss=riss)
    start = weg.verformung_II(0.0)
    if start is None:
        return linie

    def gut(verformung: float) -> bool:
        return weg.ebene(verformung) is not None

    oben = weg.obergrenze
    while gut(oben) and oben < 1.0:
        oben *= 2.0
    ende = _grenze(gut, start, oben)
    ebene = weg.ebene(ende)
    if ebene is None:
        return linie
    linie.bruch = Grenzzustand(
        kraft=weg.kraft(ebene), verformung=ende, eps_oben=ebene.eps_oben,
        eps_unten=ebene.eps_unten, massgebend=ebene.massgebend, ebene=ebene)
    kraft_u = linie.bruch.kraft
    if kraft_u <= 0.0:
        return linie

    def kraftpunkte(bis: float) -> List[Linienpunkt]:
        punkte = []
        for i in range(PUNKTE_UNGERISSEN + 1):
            # Der letzte genau bei ``bis``: bis * 10 / 10 liegt sonst eine
            # Rundung darueber, beim Riss also schon jenseits des Risses.
            kraft = bis if i == PUNKTE_UNGERISSEN else bis * i / PUNKTE_UNGERISSEN
            v_I = weg.verformung_I(kraft)
            if v_I is not None:
                punkte.append(Linienpunkt(kraft=kraft, verformung=v_I, gerissen=False,
                                          verformung_I=v_I, verformung_II=weg.verformung_II(kraft)))
        return punkte

    if riss >= kraft_u:
        # Ungerissen bis zum Bruch: reisst er, traegt er den Riss nicht.
        linie.punkte = kraftpunkte(kraft_u)
        return linie

    def fliesst(verformung: float) -> bool:
        e = weg.ebene(verformung)
        return e is not None and e.fliesst

    anfang, risskraft = start, None
    if riss > 0.0:
        linie.punkte = kraftpunkte(riss)
        nach_riss = weg.verformung_II(riss)
        if nach_riss is not None:
            anfang, risskraft = nach_riss, riss

    stellen: List[float] = []
    if not fliesst(anfang) and fliesst(ende):
        bei = _grenze(lambda v: not fliesst(v), anfang, ende)
        e = weg.ebene(bei)
        linie.fliessen = Eckpunkt(kraft=weg.kraft(e), verformung=bei)
        vorher = KURVENPUNKTE // 3
        stellen = ([anfang + (bei - anfang) * i / vorher for i in range(vorher)]
                   + [bei + (ende - bei) * i / (KURVENPUNKTE - vorher)
                      for i in range(KURVENPUNKTE - vorher + 1)])
    else:
        stellen = [anfang + (ende - anfang) * i / KURVENPUNKTE for i in range(KURVENPUNKTE + 1)]
        if fliesst(anfang) and riss > 0.0:
            linie.hinweisen("Der Stahl fliesst schon, wenn der Querschnitt reisst.")
        elif not fliesst(ende):
            linie.hinweisen("Bis zum Bruch fliesst kein Stahl: der Beton versagt zuerst.")

    for verformung in stellen:
        e = weg.ebene(verformung)
        if e is None:
            continue
        # Der erste Punkt nach dem Sprung: zu seiner Kraft wurde die
        # Verformung gesucht, also traegt er sie -- genau, nicht bis auf die
        # Schranke der Suche.
        kraft = risskraft if verformung == anfang and risskraft is not None else weg.kraft(e)
        # Ungerissen nur bis zum Riss: darueber haette der Beton Zug ohne
        # Grenze. Der erste Punkt nach dem Sprung traegt genau die Risskraft.
        linie.punkte.append(Linienpunkt(
            kraft=kraft, verformung=verformung, gerissen=True,
            verformung_I=weg.verformung_I(kraft) if kraft <= riss else None,
            verformung_II=verformung))
    if paar.wahl.art.mit_block:
        linie.hinweisen(
            f"Mit der {BLOCKANTEIL}·x-Vereinfachung trägt der Beton unter "
            f"{1.0 - BLOCKANTEIL:.2f}·ε_c2d nichts: über dem Riss ist die Linie "
            f"weicher als der Querschnitt, ihr Ende ist der Widerstand der "
            f"Vereinfachung. Die Kriechzahl wirkt bei ihr nur auf den "
            f"ungerissenen Teil.")
    return linie


def moment_kruemmung(paar: Paar, *, N: float) -> Linie:
    """
    Die Momenten-Kruemmungs-Linie bei der Normalkraft ``N`` (Zug positiv):
    ungerissen bis ``M_Riss(N)``, dort der Sprung, darueber gerissen bis zum
    Bruch.
    """
    gerissen, ungerissen = paar.ebenen()

    def kruemmung_bei(suche: Ebenensuche) -> Callable[[float], Optional[float]]:
        def bei(M: float) -> Optional[float]:
            e = suche.zu_kraeften(N, M)
            return None if e is None else e.kruemmung
        return bei

    weg = _Weg(ebene=lambda chi: gerissen.zur_kruemmung(chi, N), kraft=lambda e: e.M,
               verformung_I=kruemmung_bei(ungerissen), verformung_II=kruemmung_bei(gerissen),
               obergrenze=paar.gerissen.grenzen.kruemmungsgrenze(positiv=True))
    linie = _linie(paar, weg, Analyseart.MOMENT_KRUEMMUNG, N, paar.rissmoment_bei(N))
    if linie.bruch is None or not linie.tragfaehig:
        linie.hinweis = (
            "Schon ohne Moment gibt es keine Gleichgewichtslage – die "
            "Normalkraft allein übersteigt, was der Querschnitt aufnimmt.")
    elif linie.riss >= linie.bruch.kraft:
        linie.hinweisen(
            "Das Rissmoment liegt über dem Biegewiderstand: bis zum Bruch bleibt "
            "der Querschnitt ungerissen, und reisst er, trägt er das Rissmoment "
            "nicht. Bei N = 0 prüft genau das der Nachweis gegen sprödes Versagen.")
    elif linie.riss <= 0.0:
        linie.hinweisen("Schon die Zugkraft allein reisst den Querschnitt auf: die "
                        "ganze Linie gilt gerissen.")
    return linie


def normalkraft_dehnung(paar: Paar, *, M: float) -> Linie:
    """
    Die Normalkraft-Dehnungs-Linie beim Moment ``M``, auf Zug: ungerissen
    bis ``N_Riss(M)``, dort der Sprung, darueber gerissen bis zum Bruch.
    Die Dehnung ist die am Arm null -- dort greift ``N`` an: bei der Platte
    auf halber Hoehe, beim gezeichneten Querschnitt im Schwerpunkt.
    """
    gerissen, ungerissen = paar.ebenen()

    def dehnung_bei(suche: Ebenensuche) -> Callable[[float], Optional[float]]:
        def bei(N: float) -> Optional[float]:
            e = suche.zu_kraeften(N, M)
            return None if e is None else e.eps_m
        return bei

    obergrenze = max(g.eps_max for g in paar.gerissen.grenzen.grenzen
                     if math.isfinite(g.eps_max))
    weg = _Weg(ebene=lambda eps_m: gerissen.zur_dehnung(eps_m, M), kraft=lambda e: e.N,
               verformung_I=dehnung_bei(ungerissen), verformung_II=dehnung_bei(gerissen),
               obergrenze=obergrenze)
    linie = _linie(paar, weg, Analyseart.NORMALKRAFT_DEHNUNG, M, paar.rissnormalkraft_bei(M))
    if linie.bruch is None or not linie.tragfaehig:
        linie.hinweis = (
            "Schon ohne Normalkraft gibt es keine Gleichgewichtslage – das "
            "Moment allein übersteigt, was der Querschnitt aufnimmt.")
    elif linie.riss >= linie.bruch.kraft:
        linie.hinweisen(
            "Die Rissnormalkraft liegt über dem Zugwiderstand: bis zum Bruch bleibt "
            "der Querschnitt ungerissen, und reisst er, trägt er die Rissnormalkraft "
            "nicht.")
    elif linie.riss <= 0.0:
        linie.hinweisen("Schon das Moment allein reisst den Querschnitt auf: die "
                        "ganze Linie gilt gerissen.")
    return linie
