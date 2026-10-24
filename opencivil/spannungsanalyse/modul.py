"""
opencivil/spannungsanalyse/modul.py -- der aequivalente E-Modul.

VERANTWORTUNG:
Die letzten zwei Fragen: eine Linie, umgerechnet in den Modul, den ein
reiner, ungerissener, elastischer Betonquerschnitt braeuchte, um sich gleich
stark zu kruemmen oder zu dehnen (:class:`Modullinie`). Und derselbe Modul
an einer Stelle der Linie, fuer die Staebe eines Balkensystems
(:func:`modul_bei`, :class:`Modulfrage`): dort geht er in die Rechnung ein,
darum rechnet ihn das Rechenwerk, nicht die Auswertung danach. Gefragt wird
eine Querschnittsanalyse (:class:`ModulAusAnalyse`) oder eine Platte
(:class:`ModulAusPlatte`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Tuple

from opencivil.core.berechnung import (
    Ausfuehrung, Befundbezug, Berechnung, Eingabebezug, Eingaben, Prozedur, Vorgabe,
)
from opencivil.core.einheiten import KN, KNM, MIO_MM4, N_PRO_MM2, Groesse
from opencivil.core.protokoll import Abschnitt, Protokoll, Zwischenwerte
from opencivil.core.wert import Quelle, WertDef
from opencivil.material.basis import mit_index
from opencivil.nachweis.rechenwahl import betonbezuege, lagenbezuege
from opencivil.querschnitt.gesetzwahl import Rechenwahl
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.spannungsanalyse.art import Analyseart
from opencivil.spannungsanalyse.linie import Linie, Paar
from opencivil.spannungsanalyse.platte import loeserpaar
from opencivil.spannungsanalyse.schnitt import schnittpaar


# ===========================================================================
# Der aequivalente E-Modul
# ===========================================================================

#: Unter diesem Anteil der groessten Kraft der Linie gilt eine Kraft als null --
#: der erste Punkt einer gerissen beginnenden Linie traegt null bis auf die
#: Schranke des Loesers.
NULLKRAFT = 1e-6


@dataclass(frozen=True)
class Modulpunkt:
    """
    Ein Punkt der Linie des aequivalenten Moduls: die laufende Kraft und der
    Modul, der dort gilt -- dazu beide Zustaende zum Vergleich, wie bei der
    Linie, aus der er stammt.
    """

    kraft: float
    modul: Optional[float]
    """In Pa; ``None``, wo er nichts sagt."""

    gerissen: bool
    modul_I: Optional[float]
    modul_II: Optional[float]


@dataclass
class Modullinie:
    """
    Der aequivalente E-Modul ueber dem Moment oder ueber der Normalkraft.

    Der Modul, den ein reiner Betonquerschnitt braeuchte -- ungerissen, ohne
    Stahl, elastisch --, um sich unter der laufenden Kraft gleich stark zu
    kruemmen bzw. zu dehnen wie der bewehrte Querschnitt::

        E_eq = M / (I_c · (chi - chi_0))       I_c = b·h³/12
        E_eq = N / (A_c · (eps_m - eps_0))     A_c = b·h

    Gezaehlt wird ab dem Zustand ohne laufende Kraft -- ``chi_0`` bei M = 0
    unter der festen Normalkraft, ``eps_0`` bei N = 0 unter dem festen
    Moment --, nach Vorgabe (2026-10-11). Was die festgehaltene Kraft allein
    verformt, kann ein gerader, ungerissener Betonquerschnitt nicht abbilden:
    bei unsymmetrischer Bewehrung kruemmt schon eine Normalkraft, und ein
    gerissener Querschnitt dehnt sich schon unter dem Moment allein. Ab null
    gezaehlt, ergaebe das nahe null Ausreisser -- am Beispiel bei M = 30 kNm
    und N = 16 kN 99 500 N/mm², fast das Dreifache von E_cm. Ist die feste
    Kraft null, ist es genau ``M = E·I·chi`` bzw. ``N = E·A·eps``.

    Umgerechnet wird jeder Punkt der :class:`Linie`; gerechnet wird nichts
    Neues. So kann diese Linie nichts anderes zeigen als die M-chi- oder
    N-eps-Linie daneben.
    """

    art: Analyseart
    linie: Linie
    """Die M-chi- oder N-eps-Linie, aus der umgerechnet wird."""

    bezug: float
    """``I_c`` in m⁴ bzw. ``A_c`` in m² -- der reine Betonquerschnitt."""

    null: float
    """Die Verformung ohne laufende Kraft: ``chi_0`` bzw. ``eps_0``."""

    E_cm: float
    """Zum Vergleich: ``E_eq/E_cm`` ist der Faktor, um den man E_cm abmindert."""

    punkte: List[Modulpunkt] = field(default_factory=list)

    def modul(self, kraft: float, verformung: float) -> Optional[float]:
        """``Kraft / (Bezug · (Verformung − null))`` -- ``None``, wo das nichts sagt."""
        aenderung = verformung - self.null
        if kraft == 0.0 or aenderung == 0.0:
            return None
        return kraft / (self.bezug * aenderung)

    @property
    def ungerissen(self) -> Optional[float]:
        """Der Modul des ungerissenen Teils -- dort ist der Querschnitt linear."""
        return next((p.modul for p in reversed(self.punkte)
                     if not p.gerissen and p.modul is not None), None)

    @property
    def riss(self) -> Optional[float]:
        """Der Modul gleich nach dem Riss, bei derselben Kraft."""
        sprung = self.linie.sprung
        return None if sprung is None else self.modul(sprung[1].kraft, sprung[1].verformung)

    @property
    def fliessen(self) -> Optional[float]:
        f = self.linie.fliessen
        return None if f is None else self.modul(f.kraft, f.verformung)

    @property
    def ende(self) -> Optional[float]:
        """Der Modul am Ende der Linie -- beim Bruch, oder ungerissen, wenn sie es bleibt."""
        return next((p.modul for p in reversed(self.punkte) if p.modul is not None), None)


def aequivalenter_modul(linie: Linie, *, I_c: float, A_c: float, E_cm: float) -> Modullinie:
    """
    Die M-chi- oder N-eps-Linie als Linie des aequivalenten Moduls -- siehe
    :class:`Modullinie`. Beide Vergleichszustaende zaehlen ab ihrer eigenen
    Verformung ohne laufende Kraft. ``I_c`` und ``A_c`` sind der reine
    Betonquerschnitt, an dem sich der Modul misst.
    """
    momente = linie.art is Analyseart.MOMENT_KRUEMMUNG
    art = Analyseart.MOMENT_EMODUL if momente else Analyseart.NORMALKRAFT_EMODUL
    bezug = I_c if momente else A_c
    if not linie.punkte:
        return Modullinie(art, linie, bezug, 0.0, E_cm)

    # Der erste Punkt ist der Zustand ohne laufende Kraft -- ungerissen bei
    # null, oder gerissen bis auf die Schranke des Loesers.
    massstab = max(abs(p.kraft) for p in linie.punkte) or 1.0
    erster = linie.punkte[0]
    ohne = abs(erster.kraft) <= NULLKRAFT * massstab
    null, null_I, null_II = ((erster.verformung, erster.verformung_I, erster.verformung_II)
                             if ohne else (0.0, 0.0, 0.0))
    modul = Modullinie(art, linie, bezug, null, E_cm)

    def geteilt(kraft: float, verformung: Optional[float],
                ab: Optional[float]) -> Optional[float]:
        if verformung is None or ab is None or kraft == 0.0 or verformung == ab:
            return None
        return kraft / (bezug * (verformung - ab))

    for p in (linie.punkte[1:] if ohne else linie.punkte):
        modul.punkte.append(Modulpunkt(
            kraft=p.kraft, modul=geteilt(p.kraft, p.verformung, null), gerissen=p.gerissen,
            modul_I=geteilt(p.kraft, p.verformung_I, null_I),
            modul_II=geteilt(p.kraft, p.verformung_II, null_II)))

    # Bei null ist der Modul null durch null. Ungerissen ist der Querschnitt
    # linear: dort gilt der Wert des naechsten Punkts genau, und die Linie
    # beginnt bei null statt beim ersten Schritt.
    if ohne and not erster.gerissen and modul.punkte and not modul.punkte[0].gerissen:
        naechster = modul.punkte[0]
        modul.punkte.insert(0, Modulpunkt(
            kraft=0.0, modul=naechster.modul, gerissen=False,
            modul_I=naechster.modul_I, modul_II=naechster.modul_II))
    return modul


# ===========================================================================
# Der Modul an einer Stelle -- fuer die Staebe eines Balkensystems
# ===========================================================================


@dataclass(frozen=True)
class Modulstelle:
    """Der aequivalente Modul bei N und M -- und woraus er folgt, fuer die Herleitung."""

    N: float
    M: float
    """Das Moment, bei dem gerechnet wurde, zur Zugseite -- bei M = 0 das halbe Rissmoment."""

    riss: float
    """``M_Riss(N)``."""

    gerissen: bool
    chi_0: float
    """Die Kruemmung ohne Moment -- ab ihr wird gezaehlt."""

    chi: float
    I_c: float
    modul: float
    """In Pa."""


def modul_bei(paar: Paar, *, N: float, M: float) -> Tuple[Optional[Modulstelle], str]:
    """
    Der aequivalente E-Modul bei der Normalkraft ``N`` (Zug positiv) und dem
    Moment ``M >= 0`` zur Zugseite des Paars, in SI -- an derselben Stelle der
    M-E_eq-Linie (:func:`aequivalenter_modul` ueber
    :func:`~opencivil.spannungsanalyse.linie.moment_kruemmung`): ungerissen
    bis ``M_Riss(N)``, darueber gerissen, gezaehlt ab der Kruemmung ohne
    Moment. Bei ``M = 0`` der Wert, mit dem die Linie beginnt -- ungerissen
    ist der Querschnitt linear, das halbe Rissmoment gibt ihn genau.

    Ohne Gleichgewicht ``None``, dazu der Satz, warum -- klein beginnend, er
    steht hinter einem Doppelpunkt.
    """
    gerissen, ungerissen = paar.ebenen()
    riss = paar.rissmoment_bei(N)
    if M == 0.0:
        if riss <= 0.0:
            return None, ("schon die Normalkraft allein reisst den Querschnitt auf – "
                          "ohne Moment gibt es kein E_eq.")
        M = 0.5 * riss
    null = (ungerissen if riss > 0.0 else gerissen).zu_kraeften(N, 0.0)
    if null is None:
        return None, ("schon ohne Moment gibt es keine Gleichgewichtslage – die "
                      "Normalkraft allein übersteigt, was der Querschnitt aufnimmt.")
    ist_gerissen = M > riss
    ebene = (gerissen if ist_gerissen else ungerissen).zu_kraeften(N, M)
    if ebene is None:
        return None, ("bei diesem Moment gibt es keine Gleichgewichtslage – es "
                      "übersteigt den Biegewiderstand bei dieser Normalkraft.")
    linie = Modullinie(Analyseart.MOMENT_EMODUL, Linie(Analyseart.MOMENT_KRUEMMUNG, N, riss),
                       paar.I_c, null.kruemmung, paar.E_cm)
    modul = linie.modul(M, ebene.kruemmung)
    if modul is None:
        return None, "unter diesem Moment krümmt sich der Querschnitt nicht."
    return Modulstelle(N=N, M=M, riss=riss, gerissen=ist_gerissen, chi_0=null.kruemmung,
                       chi=ebene.kruemmung, I_c=paar.I_c, modul=modul), ""


@dataclass(frozen=True)
class Modulbefund:
    """Was die Suche nach E_eq fand: die Stelle -- oder warum es keine gibt."""

    stelle: Optional[Modulstelle]
    grund: str = ""


#: Was eine Suche ohne Bewehrung sagt -- in der Analyse und in der Platte.
OHNE_BEWEHRUNG = "ohne sie gibt es keine Momenten-Krümmungs-Linie."


@dataclass(frozen=True)
class ModulAusAnalyse:
    """
    Woher das E_eq kommt: eine Querschnittsanalyse -- das Paar ihrer
    Spannung-Dehnung-Analyse in der Zugrichtung des Moments
    (:func:`~opencivil.spannungsanalyse.schnitt.schnittpaar`).
    """

    analyse: Any
    """Die :class:`~opencivil.querschnitt.analyse.Querschnittsanalyse`."""

    @property
    def text(self) -> str:
        return f"Querschnittsanalyse «{self.analyse.name}»"

    def bezuege(self, wahl: Rechenwahl) -> List[Eingabebezug]:
        """Was das Paar liest: Schwerpunkt, Werkstoffe, Flaeche und Traegheitsmomente."""
        return [*self.analyse.grundbezuege(),
                *(Eingabebezug(k, self.analyse.id_von(k)) for k in ("A", "I_y", "I_z", "I_yz"))]

    def paar(self, M: float, wert: Callable[[str], float],
             wahl: Rechenwahl) -> Tuple[Optional[Paar], str, str]:
        """Das Paar zur Zugseite von ``M``, wie sie heisst -- ohne Paar warum."""
        seite = Zugseite.UNTEN if M >= 0.0 else Zugseite.OBEN
        paar = schnittpaar(self.analyse, seite, wert, wahl)
        grund = "" if paar else f"der Querschnitt hat keine Bewehrung – {OHNE_BEWEHRUNG}"
        return paar, seite.beschriftung, grund


@dataclass(frozen=True)
class ModulAusPlatte:
    """
    Woher das E_eq kommt: eine Platte -- immer in x-Richtung und mit Zug
    unten (Benutzer, 2026-10-24), das Paar ihrer Spannung-Dehnung-Analyse
    (:func:`~opencivil.spannungsanalyse.platte.loeserpaar`). Ein negatives
    Moment hat darum kein E_eq: es zoege oben.
    """

    platte: Any
    """Der :class:`~opencivil.querschnitt.platte.Plattenquerschnitt`."""

    @property
    def text(self) -> str:
        return f"Platte «{self.platte.name}»"

    def bezuege(self, wahl: Rechenwahl) -> List[Eingabebezug]:
        """Was das Paar liest: Dicke und Breite in x, der Beton, die Lagen in x."""
        beton = self.platte.beton
        return [Eingabebezug("h", self.platte.id_von("h")),
                Eingabebezug("b", self.platte.id_breite(Richtung.X)),
                *betonbezuege(wahl.satz, beton), Eingabebezug("f_ctm", beton.id_von("f_ctm")),
                *lagenbezuege(self.platte.posten_in_richtung(Richtung.X), wahl.satz)]

    def paar(self, M: float, wert: Callable[[str], float],
             wahl: Rechenwahl) -> Tuple[Optional[Paar], str, str]:
        """Das Paar in x mit Zug unten -- ohne Paar warum."""
        seite = "x-Richtung, Zug unten"
        if M < 0.0:
            return None, seite, ("bei einer Platte zieht das Moment für E_eq unten – ein "
                                 "negatives Moment hat keines.")
        paar = loeserpaar(self.platte, Richtung.X, wert, wahl)
        return paar, seite, "" if paar else f"in x-Richtung liegt keine Bewehrung – {OHNE_BEWEHRUNG}"


@dataclass(frozen=True)
class Modulfrage:
    """
    Das E_eq eines Querschnitts bei ``N`` in kN (Zug positiv) und ``M`` in
    kNm (positiv mit Zug unten), fuer die Staebe eines Balkensystems mit
    ihm (Benutzer, 2026-10-23) -- gerechnet mit ``wahl`` wie eine
    Spannung-Dehnung-Analyse ihrer ``quelle``.
    """

    quelle: Any
    """:class:`ModulAusAnalyse` oder :class:`ModulAusPlatte`."""

    N: float
    M: float
    wahl: Rechenwahl

    def einbauen(self, definieren: Callable[..., WertDef], *, wo: str, index: str, name: str,
                 abschnitt: Abschnitt) -> Tuple[List[Berechnung], str, str]:
        """
        Die Berechnungen dazu, im Namensraum des Systems: N und M als
        Vorgaben, die Suche (:class:`ModulProzedur`) und E aus ihrem Befund
        (:class:`ModulAusBefund`). ``definieren(kurzname, symbol, einheit,
        beschreibung, stellen)`` legt einen Wert des Systems an. Zurueck die
        Berechnungen, die Wert-ID von E -- sie fehlt, wo die Suche keinen
        Modul fand -- und die ID der Suche.
        """
        d_N = definieren(wo + "N_eq", mit_index("N", index), KN, f"Normalkraft für E_eq, {name}", 1)
        d_M = definieren(wo + "M_eq", mit_index("M", index), KNM, f"Moment für E_eq, {name}", 1)
        d_E = definieren(wo + "E", mit_index("E", index), N_PRO_MM2, f"E-Modul, {name}", 0)
        suche = f"{d_E.id}_eq"
        return [
            Vorgabe(id=d_N.id, ausgabe=d_N, groesse=Groesse(self.N, KN), quelle=Quelle.EINGABE,
                    titel=f"Normalkraft für E_eq, «{name}»", abschnitt=abschnitt),
            Vorgabe(id=d_M.id, ausgabe=d_M, groesse=Groesse(self.M, KNM), quelle=Quelle.EINGABE,
                    titel=f"Moment für E_eq, «{name}»", abschnitt=abschnitt),
            ModulProzedur(self, id=suche, N_id=d_N.id, M_id=d_M.id, name=name,
                          abschnitt=abschnitt),
            ModulAusBefund(id=f"{d_E.id}_aus", ausgabe=d_E, suche=suche, name=name,
                           abschnitt=abschnitt),
        ], d_E.id, suche


class ModulProzedur(Prozedur):
    """
    Sucht das E_eq einer :class:`Modulfrage`: mit dem Paar ihrer Quelle, an
    der Stelle der M-E_eq-Linie (:func:`modul_bei`). Ohne Ausgabe -- ihr
    Befund ist der :class:`Modulbefund`, und die Herleitung sagt, was sie
    fand. So haelt ein Moment ueber dem Widerstand nur das System auf, nicht
    das Projekt.
    """

    def __init__(self, frage: Modulfrage, *, id: str, N_id: str, M_id: str, name: str,
                 abschnitt: Abschnitt) -> None:
        bezuege = [*frage.quelle.bezuege(frage.wahl),
                   Eingabebezug("N", N_id), Eingabebezug("M", M_id)]
        super().__init__(id, ausgaben=[], bezuege=bezuege, abschnitt=abschnitt,
                         titel=f"Äquivalenter E-Modul, «{name}»")
        self.frage = frage

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        N, M = e.g("N").si, e.g("M").si
        paar, seite, grund = self.frage.quelle.paar(M, e.si_nach_id(), self.frage.wahl)
        befund = (Modulbefund(None, grund) if paar is None
                  else Modulbefund(*modul_bei(paar, N=N, M=abs(M))))
        self._schreiben(p, seite, befund)
        return Ausfuehrung({}, befund=befund)

    def _schreiben(self, p: Protokoll, seite: str, befund: Modulbefund) -> None:
        p.erklaerung(
            "Der äquivalente E-Modul eines Stabs: der Modul, den ein reiner, "
            "ungerissener Betonquerschnitt bräuchte, um sich unter dem Moment gleich "
            "stark zu krümmen wie der bewehrte. An derselben Stelle wie die Linie "
            "M–E_eq der Spannung-Dehnung-Analyse: ungerissen bis zum Rissmoment, "
            "darüber gerissen, gezählt ab der Krümmung ohne Moment. Er gilt für EA "
            "und EI jedes Stabs mit diesem Querschnitt und seinem Material.")
        p.text(f"{self.frage.quelle.text}, {seite}, {self.frage.wahl.beschriftung}.")
        s = befund.stelle
        if s is None:
            p.text(f"Kein E_eq: {befund.grund}")
            return
        w = Zwischenwerte(self.id)
        p.wert(w.moment("M_r", r"M_{Riss}", s.riss, "Rissmoment bei dieser Normalkraft"))
        p.text("Das Moment liegt über dem Rissmoment: der Querschnitt gilt gerissen."
               if s.gerissen else "Das Moment liegt nicht über dem Rissmoment: der "
                                  "Querschnitt gilt ungerissen.")
        werte = {
            "M": w.moment("M", "M", s.M, "Moment"),
            "I_c": w.wert("I_c", "I_c", Groesse.aus_si(s.I_c, MIO_MM4), 1,
                          "reiner Betonquerschnitt"),
            "chi": w.kruemmung("chi", r"\chi", s.chi, "Krümmung bei M"),
            "chi_0": w.kruemmung("chi_0", r"\chi_0", s.chi_0, "Krümmung ohne Moment"),
        }
        p.formel(w.spannung("E_eq", r"E_{eq}", s.modul, "Äquivalenter E-Modul"),
                 r"\frac{@M}{@I_c \cdot \left(@chi - @chi_0\right)}", werte,
                 titel=self.titel, name="Äquivalenter E-Modul eines Stabs")


class ModulAusBefund(Prozedur):
    """
    E aus dem Befund der Suche -- nur, wo sie einen Modul fand. Sonst ist sie
    nicht anwendbar: E fehlt, mit ihm EA und EI, und das System sagt warum.
    """

    def __init__(self, *, id: str, ausgabe: WertDef, suche: str, name: str,
                 abschnitt: Abschnitt) -> None:
        super().__init__(id, ausgaben=[ausgabe], befunde=[Befundbezug("suche", suche)],
                         abschnitt=abschnitt, titel=f"E-Modul, «{name}» (E_eq)")
        self.ausgabe = ausgabe

    def anwendbar(self, e: Eingaben) -> Tuple[bool, str]:
        befund = e.befund("suche")
        return befund.stelle is not None, befund.grund

    def rechne(self, e: Eingaben, p: Protokoll) -> dict:
        wert = self.ausgabe.belegen(Groesse.aus_si(e.befund("suche").stelle.modul, N_PRO_MM2))
        p.wert(wert, titel=self.titel)
        return {self.ausgabe.id: wert.groesse}
