"""
opencivil/core/wert.py -- Benannte Werte im Rechenmodell.

VERANTWORTUNG:
Trennt sauber zwischen der *Definition* eines Wertes (Symbol, Einheit,
Beschreibung, Normreferenz -- statisch) und seiner *Belegung* (Zahlenwert,
Herkunft -- dynamisch). Diese Trennung ist bewusst: im alten Code waren
Definition und Instanz dasselbe veraenderliche Objekt, was zu global
mutierbaren Vorlagen und schwer nachvollziehbarem Zustand fuehrte.

NAMENSRAEUME:
Wert-IDs sind punktgetrennt und global eindeutig::

    beton.C30_37.f_cd
    stahl.B500B.f_yd
    querschnitt.decke1.lage.3.a_s
    querschnitt.decke1.M_Rd

Das erlaubt mehrere Materialien und Bauteile im selben Modell, ohne dass sich
Werte gegenseitig ueberschreiben.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from opencivil.core.einheiten import EINHEITSLOS, Einheit, Groesse


class Quelle(str, Enum):
    """Woher ein Wert stammt -- entscheidend fuer die Nachvollziehbarkeit."""

    EINGABE = "eingabe"
    """Direkt vom Benutzer eingegeben."""

    VORGABE = "vorgabe"
    """Normvorgabe oder Vorlagenwert (z.B. f_ck aus der Betonsorte)."""

    BERECHNET = "berechnet"
    """Von einer Berechnung erzeugt."""

    UEBERSCHRIEBEN = "ueberschrieben"
    """Waere berechenbar, wurde aber vom Benutzer von Hand gesetzt."""

    def __str__(self) -> str:
        return self.value

    @property
    def beschriftung(self) -> str:
        return {
            Quelle.EINGABE: "Eingabe",
            Quelle.VORGABE: "Vorgabe",
            Quelle.BERECHNET: "berechnet",
            Quelle.UEBERSCHRIEBEN: "vom Benutzer ueberschrieben",
        }[self]

    @property
    def ist_vorgegeben(self) -> bool:
        """True, wenn der Wert nicht aus einer Berechnung stammt."""
        return self in (Quelle.EINGABE, Quelle.VORGABE, Quelle.UEBERSCHRIEBEN)


@dataclass(frozen=True)
class WertDef:
    """
    Statische Definition eines Wertes.

    Enthaelt alles, was zur Darstellung noetig ist, aber keinen Zahlenwert.
    Unveraenderlich, damit Definitionen gefahrlos geteilt werden koennen.
    """

    id: str
    """Global eindeutige, punktgetrennte Kennung, z.B. ``beton.C30_37.f_cd``."""

    symbol: str
    """LaTeX-Symbol ohne Mathematikumgebung, z.B. ``f_{cd}``."""

    einheit: Einheit = EINHEITSLOS
    """Anzeige-Einheit. Beeinflusst nie das Rechenergebnis."""

    beschreibung: str = ""
    """Deutscher Klartext, z.B. 'Bemessungswert der Betondruckfestigkeit'."""

    referenz: str = ""
    """Normstelle, z.B. 'SIA 262:2025, 2.4.2.3'."""

    stellen: int = 2
    """Nachkommastellen fuer die Darstellung."""

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("WertDef braucht eine id.")
        if not self.symbol:
            raise ValueError(f"WertDef '{self.id}' braucht ein Symbol.")

    @property
    def kurzname(self) -> str:
        """Letztes Segment der ID, z.B. 'f_cd' aus 'beton.C30_37.f_cd'."""
        return self.id.rsplit(".", 1)[-1]

    @property
    def namensraum(self) -> str:
        """Alles vor dem letzten Segment, z.B. 'beton.C30_37'."""
        teile = self.id.rsplit(".", 1)
        return teile[0] if len(teile) == 2 else ""

    def belegen(
        self,
        groesse: Groesse,
        quelle: Quelle = Quelle.BERECHNET,
        herkunft: Optional[str] = None,
    ) -> "Wert":
        """Erzeugt einen belegten Wert zu dieser Definition."""
        return Wert(definition=self, groesse=groesse, quelle=quelle, herkunft=herkunft)

    def mit_praefix(self, praefix: str) -> "WertDef":
        """
        Kopie mit vorangestelltem Namensraum.

        Erlaubt es, Wert-Vorlagen (z.B. alle Betoneigenschaften) einmal zu
        definieren und pro Material zu instanziieren.
        """
        neue_id = f"{praefix}.{self.id}" if praefix else self.id
        return WertDef(
            id=neue_id,
            symbol=self.symbol,
            einheit=self.einheit,
            beschreibung=self.beschreibung,
            referenz=self.referenz,
            stellen=self.stellen,
        )

    def __str__(self) -> str:
        return self.id


@dataclass(frozen=True)
class Wert:
    """Eine Definition zusammen mit ihrem Zahlenwert."""

    definition: WertDef
    groesse: Groesse
    quelle: Quelle = Quelle.BERECHNET
    herkunft: Optional[str] = None
    """ID der Berechnung, die diesen Wert erzeugt hat (None bei Eingaben)."""

    def __post_init__(self) -> None:
        erwartet = self.definition.einheit.dimension
        tatsaechlich = self.groesse.dimension
        # Eine dimensionslose Null darf jede Definition belegen.
        if tatsaechlich != erwartet and not (
            self.groesse.si == 0.0 and tatsaechlich.ist_dimensionslos
        ):
            from opencivil.core.einheiten import DimensionsFehler

            raise DimensionsFehler(
                f"Wert '{self.definition.id}' ist als {self.definition.einheit.name} "
                f"({erwartet}) definiert, hat aber Dimension {tatsaechlich}."
            )

    # -- Bequemer Zugriff ---------------------------------------------------

    @property
    def id(self) -> str:
        return self.definition.id

    @property
    def symbol(self) -> str:
        return self.definition.symbol

    @property
    def einheit(self) -> Einheit:
        return self.definition.einheit

    @property
    def stellen(self) -> int:
        return self.definition.stellen

    @property
    def beschreibung(self) -> str:
        return self.definition.beschreibung

    @property
    def referenz(self) -> str:
        return self.definition.referenz

    def in_einheit(self, ziel: Einheit) -> float:
        return self.groesse.in_einheit(ziel)

    # -- Darstellung --------------------------------------------------------

    def formatiert(self) -> str:
        """Zahlenwert in der definierten Einheit und Genauigkeit."""
        return self.groesse.formatiert(self.stellen, self.einheit)

    def zahl_latex(self) -> str:
        """Zahlenwert samt Einheit als LaTeX-Fragment, z.B. ``18.7\\,\\mathrm{MPa}``."""
        return self.groesse.als_latex(self.stellen, self.einheit)

    def __str__(self) -> str:
        einheit_text = (
            f" {self.einheit.name}" if self.einheit.name not in ("", "-") else ""
        )
        return f"{self.definition.kurzname} = {self.formatiert()}{einheit_text}"

    def __repr__(self) -> str:
        return f"Wert({self.id}={self.formatiert()} {self.einheit.name}, {self.quelle})"


@dataclass
class FehlendeEingabe:
    """
    Eine Eingabe, die zur Berechnung eines Ziels noetig waere, aber fehlt.

    Der Loeser sammelt diese, statt abzubrechen -- so kann die Oberflaeche dem
    Benutzer genau sagen, was er noch angeben muss und wofuer.
    """

    id: str
    """ID des fehlenden Wertes."""

    benoetigt_von: str
    """ID der Berechnung, die ihn braucht."""

    pfad: tuple = field(default_factory=tuple)
    """Kette der Ziele, ueber die man hierher kam -- fuer die Begruendung."""

    definition: Optional[WertDef] = None
    """Definition, falls bekannt (dann kennt man Symbol, Einheit, Beschreibung)."""

    @property
    def beschreibung(self) -> str:
        if self.definition and self.definition.beschreibung:
            return self.definition.beschreibung
        return self.id

    def __str__(self) -> str:
        wofuer = " -> ".join(self.pfad) if self.pfad else self.benoetigt_von
        return f"Fehlende Eingabe '{self.id}' (benoetigt fuer {wofuer})"
