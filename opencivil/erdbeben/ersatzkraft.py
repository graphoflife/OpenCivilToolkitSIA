"""
opencivil/erdbeben/ersatzkraft.py -- das Ersatzkraftverfahren nach SIA 261:2020, 16.5.2.

VERANTWORTUNG:
Das :class:`Gebaeude` -- Standort, Verhaltensbeiwerte, Geschosse und
Tragwaende als Vorgaben im Rechenwerk -- und seine Rechnung
:class:`Ersatzkraft`: je Hauptrichtung x und y die Grundschwingzeit, der
Wert des Bemessungsspektrums, die Ersatzkraft und ihre Verteilung auf die
Geschosse und auf die Waende. Ob das Verfahren gilt (16.5.2.1), sagen die
Urteile: je Richtung T_1 <= 4 T_C (39), mit seinem Erfuellungsgrad, und --
nur wo Grund- oder Aufriss nicht regelmaessig sind -- eines dazu, rot. Was
eines davon verfehlt, gilt fuer das ganze Gebaeude: die Norm verlangt (39) in
beiden Richtungen.

DAS VERFAHREN, je Richtung::

    W_i  = G_k,i + psi_2,i * Q_k,i                    Gewicht des Geschosses i
    EI   = Summe n * eta_EI * E_cm * I                die Waende dieser Richtung
    u    = Summe W_i * z_i^2 * (3 H - z_i) / (6 EI)   Kopf des Kragarms unter den W_i
    T_1  = 2 * sqrt(u)                                (40), u in m, T_1 in s
    S_d  = (31) bis (34)
    F_d  = S_d * Summe W_i                            (41)
    F_di = z_i * W_i / Summe z_j * W_j * F_d          (42)
    V_i  = Summe_(j >= i) F_dj                        unter dem Geschoss i
    M_i  = Summe_(j >= i) F_dj * (z_j - z_(i-1))      ebenda; M_1 = M_0 am Fuss

Die Waende einer Richtung stehen als ein Kragarm da, eingespannt am Fuss und
so hoch wie das Gebaeude; das Gewicht eines Geschosses wirkt waagrecht auf
der Hoehe seiner Decke, z_i ueber der Einspannung (16.5.2.3). Jede Wand
traegt von Querkraft und Moment am Fuss ihren Anteil an EI.

DIE WAND IM GRUNDRISS:
Ihr Querschnitt kommt aus einer Querschnittsanalyse, gezeichnet in y und z.
Bei 0 Grad liegt y in x des Gebaeudes: eine Kraft in x biegt sie um z, mit
I_z, eine in y mit I_y. Bei 90 Grad ist es umgekehrt (:meth:`Wandlage.traegheit`),
und im Bild liegt sie um 90 Grad gedreht (:meth:`Wandlage.im_grundriss`).

NACH VORGABE, NICHT NACHGESCHLAGEN (auch in TODO):
- die Verteilung auf die Waende nach ihrer Biegesteifigkeit;
- nur die Biegung der Waende verformt, weder Schub noch Fundament;
- eta_EI = 0.5 als Anteil der ungerissenen Steifigkeit -- verlangt ist nur
  eine mittlere Steifigkeit bis zum Fliessbeginn (16.5.5.2). Nicht kappa:
  das ist in der Querschnittsanalyse die Kruemmung und in SIA 262:2025 die
  Vergroesserung der Querkraft fuer hoehere Eigenformen (97) (Benutzer,
  2026-11-21);
- g = 10 m/s^2 wie beim Eigengewicht
  (:data:`~opencivil.stabwerk.rechnung.ERDBESCHLEUNIGUNG`).

QUELLE:
SIA 261:2020: 16.2 (Einwirkung), 16.3 (Bauwerksklassen), 16.5.1 und 16.5.2.
Die Verhaltensbeiwerte stehen in SIA 262:2025, 4.3.9 (Tabellen 14 und 15),
und SIA 263:2013, 4.9.1; die Beiwerte psi_2 in SIA 260:2013, Anhang A.

EINHEITEN:
Alles in SI-Basis; T_1 = 2 * sqrt(u) nimmt u als Zahl in m.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Berechnung, Eingabebezug, Eingaben
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, M, MM, MNM2, M_PRO_S2, S, Groesse
from opencivil.core.latex import Mathe, Zelle, als_text, fest
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Nachweis, NachweisUrteil, Vergleich, grad_def,
)
from opencivil.core.protokoll import (
    Abschnitt, GleichungBlock, Protokoll, TabellenBlock, Zwischenwerte,
)
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.vorgaben import Feld, Gruppe
from opencivil.core.wahl import Wahl
from opencivil.core.wert import Wert, WertDef
from opencivil.stabwerk.rechnung import ERDBESCHLEUNIGUNG
from opencivil.stabwerk.stabquerschnitt import keine_hauptachsen

SIA = "SIA 261:2020"
ZIFFER_ZONE = f"{SIA}, 16.2.1.2"
ZIFFER_BAUGRUND = f"{SIA}, Tabelle 24"
ZIFFER_BWK = f"{SIA}, Tabelle 25"
ZIFFER_SPEKTRUM = f"{SIA}, 16.2.4.1"
ZIFFER_GRENZE = f"{SIA}, 16.5.2.1, (39)"
ZIFFER_T1 = f"{SIA}, 16.5.2.3, (40)"
ZIFFER_F_D = f"{SIA}, 16.5.2.4, (41)"
ZIFFER_F_DI = f"{SIA}, 16.5.2.5, (42)"
ZIFFER_KIPPEN = f"{SIA}, 16.5.1.9"
ZIFFER_STEIFIGKEIT = f"{SIA}, 16.5.5.2"
NACH_VORGABE = "nach Vorgabe, nicht nachgeschlagen"

#: Die Hauptrichtungen des Gebaeudes, in denen gerechnet wird.
RICHTUNGEN = ("x", "y")

#: Was gilt, wo das Ersatzkraftverfahren nicht gilt (16.5.3.1).
NICHT_ZULAESSIG = "nicht zulässig – Antwortspektrenverfahren (16.5.3.1)"

#: Das Urteil, das nur steht, wo Grund- oder Aufriss nicht regelmaessig sind.
REGELMAESSIGKEIT = "Regelmässigkeit"

#: Was diese Rechnung nicht kennt -- grau im Ergebnis.
NICHT_GERECHNET = ("Nicht gerechnet: die Torsion (16.5.2.7), die vertikale Komponente "
                   "(16.5.4) und sekundäre Bauteile (16.7).")

#: Das groesste q fuer nicht-duktiles Verhalten (SIA 262:2025, 4.3.9.2.2, Tabelle 14);
#: wer mehr ansetzt, bemisst duktil (4.3.9.3.5, Tabelle 15) -- und fuer
#: Tragwaende gilt dann 4.3.9.4.
Q_NICHT_DUKTIL = 2.0
ZIFFER_DUKTIL = "SIA 262:2025, 4.3.9.2.2, Tabelle 14; 4.3.9.3.5, Tabelle 15; 4.3.9.4"


def duktile_waende(richtungen: Sequence[str]) -> str:
    """
    Der Hinweis, wo q duktiles Verhalten heisst: fuer schlanke Tragwaende
    gelten dann eigene Bemessungswerte (SIA 262:2025, 4.3.9.4), die diese
    Rechnung nicht kennt -- die Kraefte je Wand sind nicht schon die der
    Bemessung.
    """
    return (f"In {' und '.join(richtungen)} ist q grösser als {fest(Q_NICHT_DUKTIL, 1)}, "
            "das Tragwerk also duktil bemessen (SIA 262:2025, 4.3.9.3, Tabelle 15). Für "
            "schlanke Tragwände (h_w/l_w > 2) gilt dann 4.3.9.4: das Moment linear zwischen "
            "Fuss und Kopf, die Querkraft vergrössert für Überfestigkeit und höhere "
            "Eigenformen (95) – hier nicht gerechnet.")


# ===========================================================================
# Die Wahlen
# ===========================================================================


class Erdbebenzone(Wahl):
    """Die Zone des Standorts (16.2.1) -- sie gibt die Bodenbeschleunigung a_gd."""

    Z1A = "Z1a"
    Z1B = "Z1b"
    Z2 = "Z2"
    Z3A = "Z3a"
    Z3B = "Z3b"

    @property
    def a_gd(self) -> float:
        """Der Bemessungswert der Bodenbeschleunigung in m/s² (16.2.1.2)."""
        return _A_GD[self]


_A_GD = {Erdbebenzone.Z1A: 0.6, Erdbebenzone.Z1B: 0.8, Erdbebenzone.Z2: 1.0,
         Erdbebenzone.Z3A: 1.3, Erdbebenzone.Z3B: 1.6}


@dataclass(frozen=True)
class Spektrumwerte:
    """Was eine Baugrundklasse dem Spektrum gibt (Tabelle 24): S, und T_B, T_C, T_D in s."""

    S: float
    T_B: float
    T_C: float
    T_D: float


class Baugrundklasse(Wahl):
    """
    Die Klasse des Baugrunds (16.2.2, Tabelle 24). Klasse F gibt es hier
    nicht: dort braucht es eine spektrale Standortstudie (16.2.2.2).
    """

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"

    @property
    def werte(self) -> Spektrumwerte:
        return _SPEKTRUM[self]

    @property
    def erklaerung(self) -> str:
        """Der Baugrund der Klasse, kurz und in eigenen Worten -- fuer den Titel des Schalters."""
        return _BAUGRUND[self]


_SPEKTRUM = {Baugrundklasse.A: Spektrumwerte(1.00, 0.07, 0.25, 2.0),
             Baugrundklasse.B: Spektrumwerte(1.20, 0.08, 0.35, 2.0),
             Baugrundklasse.C: Spektrumwerte(1.45, 0.10, 0.40, 2.0),
             Baugrundklasse.D: Spektrumwerte(1.70, 0.10, 0.50, 2.0),
             Baugrundklasse.E: Spektrumwerte(1.70, 0.09, 0.25, 2.0)}

_BAUGRUND = {
    Baugrundklasse.A: "Fels, darüber höchstens 5 m Lockergestein",
    Baugrundklasse.B: "sehr dichter Kies oder Sand, sehr steifer Ton – einige zehn Meter mächtig",
    Baugrundklasse.C: "dichter bis mitteldichter Kies oder Sand, steifer Ton – mächtig",
    Baugrundklasse.D: "lockere bis mitteldichte oder weiche bis steife Ablagerungen",
    Baugrundklasse.E: "5 bis 20 m Lockergestein wie C oder D über steiferem Grund",
}


class Bauwerksklasse(Wahl):
    """Die Bauwerksklasse (16.3, Tabelle 25) -- sie gibt den Bedeutungsbeiwert gamma_f."""

    I = "I"  # noqa: E741 -- so heisst die Klasse
    II = "II"
    III = "III"

    @property
    def gamma_f(self) -> float:
        """Der Bedeutungsbeiwert fuer die Tragsicherheit."""
        return {Bauwerksklasse.I: 1.0, Bauwerksklasse.II: 1.2, Bauwerksklasse.III: 1.5}[self]

    @property
    def erklaerung(self) -> str:
        return {
            Bauwerksklasse.I: "Wohn-, Büro- und Gewerbebauten, Industrie, Parkhäuser – "
                              "alle übrigen Bauwerke",
            Bauwerksklasse.II: "grössere Gebäude, viele Personen, Schulen, Spitäler ohne "
                               "lebenswichtige Aufgabe",
            Bauwerksklasse.III: "lebenswichtige Infrastruktur: Akutspitäler, Feuerwehr, "
                                "Versorgung",
        }[self]


class Wandlage(Wahl):
    """Wie eine Wand im Grundriss liegt: wie in ihrer Querschnittsanalyse gezeichnet oder gedreht."""

    NULL = "0"
    NEUNZIG = "90"

    @property
    def beschriftung(self) -> str:
        return f"{self.value}°"

    @property
    def erklaerung(self) -> str:
        return {Wandlage.NULL: "wie gezeichnet: y der Querschnittsanalyse liegt in x",
                Wandlage.NEUNZIG: "um 90° gedreht: y der Querschnittsanalyse liegt in y"}[self]

    def traegheit(self, richtung: str) -> str:
        """Welches Traegheitsmoment eine Kraft in ``richtung`` biegt: ``I_z`` oder ``I_y``."""
        um_z = (self is Wandlage.NULL) == (richtung == "x")
        return "I_z" if um_z else "I_y"

    def im_grundriss(self, y: float, z: float) -> Tuple[float, float]:
        """Wo der Punkt (y, z) der Querschnittsanalyse im Grundriss liegt, als (x, y)."""
        return (y, z) if self is Wandlage.NULL else (-z, y)


class Schwingzeit(Wahl):
    """Woher die Grundschwingzeit kommt."""

    WAENDE = "waende"
    HAND = "hand"

    @property
    def beschriftung(self) -> str:
        return {Schwingzeit.WAENDE: "aus den Wänden", Schwingzeit.HAND: "von Hand"}[self]

    @property
    def erklaerung(self) -> str:
        return {
            Schwingzeit.WAENDE: "T₁ = 2·√u: u ist die Auslenkung des Dachs, wenn die Gewichte "
                                "der Geschosse waagrecht auf die Wände wirken (40)",
            Schwingzeit.HAND: "T₁ je Richtung selbst angeben, etwa nach Rayleigh (16.5.2.3)",
        }[self]


@dataclass(frozen=True)
class Regelmaessigkeit:
    """
    Ein Schalter der Regelmaessigkeit: das Feld des Eintrags, wie er heisst,
    seine Ziffer und ihre Kriterien in eigenen Worten -- fuer die Maske.
    """

    feld: str
    beschriftung: str
    ziffer: str
    kriterien: Tuple[str, ...]

    def als_dict(self) -> dict:
        return {"feld": self.feld, "beschriftung": self.beschriftung, "ziffer": self.ziffer,
                "kriterien": list(self.kriterien)}


#: Was der Benutzer bejaht, wenn er Grund- und Aufriss regelmaessig nennt.
REGELMAESSIG = (
    Regelmaessigkeit("grundriss_regelmaessig", "Grundriss regelmässig", "16.5.1.3", (
        "Steifigkeit und Masse sind in zwei rechtwinkligen Richtungen etwa symmetrisch verteilt",
        "der Grundriss ist kompakt: Einsprünge und Aussparungen messen zusammen höchstens 25 % "
        "der äusseren Abmessung in ihrer Richtung",
        "die Decken sind in ihrer Ebene viel steifer als Wände und Stützen waagrecht",
    )),
    Regelmaessigkeit("aufriss_regelmaessig", "Aufriss regelmässig", "16.5.1.4", (
        "jede Wand, jeder Kern und Rahmen, der waagrechte Kräfte trägt, läuft ohne Unterbruch "
        "vom Fundament bis oben",
        "Steifigkeit, Widerstand und Masse der Geschosse bleiben nach oben gleich oder nehmen "
        "allmählich ab, ohne Sprung – Untergeschosse ausgenommen. Nimmt das Gewicht nach oben "
        "zu, sagt es die Rechnung selbst",
    )),
)


# ===========================================================================
# Die Vorgaben
# ===========================================================================

#: Was ueber dem Verhaltensbeiwert steht -- die Werte der Normen, in eigenen Worten.
_Q_HINWEIS = ("Stahlbeton nicht duktil: 1.5 mit Betonstahl A, 2.0 mit B oder C "
              "(SIA 262:2025, Tab. 14); duktil: 3.0 mit B, 4.0 mit C (Tab. 15). "
              "Stahlbau: SIA 263:2013, 4.9.1")

#: Die Vorgaben des Gebaeudes, je Kasten der Herleitung und Karte der Maske
#: (:mod:`opencivil.core.vorgaben`).
VORGABEN = (
    Gruppe("Verhaltensbeiwert", lambda: tuple(
        Feld(f"q_{r}", f"q_{r}", EINHEITSLOS, f"Verhaltensbeiwert in {r}", 1,
             "SIA 262:2025, 4.3.9; SIA 263:2013, 4.9.1", beschriftung=f"in {r}", schritt=0.1,
             hinweis=_Q_HINWEIS)
        for r in RICHTUNGEN)),
    Gruppe("Grundschwingzeit", lambda schwingzeit: tuple(
        Feld(f"T1_{r}", f"T_{{1,{r}}}", S, f"Grundschwingzeit in {r}", 2, f"{SIA}, 16.5.2.2",
             beschriftung=f"in {r}", schritt=0.05)
        for r in RICHTUNGEN) if schwingzeit is Schwingzeit.HAND else (), nach=("schwingzeit",)),
)

GESCHOSS = "Geschoss"
WAND = "Wand"

#: Die Vorgaben jedes Geschosses, je mit seiner Nummer von unten.
JE_GESCHOSS = (Gruppe(GESCHOSS, lambda: (
    Feld("h", "h", M, "Höhe des Geschosses", 2, schritt=0.1,
         hinweis="von Decke zu Decke, das unterste ab der Einspannung"),
    Feld("G_k", "G_k", KN, "Ständige Last des Geschosses", 0, f"{SIA}, 16.5.2.3", schritt=100,
         hinweis="was mit seiner Decke schwingt: Decke, halbe Wände darüber und darunter, Ausbau"),
    Feld("Q_k", "Q_k", KN, "Nutzlast des Geschosses", 0, f"{SIA}, 16.5.2.3", schritt=100),
    Feld("psi_2", r"\psi_2", EINHEITSLOS, "Beiwert der Nutzlast, quasi-ständig", 1,
         "SIA 260:2013, Anhang A, Tabelle 2", schritt=0.1,
         hinweis="Wohn- und Büroflächen 0.3; Versammlung und Verkauf 0.6; Lager 0.8; Dächer 0"),
)),)

#: Die Vorgaben jeder Wand, je mit ihrer Nummer in der Liste.
JE_WAND = (Gruppe(WAND, lambda: (
    Feld("n", "n", EINHEITSLOS, "Anzahl gleicher Wände", 0, schritt=1),
    Feld("eta_EI", r"\eta_{EI}", EINHEITSLOS, "Anteil der ungerissenen Biegesteifigkeit", 2,
         ZIFFER_STEIFIGKEIT, schritt=0.05,
         hinweis="0.5 nach Vorgabe – verlangt ist eine mittlere Steifigkeit bis zum "
                 "Fliessbeginn"),
)),)


# ===========================================================================
# Das Gebaeude
# ===========================================================================


@dataclass(frozen=True)
class Geschoss:
    """Ein Geschoss, von unten gezaehlt: Hoehe und Lasten."""

    name: str
    h: Groesse
    G_k: Groesse
    Q_k: Groesse
    psi_2: Groesse


@dataclass(frozen=True)
class Wandquerschnitt:
    """Was eine Wand aus ihrer Querschnittsanalyse nimmt: Namen und die Wert-IDs."""

    analyse: str
    """Der Name der Querschnittsanalyse."""

    beton: str
    """Der Name ihres Betons."""

    I_y: str
    I_z: str
    I_yz: str
    E_cm: str


@dataclass(frozen=True)
class Wand:
    """Eine oder mehrere gleiche Tragwaende -- ``nummer`` ist ihr Platz in der Liste, ab 1."""

    nummer: int
    name: str
    lage: Wandlage
    n: Groesse
    eta_EI: Groesse
    querschnitt: Wandquerschnitt


@dataclass
class Gebaeude(Rechenobjekt):
    """
    Ein Gebaeude im Erdbeben: die Eingaben als Vorgaben im Rechenwerk. Die
    Geschosse liegen von unten nach oben; ``waende`` sind nur die, die
    rechnen -- ihre Querschnittsanalyse rechnet und hat einen Beton.
    """

    WAS = "Gebäude"

    name: str
    zone: Erdbebenzone
    baugrund: Baugrundklasse
    bauwerksklasse: Bauwerksklasse
    schwingzeit: Schwingzeit
    grundriss_regelmaessig: bool
    aufriss_regelmaessig: bool
    q_x: Groesse
    q_y: Groesse
    T1_x: Groesse
    T1_y: Groesse
    geschosse: Sequence[Geschoss]
    waende: Sequence[Wand]
    praefix: str

    definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)
    berechnungen: List[Berechnung] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.id = self.praefix
        for gruppe in VORGABEN:
            for f in gruppe.fuer(self):
                self._vorgabe(f, gruppe.titel, getattr(self, f.kurz))
        for i, geschoss in enumerate(self.geschosse, start=1):
            for f in JE_GESCHOSS[0].fuer(geschoss):
                self._vorgabe(f.nummeriert(i), f"{GESCHOSS} {i}: {geschoss.name}",
                              getattr(geschoss, f.kurz))
        for wand in self.waende:
            for f in JE_WAND[0].fuer(wand):
                self._vorgabe(f.nummeriert(wand.nummer), f"{WAND} {wand.nummer}: {wand.name}",
                              getattr(wand, f.kurz))

    @property
    def abschnitt(self) -> Abschnitt:
        """Ueberschrift, unter der das Gebaeude in der Herleitung steht."""
        return Abschnitt(f"Erdbeben: {self.name}", self.id, thema="Erdbeben")

    def _vorgabe(self, f: Feld, gruppe: str, groesse: Groesse) -> None:
        d, vorgabe = f.vorgabe(self.id, self.abschnitt, gruppe, groesse)
        self.definitionen[f.kurz] = d
        self.berechnungen.append(vorgabe)


# ===========================================================================
# Befund
# ===========================================================================


@dataclass(frozen=True)
class Wandanteil:
    """Was eine Wand einer Richtung traegt -- je eine von ``n`` gleichen; SI-Einheiten."""

    nummer: int
    name: str
    n: int
    EI: float
    """Die Biegesteifigkeit einer Wand in dieser Richtung, N m²."""

    anteil: float
    """Ihr Anteil an EI der Richtung -- einer Wand, nicht aller n."""

    V: float
    """Die Querkraft am Fuss, N."""

    M: float
    """Das Moment am Fuss, N m."""


def querkraefte(kraefte: Sequence[float]) -> Tuple[float, ...]:
    """Je Geschoss, von unten, die Querkraft unter ihm: die Kraefte von dort bis oben."""
    return tuple(sum(kraefte[i:]) for i in range(len(kraefte)))


def momente(kraefte: Sequence[float], z: Sequence[float]) -> Tuple[float, ...]:
    """
    Je Geschoss, von unten, das Moment unter ihm, auf der Hoehe der Decke
    darunter: die Kraefte von dort bis oben, je mal ihr Abstand. Am Fuss ist
    es das Kippmoment M_0 -- der Kragarm ist dort eingespannt.
    """
    unten = (0.0, *z[:-1])
    return tuple(sum(F * (zj - unten[i]) for F, zj in zip(kraefte[i:], z[i:]))
                 for i in range(len(kraefte)))


@dataclass(frozen=True)
class Richtungsbefund:
    """Was eine Hauptrichtung ergab, in SI-Einheiten. Die Kraefte je Geschoss von unten."""

    richtung: str
    T1: float
    u: Optional[float]
    """Die Auslenkung, aus der T_1 kommt -- ``None`` bei T_1 von Hand."""

    S_d: float
    F_d: float
    kraefte: Tuple[float, ...]
    M_0: float
    """Das Kippmoment am Fuss: die Kraefte mal ihre Hoehe."""

    S_d_1: float
    F_d_1: float
    M_0_1: float
    """Dasselbe mit q = 1.0, fuer Abheben und Kippen (16.5.1.9)."""

    EI: float
    """Die Biegesteifigkeit aller Waende dieser Richtung, N m² -- null ohne Wand."""

    waende: Tuple[Wandanteil, ...]


@dataclass(frozen=True)
class Erdbebenbefund:
    """Was die Rechnung ergab: Hoehen und Gewichte der Geschosse und je Richtung, was gilt."""

    z: Tuple[float, ...]
    """Die Hoehe jedes Geschosses ueber der Einspannung, m -- dort wirkt sein Gewicht."""

    W: Tuple[float, ...]
    """Die Gewichte, N."""

    richtungen: Tuple[Richtungsbefund, ...]
    """Je Richtung, die sich rechnen liess."""

    gruende: Tuple[str, ...] = ()
    """Warum das Verfahren nicht gilt -- leer, wo es gilt (16.5.2.1)."""

    hinweise: Tuple[str, ...] = ()
    """
    Was die Rechnung grau dazu sagt: je Querschnittsanalyse, deren y und z
    keine Hauptachsen sind, ein Satz -- und wo q duktiles Verhalten heisst,
    was das fuer die Waende bedeutet.
    """

    @property
    def zulaessig(self) -> bool:
        return not self.gruende

    @property
    def ohne_einwirkung(self) -> bool:
        """Ohne Gewicht keine Ersatzkraft -- dann rechnet keine Richtung."""
        return sum(self.W) <= 0.0


# ===========================================================================
# Die Rechnung
# ===========================================================================


class Ersatzkraft(Nachweis):
    """
    Das Ersatzkraftverfahren je Hauptrichtung. Die Urteile sagen, ob es gilt
    (16.5.2.1): je Richtung T_1 <= 4 T_C (39), dazu -- nur wo es fehlt -- ein
    regelmaessiger Grund- und Aufriss. Die Kraefte stehen im Befund.
    """

    THEMA = "Erdbeben"
    LANGNAME = "Ersatzkraftverfahren"
    ART = "T1"

    def __init__(self, gebaeude: Gebaeude) -> None:
        self.gebaeude = gebaeude
        basis = f"{gebaeude.id}.nachweis.ersatzkraft"
        self.d_grad: Dict[str, WertDef] = {
            r: grad_def(f"{basis}.erfuellungsgrad_{r}", rf"\alpha_{{eff,{r}}}",
                        f"Erfüllungsgrad Ersatzkraftverfahren in {r}", ZIFFER_GRENZE)
            for r in RICHTUNGEN}
        self.d_grad[REGELMAESSIGKEIT] = grad_def(
            f"{basis}.erfuellungsgrad_regelmaessig", r"\alpha_{eff,R}",
            "Erfüllungsgrad Regelmässigkeit", f"{SIA}, 16.5.1.3; 16.5.1.4")
        bezuege = [Eingabebezug(k, d.id) for k, d in gebaeude.definitionen.items()]
        for wand in gebaeude.waende:
            q = wand.querschnitt
            bezuege += [Eingabebezug(f"{k}_{wand.nummer}", getattr(q, k))
                        for k in ("I_y", "I_z", "I_yz", "E_cm")]
        super().__init__(basis, ausgaben=list(self.d_grad.values()), bezuege=bezuege,
                         titel=f"Ersatzkraftverfahren – {gebaeude.name}",
                         abschnitt=gebaeude.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Ersatzkraftverfahren")
        p.erklaerung(
            "Das Beben wird durch waagrechte Kräfte ersetzt: je Hauptrichtung eine "
            "Ersatzkraft aus dem Bemessungsspektrum bei der Grundschwingzeit, verteilt auf "
            "die Geschosse nach Höhe und Gewicht. Die Wände tragen sie als Kragarme, "
            "eingespannt am Fuss – jede nach ihrem Anteil an der Biegesteifigkeit."
        )
        lauf = Lauf(self, e, p)
        p.hinweis(NICHT_GERECHNET)
        leer = Erdbebenbefund(tuple(lauf.z), tuple(lauf.W), (),
                              hinweise=lauf.hauptachsen() + lauf.duktil())
        if leer.ohne_einwirkung:
            p.text(OHNE_EINWIRKUNG)
            return Ausfuehrung({}, tuple(
                self.urteil(self.d_grad[r], f"Richtung {r}", UNBESCHRAENKT, OHNE_EINWIRKUNG)
                for r in RICHTUNGEN), leer)
        befunde = tuple(b for r in RICHTUNGEN if (b := lauf.richtung(r)) is not None)
        urteile, gruende = lauf.zulaessigkeit()
        return Ausfuehrung({}, urteile, Erdbebenbefund(leer.z, leer.W, befunde, gruende,
                                                       leer.hinweise))


def _unregelmaessig(g: Gebaeude, W: Sequence[float]) -> Tuple[str, ...]:
    """
    Warum das Verfahren nicht gilt, abgesehen von T_1: der Grund- oder der
    Aufriss, wie der Benutzer sie angibt -- und das Gewicht, das nach oben
    zunimmt, was die Zahlen selbst zeigen.
    """
    gruende = []
    if not g.grundriss_regelmaessig:
        gruende.append("der Grundriss ist nicht regelmässig (16.5.1.3)")
    if not g.aufriss_regelmaessig:
        gruende.append("der Aufriss ist nicht regelmässig (16.5.1.4)")
    schwerer = [g.geschosse[i].name for i in range(1, len(W)) if W[i] > W[i - 1]]
    if schwerer:
        gruende.append(f"das Gewicht nimmt nach oben zu, in «{'», «'.join(schwerer)}» (16.5.1.4)")
    return tuple(gruende)


class Lauf:
    """
    Ein Lauf der Rechnung, mit seinem Protokoll: Standort und Gewichte
    einmal, dann je Richtung (:meth:`richtung`).
    """

    def __init__(self, nachweis: Ersatzkraft, e: Eingaben, p: Protokoll) -> None:
        self.nachweis, self.e, self.p = nachweis, e, p
        self.gebaeude = nachweis.gebaeude
        self.werte = Zwischenwerte(nachweis.id)
        self.standort = self._standort()
        self.z, self.W = self._gewichte()
        self.T1: Dict[str, Wert] = {}
        """Je Richtung, die sich rechnen liess, ihre Grundschwingzeit -- fuer (39)."""
        self.summe = self.werte.kraft("W", r"\sum W", sum(self.W), "Gewicht des Gebäudes",
                                      stellen=0)
        p.formel(self.summe, r"\sum_i W_i", {}, titel="Gewicht des Gebäudes",
                 referenz=f"{SIA}, 16.5.2.4", name="Gewicht des Gebäudes")

    # -- Standort und Gewichte --------------------------------------------------

    def _standort(self) -> Dict[str, Wert]:
        """a_gd, S, T_B, T_C, T_D, gamma_f und g -- aus den Tabellen der Norm, als Werte."""
        g, p, werte = self.gebaeude, self.p, self.werte
        spektrum = g.baugrund.werte
        p.titel("Standort und Bauwerk", ebene=3)
        standort = {
            "a_gd": werte.wert("a_gd", "a_{gd}", Groesse(g.zone.a_gd, M_PRO_S2), 1,
                               "Bemessungswert der Bodenbeschleunigung"),
            "gamma_f": werte.wert("gamma_f", r"\gamma_f",
                                  Groesse(g.bauwerksklasse.gamma_f, EINHEITSLOS), 1,
                                  "Bedeutungsbeiwert"),
            "g": werte.wert("g", "g", ERDBESCHLEUNIGUNG, 0, "Erdbeschleunigung"),
            "S": werte.wert("S", "S", Groesse(spektrum.S, EINHEITSLOS), 2, "Bodenparameter"),
            "T_B": werte.wert("T_B", "T_B", Groesse(spektrum.T_B, S), 2, "Eckperiode T_B"),
            "T_C": werte.wert("T_C", "T_C", Groesse(spektrum.T_C, S), 2, "Eckperiode T_C"),
            "T_D": werte.wert("T_D", "T_D", Groesse(spektrum.T_D, S), 1, "Eckperiode T_D"),
        }
        p.wert(standort["a_gd"], titel=f"Erdbebenzone {g.zone.value}", referenz=ZIFFER_ZONE)
        for k in ("S", "T_B", "T_C", "T_D"):
            p.wert(standort[k], titel=f"Baugrundklasse {g.baugrund.value}",
                   referenz=ZIFFER_BAUGRUND)
        p.wert(standort["gamma_f"], titel=f"Bauwerksklasse {g.bauwerksklasse.value}",
               referenz=ZIFFER_BWK)
        p.wert(standort["g"], titel="Erdbeschleunigung, wie beim Eigengewicht",
               referenz=NACH_VORGABE)
        return standort

    def _gewichte(self) -> Tuple[List[float], List[float]]:
        """Je Geschoss seine Hoehe ueber der Einspannung und sein Gewicht, von unten -- SI."""
        e, p = self.e, self.p
        geschosse = self.gebaeude.geschosse
        p.titel("Gewichte der Geschosse", ebene=3)
        p.ansatz(r"W_i = G_{k,i} + \psi_{2,i} \cdot Q_{k,i} \qquad z_i = \sum_{j \le i} h_j",
                 titel="Gewicht und Höhe eines Geschosses", referenz=f"{SIA}, 16.5.2.3",
                 name="Gewicht eines Geschosses")
        z: List[float] = []
        W: List[float] = []
        for i in range(1, len(geschosse) + 1):
            z.append((z[-1] if z else 0.0) + e.g(f"h_{i}").si)
            W.append(e.g(f"G_k_{i}").si + e.g(f"psi_2_{i}").si * e.g(f"Q_k_{i}").si)
        p.tabelle(
            kopf=[GESCHOSS, Mathe(r"h\ [\mathrm{m}]"), Mathe(r"z\ [\mathrm{m}]"),
                  Mathe(r"G_k\ [\mathrm{kN}]"), Mathe(r"Q_k\ [\mathrm{kN}]"), Mathe(r"\psi_2"),
                  Mathe(r"W\ [\mathrm{kN}]")],
            zeilen=[[f"{i}: {s.name}", Mathe(fest(e.g(f"h_{i}").si, 2)), Mathe(fest(z[i - 1], 2)),
                     Mathe(fest(e.g(f"G_k_{i}").in_einheit(KN), 0)),
                     Mathe(fest(e.g(f"Q_k_{i}").in_einheit(KN), 0)),
                     Mathe(fest(e.g(f"psi_2_{i}").si, 1)), Mathe(fest(W[i - 1] / 1e3, 0))]
                    for i, s in enumerate(geschosse, start=1)],
            titel="Geschosse, von unten", ausrichtung="lrrrrrr")
        return z, W

    def hauptachsen(self) -> Tuple[str, ...]:
        """
        Je Querschnittsanalyse einer Wand, deren y und z merklich keine
        Hauptachsen sind, der Hinweis -- derselbe wie im Raum
        (:func:`~opencivil.stabwerk.stabquerschnitt.keine_hauptachsen`).
        """
        saetze: Dict[str, str] = {}
        for w in self.gebaeude.waende:
            name = w.querschnitt.analyse
            text = keine_hauptachsen(f"Querschnittsanalyse «{name}»", *(
                self.e.g(f"{k}_{w.nummer}").si for k in ("I_y", "I_z", "I_yz")), was="die Wand")
            if text is not None and name not in saetze:
                saetze[name] = text
                self.p.hinweis(text)
        return tuple(saetze.values())

    def duktil(self) -> Tuple[str, ...]:
        """
        Der Hinweis zu duktil bemessenen Waenden (:func:`duktile_waende`) --
        nur mit Wand, und in der Herleitung mit dem q, das ihn ausloest.
        """
        q = {r: self.e[f"q_{r}"].groesse.si for r in RICHTUNGEN}
        duktil = [r for r in RICHTUNGEN if q[r] > Q_NICHT_DUKTIL]
        if not duktil or not self.gebaeude.waende:
            return ()
        self.p.gleichung(r" \qquad ".join(rf"q_{r} = {fest(q[r], 1)} > {fest(Q_NICHT_DUKTIL, 1)}"
                                          for r in duktil),
                         titel="Duktil bemessen", referenz=ZIFFER_DUKTIL)
        text = duktile_waende(duktil)
        self.p.hinweis(text)
        return (text,)

    # -- Je Richtung --------------------------------------------------------------

    def richtung(self, r: str) -> Optional[Richtungsbefund]:
        """Der Befund einer Richtung -- ``None``, wo sich T_1 nicht rechnen laesst."""
        self.p.titel(f"Richtung {r}", ebene=3)
        EI, je_wand = self._steifigkeit(r)
        T1, u = self._schwingzeit(r, EI)
        if T1 is None:
            return None
        self.T1[r] = T1
        S_d = self._spektrum(r, T1, self.e[f"q_{r}"], "")
        F_d, kraefte, M_0 = self._kraefte(r, S_d)
        EI_si = EI.groesse.si if EI is not None else 0.0
        anteile = self._waende(r, EI_si, je_wand, F_d.groesse.si, M_0.groesse.si)
        F_d_1, M_0_1, S_d_1 = self._kippen(r, T1, F_d.groesse.si, M_0.groesse.si)
        return Richtungsbefund(
            richtung=r, T1=T1.groesse.si, u=u, S_d=S_d.groesse.si, F_d=F_d.groesse.si,
            kraefte=tuple(kraefte), M_0=M_0.groesse.si, S_d_1=S_d_1, F_d_1=F_d_1, M_0_1=M_0_1,
            EI=EI_si, waende=anteile)

    def _steifigkeit(self, r: str) -> Tuple[Optional[Wert], Dict[int, float]]:
        """EI aller Waende in ``r`` -- ``None`` ohne Wand --, je Wand das EI einer von ihnen in N m²."""
        e, p = self.e, self.p
        waende = self.gebaeude.waende
        je_wand: Dict[int, float] = {}
        if not waende:
            return None, je_wand
        zeilen: List[List[Zelle]] = []
        for w in waende:
            k, traegheit = w.nummer, w.lage.traegheit(r)
            I, E_cm = e.g(f"{traegheit}_{k}").si, e.g(f"E_cm_{k}").si
            n, eta = e.g(f"n_{k}").si, e.g(f"eta_EI_{k}").si
            je_wand[k] = eta * E_cm * I
            zeilen.append([f"{k}: {w.name}", w.querschnitt.analyse, w.lage.beschriftung,
                           Mathe(f"{traegheit} = {fest(I, 4)}"), Mathe(fest(E_cm / 1e6, 0)),
                           Mathe(fest(eta, 2)), Mathe(fest(n, 0)),
                           Mathe(fest(n * je_wand[k] / 1e6, 0))])
        p.tabelle(
            kopf=[WAND, "Querschnittsanalyse", "Lage", Mathe(r"I\ [\mathrm{m}^4]"),
                  Mathe(r"E_{cm}\ [\mathrm{N/mm^2}]"), Mathe(r"\eta_{EI}"), Mathe("n"),
                  Mathe(r"n \cdot \eta_{EI} \cdot E_{cm} \cdot I\ [\mathrm{MNm^2}]")],
            zeilen=zeilen, titel=f"Biegesteifigkeit der Wände in {r}", ausrichtung="lllrrrrr")
        EI = self.werte.wert(f"EI_{r}", f"EI_{r}", Groesse.aus_si(
            sum(e.g(f"n_{w.nummer}").si * je_wand[w.nummer] for w in waende), MNM2), 0,
            f"Biegesteifigkeit der Wände in {r}")
        p.formel(EI, r"\sum n \cdot \eta_{EI} \cdot E_{cm} \cdot I", {},
                 titel=f"Biegesteifigkeit der Wände in {r}",
                 referenz=f"{ZIFFER_STEIFIGKEIT}; {NACH_VORGABE}",
                 name="Biegesteifigkeit der Wände")
        return EI, je_wand

    def _schwingzeit(self, r: str, EI: Optional[Wert]) -> Tuple[Optional[Wert], Optional[float]]:
        """T_1 von Hand oder aus den Waenden (40) -- ohne Wand keine; dazu u in m."""
        p, werte = self.p, self.werte
        if self.gebaeude.schwingzeit is Schwingzeit.HAND:
            T1 = self.e[f"T1_{r}"]
            p.wert(T1, titel=f"Grundschwingzeit in {r}, von Hand", referenz=f"{SIA}, 16.5.2.2")
            return T1, None
        if EI is None or EI.groesse.si <= 0.0:
            p.text(f"In {r} trägt keine Wand: ohne Steifigkeit keine Grundschwingzeit und "
                   f"keine Ersatzkraft.")
            return None, None
        H = self.z[-1]
        u_si = sum(Wi * zi * zi * (3.0 * H - zi)
                   for Wi, zi in zip(self.W, self.z)) / (6.0 * EI.groesse.si)
        hoehe = werte.wert(f"H_{r}", "H", Groesse.aus_si(H, M), 2, "Höhe des Gebäudes")
        u = werte.wert(f"u_{r}", f"u_{r}", Groesse.aus_si(u_si, MM), 1,
                       f"Auslenkung des Dachs in {r}")
        p.formel(u, r"\sum_i \frac{W_i \cdot z_i^2 \cdot (3 \cdot @H - z_i)}{6 \cdot @EI}",
                 {"H": hoehe, "EI": EI},
                 titel=f"Auslenkung des Dachs, die Gewichte waagrecht in {r} auf den Kragarm",
                 referenz=f"{ZIFFER_T1}; {NACH_VORGABE}", name="Auslenkung des Dachs")
        T1 = werte.wert(f"T1_{r}", f"T_{{1,{r}}}", Groesse(2.0 * math.sqrt(u_si), S), 3,
                        f"Grundschwingzeit in {r}")
        p.formel(T1, r"2 \cdot \sqrt{@u}", {"u": u}, titel=f"Grundschwingzeit in {r}",
                 referenz=ZIFFER_T1, empirisch={"u": M}, name="Grundschwingzeit")
        return T1, u_si

    def _spektrum(self, r: str, T1: Wert, q: Wert, zusatz: str) -> Wert:
        """S_d(T_1) nach (31) bis (34), je nach dem Ast, in dem T_1 liegt."""
        s = self.standort
        T, T_B, T_C, T_D = (x.groesse.si for x in (T1, s["T_B"], s["T_C"], s["T_D"]))
        faktor = s["gamma_f"].groesse.si * s["a_gd"].groesse.si / s["g"].groesse.si
        S_, q_si = s["S"].groesse.si, q.groesse.si
        if T <= T_B:
            zahl = faktor * S_ * (0.67 + (2.5 / q_si - 0.67) * T / T_B)
            nummer, vorlage = "(31)", (r"@gamma_f \cdot \frac{@a_gd}{@g} \cdot @S \cdot "
                                       r"\left(0.67 + \left(\frac{2.5}{@q} - 0.67\right) "
                                       r"\cdot \frac{@T}{@T_B}\right)")
        elif T <= T_C:
            zahl = 2.5 * faktor * S_ / q_si
            nummer, vorlage = "(32)", r"2.5 \cdot @gamma_f \cdot \frac{@a_gd}{@g} \cdot \frac{@S}{@q}"
        elif T <= T_D:
            zahl = 2.5 * faktor * S_ * T_C / (T * q_si)
            nummer, vorlage = "(33)", (r"2.5 \cdot @gamma_f \cdot \frac{@a_gd}{@g} \cdot @S "
                                       r"\cdot \frac{@T_C}{@T \cdot @q}")
        else:
            zahl = max(2.5 * faktor * S_ * T_C * T_D / (T * T * q_si), 0.1 * faktor)
            nummer, vorlage = "(34)", (r"\max\left(2.5 \cdot @gamma_f \cdot \frac{@a_gd}{@g} "
                                       r"\cdot @S \cdot \frac{@T_C \cdot @T_D}{@T^2 \cdot @q};"
                                       r"\ 0.1 \cdot @gamma_f \cdot \frac{@a_gd}{@g}\right)")
        S_d = self.werte.wert(f"S_d{zusatz}_{r}", f"S_{{d,{r}}}{zusatz and '(q = 1)'}",
                              Groesse(zahl, EINHEITSLOS), 3, "Ordinate des Bemessungsspektrums")
        self.p.formel(S_d, vorlage, {**s, "q": q, "T": T1},
                      titel=f"Bemessungsspektrum bei T₁ in {r}",
                      referenz=f"{ZIFFER_SPEKTRUM}, {nummer}", name=f"Bemessungsspektrum {nummer}")
        return S_d

    def _kraefte(self, r: str, S_d: Wert) -> Tuple[Wert, List[float], Wert]:
        """F_d (41), die Kraefte je Geschoss (42) und das Kippmoment am Fuss."""
        p, werte, z, W = self.p, self.werte, self.z, self.W
        F_d = werte.kraft(f"F_d_{r}", f"F_{{d,{r}}}", S_d.groesse.si * sum(W),
                          f"Ersatzkraft in {r}", stellen=0)
        p.formel(F_d, r"@S_d \cdot @W", {"S_d": S_d, "W": self.summe},
                 titel=f"Ersatzkraft in {r}", referenz=ZIFFER_F_D, name="Ersatzkraft")
        p.ansatz(r"F_{d,i} = \frac{z_i \cdot W_i}{\sum_j z_j \cdot W_j} \cdot F_d",
                 titel="Verteilung auf die Geschosse", referenz=ZIFFER_F_DI,
                 name="Ersatzkraft eines Geschosses")
        nenner = sum(zi * Wi for zi, Wi in zip(z, W))
        kraefte = [zi * Wi / nenner * F_d.groesse.si for zi, Wi in zip(z, W)]
        V, M_unter = querkraefte(kraefte), momente(kraefte, z)
        p.tabelle(
            kopf=[GESCHOSS, Mathe(r"z\ [\mathrm{m}]"), Mathe(r"W\ [\mathrm{kN}]"),
                  Mathe(r"z \cdot W\ [\mathrm{kNm}]"), Mathe(r"F_{d,i}\ [\mathrm{kN}]"),
                  Mathe(r"V\ [\mathrm{kN}]"), Mathe(r"M\ [\mathrm{kNm}]")],
            zeilen=[[f"{i}: {g.name}", Mathe(fest(z[i - 1], 2)), Mathe(fest(W[i - 1] / 1e3, 0)),
                     Mathe(fest(z[i - 1] * W[i - 1] / 1e3, 0)),
                     Mathe(fest(kraefte[i - 1] / 1e3, 1)), Mathe(fest(V[i - 1] / 1e3, 1)),
                     Mathe(fest(M_unter[i - 1] / 1e3, 0))]
                    for i, g in enumerate(self.gebaeude.geschosse, start=1)],
            titel=f"Kräfte je Geschoss in {r} – V und M: Querkraft und Moment unter dem "
                  f"Geschoss, auf der Höhe der Decke darunter",
            ausrichtung="lrrrrrr")
        # Am Fuss ist das Moment unter dem untersten Geschoss das Kippmoment.
        M_0 = werte.wert(f"M_0_{r}", f"M_{{0,{r}}}", Groesse.aus_si(M_unter[0], KNM), 0,
                         f"Kippmoment am Fuss in {r}")
        p.formel(M_0, r"\sum_i F_{d,i} \cdot z_i", {}, titel=f"Kippmoment am Fuss in {r}",
                 referenz="", name="Kippmoment am Fuss")
        return F_d, kraefte, M_0

    def _waende(self, r: str, EI: float, je_wand: Dict[int, float], F_d: float,
                M_0: float) -> Tuple[Wandanteil, ...]:
        """Je Wand ihr Anteil an EI -- und so viel von Querkraft und Moment am Fuss."""
        if EI <= 0.0:
            self.p.text(f"In {r} trägt keine Wand: die Kräfte bleiben ohne Verteilung.")
            return ()
        anteile = tuple(
            Wandanteil(nummer=w.nummer, name=w.name, n=round(self.e.g(f"n_{w.nummer}").si),
                       EI=je_wand[w.nummer], anteil=je_wand[w.nummer] / EI,
                       V=je_wand[w.nummer] / EI * F_d, M=je_wand[w.nummer] / EI * M_0)
            for w in self.gebaeude.waende)
        self.p.tabelle(
            kopf=[WAND, Mathe("n"), Mathe(r"EI / \sum EI"), Mathe(r"V\ [\mathrm{kN}]"),
                  Mathe(r"M\ [\mathrm{kNm}]")],
            zeilen=[[f"{a.nummer}: {a.name}", Mathe(str(a.n)), Mathe(fest(a.anteil, 3)),
                     Mathe(fest(a.V / 1e3, 1)), Mathe(fest(a.M / 1e3, 0))] for a in anteile],
            titel=f"Je Wand in {r}, am Fuss – nach ihrem Anteil an der Biegesteifigkeit "
                  f"({NACH_VORGABE})",
            ausrichtung="lrrrr")
        return anteile

    def _kippen(self, r: str, T1: Wert, F_d: float, M_0: float) -> Tuple[float, float, float]:
        """Dasselbe mit q = 1.0 -- fuer Abheben und Kippen (16.5.1.9): F_d, M_0 und S_d."""
        p, werte = self.p, self.werte
        p.titel(f"Abheben und Kippen in {r}, mit q = 1.0", ebene=4)
        eins = werte.wert(f"q_1_{r}", "q", Groesse(1.0, EINHEITSLOS), 1, "Verhaltensbeiwert")
        S_d = self._spektrum(r, T1, eins, "_1")
        F = werte.kraft(f"F_d_1_{r}", f"F_{{d,{r}}}(q = 1)", S_d.groesse.si * sum(self.W),
                        f"Ersatzkraft in {r} mit q = 1.0", stellen=0)
        p.formel(F, r"@S_d \cdot @W", {"S_d": S_d, "W": self.summe},
                 titel="Ersatzkraft für Abheben und Kippen", referenz=ZIFFER_KIPPEN,
                 name="Ersatzkraft")
        M = werte.wert(f"M_0_1_{r}", f"M_{{0,{r}}}(q = 1)",
                       Groesse.aus_si(M_0 * F.groesse.si / F_d if F_d > 0.0 else 0.0, KNM), 0,
                       f"Kippmoment am Fuss in {r} mit q = 1.0")
        p.formel(M, r"\sum_i F_{d,i} \cdot z_i", {}, titel="Kippmoment für Abheben und Kippen",
                 referenz=ZIFFER_KIPPEN, name="Kippmoment am Fuss")
        return F.groesse.si, M.groesse.si, S_d.groesse.si

    # -- Ob das Verfahren gilt ------------------------------------------------------

    def zulaessigkeit(self) -> Tuple[Tuple[NachweisUrteil, ...], Tuple[str, ...]]:
        """
        Die Urteile, ob das Verfahren gilt (16.5.2.1) -- je Richtung T_1 <= 4 T_C
        (39), dazu, nur wo es fehlt, die Regelmaessigkeit -- und alle Gruende,
        warum nicht. Wer verfehlt, nennt im Hinweis jeden Grund: das Verfahren
        gilt fuer das Gebaeude oder gar nicht.
        """
        p, nachweis, T_C = self.p, self.nachweis, self.standort["T_C"]
        p.titel("Gilt das Verfahren?", ebene=3)
        grenze = self.werte.wert("T_grenze", "T_{1,max}", Groesse(4.0 * T_C.groesse.si, S), 2,
                                 "Grenze der Grundschwingzeit")
        p.formel(grenze, r"4 \cdot @T_C", {"T_C": T_C}, titel="Grenze der Grundschwingzeit",
                 referenz=ZIFFER_GRENZE, name="Grenze der Grundschwingzeit")
        vergleiche = {r: Vergleich(T1, grenze) for r, T1 in self.T1.items()}
        unregelmaessig = _unregelmaessig(self.gebaeude, self.W)
        gruende = (*unregelmaessig, *(f"in {r} ist T₁ > 4·T_C (39)"
                                      for r, v in vergleiche.items() if not v.erfuellt))
        hinweis = f"{NICHT_ZULAESSIG}: {'; '.join(gruende)}" if gruende else ""
        urteile = []
        for r, v in vergleiche.items():
            v.bedingung(p, f"Grundschwingzeit in {r}")
            v.zeile(p, nachweis.d_grad[r])
            satz = (f"T₁ = {self.T1[r].formatiert()} s {'≤' if v.erfuellt else '>'} 4·T_C = "
                    f"{grenze.formatiert()} s.")
            urteile.append(nachweis.urteil(nachweis.d_grad[r], f"Richtung {r}", v, satz,
                                           hinweis="" if v.erfuellt else hinweis))
        if unregelmaessig:
            satz = "; ".join(unregelmaessig)
            p.text(f"{satz[0].upper()}{satz[1:]}.")
            urteile.append(nachweis.urteil(nachweis.d_grad[REGELMAESSIGKEIT], REGELMAESSIGKEIT,
                                           NICHT_FUEHRBAR, f"{satz[0].upper()}{satz[1:]}.",
                                           hinweis=hinweis))
        else:
            p.text("Grund- und Aufriss sind regelmässig, wie angegeben, und das Gewicht nimmt "
                   "nach oben nicht zu (16.5.1.3, 16.5.1.4).")
        if gruende:
            p.text(f"{hinweis[0].upper()}{hinweis[1:]}.")
        return tuple(urteile), gruende


# ===========================================================================
# Für die Zusammenfassung
# ===========================================================================


def angaben(gebaeude: Gebaeude, werte: Dict[str, Wert]) -> GleichungBlock:
    """
    Ueber der Tabelle: in der ersten Zeile Standort und Bauwerksklasse, in der
    zweiten, was sie geben, und die Verhaltensbeiwerte -- eine Zeile waere
    breiter als die rechte Spalte.
    """
    oben = als_text(f"Zone {gebaeude.zone.value}, Baugrund {gebaeude.baugrund.value}, "
                    f"BWK {gebaeude.bauwerksklasse.value}")
    unten = [rf"a_{{gd}} = {fest(gebaeude.zone.a_gd, 1)}\ \mathrm{{m/s^2}}",
             rf"\gamma_f = {fest(gebaeude.bauwerksklasse.gamma_f, 1)}"]
    unten += [rf"q_{r} = {fest(werte[gebaeude.id_von(f'q_{r}')].groesse.si, 1)}"
              for r in RICHTUNGEN if gebaeude.id_von(f"q_{r}") in werte]
    return GleichungBlock(latex=(r"\begin{aligned} & " + oben + r" \\ & "
                                 + r" \qquad ".join(unten) + r" \end{aligned}"),
                          titel="Angaben zum Gebäude")


def kraefte(befund: Erdbebenbefund) -> TabellenBlock:
    """Je Richtung T_1, S_d, F_d und das Kippmoment -- mit q und mit q = 1.0."""
    return TabellenBlock(
        kopf=["Richtung", Mathe(r"T_1\ [\mathrm{s}]"), Mathe("S_d"), Mathe(r"F_d\ [\mathrm{kN}]"),
              Mathe(r"M_0\ [\mathrm{kNm}]"), Mathe(r"F_d(q = 1)\ [\mathrm{kN}]"),
              Mathe(r"M_0(q = 1)\ [\mathrm{kNm}]")],
        zeilen=[[b.richtung, Mathe(fest(b.T1, 3)), Mathe(fest(b.S_d, 3)),
                 Mathe(fest(b.F_d / 1e3, 0)), Mathe(fest(b.M_0 / 1e3, 0)),
                 Mathe(fest(b.F_d_1 / 1e3, 0)), Mathe(fest(b.M_0_1 / 1e3, 0))]
                for b in befund.richtungen],
        titel="Ersatzkräfte", ausrichtung="lrrrrrr")
