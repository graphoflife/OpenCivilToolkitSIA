"""
opencivil/core/protokoll.py -- Mitschrift einer Berechnung.

VERANTWORTUNG:
Eine Berechnung schreibt waehrend des Rechnens in ein Protokoll. Rechenschritt
und seine Darstellung entstehen dadurch am selben Ort und koennen nicht
auseinanderlaufen -- man kann nicht das eine rechnen und das andere aufschreiben.

Genau das braucht eine Prozedur: eine Iteration soll nicht nur ihr Resultat
liefern, sondern auch ihren Ablauf zeigen -- Startwerte, Zwischenschritte in
einer Tabelle, Abbruchkriterium. Ein Leser muss die Rechnung von Hand
nachvollziehen koennen.

Das Protokoll ist reine Datenstruktur. Ob daraus Konsolentext, ein LaTeX-
Dokument oder HTML wird, entscheidet erst der Bericht.

STILLES PROTOKOLL:
In heissen Schleifen (z.B. beim punktweisen Aufbau einer M-N-Interaktionslinie
mit hunderten Dehnungsebenen) will man nichts mitschreiben. Dafuer gibt es
:class:`StillesProtokoll` -- dieselbe Schnittstelle, verwirft aber alles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, Mapping, Optional, Sequence

from opencivil.core import latex as tex
from opencivil.core.wert import Wert


# ===========================================================================
# Bloecke
# ===========================================================================


class HinweisArt(str, Enum):
    INFO = "info"
    WARNUNG = "warnung"
    ANNAHME = "annahme"

    def __str__(self) -> str:
        return self.value

    @property
    def beschriftung(self) -> str:
        return {
            HinweisArt.INFO: "Hinweis",
            HinweisArt.WARNUNG: "Warnung",
            HinweisArt.ANNAHME: "Annahme",
        }[self]


@dataclass
class Block:
    """Basis aller Protokollbausteine."""


@dataclass
class TitelBlock(Block):
    text: str
    ebene: int = 2


@dataclass
class TextBlock(Block):
    """Erklaerender Fliesstext -- das 'Warum' zwischen den Formeln."""

    text: str


@dataclass
class GleichungBlock(Block):
    """Eine gesetzte Formel."""

    latex: str
    titel: str = ""
    referenz: str = ""
    wert_id: str = ""
    """ID des erzeugten Wertes, falls die Gleichung einen Wert liefert."""

    formelzeile: Optional[tex.Formelzeile] = None
    """Strukturierte Fassung, sofern vorhanden -- erlaubt spaeteren Umbruch."""


@dataclass
class TabellenBlock(Block):
    """Tabelle, typischerweise ein Iterationsprotokoll."""

    kopf: Sequence[str]
    zeilen: Sequence[Sequence[str]]
    titel: str = ""
    ausrichtung: Optional[str] = None

    def als_latex(self) -> str:
        return tex.tabelle(self.kopf, self.zeilen, self.ausrichtung)


@dataclass
class HinweisBlock(Block):
    text: str
    art: HinweisArt = HinweisArt.INFO


@dataclass
class UnterprotokollBlock(Block):
    """Eingeschachtelte Mitschrift, z.B. ein Iterationsdurchlauf."""

    titel: str
    protokoll: "Protokoll"


# ===========================================================================
# Protokoll
# ===========================================================================


class Protokoll:
    """
    Sammelt die Bloecke einer Berechnung in der Reihenfolge ihres Entstehens.

    Beispiel::

        p.titel("Bemessungswert der Betondruckfestigkeit")
        p.formel(f_cd, r"\\frac{@eta_fc \\cdot @f_ck}{@gamma_c}",
                 {"eta_fc": eta, "f_ck": fck, "gamma_c": gamma})
        p.hinweis("Massgebend ist der abgeminderte Wert.")
    """

    def __init__(self, titel: str = "", referenz: str = "") -> None:
        self.kopftitel = titel
        self.referenz = referenz
        self.bloecke: List[Block] = []

    # -- Aufzeichnen --------------------------------------------------------

    def _anfuegen(self, block: Block) -> Block:
        self.bloecke.append(block)
        return block

    def titel(self, text: str, ebene: int = 2) -> None:
        self._anfuegen(TitelBlock(text=text, ebene=ebene))

    def text(self, text: str) -> None:
        self._anfuegen(TextBlock(text=text))

    def gleichung(self, latex: str, titel: str = "", referenz: str = "") -> None:
        """Setzt beliebiges, bereits fertiges LaTeX."""
        self._anfuegen(GleichungBlock(latex=latex, titel=titel, referenz=referenz))

    def formel(
        self,
        ergebnis: Wert,
        vorlage: str,
        eingaben: Mapping[str, Wert],
        titel: str = "",
        referenz: Optional[str] = None,
    ) -> None:
        """
        Der Regelfall: ``Symbol = analytische Formel = Formel mit Zahlen = Resultat``.

        Von Hand geschrieben wird nur ``vorlage`` (die analytische Form mit
        ``@name``-Platzhaltern). Die Fassung mit Zahlen und Einheiten entsteht
        automatisch aus ``eingaben``.
        """
        zeile = tex.Formelzeile.bauen(ergebnis, vorlage, eingaben)
        self._anfuegen(
            GleichungBlock(
                latex=zeile.darstellen(),
                titel=titel or ergebnis.beschreibung,
                referenz=ergebnis.referenz if referenz is None else referenz,
                wert_id=ergebnis.id,
                formelzeile=zeile,
            )
        )

    def wert(self, ergebnis: Wert, titel: str = "", referenz: Optional[str] = None) -> None:
        """Schlichte Form ``Symbol = Wert`` -- fuer Eingaben und Vorgaben."""
        zeile = tex.Formelzeile.bauen(ergebnis)
        self._anfuegen(
            GleichungBlock(
                latex=zeile.einzeilig(),
                titel=titel or ergebnis.beschreibung,
                referenz=ergebnis.referenz if referenz is None else referenz,
                wert_id=ergebnis.id,
                formelzeile=zeile,
            )
        )

    def tabelle(
        self,
        kopf: Sequence[str],
        zeilen: Iterable[Sequence[str]],
        titel: str = "",
        ausrichtung: Optional[str] = None,
    ) -> None:
        self._anfuegen(
            TabellenBlock(
                kopf=list(kopf),
                zeilen=[list(z) for z in zeilen],
                titel=titel,
                ausrichtung=ausrichtung,
            )
        )

    def hinweis(self, text: str) -> None:
        self._anfuegen(HinweisBlock(text=text, art=HinweisArt.INFO))

    def warnung(self, text: str) -> None:
        self._anfuegen(HinweisBlock(text=text, art=HinweisArt.WARNUNG))

    def annahme(self, text: str) -> None:
        """
        Haelt eine getroffene Annahme fest.

        Dafuer gedacht, dass empirische Normformeln ihre Einheiten-Konvention
        offenlegen (siehe ``einheiten.empirisch``).
        """
        self._anfuegen(HinweisBlock(text=text, art=HinweisArt.ANNAHME))

    def unterprotokoll(self, titel: str) -> "Protokoll":
        """Oeffnet eine eingeschachtelte Mitschrift und gibt sie zurueck."""
        unter = Protokoll(titel=titel)
        self._anfuegen(UnterprotokollBlock(titel=titel, protokoll=unter))
        return unter

    # -- Auswerten ----------------------------------------------------------

    @property
    def ist_leer(self) -> bool:
        return not self.bloecke

    def alle_bloecke(self) -> Iterable[Block]:
        """Laeuft rekursiv durch alle Bloecke, auch die eingeschachtelten."""
        for block in self.bloecke:
            yield block
            if isinstance(block, UnterprotokollBlock):
                yield from block.protokoll.alle_bloecke()

    def gleichungen(self) -> List[GleichungBlock]:
        return [b for b in self.alle_bloecke() if isinstance(b, GleichungBlock)]

    def warnungen(self) -> List[HinweisBlock]:
        return [
            b
            for b in self.alle_bloecke()
            if isinstance(b, HinweisBlock) and b.art is HinweisArt.WARNUNG
        ]

    def __len__(self) -> int:
        return len(self.bloecke)

    def __repr__(self) -> str:
        return f"Protokoll({self.kopftitel!r}, {len(self.bloecke)} Bloecke)"


class StillesProtokoll(Protokoll):
    """
    Verwirft alles. Fuer Schleifen, deren Einzelschritte nicht in den Bericht sollen.

    Die Schnittstelle bleibt identisch, damit derselbe Rechencode einmal
    protokollierend und einmal still laufen kann -- ohne Verzweigung im Code
    und ohne dass die beiden Pfade auseinanderlaufen koennen.
    """

    def _anfuegen(self, block: Block) -> Block:
        return block

    def unterprotokoll(self, titel: str) -> "Protokoll":
        return self

    @property
    def ist_leer(self) -> bool:
        return True
