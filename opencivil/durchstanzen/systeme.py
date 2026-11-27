"""
opencivil/durchstanzen/systeme.py -- woraus die Durchstanzbewehrung besteht.

VERANTWORTUNG:
Je System (:class:`Durchstanzsystem`) die Regeln, nach denen die Bemessung
(:func:`.bewehrung.bemessen`) eine Bewehrung zusammenstellt: welche
Durchmesser es gibt und wie hoch ein Element wird, wie weit die Elemente
einer Leiste vom Rand der gestützten Fläche stehen, der Faktor k_sys
anstelle der 2 in Gleichung (70), der Stahl, und wie ein Vorschlag heisst
und sich erklärt. Gleich für alle Systeme ist die Anordnung um die Stütze
(:func:`.bewehrung.leisten_anordnen`): Leisten senkrecht zum Rand der
gestützten Fläche, beim zweiten Element höchstens 1.5·d_v auseinander
(SIA 262:2025, 5.5.3.9). Gewählt wird das System an der Stelle; das
Werkzeug sucht darin Durchmesser, Anzahl und Leisten selbst. Bis 2026-11-26
gab es nur ancoPLUS, seit 2026-11-27 auch HALFEN HDB.

ANCOPLUS (:class:`AncoPlus`):
Doppelkopfanker auf Leisten, mit den Werten des Herstellers
(:mod:`.produkte`): Typen und Höhen aus der Preisliste, Abstände und k_sys
aus dem Gutachten von 2007 -- nach Vorgabe, nicht nachgeschlagen.

NACH DER NORM (:class:`NachNorm`):
Bügel und HALFEN HDB stehen, wie die Norm es verlangt (SIA 262:2025,
5.5.3.8, 5.5.3.9, 5.5.3.12, Tabelle 21): mindestens zwei Reihen, den
Abstand s_1 der Reihen und den Durchmesser höchstens nach Tabelle 21, s_0
kleiner als s_1, und tangential höchstens 1.5·d_v beim zweiten Ring;
Elemente näher als 0.35·d_v zählen nicht. Gewählt sind, nach Vorgabe, nicht
nachgeschlagen:

- das erste Element 0.35·d_v vom Rand, auf 5 mm aufgerundet -- so nah, wie
  es noch zählt;
- das zweite bei d_v, auf 5 mm abgerundet, höchstens s_1 weiter -- so
  zählen zwei Reihen;
- danach s_1, so gross, wie Tabelle 21 es zulässt, auf 5 mm abgerundet;
- die Durchmesser des Systems bis zur Grenze der Tabelle 21.

In (70) gilt die 2 der Norm: mehr lässt 4.3.6.5.9 nur für Systeme zu, deren
Sicherheit Versuche zeigen, und die halten dafür meist strengere Regeln ein
als die Norm.

BÜGEL (:class:`Buegel`):
Senkrechte Bügel, die die Biegebewehrung auf beiden Seiten umfassen. Eine
Leiste ist hier eine Linie von Bügelschenkeln, vom Rand der gestützten
Fläche nach aussen; jeder Schenkel ist ein Element. Die Durchmesser sind die
der Bügelsuche (:data:`~opencivil.material.betonstahl.BUEGELDURCHMESSER`),
aus B500B; die Höhe ist der ganze Platz zwischen den Überdeckungen.

HALFEN HDB (:class:`HalfenHdb`):
Doppelkopfanker auf Leisten wie ancoPLUS, mit den Durchmessern des
Herstellers (:mod:`.produkte`). Den Faktor 3.5 in (70) nennt der Hersteller
nach einem Gutachten, das nicht vorliegt, und mit ihm die strengeren
Regeln, die 4.3.6.5.9 dafür verlangt. Darum stehen die Anker nach der Norm,
und es gilt die 2. Die Höhe ist der Platz zwischen den Überdeckungen, auf
5 mm abgerundet -- nach Vorgabe, nicht nachgeschlagen: die Unterlage nennt
keine Höhen. Der Stahl ist B500B: die Unterlage nennt B500, und in (67) und
(69) zählen nur f_sd und E_s, für jede Duktilitätsklasse gleich.

EINHEITEN:
SI-Basis, Längen in m.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Tuple

from opencivil.core.wahl import Wahl
from opencivil.durchstanzen import produkte
from opencivil.durchstanzen.bewehrung import BEREICH_VON
from opencivil.durchstanzen.produkte import Element
from opencivil.durchstanzen.pruefung import tabelle_21
from opencivil.material.betonstahl import BUEGELDURCHMESSER

if TYPE_CHECKING:
    from opencivil.durchstanzen.bewehrung import Vorschlag

#: Auf so viel werden Abstände gerundet.
RASTER = 0.005


def _ab(x: float) -> float:
    """Auf :data:`RASTER` abgerundet."""
    return round(math.floor(round(x / RASTER, 9)) * RASTER, 6)


def _auf(x: float) -> float:
    """Auf :data:`RASTER` aufgerundet."""
    return round(math.ceil(round(x / RASTER, 9)) * RASTER, 6)


class System(ABC):
    """Die Regeln eines Systems -- siehe Dateikopf."""

    NAME: str
    """Wie es im Schalter und in der Herleitung heisst."""

    ELEMENT: str
    """Ein Element, auch mehrere: «Anker», «Bügelschenkel»."""

    ELEMENTEN: str
    """Dasselbe im Dativ Mehrzahl: «zwischen zwei äussersten Ankern»."""

    VERANKERUNG: str
    """Was auf der Druckseite verankert ist und c_v misst: «Ankerköpfe», «Bügel»."""

    LEISTEN: str
    """Was um die gestützte Fläche steht: «Leisten», «Bügel»."""

    LEISTE: str
    """Was die Elemente einer Richtung trägt, in der Einzahl: «Leiste», «Linie»."""

    FORM: str
    """Wie das Bild der Leiste ein Element zeichnet: «kopfanker», ein Schaft mit zwei Köpfen, oder «buegel»."""

    ENDEN: str
    """Wie die Enden eines Elements heissen -- das Bild zeichnet sie schematisch: «Köpfe», «Biegungen»."""

    KEINES: str
    """Das Urteil, wenn es keines gibt: «Kein ancoPLUS passt in diese Platte.»"""

    KEINES_REICHT: str
    """Der Hinweis, wenn auch der stärkste Versuch nicht alles erfüllt."""

    STAHL = "B500B"
    """Der Stahl der Elemente -- in (67) und (69) gilt seine Fliessgrenze (4.3.6.5.4)."""

    ANZAHLEN: range = produkte.ANKER_JE_LEISTE
    """
    Wie viele Elemente eine Leiste tragen kann: bei ancoPLUS die lieferbaren
    Leisten, bei Bügeln und HDB nach Vorgabe ebenso viele Reihen --
    mindestens zwei, wie 5.5.3.8 es verlangt.
    """

    @abstractmethod
    def elemente(self, d: float, h_A: float) -> List[Element]:
        """Die Elemente, die bei der statischen Höhe d und der Höhe h_A in Frage kommen, dünnste zuerst."""

    @abstractmethod
    def hoehe(self, h: float, c: float, c_v: float) -> float:
        """Die Höhe eines Elements zwischen den Überdeckungen c (Zugseite) und c_v (Druckseite)."""

    @property
    @abstractmethod
    def hoehentext(self) -> str:
        """Wie die Höhe zustande kommt -- der Titel ihrer Zeile in der Herleitung."""

    @abstractmethod
    def abstaende(self, d: float, d_v: float, anzahl: int) -> Tuple[float, ...]:
        """Die Abstände einer Leiste vom Rand der gestützten Fläche an: zum ersten Element, dann von Element zu Element."""

    @abstractmethod
    def k_sys(self, c_v: float, d: float, ausnahme: bool) -> float:
        """Der Faktor anstelle der 2 in Gleichung (70); ``ausnahme``: Innenstütze, Wandende, einspringende Ecke."""

    @property
    @abstractmethod
    def k_sys_text(self) -> str:
        """Woher k_sys kommt, für die Herleitung."""

    @abstractmethod
    def k_sys_titel(self, c_v: float, d: float) -> str:
        """Der Titel der Zeile von k_sys -- mit den Zahlen, nach denen er sich richtet."""

    @abstractmethod
    def name(self, vorschlag: "Vorschlag") -> str:
        """Wie ein Vorschlag heisst -- je Länge der Leisten, wie viele es sind."""

    @abstractmethod
    def regeln(self, vorschlag: "Vorschlag", h_A: str, wo: str) -> str:
        """Der Satz der Herleitung, der den Vorschlag und seine Regeln nennt; ``wo``: «um den Stahlpilz»."""

    @property
    @abstractmethod
    def warum_keines(self) -> str:
        """Warum es in dieser Platte keines gibt -- wenn :meth:`elemente` leer bleibt oder keine Leiste Platz findet."""


class AncoPlus(System):
    """ancoPLUS von AncoTech -- siehe Dateikopf und :mod:`.produkte`."""

    NAME = "ancoPLUS"
    ELEMENT = "Anker"
    ELEMENTEN = "Ankern"
    VERANKERUNG = "Ankerköpfe"
    LEISTEN = "Leisten"
    LEISTE = "Leiste"
    FORM = "kopfanker"
    ENDEN = "Köpfe"
    KEINES = "Kein ancoPLUS passt in diese Platte."
    KEINES_REICHT = "Kein ancoPLUS erfüllt alle Bedingungen; gerechnet ist der stärkste Versuch."
    STAHL = produkte.STAHL

    def elemente(self, d: float, h_A: float) -> List[Element]:
        groesster = produkte.groesster_durchmesser(d)
        return [t for t in produkte.ANKERTYPEN
                if groesster is not None and t.durchmesser <= groesster + 1e-9
                and t.h_min - 1e-9 <= h_A <= t.h_max + 1e-9]

    def hoehe(self, h: float, c: float, c_v: float) -> float:
        return produkte.ankerhoehe(h, c, c_v)

    @property
    def hoehentext(self) -> str:
        return "Höhe der Anker: auf eine lieferbare Höhe abgerundet, die auf 5 mm endet"

    def abstaende(self, d: float, d_v: float, anzahl: int) -> Tuple[float, ...]:
        return produkte.abstaende(d, anzahl)

    def k_sys(self, c_v: float, d: float, ausnahme: bool) -> float:
        return produkte.k_sys(c_v, d, ausnahme)

    @property
    def k_sys_text(self) -> str:
        return ("Mehr als 2·k_r und 3.5 in Gleichung (70) lässt 4.3.6.5.9 nur für Systeme zu, "
                "deren gleichwertige Sicherheit Versuche zeigen. Das Gutachten von ancoPLUS lässt "
                "für Innenstützen und Wandenden 3·k_r zu, wenn die Köpfe auf der Druckseite "
                "höchstens d/10 tief liegen; bei d/6 gilt wieder 2·k_r, dazwischen linear. Für "
                "Rand- und Eckstützen bleibt es bei 2·k_r. Die Obergrenze bleibt 3.5.")

    def k_sys_titel(self, c_v: float, d: float) -> str:
        return (f"Faktor des Produkts: c_v = {c_v * 1e3:.0f} mm, d/10 = {d * 1e2:.0f} mm, "
                f"d/6 = {d * 1e3 / 6:.0f} mm")

    def name(self, vorschlag: "Vorschlag") -> str:
        """«12 × ancoPLUS DA3-0215», mit gekürzten Leisten «… + 2 × ancoPLUS DA2-0215»."""
        return " + ".join(f"{n} × ancoPLUS {produkte.typname(vorschlag.typ, anzahl, vorschlag.h_A)}"
                          for anzahl, n in vorschlag.gruppen)

    def regeln(self, vorschlag: "Vorschlag", h_A: str, wo: str) -> str:
        abstaende = " / ".join(f"{a * 1e3:.0f}" for a in vorschlag.abstaende)
        return (f"Vorgeschlagen wird ancoPLUS von AncoTech{wo and ' ' + wo}: {self.name(vorschlag)} – "
                f"Anker ⌀{vorschlag.typ.durchmesser * 1e3:.0f} aus {self.STAHL} mit h_A = {h_A} mm, "
                f"vom Rand der gestützten Fläche {abstaende} mm. Die Abstände sind die der Typen "
                f"«D» nach dem Gutachten des Herstellers: 0.375·d zum ersten Anker, bis zum dritten "
                f"0.60·d, danach 0.75·d ({produkte.QUELLE_ANCOPLUS}, nach Vorgabe, nicht "
                f"nachgeschlagen). Zwei Leisten stehen beim zweiten Anker höchstens 1.5·d_v "
                f"auseinander (5.5.3.9).")

    @property
    def warum_keines(self) -> str:
        return ("Für diese Platte gibt es kein ancoPLUS: sie ist zu dünn (d < 160 mm), keine "
                "lieferbare Höhe passt, oder keine Leiste findet Platz.")


class NachNorm(System):
    """Ein System, das allein die Norm regelt -- Bügel und HALFEN HDB; siehe Dateikopf."""

    DURCHMESSER: Tuple[float, ...]
    """Die Durchmesser in mm, dünnste zuerst -- genommen bis zur Grenze der Tabelle 21."""

    LINIEN: str
    """Die Mehrzahl von :attr:`LEISTE`: «Linien», «Leisten»."""

    def elemente(self, d: float, h_A: float) -> List[Element]:
        grenzen = tabelle_21(d)
        if grenzen is None:
            return []
        return [Element(phi / 1e3) for phi in self.DURCHMESSER
                if phi / 1e3 <= grenzen.durchmesser + 1e-9]

    def abstaende(self, d: float, d_v: float, anzahl: int) -> Tuple[float, ...]:
        s_1 = _ab(tabelle_21(d).s_1)
        s_0 = _auf(BEREICH_VON * d_v)
        zweiter = min(_ab(d_v - s_0), s_1)
        return ((s_0, zweiter) + (s_1,) * (anzahl - 2))[:anzahl]

    def k_sys(self, c_v: float, d: float, ausnahme: bool) -> float:
        return produkte.K_SYS_NORM

    def k_sys_titel(self, c_v: float, d: float) -> str:
        return "Faktor der Norm in Gleichung (70)"

    def anordnung(self) -> str:
        """Die Sätze der Herleitung, wie die Elemente nach der Norm stehen -- siehe Dateikopf."""
        return (f"Der erste {self.ELEMENT} steht 0.35·d_v vom Rand, so nah, wie er noch zählt, der "
                f"zweite bei d_v, damit zwei Reihen zählen; danach folgen sie sich im grössten "
                f"Abstand s_1 nach Tabelle 21 (nach Vorgabe, nicht nachgeschlagen; 5.5.3.8). Zwei "
                f"{self.LINIEN} stehen beim zweiten {self.ELEMENT} höchstens 1.5·d_v auseinander "
                f"(5.5.3.9).")


class Buegel(NachNorm):
    """Bügel nach SIA 262:2025, 5.5.3 -- siehe Dateikopf."""

    NAME = "Bügel"
    ELEMENT = "Bügelschenkel"
    ELEMENTEN = "Bügelschenkeln"
    VERANKERUNG = "Bügel"
    LEISTEN = "Bügel"
    LEISTE = "Linie"
    LINIEN = "Linien"
    FORM = "buegel"
    ENDEN = "Biegungen"
    KEINES = "Keine Bügel passen in diese Platte."
    KEINES_REICHT = "Keine Bügel erfüllen alle Bedingungen; gerechnet ist der stärkste Versuch."
    DURCHMESSER = BUEGELDURCHMESSER

    def hoehe(self, h: float, c: float, c_v: float) -> float:
        return round(h - c - c_v, 6)

    @property
    def hoehentext(self) -> str:
        return "Höhe der Bügel: der ganze Platz zwischen den Überdeckungen"

    @property
    def k_sys_text(self) -> str:
        return ("Für Bügel gilt in Gleichung (70) die 2 der Norm: mehr lässt 4.3.6.5.9 nur für "
                "Systeme zu, deren gleichwertige Sicherheit Versuche zeigen. Die Obergrenze ist "
                "3.5.")

    def name(self, vorschlag: "Vorschlag") -> str:
        """«12 × 3 + 2 × 2 Bügelschenkel ⌀10»: je Länge der Linien, wie viele es sind."""
        linien = " + ".join(f"{n} × {anzahl}" for anzahl, n in vorschlag.gruppen)
        return f"{linien} Bügelschenkel ⌀{vorschlag.typ.durchmesser * 1e3:.0f}"

    def regeln(self, vorschlag: "Vorschlag", h_A: str, wo: str) -> str:
        abstaende = " / ".join(f"{a * 1e3:.0f}" for a in vorschlag.abstaende)
        return (f"Vorgeschlagen werden Bügel{wo and ' ' + wo}: {self.name(vorschlag)} aus "
                f"{self.STAHL}, {h_A} mm hoch, in Linien vom Rand der gestützten Fläche "
                f"{abstaende} mm. {self.anordnung()} Die Bügel umfassen die Biegebewehrung oben "
                f"und unten und sind dort verankert (5.5.3.10).")

    @property
    def warum_keines(self) -> str:
        return ("Für diese Platte gibt es keine Bügel: sie ist zu dünn (d < 140 mm, Tabelle 21), "
                "oder keine Linie findet Platz.")


class HalfenHdb(NachNorm):
    """HALFEN HDB von Leviat, angeordnet nach der Norm -- siehe Dateikopf und :mod:`.produkte`."""

    NAME = "HALFEN HDB"
    ELEMENT = "Anker"
    ELEMENTEN = "Ankern"
    VERANKERUNG = "Ankerköpfe"
    LEISTEN = "Leisten"
    LEISTE = "Leiste"
    LINIEN = "Leisten"
    FORM = "kopfanker"
    ENDEN = "Köpfe"
    KEINES = "Kein HALFEN HDB passt in diese Platte."
    KEINES_REICHT = "Kein HALFEN HDB erfüllt alle Bedingungen; gerechnet ist der stärkste Versuch."
    DURCHMESSER = produkte.HDB_DURCHMESSER

    def hoehe(self, h: float, c: float, c_v: float) -> float:
        return _ab(h - c - c_v)

    @property
    def hoehentext(self) -> str:
        return "Höhe der Anker: der Platz zwischen den Überdeckungen, auf 5 mm abgerundet"

    @property
    def k_sys_text(self) -> str:
        return (f"Für HALFEN HDB nennt der Hersteller {produkte.HDB_FAKTOR:g} anstelle der 2 in "
                f"Gleichung (70), nach einem Gutachten. Mehr als die 2 lässt 4.3.6.5.9 nur zu, wo "
                f"Versuche die Sicherheit zeigen, meist mit strengeren Regeln für die Anordnung; "
                f"beides stünde im Gutachten, und es liegt nicht vor. Darum stehen die Anker nach "
                f"der Norm, und es gilt ihre 2. Die Obergrenze ist 3.5.")

    def name(self, vorschlag: "Vorschlag") -> str:
        """
        «12 × HDB ⌀14 mit 3 Ankern + 4 × HDB ⌀14 mit 2 Ankern»: je Länge der
        Leisten, wie viele es sind.
        """
        phi = f"⌀{vorschlag.typ.durchmesser * 1e3:.0f}"
        return " + ".join(f"{n} × HDB {phi} mit {anzahl} Ankern" for anzahl, n in vorschlag.gruppen)

    def regeln(self, vorschlag: "Vorschlag", h_A: str, wo: str) -> str:
        abstaende = " / ".join(f"{a * 1e3:.0f}" for a in vorschlag.abstaende)
        return (f"Vorgeschlagen wird HALFEN HDB von Leviat{wo and ' ' + wo}: "
                f"{self.name(vorschlag)}, aus {self.STAHL} mit h_A = {h_A} mm, vom Rand der "
                f"gestützten Fläche {abstaende} mm. Die Durchmesser nennt der Hersteller "
                f"({produkte.QUELLE_HDB}); genommen werden die, die Tabelle 21 zulässt (5.5.3.12). "
                f"{self.anordnung()}")

    @property
    def warum_keines(self) -> str:
        return ("Für diese Platte gibt es kein HALFEN HDB: sie ist zu dünn (d < 140 mm, "
                "Tabelle 21), oder keine Leiste findet Platz.")


class Durchstanzsystem(Wahl):
    """Woraus die Durchstanzbewehrung besteht -- siehe Dateikopf."""

    ANCOPLUS = "ancoplus"
    HDB = "hdb"
    BUEGEL = "buegel"

    @property
    def beschriftung(self) -> str:
        return self.regeln.NAME

    @property
    def regeln(self) -> System:
        """Die Regeln dieses Systems."""
        return SYSTEME[self]


#: Je Stellung ihre Regeln -- eine Instanz je System, ohne eigenen Zustand.
SYSTEME: Dict[Durchstanzsystem, System] = {
    Durchstanzsystem.ANCOPLUS: AncoPlus(),
    Durchstanzsystem.HDB: HalfenHdb(),
    Durchstanzsystem.BUEGEL: Buegel(),
}
