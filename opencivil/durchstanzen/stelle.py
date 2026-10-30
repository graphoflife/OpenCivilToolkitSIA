"""
opencivil/durchstanzen/stelle.py -- die Durchstanzstelle: Platte, gestützte Fläche, Bewehrung, Last.

VERANTWORTUNG:
Was einen Durchstanznachweis beschreibt, als Vorgaben im Rechenwerk
(:class:`Durchstanzstelle`), und die Wahlen dazu: Decke oder Bodenplatte
(:class:`Plattenart`), Form und Lage der gestützten Fläche
(:class:`Stuetzenform`, :class:`Lage`), die Näherungsstufe der
Plattenrotation (:class:`Naeherungsstufe`) und wie k_e bestimmt wird
(:class:`KeArt`). Aus ihren Massen baut sie die Kandidaten des
Nachweisschnitts (:meth:`Durchstanzstelle.kandidaten`).

DECKE UND BODENPLATTE:
Bei einer Decke liegt die Zugbewehrung über der Stütze oben, bei einer
Bodenplatte unten -- die Bodenpressung drückt sie von unten gegen die Stütze.
Gerechnet wird gleich; anders heisst nur, was an Flächenlast innerhalb des
Nachweisschnitts abgezogen wird (4.3.6.2.6): bei der Decke Eigengewicht und
Nutzlast, bei der Bodenplatte die Bodenpressung.

KOORDINATEN:
In der Ebene der Platte, in m. Eine Stütze steht mit ihrer Achse im
Ursprung; der Plattenrand einer Randstütze liegt unten (y negativ), bei der
Eckstütze liegt ein zweiter links (x negativ). Ein Wandende liegt im
Ursprung, die Wand läuft nach +x; eine Wandecke liegt mit ihrer äusseren
Ecke im Ursprung, die Wände laufen nach +x und +y, die Platte liegt aussen.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from opencivil.core.berechnung import Berechnung, Vorgabe
from opencivil.core.einheiten import KN, KN_PRO_M2, KNM_PRO_M, M, MM, Groesse
from opencivil.core.protokoll import Abschnitt
from opencivil.core.wahl import Wahl
from opencivil.core.wert import WertDef
from opencivil.durchstanzen.schnitt import (
    Halbebene, Kandidat, Punkt, Stuetzenflaeche, kandidat_wandecke, kandidat_wandende,
    kandidaten_stuetze,
)
from opencivil.material.basis import Baustoff
from opencivil.querschnitt.platte import Richtung


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


class Stuetzenform(Wahl):
    """
    Die Form einer Stütze im Grundriss. Die Ovalstütze ist ein Rechteck mit
    halbrunden Enden, b_x × b_y über alles -- so heisst sie in der Software von
    Leviat (DURA); der Name ist nicht aus der Norm.
    """

    RECHTECK = "rechteck"
    RUND = "rund"
    OVAL = "oval"

    @property
    def beschriftung(self) -> str:
        return {Stuetzenform.RECHTECK: "Rechteckstütze", Stuetzenform.RUND: "Rundstütze",
                Stuetzenform.OVAL: "Ovalstütze"}[self]


class Lage(Wahl):
    """Wo die gestützte Fläche in der Platte liegt."""

    INNEN = "innen"
    RAND = "rand"
    ECKE = "ecke"
    WANDENDE = "wandende"
    WANDECKE = "wandecke"

    @property
    def beschriftung(self) -> str:
        return {Lage.INNEN: "Innenstütze", Lage.RAND: "Randstütze", Lage.ECKE: "Eckstütze",
                Lage.WANDENDE: "Wandende", Lage.WANDECKE: "Wandecke"}[self]

    @property
    def wand(self) -> bool:
        return self in (Lage.WANDENDE, Lage.WANDECKE)

    @property
    def k_e(self) -> float:
        """
        Die Näherung für k_e nach SIA 262:2025, 4.3.6.2.5 -- für Innenstützen
        mit grossen Aussparungen in Stützennähe gilt 0.7 wie am Rand
        (:meth:`Durchstanzstelle.k_e_naeherung`).
        """
        return {Lage.INNEN: 0.9, Lage.RAND: 0.7, Lage.ECKE: 0.65,
                Lage.WANDENDE: 0.75, Lage.WANDECKE: 0.75}[self]


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


class KeArt(Wahl):
    """Woher k_e kommt: aus der Näherung (4.3.6.2.5) oder aus der Exzentrizität (57)."""

    NAEHERUNG = "naeherung"
    EXZENTRIZITAET = "exzentrizitaet"

    @property
    def beschriftung(self) -> str:
        return ("Näherung nach 4.3.6.2.5" if self is KeArt.NAEHERUNG
                else "aus der Exzentrizität, Gleichung (57)")


@dataclass
class Durchstanzstelle:
    """
    Platte, gestützte Fläche, Bewehrung und Einwirkung eines Durchstanznachweises
    -- als Vorgaben im Rechenwerk. Die Masse der gestützten Fläche, die für die
    Form und die Lage nicht gelten, gehen nicht ein: eine Rundstütze hat kein
    b_x, eine Innenstütze keinen Randabstand.
    """

    name: str
    praefix: str
    plattenart: Plattenart
    beton: Baustoff
    stahl: Baustoff
    """Der Stahl der Biegebewehrung."""

    h: Groesse
    c: Groesse
    """Die Überdeckung auf der Zugseite."""

    D_max: Groesse
    phi_x: Groesse
    s_x: Groesse
    phi_y: Groesse
    s_y: Groesse
    aussen: Richtung
    """Welche Lage der Zugbewehrung aussen liegt, näher am Rand."""

    form: Stuetzenform
    lage: Lage
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

    def __post_init__(self) -> None:
        self.id = self.praefix
        self.aussparungen = tuple(tuple(map(tuple, a)) for a in self.aussparungen)
        self._aufbauen()

    @property
    def abschnitt(self) -> Abschnitt:
        return Abschnitt(f"Durchstanzen: {self.name}", self.id, thema="Durchstanzen")

    def id_von(self, kurzname: str) -> str:
        return self.definitionen[kurzname].id

    def ins_rechenwerk(self, werk) -> "Durchstanzstelle":
        werk.definiere(*self.definitionen.values())
        werk.registriere(*self.berechnungen)
        return self

    def masse(self) -> Tuple[str, ...]:
        """Die Masse der gestützten Fläche, die für Form und Lage gelten."""
        if self.lage.wand:
            return ("t",)
        masse = ("D",) if self.form is Stuetzenform.RUND else ("b_x", "b_y")
        if self.lage is Lage.RAND:
            masse += ("a_y",)
        elif self.lage is Lage.ECKE:
            masse += ("a_x", "a_y")
        return masse

    def eingaben(self) -> Tuple[str, ...]:
        """Die Kurznamen, die der Nachweis liest."""
        namen = ("h", "c", "D_max", "phi_x", "s_x", "phi_y", "s_y", *self.masse(), "V_d", "q_d")
        if self.stufe is Naeherungsstufe.DREI:
            namen += ("r_sx", "r_sy", "m_sdx", "m_sdy")
        else:
            namen += ("l_x", "l_y")
        # Stufe 2 braucht e_u für die Momente im Stützstreifen -- nicht an
        # Wänden, dort rechnet sie wie Stufe 1 (siehe :mod:`.nachweis`).
        if self.ke is KeArt.EXZENTRIZITAET or (self.stufe is Naeherungsstufe.ZWEI
                                                and not self.lage.wand):
            namen += ("e_x", "e_y")
        return namen

    def _aufbauen(self) -> None:
        gruppen = [
            ("Platte", (
                ("h", "h", MM, "Plattendicke", 0, self.h),
                ("c", "c_{nom}", MM, f"Überdeckung der Zugbewehrung {self.plattenart.zugseite}",
                 0, self.c),
                ("D_max", "D_{max}", MM, "Grösstkorndurchmesser", 0, self.D_max),
            )),
            ("Biegebewehrung", (
                ("phi_x", r"\varnothing_x", MM, "Stabdurchmesser in x", 0, self.phi_x),
                ("s_x", "s_x", MM, "Stababstand in x", 0, self.s_x),
                ("phi_y", r"\varnothing_y", MM, "Stabdurchmesser in y", 0, self.phi_y),
                ("s_y", "s_y", MM, "Stababstand in y", 0, self.s_y),
            )),
            ("Gestützte Fläche", tuple(e for e in (
                ("b_x", "b_x", MM, "Abmessung der Stütze in x", 0, self.b_x),
                ("b_y", "b_y", MM, "Abmessung der Stütze in y", 0, self.b_y),
                ("D", "D", MM, "Durchmesser der Stütze", 0, self.D),
                ("t", "t", MM, "Dicke der Wand", 0, self.t),
                ("a_x", "a_x", MM, "Abstand vom Plattenrand in x", 0, self.a_x),
                ("a_y", "a_y", MM, "Abstand vom Plattenrand in y", 0, self.a_y),
            ) if e[0] in self.masse())),
            ("Plattenrotation", (
                ("r_sx", "r_{sx}", M, "Abstand zum Momentennullpunkt in x", 2, self.r_sx),
                ("r_sy", "r_{sy}", M, "Abstand zum Momentennullpunkt in y", 2, self.r_sy),
                ("m_sdx", "m_{sd,x}", KNM_PRO_M, "Mittleres Moment im Stützstreifen, x", 1,
                 self.m_sdx),
                ("m_sdy", "m_{sd,y}", KNM_PRO_M, "Mittleres Moment im Stützstreifen, y", 1,
                 self.m_sdy),
            ) if self.stufe is Naeherungsstufe.DREI else (
                ("l_x", "l_x", M, "Spannweite in x", 2, self.l_x),
                ("l_y", "l_y", M, "Spannweite in y", 2, self.l_y),
            )),
            ("Einwirkung", tuple(e for e in (
                ("V_d", "V_d", KN, "Bemessungswert der Auflagerkraft", 1, self.V_d),
                ("q_d", "q_d", KN_PRO_M2, f"Flächenlast im Nachweisschnitt: {self.plattenart.last}",
                 1, self.q_d),
                ("e_x", "e_x", MM, "Exzentrizität der Auflagerkraft in x", 0, self.e_x),
                ("e_y", "e_y", MM, "Exzentrizität der Auflagerkraft in y", 0, self.e_y),
            ) if e[0] in self.eingaben())),
        ]
        for gruppe, eintraege in gruppen:
            for kurz, symbol, einheit, beschreibung, stellen, groesse in eintraege:
                d = WertDef(id=f"{self.id}.{kurz}", symbol=symbol, einheit=einheit,
                            beschreibung=beschreibung, stellen=stellen)
                self.definitionen[kurz] = d
                self.berechnungen.append(Vorgabe(id=d.id, ausgabe=d, groesse=groesse,
                                                 abschnitt=self.abschnitt, gruppe=gruppe))

    # -- Geometrie ----------------------------------------------------------

    def stuetze(self, masse: Dict[str, float]) -> Stuetzenflaeche:
        """Die Stütze aus ihren Massen in m, mit der Achse im Ursprung."""
        if self.form is Stuetzenform.RUND:
            return Stuetzenflaeche(((0.0, 0.0),), masse["D"] / 2.0)
        bx, by = masse["b_x"] / 2.0, masse["b_y"] / 2.0
        if self.form is Stuetzenform.OVAL:
            # Die Strecke zwischen den Mitten der Halbkreise, mit dem halben
            # kürzeren Mass darum -- bei b_x = b_y ein Kreis.
            r = min(bx, by)
            kern = ((-(bx - r), -(by - r)), (bx - r, by - r))
            return Stuetzenflaeche(kern if kern[0] != kern[1] else ((0.0, 0.0),), r)
        return Stuetzenflaeche(((-bx, -by), (bx, -by), (bx, by), (-bx, by)))

    def raender(self, masse: Dict[str, float]) -> Tuple[Halbebene, ...]:
        """Die Plattenränder: unten am Rand, unten und links an der Ecke."""
        if self.lage not in (Lage.RAND, Lage.ECKE):
            return ()
        x0, y0, _, _ = self.stuetze(masse).grenzen()
        raender = [Halbebene((0.0, -1.0), -(y0 - masse["a_y"]))]
        if self.lage is Lage.ECKE:
            raender.append(Halbebene((-1.0, 0.0), -(x0 - masse["a_x"])))
        return tuple(raender)

    def achse(self, masse: Dict[str, float]) -> Punkt:
        """Die Achse der gestützten Fläche -- von ihr gehen die Strahlen an Aussparungen vorbei."""
        if self.lage is Lage.WANDENDE:
            return (masse["t"] / 2.0, 0.0)
        if self.lage is Lage.WANDECKE:
            return (masse["t"] / 2.0, masse["t"] / 2.0)
        return (0.0, 0.0)

    def kandidaten(self, masse: Dict[str, float], abstand: float, d_v: float) -> List[Kandidat]:
        """Die möglichen Nachweisschnitte im Abstand ``abstand`` -- siehe :mod:`.schnitt`."""
        if self.lage is Lage.WANDENDE:
            return [kandidat_wandende(masse["t"], abstand, d_v)]
        if self.lage is Lage.WANDECKE:
            return [kandidat_wandecke(masse["t"], abstand, d_v)]
        return kandidaten_stuetze(self.stuetze(masse), abstand, 1.5 * d_v, self.raender(masse))

    def umriss(self, masse: Dict[str, float], d_v: float) -> List[Punkt]:
        """
        Der Umriss der gestützten Fläche fürs Bild -- eine Wand 4·d_v weit, etwas
        über den Schnitt hinaus, der entlang der Wand 3.5·d_v weit reicht.
        """
        t, L = masse.get("t", 0.0), 4.0 * d_v
        if self.lage is Lage.WANDENDE:
            return [(0.0, -t / 2), (L, -t / 2), (L, t / 2), (0.0, t / 2)]
        if self.lage is Lage.WANDECKE:
            return [(0.0, 0.0), (L, 0.0), (L, t), (t, t), (t, L), (0.0, L)]
        return self.stuetze(masse).umriss()
