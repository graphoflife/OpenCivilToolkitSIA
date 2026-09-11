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
from opencivil.core.einheiten import EINHEITSLOS, MM, MM2, Groesse
from opencivil.core.latex import als_text
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.material.basis import Baustoff

#: Anzahl Lagen einer Platte. Bewusst fest -- eine Platte hat unten und oben je
#: eine Haupt- und eine Querlage, mehr braucht es nicht, weniger waere ein
#: Sonderfall mit leeren Lagen.
LAGENZAHL = 4


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


# ===========================================================================
# Lagenaufbau
# ===========================================================================


@dataclass(frozen=True)
class Postenbezug:
    """Ein Bewehrungsposten samt der Werte, die der Lagenaufbau fuer ihn liefert."""

    lage: Bewehrungslage
    art: Postenart
    posten: Bewehrungsposten
    marke: str
    """Kurzform fuer die Eingabenamen, z.B. ``1g``."""

    d_def: WertDef
    as_def: WertDef


class Lagenaufbau(Prozedur):
    """
    Bestimmt statische Hoehe und Bewehrungsquerschnitt aller Posten.

    Beides in einem Zug und in einer Tabelle. Frueher stand fuer jeden Posten
    eine eigene Flaechenformel in der Herleitung -- fuenf Lagen ergaben fuenf
    gleich aussehende Bloecke, in denen sich nur die Zahlen unterschieden. Die
    Formel steht jetzt einmal da, die Ergebnisse stehen in der Tabelle.
    """

    def __init__(
        self,
        id: str,
        *,
        ausgaben: Sequence[WertDef],
        bezuege: Sequence[Eingabebezug],
        posten: Sequence["Postenbezug"],
        titel: str = "Bewehrungslagen",
        abschnitt: str = "",
    ) -> None:
        super().__init__(id, ausgaben=ausgaben, bezuege=bezuege, titel=titel,
                         referenz="SIA 262:2025, 5.2.2", abschnitt=abschnitt)
        self.posten = list(posten)

    def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]:
        h = e.g("h")
        b = e.g("b")
        p.text(
            "Die Lagen werden je Seite von aussen nach innen gestapelt. Die Hülle "
            "einer Lage beginnt bei der Überdeckung und wächst um den grössten "
            "Durchmesser der davorliegenden Lage. Grundbewehrung und Zulage einer "
            "Lage liegen auf derselben Hülle und sind je um ihren eigenen "
            "Halbmesser eingerückt. d wird von der gezogenen Randfaser aus "
            "gemessen, hier von der Oberkante nach unten."
        )

        ueber_abstand = any(q.posten.ueber_abstand for q in self.posten)
        ueber_anzahl = any(not q.posten.ueber_abstand for q in self.posten)
        # Nur wenn alle Posten dieselbe Art der Mengenangabe verwenden, darf die
        # Grösse in die Kopfzeile. Sonst muss sie in jeder Zelle stehen.
        einheitlich = not (ueber_abstand and ueber_anzahl)
        if ueber_abstand:
            p.gleichung(
                r"A_s = \frac{\pi \cdot \varnothing^{2}}{4} \cdot \frac{b}{s}",
                titel="Bewehrungsquerschnitt je Laufmeter",
                referenz="SIA 262:2025, 5.5.2")
        if ueber_anzahl:
            p.gleichung(
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

        ergebnis: Dict[str, Groesse] = {}
        zeilen: List[List[str]] = []
        for q in self.posten:
            phi = e.g(f"phi_{q.marke}")
            rand = raender[(q.lage.von_unten, q.lage.stapelrang)] + phi / 2.0
            d = h - rand if q.lage.von_unten else rand

            if q.posten.ueber_abstand:
                s = e.g(f"s_{q.marke}")
                a_s = Groesse.aus_si(
                    math.pi * phi.si * phi.si / 4.0 * (b.si / s.si), MM2)
                # Bei gemischter Angabe muss in jeder Zelle stehen, um welche
                # Grösse es geht -- sonst liest man 150 und 7 in derselben
                # Spalte und weiss nicht, was gemeint ist.
                menge = s.formatiert(0, MM) if einheitlich else rf"s = {s.als_latex(0, MM)}"
            else:
                anzahl = float(q.posten.anzahl)
                a_s = Groesse.aus_si(math.pi * phi.si * phi.si / 4.0 * anzahl, MM2)
                menge = f"{anzahl:g}" if einheitlich else f"n = {anzahl:g}"

            ergebnis[q.d_def.id] = d
            ergebnis[q.as_def.id] = a_s
            zeilen.append([
                als_text(f"{q.lage.nummer}. Lage {q.art.beschriftung}"),
                als_text(q.lage.richtung.value),
                als_text(q.lage.stahl.name if q.lage.stahl else "–"),
                phi.formatiert(0, MM),
                menge,
                rand.formatiert(1, MM),
                d.formatiert(1, MM),
                a_s.formatiert(0, MM2),
            ])

        if not einheitlich:
            mengenkopf = r"\text{Menge}"
        elif ueber_abstand:
            mengenkopf = r"s\ [\mathrm{mm}]"
        else:
            mengenkopf = r"n"

        p.tabelle(
            kopf=[r"\text{Bewehrung}", r"\text{Richtung}", r"\text{Stahl}",
                  r"\varnothing\ [\mathrm{mm}]", mengenkopf,
                  r"\text{Randabstand}\ [\mathrm{mm}]",
                  r"d\ [\mathrm{mm}]", r"A_s\ [\mathrm{mm}^2]"],
            zeilen=zeilen,
            titel="Randabstände, statische Höhen und Bewehrungsquerschnitte",
            ausrichtung="lllrrrrr",
        )
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
        self.id = self.praefix or f"querschnitt.{_kennung(self.name)}"
        self._aufbauen()

    # -- Zugriff ------------------------------------------------------------

    def id_von(self, kurzname: str) -> str:
        if kurzname not in self.definitionen:
            raise KeyError(
                f"Querschnitt '{self.name}' kennt '{kurzname}' nicht. "
                f"Bekannt: {sorted(self.definitionen)}."
            )
        return self.definitionen[kurzname].id

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
    def abschnitt(self) -> str:
        """Ueberschrift, unter der die ganze Platte in der Herleitung steht."""
        return f"Plattenanalyse: {self.name}"

    def _aufbauen(self) -> None:
        d_h = self._def("h", "h", MM, "Plattendicke", 0)
        d_b = self._def("b", "b", MM, "Betrachtete Breite", 0)
        d_cu = self._def("c_nom_unten", "c_{nom,u}", MM, "Überdeckung unten", 0)
        d_co = self._def("c_nom_oben", "c_{nom,o}", MM, "Überdeckung oben", 0)
        d_dmax = self._def("D_max", "D_{max}", MM, "Grösstkorndurchmesser", 0)
        d_einl = self._def("einlagenhoehe", "e_{Einlage}", MM, "Höhe der Einlage", 0)

        abschnitt = self.abschnitt
        self.berechnungen += [
            Vorgabe(id=f"{self.id}.D_max", ausgabe=d_dmax, groesse=self.d_max,
                    abschnitt=abschnitt),
            Vorgabe(id=f"{self.id}.einlagenhoehe", ausgabe=d_einl,
                    groesse=self.einlagenhoehe, abschnitt=abschnitt),
            Vorgabe(id=f"{self.id}.h", ausgabe=d_h, groesse=self.h, abschnitt=abschnitt),
            Vorgabe(id=f"{self.id}.b", ausgabe=d_b, groesse=self.b, abschnitt=abschnitt),
            Vorgabe(id=f"{self.id}.c_nom_unten", ausgabe=d_cu,
                    groesse=self.ueberdeckung_unten, abschnitt=abschnitt),
            Vorgabe(id=f"{self.id}.c_nom_oben", ausgabe=d_co,
                    groesse=self.ueberdeckung_oben, abschnitt=abschnitt),
        ]

        aufbau_ausgaben: List[WertDef] = []
        aufbau_posten: List[Postenbezug] = []
        aufbau_bezuege = [
            Eingabebezug("h", d_h.id),
            Eingabebezug("b", d_b.id),
            Eingabebezug("c_nom_unten", d_cu.id),
            Eingabebezug("c_nom_oben", d_co.id),
        ]

        for lage in self.lagen:
            for art, posten in lage.benannte_posten():
                if not posten.vorhanden:
                    continue
                marke = f"{lage.nummer}{art.kuerzel}"
                # Lage, Richtung, Art -- in dieser Reihenfolge, und immer alle
                # drei. Damit ist jedes Symbol eindeutig, auch wenn zwei Lagen
                # dieselbe Richtung tragen.
                index = f"{lage.nummer},{lage.richtung.value},{art.kuerzel}"
                bezeichnung = f"{lage.nummer}. Lage {art.beschriftung}"

                d_phi = self._def(
                    f"lage.{marke}.phi", rf"\varnothing_{{{index}}}", MM,
                    f"Stabdurchmesser {bezeichnung}", 0)
                self.berechnungen.append(
                    Vorgabe(id=f"{self.id}.lage.{marke}.phi", ausgabe=d_phi,
                            groesse=posten.durchmesser, abschnitt=abschnitt))
                aufbau_bezuege.append(Eingabebezug(f"phi_{marke}", d_phi.id))

                if posten.ueber_abstand:
                    d_s = self._def(f"lage.{marke}.s", f"s_{{{index}}}", MM,
                                    f"Teilung {bezeichnung}", 0)
                    self.berechnungen.append(
                        Vorgabe(id=f"{self.id}.lage.{marke}.s", ausgabe=d_s,
                                groesse=posten.abstand, abschnitt=abschnitt))
                    aufbau_bezuege.append(Eingabebezug(f"s_{marke}", d_s.id))

                d_as = self._def(
                    f"lage.{marke}.a_s", f"A_{{s,{index}}}", MM2,
                    f"Bewehrungsquerschnitt {bezeichnung}", 0,
                    referenz="SIA 262:2025, 5.5.2")
                d_d = self._def(
                    f"lage.{marke}.z", f"d_{{{index}}}", MM,
                    f"Statische Höhe {bezeichnung} (ab Oberkante)", 1)

                aufbau_ausgaben += [d_d, d_as]
                aufbau_posten.append(Postenbezug(lage, art, posten, marke, d_d, d_as))
                self.posten_ids.append((lage, art, posten, d_as.id, d_d.id))

        self.berechnungen.append(
            Lagenaufbau(
                id=f"{self.id}.lagenaufbau",
                ausgaben=aufbau_ausgaben,
                bezuege=aufbau_bezuege,
                posten=aufbau_posten,
                abschnitt=abschnitt,
            ))

    def __repr__(self) -> str:
        return (f"Plattenquerschnitt({self.name!r}, h={self.h}, b={self.b}, "
                f"{len(self.posten_ids)} Bewehrungsposten)")


def _kennung(text: str) -> str:
    ersetzt = text.replace("/", "_").replace(" ", "_").replace(".", "_")
    return "".join(z for z in ersetzt if z.isalnum() or z == "_")
