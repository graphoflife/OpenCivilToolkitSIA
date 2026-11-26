"""
opencivil/nachweis/qa_stahl_werte.py -- was Kennzahlen und Nachweise eines Stahlquerschnitts teilen.

VERANTWORTUNG:
Die Kennzahlen (:mod:`opencivil.nachweis.qa_stahl_kennzahlen`) und die
Nachweise je Lastfall (:mod:`opencivil.nachweis.qa_stahl`) lesen dieselben
Kennwerte und schreiben dieselben Tabellen; beides steht hier, je einmal:

* die Kennwerte je Gruppe -- Baustahl in einer Dicke -- und die Festigkeit,
  mit der gerechnet wird (:class:`Stahlwerte`);
* die Tabelle der Bleche mit ihren Klassen (:func:`klassen`);
* die Tabelle der mitwirkenden Breiten in Klasse 4 (:func:`breiten`).

BEMESSUNG ODER CHARAKTERISTISCH:
Wie beim Stahlbeton rechnet ein Baustahl mit dem Wertesatz, den die
Tragsicherheit der Analyse fuer ihn waehlt
(:class:`~opencivil.querschnitt.gesetzwahl.Werkstoffsatz`): mit ``f_y/γ_M1``
und ``τ_y/γ_M1`` oder mit ``f_y`` und ``τ_y``. Die Widerstaende heissen in
beiden Faellen ``Rd`` -- wie beim Stahlbeton (nach Vorgabe, nicht
nachgeschlagen).
"""

from __future__ import annotations

import math
from functools import cached_property
from typing import Dict, List, Sequence, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll
from opencivil.core.wert import Wert
from opencivil.querschnitt.gesetzwahl import Rechenwahl, Werkstoffsatz
from opencivil.stahlbau import klasse as kl
from opencivil.stahlbau.querschnitt import Blechzustand, Stahlquerschnitt, Teil, Wirksam
from opencivil.stahlprofile.bleche import Halterung

#: Was Kennzahlen und Nachweise je Baustahl lesen.
KENNWERTE = ("f_y", "f_y_dick", "tau_y", "tau_y_dick", "gamma_M1", "E_a")

#: Was in jeder Dicke gilt -- die anderen Kennwerte haben einen Wert ueber 40 mm.
_JEDE_DICKE = ("gamma_M1", "E_a")

#: Warum ein Rundrohr der Klasse 4 nichts traegt.
ROHR_KLASSE_4 = ("Ein Rundrohr der Klasse 4 rechnet das Werkzeug nicht – SIA 263 nennt dafür "
                 "keine mitwirkende Breite. Der Widerstand steht darum auf null.")

SPANNUNG = Mathe(r"f_y\ [\mathrm{N}/\mathrm{mm}^2]")

#: Namen der Formeln, die Kennzahlen und Nachweise beide schreiben: eine Formel, ein Name in der
#: Formelsammlung, gleich in welcher Klasse.
WIDERSTANDSMOMENT = "Widerstandsmoment bis zur weitesten Faser"
ELASTISCH = "Biegewiderstand bis zum ersten Fliessen"


def stoffbezuege(stahl: Stahlquerschnitt) -> List[Eingabebezug]:
    """Die Kennwerte aller Baustaehle des Querschnitts, als Eingaben."""
    stoffe = {g.stoff.id: g.stoff for g in stahl.gruppen}.values()
    return [stoff.bezug(k) for stoff in stoffe for k in KENNWERTE]


class Stahlwerte:
    """Die Kennwerte der Gruppen eines Stahlquerschnitts -- siehe Dateikopf."""

    def __init__(self, stahl: Stahlquerschnitt, e: Eingaben, wahl: Rechenwahl) -> None:
        self.stahl = stahl
        self.e = e
        self.bemessung = [wahl.satz(g.stoff) is Werkstoffsatz.BEMESSUNG for g in stahl.gruppen]

    def wert(self, g: int, kurz: str) -> Wert:
        """Ein Kennwert der Gruppe ``g``, in ihrer Dicke."""
        gruppe = self.stahl.gruppen[g]
        name = kurz if kurz in _JEDE_DICKE else gruppe.kennwert(kurz)
        return self.e[gruppe.stoff.eingabename(name)]

    def zahl(self, g: int, kurz: str) -> float:
        """Derselbe als Zahl, Spannungen in N/mm²."""
        return self.wert(g, kurz).groesse.si / (1.0 if kurz == "gamma_M1" else 1e6)

    def gamma(self, g: int) -> float:
        """``γ_M1`` mit Bemessungswerten, sonst eins."""
        return self.zahl(g, "gamma_M1") if self.bemessung[g] else 1.0

    @cached_property
    def f(self) -> List[float]:
        """Je Gruppe die Fliessgrenze, mit der gerechnet wird: ``f_y/γ_M1`` oder ``f_y``."""
        return [self.zahl(g, "f_y") / self.gamma(g) for g in range(len(self.stahl.gruppen))]

    @cached_property
    def eps(self) -> List[float]:
        """Je Gruppe ``ε`` -- immer mit ``f_y``."""
        return [kl.epsilon(self.zahl(g, "f_y")) for g in range(len(self.stahl.gruppen))]

    @property
    def mit_gamma(self) -> bool:
        """Ob einer der Staehle mit Bemessungswerten rechnet -- dann steht ``γ_M1`` in den Formeln."""
        return any(self.bemessung)

    def formel(self, g: int, x: str, zeichen: str = "f_y") -> Tuple[str, Dict[str, Wert]]:
        """
        ``f_y X/γ_M1`` der Gruppe ``g`` als Vorlage mit ihren Werten -- mit
        charakteristischen Werten ohne ``γ_M1``. ``x`` ist ``X`` in der
        Vorlage, etwa ``@W``.
        """
        werte = {zeichen: self.wert(g, zeichen)}
        if not self.bemessung[g]:
            return rf"@{zeichen} \cdot {x}", werte
        werte["gamma_M1"] = self.wert(g, "gamma_M1")
        return rf"\frac{{@{zeichen} \cdot {x}}}{{@gamma_M1}}", werte

    def bruch(self, oben: str) -> str:
        """``oben/γ_M1`` als LaTeX, wo mit Bemessungswerten gerechnet wird -- sonst ``oben``."""
        return rf"\frac{{{oben}}}{{\gamma_{{M1}}}}" if self.mit_gamma else oben


