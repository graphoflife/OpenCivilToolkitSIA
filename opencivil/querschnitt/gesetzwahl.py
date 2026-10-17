"""
opencivil/querschnitt/gesetzwahl.py -- womit ein Querschnitt rechnet.

VERANTWORTUNG:
Die Wahl der Werkstoffgesetze: der Wertesatz (:class:`Werkstoffsatz`) und die
Rechenart (:class:`Rechenart`), mit der Kriechzahl zusammen eine
:class:`Rechenwahl` -- und die eine Stelle, die daraus den Beton baut
(:func:`betongesetz`), mit dem wirksamen Modul (:func:`wirksamer_modul`).
Das gehoert dem Querschnitt: die Platte, der gezeichnete Querschnitt und die
Spannung-Dehnung-Analyse fragen hier, ohne dafuer einen Nachweis zu laden.
Was ein Nachweis-Kapitel davon anbietet, steht bei den Nachweisen
(:mod:`opencivil.nachweis.rechenwahl`). Bis 2026-10-17 stand alles dort und
im Loeser, und der gezeichnete Querschnitt importierte darum aus den
Nachweisen.

DIE RECHENARTEN:
* **Handrechnung** -- im Loeser derselbe Querschnitt wie in der
  Resistenzlinie aus Handrechnung: der Spannungsblock, die Bewehrung nur auf
  Zug, je Seite zu einer Lage im Schwerpunkt zusammengefasst, und der Beton
  auch dort gezaehlt, wo der Stahl liegt. Die gedrueckte Bewehrung zaehlt
  nicht -- in keiner anderen Rechenart fehlt sie.
* **0.85·x-Vereinfachung** -- derselbe Spannungsblock, ueber die Hoehe
  integriert, jede Faser mit ihrer mittleren Spannung. Die gedrueckte
  Bewehrung wirkt mit und verdraengt den Beton an ihrer Stelle.
* **Praezise ohne Vereinfachung** -- die Parabel-Rechteck-Beziehung, ihr
  Anstieg mit dem wirksamen Modul ``E_cm/(1+phi)``, ``k_sigma`` nie unter 1.
* **elastisch** -- nur fuer die Stahlspannungen: der Beton linear mit
  ``E_cm/(1+phi)``, hoechstens ``f_c``. So rechneten sie bis 2026-10-09 fest.

Die Namen hat der Benutzer am 2026-10-12 gewaehlt; vorher hiessen sie
«Handrechnung Block 0.85·x», «Block 0.85·x genau» und «Parabel».

Die Kriechzahl wirkt nur bei praezise und elastisch: an den anderen Gesetzen
haengt kein Modul. Der Wertesatz bestimmt, wo die Plateaus liegen
(:class:`Werkstoffsatz`), und wie ein Widerstand heisst -- ``R_d`` oder
``R_k``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from opencivil.core.wahl import Wahl
from opencivil.querschnitt.werkstoffgesetz import (
    BLOCKANTEIL, BetonElastisch, Betongesetz, Gesetz, Spannungsblock,
)


class Werkstoffsatz(Wahl):
    """
    Mit welchen Festigkeiten die Werkstoffgesetze rechnen.

    **Bemessung** -- ``f_cd`` und ``f_yd``. Fuer die Tragsicherheit: gefragt
    ist, was der Querschnitt *darf*, und dahinein gehoert der
    Teilsicherheitsbeiwert.

    **Charakteristisch** -- ``f_ck`` und ``f_yk``. Fuer die
    Gebrauchstauglichkeit: gefragt ist, was der Querschnitt *tut*, und Stahl
    fliesst bei ``f_yk``, nicht bei ``f_yd``. Mit dem Plateau bei ``f_yd``
    laege jede Stahlspannung unter 435 N/mm², und eine Grenze darueber --
    ``f_yk`` bei normaler Rissanforderung -- waere nie zu ueberschreiten: ein
    Nachweis, der per Konstruktion immer aufgeht.

    Der Satz bestimmt, **wo die Plateaus liegen**, und sonst nichts. Die
    Moduln und Dehnungsgrenzen sind in beiden Saetzen dieselben. Er steht hier
    als Name und nicht als zwei Zahlen an jeder Aufrufstelle: welche Werte ein
    Nachweis ansetzt, ist eine Entscheidung, und eine Entscheidung soll man
    lesen koennen, statt sie aus ``f_sd=...`` erschliessen zu muessen. Jeder
    Nutzer des Loesers nennt darum seinen Satz -- der Knicknachweis
    ``BEMESSUNG``, die Spannungsbegrenzung ``CHARAKTERISTISCH``; die
    Spannung-Dehnung-Analyse waehlt ihn je Analyse.
    """

    BEMESSUNG = "bemessung"
    CHARAKTERISTISCH = "charakteristisch"

    @property
    def beschriftung(self) -> str:
        return "Bemessungswerte" if self is Werkstoffsatz.BEMESSUNG else "charakteristisch"

    @property
    def kurz(self) -> str:
        """Fuer schmale Zeilen."""
        return "Bemessung" if self is Werkstoffsatz.BEMESSUNG else "charakteristisch"

    @property
    def kuerzel(self) -> str:
        """Der Buchstabe am Index: ``d`` (design) oder ``k`` (charakteristisch)."""
        return "d" if self is Werkstoffsatz.BEMESSUNG else "k"

    @property
    def widerstandsindex(self) -> str:
        """Der Index an einem Widerstand: ``M_{Rd}`` oder ``M_{Rk}``."""
        return "Rd" if self is Werkstoffsatz.BEMESSUNG else "Rk"

    @property
    def stahl_druck(self) -> str:
        """Kurzname der Stahlfestigkeit auf Druck -- dort beginnt das Plateau."""
        return "f_yd_druck" if self is Werkstoffsatz.BEMESSUNG else "f_yk_druck"

    @property
    def stahl(self) -> str:
        """Kurzname der Stahlfestigkeit -- dort beginnt das Fliessplateau."""
        return "f_yd" if self is Werkstoffsatz.BEMESSUNG else "f_yk"

    @property
    def beton(self) -> str:
        """Kurzname der Betonfestigkeit -- dort endet der Anstieg im Druck."""
        return "f_cd" if self is Werkstoffsatz.BEMESSUNG else "f_ck"

    @property
    def stahl_zeichen(self) -> str:
        """Das Formelzeichen dazu, fuer die Herleitung -- ``f_{yd}``."""
        return "f_{yd}" if self is Werkstoffsatz.BEMESSUNG else "f_{yk}"

    @property
    def stahl_druck_zeichen(self) -> str:
        """Das Zeichen des Plateaus auf Druck -- ``f_{yd}^{-}``."""
        return f"{self.stahl_zeichen}^{{-}}"

    @property
    def beton_zeichen(self) -> str:
        """Das Formelzeichen dazu, fuer die Herleitung -- ``f_{cd}``."""
        return "f_{cd}" if self is Werkstoffsatz.BEMESSUNG else "f_{ck}"

    @property
    def betonkennwerte(self) -> Dict[str, str]:
        """
        Je Rolle eines Betongesetzes
        (:data:`~opencivil.querschnitt.werkstoffgesetz.Werte`) der Kurzname
        seines Kennwerts in diesem Satz -- ``E_c`` als ``E_cm``, ohne Kriechen.
        """
        return {"f_c": self.beton, "E_c": "E_cm", "eps_c1d": "eps_c1d", "eps_c2d": "eps_c2d"}

    @property
    def stahlkennwerte(self) -> Dict[str, str]:
        """Dasselbe fuer ein Stahlgesetz."""
        return {"f_s": self.stahl, "f_s_druck": self.stahl_druck, "E_s": "E_s",
                "eps_ud": "eps_ud"}


class Rechenart(Wahl):
    """Wie der Querschnitt gerechnet wird -- siehe Dateikopf."""

    HANDRECHNUNG = "handrechnung"
    BLOCK = "block"
    PARABEL = "parabel"
    ELASTISCH = "elastisch"

    @property
    def beschriftung(self) -> str:
        return {
            Rechenart.HANDRECHNUNG: "Handrechnung",
            Rechenart.BLOCK: f"{BLOCKANTEIL}·x-Vereinfachung",
            Rechenart.PARABEL: "Präzise ohne Vereinfachung",
            Rechenart.ELASTISCH: "elastisch",
        }[self]

    @property
    def kurz(self) -> str:
        """Fuer schmale Zeilen -- etwa die Auswahl auf der Karte einer Analyse."""
        return {
            Rechenart.HANDRECHNUNG: "Hand",
            Rechenart.BLOCK: f"{BLOCKANTEIL}·x",
            Rechenart.PARABEL: "präzise",
            Rechenart.ELASTISCH: "elastisch",
        }[self]

    @property
    def latex(self) -> str:
        """Der Name als Formeltext -- fuer die Zeile «Rechenwahl» der Herleitung."""
        return {
            Rechenart.HANDRECHNUNG: r"\text{Handrechnung}",
            Rechenart.BLOCK: rf"{BLOCKANTEIL} \cdot x\text{{-Vereinfachung}}",
            Rechenart.PARABEL: r"\text{Präzise ohne Vereinfachung}",
            Rechenart.ELASTISCH: r"\text{elastisch}",
        }[self]

    @property
    def mit_kriechzahl(self) -> bool:
        """Ob ``phi`` etwas aendert -- nur, wo ein Gesetz am Modul haengt."""
        return self in (Rechenart.PARABEL, Rechenart.ELASTISCH)

    @property
    def mit_block(self) -> bool:
        """Ob der Beton als Spannungsblock rechnet."""
        return self in (Rechenart.HANDRECHNUNG, Rechenart.BLOCK)

    @property
    def ohne_ebene(self) -> str:
        """
        Was statt der Probe dasteht, wenn die Suche ihre Ebene verfehlt
        (:attr:`~opencivil.nachweis.querschnittsloeser.Ebene.verfehlt`) --
        mit dem Spannungsblock bei viel Druck und wenig Moment. Mit der
        Parabel gibt es die Ebene dort.
        """
        if self.mit_block:
            return (f"Mit der {self.beschriftung} gibt es zu dieser Einwirkung keine "
                    f"Dehnungsebene – präzise rechnen.")
        return "Die gefundene Dehnungsebene erzeugt diese Einwirkung nicht."


@dataclass(frozen=True)
class Rechenwahl:
    """Was ein Kapitel waehlt: Kriechzahl, Wertesatz, Rechenart."""

    kriechzahl: float = 0.0
    satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG
    art: Rechenart = Rechenart.HANDRECHNUNG

    @property
    def index(self) -> str:
        """``Rd`` oder ``Rk`` -- wie ein Widerstand dieser Wahl heisst."""
        return self.satz.widerstandsindex

    @property
    def beschriftung(self) -> str:
        """Fuer Legenden: «Präzise ohne Vereinfachung, φ = 2, Bemessung» -- phi nur, wo es wirkt."""
        teile = [self.art.beschriftung]
        if self.art.mit_kriechzahl:
            teile.append(f"φ = {self.kriechzahl:g}")
        return ", ".join(teile + [self.satz.kurz])


def wirksamer_modul(E_cm: float, phi: float) -> float:
    """``E_c,eff = E_cm / (1 + phi)`` -- das Kriechen weicht den Beton auf."""
    return E_cm / (1.0 + phi)


def betongesetz(wahl: Rechenwahl, *, f_c: float, E_cm: float, eps_c1d: float,
                 eps_c2d: float) -> Gesetz:
    """
    Der Beton im gerissenen Zustand -- je Rechenart. Die eine Stelle fuer
    die Parabel und den Block: der Loeser und die genaue Resistenzlinie
    bekommen ihren Beton beide hier.
    """
    if wahl.art is Rechenart.ELASTISCH:
        return BetonElastisch(E_c=wirksamer_modul(E_cm, wahl.kriechzahl), f_c=f_c)
    if wahl.art is Rechenart.PARABEL:
        return Betongesetz.mit_modul(f_c=f_c, E_c=wirksamer_modul(E_cm, wahl.kriechzahl),
                                     eps_c1d=eps_c1d, eps_c2d=eps_c2d)
    return Spannungsblock(f_cd=f_c, eps_c2d=eps_c2d)
