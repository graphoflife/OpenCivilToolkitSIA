"""
opencivil/projekt/grundbruch.py -- ein Grundbruchnachweis, wie die Oberflaeche ihn beschreibt.

VERANTWORTUNG:
Der :class:`GrundbruchEintrag`: Boden, Fundament, Gelaende und Grundwasser
als Zahlen, dazu die Einwirkungskombinationen -- als speicherbare
Datenklasse. Gerechnet wird in :mod:`opencivil.geotechnik.fundament` und den
Nachweisen :mod:`~opencivil.geotechnik.grundbruch` und
:mod:`~opencivil.geotechnik.gleiten`.

Die Vorgaben der Felder hat der Benutzer genannt (2026-10-16): phi_k = 30°,
gamma_phi = 1.2, c = 0, gamma_c = 1.5, gamma = 21 und gamma_w = 10 kN/m³,
b = L = 1 m, t = t_1 = 0, N_Ed = 1000 kN, T_Ed = 200 kN, alpha = beta = 0.
delta_k/phi_k = 1 ist dazugekommen, damit sich T_Rd rechnen laesst: SIA
267:2013, 8.4.1.1, nennt 1 fuer eine raue Sohle mit dem Bruch im Boden und
1/2 bis 2/3 fuer eine glatte mit dem Bruch in der Fuge; das Buch etwa 2/3
bis 1 (Kap. 9.2.18).

Am 2026-11-19 der Schalter drainiert/undrainiert, wie beim Pfahl (Benutzer):
undrainiert mit s_u = 50 kPa, der Vorgabe des Pfahls, und gamma_cu = 1.5
nach SIA 267:2013, 5.3.2.2, Tabelle 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from opencivil.core.einheiten import GRAD, KN, KN_PRO_M3, KPA, M
from opencivil.geotechnik.verhalten import Verhalten
from opencivil.projekt.eintraege import BauteilEintrag, Beschreibung
from opencivil.projekt.fallnamen import Fallnamen
from opencivil.projekt.lesen import ProjektFehler, bereich


@dataclass
class GrundbruchkombinationEintrag(Beschreibung):
    """Eine Einwirkung auf das Fundament: N normal zur Sohle, T in ihrer Richtung, in kN."""

    name: str
    N_Ed: float = bereich(1000.0, heisst="Druckkraft N_Ed", einheit=KN, ueber=0.0)
    T_Ed: float = bereich(200.0, heisst="T_Ed, in Richtung von Bild 9.2.15,", einheit=KN,
                          ab=0.0)
    aktiv: bool = True
    """Ob die Kombination gerechnet wird. Ausgeschaltet bleibt sie stehen."""


@dataclass
class GrundbruchEintrag(BauteilEintrag):
    """Ein Flachfundament auf seinem Baugrund, mit seinen Einwirkungen."""

    BEZEICHNUNG = "Grundbruch"

    kennung: str
    name: str

    verhalten: Verhalten = Verhalten.DRAINIERT
    """
    Womit der Boden trägt: drainiert mit phi_k und c_k, undrainiert mit
    s_u -- derselbe Schalter wie beim Pfahl (Benutzer, 2026-11-19). Bis
    dahin hiess phi = 0 undrainiert, und c galt dann als s_u.
    """

    phi_k: float = bereich(30.0, heisst="φ_k", einheit=GRAD, ab=0.0, unter=90.0)
    """Reibungswinkel, charakteristisch, in Grad -- drainiert."""

    gamma_phi: float = bereich(1.2, heisst="Partialfaktor γ_φ", ueber=0.0)
    """Partialfaktor des Reibungswinkels -- SIA 267:2013, 5.3.2.2."""

    c_k: float = bereich(0.0, heisst="Kohäsion c", einheit=KPA, ab=0.0)
    """
    Kohäsion, charakteristisch, in kPa -- drainiert, und nur, wo sie
    dauerhaft wirkt (SIA 267:2013, 8.5.1.6).
    """

    gamma_c: float = bereich(1.5, heisst="Partialfaktor γ_c", ueber=0.0)
    """Partialfaktor der Kohäsion."""

    s_u: float = bereich(50.0, heisst="s_u,k", einheit=KPA, ab=0.0)
    """Undrainierte Scherfestigkeit, charakteristisch, in kPa -- undrainiert."""

    gamma_cu: float = bereich(1.5, heisst="Partialfaktor γ_cu", ueber=0.0)
    """
    Partialfaktor der undrainierten Scherfestigkeit -- SIA 267:2013, 5.3.2.2,
    Tabelle 1. Bis 2026-11-19 galt dafür gamma_c, mit demselben Wert.
    """

    gamma: float = bereich(21.0, heisst="Raumlast γ", einheit=KN_PRO_M3, ueber=0.0)
    """
    Raumlast des Bodens in kN/m³, über und unter dem Wasser dieselbe: unter
    ihm zählt gamma - gamma_w. Das Buch nimmt dort die gesättigte Raumlast
    (Kap. 1.4); mit der feuchten wird gamma' etwas kleiner, auf der sicheren
    Seite.
    """

    gamma_w: float = bereich(10.0, heisst="γ_w", einheit=KN_PRO_M3, ab=0.0)
    """
    Raumlast des Wassers in kN/m³ -- nur drainiert, fuer gamma': undrainiert
    gelten totale Spannungen, das Wasser wirkt dort nicht.
    """

    q_Ed: float = bereich(0.0, heisst="Auflast q_Ed", einheit=KPA, ab=0.0)
    """
    Auflast neben dem Fundament in kPa. Sie zählt nur, wenn sie dauernd und
    auf beiden Seiten mindestens über L_Gl liegt (Kap. 9.2.5); sie wirkt
    günstig.
    """

    b: float = bereich(1.0, heisst="Breite b", einheit=M, ueber=0.0)
    """Breite des Fundaments in m -- die kürzere Seite."""

    L: float = bereich(1.0, heisst="Länge L", einheit=M, ueber=0.0)
    """Länge des Fundaments in m."""

    t1: float = bereich(0.0, heisst="Tiefe t_1", einheit=M, ab=0.0)
    """Tiefe des höchsten möglichen Grundwasserspiegels unter Terrain, in m."""

    t: float = bereich(0.0, heisst="Tiefe t", einheit=M, ab=0.0)
    """Tiefe der Fundamentsohle unter Terrain, in m."""

    alpha: float = bereich(0.0, heisst="α", einheit=GRAD, ab=0.0, unter=90.0)
    """Neigung der Sohle in Grad, positiv gegen T ansteigend (Bild 9.2.15)."""

    beta: float = bereich(0.0, heisst="β", einheit=GRAD, ab=0.0, unter=90.0)
    """Neigung des Geländes in Grad, positiv vom Fundament weg abfallend."""

    delta_faktor: float = bereich(1.0, heisst="δ_k/φ_k", ueber=0.0)
    """
    Sohlreibungswinkel im Verhältnis zum Reibungswinkel, delta_k/phi_k
    (SIA 267:2013, 8.4.1.1).
    """

    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    kombinationen: List[GrundbruchkombinationEintrag] = field(default_factory=list)

    @classmethod
    def neu(cls, kennung: str, name: str) -> "GrundbruchEintrag":
        """Ein frischer Grundbruch, wie die Oberflaeche ihn anlegt: mit einer Kombination."""
        return cls(kennung=kennung, name=name,
                   kombinationen=[GrundbruchkombinationEintrag(name="Kombination 1")])

    def kombination(self, name: str, *, N_Ed: float, T_Ed: float = 0.0
                    ) -> GrundbruchkombinationEintrag:
        """Eine Kombination anfügen -- N normal zur Sohle, T in ihrer Richtung, in kN."""
        eintrag = GrundbruchkombinationEintrag(name=name, N_Ed=N_Ed, T_Ed=T_Ed)
        self.kombinationen.append(eintrag)
        return eintrag

    def fallnamen(self) -> List[Fallnamen]:
        """Die Namen der Kombinationen muessen sich unterscheiden."""
        return [Fallnamen.aus("kombinationen", "Kombination", self.kombinationen)]

    def regeln(self, wo: str) -> None:
        """
        Haelt unmoegliche Zahlen und Namen auf, bevor daraus ein Widerstand
        wird -- was mehrere Felder zusammen betrifft; wo jede Zahl fuer sich
        liegt, steht an ihrem Feld. Vor dem Rechnen und nicht beim Oeffnen:
        eine abgelegte Datei mit b = 0 oder zwei gleich benannten
        Kombinationen soll sich oeffnen und korrigieren lassen.
        """
        if self.L < self.b:
            raise ProjektFehler(
                f"b ist die kürzere Seite des Fundaments – die Länge L = {self.L:g} m "
                f"muss mindestens so gross sein wie die Breite b = {self.b:g} m.", wo=wo)
        # Nur drainiert: undrainiert gibt es kein gamma', und gamma_w ist ausgeblendet.
        if self.verhalten is Verhalten.DRAINIERT and self.gamma <= self.gamma_w:
            raise ProjektFehler(
                f"die Raumlast des Bodens γ = {self.gamma:g} kN/m³ muss grösser sein "
                f"als die des Wassers, γ_w = {self.gamma_w:g} kN/m³ – sonst ist γ' nicht "
                f"positiv.", wo=wo)
        # Wie beim Pfahl, je Schicht (``PfahlEintrag._festigkeiten``).
        if self.verhalten is Verhalten.DRAINIERT and self.phi_k <= 0.0:
            raise ProjektFehler(f"drainiert braucht φ_k über null; ohne Reibung "
                                f"undrainiert rechnen, mit s_u,k.", wo=wo)
        if self.verhalten is Verhalten.UNDRAINIERT and self.s_u <= 0.0:
            raise ProjektFehler("undrainiert braucht s_u,k über null.", wo=wo)