def klassen(p: Protokoll, zustaende: Sequence[Blechzustand], freie: Sequence[Teil],
            titel: str) -> Tuple[int, str]:
    """
    Die Klasse je Blech, als Tabelle, und die des Querschnitts -- die
    unguenstigste -- mit dem Namen dessen, was sie bestimmt (ohne Namen in
    Klasse 1). Gedrueckte freie Flaechen zaehlen mit Klasse 3.
    """
    if zustaende:
        p.tabelle(
            kopf=["Blech", "Tabelle", Mathe(r"c/t"), Mathe(r"\alpha"), Mathe(r"\psi"),
                  Mathe(r"\text{Grenzen}\ 1 / 2 / 3"), "Klasse"],
            zeilen=[_zeile(z) for z in zustaende], titel=titel, ausrichtung="llrrrrr")
    kandidaten = ([(z.klasse, z.name) for z in zustaende]
                  + [(3, f"«{f.flaeche.name}»") for f in freie])
    klasse = max((k for k, _ in kandidaten), default=1)
    wer = next((name for k, name in kandidaten if k == klasse), "") if klasse > 1 else ""
    if freie:
        p.text("Gedrückt und frei gezeichnet: "
               + ", ".join(f"«{f.flaeche.name}»" for f in freie) + " – höchstens Klasse 3.")
    return klasse, wer


def _zeile(z: Blechzustand) -> List:
    rohr = z.blech.halterung is Halterung.ROHR
    tabelle = z.blech.halterung.tabelle.replace("Tabelle ", "")
    if z.frei and z.psi is not None and z.psi < 1.0:
        tabelle += ", freier Rand gedrückt"
    return [z.name, f"{tabelle}, D/t" if rohr else tabelle,
            Mathe(rf"{fest(z.blech.c, 1)}/{fest(z.blech.t, 1)} = {fest(z.schlankheit, 1)}"),
            Mathe("–" if rohr else fest(z.alpha, 2)),
            Mathe("–" if rohr or z.psi is None else fest(z.psi, 2)),
            Mathe(" / ".join("–" if math.isinf(g) else fest(g, 1) for g in z.grenzen.werte)),
            Mathe(f"{z.klasse}")]


def breiten(p: Protokoll, wirksam: Sequence[Wirksam], titel: str) -> None:
    """Die mitwirkenden Breiten der Bleche in Klasse 4, als Tabelle mit ihren Formeln."""
    p.ansatz(r"\bar{\lambda}_p = \frac{b/t}{28.4\, \varepsilon \sqrt{k}} \qquad "
             r"\rho = \frac{0.9}{\bar{\lambda}_p} \le 1 \qquad b_{eff} = \rho\, b_c",
             titel="Mitwirkende Breite, b zwischen den theoretischen Scheibenschnittlinien",
             referenz=kl.REFERENZ_BREITE, name="Mitwirkende Breite eines Blechs")
    if any(w.zustand.blech.kasten for w in wirksam):
        p.ansatz(r"\rho = \frac{\bar{\lambda}_p - 0.055\,(3 + \psi)}{\bar{\lambda}_p^2} \le 1",
                 titel="Im Kasten, hier im Rechteckrohr", referenz=kl.REFERENZ_KASTEN)
    p.tabelle(
        kopf=["Blech", Mathe(r"b\ [\mathrm{mm}]"), Mathe(r"\psi"), Mathe("k"),
              Mathe(r"\bar{\lambda}_p"), Mathe(r"\rho"), Mathe(r"b_c\ [\mathrm{mm}]"),
              Mathe(r"b_{eff}\ [\mathrm{mm}]")],
        zeilen=[[w.zustand.name, Mathe(fest(w.zustand.blech.b, 1)), Mathe(fest(w.psi, 2)),
                 Mathe(fest(w.k, 3)), Mathe(fest(w.lambda_p, 3)), Mathe(fest(w.rho, 3)),
                 Mathe(fest(w.b_c, 1)), Mathe(fest(w.b_eff, 1))] for w in wirksam],
        titel=titel, ausrichtung="lrrrrrrr")
    p.annahme("Der wirksame Querschnitt entsteht in einem Schritt aus den Spannungen des "
              "Bruttoquerschnitts; je Blech fällt ein Streifen der gedrückten Zone weg, beim "
              "einseitig gehaltenen am freien Ende – nach Vorgabe, nicht nachgeschlagen.")
