"""
opencivil/decke/werk.py -- die Decke im Rechenwerk.

VERANTWORTUNG:
Was eine Decke im Rechenwerk anmeldet: eine Prozedur, die sie nach ihrem
Verfahren rechnet und ihre Herleitung schreibt -- nach der Streifenmethode
(:mod:`~opencivil.decke.rechnung`, :mod:`~opencivil.decke.herleitung`) oder
der FEM (:mod:`~opencivil.decke.fem`) --, samt dem, was sie von aussen
liest. Welches Verfahren, steht einmal fest, wenn die Decke angemeldet
wird (:data:`VERFAHREN`).

E UND GEWICHT:
nimmt jede Platte von ihrem Beton, wie ein Stab des Balkensystems
(:data:`~opencivil.stabwerk.rechnung.STABKENNWERTE`): ``E_cm`` am
ungerissenen Querschnitt (SIA 262:2025, 4.1.4.1.3) und die Dichte des
Stahlbetons, mit
``g = 10 m/s²`` (:data:`~opencivil.material.basis.ERDBESCHLEUNIGUNG`,
Benutzer, 2026-10-23) ihr Gewicht je m³. Die Regel steht dort; hier wird
sie nur gelesen. Die FEM nimmt dazu ``ν_c`` (SIA 262:2025, 3.1.2.3.5).

DAS ERGEBNIS:
kommt als Befund in die Loesung (:class:`Deckenbefund`); Bilder und
Zusammenfassung lesen es dort. Eine Decke, die nicht rechnet, ist ein
Befund mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Union

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben, Prozedur, Vorgabe
from opencivil.core.einheiten import M_PRO_S2
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.core.wert import WertDef
from opencivil.decke import herleitung, rechnung
from opencivil.decke.fem import herleitung as fem_herleitung
from opencivil.decke.fem import rechnung as fem_rechnung
from opencivil.decke.fem.rechnung import Femergebnis
from opencivil.decke.modell import Decke, Verfahren
from opencivil.decke.rechnung import Ergebnis
from opencivil.material.basis import ERDBESCHLEUNIGUNG, Baustoff
from opencivil.stabwerk.rechnung import STABKENNWERTE
from opencivil.stabwerk.system import Meldung

@dataclass(frozen=True)
class Art:
    """
    Ein Verfahren, eine Decke zu rechnen: Thema der Formelsammlung, Titel,
    Rechnung und Herleitung -- und ob es die Querdehnungszahl des Betons braucht.
    """

    thema: str
    titel: str
    rechnen: Callable[[Decke], Any]
    schreiben: Callable[..., None]
    querdehnung: bool = False


#: Je Verfahren, wie es rechnet und schreibt.
VERFAHREN = {
    Verfahren.STREIFEN: Art("Streifenmethode", "Streifenmethode", rechnung.rechnen, herleitung.schreiben),
    Verfahren.FEM: Art("FEM der Decke", "FEM", fem_rechnung.rechnen, fem_herleitung.schreiben, True),
}


@dataclass
class Deckenbefund:
    """
    Was die Rechnung im Lauf fand: die Decke, wie sie gerechnet wurde --
    mit E, ν und Gewicht jeder Platte und in der Streifenmethode den
    Richtungen, die sie selbst wählt --, die Meldungen und das Ergebnis.
    """

    gerechnet: Decke
    meldungen: List[Meldung]
    """Die der Beschreibung und die der Rechnung, in dieser Reihenfolge."""

    ergebnis: Optional[Union[Ergebnis, Femergebnis]] = None
    """``None``, wenn eine Meldung der Beschreibung die Rechnung aufhielt."""


class DeckenProzedur(Prozedur):
    """Die ganze Decke, gerechnet und aufgeschrieben -- ihr Thema ist das ihres Verfahrens."""

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
        self.art = VERFAHREN[decke.verfahren]
        self.definitionen: Dict[str, WertDef] = {}
        self.berechnungen = []
        self._aufbauen()

    def abschnitt(self) -> Abschnitt:
        return Abschnitt(f"Decke: {self.name}", self.id, thema=self.art.thema)

    @property
    def baustoffe(self) -> List[Baustoff]:
        """Die Betone der Platten, jeder einmal."""
        return list({id(b): b for b in self.betone.values()}.values())

    def _aufbauen(self) -> None:
        bezuege = []
        for i, stoff in enumerate(self.baustoffe):
            kennwerte = STABKENNWERTE[stoff.art]
            bezuege += [Eingabebezug(f"E_{i}", stoff.id_von(kennwerte["E"])),
                        Eingabebezug(f"rho_{i}", stoff.id_von(kennwerte["rho"]))]
            if self.art.querdehnung:
                bezuege.append(Eingabebezug(f"nu_{i}", stoff.id_von("nu_c")))
        if bezuege:
            g = WertDef(id=f"{self.id}.g", symbol="g", einheit=M_PRO_S2,
                        beschreibung="Erdbeschleunigung", stellen=0)
            self.definitionen["g"] = g
            self.berechnungen.append(Vorgabe(
                id=g.id, ausgabe=g, groesse=ERDBESCHLEUNIGUNG, abschnitt=self.abschnitt(),
                titel="Erdbeschleunigung für das Eigengewicht (nach Vorgabe des Benutzers)"))
            bezuege.append(Eingabebezug("g", g.id))
        self.rechnung = DeckenProzedur(
            self, id=f"{self.id}.rechnung", ausgaben=[], bezuege=bezuege,
            titel=self.art.titel, abschnitt=self.abschnitt())
        """Die Prozedur, die die Decke rechnet -- ihr Befund ist der :class:`Deckenbefund`."""
        self.berechnungen.append(self.rechnung)

    def ziele(self) -> List[str]:
        """Was ein Lauf rechnen muss: die Decke."""
        return [self.rechnung.id]

    # -- Rechnen ----------------------------------------------------------------

    def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        """
        E, ν und Gewicht in die Platten, die Decke gerechnet, die Herleitung
        geschrieben. Hält eine Meldung der Beschreibung die Rechnung auf,
        bleibt es bei ihr.
        """
        stoffe = {id(b): i for i, b in enumerate(self.baustoffe)}
        platten = []
        for platte in self.decke.platten:
            stoff = self.betone.get(platte.name)
            if stoff is not None:
                i = stoffe[id(stoff)]
                platte = replace(platte, E=e.g(f"E_{i}").si, wichte=e.g(f"rho_{i}").si * e.g("g").si,
                                 nu=e.g(f"nu_{i}").si if self.art.querdehnung else 0.0)
            platten.append(platte)
        gerechnet = replace(self.decke, platten=platten)
        ergebnis = None if any(m.haelt_an for m in self.meldungen) else self.art.rechnen(gerechnet)
        befund = Deckenbefund(ergebnis.decke if ergebnis else gerechnet,
                              self.meldungen + (ergebnis.meldungen if ergebnis else []), ergebnis)
        self.art.schreiben(p, self, befund)
        return Ausfuehrung({}, befund=befund)
