"""
opencivil/pfahl/pfahl.py -- ein Einzelpfahl in seinem Baugrund.

VERANTWORTUNG:
Der :class:`Pfahl`: Art, Masse und Querschnitt, die Schichten des Baugrunds,
das Grundwasser und die Beiwerte des Widerstands -- als Vorgaben im
Rechenwerk, und nur die, die nach den Wahlen gelten (:data:`VORGABEN`,
:data:`JE_SCHICHT`):

* :class:`Pfahlart` -- Bohrpfahl aus Stahlbeton oder Mikropfahl mit einem
  Tragglied aus Stahl (:class:`Tragglied`) in einem Verpresskörper;
* :class:`Grundlage` -- worauf der äussere Widerstand R_a,k beruht: auf einer
  Berechnung aus den Schichten, auf Erfahrung oder auf einem Versuch, und
  wie gross der Umrechnungsfaktor η_a darum höchstens ist;
* :class:`Umrechnung` -- ob η_a dieser Grenzwert ist oder von Hand kommt;
* :class:`Spitze` und :class:`Abscheren` -- ob der Fuss trägt und wie;
* :class:`Kopf` -- ob sich der Kopf frei drehen kann oder eingespannt ist.

Gerechnet wird in den Nachweisen: äusserer Widerstand in
:mod:`opencivil.pfahl.aussen`, innerer in :mod:`opencivil.pfahl.innen`, der
äussere quer zur Achse in :mod:`opencivil.pfahl.quer`, der innere quer in
:mod:`opencivil.pfahl.innen_quer` -- und die Steifigkeit
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
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Berechnung, Eingaben
from opencivil.core.einheiten import (
    EINHEITSLOS, GRAD, KN, KN_PRO_M3, KNM, KPA, M, MM, MN_PRO_M2, Groesse,
)
from opencivil.core.protokoll import Abschnitt
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.vorgaben import SCHICHT, Feld, Gruppe
from opencivil.core.wahl import Wahl
from opencivil.core.wert import WertDef, kennung_aus
from opencivil.geotechnik.verhalten import Verhalten
from opencivil.geotechnik.wasser import raumlast
from opencivil.material.basis import Baustoff
from opencivil.pfahl import buch
from opencivil.pfahl.boden import Mantel, Pfahlschicht, Profil

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


#: Wann der Grenzwert von η_a gilt -- am Schalter, in der Maske und in der
#: Herleitung (SIA 267:2013, 9.5.2.2.6).
GRENZWERT_GILT = ("Der Grenzwert gilt, wenn R_a,k sehr zuverlässig bestimmt ist; sonst ist "
                  "η_a kleiner (SIA 267:2013, 9.5.2.2.6).")


class Umrechnung(Wahl):
    """
    Woher der Umrechnungsfaktor η_a kommt (Benutzer, 2026-11-27): aus der
    Grundlage, dann ist er ihr Grenzwert, oder von Hand, höchstens dieser
    Grenzwert (:data:`GRENZWERT_GILT`). Bis 2026-11-27 war η_a immer eine
    Zahl von Hand, Vorgabe 0.7 -- auch nach einem statischen Versuch.
    """

    GRUNDLAGE = "grundlage"
    HAND = "hand"

    @property
    def beschriftung(self) -> str:
        return {Umrechnung.GRUNDLAGE: "aus der Grundlage", Umrechnung.HAND: "von Hand"}[self]

    @property
    def erklaerung(self) -> str:
        return {Umrechnung.GRUNDLAGE: "η_a ist der Grenzwert der Grundlage.",
                Umrechnung.HAND: "η_a von Hand, höchstens der Grenzwert der Grundlage."}[self] \
            + " " + GRENZWERT_GILT


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
# Die Vorgaben
# ===========================================================================

#: R_a,k aus einem Versuch: der kleinste gemessene Wert.
_VERSUCH = "SIA 267:2013, 9.4.4.1.3, 9.4.4.1.6"

_ABROSTUNG = Feld("dt", r"\Delta t", MM, "Abrostung aussen", 1, "SIA 267:2013, 9.6.1.5.2",
                  schritt=0.5, hinweis="Zuschlag für die Korrosion statt weiteren Schutzes")


def _pfahl(art: Pfahlart) -> Tuple[Feld, ...]:
    """Die Masse -- was D meint, hängt an der Art (siehe Dateikopf)."""
    if art is Pfahlart.MIKROPFAHL:
        D = Feld("D", "D", MM, "Durchmesser des Verpresskörpers", 0,
                 beschriftung="Verpresskörper", schritt=50,
                 hinweis="an ihm tragen Mantel und Fuss")
    else:
        D = Feld("D", "D", MM, "Durchmesser des Pfahls", 0, "SIA 267:2013, 9.5.2.4.7",
                 beschriftung="Durchmesser", schritt=50,
                 hinweis="verrohrt aussen an der Verrohrung, unverrohrt der des Bohrwerkzeugs")
    return (D,
            Feld("L", "L", M, "Länge des Pfahls", 2, beschriftung="Länge", schritt=0.5),
            Feld("t_K", "t_K", M, "Tiefe des Pfahlkopfs unter Terrain", 2,
                 beschriftung="Tiefe des Kopfs", schritt=0.5,
                 hinweis="darüber trägt der Boden nur als Auflast"))


def _aussen(grundlage: Grundlage, umrechnung: Umrechnung) -> Tuple[Feld, ...]:
    """
    η_a: aus der Grundlage fest ihr Grenzwert, von Hand höchstens er -- aus
    einem Versuch dazu R_a,k selbst.
    """
    grenze, fuer = grundlage.eta_grenze, f"für «{grundlage.beschriftung}»"
    fest = umrechnung is Umrechnung.GRUNDLAGE
    eta = Feld("eta_a", r"\eta_a", EINHEITSLOS, "Umrechnungsfaktor des äusseren Widerstands", 2,
               grundlage.referenz, beschriftung="Umrechnungsfaktor", schritt=0.05,
               hinweis=(f"der Grenzwert {fuer}" if fest else f"höchstens {grenze:.1f} {fuer}"),
               bis=grenze, fest=fest,
               bis_satz=f"η_a ist {fuer} höchstens {grenze:g} ({grundlage.referenz})")
    if not grundlage.aus_versuch:
        return (eta,)
    return (eta,
            Feld("R_ak", "R_{a,k}", KN, "Äusserer Widerstand auf Druck, aus dem Versuch", 0,
                 _VERSUCH, beschriftung="Widerstand auf Druck", schritt=50,
                 hinweis="der kleinste gemessene Wert"),
            Feld("R_ak_zug", "R_{a,k,Z}", KN, "Äusserer Widerstand auf Zug, aus dem Versuch", 0,
                 _VERSUCH, beschriftung="Widerstand auf Zug", schritt=50))


def _fuss(grundlage: Grundlage, spitze: Spitze) -> Tuple[Feld, ...]:
    """Der Spitzendruck, wo er eingegeben wird -- aus einem Versuch nie: R_a,k enthält den Fuss."""
    if grundlage.aus_versuch or spitze is not Spitze.EINGEBEN:
        return ()
    return (Feld("q_b", "q_{b,k}", KPA, "Spitzendruck, charakteristisch", 0,
                 beschriftung="Spitzendruck", schritt=100),)


def _querschnitt(art: Pfahlart, tragglied: Tragglied) -> Tuple[Feld, ...]:
    """Beim Bohrpfahl die Bewehrung, beim Mikropfahl das Tragglied -- dazu η_i."""
    if art is Pfahlart.BOHRPFAHL:
        masse: Tuple[Feld, ...] = (
            Feld("n", "n", EINHEITSLOS, "Zahl der Längsstäbe", 0, beschriftung="Zahl der Stäbe"),
            Feld("phi_l", r"\varnothing_l", MM, "Durchmesser der Längsstäbe", 0,
                 beschriftung="Durchmesser der Stäbe", schritt=2),
            Feld("c", "c", MM, "Überdeckung der Wendel", 0, schritt=5,
                 hinweis="mindestens 60 mm verrohrt, 60 mm unverrohrt in Fels oder hartem "
                         "Boden, 75 mm unverrohrt in weichem Boden (SIA 267:2013, 9.6.3.2.6)"),
            Feld("phi_w", r"\varnothing_w", MM, "Durchmesser der Wendel", 0, schritt=2),
            Feld("s_w", "s_w", MM, "Ganghöhe der Wendel", 0, "SIA 267:2013, 9.6.3.2.4",
                 schritt=10, hinweis="die grösste längs des Pfahls; in der Regel höchstens "
                                     "0.40 m, am Kopf 0.10 bis 0.15 m"),
        )
    elif tragglied is Tragglied.ROHR:
        masse = (Feld("d_a", "d_a", MM, "Aussendurchmesser des Rohrs", 1,
                      beschriftung="Aussendurchmesser"),
                 Feld("t_r", "t", MM, "Wanddicke des Rohrs", 1, beschriftung="Wanddicke",
                      schritt=0.5),
                 _ABROSTUNG)
    else:
        masse = (Feld("d_a", r"\varnothing", MM, "Durchmesser des Stabs", 1,
                      beschriftung="Durchmesser"),
                 _ABROSTUNG)
    return (*masse,
            Feld("eta_i", r"\eta_i", EINHEITSLOS, "Umrechnungsfaktor des inneren Widerstands", 2,
                 "SIA 267:2013, 9.5.2.4.4, (51); 9.5.2.4.9", beschriftung="Umrechnungsfaktor",
                 schritt=0.05, hinweis=f"in der Regel höchstens {ETA_I_REGEL}, mit verlässlicher "
                                       f"Prüfung der Integrität bis {ETA_I_HOECHSTENS}"))


#: Die Vorgaben des Pfahls, je Kasten der Herleitung und Karte der Maske
#: (:mod:`opencivil.core.vorgaben`) -- je nur, was nach den Wahlen gilt.
VORGABEN = (
    Gruppe("Pfahl", _pfahl, nach=("art",)),
    Gruppe("Grundwasser", lambda: (
        Feld("t_w", "t_w", M, "Tiefe des höchsten Grundwasserspiegels unter Terrain", 2,
             "SIA 267:2013, 4.2.2.3", beschriftung="Tiefe des Grundwassers", schritt=0.5),
    )),
    Gruppe("Äusserer Widerstand", _aussen, nach=("grundlage", "umrechnung")),
    Gruppe("Fuss", _fuss, nach=("grundlage", "spitze")),
    Gruppe("Querschnitt", _querschnitt, nach=("art", "tragglied")),
    Gruppe("Querlast", lambda: (
        Feld("t_red", "t_{red}", M,
             "Tiefe unter Terrain, bis zu der die Bettung quer von null an wächst", 2,
             "SIA 267:2013, 9.5.4.5", beschriftung="Abminderung bis", schritt=0.5),
        Feld("eta_tr", r"\eta_{a,tr}", EINHEITSLOS,
             "Umrechnungsfaktor des äusseren Widerstands quer", 2,
             "SIA 267:2013, 9.5.2.3.2; 9.5.2.2.5, (48)", beschriftung="Umrechnungsfaktor",
             schritt=0.05, hinweis=f"höchstens {Grundlage.BERECHNUNG.eta_grenze:.1f}: "
                                   "R_tr,k wird immer gerechnet"),
    )),
)


def _festigkeit(verhalten: Verhalten) -> Tuple[Feld, ...]:
    """Drainiert φ'_k und c'_k, undrainiert s_u,k -- wie beim Grundbruch."""
    if verhalten is Verhalten.UNDRAINIERT:
        return (Feld("s_u", "s_{u,k}", KPA, "Undrainierte Scherfestigkeit der #, charakteristisch",
                     1, beschriftung="Scherfestigkeit", schritt=5),)
    return (Feld("phi_k", r"\varphi'_k", GRAD, "Reibungswinkel der #, charakteristisch", 1,
                 beschriftung="Reibungswinkel"),
            Feld("c_k", "c'_k", KPA, "Kohäsion der #, charakteristisch", 1,
                 beschriftung="Kohäsion", hinweis="zählt am Fuss und im Erdwiderstand quer"))


def _mantel(verhalten: Verhalten, mantel: Mantel) -> Tuple[Feld, ...]:
    """Eingegeben q_s,k selbst, gerechnet die Beiwerte nach dem Verhalten."""
    if mantel is Mantel.EINGEBEN:
        return (Feld("q_s", "q_{s,k}", KPA, "Mantelreibung in der #, charakteristisch", 1,
                     beschriftung="Mantelreibung", schritt=5),)
    if verhalten is Verhalten.UNDRAINIERT:
        return (Feld("alpha", r"\alpha", EINHEITSLOS, "Adhäsion in der #, als Teil von s_u,k", 2,
                     buch.KAP_MANTEL, beschriftung="Adhäsion", schritt=0.05,
                     hinweis="am Bohrpfahl etwa 0.6 in weichem, 0.9 in steifem Ton"),)
    return (Feld("K", "K", EINHEITSLOS, "Erddruckbeiwert am Mantel in der #", 2, buch.KAP_MANTEL,
                 beschriftung="Erddruckbeiwert", schritt=0.05,
                 hinweis="an einem Bohrpfahl höchstens etwa K₀ = 1 − sin φ'_k"),
            Feld("delta_faktor", r"k_{\delta}", EINHEITSLOS,
                 "Reibungswinkel Pfahl–Boden in der #, als Teil von φ'_k", 2, buch.KAP_MANTEL,
                 beschriftung="Wandreibung", schritt=0.05, hinweis="rau etwa 1"))


#: Die Vorgaben jeder Schicht, je mit ihrer Nummer -- in der Herleitung ein
#: Kasten je Schicht, in der Maske eine Karte. Die Gruppen teilen sich beide;
#: ihre Titel sagen der Maske nur, wo die Schalter für Verhalten und Mantel
#: stehen.
JE_SCHICHT = (
    Gruppe(SCHICHT, lambda: (
        Feld("d", "d", M, "Dicke der #", 2, beschriftung="Dicke", schritt=0.5),
        Feld("gamma", r"\gamma", KN_PRO_M3, "Raumlast der #", 1, beschriftung="Raumlast",
             schritt=0.5),
    )),
    Gruppe("Festigkeit", _festigkeit, nach=("verhalten",)),
    Gruppe("Mantelreibung", _mantel, nach=("verhalten", "mantel")),
    Gruppe("Verformung", lambda: (
        Feld("E_s", "E_{s,k}", MN_PRO_M2, "Verformungsmodul der #, charakteristisch", 0,
             beschriftung="Verformungsmodul", schritt=5,
             hinweis="für die Federn: am Mantel 0.42·E, am Fuss 4.5·E (Cassan, Kap. 12.8), "
                     "quer E/D (SIA 267:2013, (53))"),
    )),
)


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

    wasser: Baustoff
    """
    Das Grundwasser, eine Flüssigkeit: seine Raumlast γ_w rechnet der Pfahl
    aus ihr (:mod:`opencivil.geotechnik.wasser`). Bis 2026-11-27 eine Zahl.
    """

    schichten: Sequence[Pfahlschicht]
    grundlage: Grundlage
    umrechnung: Umrechnung
    eta_a: Groesse
    """η_a von Hand -- aus der Grundlage gilt ihr Grenzwert (:func:`_aussen`)."""

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
    s_w: Groesse
    """
    Bohrpfahl: Zahl und Durchmesser der Längsstäbe, Überdeckung, Durchmesser
    und Ganghöhe der Wendel.
    """

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

    def _vorgaben(self) -> Iterator[Tuple[str, str, Feld, Groesse]]:
        """
        Je Vorgabe, die nach den Wahlen gilt: ihre Gruppe -- die der Schichten
        zusammen «Schicht» --, ihr Kasten in der Herleitung, ihr Feld und ihre
        Grösse.
        """
        for gruppe in VORGABEN:
            for f in gruppe.fuer(self):
                yield gruppe.titel, gruppe.titel, f, getattr(self, f.kurz)
        for i, s in enumerate(self.schichten, start=1):
            for gruppe in JE_SCHICHT:
                for f in gruppe.fuer(s):
                    yield SCHICHT, f"{SCHICHT} {i}: {s.name}", f.nummeriert(i), getattr(s, f.kurz)

    def _aufbauen(self) -> None:
        for _, kasten, f, groesse in self._vorgaben():
            d, vorgabe = f.vorgabe(self.id, self.abschnitt, kasten, groesse)
            self.definitionen[f.kurz] = d
            self.berechnungen.append(vorgabe)
        d_w, gamma_w = raumlast(self.id, self.abschnitt, self.wasser)
        self.definitionen["gamma_w"] = d_w
        self.berechnungen.append(gamma_w)

    def kurznamen(self, *gruppen: str) -> List[str]:
        """
        Die Kurznamen der Vorgaben, die gelten -- aus den genannten Gruppen, ohne
        Angabe aus allen. Die Schichten heissen zusammen «Schicht».
        """
        return [f.kurz for gruppe, _, f, _ in self._vorgaben() if not gruppen or gruppe in gruppen]
