"""
opencivil/querschnitt/platte.py -- Plattenquerschnitt mit Bewehrungslagen.

VERANTWORTUNG:
Beschreibt die Geometrie eines Plattenquerschnitts und erzeugt daraus die
Berechnungen fuer Bewehrungsquerschnitte und statische Hoehen.

VORZEICHEN UND ACHSEN:
``z`` wird von der Oberkante nach unten gemessen, 0 <= z <= h. Die statische
Hoehe einer Lage ist ihr ``z``, also der Abstand ihres Schwerpunkts von der
Oberkante. Damit gilt fuer alle Lagen -- oben wie unten -- dieselbe Rechnung,
und die Interaktionsrechnung braucht keine Sonderfaelle.

LAGENAUFBAU:
Die Lagen werden von der jeweiligen Aussenseite nach innen aufgezaehlt. Der
Randabstand einer Lage ergibt sich aus der Ueberdeckung, den davor liegenden
Stabdurchmessern und den lichten Abstaenden. Das ist eine echte Abfolge und
darum eine :class:`Prozedur` -- ihr Ablauf erscheint im Bericht als Tabelle,
statt als undurchsichtige Zahl.

EIGENSTAENDIG NUTZBAR::

    platte = Plattenquerschnitt(
        name="Decke", h=Groesse(300, MM), b=Groesse(1000, MM), beton=c30,
        lagen_unten=[Bewehrungslage(Groesse(18, MM), b500b, abstand=Groesse(150, MM))],
    )
    platte.ins_rechenwerk(werk)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import (
    Berechnung, Eingabebezug, Eingaben, Formel, Prozedur, Vorgabe,
)
from opencivil.core.einheiten import EINHEITSLOS, MM, MM2, Groesse
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import WertDef
from opencivil.material.basis import Baustoff


class Seite(str, Enum):
    """Welcher Querschnittsrand -- bestimmt, von wo aus gestapelt wird."""

    UNTEN = "unten"
    OBEN = "oben"

    def __str__(self) -> str:
        return self.value

    @property
    def kuerzel(self) -> str:
        return "u" if self is Seite.UNTEN else "o"

    @property
    def beschriftung(self) -> str:
        return "unten" if self is Seite.UNTEN else "oben"


# ===========================================================================
# Bewehrungslage
# ===========================================================================


@dataclass
class Bewehrungslage:
    """
    Eine Lage gleicher Staebe.

    Die Menge wird entweder ueber den Stababstand (Regelfall bei Platten) oder
    ueber die Stabzahl angegeben -- genau eines von beiden.
    """

    durchmesser: Groesse
    stahl: Baustoff
    abstand: Optional[Groesse] = None
    """Stababstand s. Die Bewehrung wird dann auf die Breite b bezogen."""

    anzahl: Optional[float] = None
    """Stabzahl auf der Breite b."""

    lichter_abstand: Groesse = field(default_factory=lambda: Groesse(0, MM))
    """Lichter Abstand zur davorliegenden Lage."""

    bezeichnung: str = ""

    def __post_init__(self) -> None:
        if (self.abstand is None) == (self.anzahl is None):
            raise ValueError(
                "Bewehrungslage: genau eines von 'abstand' oder 'anzahl' angeben."
            )
        if self.durchmesser.si <= 0:
            raise ValueError("Bewehrungslage: der Durchmesser muss positiv sein.")

    @property
    def ueber_abstand(self) -> bool:
        return self.abstand is not None

    def flaeche(self, b: Groesse) -> Groesse:
        """Bewehrungsquerschnitt der Lage, bezogen auf die Breite ``b``."""
        einzelflaeche = math.pi * self.durchmesser * self.durchmesser / 4.0
        if self.ueber_abstand:
            return einzelflaeche * (b / self.abstand)
        return einzelflaeche * self.anzahl

    def beschriftung(self, nummer: int, seite: Seite) -> str:
        if self.bezeichnung:
            return self.bezeichnung
        menge = (
            f"⌀{self.durchmesser.formatiert(0)}@{self.abstand.formatiert(0)}"
            if self.ueber_abstand
            else f"{self.anzahl:g}⌀{self.durchmesser.formatiert(0)}"
        )
        return f"Lage {nummer} {seite.beschriftung} ({menge})"


# ===========================================================================
# Lagenaufbau
# ===========================================================================


class Lagenaufbau(Prozedur):
    """
    Bestimmt die statischen Hoehen aller Lagen aus Ueberdeckung und Stapelung.

    Ausgabe ist fuer jede Lage ihr ``z`` -- der Abstand des Stabschwerpunkts von
    der Oberkante. Der Ablauf wird als Tabelle mitgeschrieben, damit jede Zahl
    von Hand nachgerechnet werden kann.
    """

    def __init__(
        self,
        id: str,
        *,
        ausgaben: Sequence[WertDef],
        bezuege: Sequence[Eingabebezug],
        lagen: Sequence[Tuple[Seite, int, Bewehrungslage, WertDef]],
        titel: str = "Lagenaufbau",
    ) -> None:
        super().__init__(id, ausgaben=ausgaben, bezuege=bezuege, titel=titel,
                         referenz="SIA 262:2025, 5.2.2")
        self.lagen = list(lagen)

    def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]:
        h = e.g("h")
        p.text(
            "Die Lagen werden je Seite von aussen nach innen gestapelt. Der "
            "Randabstand einer Lage ist die Überdeckung zuzüglich der davor "
            "liegenden Stabdurchmesser und lichten Abstände, zuzüglich des "
            "halben eigenen Durchmessers. Die statische Höhe z wird von der "
            "Oberkante nach unten gemessen."
        )

        ergebnis: Dict[str, Groesse] = {}
        zeilen: List[List[str]] = []
        huelle = {
            Seite.UNTEN: e.g("c_nom_unten"),
            Seite.OBEN: e.g("c_nom_oben"),
        }

        for seite, nummer, lage, wertdef in self.lagen:
            rand = huelle[seite] + lage.lichter_abstand + lage.durchmesser / 2.0
            # Von der Oberkante gemessen: untere Lagen von h aus zurueckrechnen.
            z = rand if seite is Seite.OBEN else h - rand
            huelle[seite] = huelle[seite] + lage.lichter_abstand + lage.durchmesser

            ergebnis[wertdef.id] = z
            zeilen.append([
                lage.beschriftung(nummer, seite),
                lage.durchmesser.formatiert(0, MM),
                rand.formatiert(1, MM),
                z.formatiert(1, MM),
            ])

        p.tabelle(
            kopf=[r"\text{Lage}", r"\varnothing\ [\mathrm{mm}]",
                  r"\text{Randabstand}\ [\mathrm{mm}]", r"z\ [\mathrm{mm}]"],
            zeilen=zeilen,
            titel="Randabstände und statische Höhen",
            ausrichtung="lrrr",
        )
        return ergebnis


# ===========================================================================
# Plattenquerschnitt
# ===========================================================================


@dataclass
class Plattenquerschnitt:
    """
    Rechteckiger Plattenquerschnitt mit Bewehrung oben und unten.

    ``b`` ist die betrachtete Breite; bei Platten ueblicherweise 1 m, dann sind
    alle Schnittgroessen Werte pro Laufmeter.
    """

    name: str
    h: Groesse
    b: Groesse
    beton: Baustoff
    lagen_unten: List[Bewehrungslage] = field(default_factory=list)
    lagen_oben: List[Bewehrungslage] = field(default_factory=list)
    ueberdeckung_unten: Groesse = field(default_factory=lambda: Groesse(30, MM))
    ueberdeckung_oben: Groesse = field(default_factory=lambda: Groesse(30, MM))
    praefix: Optional[str] = None

    # Wird in __post_init__ aufgebaut.
    definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)
    berechnungen: List[Berechnung] = field(default_factory=list, init=False)
    lagen_ids: List[Tuple[Seite, int, Bewehrungslage, str, str]] = field(
        default_factory=list, init=False
    )
    """Je Lage: (Seite, Nummer, Lage, ID der Fläche, ID der statischen Höhe)."""

    def __post_init__(self) -> None:
        if not self.lagen_unten and not self.lagen_oben:
            raise ValueError(
                f"Querschnitt '{self.name}': ohne Bewehrungslage lässt sich "
                f"kein Widerstand bestimmen."
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

    @property
    def alle_lagen(self) -> List[Tuple[Seite, int, Bewehrungslage]]:
        return [(s, n, l) for s, n, l, _, _ in self.lagen_ids]

    @property
    def staehle(self) -> List[Baustoff]:
        """Alle vorkommenden Betonstaehle, ohne Wiederholung."""
        gesehen: Dict[str, Baustoff] = {}
        for _, _, lage, _, _ in self.lagen_ids:
            gesehen.setdefault(lage.stahl.id, lage.stahl)
        return list(gesehen.values())

    def ins_rechenwerk(self, werk) -> "Plattenquerschnitt":
        """Meldet Beton, Staehle und die Querschnittsberechnungen an."""
        self.beton.ins_rechenwerk(werk)
        for stahl in self.staehle:
            if not any(b.id.startswith(stahl.id + ".") for b in werk.berechnungen):
                stahl.ins_rechenwerk(werk)
        werk.definiere(*self.definitionen.values())
        werk.registriere(*self.berechnungen)
        return self

    # -- Aufbau -------------------------------------------------------------

    def _def(self, kurzname: str, symbol: str, einheit, beschreibung: str,
             stellen: int = 1, referenz: str = "") -> WertDef:
        d = WertDef(
            id=f"{self.id}.{kurzname}",
            symbol=symbol,
            einheit=einheit,
            beschreibung=beschreibung,
            referenz=referenz,
            stellen=stellen,
        )
        self.definitionen[kurzname] = d
        return d

    def _aufbauen(self) -> None:
        # -- Geometrie ------------------------------------------------------
        d_h = self._def("h", "h", MM, "Querschnittshöhe", 0)
        d_b = self._def("b", "b", MM, "Betrachtete Breite", 0)
        d_cu = self._def("c_nom_unten", "c_{nom,u}", MM, "Überdeckung unten", 0)
        d_co = self._def("c_nom_oben", "c_{nom,o}", MM, "Überdeckung oben", 0)

        self.berechnungen += [
            Vorgabe(id=f"{self.id}.h", ausgabe=d_h, groesse=self.h),
            Vorgabe(id=f"{self.id}.b", ausgabe=d_b, groesse=self.b),
            Vorgabe(id=f"{self.id}.c_nom_unten", ausgabe=d_cu, groesse=self.ueberdeckung_unten),
            Vorgabe(id=f"{self.id}.c_nom_oben", ausgabe=d_co, groesse=self.ueberdeckung_oben),
        ]

        # -- Lagen ----------------------------------------------------------
        aufbau_ausgaben: List[WertDef] = []
        aufbau_lagen: List[Tuple[Seite, int, Bewehrungslage, WertDef]] = []

        for seite, lagen in ((Seite.UNTEN, self.lagen_unten), (Seite.OBEN, self.lagen_oben)):
            for i, lage in enumerate(lagen, start=1):
                marke = f"{seite.kuerzel}{i}"
                index = f"{seite.kuerzel},{i}"

                d_phi = self._def(
                    f"lage.{marke}.phi", rf"\varnothing_{{{index}}}", MM,
                    f"Stabdurchmesser {lage.beschriftung(i, seite)}", 0,
                )
                self.berechnungen.append(
                    Vorgabe(id=f"{self.id}.lage.{marke}.phi", ausgabe=d_phi,
                            groesse=lage.durchmesser)
                )

                d_as = self._def(
                    f"lage.{marke}.a_s", f"a_{{s,{index}}}", MM2,
                    f"Bewehrungsquerschnitt {lage.beschriftung(i, seite)}", 0,
                    referenz="SIA 262:2025, 5.5.2",
                )
                self.berechnungen.append(self._flaechen_formel(marke, index, lage, d_as, d_phi, d_b))

                d_z = self._def(
                    f"lage.{marke}.z", f"z_{{{index}}}", MM,
                    f"Statische Höhe {lage.beschriftung(i, seite)} (ab Oberkante)", 1,
                )
                aufbau_ausgaben.append(d_z)
                aufbau_lagen.append((seite, i, lage, d_z))
                self.lagen_ids.append((seite, i, lage, d_as.id, d_z.id))

        self.berechnungen.append(
            Lagenaufbau(
                id=f"{self.id}.lagenaufbau",
                ausgaben=aufbau_ausgaben,
                bezuege=[
                    Eingabebezug("h", d_h.id),
                    Eingabebezug("c_nom_unten", d_cu.id),
                    Eingabebezug("c_nom_oben", d_co.id),
                ],
                lagen=aufbau_lagen,
            )
        )

    def _flaechen_formel(
        self, marke: str, index: str, lage: Bewehrungslage,
        d_as: WertDef, d_phi: WertDef, d_b: WertDef,
    ) -> Formel:
        """Bewehrungsquerschnitt -- ueber Stababstand oder ueber Stabzahl."""
        if lage.ueber_abstand:
            d_s = self._def(
                f"lage.{marke}.s", f"s_{{{index}}}", MM,
                f"Stababstand Lage {index}", 0,
            )
            self.berechnungen.append(
                Vorgabe(id=f"{self.id}.lage.{marke}.s", ausgabe=d_s, groesse=lage.abstand)
            )
            return Formel(
                id=f"{self.id}.lage.{marke}.a_s",
                ausgabe=d_as,
                eingaben={"phi": d_phi.id, "s": d_s.id, "b": d_b.id},
                vorlage=r"\frac{\pi \cdot @phi^{2}}{4} \cdot \frac{@b}{@s}",
                funktion=lambda phi, s, b: math.pi * phi * phi / 4.0 * (b / s),
            )
        return Formel(
            id=f"{self.id}.lage.{marke}.a_s",
            ausgabe=d_as,
            eingaben={"phi": d_phi.id},
            vorlage=rf"\frac{{\pi \cdot @phi^{{2}}}}{{4}} \cdot {lage.anzahl:g}",
            funktion=lambda phi: math.pi * phi * phi / 4.0 * lage.anzahl,
        )

    def __repr__(self) -> str:
        return (
            f"Plattenquerschnitt({self.name!r}, h={self.h}, b={self.b}, "
            f"{len(self.lagen_ids)} Lagen)"
        )


def _kennung(text: str) -> str:
    ersetzt = text.replace("/", "_").replace(" ", "_").replace(".", "_")
    return "".join(z for z in ersetzt if z.isalnum() or z == "_")
