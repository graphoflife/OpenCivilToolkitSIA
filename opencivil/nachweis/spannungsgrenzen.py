"""
opencivil/nachweis/spannungsgrenzen.py -- wogegen die Stahlspannung gehalten wird.

VERANTWORTUNG:
Die zulaessige Stahlspannung der Gebrauchsnachweise, an der Platte wie am
gezeichneten Querschnitt (:mod:`opencivil.nachweis.spannungsbegrenzung`):

* **die Grenzen** -- gegen das Fliessen ``f_yd - 80 N/mm²``
  (:class:`GrenzeGegenFliessen`), aus der Rissbreite ``sigma_s,adm``
  (:class:`GrenzeAusRissbreite`), jede mit ihren Woertern, Eingaben und
  ihrem Absatz in der Herleitung (:class:`Spannungsgrenze`);
* **die Stellen**, an denen gemessen wird -- bei der Platte ihre Lagen, beim
  gezeichneten Querschnitt jeder Stab (:class:`Stelle`) --, und je Stelle
  ihre Grenze, in Gruppen gleicher Grenze hergeleitet (:class:`Grenzen`).

Gegen das Fliessen gilt je Stahl dieselbe Zahl, fuer jede Geometrie
(:func:`gegen_fliessen`); mit welchem Durchmesser die Rissbreite zaehlt, sagt
die Geometrie selbst (:meth:`~opencivil.nachweis.spannungsbegrenzung.Stahlspannungsort.aus_rissbreite`).
Bis 2026-10-17 standen die Grenzen im Modul des Nachweises und fuer den
gezeichneten Querschnitt ein zweites Mal in ``stabgrenzen.py``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.einheiten import N_PRO_MM2, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, kennung_aus
from opencivil.material.basis import Baustoff, mit_index
from opencivil.nachweis.rissanforderung import Rissanforderung

if TYPE_CHECKING:
    from opencivil.nachweis.spannungsbegrenzung import Stahlspannungsort
    from opencivil.nachweis.stabgrenzen import Stabangabe

#: Abstand zur Bemessungsfliessgrenze, in Pa. SIA 262:2025, Tabelle 17.
FLIESSABSTAND = 80e6


# ===========================================================================
# Stellen und ihre Grenzen
# ===========================================================================


@dataclass(frozen=True)
class Stelle:
    """Wo eine Stahlspannung gemessen wird: eine Lage der Platte, ein Stab des gezeichneten Querschnitts."""

    stahl: Baustoff
    E_s: float
    eps_y: float
    """Die Fliessdehnung ``f_s / E_s``, im Wertesatz der Wahl."""


@dataclass(frozen=True)
class Stahlzustand:
    """
    Was ein Ort fuer eine Rechnung vorbereitet -- aus ihren Eingaben: die
    Stellen und ihre Staehle. Jeder Ort fuegt hinzu, was nur er braucht.
    """

    stellen: Tuple[Stelle, ...]
    staehle: Tuple[Baustoff, ...]
    """Jeder Stahl der Stellen einmal, in der Folge, in der seine Grenze hergeleitet wird."""


@dataclass
class Grenzgruppe:
    """Stellen mit derselben zulaessigen Spannung -- und woraus sie entsteht."""

    sigma: float
    """``sigma_s,adm`` in Pa."""

    stahl: Baustoff
    stab: Optional["Stabangabe"] = None
    """
    Nur beim gezeichneten Querschnitt, wo die Rissbreite zaehlt: ein Stab der
    Gruppe, fuer Durchmesser und Beton. Bei normaler Anforderung, gegen das
    Fliessen und an der Platte gilt die Grenze fuer jede Stelle des Stahls.
    """

    stellen: List[int] = field(default_factory=list)
    """Die Stellen der Gruppe, nach ihrer Nummer."""

    wert: Optional[Wert] = None
    """Die Grenze, wie sie in Herleitung und Vergleich steht -- gesetzt beim Protokollieren."""


@dataclass(frozen=True)
class Grenzen:
    """Die Grenze jeder Stelle -- und die Gruppen, in denen sie hergeleitet wird."""

    gruppen: List[Grenzgruppe]
    je_stelle: List[int]
    """Je Stelle die Nummer ihrer Gruppe."""

    def gruppe(self, i: int) -> Grenzgruppe:
        return self.gruppen[self.je_stelle[i]]

    def sigma(self, i: int) -> float:
        return self.gruppe(i).sigma

    @property
    def strengste(self) -> int:
        """Die Stelle mit der kleinsten Grenze -- sie steht da, wo keine gezogen ist."""
        return min(range(len(self.je_stelle)), key=self.sigma)


def nach_stahl(zustand: Stahlzustand, sigma: Callable[[Baustoff], float]) -> Grenzen:
    """
    Je Stahl eine Gruppe, in der Folge der Staehle des Zustands -- jede
    Stelle in der ihres Stahls. ``sigma`` gibt die Grenze eines Stahls.
    """
    nummer = {s.id: i for i, s in enumerate(zustand.staehle)}
    gruppen = [Grenzgruppe(sigma=sigma(s), stahl=s) for s in zustand.staehle]
    je_stelle = [nummer[st.stahl.id] for st in zustand.stellen]
    for i, gruppe in enumerate(je_stelle):
        gruppen[gruppe].stellen.append(i)
    return Grenzen(gruppen=gruppen, je_stelle=je_stelle)


def je_stahl(name: str, symbol: str, stahl: Baustoff,
             alle: Sequence[Baustoff]) -> Tuple[str, str]:
    """
    Name und Zeichen eines Werts, der zu einem Stahl gehoert -- mit dem
    Stahl daran, sobald es mehr als einen gibt.
    """
    if len(alle) == 1:
        return name, symbol
    return f"{name}_{kennung_aus(stahl.id)}", mit_index(symbol, stahl.symbol_index)


def gegen_fliessen(zustand: Stahlzustand, e: Eingaben, p: Protokoll, basis: str) -> Grenzen:
    """
    ``f_yd - 80 N/mm²`` je Stahl, hergeleitet -- fuer jede Geometrie dasselbe:
    der Durchmesser zaehlt hier nicht. Setzt :attr:`Grenzgruppe.wert`.
    """
    grenzen = nach_stahl(zustand, lambda s: abs(e.g(s.eingabename("f_yd")).si) - FLIESSABSTAND)
    # Die 80 N/mm² haben kein Zeichen -- sie stehen als Zahl in der Formel.
    abstand = Groesse.aus_si(FLIESSABSTAND, N_PRO_MM2).als_latex(0)
    for gruppe in grenzen.gruppen:
        name, symbol = je_stahl("sigma_s_adm", r"\sigma_{s,adm}", gruppe.stahl, zustand.staehle)
        gruppe.wert = Zwischenwerte(basis).spannung(name, symbol, gruppe.sigma, "Widerstand")
        p.formel(gruppe.wert, f"@f_yd - {abstand}", {"f_yd": e[gruppe.stahl.eingabename("f_yd")]},
                 titel="Zulässige Stahlspannung", referenz=GrenzeGegenFliessen.referenz)
    return grenzen


# ===========================================================================
# Die Grenzen
# ===========================================================================


class Spannungsgrenze(ABC):
    """
    Wogegen ein Stahlspannungsnachweis haelt -- und alles, was nur dazugehoert.

    Die Zahl, die Eingaben, aus denen sie entsteht, und die Absaetze, die sie
    begruenden. Dazu die Woerter, unter denen der Nachweis ueberall erscheint:
    Wert-ID, Symbol, Tabellenzeile, Ueberschrift. Zwei Grenzen mit gleichem
    ``langname`` stuenden als zwei ununterscheidbare Zeilen in derselben
    Tabelle.

    Die Absaetze sind **nicht** zu einem Text mit Platzhaltern
    zusammenzulegen: der eine argumentiert fuer ``f_yd``, der andere fuer
    ``f_yk``. Ein Text, der beides behauptet, behauptet nichts.

    Eine Grenze ist eine Klasse, kein Gegenstand: was sie von der Geometrie
    braucht, fragt sie den Ort
    (:class:`~opencivil.nachweis.spannungsbegrenzung.Stahlspannungsort`).
    """

    #: Teil der Wert-ID: ``<bauteil>.nachweis.<idteil>``, bei der Platte mit der Richtung.
    idteil: str
    #: Index am Erfuellungsgrad.
    symbolteil: str
    #: Kurzzeichen im Urteil.
    art: str
    #: Spalte «Nachweis» der Zusammenfassung.
    langname: str
    #: Thema in der Formelsammlung, und wovon der Erfuellungsgrad spricht.
    thema: str
    #: «häufiger» / «quasi-ständiger» -- im Titel.
    einwirkung: str
    #: Index an M_Ed und N_Ed in der Herleitung.
    lastindex: str
    #: Ueberschrift je Fall.
    fallwort: str
    referenz: str
    #: Der erste Satz der Herleitung: wozu der Nachweis da ist.
    einleitung: str

    @classmethod
    def gilt_bei(cls, anforderung: Rissanforderung) -> bool:
        """Ob der Nachweis bei dieser Rissanforderung verlangt ist."""
        return True

    @classmethod
    @abstractmethod
    def bezuege(cls, ort: "Stahlspannungsort") -> List[Eingabebezug]:
        """Was nur diese Grenze braucht, zusaetzlich zur gemeinsamen Rechnung."""

    @classmethod
    @abstractmethod
    def bestimmen(cls, ort: "Stahlspannungsort", zustand: Stahlzustand, e: Eingaben,
                  p: Protokoll, anforderung: Rissanforderung, basis: str) -> Grenzen:
        """
        Die zulaessige Stahlspannung jeder Stelle -- gerechnet und
        mitgeschrieben, mit :attr:`Grenzgruppe.wert` gesetzt.
        """

    @classmethod
    @abstractmethod
    def festlegung(cls, p: Protokoll, ort: "Stahlspannungsort") -> None:
        """Welche Werte die Grenze ansetzt, und warum -- nur der Absatz."""


class GrenzeGegenFliessen(Spannungsgrenze):
    """
    ``f_yd - 80 N/mm²`` unter haeufiger Einwirkung -- das Fliessen verhindern.

    Nur bei erhoehter und hoher Anforderung -- bei normaler steht in
    Tabelle 17 ein Strich (:attr:`Rissanforderung.gegen_fliessen`). Der
    Aufbau fragt :meth:`gilt_bei`.
    """

    idteil = "spannung"
    symbolteil = r"\sigma"
    art = "σ_s"
    langname = "Risse: Häufige Lastfälle"
    thema = "Stahlspannung gegen Fliessen"
    einwirkung = "häufiger"
    lastindex = "häufig"
    fallwort = "Häufiger Lastfall"
    referenz = "SIA 262:2025, Tabelle 17"
    einleitung = ("Unter häufiger Einwirkung darf die Bewehrung nicht "
                  "fliessen – sonst bleiben Risse und Durchbiegung dauerhaft.")

    @classmethod
    def gilt_bei(cls, anforderung: Rissanforderung) -> bool:
        return anforderung.gegen_fliessen

    @classmethod
    def bezuege(cls, ort: "Stahlspannungsort") -> List[Eingabebezug]:
        return ort.stahlbezuege(("f_yd",))

    @classmethod
    def bestimmen(cls, ort: "Stahlspannungsort", zustand: Stahlzustand, e: Eingaben,
                  p: Protokoll, anforderung: Rissanforderung, basis: str) -> Grenzen:
        return gegen_fliessen(zustand, e, p, basis)

    @classmethod
    def festlegung(cls, p: Protokoll, ort: "Stahlspannungsort") -> None:
        p.erklaerung(
            "Drittens die Grenze: sie rechnet mit dem Bemessungswert, "
            "σ_s,adm = f_yd − 80 N/mm², und nicht mit f_yk − 80. Die Norm sagt "
            "an dieser Stelle nicht eindeutig, welcher Wert gemeint ist; f_yd "
            "ist die strengere Wahl – die Grenze liegt rund 15 % tiefer –, "
            "gewählt ist deshalb die Seite, auf der man nicht danebenliegen "
            "kann. Das ist etwas anderes als das Fliessplateau oben: dort geht "
            "es darum, was der Stahl tut, hier darum, wie viel Abstand man "
            "davon verlangt."
        )


class GrenzeAusRissbreite(Spannungsgrenze):
    """
    ``sigma_s,adm`` aus der Rissanforderung, unter quasi-staendiger Einwirkung.

    Dieselbe zulaessige Spannung wie bei der Zwaengung -- dieselbe Funktion,
    :func:`mindestbewehrung.zulaessige_stahlspannung`, und keine zweite
    Fassung davon. Bei normaler Anforderung ``f_yk``: die Bewehrung darf
    unter Dauerlast nicht fliessen. Bei erhoehter und hoher zusaetzlich die
    Wurzelformel mit ``w_nom``.

    **Mit welchem Durchmesser, sagt die Geometrie**
    (:meth:`~opencivil.nachweis.spannungsbegrenzung.Stahlspannungsort.aus_rissbreite`):
    die Platte nimmt den dicksten Stab der Tragrichtung, der gezeichnete
    Querschnitt je Stab den eigenen.
    """

    idteil = "spannung_riss"
    symbolteil = r"\sigma,w"
    art = "σ_s,w"
    langname = "Risse: Quasi-ständige Lastfälle"
    thema = "Stahlspannung aus Rissbreite"
    einwirkung = "quasi-ständiger"
    lastindex = r"\text{quasi-ständig}"
    fallwort = "Quasi-ständiger Lastfall"
    referenz = "SIA 262:2025, 4.4.2"
    einleitung = ("Unter quasi-ständiger Einwirkung begrenzt die "
                  "Stahlspannung die Rissbreite – dieselbe Grenze wie bei der "
                  "Zwängung, nur dass die Spannung hier aus den Lasten kommt "
                  "und nicht aus einer aufgezwungenen Verformung.")

    @classmethod
    def bezuege(cls, ort: "Stahlspannungsort") -> List[Eingabebezug]:
        return ort.rissbreitenbezuege()

    @classmethod
    def bestimmen(cls, ort: "Stahlspannungsort", zustand: Stahlzustand, e: Eingaben,
                  p: Protokoll, anforderung: Rissanforderung, basis: str) -> Grenzen:
        return ort.aus_rissbreite(zustand, e, p, anforderung, basis)

    @classmethod
    def festlegung(cls, p: Protokoll, ort: "Stahlspannungsort") -> None:
        p.erklaerung(
            "Drittens die Grenze: dieselbe wie bei der Zwängung, mit f_yk und "
            "bei erhöhter und hoher Anforderung zusätzlich begrenzt durch die "
            f"Rissbreite. {ort.regel_der_rissbreite}"
        )
