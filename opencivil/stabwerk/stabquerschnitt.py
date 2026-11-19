"""
opencivil/stabwerk/stabquerschnitt.py -- woher A und I eines Stabs kommen.

VERANTWORTUNG:
Ein Querschnitt der Staebe, aufgeloest: je Art eine Klasse, die ihre
Berechnungen fuer die Kennwerte des Stabs und ihren Umriss selbst traegt.
Welche Kennwerte, sagt das System: der ebene Rahmen braucht ``A`` und ``I``
(:data:`EBEN`), das Stabwerk im Raum ``A``, ``I_y``, ``I_z`` und ``I_T``
(:data:`RAEUMLICH`). Die Arten --

* nach Vorlage (:class:`NachVorlage`) -- die Formeln der Vorlage
  (:mod:`~opencivil.stabwerk.querschnitte`), die Masse als Vorgaben; ein
  Stahlprofil ebenso, mit den Massen aus der Tabelle
  (:mod:`~opencivil.stabwerk.profilformen`). Das ``I`` des ebenen Rahmens
  ist ihr ``I_y`` -- bei einem Profil, das sich um z biegt, ihr ``I_z``;
* von Hand (:class:`VonHand`) -- die Kennwerte als Eingaben;
* aus einer Platte (:class:`AusPlatte`) -- die Formeln des Rechtecks mit
  ``b`` und ``h`` der Platte, im Raum mit ``I_z`` und ``I_T`` dazu;
* aus einer Querschnittsanalyse (:class:`AusAnalyse`) -- ``A`` und ``I_y``
  ihres Bruttoquerschnitts, im Raum ``I_z`` dazu und ``I_T``, das sie dafuer
  numerisch rechnet (:mod:`~opencivil.querschnitt.torsion`), und ``I_yz``:
  daran prueft die Rechnung, ob y und z Hauptachsen sind.

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
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

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


@dataclass(frozen=True)
class Kennwert:
    """Ein Wert, den ein Stab von seinem Querschnitt braucht -- wie er heisst und gezeigt wird."""

    kurzname: str
    einheit: Einheit
    stellen: int
    beschreibung: str
    symbol: str = ""
    """In LaTeX, wo es anders heisst als ``kurzname`` -- ``I_{yz}``."""


_A = Kennwert("A", MM2, 0, "Querschnittsfläche")

#: Was ein Stab des ebenen Rahmens braucht: ``I`` um die Achse senkrecht zur Ebene.
EBEN = (_A, Kennwert("I", MIO_MM4, 2, "Flächenträgheitsmoment"))

#: Was ein Stab im Raum braucht (:mod:`opencivil.stabwerk3d`).
RAEUMLICH = (_A, Kennwert("I_y", MIO_MM4, 2, "Flächenträgheitsmoment um y"),
             Kennwert("I_z", MIO_MM4, 2, "Flächenträgheitsmoment um z"),
             Kennwert("I_T", MIO_MM4, 2, "Torsionsträgheitsmoment"))

#: Kein Kennwert eines Stabs: wer mit ``I_y`` und ``I_z`` rechnet, nimmt y
#: und z als Hauptachsen. Ein Querschnitt aus einer Analyse bringt es dann
#: mit -- nur er kann unsymmetrisch sein --, und die Rechnung prueft, wie
#: weit sie es nicht sind (:mod:`opencivil.stabwerk.rechnung`).
DEVIATIONSMOMENT = Kennwert("I_yz", MIO_MM4, 2, "Deviationsmoment", symbol="I_{yz}")

#: Ab so viel |I_yz| / min(I_y; I_z) sagt ein Hinweis, dass y und z keine
#: Hauptachsen sind: so stark kruemmt ein Moment um die steifere Achse den
#: Stab auch um die weichere, und die Rechnung laesst das weg. Nach Vorgabe,
#: nicht nachgeschlagen (Benutzer, 2026-11-19: ein Hinweis, keine Drehung).
KOPPLUNG = 0.05

#: Je Kennwert die Wert-ID, die ihn liefert.
Werte = Dict[str, str]


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
    def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str,
                      kennwerte: Sequence[Kennwert] = EBEN) -> Tuple[List[Berechnung], Werte]:
        """Die Berechnungen fuer die ``kennwerte`` -- und je Kennwert seine Wert-ID."""

    def umriss(self, loesung: Any) -> Umriss:
        """Sein Umriss in mm, fuer das Bildchen seiner Zeile -- ohne einen leer."""
        return []

    def _wert(self, definieren: Definieren, kurz: str, symbol: str, einheit: Einheit,
              beschreibung: str, stellen: int, index: str) -> WertDef:
        return definieren(f"{self.kennung}.{kurz}", mit_index(symbol, index), einheit,
                          f"{beschreibung}, {self.name}", stellen)

    def _formeln(self, vorlage: Stabvorlage, quellen: Mapping[str, str],
                 definieren: Definieren, abschnitt: Abschnitt, index: str,
                 kennwerte: Sequence[Kennwert], traegheit: str = "I_y"
                 ) -> Tuple[List[Berechnung], Werte]:
        """
        Die Formeln einer Vorlage, aus den Wert-IDs ihrer Masse -- je
        Kennwert die mit seinem Kurznamen, als ``I`` des ebenen Rahmens die
        mit dem Kurznamen ``traegheit``. Gerechnet wird davon nur, was die
        Kennwerte brauchen: das Rechenwerk folgt den Zielen.
        """
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
        return berechnungen, {k.kurzname: quellen[traegheit if k.kurzname == "I" else k.kurzname]
                              for k in kennwerte}

    def _je_kennwert(self, definieren: Definieren, index: str, kennwerte: Sequence[Kennwert],
                     berechnung: Callable[[WertDef, Kennwert], Berechnung]
                     ) -> Tuple[List[Berechnung], Werte]:
        """Jeder Kennwert als eine Berechnung -- von Hand eine Vorgabe, sonst ein Bezug."""
        berechnungen = [berechnung(self._wert(definieren, k.kurzname, k.symbol or k.kurzname,
                                              k.einheit, k.beschreibung, k.stellen, index), k)
                        for k in kennwerte]
        return berechnungen, {k.kurzname: b.id for k, b in zip(kennwerte, berechnungen)}


@dataclass(frozen=True, kw_only=True)
class NachVorlage(Stabquerschnitt):
    """Nach einer Vorlage: ihre Masse als Vorgaben, ihre Formeln."""

    vorlage: Stabvorlage
    masse: Mapping[str, float]
    """Die Masse der Vorlage in mm -- was fehlte, mit seiner Vorgabe."""

    traegheit: str = "I_y"
    """Welche ihrer Formeln das ``I`` des ebenen Rahmens ist -- bei einem Profil um z ``I_z``."""

    def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str,
                      kennwerte: Sequence[Kennwert] = EBEN) -> Tuple[List[Berechnung], Werte]:
        berechnungen: List[Berechnung] = []
        quellen = {}
        for mass in self.vorlage.masse:
            wert = self.masse[mass.schluessel]
            d = self._wert(definieren, mass.schluessel, mass.symbol, mass.einheit,
                           mass.beschriftung, _stellen(wert), index)
            berechnungen.append(Vorgabe(id=d.id, ausgabe=d, groesse=Groesse(wert, mass.einheit),
                                        abschnitt=abschnitt, stumm=True))
            quellen[mass.schluessel] = d.id
        formeln, werte = self._formeln(self.vorlage, quellen, definieren, abschnitt, index,
                                       kennwerte, self.traegheit)
        return berechnungen + formeln, werte

    def umriss(self, loesung: Any) -> Umriss:
        return self.vorlage.umriss(self.masse)


@dataclass(frozen=True, kw_only=True)
class VonHand(Stabquerschnitt):
    """Kennwerte von Hand: ``A`` in mm², die Traegheitsmomente in 10⁶ mm⁴. Ein Umriss fehlt."""

    masse: Mapping[str, float]

    def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str,
                      kennwerte: Sequence[Kennwert] = EBEN) -> Tuple[List[Berechnung], Werte]:
        return self._je_kennwert(definieren, index, kennwerte, lambda d, k: Vorgabe(
            id=d.id, ausgabe=d, groesse=Groesse(self.masse.get(k.kurzname, 0.0), d.einheit),
            quelle=Quelle.EINGABE, titel=f"{k.beschreibung}, «{self.name}» (von Hand)",
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

    def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str,
                      kennwerte: Sequence[Kennwert] = EBEN) -> Tuple[List[Berechnung], Werte]:
        return self._formeln(RECHTECK, self.quelle, definieren, abschnitt, index, kennwerte)

    def umriss(self, loesung: Any) -> Umriss:
        werte = [loesung.werte.get(self.quelle[k]) for k in ("b", "h")]
        if not all(werte):
            return []
        b, h = (w.groesse.in_einheit(MM) for w in werte)
        return RECHTECK.umriss({"b": b, "h": h})


@dataclass(frozen=True, kw_only=True)
class AusAnalyse(AusBauteil):
    """
    Der Bruttoquerschnitt einer Querschnittsanalyse -- ``quelle`` je
    Kennwert, ``I`` ist ``I_y``. Mit ``I_y`` und ``I_z`` gefragt, gibt er
    ``I_yz`` dazu (:data:`DEVIATIONSMOMENT`).
    """

    flaechen: Tuple[Sequence[Tuple[float, float]], ...] = ()
    """Die Polygone ihrer Flaechen, in mm -- Aussparungen mit, das Bild fuellt gerade-ungerade."""

    def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str,
                      kennwerte: Sequence[Kennwert] = EBEN) -> Tuple[List[Berechnung], Werte]:
        if {"I_y", "I_z"} <= {k.kurzname for k in kennwerte}:
            kennwerte = (*kennwerte, DEVIATIONSMOMENT)
        return self._je_kennwert(definieren, index, kennwerte, lambda d, k: Formel(
            id=d.id, ausgabe=d, funktion=_derselbe, eingaben={"wert": self.quelle[k.kurzname]},
            titel=f"{k.beschreibung}, «{self.name}» (Bruttoquerschnitt der {self.herkunft})",
            abschnitt=abschnitt))

    def umriss(self, loesung: Any) -> Umriss:
        return list(self.flaechen)


def _derselbe(wert: Groesse) -> Groesse:
    return wert


def _stellen(wert: float) -> int:
    """So viele Nachkommastellen, wie ein Mass hat -- 8.75 bleibt 8.75, bis drei."""
    return next((n for n in range(3) if round(wert, n) == wert), 3)
