"""
opencivil/pfahl/boden.py -- der Baugrund um einen Pfahl.

VERANTWORTUNG:
Die Schichten des Baugrunds, wie der Pfahl sie braucht (:class:`Pfahlschicht`):
Dicke, Raumlast, das Verhalten -- drainiert mit φ'_k und c'_k, undrainiert
mit s_u,k (:class:`Verhalten`) --, woher die Mantelreibung kommt: gerechnet
oder eingegeben (:class:`Mantel`), und der Verformungsmodul, auf dem der
Pfahl gebettet ist. Dazu als Zahlen die Spannungen
im Boden und die Stücke des Mantels, über die die Mantelreibung summiert
wird (:class:`Profil`).

TIEFEN UND WASSER:
z zählt ab Oberkante Terrain nach unten, in m; die Schichten liegen vom
Terrain an untereinander. Unter dem Grundwasserspiegel t_w steht das
Porenwasser unter u = γ_w · (z − t_w), und es zählt die wirksame Spannung
σ'_v = σ_v − u -- mit einer Raumlast γ je Schicht über und unter dem
Wasser, darunter also γ − γ_w, wie beim Grundbruch.

DIE STÜCKE DES MANTELS:
Je Schicht der Teil des Pfahls, der in ihr steckt, am Grundwasserspiegel
noch einmal geteilt: innerhalb eines Stücks ändert sich σ'_v linear, der Wert
in seiner Mitte ist also sein Mittel, und die Summe über die Stücke das
Integral der Mantelreibung. Das Buch rechnet mit der Spannung auf halber
Einbindetiefe (Kap. 12.5) -- dasselbe, solange kein Wasserspiegel das Stück
teilt.

EINHEITEN:
Die Schichten als Grössen; das Profil in SI-Basis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from opencivil.core.einheiten import Groesse
from opencivil.core.wahl import Wahl


class Verhalten(Wahl):
    """Womit eine Schicht trägt: drainiert mit φ'_k und c'_k, undrainiert mit s_u,k."""

    DRAINIERT = "drainiert"
    UNDRAINIERT = "undrainiert"

    @property
    def beschriftung(self) -> str:
        return {Verhalten.DRAINIERT: "drainiert", Verhalten.UNDRAINIERT: "undrainiert"}[self]

    @property
    def erklaerung(self) -> str:
        return {Verhalten.DRAINIERT: "Wirksame Spannungen, mit φ'_k und c'_k",
                Verhalten.UNDRAINIERT: "Totale Spannungen, mit s_u,k"}[self]


class Mantel(Wahl):
    """Woher die Mantelreibung einer Schicht kommt."""

    RECHNEN = "rechnen"
    EINGEBEN = "eingeben"

    @property
    def beschriftung(self) -> str:
        return {Mantel.RECHNEN: "gerechnet", Mantel.EINGEBEN: "eingegeben"}[self]

    @property
    def erklaerung(self) -> str:
        return {Mantel.RECHNEN: "q_s,k = K · σ'_v · tan δ oder α · s_u,k (Kap. 12.5)",
                Mantel.EINGEBEN: "q_s,k eingegeben, etwa aus dem geotechnischen Bericht"}[self]


@dataclass(frozen=True)
class Pfahlschicht:
    """
    Eine Schicht des Baugrunds, vom Terrain an nach unten gezählt. Welche
    ihrer Zahlen gelten, hängt an Verhalten und Mantel (:meth:`kurznamen`);
    die übrigen stehen da und gehen nicht ein.
    """

    name: str
    d: Groesse
    """Die Dicke der Schicht."""

    gamma: Groesse
    """Die Raumlast, über und unter dem Wasser dieselbe."""

    verhalten: Verhalten
    phi_k: Groesse
    """Der Reibungswinkel, charakteristisch -- drainiert."""

    c_k: Groesse
    """Die Kohäsion, charakteristisch -- drainiert; sie zählt am Fuss und im Erdwiderstand quer."""

    s_u: Groesse
    """Die undrainierte Scherfestigkeit, charakteristisch -- undrainiert."""

    mantel: Mantel
    q_s: Groesse
    """Die Mantelreibung, charakteristisch -- eingegeben."""

    K: Groesse
    """Der Erddruckbeiwert am Mantel -- gerechnet, drainiert."""

    delta_faktor: Groesse
    """Der Reibungswinkel zwischen Pfahl und Boden im Verhältnis zu φ'_k -- gerechnet, drainiert."""

    alpha: Groesse
    """Die Adhäsion im Verhältnis zu s_u,k -- gerechnet, undrainiert."""

    E_s: Groesse
    """Der Verformungsmodul, charakteristisch: woraus die Bettung des Pfahls folgt."""

    @property
    def drainiert(self) -> bool:
        return self.verhalten is Verhalten.DRAINIERT

    def kurznamen(self) -> Tuple[str, ...]:
        """
        Die Zahlen, die gelten: Dicke und Raumlast, die Festigkeit, die
        Mantelreibung, der Verformungsmodul.
        """
        namen = ["d", "gamma", *(("phi_k", "c_k") if self.drainiert else ("s_u",))]
        if self.mantel is Mantel.EINGEBEN:
            namen.append("q_s")
        else:
            namen += ["K", "delta_faktor"] if self.drainiert else ["alpha"]
        return (*namen, "E_s")


