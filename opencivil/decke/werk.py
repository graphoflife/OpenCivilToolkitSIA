"""
opencivil/decke/werk.py -- die Decke im Rechenwerk.

VERANTWORTUNG:
Was eine Decke im Rechenwerk anmeldet: eine Prozedur, die sie nach der
Streifenmethode rechnet (:func:`~opencivil.decke.rechnung.rechnen`) und ihre
Herleitung schreibt (:mod:`~opencivil.decke.herleitung`), samt dem, was sie
von aussen liest.

E UND GEWICHT:
nimmt jede Platte von ihrem Beton, wie ein Stab des Balkensystems
(:data:`~opencivil.stabwerk.rechnung.BETONKENNWERTE`): ``E_cm`` -- nach
Vorgabe, nicht nachgeschlagen -- und die Dichte des Stahlbetons, mit
``g = 10 m/s²`` (:data:`~opencivil.stabwerk.rechnung.ERDBESCHLEUNIGUNG`,
Benutzer, 2026-10-23) ihr Gewicht je m³. Die Regel steht dort; hier wird
sie nur gelesen.

DAS ERGEBNIS:
kommt als Befund in die Loesung (:class:`Deckenbefund`); Bilder und
Zusammenfassung lesen es dort. Eine Decke, die nicht rechnet, ist ein
Befund mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, List, Mapping, Optional, Sequence

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben, Prozedur, Vorgabe
from opencivil.core.einheiten import M_PRO_S2
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.wert import WertDef
from opencivil.decke import herleitung
from opencivil.decke.modell import Decke
from opencivil.decke.rechnung import Ergebnis, rechnen
from opencivil.material.basis import Baustoff
from opencivil.stabwerk.rechnung import BETONKENNWERTE, ERDBESCHLEUNIGUNG
from opencivil.stabwerk.system import Meldung

#: Das Thema der Formelsammlung.
STREIFENMETHODE = "Streifenmethode"


@dataclass
class Deckenbefund:
    """
    Was die Streifenmethode im Lauf fand: die Decke, wie sie gerechnet wurde
    -- mit E und Gewicht jeder Platte --, die Meldungen und das Ergebnis.
    """

    gerechnet: Decke
    meldungen: List[Meldung]
    """Die der Beschreibung und die der Rechnung, in dieser Reihenfolge."""

    ergebnis: Optional[Ergebnis] = None
    """``None``, wenn eine Meldung der Beschreibung die Rechnung aufhielt."""


class StreifenmethodeProzedur(Prozedur):
    """Die ganze Decke, gerechnet und aufgeschrieben."""

    THEMA = STREIFENMETHODE

    def __init__(self, system: "Deckensystem", **kwargs) -> None:
        super().__init__(**kwargs)
        self.system = system

    def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        return self.system.rechnen_und_schreiben(e, p)


class Deckensystem(Rechenobjekt):
    """Eine Decke, fertig fuer das Rechenwerk."""

    WAS = "Decke"

    def __init__(self, *, name: str, kennung: str, praefix: str, decke: Decke,
                 betone: Mapping[str, Baustoff], meldungen: Sequence[Meldung]) -> None:
        """
        ``decke`` mit E und Gewicht null; ``betone`` je Platte (nach ihrem
        Namen) ihr Beton. Einer Platte ohne Beton fehlt er hier -- warum,
        steht in ``meldungen``.
        """
        self.name = name
        self.kennung = kennung
        self.id = praefix
        self.decke = decke
        self.betone = dict(betone)
        self.meldungen = list(meldungen)
        self.definitionen: Dict[str, WertDef] = {}
        self.berechnungen = []
        self._aufbauen()

    def abschnitt(self) -> Abschnitt:
        return Abschnitt(f"Decke: {self.name}", self.id, thema=STREIFENMETHODE)

    @property
    def baustoffe(self) -> List[Baustoff]:
        """Die Betone der Platten, jeder einmal."""
        return list({id(b): b for b in self.betone.values()}.values())

    def _aufbauen(self) -> None:
        bezuege = []
        for i, stoff in enumerate(self.baustoffe):
            bezuege += [Eingabebezug(f"E_{i}", stoff.id_von(BETONKENNWERTE["E"])),
                        Eingabebezug(f"rho_{i}", stoff.id_von(BETONKENNWERTE["rho"]))]
        if bezuege:
            g = WertDef(id=f"{self.id}.g", symbol="g", einheit=M_PRO_S2,
                        beschreibung="Erdbeschleunigung", stellen=0)
            self.definitionen["g"] = g
            self.berechnungen.append(Vorgabe(
                id=g.id, ausgabe=g, groesse=ERDBESCHLEUNIGUNG, abschnitt=self.abschnitt(),
                titel="Erdbeschleunigung für das Eigengewicht (nach Vorgabe des Benutzers)"))
            bezuege.append(Eingabebezug("g", g.id))
        self.rechnung = StreifenmethodeProzedur(
            self, id=f"{self.id}.rechnung", ausgaben=[], bezuege=bezuege,
            titel="Streifenmethode", abschnitt=self.abschnitt())
        """Die Prozedur, die die Decke rechnet -- ihr Befund ist der :class:`Deckenbefund`."""
        self.berechnungen.append(self.rechnung)

    def ziele(self) -> List[str]:
        """Was ein Lauf rechnen muss: die Decke."""
        return [self.rechnung.id]

    # -- Rechnen ----------------------------------------------------------------

    def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        """
        E und Gewicht in die Platten, die Decke gerechnet, die Herleitung
        geschrieben. Hält eine Meldung der Beschreibung die Rechnung auf,
        bleibt es bei ihr.
        """
        stoffe = {id(b): i for i, b in enumerate(self.baustoffe)}
        platten = []
        for platte in self.decke.platten:
            stoff = self.betone.get(platte.name)
            if stoff is not None:
                i = stoffe[id(stoff)]
                platte = replace(platte, E=e.g(f"E_{i}").si, wichte=e.g(f"rho_{i}").si * e.g("g").si)
            platten.append(platte)
        gerechnet = replace(self.decke, platten=platten)
        ergebnis = None if any(m.fehler for m in self.meldungen) else rechnen(gerechnet)
        befund = Deckenbefund(gerechnet, self.meldungen + (ergebnis.meldungen if ergebnis else []),
                              ergebnis)
        herleitung.schreiben(p, self, befund)
        return Ausfuehrung({}, befund=befund)
