"""
opencivil/stabwerk/stabquerschnitt.py -- woher A und I eines Stabs kommen.

VERANTWORTUNG:
Ein Querschnitt der Staebe, aufgeloest: je Art eine Klasse, die ihre
Berechnungen fuer ``A`` und ``I`` und ihren Umriss selbst traegt --

* nach Vorlage (:class:`NachVorlage`) -- die Formeln der Vorlage
  (:mod:`~opencivil.stabwerk.querschnitte`), die Masse als Vorgaben;
* von Hand (:class:`VonHand`) -- ``A`` und ``I`` als Eingaben;
* aus einer Platte (:class:`AusPlatte`) -- die Formeln des Rechtecks mit
  ``b`` und ``h`` der Platte;
* aus einer Querschnittsanalyse (:class:`AusAnalyse`) -- ``A`` und ``I_y``
  ihres Bruttoquerschnitts.

Ueber die Werte der Platte und der Analyse haengt das System im Rechengraph
an ihnen: aendert sich deren Dicke, rechnet es neu. Nur ein Querschnitt aus
einem Bauteil (:class:`AusBauteil`) kann ein E_eq haben.

Bis 2026-10-25 war die Art ein Text, und vier Schichten fragten ihn je fuer
sich ab: die Beschreibung, der Aufbau, das Rechenwerk und das Bildchen
einer Zeile. Jetzt loest der Aufbau ihn einmal auf
(:mod:`opencivil.projekt.aufbau.balkensystem`).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.berechnung import Berechnung, Formel, Vorgabe
from opencivil.core.einheiten import MIO_MM4, MM, MM2, Einheit, Groesse
from opencivil.core.latex import platzhalter_namen
from opencivil.core.protokoll import Abschnitt
from opencivil.core.wert import Quelle, WertDef
from opencivil.material.basis import mit_index
from opencivil.stabwerk.querschnitte import RECHTECK, Stabvorlage

#: Wie das System einen Wert anlegt: Kurzname, Zeichen, Einheit, Beschreibung, Stellen.
Definieren = Callable[[str, str, Einheit, str, int], WertDef]

#: Ein Umriss in mm -- der erste aussen, die weiteren Loecher.
Umriss = List[Sequence[Tuple[float, float]]]

#: Was ein Querschnitt von Hand oder aus einer Analyse traegt.
FLAECHENWERTE = (("A", MM2, 0, "Querschnittsfläche"), ("I", MIO_MM4, 2, "Flächenträgheitsmoment"))


@dataclass(frozen=True, kw_only=True)
class Stabquerschnitt(ABC):
    """Ein Querschnitt der Staebe, aufgeloest: woher ``A`` und ``I`` kommen."""

    kennung: str
    name: str
    herkunft: str
    """Woher, in Worten -- «Rechteck», «von Hand», «Platte «Decke»»."""

    fehler: str = ""
    """Was nicht geht -- dann rechnet er nicht, und kein Stab mit ihm."""

    @property
    def bauteil(self) -> str:
        """Die Kennung der Platte oder Analyse, deren Werte er liest -- leer bei einer Form."""
        return ""

    @property
    def modulfrage(self) -> Optional[Any]:
        """Die Frage nach seinem E_eq -- nur einer aus einem Bauteil kann eine haben."""
        return None

    @abstractmethod
    def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt,
                      index: str) -> Tuple[List[Berechnung], str, str]:
        """Die Berechnungen fuer ``A`` und ``I`` -- und deren Wert-IDs."""

    def umriss(self, loesung: Any) -> Umriss:
        """Sein Umriss in mm, fuer das Bildchen seiner Zeile -- ohne einen leer."""
        return []

    def _wert(self, definieren: Definieren, kurz: str, symbol: str, einheit: Einheit,
              beschreibung: str, stellen: int, index: str) -> WertDef:
        return definieren(f"{self.kennung}.{kurz}", mit_index(symbol, index), einheit,
                          f"{beschreibung}, {self.name}", stellen)

    def _formeln(self, vorlage: Stabvorlage, quellen: Mapping[str, str],
                 definieren: Definieren, abschnitt: Abschnitt,
                 index: str) -> Tuple[List[Berechnung], str, str]:
        """Die Formeln einer Vorlage, aus den Wert-IDs ihrer Masse."""
        quellen = dict(quellen)
        berechnungen: List[Berechnung] = []
        for f in vorlage.formeln:
            d = self._wert(definieren, f.kurzname, f.symbol, f.einheit, f.beschreibung,
                           f.stellen, index)
            berechnungen.append(Formel(
                id=d.id, ausgabe=d, funktion=f.funktion, vorlage=f.vorlage,
                eingaben={n: quellen[n] for n in platzhalter_namen(f.vorlage)},
                titel=f"{f.beschreibung}, «{self.name}» ({self.herkunft})", name=f.name,
                abschnitt=abschnitt))
            quellen[f.kurzname] = d.id
        return berechnungen, quellen["A"], quellen["I"]

    def _a_und_i(self, definieren: Definieren, index: str,
                 berechnung: Callable[[WertDef, str, str], Berechnung]
                 ) -> Tuple[List[Berechnung], str, str]:
        """``A`` und ``I`` je als eine Berechnung -- von Hand eine Vorgabe, sonst ein Bezug."""
        berechnungen = [berechnung(self._wert(definieren, kurz, kurz, einheit, beschreibung,
                                              stellen, index), kurz, beschreibung)
                        for kurz, einheit, stellen, beschreibung in FLAECHENWERTE]
        return berechnungen, berechnungen[0].id, berechnungen[1].id


@dataclass(frozen=True, kw_only=True)
class NachVorlage(Stabquerschnitt):
    """Nach einer Vorlage: ihre Masse als Vorgaben, ihre Formeln."""

    vorlage: Stabvorlage
    masse: Mapping[str, float]
    """Die Masse der Vorlage in mm -- was fehlte, mit seiner Vorgabe."""

    def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt,
                      index: str) -> Tuple[List[Berechnung], str, str]:
        berechnungen: List[Berechnung] = []
        quellen = {}
        for mass in self.vorlage.masse:
            wert = self.masse[mass.schluessel]
            d = self._wert(definieren, mass.schluessel, mass.symbol, MM, mass.beschriftung,
                           0 if float(wert).is_integer() else 1, index)
            berechnungen.append(Vorgabe(id=d.id, ausgabe=d, groesse=Groesse(wert, MM),
                                        abschnitt=abschnitt, stumm=True))
            quellen[mass.schluessel] = d.id
        formeln, A, I = self._formeln(self.vorlage, quellen, definieren, abschnitt, index)
        return berechnungen + formeln, A, I

    def umriss(self, loesung: Any) -> Umriss:
        return self.vorlage.umriss(self.masse)


@dataclass(frozen=True, kw_only=True)
class VonHand(Stabquerschnitt):
    """Kennwerte von Hand: ``A`` in mm², ``I`` in 10⁶ mm⁴. Ein Umriss fehlt."""

    masse: Mapping[str, float]

    def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt,
                      index: str) -> Tuple[List[Berechnung], str, str]:
        return self._a_und_i(definieren, index, lambda d, kurz, beschreibung: Vorgabe(
            id=d.id, ausgabe=d, groesse=Groesse(self.masse.get(kurz, 0.0), d.einheit),
            quelle=Quelle.EINGABE, titel=f"{beschreibung}, «{self.name}» (von Hand)",
            abschnitt=abschnitt))


@dataclass(frozen=True, kw_only=True)
class AusBauteil(Stabquerschnitt):
    """Aus einem Bauteil des Projekts -- seine Werte gehen ein, und er kann ein E_eq haben."""

    bezug: str
    """Die Kennung der Platte oder Analyse."""

    quelle: Mapping[str, str] = field(default_factory=dict)
    """Die Wert-IDs, aus denen er rechnet."""

    eq: Optional[Any] = None
    """
    Die Frage nach seinem E_eq (:class:`~opencivil.spannungsanalyse.modul.Modulfrage`)
    -- sie gilt fuer die Staebe, die sein Material nehmen; ``None``: E_cm. Sie
    baut ihre Berechnungen selbst ein.
    """

    @property
    def bauteil(self) -> str:
        return self.bezug

    @property
    def modulfrage(self) -> Optional[Any]:
        return self.eq


@dataclass(frozen=True, kw_only=True)
class AusPlatte(AusBauteil):
    """Der Streifen ``b × h`` einer Platte -- ``quelle`` sind ``b`` und ``h``."""

    def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt,
                      index: str) -> Tuple[List[Berechnung], str, str]:
        return self._formeln(RECHTECK, self.quelle, definieren, abschnitt, index)

    def umriss(self, loesung: Any) -> Umriss:
        werte = [loesung.werte.get(self.quelle[k]) for k in ("b", "h")]
        if not all(werte):
            return []
        b, h = (w.groesse.in_einheit(MM) for w in werte)
        return RECHTECK.umriss({"b": b, "h": h})


@dataclass(frozen=True, kw_only=True)
class AusAnalyse(AusBauteil):
    """Der Bruttoquerschnitt einer Querschnittsanalyse -- ``quelle`` sind ``A`` und ``I``."""

    flaechen: Tuple[Sequence[Tuple[float, float]], ...] = ()
    """Die Polygone ihrer Flaechen, in mm -- Aussparungen mit, das Bild fuellt gerade-ungerade."""

    def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt,
                      index: str) -> Tuple[List[Berechnung], str, str]:
        return self._a_und_i(definieren, index, lambda d, kurz, beschreibung: Formel(
            id=d.id, ausgabe=d, funktion=_derselbe, eingaben={"wert": self.quelle[kurz]},
            titel=f"{beschreibung}, «{self.name}» (Bruttoquerschnitt der {self.herkunft})",
            abschnitt=abschnitt))

    def umriss(self, loesung: Any) -> Umriss:
        return list(self.flaechen)


def _derselbe(wert: Groesse) -> Groesse:
    return wert
