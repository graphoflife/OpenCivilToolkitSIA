"""
opencivil/nachweis/stabgrenzen.py -- die zulaessige Stahlspannung je Stab des gezeichneten Querschnitts.

VERANTWORTUNG:
Die Gebrauchsnachweise der Querschnittsanalyse (:mod:`opencivil.nachweis.qa_gebrauch`)
halten jeden Stab gegen seine eigene Grenze. Hier steht, wie ein Stab zu ihr
kommt und wie sie in die Herleitung kommt: aus der Rissbreite
(:func:`grenzen_aus_rissbreite`) oder gegen das Fliessen
(:func:`grenzen_gegen_fliessen`), mit denselben Funktionen wie bei der
Platte (:func:`~opencivil.nachweis.mindestbewehrung.zulaessige_stahlspannung`,
``f_yd - 80 N/mm²``).

JE STAB:
Die Platte haelt je Lage den dicksten Stab gegen die Rissbreite. Hier hat
jeder Stab seine Grenze -- mit seinem Durchmesser und dem ``f_ctm`` des
Betons, in dem er liegt (Benutzer, 2026-10-15). Staebe mit derselben Grenze
bilden eine Gruppe, die einmal hergeleitet wird (:class:`Grenzgruppe`).

DER FIKTIVE DURCHMESSER:
Eine verschmierte Linie hat keinen Durchmesser: sie bekommt einen fiktiven,
als laegen ihre Staebe 150 mm auseinander (Annahme des Benutzers,
2026-10-15)::

    ⌀_fikt = sqrt(4/π · A_s/l · s)        s = 150 mm

Nach Vorgabe, nicht nachgeschlagen: die Grenze je Stab und der fiktive
Durchmesser. Siehe ``notizbuch/Notizen/TODO.md``.

EINHEITEN:
SI-Basis; die Zeichnung in mm.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence

from opencivil.core.berechnung import Eingaben
from opencivil.core.einheiten import N_PRO_MM2, Groesse
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, kennung_aus
from opencivil.material.basis import Baustoff, mit_index
from opencivil.nachweis.mindestbewehrung import (
    RISSBREITE, protokoll_zulaessige_stahlspannung, zulaessige_stahlspannung,
)
from opencivil.nachweis.spannungsbegrenzung import FLIESSABSTAND, GrenzeGegenFliessen
from opencivil.querschnitt.analyse import Querschnittsanalyse, Stabgruppe
from opencivil.querschnitt.geometrie import Linienart, Punkt
from opencivil.querschnitt.interaktion import Querschnitt

#: Die Teilung, mit der eine verschmierte Linie einen fiktiven Durchmesser
#: bekommt, in m -- Annahme des Benutzers, 2026-10-15.
FIKTIVE_TEILUNG = 0.150


@dataclass(frozen=True)
class Stabangabe:
    """Ein Stab -- oder ein Stueck einer verschmierten Linie --, wie die Nachweise ihn sehen."""

    element: Stabgruppe
    """Das Element der Zeichnung, aus dem er stammt."""

    lage: Punkt
    """in m."""

    flaeche: float
    """in m²."""

    beton: Baustoff
    """Der Beton, in dem er liegt: er gibt ``f_ctm`` fuer die Rissbreite."""

    durchmesser: float
    """in m -- bei einer verschmierten Linie der fiktive."""

    @property
    def stahl(self) -> Baustoff:
        return self.element.stahl

    @property
    def verschmiert(self) -> bool:
        return self.element.art == Linienart.FLAECHE.value

    @property
    def ort(self) -> str:
        """Wie er in einem Satz heisst: Element und Lage, in mm."""
        return (f"{self.element.name} (y = {self.lage[0] * 1e3:.0f} mm, "
                f"z = {self.lage[1] * 1e3:.0f} mm)")


def fiktiver_durchmesser(element: Stabgruppe) -> float:
    """
    Der Durchmesser einer verschmierten Linie, in m: ihre Stahlflaeche je
    Laenge, auf Staebe im Abstand :data:`FIKTIVE_TEILUNG` verteilt.
    """
    laenge = math.hypot(element.bis[0] - element.von[0], element.bis[1] - element.von[1])
    je_stab = element.flaeche / laenge * FIKTIVE_TEILUNG * 1e3   # mm²
    return math.sqrt(4.0 / math.pi * je_stab) * 1e-3


def stabangaben(analyse: Querschnittsanalyse, q: Querschnitt,
                herkunft: Sequence[Stabgruppe]) -> List[Stabangabe]:
    """Je Bewehrung des Querschnitts ihre Angaben -- in derselben Reihenfolge wie dort."""
    angaben = []
    for b, element in zip(q.bewehrung, herkunft):
        verschmiert = element.art == Linienart.FLAECHE.value
        angaben.append(Stabangabe(
            element=element, lage=b.lage, flaeche=b.flaeche,
            beton=analyse.beton_an((b.lage[0] * 1e3, b.lage[1] * 1e3)),
            durchmesser=(fiktiver_durchmesser(element) if verschmiert
                         else element.durchmesser * 1e-3)))
    return angaben


@dataclass
class Grenzgruppe:
    """Staebe mit derselben zulaessigen Spannung -- und woraus sie entsteht."""

    sigma: float
    """``sigma_s,adm`` in Pa."""

    stahl: Baustoff
    stab: Optional[Stabangabe]
    """
    Ein Stab der Gruppe, fuer Durchmesser und Beton -- nur, wo die Rissbreite
    zaehlt. Bei normaler Anforderung und gegen das Fliessen gilt die Grenze
    fuer jeden Stab des Stahls.
    """

    staebe: List[int] = field(default_factory=list)
    """Die Staebe, nach ihrer Stelle in :func:`stabangaben`."""

    wert: Optional[Wert] = None
    """Die Grenze, wie sie in Herleitung und Vergleich steht -- gesetzt beim Protokollieren."""


@dataclass(frozen=True)
class Grenzen:
    """Die Grenze jedes Stabs -- und die Gruppen, in denen sie hergeleitet wird."""

    gruppen: List[Grenzgruppe]
    je_stab: List[int]
    """Je Stab die Stelle seiner Gruppe."""

    def gruppe(self, i: int) -> Grenzgruppe:
        return self.gruppen[self.je_stab[i]]

    def sigma(self, i: int) -> float:
        return self.gruppe(i).sigma

    @property
    def strengste(self) -> int:
        """Der Stab mit der kleinsten Grenze -- er steht da, wo keiner gezogen ist."""
        return min(range(len(self.je_stab)), key=self.sigma)


def _gruppieren(staebe: Sequence[Stabangabe], schluessel: Callable[[Stabangabe], tuple],
                bilden: Callable[[Stabangabe], Grenzgruppe]) -> Grenzen:
    """Je Schluessel eine Gruppe, in der Reihenfolge ihres ersten Stabs."""
    gruppen: List[Grenzgruppe] = []
    stelle: Dict[tuple, int] = {}
    je_stab = []
    for i, stab in enumerate(staebe):
        k = schluessel(stab)
        if k not in stelle:
            stelle[k] = len(gruppen)
            gruppen.append(bilden(stab))
        gruppen[stelle[k]].staebe.append(i)
        je_stab.append(stelle[k])
    return Grenzen(gruppen=gruppen, je_stab=je_stab)


def grenzen_aus_rissbreite(analyse: Querschnittsanalyse, e: Eingaben,
                           staebe: Sequence[Stabangabe], anforderung: str) -> Grenzen:
    """
    ``sigma_s,adm`` je Stab aus der Rissanforderung: bei normaler Anforderung
    ``f_yk`` seines Stahls, bei erhoehter und hoher dazu die Rissbreite mit
    seinem Durchmesser und dem ``f_ctm`` seines Betons.
    """
    mit_rissbreite = RISSBREITE[anforderung] is not None

    def schluessel(s: Stabangabe) -> tuple:
        if not mit_rissbreite:
            return (s.stahl.id,)
        return (s.stahl.id, s.beton.id, s.verschmiert, round(s.durchmesser, 9))

    def bilden(s: Stabangabe) -> Grenzgruppe:
        sigma = zulaessige_stahlspannung(
            anforderung=anforderung, f_yk=abs(analyse.kennwert(e, s.stahl, "f_yk")),
            E_s=analyse.kennwert(e, s.stahl, "E_s"),
            f_ctm=abs(analyse.kennwert(e, s.beton, "f_ctm")), durchmesser=s.durchmesser)
        return Grenzgruppe(sigma=sigma, stahl=s.stahl, stab=s if mit_rissbreite else None)
    return _gruppieren(staebe, schluessel, bilden)


def grenzen_gegen_fliessen(analyse: Querschnittsanalyse, e: Eingaben,
                           staebe: Sequence[Stabangabe]) -> Grenzen:
    """``f_yd - 80 N/mm²`` je Stahl -- der Durchmesser zaehlt hier nicht."""
    return _gruppieren(
        staebe, lambda s: (s.stahl.id,),
        lambda s: Grenzgruppe(sigma=abs(analyse.kennwert(e, s.stahl, "f_yd")) - FLIESSABSTAND,
                              stahl=s.stahl, stab=None))


#: Wie die Grenze aus der Rissbreite hier gemessen wird.
GRENZE_JE_STAB = (
    "Jeder gezogene Stab hält gegen seine eigene Grenze, mit seinem "
    "Durchmesser und dem f_ctm des Betons, in dem er liegt; massgebend ist "
    "der Stab mit dem kleinsten Erfüllungsgrad.")

#: Woher eine verschmierte Linie ihren Durchmesser hat.
FIKTIV = ("Eine verschmierte Linie hat keinen Durchmesser – sie bekommt einen "
          "fiktiven, als lägen ihre Stäbe 150 mm auseinander (Annahme).")


def protokoll_rissbreitengrenzen(p: Protokoll, e: Eingaben, analyse: Querschnittsanalyse,
                                 staebe: Sequence[Stabangabe], grenzen: Grenzen,
                                 anforderung: str, basis: str, *, referenz: str) -> None:
    """
    ``sigma_s,adm`` aus der Rissbreite, je Gruppe gleicher Staebe einmal
    hergeleitet -- vorher der fiktive Durchmesser jeder verschmierten Linie,
    die ihn braucht. Bei mehreren Gruppen danach eine Tabelle, welche Elemente
    zu welcher gehoeren. Setzt :attr:`Grenzgruppe.wert`.
    """
    fiktiv: Dict[str, Wert] = {}
    for gruppe in grenzen.gruppen:
        s = gruppe.stab
        if s is not None and s.verschmiert and s.element.kennung not in fiktiv:
            if not fiktiv:
                p.erklaerung(FIKTIV)
            fiktiv[s.element.kennung] = _protokoll_fiktiv(p, s, basis)
    mehrere = len(grenzen.gruppen) > 1
    for nummer, gruppe in enumerate(grenzen.gruppen, start=1):
        w = Zwischenwerte(f"{basis}.grenze{nummer}" if mehrere else basis)
        symbol = rf"\sigma_{{s,adm,{nummer}}}" if mehrere else r"\sigma_{s,adm}"
        gruppe.wert = w.spannung("sigma_s_adm", symbol, gruppe.sigma, "Widerstand")
        s = gruppe.stab
        # Bei normaler Anforderung zaehlen Durchmesser und Beton nicht: es
        # gilt f_yk, und die Herleitung zeigt nur das.
        beton = (s or staebe[gruppe.staebe[0]]).beton
        if s is None:
            durchmesser = w.laenge("dm", r"\varnothing", 0.0)
        elif s.verschmiert:
            durchmesser = fiktiv[s.element.kennung]
        else:
            durchmesser = w.laenge("dm", r"\varnothing", s.durchmesser, stellen=0)
        protokoll_zulaessige_stahlspannung(
            p, gruppe.wert, anforderung=anforderung,
            f_yk=e[analyse._name(gruppe.stahl, "f_yk")],
            E_s=e[analyse._name(gruppe.stahl, "E_s")], f_ctm=e[analyse._name(beton, "f_ctm")],
            durchmesser=durchmesser, basis=w.basis, referenz=referenz)
    if mehrere:
        _tabelle_grenzen(p, staebe, grenzen)


def protokoll_fliessgrenzen(p: Protokoll, e: Eingaben, analyse: Querschnittsanalyse,
                            grenzen: Grenzen, basis: str) -> None:
    """``f_yd - 80 N/mm²`` je Stahl -- wie bei der Platte. Setzt :attr:`Grenzgruppe.wert`."""
    abstand = Groesse.aus_si(FLIESSABSTAND, N_PRO_MM2).als_latex(0)
    for gruppe in grenzen.gruppen:
        name, symbol = "sigma_s_adm", r"\sigma_{s,adm}"
        if len(grenzen.gruppen) > 1:
            name = f"sigma_s_adm_{kennung_aus(gruppe.stahl.id)}"
            symbol = mit_index(symbol, gruppe.stahl.symbol_index)
        gruppe.wert = Zwischenwerte(basis).spannung(name, symbol, gruppe.sigma, "Widerstand")
        p.formel(gruppe.wert, f"@f_yd - {abstand}",
                 {"f_yd": e[analyse._name(gruppe.stahl, "f_yd")]},
                 titel="Zulässige Stahlspannung", referenz=GrenzeGegenFliessen.referenz)


def _protokoll_fiktiv(p: Protokoll, s: Stabangabe, basis: str) -> Wert:
    """Der fiktive Durchmesser einer verschmierten Linie, hergeleitet."""
    g = s.element
    w = Zwischenwerte(f"{basis}.{kennung_aus(g.kennung)}")
    laenge = math.hypot(g.bis[0] - g.von[0], g.bis[1] - g.von[1]) * 1e-3
    durchmesser = w.laenge("dm", r"\varnothing_{fikt}", s.durchmesser)
    p.formel(durchmesser, r"\sqrt{\frac{4}{\pi} \cdot \frac{@A_s}{@l} \cdot @s}",
             {"A_s": w.flaeche("A_s", "A_s", g.flaeche * 1e-6, "Stahlfläche der Linie"),
              "l": w.laenge("l", "l", laenge, "Länge der Linie", stellen=0),
              "s": w.laenge("s", "s", FIKTIVE_TEILUNG, "Angenommene Teilung", stellen=0)},
             titel=f"{g.name}: verschmiert, als Stäbe mit 150 mm Teilung",
             name="Fiktiver Durchmesser einer verschmierten Linie")
    return durchmesser


def _tabelle_grenzen(p: Protokoll, staebe: Sequence[Stabangabe], grenzen: Grenzen) -> None:
    """Welche Elemente zu welcher Grenze gehoeren."""
    zeilen = []
    for gruppe in grenzen.gruppen:
        elemente = ", ".join(dict.fromkeys(staebe[i].element.name for i in gruppe.staebe))
        zeilen.append([Mathe(gruppe.wert.symbol), elemente,
                       Mathe(fest(gruppe.sigma / 1e6, 0))])
    p.tabelle(kopf=["Grenze", "Elemente", Mathe(r"\sigma_{s,adm}\ [\mathrm{N/mm^2}]")],
              zeilen=zeilen, titel="Welche Stäbe welche Grenze haben", ausrichtung="llr")