@dataclass(frozen=True)
class Stueck:
    """Ein Stück des Mantels in einer Schicht, auf einer Seite des Wassers -- z in m."""

    schicht: int
    """Die Schicht, in der es liegt: ihr Platz in der Liste, ab null."""

    z_o: float
    z_u: float

    @property
    def h(self) -> float:
        return self.z_u - self.z_o

    @property
    def mitte(self) -> float:
        return 0.5 * (self.z_o + self.z_u)


class Profil:
    """
    Die Schichten als Zahlen: ihre Grenzen, Raumlasten und das Wasser, in
    SI-Basis -- woraus die Spannungen in jeder Tiefe folgen.
    """

    def __init__(self, dicken: Sequence[float], raumlasten: Sequence[float], t_w: float,
                 gamma_w: float) -> None:
        self.grenzen: List[Tuple[float, float]] = []
        oben = 0.0
        for d in dicken:
            self.grenzen.append((oben, oben + d))
            oben += d
        self.raumlasten = tuple(raumlasten)
        self.t_w = t_w
        self.gamma_w = gamma_w

    @property
    def tiefe(self) -> float:
        """Wie tief die unterste Schicht reicht."""
        return self.grenzen[-1][1] if self.grenzen else 0.0

    def schicht_bei(self, z: float) -> int:
        """
        Die Schicht, in der die Tiefe z liegt -- an einer Grenze die untere:
        ein Fuss auf der Grenze steht auf ihr.
        """
        for i, (_, unten) in enumerate(self.grenzen):
            if z < unten:
                return i
        raise ValueError(f"z = {z:g} m liegt unter der untersten Schicht.")

    def sigma_v(self, z: float) -> float:
        """Die totale Spannung aus dem Gewicht des Bodens darüber."""
        summe = 0.0
        for (oben, unten), gamma in zip(self.grenzen, self.raumlasten):
            if z <= oben:
                break
            summe += gamma * (min(z, unten) - oben)
        return summe

    def u(self, z: float) -> float:
        """Der Porenwasserdruck unter dem Grundwasserspiegel."""
        return self.gamma_w * max(0.0, z - self.t_w)

    def sigma_v_wirksam(self, z: float) -> float:
        return self.sigma_v(z) - self.u(z)

    def stuecke(self, oben: float, unten: float) -> List[Stueck]:
        """Der Mantel von ``oben`` bis ``unten`` in Stücken, je Schicht und Seite des Wassers."""
        stuecke = []
        for i, (z_o, z_u) in enumerate(self.grenzen):
            a, b = max(z_o, oben), min(z_u, unten)
            if b <= a:
                continue
            if a < self.t_w < b:
                stuecke += [Stueck(i, a, self.t_w), Stueck(i, self.t_w, b)]
            else:
                stuecke.append(Stueck(i, a, b))
        return stuecke
