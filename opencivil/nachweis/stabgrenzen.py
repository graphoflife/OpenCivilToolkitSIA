"""
opencivil/nachweis/stabgrenzen.py -- die zulaessige Stahlspannung je Stab des gezeichneten Querschnitts.

VERANTWORTUNG:
Die Gebrauchsnachweise der Querschnittsanalyse (:mod:`opencivil.nachweis.qa_gebrauch`)
halten jeden Stab gegen seine eigene Grenze. Hier steht, wie ein Stab zu ihr
kommt und wie sie in die Herleitung kommt, wo die Rissbreite zaehlt
(:func:`grenzen_aus_rissbreite`), mit derselben Funktion wie bei der Platte
(:func:`~opencivil.nachweis.mindestbewehrung.zulaessige_stahlspannung`).
Gegen das Fliessen gilt je Stahl ``f_yd - 80 N/mm²``, fuer jede Geometrie
gleich (:func:`~opencivil.nachweis.spannungsgrenzen.gegen_fliessen`).

JE STAB:
Die Platte haelt je Lage den dicksten Stab gegen die Rissbreite. Hier hat
jeder Stab seine Grenze -- mit seinem Durchmesser und dem ``f_ctm`` des
Betons, in dem er liegt (Benutzer, 2026-10-15). Staebe mit derselben Grenze
bilden eine Gruppe, die einmal hergeleitet wird
(:class:`~opencivil.nachweis.spannungsgrenzen.Grenzgruppe`).

DER FIKTIVE DURCHMESSER:
Eine verschmierte Linie hat keinen Durchmesser: sie bekommt einen fiktiven,
als laegen ihre Staebe 150 mm auseinander (Annahme des Benutzers,
2026-10-15). Die Regel steht in
:func:`~opencivil.querschnitt.geometrie.aequivalenter_durchmesser` -- die
Ueberdeckung braucht dieselbe::

    ⌀_fikt = sqrt(4/π · A_s/l · s)        s = 150 mm

Nach Vorgabe, nicht nachgeschlagen: die Grenze je Stab und der fiktive
Durchmesser. Siehe ``notizbuch/Notizen/TODO.md``.

EINHEITEN:
SI-Basis; die Zeichnung in mm.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence

from opencivil.core.berechnung import Eingaben
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, kennung_aus
from opencivil.material.basis import Baustoff
from opencivil.nachweis.mindestbewehrung import (
    protokoll_zulaessige_stahlspannung, zulaessige_stahlspannung,
)
from opencivil.nachweis.rissanforderung import Rissanforderung
from opencivil.nachweis.spannungsgrenzen import Grenzen, Grenzgruppe
from opencivil.querschnitt.analyse import Querschnittsanalyse, Stabgruppe
from opencivil.querschnitt.geometrie import (
    TEILUNG_VERSCHMIERT, Linienart, Punkt, aequivalenter_durchmesser,
)
from opencivil.querschnitt.interaktion import Querschnitt

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
    Laenge, auf Staebe im Abstand
    :data:`~opencivil.querschnitt.geometrie.TEILUNG_VERSCHMIERT` verteilt.
    """
    laenge = math.hypot(element.bis[0] - element.von[0], element.bis[1] - element.von[1])
    return aequivalenter_durchmesser(element.flaeche, laenge) * 1e-3


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


def _gruppieren(staebe: Sequence[Stabangabe], schluessel: Callable[[Stabangabe], tuple],
                bilden: Callable[[Stabangabe], Grenzgruppe]) -> Grenzen:
    """Je Schluessel eine Gruppe, in der Reihenfolge ihres ersten Stabs -- jeder Stab eine Stelle."""
    gruppen: List[Grenzgruppe] = []
    nummer: Dict[tuple, int] = {}
    je_stelle = []
    for i, stab in enumerate(staebe):
        k = schluessel(stab)
        if k not in nummer:
            nummer[k] = len(gruppen)
            gruppen.append(bilden(stab))
        gruppen[nummer[k]].stellen.append(i)
        je_stelle.append(nummer[k])
    return Grenzen(gruppen=gruppen, je_stelle=je_stelle)


def grenzen_aus_rissbreite(analyse: Querschnittsanalyse, e: Eingaben,
                           staebe: Sequence[Stabangabe],
                           anforderung: Rissanforderung) -> Grenzen:
    """
    ``sigma_s,adm`` je Stab aus der Rissanforderung: bei normaler Anforderung
    ``f_yk`` seines Stahls, bei erhoehter und hoher dazu die Rissbreite mit
    seinem Durchmesser und dem ``f_ctm`` seines Betons.
    """
    mit_rissbreite = anforderung.rissbreite is not None

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
                                 anforderung: Rissanforderung, basis: str, *,
                                 referenz: str) -> None:
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
        beton = (s or staebe[gruppe.stellen[0]]).beton
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


def _protokoll_fiktiv(p: Protokoll, s: Stabangabe, basis: str) -> Wert:
    """Der fiktive Durchmesser einer verschmierten Linie, hergeleitet."""
    g = s.element
    w = Zwischenwerte(f"{basis}.{kennung_aus(g.kennung)}")
    laenge = math.hypot(g.bis[0] - g.von[0], g.bis[1] - g.von[1]) * 1e-3
    durchmesser = w.laenge("dm", r"\varnothing_{fikt}", s.durchmesser)
    p.formel(durchmesser, r"\sqrt{\frac{4}{\pi} \cdot \frac{@A_s}{@l} \cdot @s}",
             {"A_s": w.flaeche("A_s", "A_s", g.flaeche * 1e-6, "Stahlfläche der Linie"),
              "l": w.laenge("l", "l", laenge, "Länge der Linie", stellen=0),
              "s": w.laenge("s", "s", TEILUNG_VERSCHMIERT * 1e-3, "Angenommene Teilung",
                            stellen=0)},
             titel=f"{g.name}: verschmiert, als Stäbe mit 150 mm Teilung",
             name="Fiktiver Durchmesser einer verschmierten Linie")
    return durchmesser


def _tabelle_grenzen(p: Protokoll, staebe: Sequence[Stabangabe], grenzen: Grenzen) -> None:
    """Welche Elemente zu welcher Grenze gehoeren."""
    zeilen = []
    for gruppe in grenzen.gruppen:
        elemente = ", ".join(dict.fromkeys(staebe[i].element.name for i in gruppe.stellen))
        zeilen.append([Mathe(gruppe.wert.symbol), elemente,
                       Mathe(fest(gruppe.sigma / 1e6, 0))])
    p.tabelle(kopf=["Grenze", "Elemente", Mathe(r"\sigma_{s,adm}\ [\mathrm{N/mm^2}]")],
              zeilen=zeilen, titel="Welche Stäbe welche Grenze haben", ausrichtung="llr")
