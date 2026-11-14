"""
opencivil/durchstanzen/stelle.py -- die Durchstanzstelle: Platte, gestützte Fläche, Bewehrung, Last.

VERANTWORTUNG:
Was einen Durchstanznachweis beschreibt, als Vorgaben im Rechenwerk
(:class:`Durchstanzstelle`), und die Wahlen dazu: Decke oder Bodenplatte
(:class:`Plattenart`), die Näherungsstufe der Plattenrotation
(:class:`Naeherungsstufe`) und wie k_e bestimmt wird (:class:`KeArt`). Was
Lage und Form der gestützten Fläche heissen, steht in :mod:`.flaeche`.
Welche Felder der Nachweis liest, sagt :func:`eingaben_fuer` -- dieselben Teile
bekommt die Maske über den Katalog, damit sie nichts davon nachbaut.

DER STAHL DER ANKER:
Die Durchstanzbewehrung hat ihren eigenen Stahl, den des Produkts
(:data:`.produkte.STAHL`): in (67) und (69) gilt dessen Fliessgrenze
(SIA 262:2025, 4.3.6.5.4). Er steht als Baustoff neben der Stelle, mit dem
Index «sw» an seinen Zeichen; alle Stellen teilen ihn. Bis 2026-11-14
rechneten die Anker mit dem Stahl der Biegebewehrung -- mit B700B um 40 %
zu günstig.

DECKE UND BODENPLATTE:
Bei einer Decke liegt die Zugbewehrung über der Stütze oben, bei einer
Bodenplatte unten -- die Bodenpressung drückt sie von unten gegen die Stütze.
Gerechnet wird gleich; anders heisst nur, was an Flächenlast innerhalb des
Nachweisschnitts abgezogen wird (4.3.6.2.6): bei der Decke Eigengewicht und
Nutzlast, bei der Bodenplatte die Bodenpressung.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from opencivil.core.berechnung import Berechnung, Vorgabe
from opencivil.core.einheiten import KN, KN_PRO_M2, KNM_PRO_M, M, MM, Groesse
from opencivil.core.protokoll import Abschnitt
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.wahl import Wahl
from opencivil.core.wert import WertDef
from opencivil.durchstanzen import produkte
from opencivil.durchstanzen.flaeche import GestuetzteFlaeche
from opencivil.durchstanzen.schnitt import Punkt
from opencivil.material.basis import Baustoff
from opencivil.material.betonstahl import betonstahl
from opencivil.querschnitt.platte import Richtung

#: Der Namensraum des Stahls der Anker -- einer für alle Stellen.
ANKERSTAHL = "produkt.ancoplus"

#: Was der Nachweis an jeder Stelle liest -- vor den Massen der gestützten Fläche und danach.
VOR_DEN_MASSEN = ("h", "c", "c_v", "D_max", "phi_x", "s_x", "phi_y", "s_y")
NACH_DEN_MASSEN = ("V_d", "q_d")


class Plattenart(Wahl):
    """Decke oder Bodenplatte -- siehe Dateikopf."""

    DECKE = "decke"
    BODENPLATTE = "bodenplatte"

    @property
    def beschriftung(self) -> str:
        return "Decke" if self is Plattenart.DECKE else "Bodenplatte"

    @property
    def last(self) -> str:
        """Was an Flächenlast im Nachweisschnitt abgezogen wird (4.3.6.2.6)."""
        return ("Eigengewicht und Nutzlast" if self is Plattenart.DECKE
                else "Bodenpressung")

    @property
    def zugseite(self) -> str:
        """Wo die Zugbewehrung über der gestützten Fläche liegt."""
        return "oben" if self is Plattenart.DECKE else "unten"

    @property
    def druckseite(self) -> str:
        """Die andere Seite -- von ihr aus misst c_v die Verankerung der Anker."""
        return "unten" if self is Plattenart.DECKE else "oben"


class Naeherungsstufe(Wahl):
    """Wie die Plattenrotation geschätzt wird (SIA 262:2025, 4.3.6.4.2)."""

    EINS = "1"
    ZWEI = "2"
    DREI = "3"

    @property
    def beschriftung(self) -> str:
        return f"Näherungsstufe {self.value}"

    @property
    def faktor(self) -> float:
        """Der Vorfaktor in Gleichung (60): 1.5, in Stufe 3 mit Momenten aus der Elastizitätstheorie 1.2."""
        return 1.2 if self is Naeherungsstufe.DREI else 1.5

    @property
    def eingaben(self) -> Tuple[str, ...]:
        """
        Was die Stufe liest: die Spannweiten, in Stufe 2 dazu die Exzentrizität
        für die Momente im Stützstreifen, in Stufe 3 statt beidem r_s und m_sd.
        """
        return {Naeherungsstufe.EINS: ("l_x", "l_y"),
                Naeherungsstufe.ZWEI: ("l_x", "l_y", "e_x", "e_y"),
                Naeherungsstufe.DREI: ("r_sx", "r_sy", "m_sdx", "m_sdy")}[self]


class KeArt(Wahl):
    """Woher k_e kommt: aus der Näherung (4.3.6.2.5) oder aus der Exzentrizität (57)."""

    NAEHERUNG = "naeherung"
    EXZENTRIZITAET = "exzentrizitaet"

    @property
    def beschriftung(self) -> str:
        return ("Näherung nach 4.3.6.2.5" if self is KeArt.NAEHERUNG
                else "aus der Exzentrizität, Gleichung (57)")

    @property
    def eingaben(self) -> Tuple[str, ...]:
        return ("e_x", "e_y") if self is KeArt.EXZENTRIZITAET else ()


def wirksame_stufe(flaeche: GestuetzteFlaeche, stufe: Naeherungsstufe) -> Naeherungsstufe:
    """
    Die Stufe, mit der gerechnet wird: Stufe 2 braucht die Momente im
    Stützstreifen -- wo 4.3.6.4.7 keine nennt, an Wänden, rechnet sie wie
    Stufe 1.
    """
    return Naeherungsstufe.EINS if stufe is Naeherungsstufe.ZWEI and not flaeche.momente else stufe


def eingaben_fuer(flaeche: GestuetzteFlaeche, stufe: Naeherungsstufe, ke: KeArt) -> Tuple[str, ...]:
    """
    Die Kurznamen, die der Nachweis liest: die Masse der gestützten Fläche,
    was die wirksame Stufe liest und was k_e liest -- je ohne Doppel.
    """
    return tuple(dict.fromkeys((*VOR_DEN_MASSEN, *flaeche.masse, *NACH_DEN_MASSEN,
                                *wirksame_stufe(flaeche, stufe).eingaben, *ke.eingaben)))


@dataclass
class Durchstanzstelle(Rechenobjekt):
    """
    Platte, gestützte Fläche, Bewehrung und Einwirkung eines Durchstanznachweises
    -- als Vorgaben im Rechenwerk. Die Masse der gestützten Fläche, die für die
    Form und die Lage nicht gelten, gehen nicht ein: eine Rundstütze hat kein
    b_x, eine Innenstütze keinen Randabstand.
    """

    WAS = "Durchstanzstelle"

    name: str
    praefix: str
    plattenart: Plattenart
    beton: Baustoff
    stahl: Baustoff
    """Der Stahl der Biegebewehrung."""

    h: Groesse
    c: Groesse
    """Die Überdeckung auf der Zugseite."""

    c_v: Groesse
    """
    Der Abstand der Verankerung der Durchstanzbewehrung von der Oberfläche
    der Druckseite (SIA 262:2025, Figur 26) -- bei ancoPLUS bis zu den Köpfen.
    """

    D_max: Groesse
    phi_x: Groesse
    s_x: Groesse
    phi_y: Groesse
    s_y: Groesse
    aussen: Richtung
    """Welche Lage der Zugbewehrung aussen liegt, näher am Rand."""

    flaeche: GestuetzteFlaeche
    b_x: Groesse
    b_y: Groesse
    D: Groesse
    t: Groesse
    """Die Dicke der Wand -- an Wandende und Wandecke."""

    a_x: Groesse
    """Der Abstand der Stütze vom linken Plattenrand -- nur an der Ecke."""

    a_y: Groesse
    """Der Abstand der Stütze vom unteren Plattenrand -- am Rand und an der Ecke."""

    l_x: Groesse
    l_y: Groesse
    stufe: Naeherungsstufe
    r_sx: Groesse
    r_sy: Groesse
    m_sdx: Groesse
    m_sdy: Groesse
    """``r_s`` und ``m_sd`` von Hand -- nur in Näherungsstufe 3."""

    V_d: Groesse
    q_d: Groesse
    """Die Flächenlast, die im Nachweisschnitt abgezogen wird (4.3.6.2.6)."""

    ke: KeArt
    e_x: Groesse
    e_y: Groesse
    """Die Exzentrizität der Auflagerkraft gegenüber der Stützenachse."""

    aussparungen: Sequence[Sequence[Punkt]] = ()
    """Je Aussparung ihre Ecken, in m."""

    definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)
    berechnungen: List[Berechnung] = field(default_factory=list, init=False)
    anker: Baustoff = field(init=False)
    """Der Stahl der Durchstanzbewehrung -- siehe Dateikopf."""

    def __post_init__(self) -> None:
        self.id = self.praefix
        self.aussparungen = tuple(tuple(map(tuple, a)) for a in self.aussparungen)
        self.anker = betonstahl(produkte.STAHL, name=f"ancoPLUS, {produkte.STAHL}",
                                praefix=ANKERSTAHL, symbol_index="sw")
        self._aufbauen()

    @property
    def baustoffe(self) -> Tuple[Baustoff, ...]:
        """Der Stahl der Anker -- Beton und Biegebewehrung meldet das Projekt an."""
        return (self.anker,)

    @property
    def abschnitt(self) -> Abschnitt:
        return Abschnitt(f"Durchstanzen: {self.name}", self.id, thema="Durchstanzen")

    def eingaben(self) -> Tuple[str, ...]:
        """Die Kurznamen, die der Nachweis liest -- siehe :func:`eingaben_fuer`."""
        return eingaben_fuer(self.flaeche, self.stufe, self.ke)

    def _aufbauen(self) -> None:
        gelesen = self.eingaben()
        gruppen = [
            ("Platte", (
                ("h", "h", MM, "Plattendicke", 0, self.h),
                ("c", "c_{nom}", MM, f"Überdeckung der Zugbewehrung {self.plattenart.zugseite}",
                 0, self.c),
                ("c_v", "c_v", MM, "Abstand der Verankerung der Durchstanzbewehrung von der "
                 f"Druckseite, {self.plattenart.druckseite}", 0, self.c_v),
                ("D_max", "D_{max}", MM, "Grösstkorndurchmesser", 0, self.D_max),
            )),
            ("Biegebewehrung", (
                ("phi_x", r"\varnothing_x", MM, "Stabdurchmesser in x", 0, self.phi_x),
                ("s_x", "s_x", MM, "Stababstand in x", 0, self.s_x),
                ("phi_y", r"\varnothing_y", MM, "Stabdurchmesser in y", 0, self.phi_y),
                ("s_y", "s_y", MM, "Stababstand in y", 0, self.s_y),
            )),
            ("Gestützte Fläche", (
                ("b_x", "b_x", MM, "Abmessung der Stütze in x", 0, self.b_x),
                ("b_y", "b_y", MM, "Abmessung der Stütze in y", 0, self.b_y),
                ("D", "D", MM, "Durchmesser der Stütze", 0, self.D),
                ("t", "t", MM, "Dicke der Wand", 0, self.t),
                ("a_x", "a_x", MM, "Abstand vom Plattenrand in x", 0, self.a_x),
                ("a_y", "a_y", MM, "Abstand vom Plattenrand in y", 0, self.a_y),
            )),
            ("Plattenrotation", (
                ("r_sx", "r_{sx}", M, "Abstand zum Momentennullpunkt in x", 2, self.r_sx),
                ("r_sy", "r_{sy}", M, "Abstand zum Momentennullpunkt in y", 2, self.r_sy),
                ("m_sdx", "m_{sd,x}", KNM_PRO_M, "Mittleres Moment im Stützstreifen, x", 1,
                 self.m_sdx),
                ("m_sdy", "m_{sd,y}", KNM_PRO_M, "Mittleres Moment im Stützstreifen, y", 1,
                 self.m_sdy),
                ("l_x", "l_x", M, "Spannweite in x", 2, self.l_x),
                ("l_y", "l_y", M, "Spannweite in y", 2, self.l_y),
            )),
            ("Einwirkung", (
                ("V_d", "V_d", KN, "Bemessungswert der Auflagerkraft", 1, self.V_d),
                ("q_d", "q_d", KN_PRO_M2, f"Flächenlast im Nachweisschnitt: {self.plattenart.last}",
                 1, self.q_d),
                ("e_x", "e_x", MM, "Exzentrizität der Auflagerkraft in x", 0, self.e_x),
                ("e_y", "e_y", MM, "Exzentrizität der Auflagerkraft in y", 0, self.e_y),
            )),
        ]
        for gruppe, eintraege in gruppen:
            for kurz, symbol, einheit, beschreibung, stellen, groesse in eintraege:
                if kurz not in gelesen:
                    continue
                d = WertDef(id=f"{self.id}.{kurz}", symbol=symbol, einheit=einheit,
                            beschreibung=beschreibung, stellen=stellen)
                self.definitionen[kurz] = d
                self.berechnungen.append(Vorgabe(id=d.id, ausgabe=d, groesse=groesse,
                                                 abschnitt=self.abschnitt, gruppe=gruppe))
