"""
opencivil/erdbeben/ersatzkraft.py -- das Ersatzkraftverfahren nach SIA 261:2020, 16.5.2.

VERANTWORTUNG:
Das :class:`Gebaeude` -- Standort, Verhaltensbeiwerte und Geschosse mit
ihrem Kern als Vorgaben im Rechenwerk -- und seine Rechnung
:class:`Ersatzkraft`: je Hauptrichtung x und y die Grundschwingzeit, der
Wert des Bemessungsspektrums, die Ersatzkraft und ihre Verteilung auf die
Geschosse und, am Fuss, auf die Teile des Kerns. Ob das Verfahren gilt
(16.5.2.1), sagen die Urteile: je Richtung T_1 <= 4 T_C (39), mit seinem Erfuellungsgrad, und --
nur wo Grund- oder Aufriss nicht regelmaessig sind -- eines dazu, rot. Was
eines davon verfehlt, gilt fuer das ganze Gebaeude: die Norm verlangt (39) in
beiden Richtungen.

DAS VERFAHREN, je Richtung::

    W_i  = G_k,i + psi_2,i * Q_k,i                    Gewicht des Geschosses i
    EI_i = eta_EI,i * E_cm,i * I_i                    sein Kern in dieser Richtung
    u    = Summe Delta u_i (:mod:`.kragarm`)          Kopf des Kragarms unter den W_i
    T_1  = 2 * sqrt(u)                                (40), u in m, T_1 in s
    S_d  = (31) bis (34)
    F_d  = S_d * Summe W_i                            (41)
    F_di = z_i * W_i / Summe z_j * W_j * F_d          (42)
    V_i  = Summe_(j >= i) F_dj                        unter dem Geschoss i
    M_i  = Summe_(j >= i) F_dj * (z_j - z_(i-1))      ebenda; M_1 = M_0 am Fuss

Der Kern steht je Richtung als ein Kragarm da, eingespannt am Fuss und so
hoch wie das Gebaeude, in jedem Geschoss mit dessen EI; das Gewicht eines
Geschosses wirkt waagrecht auf der Hoehe seiner Decke, z_i ueber der
Einspannung (16.5.2.3). Besteht der Kern am Fuss aus getrennten Teilen,
traegt jeder von Querkraft und Moment dort seinen Anteil an EI.

DER KERN IM GRUNDRISS:
Je Geschoss eine Querschnittsanalyse: der ganze Kern mit allen Waenden in x
und in y, gezeichnet, wie er im Grundriss liegt -- y der Analyse liegt in x
des Gebaeudes, z in y (Benutzer, 2026-11-27). Eine Kraft in x biegt ihn um
z, mit I_z, eine in y um y, mit I_y (:func:`traegheit`). Getrennte Teile
zaehlen je um ihren eigenen Schwerpunkt (:mod:`.kern`).

NACH VORGABE, NICHT NACHGESCHLAGEN (auch in TODO):
- getrennte Teile des Kerns je um ihren eigenen Schwerpunkt, ohne
  Steiner-Anteil zwischen ihnen (:mod:`.kern`);
- die Verteilung auf die Teile am Fuss nach ihrer Biegesteifigkeit;
- nur die Biegung des Kerns verformt, weder Schub noch Fundament;
- eta_EI = 0.5 als Anteil der ungerissenen Steifigkeit -- verlangt ist nur
  eine mittlere Steifigkeit bis zum Fliessbeginn (16.5.5.2). Nicht kappa:
  das ist in der Querschnittsanalyse die Kruemmung und in SIA 262:2025 die
  Vergroesserung der Querkraft fuer hoehere Eigenformen (97) (Benutzer,
  2026-11-21);
- g = 10 m/s^2 wie beim Eigengewicht
  (:data:`~opencivil.material.basis.ERDBESCHLEUNIGUNG`).

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
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Berechnung, Eingabebezug, Eingaben
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, M, MM, M_PRO_S2, S, Groesse
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
from opencivil.erdbeben.kern import Kern, Kerndaten
from opencivil.erdbeben.kragarm import beitraege, momente, querkraefte
from opencivil.material.basis import ERDBESCHLEUNIGUNG
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
    Rechnung nicht kennt -- die Kraefte am Kern und an seinen Teilen sind
    nicht schon die der Bemessung.
    """
    return (f"In {' und '.join(richtungen)} ist q grösser als {fest(Q_NICHT_DUKTIL, 1)}, "
            "das Tragwerk also duktil bemessen (SIA 262:2025, 4.3.9.3, Tabelle 15). Für "
            "schlanke Tragwände (h_w/l_w > 2) gilt dann 4.3.9.4: das Moment linear zwischen "
            "Fuss und Kopf, die Querkraft vergrössert für Überfestigkeit und höhere "
            "Eigenformen (95) – hier nicht gerechnet.")


