"""
opencivil/projekt/grundbruch.py -- ein Grundbruchnachweis, wie die Oberflaeche ihn beschreibt.

VERANTWORTUNG:
Der :class:`GrundbruchEintrag`: Boden, Fundament, Gelaende und Grundwasser
als Zahlen, dazu die Einwirkungskombinationen -- als speicherbare
Datenklasse. Gerechnet wird in :mod:`opencivil.geotechnik.grundbruch`.

Die Vorgaben der Felder hat der Benutzer genannt (2026-10-16): phi_k = 30°,
gamma_phi = 1.2, c = 0, gamma_c = 1.5, gamma = 21 und gamma_w = 10 kN/m³,
b = L = 1 m, t = t_1 = 0, N_Ed = 1000 kN, T_Ed = 200 kN, alpha = beta = 0.
delta*/phi = 1 ist dazugekommen, damit sich T_Rd rechnen laesst: das Kapitel
nennt fuer delta* «2/3 phi bis 1 · phi».
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from opencivil.projekt.eintraege import Beschreibung, eindeutig
from opencivil.projekt.lesen import ProjektFehler


@dataclass
class GrundbruchkombinationEintrag(Beschreibung):
    """Eine Einwirkung auf das Fundament: N normal zur Sohle, T in ihrer Richtung, in kN."""

    name: str
    N_Ed: float = 1000.0
    T_Ed: float = 200.0
    aktiv: bool = True
    """Ob die Kombination gerechnet wird. Ausgeschaltet bleibt sie stehen."""


@dataclass
class GrundbruchEintrag(Beschreibung):
    """Ein Flachfundament auf seinem Baugrund, mit seinen Einwirkungen."""

    BEZEICHNUNG = "Grundbruch"

    kennung: str
    name: str

    phi_k: float = 30.0
    """Reibungswinkel, charakteristisch, in Grad."""

    gamma_phi: float = 1.2
    """Partialfaktor des Reibungswinkels -- SIA 267:2013, 5.3.2.2."""

    c_k: float = 0.0
    """Kohäsion, charakteristisch, in kPa -- mit phi = 0 die undrainierte Scherfestigkeit."""

    gamma_c: float = 1.5
    """Partialfaktor der Kohäsion."""

    gamma: float = 21.0
    """Raumlast des Bodens in kN/m³."""

    gamma_w: float = 10.0
    """Raumlast des Wassers in kN/m³."""

    q_Ed: float = 0.0
    """Bemessungslast neben dem Fundament in kPa."""

    b: float = 1.0
    """Breite des Fundaments in m -- die kürzere Seite."""

    L: float = 1.0
    """Länge des Fundaments in m."""

    t1: float = 0.0
    """Tiefe des höchsten möglichen Grundwasserspiegels unter Terrain, in m."""

    t: float = 0.0
    """Tiefe der Fundamentsohle unter Terrain, in m."""

    alpha: float = 0.0
    """Neigung der Sohle in Grad, positiv gegen T ansteigend (Bild 9.2.15)."""

    beta: float = 0.0
    """Neigung des Geländes in Grad, positiv vom Fundament weg abfallend."""

    delta_faktor: float = 1.0
    """Sohlreibungswinkel im Verhältnis zum Reibungswinkel, delta*/phi."""

    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    kombinationen: List[GrundbruchkombinationEintrag] = field(default_factory=list)

    @classmethod
    def neu(cls, kennung: str, name: str) -> "GrundbruchEintrag":
        """Ein frischer Grundbruch, wie die Oberflaeche ihn anlegt: mit einer Kombination."""
        return cls(kennung=kennung, name=name,
                   kombinationen=[GrundbruchkombinationEintrag(name="Kombination 1")])

    def materialien(self) -> List[str]:
        """Die Materialien, auf die das Fundament zeigt -- keine: der Boden steht im Eintrag."""
        return []

    def bezuege(self) -> List[str]:
        """Die Bauteile, deren Querschnitt das Fundament nimmt -- keine."""
        return []

    def kombination(self, name: str, *, N_Ed: float, T_Ed: float = 0.0
                    ) -> GrundbruchkombinationEintrag:
        """Eine Kombination anfügen -- N normal zur Sohle, T in ihrer Richtung, in kN."""
        eintrag = GrundbruchkombinationEintrag(name=name, N_Ed=N_Ed, T_Ed=T_Ed)
        self.kombinationen.append(eintrag)
        return eintrag

    def regeln(self, wo: str) -> None:
        """
        Haelt unmoegliche Zahlen und Namen auf, bevor daraus ein Widerstand
        wird -- vor dem Rechnen und nicht beim Oeffnen: eine abgelegte Datei
        mit b = 0 oder zwei gleich benannten Kombinationen soll sich oeffnen
        und korrigieren lassen.
        """
        eindeutig((k.name for k in self.kombinationen), wo, "Kombination")
        for feld, wert, wie in (
                ("Breite b", self.b, self.b > 0.0),
                ("Partialfaktor γ_φ", self.gamma_phi, self.gamma_phi > 0.0),
                ("Partialfaktor γ_c", self.gamma_c, self.gamma_c > 0.0),
                ("δ*/φ", self.delta_faktor, self.delta_faktor > 0.0)):
            if not wie:
                raise ProjektFehler(f"{wo}: {feld} muss grösser als null sein, "
                                    f"angegeben ist {wert:g}.")
        for feld, wert in (("Tiefe t", self.t), ("Tiefe t_1", self.t1),
                           ("Kohäsion c", self.c_k), ("Auflast q_Ed", self.q_Ed),
                           ("γ_w", self.gamma_w)):
            if wert < 0.0:
                raise ProjektFehler(f"{wo}: {feld} kann nicht negativ sein ({wert:g}).")
        if self.L < self.b:
            raise ProjektFehler(
                f"{wo}: b ist die kürzere Seite des Fundaments -- die Länge L = {self.L:g} m "
                f"muss mindestens so gross sein wie die Breite b = {self.b:g} m.")
        if self.gamma <= self.gamma_w:
            raise ProjektFehler(
                f"{wo}: die Raumlast des Bodens γ = {self.gamma:g} kN/m³ muss grösser sein "
                f"als die des Wassers, γ_w = {self.gamma_w:g} kN/m³ -- sonst ist γ' nicht "
                f"positiv.")
        for feld, wert in (("φ_k", self.phi_k), ("α", self.alpha), ("β", self.beta)):
            if not 0.0 <= wert < 90.0:
                raise ProjektFehler(f"{wo}: {feld} muss zwischen 0° und 90° liegen, "
                                    f"angegeben sind {wert:g}°.")
        if self.phi_k == 0.0 and self.c_k <= 0.0:
            raise ProjektFehler(
                f"{wo}: mit φ = 0 trägt nur die Kohäsion (undrainiert, c = s_u) -- sie muss "
                f"grösser als null sein.")
        for k in self.kombinationen:
            if k.N_Ed <= 0.0:
                raise ProjektFehler(
                    f"{wo}, Kombination '{k.name}': N_Ed muss eine Druckkraft sein, "
                    f"grösser als null, angegeben sind {k.N_Ed:g} kN.")
            if k.T_Ed < 0.0:
                raise ProjektFehler(
                    f"{wo}, Kombination '{k.name}': T_Ed zeigt in die Richtung von "
                    f"Bild 9.2.15 und ist nicht negativ, angegeben sind {k.T_Ed:g} kN.")
