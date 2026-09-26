"""
opencivil/querschnitt/platte.py -- Stahlbeton-Plattenquerschnitt.

VERANTWORTUNG:
Beschreibt die Geometrie einer Platte und erzeugt daraus die Berechnungen fuer
Bewehrungsquerschnitte und statische Hoehen.

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
``z`` wird von der Oberkante nach unten gemessen, 0 <= z <= h. Die statische
Hoehe einer Bewehrung ist ihr ``z``. Damit gilt fuer alle Lagen dieselbe
Rechnung, und die Interaktionsrechnung braucht keine Sonderfaelle.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Berechnung, Eingabebezug, Eingaben, Formel, Prozedur, Vorgabe,
)
from opencivil.core.einheiten import (
    EINHEITSLOS, GRAD, KG_PRO_M3, MM, MM2, Groesse,
)
from opencivil.core.latex import Mathe
from opencivil.core.protokoll import Abschnitt, Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.material.basis import Baustoff

#: Anzahl Lagen einer Platte. Bewusst fest -- eine Platte hat unten und oben je
#: eine Haupt- und eine Querlage, mehr braucht es nicht, weniger waere ein
#: Sonderfall mit leeren Lagen.
LAGENZAHL = 4

#: Breite, auf die sich eine y-Lage bezieht: in y wird immer je Laufmeter
#: gerechnet, ``b`` ist der Streifen in x.
BREITE_Y_MM = 1000.0

#: Rohdichte von Betonstahl, fuer das Bewehrungsmass.
STAHLDICHTE = 7850.0


class Richtung(str, Enum):
    """Tragrichtung einer Bewehrungslage."""

    X = "x"
    Y = "y"

    def __str__(self) -> str:
        return self.value

    @property
    def gegenrichtung(self) -> "Richtung":
        return Richtung.Y if self is Richtung.X else Richtung.X

    @property
    def beschriftung(self) -> str:
        return "x-Richtung" if self is Richtung.X else "y-Richtung"


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
        seite = "unten" if self.von_unten else "oben"
        return f"{self.nummer}. Lage ({seite}, {self.richtung.beschriftung})"


#: Vorgabe fuer die Neigung der Druckdiagonalen, in Grad.
ALPHA_MIN = 30
ALPHA_MAX = 45

#: Bei einer Normalzugkraft steilt sich die Druckdiagonale auf. Beide Grenzen
#: werden dann auf mindestens diesen Wert gehoben.
ALPHA_ZUG = 40

#: Vorgabe fuer den Abminderungsbeiwert der Betondruckfestigkeit in der
#: Druckdiagonalen.
K_C = 0.55

#: Vorgabe fuer die Kriechzahl phi. Sie beschreibt Klima und Belastungsalter --
#: eine Annahme ueber das Bauwerk, keine Materialgroesse.
KRIECHZAHL = 2.0


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
        """
        Die beiden Grenzwinkel in Grad, angepasst an das Vorzeichen von ``N_Ed``.

        Bei Normalzug steilt sich die Druckdiagonale auf: ``alpha_min`` wird auf
        40° gesetzt und ``alpha_max`` notfalls mitgehoben, damit der Bereich
        nicht leer wird.
        """
        if not zugkraft:
            return self.alpha_min, self.alpha_max
        return ALPHA_ZUG, max(self.alpha_max, ALPHA_ZUG)


# ===========================================================================
# Lagenaufbau
# ===========================================================================


#: Die beiden Kaesten, in denen die Plattenangaben zusammenstehen. Der erste
#: traegt die Betonsorte im Namen: sie ist keine gerechnete Groesse und hat
#: darum keine eigene Kette, an der sie haengen koennte -- als Aufschrift des
#: Kastens gilt sie dagegen immer, denn eine Platte hat genau einen Beton.
UEBERDECKUNGEN = "Überdeckungen"


def _abmessungen(beton_name: str) -> str:
    return f"Abmessungen – Beton {beton_name}" if beton_name else "Abmessungen"


def posten_index(lage: "Bewehrungslage", art: Postenart) -> str:
    """
    Der Symbolindex eines Bewehrungspostens, z.B. ``1,x,g``.

    Lage, Richtung, Art -- in dieser Reihenfolge, und immer alle drei. Damit ist
    jedes Symbol eindeutig, auch wenn zwei Lagen dieselbe Richtung tragen.

    Steht hier und nirgends sonst: die Handrechnung braucht denselben Index für
    ihre zusammengefassten Lagen, und zwei Stellen mit derselben Formel laufen
    früher oder später auseinander.
    """
    return f"{lage.nummer},{lage.richtung.value},{art.kuerzel}"


def lagenindex(eintraege: Sequence[Tuple]) -> str:
    """
    Der Symbolindex einer Lage aus ihren Posten -- ``1,x`` statt ``1,x,g``.

    Gerechnet wird mit der ganzen Lage, nicht mit einem Posten; ein
    Postenindex am Symbol behauptete etwas anderes. Hat die Lage nur einen
    Posten, ist dessen Index auch ihrer -- dann heisst ``A_s`` so wie in der
    Tabelle der Platte. ``eintraege`` sind Zeilen aus ``posten_ids``.
    """
    if not eintraege:
        return ""
    lage, art, *_ = eintraege[0]
    if len(eintraege) == 1:
        return posten_index(lage, art)
    return f"{lage.nummer},{lage.richtung.value}"


def protokoll_lage(
    p: Protokoll, e: Eingaben, werte: Zwischenwerte, eintraege: Sequence[Tuple],
    *, a_s: float, z: Optional[float] = None, d: float = 0.0,
) -> Tuple[Wert, Optional[Wert]]:
    """
    Querschnitt und statische Hoehe einer Lage, aus ihren Posten hergeleitet.

    ``eintraege`` sind die Zeilen der Lage aus ``posten_ids``; die Eingaben
    der Posten heissen ``a_s_<marke>`` und ``z_<marke>`` (Tiefe ab
    Oberkante), die Dicke ``h``. Liegen Grundbewehrung und Zulage in der Lage,
    stehen Summe und gemeinsamer Schwerpunkt da -- sonst fiele der
    Schwerpunkt vom Himmel. Ohne ``z`` nur der Querschnitt. Zurueck kommen
    ``A_s`` und ``d`` fuer die Formeln danach.
    """
    lage = eintraege[0][0]
    index = lagenindex(eintraege)
    marken = [f"{lage.nummer}{art.kuerzel}" for _, art, *_ in eintraege]
    eingaben = {f"a{i}": e[f"a_s_{m}"] for i, m in enumerate(marken)}
    summe = " + ".join(f"@{name}" for name in eingaben)
    flaeche = werte.flaeche("A_s", f"A_{{s,{index}}}", a_s)
    if len(marken) > 1:
        p.formel(flaeche, summe, eingaben, titel="Bewehrung der Lage")
    if z is None:
        return flaeche, None

    if len(marken) > 1:
        tiefe = werte.laenge("z", f"z_{{{index}}}", z)
        eingaben.update({f"z{i}": e[f"z_{m}"] for i, m in enumerate(marken)})
        momente = " + ".join(rf"@a{i} \cdot @z{i}" for i in range(len(marken)))
        p.formel(tiefe, rf"\frac{{{momente}}}{{{summe}}}", eingaben,
                 titel="Gemeinsamer Schwerpunkt der Lage")
    else:
        tiefe = e[f"z_{marken[0]}"]
    hoehe = werte.laenge("d", f"d_{{{index}}}", d)
    protokoll_statische_hoehe(p, hoehe, h=e["h"], z=tiefe, von_unten=lage.von_unten)
    return flaeche, hoehe


def protokoll_statische_hoehe(
    p: Protokoll, d: Wert, *, h: Wert, z: Wert, von_unten: bool,
) -> None:
    """
    Die statische Hoehe einer gezogenen Lage, gemessen ab dem gedrueckten Rand.

    Eine untere Lage misst ab der Oberkante, ``d = z``; eine obere ab der
    Unterkante, ``d = h - z``. Mehrere Nachweise brauchen diese Zeile -- steht
    sie an einer Stelle, sagt «unten» in allen dasselbe.
    """
    seite, rand = ("unten", "oben") if von_unten else ("oben", "unten")
    vorlage, eingaben = (("@z", {"z": z}) if von_unten
                         else ("@h - @z", {"h": h, "z": z}))
    p.formel(d, vorlage, eingaben,
             titel=f"Statische Höhe der Lage {seite}, ab dem gedrückten Rand {rand}")


@dataclass(frozen=True)
class Postenbezug:
    """Ein Bewehrungsposten samt der Werte, die der Lagenaufbau fuer ihn liefert."""

    lage: Bewehrungslage
    art: Postenart
    posten: Bewehrungsposten
    marke: str
    """Kurzform fuer die Eingabenamen, z.B. ``1g``."""

    z_def: WertDef
    as_def: WertDef


class Lagenaufbau(Prozedur):
    """
    Bestimmt statische Hoehe und Bewehrungsquerschnitt aller Posten.

    Beides in einem Zug und in einer Tabelle. Frueher stand fuer jeden Posten
    eine eigene Flaechenformel in der Herleitung -- fuenf Lagen ergaben fuenf
    gleich aussehende Bloecke, in denen sich nur die Zahlen unterschieden. Die
    Formel steht jetzt einmal da, die Ergebnisse stehen in der Tabelle.

    STAPELUNG:
    Die Lagen werden je Seite von aussen nach innen gestapelt. Die Huelle einer
    Lage beginnt bei der Ueberdeckung und waechst um den groessten Durchmesser
    der davorliegenden Lage. ``d`` wird von der gezogenen Randfaser aus
    gemessen -- bei den unteren Lagen von der Unterkante, bei den oberen von
    der Oberkante.

    Wie Grundbewehrung und Zulage innerhalb einer Lage zueinander liegen, sagt
    :attr:`Bewehrungslage.unguenstig`.
    """

    def __init__(
        self,
        id: str,
        *,
        ausgaben: Sequence[WertDef],
        bezuege: Sequence[Eingabebezug],
        posten: Sequence["Postenbezug"],
        d_bewehrungsmass: WertDef,
        d_distanzhalter: WertDef,
        titel: str = "Bewehrungslagen",
        abschnitt: Optional[Abschnitt] = None,
    ) -> None:
        super().__init__(id, ausgaben=ausgaben, bezuege=bezuege, titel=titel,
                         referenz="SIA 262:2025, 5.2.2", abschnitt=abschnitt)
        self.posten = list(posten)
        self.d_bewehrungsmass = d_bewehrungsmass
        self.d_distanzhalter = d_distanzhalter

    def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]:
        h = e.g("h")
        b = e.g("b")
        b_y = e.g("b_y")
        # Die Teilung einer y-Lage ist auf den Laufmeter bezogen, die einer
        # x-Lage auf die eingegebene Breite. Wer hier eine einzige Breite
        # nimmt, rechnet bei b != 1000 mm die halbe oder doppelte y-Bewehrung.
        breite_von = lambda r: b if r is Richtung.X else b_y
        breiten: Dict[str, Groesse] = {}
        # Ohne erklaerende Vorrede: die Lagentabelle zeigt Randabstand und Tiefe
        # je Posten, und wie beides zustande kommt, steht in der Klassendoku.
        ueber_abstand = any(q.posten.ueber_abstand for q in self.posten)
        ueber_anzahl = any(not q.posten.ueber_abstand for q in self.posten)
        # Nur wenn alle Posten dieselbe Art der Mengenangabe verwenden, darf die
        # Grösse in die Kopfzeile. Sonst muss sie in jeder Zelle stehen.
        einheitlich = not (ueber_abstand and ueber_anzahl)
        if ueber_abstand:
            p.ansatz(
                r"A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}",
                titel="Bewehrungsquerschnitt über die Breite b",
                referenz="SIA 262:2025, 5.5.2")
        if ueber_anzahl:
            p.ansatz(
                r"A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot n",
                titel="Bewehrungsquerschnitt aus der Stabzahl",
                referenz="SIA 262:2025, 5.5.2")

        # Huellen je Seite, von aussen nach innen. Jede Lage kommt nur einmal
        # vor, auch wenn sie zwei Posten traegt -- nach Nummer entdoppelt, weil
        # Bewehrungslage als veraenderliche Datenklasse nicht hashbar ist.
        huelle = {True: e.g("c_nom_unten"), False: e.g("c_nom_oben")}
        lagen_nach_nummer = {q.lage.nummer: q.lage for q in self.posten}
        raender: Dict[Tuple[bool, int], Groesse] = {}
        for lage in sorted(lagen_nach_nummer.values(),
                           key=lambda l: (not l.von_unten, l.stapelrang)):
            schluessel = (lage.von_unten, lage.stapelrang)
            raender[schluessel] = huelle[lage.von_unten]
            huelle[lage.von_unten] = huelle[lage.von_unten] + lage.groesster_durchmesser

        # Der dickste Stab je Lage bestimmt, wo die innere Kante liegt.
        dickster: Dict[int, Groesse] = {}
        for q in self.posten:
            phi = e.g(f"phi_{q.marke}")
            vorher = dickster.get(q.lage.nummer)
            if vorher is None or phi.si > vorher.si:
                dickster[q.lage.nummer] = phi

        # Die Breite je Zeile nur, wo sie sich unterscheidet: x gilt je b, y
        # je Laufmeter. Bei b = 1000 mm stuende in jeder Zeile dieselbe Zahl.
        mit_breite = len({breite_von(q.lage.richtung).si for q in self.posten}) > 1

        ergebnis: Dict[str, Groesse] = {}
        zeilen: List[List[str]] = []
        #: Je Lagennummer die Ober- und Unterkante des Stahls, in m ab Oberkante.
        kanten: Dict[int, Tuple[float, float]] = {}
        for q in self.posten:
            phi = e.g(f"phi_{q.marke}")
            huellebene = raender[(q.lage.von_unten, q.lage.stapelrang)]
            if q.lage.unguenstig:
                # Innere Kanten fluchten: der dünnere Stab rückt zur Mitte.
                rand = huellebene + dickster[q.lage.nummer] - phi / 2.0
            else:
                # Äussere Kanten fluchten, jeder um seinen eigenen Halbmesser.
                rand = huellebene + phi / 2.0
            z = h - rand if q.lage.von_unten else rand

            oben, unten = z.si - phi.si / 2.0, z.si + phi.si / 2.0
            vorher = kanten.get(q.lage.nummer)
            kanten[q.lage.nummer] = (
                (min(oben, vorher[0]), max(unten, vorher[1])) if vorher
                else (oben, unten))

            b_q = breite_von(q.lage.richtung)
            breiten[q.as_def.id] = b_q
            if q.posten.ueber_abstand:
                s = e.g(f"s_{q.marke}")
                a_s = Groesse.aus_si(
                    math.pi * phi.si * phi.si / 4.0 * (b_q.si / s.si), MM2)
                # Bei gemischter Angabe muss in jeder Zelle stehen, um welche
                # Grösse es geht -- sonst liest man 150 und 7 in derselben
                # Spalte und weiss nicht, was gemeint ist.
                menge = Mathe(s.formatiert(0, MM) if einheitlich
                              else rf"s = {s.als_latex(0, MM)}")
            else:
                anzahl = float(q.posten.anzahl)
                a_s = Groesse.aus_si(math.pi * phi.si * phi.si / 4.0 * anzahl, MM2)
                menge = Mathe(f"{anzahl:g}" if einheitlich else f"n = {anzahl:g}")

            ergebnis[q.z_def.id] = z
            ergebnis[q.as_def.id] = a_s
            zeilen.append([
                f"{q.lage.nummer}. Lage {q.art.beschriftung}",
                q.lage.richtung.value,
                q.lage.stahl.name if q.lage.stahl else "–",
                Mathe(phi.formatiert(0, MM)),
                menge,
                *([Mathe(b_q.formatiert(0, MM))] if mit_breite else []),
                Mathe(rand.formatiert(1, MM)),
                Mathe(z.formatiert(1, MM)),
                Mathe(a_s.formatiert(0, MM2)),
            ])

        ergebnis.update(self._kennzahlen(p, e, h, b, ergebnis, kanten, breiten))

        if not einheitlich:
            mengenkopf = "Menge"
        elif ueber_abstand:
            mengenkopf = Mathe(r"s\ [\mathrm{mm}]")
        else:
            mengenkopf = Mathe("n")

        kopf = ["Bewehrung", "Richtung", "Stahl",
                Mathe(r"\varnothing\ [\mathrm{mm}]"), mengenkopf,
                *([Mathe(r"b\ [\mathrm{mm}]")] if mit_breite else []),
                "Randabstand [mm]",
                Mathe(r"z\ [\mathrm{mm}]"), Mathe(r"A_s\ [\mathrm{mm}^2]")]
        p.tabelle(
            kopf=kopf,
            zeilen=zeilen,
            titel="Randabstände, Tiefen ab Oberkante und Bewehrungsquerschnitte",
            ausrichtung="lll" + "r" * (len(kopf) - 3),
        )
        return ergebnis

    def _kennzahlen(
        self, p: Protokoll, e: Eingaben, h: Groesse, b: Groesse,
        flaechen: Mapping[str, Groesse], kanten: Mapping[int, Tuple[float, float]],
        breiten: Mapping[str, Groesse],
    ) -> Dict[str, Groesse]:
        """
        Bewehrungsmass und Hoehe der Distanzhalter.

        Beides sind Angaben fuer die Ausfuehrung, keine Nachweisgroessen -- sie
        gehoeren aber in den Kern und nicht in die Oberflaeche, damit sie in der
        Herleitung stehen und sich zurueckverfolgen lassen.
        """
        ergebnis: Dict[str, Groesse] = {}
        werte = Zwischenwerte(self.id)

        # Auf b bezogen: eine y-Lage steht je Laufmeter da, eine x-Lage je b.
        # Das Verhaeltnis b/b_q rechnet sie auf denselben Streifen um; sind alle
        # Breiten gleich, ist es die schlichte Summe.
        a_s_gesamt = sum(
            (flaechen[q.as_def.id].si * (b.si / breiten[q.as_def.id].si)
             for q in self.posten), 0.0)
        # Stahlvolumen je Betonvolumen: A_s * L * rho / (b * L * h) -- die Laenge
        # kuerzt sich heraus.
        mass = a_s_gesamt * STAHLDICHTE / (b.si * h.si)
        ergebnis[self.d_bewehrungsmass.id] = Groesse(mass, KG_PRO_M3)
        p.formel(
            self.d_bewehrungsmass.belegen(Groesse(mass, KG_PRO_M3)),
            rf"\frac{{@A_s \cdot {STAHLDICHTE:g}\,\mathrm{{kg}}/\mathrm{{m}}^{{3}}}}"
            rf"{{@b \cdot @h}}",
            {"A_s": werte.flaeche("A_s_gesamt", "A_{s,tot}", a_s_gesamt),
             "b": e["b"], "h": e["h"]},
            titel="Bewehrungsmass je Kubikmeter Beton",
        )

        # Die Distanzhalter stehen zwischen der innersten unteren und der
        # innersten oberen Lage. Fehlt die innere, gilt die aeussere.
        unten = kanten.get(2) or kanten.get(1)
        oben = kanten.get(3) or kanten.get(4)
        if unten is None or oben is None:
            # Eine deklarierte Ausgabe muss immer entstehen, sonst bricht der
            # Loeser ab. Ohne Bewehrung auf beiden Seiten gibt es nichts
            # abzustuetzen -- null ist hier die richtige Antwort, nicht "fehlt".
            ergebnis[self.d_distanzhalter.id] = Groesse(0, MM)
            p.text("Bewehrung nur auf einer Seite → keine Distanzhalter.")
            return ergebnis

        hoehe = unten[0] - oben[1]
        ergebnis[self.d_distanzhalter.id] = Groesse.aus_si(hoehe, MM)
        p.formel(
            self.d_distanzhalter.belegen(Groesse.aus_si(hoehe, MM)), "@OK - @UK",
            {"OK": werte.laenge("OK", r"\text{OK innere untere Lage}", unten[0]),
             "UK": werte.laenge("UK", r"\text{UK innere obere Lage}", oben[1])},
            titel="Höhe der Distanzhalter")
        return ergebnis


# ===========================================================================
# Plattenquerschnitt
# ===========================================================================


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

    kriechzahl: Groesse = field(default_factory=lambda: Groesse(KRIECHZAHL, EINHEITSLOS))
    """Kriechzahl phi -- geht ueber n = (E_s/E_cm)*(1+phi) in den Hebelarm ein."""

    querkraftbewehrung: Optional[Querkraftbewehrung] = None
    """Bügel, sofern welche angegeben sind. ``None`` heisst: ohne."""

    praefix: Optional[str] = None

    definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)
    berechnungen: List[Berechnung] = field(default_factory=list, init=False)
    posten_ids: List[Tuple[Bewehrungslage, Postenart, Bewehrungsposten, str, str]] = field(
        default_factory=list, init=False
    )
    """Je vorhandenem Posten: (Lage, Art, Posten, ID der Fläche, ID von z)."""

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
        return self.id_von("b" if richtung is Richtung.X else "b_y")

    def lagen_in_richtung(self, richtung: Richtung) -> List[Bewehrungslage]:
        return [l for l in self.lagen if l.richtung is richtung and l.vorhanden]

    def posten_in_richtung(
        self, richtung: Richtung
    ) -> List[Tuple[Bewehrungslage, Postenart, Bewehrungsposten, str, str]]:
        return [e for e in self.posten_ids if e[0].richtung is richtung]

    @property
    def richtungen_mit_bewehrung(self) -> List[Richtung]:
        return [r for r in Richtung if self.posten_in_richtung(r)]

    @property
    def staehle(self) -> List[Baustoff]:
        gesehen: Dict[str, Baustoff] = {}
        for lage, _, _, _, _ in self.posten_ids:
            gesehen.setdefault(lage.stahl.id, lage.stahl)
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

        aufbau_ausgaben: List[WertDef] = [self.d_bewehrungsmass, self.d_distanzhalter]
        aufbau_posten: List[Postenbezug] = []
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
                index = posten_index(lage, art)
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
                aufbau_bezuege.append(Eingabebezug(f"phi_{marke}", d_phi.id))

                if posten.ueber_abstand:
                    d_s = self._def(f"lage.{marke}.s", f"s_{{{index}}}", MM,
                                    f"Teilung {bezeichnung}", 0)
                    self.berechnungen.append(
                        Vorgabe(id=f"{self.id}.lage.{marke}.s", ausgabe=d_s,
                                groesse=posten.abstand, abschnitt=abschnitt,
                                stumm=True))
                    aufbau_bezuege.append(Eingabebezug(f"s_{marke}", d_s.id))

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

                aufbau_ausgaben += [d_z, d_as]
                aufbau_posten.append(Postenbezug(lage, art, posten, marke, d_z, d_as))
                self.posten_ids.append((lage, art, posten, d_as.id, d_z.id))

        self.berechnungen.append(
            Lagenaufbau(
                id=f"{self.id}.lagenaufbau",
                ausgaben=aufbau_ausgaben,
                bezuege=aufbau_bezuege,
                posten=aufbau_posten,
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
        d_phi = self._def("kriechzahl", r"\varphi", EINHEITSLOS,
                          "Kriechzahl", 2)
        self.berechnungen += [
            Vorgabe(id=f"{self.id}.k_c", ausgabe=d_kc, groesse=self.k_c,
                    abschnitt=abschnitt, stumm=True),
            # Wie k_c: sie steht dort, wo sie erklaert wird -- beim Nachweis,
            # der mit ihr rechnet, nicht verwaist am Anfang der Plattenanalyse.
            Vorgabe(id=f"{self.id}.kriechzahl", ausgabe=d_phi,
                    groesse=self.kriechzahl, abschnitt=abschnitt, stumm=True),
        ]

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
                f"{len(self.posten_ids)} Bewehrungsposten)")