def gewicht(G_k: float, Q_k: float, psi_2: float) -> float:
    """
    Was von einem Geschoss im Beben mitschwingt: W = G_k + psi_2 Q_k
    (16.5.2.3) -- SI. Die Rechnung nimmt es von hier, das Bild eines
    Gebaeudes, das noch nicht rechnet, auch (:mod:`opencivil.web.erdbebendaten`).
    """
    return G_k + psi_2 * Q_k


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


def traegheit(richtung: str) -> str:
    """
    Welches Traegheitsmoment des Kerns eine Kraft in ``richtung`` biegt: in x
    ``I_z``, in y ``I_y`` -- y der Querschnittsanalyse liegt in x des Gebaeudes.
    """
    return "I_z" if richtung == "x" else "I_y"


class Schwingzeit(Wahl):
    """Woher die Grundschwingzeit kommt."""

    KERN = "kern"
    HAND = "hand"

    @property
    def beschriftung(self) -> str:
        return {Schwingzeit.KERN: "aus dem Kern", Schwingzeit.HAND: "von Hand"}[self]

    @property
    def erklaerung(self) -> str:
        return {
            Schwingzeit.KERN: "T₁ = 2·√u: u ist die Auslenkung des Dachs, wenn die Gewichte "
                              "der Geschosse waagrecht auf den Kern wirken (40)",
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
KERN = "Kern"

#: Die Vorgaben jedes Geschosses, je mit seiner Nummer von unten: Hoehe und
#: Lasten, dann was von seinem Kern gilt -- je eine Kachel der Maske.
JE_GESCHOSS = (Gruppe(GESCHOSS, lambda: (
    Feld("h", "h", M, "Höhe des Geschosses", 2, schritt=0.1,
         hinweis="von Decke zu Decke, das unterste ab der Einspannung"),
    Feld("G_k", "G_k", KN, "Ständige Last des Geschosses", 0, f"{SIA}, 16.5.2.3", schritt=100,
         hinweis="was mit seiner Decke schwingt: Decke, halbe Wände darüber und darunter, Ausbau"),
    Feld("Q_k", "Q_k", KN, "Nutzlast des Geschosses", 0, f"{SIA}, 16.5.2.3", schritt=100),
    Feld("psi_2", r"\psi_2", EINHEITSLOS, "Beiwert der Nutzlast, quasi-ständig", 1,
         "SIA 260:2013, Anhang A, Tabelle 2", schritt=0.1,
         hinweis="Wohn- und Büroflächen 0.3; Versammlung und Verkauf 0.6; Lager 0.8; Dächer 0"),
)), Gruppe(KERN, lambda: (
    Feld("eta_EI", r"\eta_{EI}", EINHEITSLOS, "Anteil der ungerissenen Biegesteifigkeit", 2,
         ZIFFER_STEIFIGKEIT, schritt=0.05,
         hinweis="0.5 nach Vorgabe – verlangt ist eine mittlere Steifigkeit bis zum "
                 "Fliessbeginn"),
)))


# ===========================================================================
# Das Gebaeude
# ===========================================================================


@dataclass(frozen=True)
class Geschoss:
    """Ein Geschoss, von unten gezaehlt: Hoehe, Lasten und sein Kern."""

    name: str
    h: Groesse
    G_k: Groesse
    Q_k: Groesse
    psi_2: Groesse
    eta_EI: Groesse
    kern: Optional[str] = None
    """Die Kennung der Querschnittsanalyse seines Kerns -- ``None`` ohne Kern."""


@dataclass
class Gebaeude(Rechenobjekt):
    """
    Ein Gebaeude im Erdbeben: die Eingaben als Vorgaben im Rechenwerk, dazu
    je Kern seine Traegheitsmomente (:class:`~.kern.Kern`). Die Geschosse
    liegen von unten nach oben; ``kerne`` sind nur die, die rechnen -- ihre
    Querschnittsanalyse rechnet und hat einen Beton.
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
    kerne: Mapping[str, Kerndaten]
    """Je Kennung einer Querschnittsanalyse, die ein Geschoss als Kern nimmt, was sie gibt."""

    praefix: str

    definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)
    berechnungen: List[Berechnung] = field(default_factory=list, init=False)
    kernrechnungen: Dict[str, Kern] = field(default_factory=dict, init=False)
    """Je Kern seine Traegheitsmomente -- unter dem Gebaeude, in seiner Herleitung."""

    def __post_init__(self) -> None:
        self.id = self.praefix
        for gruppe in VORGABEN:
            for f in gruppe.fuer(self):
                self._vorgabe(f, gruppe.titel, getattr(self, f.kurz))
        for i, geschoss in enumerate(self.geschosse, start=1):
            for gruppe in JE_GESCHOSS:
                for f in gruppe.fuer(geschoss):
                    self._vorgabe(f.nummeriert(i), f"{GESCHOSS} {i}: {geschoss.name}",
                                  getattr(geschoss, f.kurz))
        for kennung, daten in self.kerne.items():
            self.kernrechnungen[kennung] = Kern(f"{self.id}.kern.{kennung}", daten,
                                                self.abschnitt)
            self.berechnungen.append(self.kernrechnungen[kennung])

    @property
    def mit_kern(self) -> bool:
        """Ob die Geschosse einen Kern haben -- dann jedes, sonst rechnet das Gebaeude nicht."""
        return any(g.kern is not None for g in self.geschosse)

    @property
    def fusskern(self) -> Optional[Kern]:
        """Der Kern des untersten Geschosses -- auf ihn verteilen sich die Kraefte am Fuss."""
        kern = self.geschosse[0].kern if self.geschosse else None
        return None if kern is None else self.kernrechnungen[kern]

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
class Kernanteil:
    """Was ein getrennter Teil des Kerns am Fuss in einer Richtung traegt; SI-Einheiten."""

    nummer: int
    """Sein Platz unter den Teilen, ab 1 (:class:`~.kern.Kernteil`)."""

    I: float  # noqa: E741 -- so heisst das Traegheitsmoment
    """Sein Traegheitsmoment in dieser Richtung, um seinen eigenen Schwerpunkt, m⁴."""

    anteil: float
    """Sein Anteil an EI am Fuss -- E_cm und eta_EI gelten fuer alle Teile gleich."""

    V: float
    """Die Querkraft am Fuss, N."""

    M: float
    """Das Moment am Fuss, N m."""


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

    EI: Tuple[float, ...]
    """Je Geschoss, von unten, die Biegesteifigkeit seines Kerns, N m² -- leer ohne Kern."""

    teile: Tuple[Kernanteil, ...]
    """Je getrenntem Teil des Kerns am Fuss, was er traegt -- leer, wo er zusammenhaengt."""


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
    Was die Rechnung grau dazu sagt: je Kern, dessen y und z keine
    Hauptachsen sind, ein Satz -- und wo q duktiles Verhalten heisst, was das
    fuer die Waende bedeutet.
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
        for i, g in enumerate(gebaeude.geschosse, start=1):
            if g.kern is not None:
                kern = gebaeude.kernrechnungen[g.kern]
                bezuege += [Eingabebezug(f"{k}_{i}", d.id) for k, d in kern.d.items()]
                bezuege.append(Eingabebezug(f"E_cm_{i}", gebaeude.kerne[g.kern].E_cm))
        fuss = gebaeude.fusskern
        for k, teil in enumerate(fuss.je_teil if fuss is not None else (), start=1):
            bezuege += [Eingabebezug(f"{n}_teil_{k}", d.id) for n, d in teil.items()]
        super().__init__(basis, ausgaben=list(self.d_grad.values()), bezuege=bezuege,
                         titel=f"Ersatzkraftverfahren – {gebaeude.name}",
                         abschnitt=gebaeude.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Ersatzkraftverfahren")
        p.erklaerung(
            "Das Beben wird durch waagrechte Kräfte ersetzt: je Hauptrichtung eine "
            "Ersatzkraft aus dem Bemessungsspektrum bei der Grundschwingzeit, verteilt auf "
            "die Geschosse nach Höhe und Gewicht. Der Kern trägt sie als Kragarm, eingespannt "
            "am Fuss, in jedem Geschoss mit dessen Biegesteifigkeit; getrennte Teile am Fuss "
            "je nach ihrem Anteil daran."
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
            W.append(gewicht(e.g(f"G_k_{i}").si, e.g(f"Q_k_{i}").si, e.g(f"psi_2_{i}").si))
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
        Je Kern, dessen y und z merklich keine Hauptachsen sind, der Hinweis --
        derselbe wie im Raum
        (:func:`~opencivil.stabwerk.stabquerschnitt.keine_hauptachsen`), mit den
        Summen ueber seine Teile.
        """
        saetze: Dict[str, Optional[str]] = {}
        for i, g in enumerate(self.gebaeude.geschosse, start=1):
            if g.kern is None or g.kern in saetze:
                continue
            saetze[g.kern] = text = keine_hauptachsen(
                f"Querschnittsanalyse «{self.gebaeude.kerne[g.kern].analyse}»",
                *(self.e.g(f"{k}_{i}").si for k in ("I_y", "I_z", "I_yz")), was="den Kern")
            if text is not None:
                self.p.hinweis(text)
        return tuple(text for text in saetze.values() if text is not None)

    def duktil(self) -> Tuple[str, ...]:
        """
        Der Hinweis zu duktil bemessenen Waenden (:func:`duktile_waende`) --
        nur mit Kern, und in der Herleitung mit dem q, das ihn ausloest.
        """
        q = {r: self.e[f"q_{r}"].groesse.si for r in RICHTUNGEN}
        duktil = [r for r in RICHTUNGEN if q[r] > Q_NICHT_DUKTIL]
        if not duktil or not self.gebaeude.mit_kern:
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
        EI = self._steifigkeit(r)
        T1, u = self._schwingzeit(r, EI)
        if T1 is None:
            return None
        self.T1[r] = T1
        S_d = self._spektrum(r, T1, self.e[f"q_{r}"], "")
        F_d, kraefte, M_0 = self._kraefte(r, S_d)
        anteile = self._teile(r, F_d.groesse.si, M_0.groesse.si)
        F_d_1, M_0_1, S_d_1 = self._kippen(r, T1, F_d.groesse.si, M_0.groesse.si)
        return Richtungsbefund(
            richtung=r, T1=T1.groesse.si, u=u, S_d=S_d.groesse.si, F_d=F_d.groesse.si,
            kraefte=tuple(kraefte), M_0=M_0.groesse.si, S_d_1=S_d_1, F_d_1=F_d_1, M_0_1=M_0_1,
            EI=tuple(EI or ()), teile=anteile)

    def _steifigkeit(self, r: str) -> Optional[List[float]]:
        """Je Geschoss, von unten, EI seines Kerns in ``r``, in N m² -- ``None`` ohne Kern."""
        e, p, g = self.e, self.p, self.gebaeude
        if not g.mit_kern:
            return None
        I = traegheit(r)  # noqa: E741 -- so heisst das Traegheitsmoment
        EI: List[float] = []
        zeilen: List[List[Zelle]] = []
        for i, s in enumerate(g.geschosse, start=1):
            werte = [e.g(f"{n}_{i}").si for n in (I, "E_cm", "eta_EI")]
            EI.append(math.prod(werte))
            zeilen.append([f"{i}: {s.name}", g.kerne[s.kern].analyse, Mathe(fest(werte[0], 4)),
                           Mathe(fest(werte[1] / 1e6, 0)), Mathe(fest(werte[2], 2)),
                           Mathe(fest(EI[-1] / 1e6, 0))])
        p.ansatz(r"EI_i = \eta_{EI,i} \cdot E_{cm,i} \cdot I_i",
                 titel="Biegesteifigkeit des Kerns in einem Geschoss",
                 referenz=f"{ZIFFER_STEIFIGKEIT}; {NACH_VORGABE}",
                 name="Biegesteifigkeit des Kerns")
        zeichen = f"{I[0]}_{I[2:]}"
        p.tabelle(
            kopf=[GESCHOSS, KERN, Mathe(rf"{zeichen}\ [\mathrm{{m}}^4]"),
                  Mathe(r"E_{cm}\ [\mathrm{N/mm^2}]"), Mathe(r"\eta_{EI}"),
                  Mathe(r"EI\ [\mathrm{MNm^2}]")],
            zeilen=zeilen, ausrichtung="llrrrr",
            titel=f"Biegesteifigkeit des Kerns in {r}, von unten – eine Kraft in {r} biegt ihn "
                  f"um {I[2:]}, mit {zeichen}")
        return EI

    def _schwingzeit(self, r: str,
                     EI: Optional[List[float]]) -> Tuple[Optional[Wert], Optional[float]]:
        """T_1 von Hand oder aus dem Kern (40) -- ohne Kern keine; dazu u in m."""
        p, werte = self.p, self.werte
        if self.gebaeude.schwingzeit is Schwingzeit.HAND:
            T1 = self.e[f"T1_{r}"]
            p.wert(T1, titel=f"Grundschwingzeit in {r}, von Hand", referenz=f"{SIA}, 16.5.2.2")
            return T1, None
        if EI is None:
            p.text(f"In {r} trägt kein Kern: ohne Steifigkeit keine Grundschwingzeit und "
                   f"keine Ersatzkraft.")
            return None, None
        teile = beitraege(self.z, self.W, EI)
        p.ansatz(r"\Delta u_i = \frac{h_i}{6 \cdot EI_i} \cdot \left(M_{u,i} \cdot "
                 r"(2 \cdot a_{u,i} + a_{o,i}) + M_{o,i} \cdot (a_{u,i} + 2 \cdot a_{o,i})"
                 r"\right) \qquad a = H - z",
                 titel="Auslenkung des Dachs aus einem Geschoss – nach dem Arbeitssatz, M aus "
                       "den Gewichten, a aus einer Kraft 1 am Dach",
                 referenz=f"{ZIFFER_T1}; {NACH_VORGABE}", name="Auslenkung aus einem Geschoss")
        p.tabelle(
            kopf=[GESCHOSS, Mathe(r"h\ [\mathrm{m}]"), Mathe(r"EI\ [\mathrm{MNm^2}]"),
                  Mathe(r"M_u\ [\mathrm{kNm}]"), Mathe(r"M_o\ [\mathrm{kNm}]"),
                  Mathe(r"a_u\ [\mathrm{m}]"), Mathe(r"a_o\ [\mathrm{m}]"),
                  Mathe(r"\Delta u\ [\mathrm{mm}]")],
            zeilen=[[f"{i}: {s.name}", Mathe(fest(b.h, 2)), Mathe(fest(b.EI / 1e6, 0)),
                     Mathe(fest(b.M_u / 1e3, 0)), Mathe(fest(b.M_o / 1e3, 0)),
                     Mathe(fest(b.a_u, 2)), Mathe(fest(b.a_o, 2)), Mathe(fest(b.du * 1e3, 2))]
                    for i, (s, b) in enumerate(zip(self.gebaeude.geschosse, teile), start=1)],
            titel=f"Auslenkung je Geschoss in {r}, von unten – u: an der Decke darunter, o: an "
                  f"seiner", ausrichtung="lrrrrrrr")
        u_si = sum(b.du for b in teile)
        u = werte.wert(f"u_{r}", f"u_{r}", Groesse.aus_si(u_si, MM), 1,
                       f"Auslenkung des Dachs in {r}")
        p.formel(u, r"\sum_i \Delta u_i", {},
                 titel=f"Auslenkung des Dachs, die Gewichte waagrecht in {r} auf den Kern",
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

    def _teile(self, r: str, F_d: float, M_0: float) -> Tuple[Kernanteil, ...]:
        """
        Je getrenntem Teil des Kerns am Fuss sein Anteil an EI -- und so viel
        von Querkraft und Moment dort. Leer, wo der Kern am Fuss
        zusammenhaengt; ohne Kern bleiben die Kraefte ohne Verteilung.
        """
        kern = self.gebaeude.fusskern
        if kern is None:
            self.p.text(f"In {r} trägt kein Kern: die Kräfte bleiben ohne Verteilung.")
            return ()
        I = [self.e.g(f"{traegheit(r)}_teil_{k}").si  # noqa: E741
             for k in range(1, len(kern.je_teil) + 1)]
        anteile = tuple(Kernanteil(nummer=k, I=I_k, anteil=I_k / sum(I), V=I_k / sum(I) * F_d,
                                   M=I_k / sum(I) * M_0)
                        for k, I_k in enumerate(I, start=1))
        if anteile:
            zeichen = f"I_{traegheit(r)[2:]}"
            self.p.tabelle(
                kopf=["Teil", Mathe(rf"{zeichen}\ [\mathrm{{m}}^4]"),
                      Mathe(rf"{zeichen} / \sum {zeichen}"), Mathe(r"V\ [\mathrm{kN}]"),
                      Mathe(r"M\ [\mathrm{kNm}]")],
                zeilen=[[str(a.nummer), Mathe(fest(a.I, 4)), Mathe(fest(a.anteil, 3)),
                         Mathe(fest(a.V / 1e3, 1)), Mathe(fest(a.M / 1e3, 0))] for a in anteile],
                titel=f"Je Teil des Kerns am Fuss in {r} – nach seinem Anteil an der "
                      f"Biegesteifigkeit; E_cm und η_EI gelten für alle gleich ({NACH_VORGABE})",
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
