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
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, List, Mapping, Optional, Protocol, Tuple

from opencivil.nachweis.querschnittsloeser import Ebene, Faserloeser
from opencivil.querschnitt.werkstoffgesetz import BLOCKANTEIL
from opencivil.querschnitt.gesetzwahl import Rechenwahl
from opencivil.spannungsanalyse.art import Analyseart

if TYPE_CHECKING:
    from opencivil.core.protokoll import Protokoll, Zwischenwerte
    from opencivil.core.wert import Wert

#: Punkte des gerissenen Teils einer Linie -- vor dem Fliessen ein Drittel,
#: danach der Rest, denn dort waechst die Verformung am staerksten.
KURVENPUNKTE = 40

#: Punkte des ungerissenen Teils. Er ist beinahe gerade.
PUNKTE_UNGERISSEN = 10


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
    wahl: Rechenwahl
    """Womit gerechnet wird -- Kriechzahl, Wertesatz, Rechenart."""

    grenznamen: Tuple[str, ...]
    """Je Grenze des gerissenen Loesers, was sie ist -- fuer «massgebend»."""

    ids: Mapping[str, str]
    """Kurzname -> Wert-ID der Eingaben, fuer die Herleitung."""

    staehle: Tuple[Any, ...]
    """Die Staehle der Bewehrung, jeder einmal -- fuer die Fliessdehnung."""

    E_cm: float
    """Der Modul des Betons -- daran misst sich der aequivalente Modul."""

    bezugsort: str
    """Wo die Mitteldehnung gilt -- dort greift N an."""

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
                                   bruch: "Grenzzustand", oben: "Wert", unten: "Wert") -> None: ...

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

    ``ebene`` fuehrt von einer Verformung zur gerissenen Ebene ``(eps_m,
    chi)`` oder zu ``None``, wo es kein Gleichgewicht gibt; ``kraft`` liest
    aus der Ebene die Kraft der Linie; ``verformung_bei`` sucht zu einer Kraft
    die Verformung, mit einem der beiden Loeser.
    """

    ebene: Callable[[float], Optional[Tuple[float, float]]]
    kraft: Callable[[Tuple[float, float]], float]
    verformung_bei: Callable[[Faserloeser, float], Optional[float]]
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


def _massgebend(paar: Paar, eps_m: float, chi: float) -> str:
    """Welche Grenzdehnung die Ebene erreicht -- die mit dem kleinsten Abstand."""
    bester, abstand = ("", 0.0), math.inf
    for g, name in zip(paar.gerissen.grenzen.grenzen, paar.grenznamen):
        eps = eps_m + chi * g.arm
        for grenze in (g.eps_min, g.eps_max):
            if math.isfinite(grenze) and abs(eps - grenze) < abstand:
                bester, abstand = (name, grenze), abs(eps - grenze)
    name, grenze = bester
    return f"{name} bei {grenze * 1e3:.2f} ‰".replace("-", "−")


def _linie(paar: Paar, weg: _Weg, art: Analyseart, fest: float,
           riss: float) -> Linie:
    """
    Die Linie von null bis zum Bruch: ungerissen bis ``riss``, dort der
    Sprung, darueber gerissen -- ueber die Verformung gerechnet, mit dem
    Fliessbeginn als Punkt der Linie.
    """
    linie = Linie(art=art, fest=fest, riss=riss)
    start = weg.verformung_bei(paar.gerissen, 0.0)
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
    eps_m, chi = ebene
    g = paar.gerissen
    linie.bruch = Grenzzustand(
        kraft=weg.kraft(ebene), verformung=ende, eps_oben=eps_m + chi * g.oben,
        eps_unten=eps_m + chi * g.unten, massgebend=_massgebend(paar, eps_m, chi))
    kraft_u = linie.bruch.kraft
    if kraft_u <= 0.0:
        return linie

    def kraftpunkte(bis: float) -> List[Linienpunkt]:
        punkte = []
        for i in range(PUNKTE_UNGERISSEN + 1):
            # Der letzte genau bei ``bis``: bis * 10 / 10 liegt sonst eine
            # Rundung darueber, beim Riss also schon jenseits des Risses.
            kraft = bis if i == PUNKTE_UNGERISSEN else bis * i / PUNKTE_UNGERISSEN
            v_I = weg.verformung_bei(paar.ungerissen, kraft)
            if v_I is not None:
                punkte.append(Linienpunkt(kraft=kraft, verformung=v_I, gerissen=False,
                                          verformung_I=v_I,
                                          verformung_II=weg.verformung_bei(paar.gerissen, kraft)))
        return punkte

    if riss >= kraft_u:
        # Ungerissen bis zum Bruch: reisst er, traegt er den Riss nicht.
        linie.punkte = kraftpunkte(kraft_u)
        return linie

    arme = [(l.z + g.oben, l.stahl.eps_yd) for l in g.lagen]

    def fliesst(verformung: float) -> bool:
        # Jede Lage an der Fliessdehnung ihres eigenen Stahls.
        e = weg.ebene(verformung)
        return e is not None and any(e[0] + e[1] * a >= eps_y for a, eps_y in arme)

    anfang, risskraft = start, None
    if riss > 0.0:
        linie.punkte = kraftpunkte(riss)
        nach_riss = weg.verformung_bei(paar.gerissen, riss)
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
            verformung_I=(weg.verformung_bei(paar.ungerissen, kraft)
                          if kraft <= riss else None),
            verformung_II=verformung))
    if paar.wahl.art.mit_block:
        linie.hinweisen(
            f"Mit der {BLOCKANTEIL}·x-Vereinfachung trägt der Beton unter "
            f"{1.0 - BLOCKANTEIL:.2f}·ε_c2d nichts: über dem Riss ist die Linie "
            f"weicher als der Querschnitt, ihr Ende ist der Widerstand der "
            f"Vereinfachung. Die Kriechzahl wirkt bei ihr nur auf den "
            f"ungerissenen Teil.")
    return linie


def _durchlaufen(e: Ebene) -> bool:
    """
    Ob eine Linie die Ebene nimmt: gefunden -- oder verfehlt an einem Sprung
    des Spannungsblocks (:attr:`Ebene.verfehlt`). Eine Linie fragt nach der
    Verformung, bei der ihre Kraft einen Wert durchlaeuft; am Sprung ist das
    seine Stelle, auch wenn dort keine Ebene die Kraft genau erzeugt. Ein
    Nachweis dagegen braucht die Ebene selbst.
    """
    return e.konvergiert or e.verfehlt


def moment_kruemmung(paar: Paar, *, N: float) -> Linie:
    """
    Die Momenten-Kruemmungs-Linie bei der Normalkraft ``N`` (Zug positiv):
    ungerissen bis ``M_Riss(N)``, dort der Sprung, darueber gerissen bis zum
    Bruch.
    """
    gerissen = paar.gerissen

    def ebene(chi: float) -> Optional[Tuple[float, float]]:
        eps_m = gerissen.mitteldehnung(chi, N)
        return None if eps_m is None else (eps_m, chi)

    def verformung_bei(loeser: Faserloeser, M: float) -> Optional[float]:
        e = loeser.loese(N_Ed=N, M_Ed=M)
        return e.chi if _durchlaufen(e) else None

    weg = _Weg(ebene=ebene, kraft=lambda e: gerissen.kraefte(*e).M,
               verformung_bei=verformung_bei,
               obergrenze=gerissen.grenzen.kruemmungsgrenze(positiv=True))
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
    gerissen = paar.gerissen

    def ebene(eps_m: float) -> Optional[Tuple[float, float]]:
        chi = gerissen.kruemmung(eps_m, M)
        return None if chi is None else (eps_m, chi)

    def verformung_bei(loeser: Faserloeser, N: float) -> Optional[float]:
        e = loeser.loese(N_Ed=N, M_Ed=M)
        return e.eps_m if _durchlaufen(e) else None

    obergrenze = max(g.eps_max for g in gerissen.grenzen.grenzen if math.isfinite(g.eps_max))
    weg = _Weg(ebene=ebene, kraft=lambda e: gerissen.kraefte(*e).N,
               verformung_bei=verformung_bei, obergrenze=obergrenze)
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
