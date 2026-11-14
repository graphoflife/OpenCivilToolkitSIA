"""
opencivil/projekt/pfahl.py -- ein Einzelpfahl, wie die Oberflaeche ihn beschreibt.

VERANTWORTUNG:
Der :class:`PfahlEintrag`: Art und Masse des Pfahls, sein Querschnitt, die
Schichten des Baugrunds, das Grundwasser, worauf der äussere Widerstand
beruht, wie der Kopf gehalten ist, und die Kräfte am Kopf -- als
speicherbare Datenklasse. Gerechnet wird in :mod:`opencivil.pfahl`.

DIE VORGABEN:
Gesetzt, damit sich gleich etwas rechnen lässt, aus keiner Quelle: ein
Bohrpfahl mit D = 900 mm und L = 10 m, der Kopf 1 m unter Terrain, das
Grundwasser am Terrain, auf der sicheren Seite wie beim Grundbruch; zwölf
Stäbe ⌀ 20 mit einer Wendel ⌀ 10 und 75 mm Überdeckung, dem grössten Wert
von SIA 267:2013, 9.6.3.2.6. Eine Schicht, 20 m Kies mit φ'_k = 30° und
K = 0.5, etwa K_0 = 1 − sin φ'_k (Kap. 2.7), und δ = φ'_k, wie das Buch
für raue Pfähle sagt (Kap. 12.5); undrainiert α = 0.6, sein Wert für
Bohrpfähle in weichem Ton. η_a = 0.7 und η_i = 0.8 sind die Grenzwerte der
Norm für eine Berechnung und ohne Prüfung der Integrität. Der Mikropfahl
hat ein Rohr 114.3 × 10 mm ohne Abrostung, bis jemand eine angibt. Der
Verformungsmodul E_s,k = 30 MN/m² ist der des Beispiels im Buch zu Cassans
Federn (Kap. 12.8); der Kopf dreht sich frei, und die Bettung quer wächst
bis 2 m unter Terrain von null an.

Die Namen der Schichten müssen nicht verschieden sein, wie bei der Setzung:
die Werte tragen die Nummer der Schicht.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, List

from opencivil.core.einheiten import GRAD, KN, KN_PRO_M3, KNM, KPA, M, MM, MN_PRO_M2
from opencivil.pfahl.boden import Mantel, Verhalten
from opencivil.pfahl.pfahl import (
    ETA_I_HOECHSTENS, Abscheren, Grundlage, Kopf, Pfahlart, Spitze, Tragglied,
)
from opencivil.projekt.eintraege import BauteilEintrag, Beschreibung, eindeutig
from opencivil.projekt.lesen import ProjektFehler, bereich, lesen


@dataclass
class PfahlschichtEintrag(Beschreibung):
    """Eine Schicht des Baugrunds, vom Terrain an nach unten -- siehe :class:`~opencivil.pfahl.boden.Pfahlschicht`."""

    name: str
    d: float = bereich(20.0, heisst="Dicke d", einheit=M, ueber=0.0)
    gamma: float = bereich(20.0, heisst="Raumlast γ", einheit=KN_PRO_M3, ueber=0.0)
    verhalten: Verhalten = Verhalten.DRAINIERT
    phi_k: float = bereich(30.0, heisst="φ'_k", einheit=GRAD, ab=0.0, unter=90.0)
    c_k: float = bereich(0.0, heisst="c'_k", einheit=KPA, ab=0.0)
    s_u: float = bereich(50.0, heisst="s_u,k", einheit=KPA, ab=0.0)
    mantel: Mantel = Mantel.RECHNEN
    q_s: float = bereich(50.0, heisst="q_s,k", einheit=KPA, ab=0.0)
    K: float = bereich(0.5, heisst="K", ab=0.0)
    delta_faktor: float = bereich(1.0, heisst="δ/φ'_k", ab=0.0, bis=1.0)
    """
    Höchstens eins: zwischen Pfahl und Boden reibt es nie stärker als im Boden
    -- nach Vorgabe, nicht nachgeschlagen.
    """

    alpha: float = bereich(0.6, heisst="α", ab=0.0, bis=1.0)
    """
    Höchstens eins: die Adhäsion erreicht höchstens die Scherfestigkeit -- nach
    Vorgabe, nicht nachgeschlagen.
    """

    E_s: float = bereich(30.0, heisst="Verformungsmodul E_s,k", einheit=MN_PRO_M2, ueber=0.0)


@dataclass
class PfahlkombinationEintrag(Beschreibung):
    """
    Eine Einwirkung auf den Pfahlkopf: die Normalkraft in kN, Druck positiv,
    die Querkraft in kN und das Moment in kNm -- siehe
    :class:`~opencivil.pfahl.pfahl.Kombination`.
    """

    name: str
    N_Ed: float = bereich(1000.0, heisst="Normalkraft N_Ed, Druck positiv", einheit=KN)
    H_Ed: float = bereich(0.0, heisst="Querkraft H_Ed", einheit=KN)
    M_Ed: float = bereich(0.0, heisst="Moment M_Ed", einheit=KNM)
    aktiv: bool = True
    """Ob die Kombination gerechnet wird. Ausgeschaltet bleibt sie stehen."""


@dataclass
class PfahlEintrag(BauteilEintrag):
    """Ein Einzelpfahl in seinem Baugrund, mit seinen Einwirkungen -- siehe Dateikopf."""

    BEZEICHNUNG = "Pfahl"

    kennung: str
    name: str

    art: Pfahlart = Pfahlart.BOHRPFAHL
    beton: str = ""
    """Kennung des Betons -- nur beim Bohrpfahl."""

    stahl: str = ""
    """Kennung des Stahls: die Längsbewehrung des Bohrpfahls, das Tragglied des Mikropfahls."""

    D: float = bereich(900.0, heisst="Durchmesser D", einheit=MM, ueber=0.0)
    L: float = bereich(10.0, heisst="Länge L", einheit=M, ueber=0.0)
    t_K: float = bereich(1.0, heisst="Tiefe des Kopfs t_K", einheit=M, ab=0.0)
    t_w: float = bereich(0.0, heisst="Tiefe des Grundwassers t_w", einheit=M, ab=0.0)
    gamma_w: float = bereich(10.0, heisst="γ_w", einheit=KN_PRO_M3, ab=0.0)

    grundlage: Grundlage = Grundlage.BERECHNUNG
    eta_a: float = bereich(0.7, heisst="η_a", ueber=0.0, bis=1.0)
    """Höchstens der Grenzwert der Grundlage -- das prüft :meth:`regeln`."""

    R_ak: float = bereich(1000.0, heisst="R_a,k auf Druck", einheit=KN, ab=0.0)
    R_ak_zug: float = bereich(500.0, heisst="R_a,k auf Zug", einheit=KN, ab=0.0)
    spitze: Spitze = Spitze.RECHNEN
    abscheren: Abscheren = Abscheren.OERTLICH
    q_b: float = bereich(2000.0, heisst="q_b,k", einheit=KPA, ab=0.0)

    eta_i: float = bereich(0.8, heisst="η_i", ueber=0.0, bis=ETA_I_HOECHSTENS)
    n: int = bereich(12, heisst="Zahl der Stäbe n", ab=1)
    phi_l: float = bereich(20.0, heisst="⌀ der Stäbe", einheit=MM, ueber=0.0)
    c: float = bereich(75.0, heisst="Überdeckung c", einheit=MM, ab=0.0)
    phi_w: float = bereich(10.0, heisst="⌀ der Wendel", einheit=MM, ab=0.0)
    tragglied: Tragglied = Tragglied.ROHR
    d_a: float = bereich(114.3, heisst="Aussendurchmesser d_a", einheit=MM, ueber=0.0)
    t_r: float = bereich(10.0, heisst="Wanddicke t", einheit=MM, ueber=0.0)
    dt: float = bereich(0.0, heisst="Abrostung Δt", einheit=MM, ab=0.0)

    kopf: Kopf = Kopf.FREI
    t_red: float = bereich(2.0, heisst="Tiefe der Abminderung t_red", einheit=M, ab=0.0)

    beschreibung: str = ""
    """Freier Text -- geht in keine Rechnung ein."""

    schichten: List[PfahlschichtEintrag] = field(default_factory=list)
    """Vom Terrain an nach unten."""

    kombinationen: List[PfahlkombinationEintrag] = field(default_factory=list)

    @classmethod
    def neu(cls, kennung: str, name: str) -> "PfahlEintrag":
        """Ein frischer Pfahl, wie die Oberflaeche ihn anlegt: mit einer Schicht und einer Kombination."""
        return cls(kennung=kennung, name=name,
                   schichten=[PfahlschichtEintrag(name="Kies")],
                   kombinationen=[PfahlkombinationEintrag(name="Kombination 1")])

    def materialien(self) -> List[str]:
        """Die Materialien, die der Pfahl braucht: der Beton nur beim Bohrpfahl."""
        return [k for k in ((self.beton if self.bohrpfahl else ""), self.stahl) if k]

    @property
    def bohrpfahl(self) -> bool:
        return self.art is Pfahlart.BOHRPFAHL

    def schicht(self, name: str, **felder: Any) -> PfahlschichtEintrag:
        """
        Eine Schicht unten anfügen -- Dicke in m, Raumlast in kN/m³, Winkel in
        Grad, Spannungen in kPa, den Verformungsmodul in MN/m²; ``verhalten``
        und ``mantel`` als Wort, wie in der Datei: ``verhalten="undrainiert"``.
        """
        eintrag = lesen(PfahlschichtEintrag, {"name": name, **felder}, f"Schicht '{name}'")
        self.schichten.append(eintrag)
        return eintrag

    def kombination(self, name: str, *, N_Ed: float, H_Ed: float = 0.0,
                    M_Ed: float = 0.0) -> PfahlkombinationEintrag:
        """Eine Kombination anfügen -- N_Ed und H_Ed in kN, Druck positiv, M_Ed in kNm."""
        eintrag = PfahlkombinationEintrag(name=name, N_Ed=N_Ed, H_Ed=H_Ed, M_Ed=M_Ed)
        self.kombinationen.append(eintrag)
        return eintrag

    @property
    def boden_unter_dem_fuss(self) -> bool:
        """Ob die Schichten tiefer reichen als der Fuss -- nur dann trägt ihn Boden."""
        return self.t_K + self.L < sum(s.d for s in self.schichten)

    def regeln(self, wo: str) -> None:
        """
        Hält auf, was mehrere Felder zusammen unmöglich machen, bevor daraus
        ein Widerstand wird. Wie beim Grundbruch vor dem Rechnen und nicht
        beim Öffnen: eine Datei mit einem zu kurzen Baugrund soll sich öffnen
        und korrigieren lassen.
        """
        eindeutig((k.name for k in self.kombinationen), wo, "Kombination")
        if self.eta_a > self.grundlage.eta_grenze:
            raise ProjektFehler(
                f"{wo}: η_a = {self.eta_a:g} liegt über {self.grundlage.eta_grenze:g}, dem "
                f"Grenzwert für «{self.grundlage.beschriftung}» ({self.grundlage.referenz}).")
        if not self.grundlage.aus_versuch:
            self._baugrund(wo)
        if self.bohrpfahl:
            self._bewehrung(wo)
        else:
            self._tragglied(wo)

    def _baugrund(self, wo: str) -> None:
        """Was die Rechnung aus den Schichten braucht."""
        if not self.schichten:
            raise ProjektFehler(f"{wo}: ohne Schicht lässt sich R_a,k nicht rechnen -- "
                                f"eine Schicht anlegen oder R_a,k aus einem Versuch eingeben.")
        for i, s in enumerate(self.schichten, start=1):
            if s.gamma <= self.gamma_w:
                raise ProjektFehler(
                    f"{wo}, Schicht {i}: die Raumlast γ = {s.gamma:g} kN/m³ muss grösser sein "
                    f"als die des Wassers, γ_w = {self.gamma_w:g} kN/m³ -- sonst ist γ' nicht "
                    f"positiv.")
            if s.verhalten is Verhalten.DRAINIERT and s.phi_k <= 0.0:
                raise ProjektFehler(f"{wo}, Schicht {i}: drainiert braucht φ'_k über null; "
                                    f"ohne Reibung die Schicht undrainiert rechnen.")
            if s.verhalten is Verhalten.UNDRAINIERT and s.s_u <= 0.0:
                raise ProjektFehler(f"{wo}, Schicht {i}: undrainiert braucht s_u,k über null.")
        if not self.boden_unter_dem_fuss:
            raise ProjektFehler(
                f"{wo}: der Fuss liegt in {self.t_K + self.L:g} m, die Schichten reichen bis "
                f"{sum(s.d for s in self.schichten):g} m. Unter dem Fuss muss noch Boden "
                f"sein, der ihn trägt.")

    def _bewehrung(self, wo: str) -> None:
        """Die Längsstäbe müssen im Kreis Platz haben, ohne sich zu berühren."""
        r_s = self.D / 2.0 - self.c - self.phi_w - self.phi_l / 2.0
        if r_s <= 0.0:
            raise ProjektFehler(
                f"{wo}: die Stäbe haben keinen Platz -- D/2 = {self.D / 2.0:g} mm reicht nicht "
                f"für Überdeckung, Wendel und den halben Stab.")
        if self.n >= 2 and 2.0 * r_s * math.sin(math.pi / self.n) <= self.phi_l:
            raise ProjektFehler(
                f"{wo}: {self.n} Stäbe ⌀ {self.phi_l:g} berühren sich auf dem Kreis mit "
                f"r_s = {r_s:g} mm.")

    def _tragglied(self, wo: str) -> None:
        """Das Tragglied muss nach der Abrostung noch Stahl haben und im Verpresskörper liegen."""
        if self.d_a >= self.D:
            raise ProjektFehler(
                f"{wo}: das Tragglied, d_a = {self.d_a:g} mm, muss im Verpresskörper liegen, "
                f"D = {self.D:g} mm.")
        if self.tragglied is Tragglied.ROHR:
            if 2.0 * self.t_r >= self.d_a:
                raise ProjektFehler(f"{wo}: die Wand t = {self.t_r:g} mm ist zu dick für ein Rohr "
                                    f"mit d_a = {self.d_a:g} mm.")
            if self.dt >= self.t_r:
                raise ProjektFehler(f"{wo}: die Abrostung Δt = {self.dt:g} mm frisst die ganze "
                                    f"Wand t = {self.t_r:g} mm.")
        elif 2.0 * self.dt >= self.d_a:
            raise ProjektFehler(f"{wo}: die Abrostung Δt = {self.dt:g} mm frisst den ganzen Stab "
                                f"⌀ {self.d_a:g} mm.")
