"""
opencivil/pfahl/pfahl.py -- ein Einzelpfahl in seinem Baugrund.

VERANTWORTUNG:
Der :class:`Pfahl`: Art, Masse und Querschnitt, die Schichten des Baugrunds,
das Grundwasser und die Beiwerte des Widerstands -- als Vorgaben im
Rechenwerk, und nur die, die nach den Wahlen gelten (:meth:`Pfahl.kurznamen`):

* :class:`Pfahlart` -- Bohrpfahl aus Stahlbeton oder Mikropfahl mit einem
  Tragglied aus Stahl (:class:`Tragglied`) in einem Verpresskörper;
* :class:`Grundlage` -- worauf der äussere Widerstand R_a,k beruht: auf einer
  Berechnung aus den Schichten, auf Erfahrung oder auf einem Versuch, und
  wie gross der Umrechnungsfaktor η_a darum höchstens ist;
* :class:`Spitze` und :class:`Abscheren` -- ob der Fuss trägt und wie;
* :class:`Kopf` -- ob sich der Kopf frei drehen kann oder eingespannt ist.

Gerechnet wird in den Nachweisen: äusserer Widerstand in
:mod:`opencivil.pfahl.aussen`, innerer in :mod:`opencivil.pfahl.innen`, der
äussere quer zur Achse in :mod:`opencivil.pfahl.quer` -- und die Steifigkeit
in :mod:`opencivil.pfahl.steifigkeit`. Welche Kombination den Pfahl quer
belastet, sagt :meth:`Pfahl.quer_belastet`.

TIEFEN:
z zählt ab Oberkante Terrain nach unten. Der Kopf liegt in der Tiefe t_K,
der Fuss in t_K + L. Über dem Kopf trägt der Boden nur als Auflast.

DER DURCHMESSER:
Beim Bohrpfahl der des Pfahls -- verrohrt aussen an der Verrohrung,
unverrohrt der des Bohrwerkzeugs (SIA 267:2013, 9.5.2.4.7); beim
Mikropfahl der des Verpresskörpers, an dem Mantel und Fuss tragen. Das
Tragglied hat seine eigenen Masse.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Berechnung, Eingaben, Vorgabe
from opencivil.core.einheiten import (
    EINHEITSLOS, GRAD, KN, KN_PRO_M3, KNM, KPA, M, MM, MN_PRO_M2, Groesse,
)
from opencivil.core.protokoll import Abschnitt
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.wahl import Wahl
from opencivil.core.wert import WertDef, kennung_aus
from opencivil.material.basis import Baustoff
from opencivil.pfahl import buch
from opencivil.pfahl.boden import Pfahlschicht, Profil

#: Wie gross der Umrechnungsfaktor des inneren Widerstands höchstens ist --
#: nur mit verlässlicher Prüfung der Integrität (SIA 267:2013, 9.5.2.4.9).
ETA_I_HOECHSTENS = 0.9

#: Ohne diese Prüfung, in der Regel (SIA 267:2013, 9.5.2.4.4, (51)).
ETA_I_REGEL = 0.8


class Pfahlart(Wahl):
    """Was für ein Pfahl -- daran hängen sein Querschnitt und was der Durchmesser meint."""

    BOHRPFAHL = "bohrpfahl"
    MIKROPFAHL = "mikropfahl"

    @property
    def beschriftung(self) -> str:
        return {Pfahlart.BOHRPFAHL: "Bohrpfahl",
                Pfahlart.MIKROPFAHL: "Mikropfahl"}[self]

    @property
    def erklaerung(self) -> str:
        return {Pfahlart.BOHRPFAHL: "Bohrpfahl aus Stahlbeton, längs bewehrt",
                Pfahlart.MIKROPFAHL: "Mikropfahl: ein Tragglied aus Stahl im "
                                     "Verpresskörper"}[self]


class Grundlage(Wahl):
    """
    Worauf der charakteristische äussere Widerstand R_a,k beruht -- und
    darum, wie gross der Umrechnungsfaktor η_a höchstens ist
    (SIA 267:2013, 9.5.2.2.5). Aus einer Berechnung oder aus Erfahrung kommt
    R_a,k aus den Schichten, aus einem Versuch wird er eingegeben.
    """

    BERECHNUNG = "berechnung"
    ERFAHRUNG = "erfahrung"
    DYNAMISCH = "dynamisch"
    STATISCH = "statisch"

    @property
    def beschriftung(self) -> str:
        return {Grundlage.BERECHNUNG: "Berechnung",
                Grundlage.ERFAHRUNG: "vergleichbare Erfahrung",
                Grundlage.DYNAMISCH: "dynamischer Versuch",
                Grundlage.STATISCH: "statischer Versuch"}[self]

    @property
    def erklaerung(self) -> str:
        return {Grundlage.BERECHNUNG: "R_a,k aus den Schichten gerechnet",
                Grundlage.ERFAHRUNG: "R_a,k aus den Schichten, die Werte durch vergleichbare "
                                     "Erfahrung belegt",
                Grundlage.DYNAMISCH: "R_a,k eingegeben: der kleinste Wert der dynamischen "
                                     "Versuche",
                Grundlage.STATISCH: "R_a,k eingegeben: der kleinste Wert der statischen "
                                    "Versuche"}[self]

    @property
    def eta_grenze(self) -> float:
        """Der Grenzwert von η_a."""
        return {Grundlage.BERECHNUNG: 0.7, Grundlage.ERFAHRUNG: 0.9,
                Grundlage.DYNAMISCH: 0.9, Grundlage.STATISCH: 1.0}[self]

    @property
    def referenz(self) -> str:
        """Wo der Grenzwert steht."""
        gleichung = {Grundlage.BERECHNUNG: 48, Grundlage.ERFAHRUNG: 46,
                     Grundlage.DYNAMISCH: 47, Grundlage.STATISCH: 45}[self]
        return f"SIA 267:2013, 9.5.2.2.5, ({gleichung})"

    @property
    def aus_versuch(self) -> bool:
        """Ob R_a,k eingegeben wird, statt aus den Schichten zu folgen."""
        return self in (Grundlage.DYNAMISCH, Grundlage.STATISCH)


class Spitze(Wahl):
    """Ob und wie der Fuss trägt."""

    RECHNEN = "rechnen"
    EINGEBEN = "eingeben"
    KEINE = "keine"

    @property
    def beschriftung(self) -> str:
        return {Spitze.RECHNEN: "gerechnet", Spitze.EINGEBEN: "eingegeben",
                Spitze.KEINE: "trägt nicht"}[self]

    @property
    def erklaerung(self) -> str:
        return {Spitze.RECHNEN: "q_b,k aus der Schicht am Fuss (Kap. 12.5)",
                Spitze.EINGEBEN: "q_b,k eingegeben, etwa aus dem geotechnischen Bericht",
                Spitze.KEINE: "Der Fuss trägt nicht, nur der Mantel"}[self]


class Abscheren(Wahl):
    """
    Wie der Boden am Fuss bricht, drainiert. Das Buch empfiehlt, die
    Tragfähigkeitsfaktoren für örtliches Abscheren zu nehmen, mit 2/3 von φ
    und c: der volle Spitzendruck stellte sich erst bei grossen Setzungen ein
    (Kap. 9.2.7, 12.5).
    """

    OERTLICH = "oertlich"
    ALLGEMEIN = "allgemein"

    @property
    def beschriftung(self) -> str:
        return {Abscheren.OERTLICH: "örtlich", Abscheren.ALLGEMEIN: "allgemein"}[self]

    @property
    def erklaerung(self) -> str:
        return {Abscheren.OERTLICH: "Örtliches Abscheren: 2/3 von φ'_k und c'_k "
                                    "(Kap. 9.2.7, 12.5)",
                Abscheren.ALLGEMEIN: "Allgemeines Abscheren: φ'_k und c'_k"}[self]


class Tragglied(Wahl):
    """Was im Mikropfahl trägt: ein Stahlrohr oder ein Vollstab."""

    ROHR = "rohr"
    STAB = "stab"

    @property
    def beschriftung(self) -> str:
        return {Tragglied.ROHR: "Rohr", Tragglied.STAB: "Vollstab"}[self]

    @property
    def erklaerung(self) -> str:
        return {Tragglied.ROHR: "Ein Stahlrohr; der Mörtel darin zählt nicht",
                Tragglied.STAB: "Ein voller Stab aus Stahl"}[self]


class Kopf(Wahl):
    """Wie der Pfahlkopf gehalten ist -- daran hängt, was eine Querkraft mit ihm macht."""

    FREI = "frei"
    EINGESPANNT = "eingespannt"

    @property
    def beschriftung(self) -> str:
        return {Kopf.FREI: "frei drehbar", Kopf.EINGESPANNT: "eingespannt"}[self]

    @property
    def erklaerung(self) -> str:
        return {Kopf.FREI: "Der Kopf dreht sich frei; ein Moment am Kopf ist eine Einwirkung",
                Kopf.EINGESPANNT: "Der Kopf dreht sich nicht, etwa in einer steifen "
                                  "Pfahlkopfplatte; das Moment dort ist die Reaktion"}[self]


def quer_belastet(H: float, M: float, kopf: Kopf) -> bool:
    """
    Ob Kräfte am Kopf den Pfahl quer belasten: eine Querkraft, oder ein Moment
    am frei drehbaren Kopf -- am eingespannten ist das Moment Reaktion.
    """
    return H != 0.0 or (M != 0.0 and kopf is Kopf.FREI)


@dataclass(frozen=True)
class Kombination:
    """
    Eine Einwirkung auf den Pfahlkopf: die Normalkraft, Druck positiv, die
    Querkraft und das Moment -- das Moment dreht wie die Querkraft, wenn sie
    über dem Kopf angreift.
    """

    name: str
    N_Ed: Groesse
    H_Ed: Groesse = field(default_factory=lambda: Groesse(0.0, KN))
    M_Ed: Groesse = field(default_factory=lambda: Groesse(0.0, KNM))

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


# ===========================================================================
# Der Pfahl
# ===========================================================================


@dataclass
class Pfahl(Rechenobjekt):
    """Siehe Dateikopf."""

    WAS = "Pfahl"

    name: str
    praefix: str
    art: Pfahlart
    D: Groesse
    L: Groesse
    t_K: Groesse
    """Die Tiefe des Pfahlkopfs unter Terrain."""

    t_w: Groesse
    """Die Tiefe des höchsten Grundwasserspiegels unter Terrain."""

    gamma_w: Groesse
    schichten: Sequence[Pfahlschicht]
    grundlage: Grundlage
    eta_a: Groesse
    R_ak: Groesse
    R_ak_zug: Groesse
    """R_a,k aus einem Versuch, auf Druck und auf Zug -- nur dann."""

    spitze: Spitze
    abscheren: Abscheren
    q_b: Groesse
    """Der Spitzendruck, charakteristisch -- eingegeben."""

    eta_i: Groesse
    stahl: Baustoff
    """Die Längsbewehrung des Bohrpfahls, das Tragglied des Mikropfahls."""

    beton: Optional[Baustoff]
    """Der Beton des Bohrpfahls -- beim Mikropfahl trägt nur der Stahl."""

    n: Groesse
    phi_l: Groesse
    c: Groesse
    phi_w: Groesse
    """Bohrpfahl: Zahl und Durchmesser der Längsstäbe, Überdeckung, Durchmesser der Wendel."""

    tragglied: Tragglied
    d_a: Groesse
    t_r: Groesse
    dt: Groesse
    """Mikropfahl: Aussendurchmesser und Wanddicke des Tragglieds, Abrostung aussen."""

    kopf: Kopf
    t_red: Groesse
    """Bis in diese Tiefe unter Terrain wächst die Bettung quer von null an."""

    eta_tr: Groesse
    """Der Umrechnungsfaktor des äusseren Widerstands quer zur Achse."""

    definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)
    berechnungen: List[Berechnung] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.id = self.praefix
        self._aufbauen()

    @property
    def abschnitt(self) -> Abschnitt:
        """Ueberschrift, unter der der Pfahl in der Herleitung steht."""
        return Abschnitt(f"Pfahl: {self.name}", self.id, thema="Pfahl")

    @property
    def bohrpfahl(self) -> bool:
        return self.art is Pfahlart.BOHRPFAHL

    def quer_belastet(self, k: Kombination) -> bool:
        """Ob eine Kombination den Pfahl quer belastet (:func:`quer_belastet`)."""
        return quer_belastet(k.H_Ed.si, k.M_Ed.si, self.kopf)

    @property
    def fuss_traegt(self) -> bool:
        """
        Ob der Fuss trägt: nach der Wahl «Fuss» -- mit R_a,k aus einem Versuch
        immer, der Versuch hat den ganzen Pfahl belastet.
        """
        return self.grundlage.aus_versuch or self.spitze is not Spitze.KEINE

    @property
    def baustoffe(self) -> Tuple[Baustoff, ...]:
        """Keine eigenen -- Beton und Stahl meldet das Projekt an."""
        return ()

    @property
    def stoffe(self) -> Tuple[Baustoff, ...]:
        """Die Baustoffe des Querschnitts: Beton und Stahl beim Bohrpfahl, Stahl beim Mikropfahl."""
        if self.bohrpfahl:
            assert self.beton is not None, "Ein Bohrpfahl braucht einen Beton."
            return (self.beton, self.stahl)
        return (self.stahl,)

    def profil(self, e: Eingaben) -> Profil:
        """Die Schichten und das Wasser als Zahlen, aus den Eingaben eines Nachweises."""
        n = range(1, len(self.schichten) + 1)
        return Profil([e.g(f"d_{i}").si for i in n], [e.g(f"gamma_{i}").si for i in n],
                      e.g("t_w").si, e.g("gamma_w").si)

    # -- Die Vorgaben -------------------------------------------------------

    def _gruppen(self) -> List[Tuple[str, Tuple[tuple, ...]]]:
        """
        Je Kasten der Herleitung seine Vorgaben: Kurzname, Symbol, Einheit,
        Beschreibung, Stellen, Grösse, Referenz -- nur, was nach den Wahlen gilt.
        """
        mikro = not self.bohrpfahl
        pfahl = (
            ("D", "D", MM,
             "Durchmesser des Verpresskörpers" if mikro else "Durchmesser des Pfahls", 0, self.D,
             "" if mikro else "SIA 267:2013, 9.5.2.4.7"),
            ("L", "L", M, "Länge des Pfahls", 2, self.L, ""),
            ("t_K", "t_K", M, "Tiefe des Pfahlkopfs unter Terrain", 2, self.t_K, ""),
        )
        wasser = (
            ("t_w", "t_w", M, "Tiefe des höchsten Grundwasserspiegels unter Terrain", 2,
             self.t_w, "SIA 267:2013, 4.2.2.3"),
            ("gamma_w", r"\gamma_w", KN_PRO_M3, "Raumlast des Wassers", 1, self.gamma_w, ""),
        )
        aussen = [("eta_a", r"\eta_a", EINHEITSLOS, "Umrechnungsfaktor des äusseren Widerstands",
                   2, self.eta_a, self.grundlage.referenz)]
        if self.grundlage.aus_versuch:
            aussen += [
                ("R_ak", "R_{a,k}", KN, "Äusserer Widerstand auf Druck, aus dem Versuch", 0,
                 self.R_ak, "SIA 267:2013, 9.4.4.1.3, 9.4.4.1.6"),
                ("R_ak_zug", "R_{a,k,Z}", KN, "Äusserer Widerstand auf Zug, aus dem Versuch", 0,
                 self.R_ak_zug, "SIA 267:2013, 9.4.4.1.3, 9.4.4.1.6"),
            ]
        elif self.spitze is Spitze.EINGEBEN:
            aussen.append(("q_b", "q_{b,k}", KPA, "Spitzendruck, charakteristisch", 0, self.q_b,
                           ""))
        if self.bohrpfahl:
            querschnitt = (
                ("n", "n", EINHEITSLOS, "Zahl der Längsstäbe", 0, self.n, ""),
                ("phi_l", r"\varnothing_l", MM, "Durchmesser der Längsstäbe", 0, self.phi_l, ""),
                ("c", "c", MM, "Überdeckung der Wendel", 0, self.c, ""),
                ("phi_w", r"\varnothing_w", MM, "Durchmesser der Wendel", 0, self.phi_w, ""),
            )
        elif self.tragglied is Tragglied.ROHR:
            querschnitt = (
                ("d_a", "d_a", MM, "Aussendurchmesser des Rohrs", 1, self.d_a, ""),
                ("t_r", "t", MM, "Wanddicke des Rohrs", 1, self.t_r, ""),
                ("dt", r"\Delta t", MM, "Abrostung aussen", 1, self.dt, "SIA 267:2013, 9.6.1.5.2"),
            )
        else:
            querschnitt = (
                ("d_a", r"\varnothing", MM, "Durchmesser des Stabs", 1, self.d_a, ""),
                ("dt", r"\Delta t", MM, "Abrostung aussen", 1, self.dt, "SIA 267:2013, 9.6.1.5.2"),
            )
        querschnitt += (("eta_i", r"\eta_i", EINHEITSLOS,
                         "Umrechnungsfaktor des inneren Widerstands", 2, self.eta_i,
                         "SIA 267:2013, 9.5.2.4.4, (51); 9.5.2.4.9"),)
        querlast = (
            ("t_red", "t_{red}", M,
             "Tiefe unter Terrain, bis zu der die Bettung quer von null an wächst", 2,
             self.t_red, "SIA 267:2013, 9.5.4.5"),
            ("eta_tr", r"\eta_{a,tr}", EINHEITSLOS,
             "Umrechnungsfaktor des äusseren Widerstands quer", 2, self.eta_tr,
             "SIA 267:2013, 9.5.2.3.2; 9.5.2.2.5, (48)"),
        )
        gruppen = [("Pfahl", pfahl), ("Grundwasser", wasser),
                   ("Äusserer Widerstand", tuple(aussen)), ("Querschnitt", querschnitt),
                   ("Querlast", querlast)]
        for i, s in enumerate(self.schichten, start=1):
            gruppen.append((f"Schicht {i}: {s.name}", tuple(
                self._schichtwert(i, s, kurz) for kurz in s.kurznamen())))
        return gruppen

    @staticmethod
    def _schichtwert(i: int, s: Pfahlschicht, kurz: str) -> tuple:
        """Eine Zahl der Schicht i als Vorgabe; «#» in der Beschreibung steht für die Schicht."""
        symbol, einheit, beschreibung, stellen, referenz = {
            "d": (f"d_{{{i}}}", M, "Dicke der #", 2, ""),
            "gamma": (rf"\gamma_{{{i}}}", KN_PRO_M3, "Raumlast der #", 1, ""),
            "phi_k": (rf"\varphi'_{{k,{i}}}", GRAD, "Reibungswinkel der #, charakteristisch", 1,
                      ""),
            "c_k": (f"c'_{{k,{i}}}", KPA, "Kohäsion der #, charakteristisch", 1, ""),
            "s_u": (f"s_{{u,k,{i}}}", KPA,
                    "Undrainierte Scherfestigkeit der #, charakteristisch", 1, ""),
            "q_s": (f"q_{{s,k,{i}}}", KPA, "Mantelreibung in der #, charakteristisch", 1, ""),
            "K": (f"K_{{{i}}}", EINHEITSLOS, "Erddruckbeiwert am Mantel in der #", 2,
                  buch.KAP_MANTEL),
            "delta_faktor": (rf"k_{{\delta,{i}}}", EINHEITSLOS,
                             "Reibungswinkel Pfahl–Boden in der #, als Teil von φ'_k", 2,
                             buch.KAP_MANTEL),
            "alpha": (rf"\alpha_{{{i}}}", EINHEITSLOS,
                      "Adhäsion in der #, als Teil von s_u,k", 2, buch.KAP_MANTEL),
            "E_s": (f"E_{{s,k,{i}}}", MN_PRO_M2, "Verformungsmodul der #, charakteristisch", 0,
                    ""),
        }[kurz]
        return (f"{kurz}_{i}", symbol, einheit, beschreibung.replace("#", f"Schicht {i}"),
                stellen, getattr(s, kurz), referenz)

    def _aufbauen(self) -> None:
        for gruppe, eintraege in self._gruppen():
            for kurz, symbol, einheit, beschreibung, stellen, groesse, referenz in eintraege:
                d = WertDef(id=f"{self.id}.{kurz}", symbol=symbol, einheit=einheit,
                            beschreibung=beschreibung, referenz=referenz, stellen=stellen)
                self.definitionen[kurz] = d
                self.berechnungen.append(Vorgabe(id=d.id, ausgabe=d, groesse=groesse,
                                                 abschnitt=self.abschnitt, gruppe=gruppe))

    def kurznamen(self, *gruppen: str) -> List[str]:
        """
        Die Kurznamen der Vorgaben, die gelten -- aus den genannten Kästen, ohne
        Angabe aus allen. Die Schichten heissen zusammen «Schicht».
        """
        heraus = []
        for gruppe, eintraege in self._gruppen():
            name = "Schicht" if gruppe.startswith("Schicht ") else gruppe
            if not gruppen or name in gruppen:
                heraus += [e[0] for e in eintraege]
        return heraus
