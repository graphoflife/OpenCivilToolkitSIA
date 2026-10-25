"""
opencivil/querschnitt/platte.py -- Stahlbeton-Plattenquerschnitt.

VERANTWORTUNG:
Beschreibt die Geometrie einer Platte und erzeugt daraus die Berechnungen fuer
Bewehrungsquerschnitte und statische Hoehen. Wie der Lagenaufbau Tiefe und
Querschnitt je Posten rechnet und wie ein Posten zu den Nachweisen reist,
steht in :mod:`opencivil.querschnitt.lagenaufbau`.

AUFBAU -- VIER LAGEN:
Eine Platte hat vier Bewehrungslagen, von unten nach oben durchgezaehlt::

    Überdeckung oben
        4. Lage      Richtung waehlbar
        3. Lage      Gegenrichtung zur 4. Lage
        ---- Plattenmitte ----
        2. Lage      Gegenrichtung zur 1. Lage
        1. Lage      Richtung waehlbar
    Überdeckung unten

Jede Lage besteht aus einer **Grundbewehrung** und einer optionalen **Zulage**.
Beide liegen auf derselben Hoehe -- sie beruehren dieselbe Huellebene und sind
je um ihren eigenen Halbmesser eingerueckt. Die Huelle fuer die naechste Lage
richtet sich nach dem groesseren der beiden Durchmesser.

X UND Y SIND GETRENNTE TRAGRICHTUNGEN:
Bewehrung in y-Richtung traegt nichts zum Momentenwiderstand um die x-Achse bei.
Deshalb liefert :meth:`Plattenquerschnitt.lagen_in_richtung` die Lagen je
Richtung, und der Nachweis wird je Richtung eigens gefuehrt.

Z-ACHSE:
``z`` wird von der Oberkante nach unten gemessen, 0 <= z <= h. Damit gilt fuer
alle Lagen dieselbe Rechnung, und die Interaktionsrechnung braucht keine
Sonderfaelle. Die statische Hoehe einer unteren Lage ist ihr ``z``, die einer
oberen ``h - z`` (:func:`~opencivil.querschnitt.lagenaufbau.statische_hoehe`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterator, List, Optional, Tuple

from opencivil.core.berechnung import Berechnung, Eingabebezug, Formel, Vorgabe
from opencivil.core.einheiten import (
    EINHEITSLOS, GRAD, KG_PRO_M3, MM, MM2, Groesse,
)
from opencivil.core.protokoll import Abschnitt
from opencivil.core.wahl import Wahl
from opencivil.core.wert import Kennzahl, WertDef, kennung_aus
from opencivil.material.basis import Baustoff
from opencivil.material.betonstahl import STAHLDICHTE
from opencivil.querschnitt.lagenaufbau import Lagenaufbau, Postenbezug
from opencivil.querschnitt.zugseite import Zugseite

#: Anzahl Lagen einer Platte. Bewusst fest -- eine Platte hat unten und oben je
#: eine Haupt- und eine Querlage, mehr braucht es nicht, weniger waere ein
#: Sonderfall mit leeren Lagen.
LAGENZAHL = 4

#: Breite, auf die sich eine y-Lage bezieht: in y wird immer je Laufmeter
#: gerechnet, ``b`` ist der Streifen in x.
BREITE_Y_MM = 1000.0



class Richtung(Wahl):
    """Tragrichtung einer Bewehrungslage."""

    X = "x"
    Y = "y"

    @property
    def gegenrichtung(self) -> "Richtung":
        return Richtung.Y if self is Richtung.X else Richtung.X

    @property
    def beschriftung(self) -> str:
        return "x-Richtung" if self is Richtung.X else "y-Richtung"

    @property
    def breite(self) -> str:
        """
        Der Name der Breite, je die in dieser Richtung gerechnet wird: ``b``
        in x, ``b_y`` in y -- in y stets je Laufmeter (:data:`BREITE_Y_MM`).
        """
        return "b" if self is Richtung.X else "b_y"


class Postenart(str, Enum):
    """Grundbewehrung oder Zulage innerhalb einer Lage."""

    GRUND = "grund"
    ZULAGE = "zulage"

    def __str__(self) -> str:
        return self.value

    @property
    def beschriftung(self) -> str:
        return "Grundbewehrung" if self is Postenart.GRUND else "Zulage"

    @property
    def kuerzel(self) -> str:
        return "g" if self is Postenart.GRUND else "z"


# ===========================================================================
# Bewehrung
# ===========================================================================


@dataclass
class Bewehrungsposten:
    """
    Ein Satz gleicher Staebe innerhalb einer Lage.

    Die Menge wird entweder ueber die Teilung (Regelfall bei Platten) oder ueber
    die Stabzahl angegeben. Ein Durchmesser von null bedeutet: nicht vorhanden.
    """

    durchmesser: Groesse = field(default_factory=lambda: Groesse(0, MM))
    abstand: Optional[Groesse] = None
    anzahl: Optional[float] = None

    @property
    def vorhanden(self) -> bool:
        if self.durchmesser.si <= 0:
            return False
        if self.abstand is not None:
            return self.abstand.si > 0
        return bool(self.anzahl and self.anzahl > 0)

    @property
    def ueber_abstand(self) -> bool:
        return self.abstand is not None

    def flaeche(self, b: Groesse) -> Groesse:
        """Bewehrungsquerschnitt, bezogen auf die Breite ``b``."""
        if not self.vorhanden:
            return Groesse(0, MM2)
        einzeln = math.pi * self.durchmesser * self.durchmesser / 4.0
        if self.ueber_abstand:
            return einzeln * (b / self.abstand)
        return einzeln * float(self.anzahl)

    def menge_text(self) -> str:
        if not self.vorhanden:
            return "—"
        if self.ueber_abstand:
            return f"⌀{self.durchmesser.formatiert(0)}@{self.abstand.formatiert(0)}"
        return f"{self.anzahl:g}⌀{self.durchmesser.formatiert(0)}"


@dataclass
class Bewehrungslage:
    """Eine der vier Lagen, bestehend aus Grundbewehrung und Zulage."""

    nummer: int
    """1 = unterste Lage, 4 = oberste."""

    richtung: Richtung
    stahl: Baustoff
    grund: Bewehrungsposten = field(default_factory=Bewehrungsposten)
    zulage: Bewehrungsposten = field(default_factory=Bewehrungsposten)

    unguenstig: bool = True
    """
    Wie Grundbewehrung und Zulage innerhalb der Lage liegen.

    ``False`` (guenstig): beide beruehren dieselbe Huellebene und sind je um
    ihren eigenen Halbmesser eingerueckt -- die **aeusseren** Kanten fluchten.
    Das ist die guenstigste Anordnung; der duennere Stab bekommt den groessten
    Hebelarm.

    ``True`` (unguenstig, Vorgabe): die **inneren** Kanten fluchten, der
    duennere Stab wird also zur Plattenmitte hin geschoben. Bei den unteren
    Lagen heisst das: gleiche Oberkante; bei den oberen: gleiche Unterkante.
    Massgebend ist je der dickere Stab. Auf der Baustelle laesst sich nicht
    steuern, welche Kante fluchtet -- deshalb ist das die Vorgabe.
    """

    def __post_init__(self) -> None:
        if not 1 <= self.nummer <= LAGENZAHL:
            raise ValueError(f"Lagennummer {self.nummer} liegt ausserhalb 1..{LAGENZAHL}.")

    @property
    def von_unten(self) -> bool:
        """Lagen 1 und 2 werden von der Unterkante aus gestapelt."""
        return self.nummer <= 2

    @property
    def seite(self) -> Zugseite:
        """Die Seite, an der sie liegt -- und die ein Moment ziehen muss, damit sie traegt."""
        return Zugseite.UNTEN if self.von_unten else Zugseite.OBEN

    @property
    def stapelrang(self) -> int:
        """0 = aussen (direkt auf der Überdeckung), 1 = darüber."""
        return self.nummer - 1 if self.von_unten else LAGENZAHL - self.nummer

    @property
    def vorhanden(self) -> bool:
        return self.grund.vorhanden or self.zulage.vorhanden

    @property
    def groesster_durchmesser(self) -> Groesse:
        vorhandene = [p.durchmesser for p in self.posten() if p.vorhanden]
        return max(vorhandene) if vorhandene else Groesse(0, MM)

    def posten(self) -> Iterator[Bewehrungsposten]:
        yield self.grund
        yield self.zulage

    def benannte_posten(self) -> Iterator[Tuple[Postenart, Bewehrungsposten]]:
        yield Postenart.GRUND, self.grund
        yield Postenart.ZULAGE, self.zulage

    def beschriftung(self) -> str:
        return f"{self.nummer}. Lage ({self.seite.value}, {self.richtung.beschriftung})"

    @property
    def index(self) -> str:
        """Der Symbolindex der Lage, z.B. ``1,x`` -- der eines Postens haengt die Art an."""
        return f"{self.nummer},{self.richtung.value}"


#: Vorgabe fuer die Neigung der Druckdiagonalen, in Grad.
ALPHA_MIN = 30
ALPHA_MAX = 45

#: Bei einer Normalzugkraft steilt sich die Druckdiagonale auf. Beide Grenzen
#: werden dann auf mindestens diesen Wert gehoben.
ALPHA_ZUG = 40

#: Vorgabe fuer den Abminderungsbeiwert der Betondruckfestigkeit in der
#: Druckdiagonalen.
K_C = 0.55

@dataclass
class Querkraftbewehrung:
    """
    Bügelbewehrung einer Platte -- ein Raster über die ganze Fläche.

    Ein Durchmesser, eine Teilung in x und eine in y. In y darf statt der
    Teilung eine Stabzahl über die betrachtete Breite ``b`` stehen; in x
    nicht. Der Widerstand bezieht sich auf den Laufmeter in Tragrichtung, und
    eine Stabzahl in x hätte darin keinen Bezug -- wer sie angibt, bekommt
    deshalb nur noch Nachweise in x-Richtung.

    ``alpha_min`` und ``alpha_max`` begrenzen die Neigung der Druckdiagonalen.
    Gesucht wird darin ganzgradig die Neigung mit dem grössten Widerstand;
    Zwischenwerte sind eine Genauigkeit, die das Fachwerkmodell nicht hergibt.
    """

    durchmesser: Groesse = field(default_factory=lambda: Groesse(0, MM))
    stahl: Optional[Baustoff] = None
    abstand_x: Optional[Groesse] = None
    abstand_y: Optional[Groesse] = None
    anzahl_y: Optional[float] = None
    alpha_min: int = ALPHA_MIN
    alpha_max: int = ALPHA_MAX

    @property
    def vorhanden(self) -> bool:
        if self.durchmesser.si <= 0:
            return False
        if self.abstand_x is None or self.abstand_x.si <= 0:
            return False
        return self.ueber_abstand_y or bool(self.anzahl_y and self.anzahl_y > 0)

    @property
    def ueber_abstand_y(self) -> bool:
        """Ob die Menge in y über die Teilung angegeben ist (statt über die Zahl)."""
        return self.abstand_y is not None and self.abstand_y.si > 0

    @property
    def flaeche(self) -> Groesse:
        """Querschnitt **eines** Bügelschenkels."""
        if not self.vorhanden:
            return Groesse(0, MM2)
        return math.pi * self.durchmesser * self.durchmesser / 4.0

    def menge_text(self) -> str:
        if not self.vorhanden:
            return "—"
        y = (f"{self.abstand_y.formatiert(0)} mm" if self.ueber_abstand_y
             else f"{self.anzahl_y:g} Stk")
        return (f"⌀{self.durchmesser.formatiert(0)}, "
                f"x: {self.abstand_x.formatiert(0)} mm, y: {y}")

    def grenzen(self, zugkraft: bool) -> Tuple[int, int]:
        """Die beiden Grenzwinkel in Grad -- siehe :func:`druckfeldgrenzen`."""
        return druckfeldgrenzen(self.alpha_min, self.alpha_max, zugkraft)


def druckfeldgrenzen(alpha_min: int, alpha_max: int, zugkraft: bool) -> Tuple[int, int]:
    """
    Die beiden Grenzwinkel der Druckdiagonalen in Grad, angepasst an das
    Vorzeichen von ``N_Ed`` -- fuer die Buegel der Platte wie fuer die
    Schubwaende der Querschnittsanalyse.

    Bei Normalzug steilt sich die Druckdiagonale auf: ``alpha_min`` wird auf
    40° gesetzt und ``alpha_max`` notfalls mitgehoben, damit der Bereich
    nicht leer wird.
    """
    if not zugkraft:
        return alpha_min, alpha_max
    return ALPHA_ZUG, max(alpha_max, ALPHA_ZUG)


# ===========================================================================
# Plattenquerschnitt
# ===========================================================================


#: Die beiden Kaesten, in denen die Plattenangaben zusammenstehen. Der erste
#: traegt die Betonsorte im Namen: sie ist keine gerechnete Groesse und hat
#: darum keine eigene Kette, an der sie haengen koennte -- als Aufschrift des
#: Kastens gilt sie dagegen immer, denn eine Platte hat genau einen Beton.
UEBERDECKUNGEN = "Überdeckungen"


def _abmessungen(beton_name: str) -> str:
    return f"Abmessungen – Beton {beton_name}" if beton_name else "Abmessungen"


@dataclass
class Plattenquerschnitt:
    """
    Stahlbeton-Platte mit vier Bewehrungslagen.

    ``b`` ist die betrachtete Breite; bei Platten ueblicherweise 1 m, dann sind
    alle Schnittgroessen Werte pro Laufmeter.
    """

    name: str
    h: Groesse
    b: Groesse
    beton: Baustoff
    lagen: List[Bewehrungslage] = field(default_factory=list)
    ueberdeckung_unten: Groesse = field(default_factory=lambda: Groesse(30, MM))
    ueberdeckung_oben: Groesse = field(default_factory=lambda: Groesse(30, MM))
    d_max: Groesse = field(default_factory=lambda: Groesse(32, MM))
    """Grösstkorndurchmesser -- geht in den Querkraftwiderstand ein."""

    einlagenhoehe: Groesse = field(default_factory=lambda: Groesse(0, MM))
    """Höhe einer Einlage; verringert den Hebelarm d_v, wenn h/6 < e < d."""

    k_c: Groesse = field(default_factory=lambda: Groesse(K_C, EINHEITSLOS))
    """Abminderung der Betondruckfestigkeit in der Druckdiagonalen."""

    querkraftbewehrung: Optional[Querkraftbewehrung] = None
    """Bügel, sofern welche angegeben sind. ``None`` heisst: ohne."""

    praefix: Optional[str] = None

    definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)
    berechnungen: List[Berechnung] = field(default_factory=list, init=False)
    posten: List[Postenbezug] = field(default_factory=list, init=False)
    """Die vorhandenen Posten, von der 1. Lage an, je Lage erst die Grundbewehrung."""

    def __post_init__(self) -> None:
        if len(self.lagen) != LAGENZAHL:
            raise ValueError(
                f"Querschnitt '{self.name}': es müssen genau {LAGENZAHL} Lagen "
                f"angegeben werden, erhalten: {len(self.lagen)}."
            )
        for erwartet, lage in enumerate(self.lagen, start=1):
            if lage.nummer != erwartet:
                raise ValueError(
                    f"Querschnitt '{self.name}': die Lagen müssen von 1 bis "
                    f"{LAGENZAHL} durchnummeriert sein."
                )
        # Die Richtungen der Paare (1,2) und (3,4) muessen entgegengesetzt sein.
        for unten, oben in ((0, 1), (3, 2)):
            if self.lagen[unten].richtung is self.lagen[oben].richtung:
                raise ValueError(
                    f"Querschnitt '{self.name}': die {self.lagen[unten].nummer}. und "
                    f"die {self.lagen[oben].nummer}. Lage müssen entgegengesetzte "
                    f"Richtungen haben."
                )
        if not any(l.vorhanden for l in self.lagen):
            raise ValueError(
                f"Querschnitt '{self.name}': ohne Bewehrung lässt sich kein "
                f"Widerstand bestimmen."
            )
        self.id = self.praefix or f"querschnitt.{kennung_aus(self.name)}"
        self._aufbauen()

    # -- Zugriff ------------------------------------------------------------

    def id_von(self, kurzname: str) -> str:
        if kurzname not in self.definitionen:
            raise KeyError(
                f"Querschnitt '{self.name}' kennt '{kurzname}' nicht. "
                f"Bekannt: {sorted(self.definitionen)}."
            )
        return self.definitionen[kurzname].id

    def id_breite(self, richtung: Richtung) -> str:
        """
        Kennung der Breite, die fuer diese Tragrichtung gilt.

        Eine Platte wird in y stets je Laufmeter nachgewiesen -- die Angabe
        ``b`` beschreibt den Streifen in x. Wer beides dieselbe Breite nehmen
        laesst, bekommt bei b != 1000 mm in y einen Widerstand, der zur
        eingegebenen Bewehrung nicht passt.
        """
        return self.id_von(richtung.breite)

    def lagen_in_richtung(self, richtung: Richtung) -> List[Bewehrungslage]:
        return [l for l in self.lagen if l.richtung is richtung and l.vorhanden]

    def posten_in_richtung(self, richtung: Richtung) -> List[Postenbezug]:
        return [q for q in self.posten if q.lage.richtung is richtung]

    def posten_der_lage(self, lage: Bewehrungslage) -> List[Postenbezug]:
        """Grundbewehrung und Zulage der Lage, soweit vorhanden."""
        return [q for q in self.posten if q.lage.nummer == lage.nummer]

    @property
    def richtungen_mit_bewehrung(self) -> List[Richtung]:
        return [r for r in Richtung if self.posten_in_richtung(r)]

    @property
    def staehle(self) -> List[Baustoff]:
        gesehen: Dict[str, Baustoff] = {}
        for q in self.posten:
            gesehen.setdefault(q.lage.stahl.id, q.lage.stahl)
        return list(gesehen.values())

    def ins_rechenwerk(self, werk) -> "Plattenquerschnitt":
        self.beton.ins_rechenwerk(werk)
        for stahl in self.staehle:
            stahl.ins_rechenwerk(werk)
        werk.definiere(*self.definitionen.values())
        werk.registriere(*self.berechnungen)
        return self

    # -- Aufbau -------------------------------------------------------------

    def _def(self, kurzname: str, symbol: str, einheit, beschreibung: str,
             stellen: int = 1, referenz: str = "") -> WertDef:
        d = WertDef(
            id=f"{self.id}.{kurzname}", symbol=symbol, einheit=einheit,
            beschreibung=beschreibung, referenz=referenz, stellen=stellen,
        )
        self.definitionen[kurzname] = d
        return d

    @property
    def abschnitt(self) -> Abschnitt:
        """Ueberschrift, unter der die ganze Platte in der Herleitung steht."""
        return Abschnitt(f"Plattenanalyse: {self.name}", self.id, thema="Querschnitt")

    def _aufbauen(self) -> None:
        d_h = self._def("h", "h", MM, "Plattendicke", 0)
        d_b = self._def("b", "b", MM, "Betrachtete Breite (x)", 0)
        d_b_y = self._def("b_y", "b_y", MM, "Betrachtete Breite (y)", 0)
        d_cu = self._def("c_nom_unten", "c_{nom,u}", MM, "Überdeckung unten", 0)
        d_co = self._def("c_nom_oben", "c_{nom,o}", MM, "Überdeckung oben", 0)
        d_dmax = self._def("D_max", "D_{max}", MM, "Grösstkorndurchmesser", 0)
        d_einl = self._def("einlagenhoehe", "e_{Einlage}", MM, "Höhe der Einlage", 0)

        abschnitt = self.abschnitt
        self.berechnungen += [
            # Grösstkorn und Einlagenhöhe gehen nur in den Querkraftnachweis
            # ein und stehen darum dort, bei den Grössen, die sie erklären --
            # nicht verwaist am Anfang der Plattenanalyse.
            Vorgabe(id=f"{self.id}.D_max", ausgabe=d_dmax, groesse=self.d_max,
                    abschnitt=abschnitt, stumm=True),
            Vorgabe(id=f"{self.id}.einlagenhoehe", ausgabe=d_einl,
                    groesse=self.einlagenhoehe, abschnitt=abschnitt, stumm=True),
            # Zwei Kaesten statt vier Einzelzeilen: die Abmessungen gehoeren
            # zusammen, die Ueberdeckungen auch. Jede Vorgabe bleibt dabei ihr
            # eigener Knoten -- nur so zeigt der Kasten bei einer
            # Rueckverfolgung genau die Angaben, die dafuer gebraucht wurden.
            Vorgabe(id=f"{self.id}.h", ausgabe=d_h, groesse=self.h,
                    abschnitt=abschnitt, gruppe=_abmessungen(self.beton.name)),
            Vorgabe(id=f"{self.id}.b", ausgabe=d_b, groesse=self.b,
                    abschnitt=abschnitt, gruppe=_abmessungen(self.beton.name)),
            # Die Breite in y ist keine Eingabe, sondern die Festlegung, dass in
            # y je Laufmeter gerechnet wird. Sie steht trotzdem im Protokoll:
            # eine stille Festlegung waere genau die Art Zahl, die man spaeter
            # in keiner Herleitung wiederfindet.
            Vorgabe(id=f"{self.id}.b_y", ausgabe=d_b_y,
                    groesse=Groesse(BREITE_Y_MM, MM), abschnitt=abschnitt,
                    gruppe=_abmessungen(self.beton.name)),
            Vorgabe(id=f"{self.id}.c_nom_unten", ausgabe=d_cu,
                    groesse=self.ueberdeckung_unten, abschnitt=abschnitt,
                    gruppe=UEBERDECKUNGEN),
            Vorgabe(id=f"{self.id}.c_nom_oben", ausgabe=d_co,
                    groesse=self.ueberdeckung_oben, abschnitt=abschnitt,
                    gruppe=UEBERDECKUNGEN),
        ]

        self._querkraftbewehrung_aufbauen(abschnitt)

        self.d_bewehrungsmass = self._def(
            "bewehrungsmass", r"\mu_s", KG_PRO_M3,
            "Bewehrungsmass je Kubikmeter Beton", 0)
        self.d_distanzhalter = self._def(
            "distanzhalter", "h_{Dist}", MM,
            "Höhe der Distanzhalter (OK innere untere bis UK innere obere Lage)", 1)
        #: Was der Lagenaufbau beschreibt, gleich welche Lastfaelle es gibt.
        self.kennzahlen: List[Kennzahl] = [
            Kennzahl(self.d_bewehrungsmass, "Bewehrungsmass",
                     f"Stahldichte {STAHLDICHTE:g} kg/m³"),
            Kennzahl(self.d_distanzhalter, "Höhe der Distanzhalter",
                     "OK innere untere Lage bis UK innere obere Lage"),
        ]

        aufbau_ausgaben: List[WertDef] = [self.d_bewehrungsmass, self.d_distanzhalter]
        aufbau_bezuege = [
            Eingabebezug("h", d_h.id),
            Eingabebezug("b", d_b.id),
            Eingabebezug("b_y", d_b_y.id),
            Eingabebezug("c_nom_unten", d_cu.id),
            Eingabebezug("c_nom_oben", d_co.id),
        ]

        for lage in self.lagen:
            for art, posten in lage.benannte_posten():
                if not posten.vorhanden:
                    continue
                marke = f"{lage.nummer}{art.kuerzel}"
                index = f"{lage.index},{art.kuerzel}"
                bezeichnung = f"{lage.nummer}. Lage {art.beschriftung}"

                # Durchmesser und Teilung stehen in der Lagentabelle, Spalte
                # für Spalte. Ein eigener Block je Posten gäbe bei vier Lagen
                # bis zu sechzehn Zeilen der Form 's = 150 mm' -- dieselben
                # Zahlen ein zweites Mal, nur schlechter zu vergleichen.
                d_phi = self._def(
                    f"lage.{marke}.phi", rf"\varnothing_{{{index}}}", MM,
                    f"Stabdurchmesser {bezeichnung}", 0)
                self.berechnungen.append(
                    Vorgabe(id=f"{self.id}.lage.{marke}.phi", ausgabe=d_phi,
                            groesse=posten.durchmesser, abschnitt=abschnitt,
                            stumm=True))

                if posten.ueber_abstand:
                    d_s = self._def(f"lage.{marke}.s", f"s_{{{index}}}", MM,
                                    f"Teilung {bezeichnung}", 0)
                    self.berechnungen.append(
                        Vorgabe(id=f"{self.id}.lage.{marke}.s", ausgabe=d_s,
                                groesse=posten.abstand, abschnitt=abschnitt,
                                stumm=True))

                d_as = self._def(
                    f"lage.{marke}.a_s", f"A_{{s,{index}}}", MM2,
                    f"Bewehrungsquerschnitt {bezeichnung}", 0,
                    referenz="SIA 262:2025, 5.5.2")
                # Die Tiefe ab Oberkante, nicht die statische Hoehe: bei einer
                # oberen Lage misst die ab der Unterkante. Mit «d» hiess eine
                # obere Lage hier 48 mm, im Nachweis darunter 252 mm.
                d_z = self._def(
                    f"lage.{marke}.z", f"z_{{{index}}}", MM,
                    f"Tiefe {bezeichnung} ab Oberkante", 1)

                q = Postenbezug(lage, art, posten, marke=marke, index=index,
                                bezeichnung=bezeichnung, phi_def=d_phi, as_def=d_as, z_def=d_z)
                aufbau_bezuege += q.bezuege("phi")
                if posten.ueber_abstand:
                    aufbau_bezuege.append(Eingabebezug(q.name("s"), d_s.id))
                aufbau_ausgaben += [d_z, d_as]
                self.posten.append(q)

        self.berechnungen.append(
            Lagenaufbau(
                id=f"{self.id}.lagenaufbau",
                ausgaben=aufbau_ausgaben,
                bezuege=aufbau_bezuege,
                posten=self.posten,
                d_bewehrungsmass=self.d_bewehrungsmass,
                d_distanzhalter=self.d_distanzhalter,
                abschnitt=abschnitt,
            ))

    # -- Querkraftbewehrung -------------------------------------------------

    @property
    def hat_buegel(self) -> bool:
        return bool(self.querkraftbewehrung and self.querkraftbewehrung.vorhanden)

    def _querkraftbewehrung_aufbauen(self, abschnitt: Abschnitt) -> None:
        """
        Die Werte der Bügel -- Durchmesser, Teilungen, Grenzwinkel, k_c.

        ``k_c`` entsteht auch ohne Bügel: er gehört zur Platte, nicht zur
        Bewehrung, und eine Vorgabe, die je nach Eingabe da ist oder nicht,
        macht die Rückverfolgung von der Bestückung abhängig.

        Der Bügelquerschnitt ist eine **Formel** und keine Vorgabe: er wird aus
        dem Durchmesser gerechnet, und wer ihn nachrechnen will, soll die
        Rechnung sehen statt nur die Zahl.
        """
        d_kc = self._def("k_c", "k_c", EINHEITSLOS,
                         "Abminderung der Betondruckfestigkeit in der Druckdiagonalen", 2)
        self.berechnungen.append(
            Vorgabe(id=f"{self.id}.k_c", ausgabe=d_kc, groesse=self.k_c,
                    abschnitt=abschnitt, stumm=True))

        buegel = self.querkraftbewehrung
        if buegel is None or not buegel.vorhanden:
            return

        gruppe = "Querkraftbewehrung"
        d_phi = self._def("querkraft.phi", r"\varnothing_{V}", MM,
                          "Bügeldurchmesser", 0)
        d_sx = self._def("querkraft.s_x", "s_{V,x}", MM,
                         "Bügelteilung in x-Richtung", 0)
        d_amin = self._def("querkraft.alpha_min", r"\alpha_{min}", GRAD,
                           "Kleinste Neigung der Druckdiagonalen", 0)
        d_amax = self._def("querkraft.alpha_max", r"\alpha_{max}", GRAD,
                           "Grösste Neigung der Druckdiagonalen", 0)

        self.berechnungen += [
            Vorgabe(id=f"{self.id}.querkraft.phi", ausgabe=d_phi,
                    groesse=buegel.durchmesser, abschnitt=abschnitt, gruppe=gruppe),
            Vorgabe(id=f"{self.id}.querkraft.s_x", ausgabe=d_sx,
                    groesse=buegel.abstand_x, abschnitt=abschnitt, gruppe=gruppe),
        ]
        if buegel.ueber_abstand_y:
            d_y = self._def("querkraft.s_y", "s_{V,y}", MM,
                            "Bügelteilung in y-Richtung", 0)
            menge_y = buegel.abstand_y
        else:
            d_y = self._def("querkraft.n_y", "n_{V,y}", EINHEITSLOS,
                            "Bügelzahl über die betrachtete Breite", 0)
            menge_y = Groesse(float(buegel.anzahl_y), EINHEITSLOS)
        self.berechnungen += [
            Vorgabe(id=f"{self.id}.{'querkraft.s_y' if buegel.ueber_abstand_y else 'querkraft.n_y'}",
                    ausgabe=d_y, groesse=menge_y, abschnitt=abschnitt, gruppe=gruppe),
            Vorgabe(id=f"{self.id}.querkraft.alpha_min", ausgabe=d_amin,
                    groesse=Groesse(buegel.alpha_min, GRAD), abschnitt=abschnitt,
                    gruppe=gruppe),
            Vorgabe(id=f"{self.id}.querkraft.alpha_max", ausgabe=d_amax,
                    groesse=Groesse(buegel.alpha_max, GRAD), abschnitt=abschnitt,
                    gruppe=gruppe),
        ]

        d_as = self._def("querkraft.a_s", r"A_{\varnothing,V}", MM2,
                         "Querschnitt eines Bügelschenkels", 1,
                         referenz="SIA 262:2025, 5.5.2")
        self.berechnungen.append(
            Formel(
                id=f"{self.id}.querkraft.a_s",
                ausgabe=d_as,
                eingaben={"phi": d_phi.id},
                vorlage=r"\frac{\pi \cdot \left(@phi\right)^{2}}{4}",
                funktion=lambda phi: math.pi * phi * phi / 4.0,
                titel="Querschnitt eines Bügelschenkels",
                abschnitt=abschnitt,
            ))

    def __repr__(self) -> str:
        return (f"Plattenquerschnitt({self.name!r}, h={self.h}, b={self.b}, "
                f"{len(self.posten)} Bewehrungsposten)")
