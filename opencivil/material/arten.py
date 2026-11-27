"""
opencivil/material/arten.py -- die Materialarten des Projekts, je eine Zeile.

VERANTWORTUNG:
Was Projekt, Aufbau und Oberflaeche ueber eine Materialart wissen muessen:
ihre Sorten und Kennwerte, wie ein Material entsteht, womit seine Kennung
und der Name eines eigenen beginnen, und worauf die Kennwerte stehen. Die
Oberflaeche liest dasselbe aus dem Katalog (``materialarten``).

Bis 2026-11-15 stand das an sieben Stellen je von Hand, als Zuordnung von
«beton» und «betonstahl» -- der Baustahl haette an jeder dazukommen muessen,
und eine vergessene fiele erst beim Anlegen auf.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping, Tuple

from opencivil.material.basis import Baustoff, Baustoffart, KennwertVorlage
from opencivil.material.baustahl import (
    BAUSTAHL_VORLAGEN, BAUSTAHLSORTEN, baustahl, baustahlsorten_zum_anlegen,
)
from opencivil.material.beton import BETON_VORLAGEN, BETONSORTEN, beton, betonsorten_zum_anlegen
from opencivil.material.betonstahl import (
    STAHL_VORLAGEN, STAHLSORTEN, betonstahl, stahlsorten_zum_anlegen,
)
from opencivil.material.holz import HOLZ_VORLAGEN, HOLZSORTEN, holz, holzsorten_zum_anlegen
from opencivil.material.profilblech import (
    PROFILBLECH_VORLAGEN, PROFILBLECHSORTEN, profilblech, profilblechsorten_zum_anlegen,
)
from opencivil.material.spannstahl import (
    SPANNSTAHL_VORLAGEN, SPANNSTAHLSORTEN, TABELLE_7, Erzeugnis, spannstahl,
    spannstahlsorten_zum_anlegen,
)


@dataclass(frozen=True)
class Materialart:
    art: Baustoffart
    sorten: Mapping[str, Any]
    vorlagen: Tuple[KennwertVorlage, ...]
    bauen: Callable[..., Baustoff]
    """Wie :func:`~opencivil.material.beton.beton`: Sorte, dann Name, Praefix, Abweichungen."""

    anlegen: Tuple[str, ...]
    """Die Sorten in der Folge, in der das Fenster «Neues Material» sie anbietet."""

    kennung: str
    """Womit die Kennung beginnt: b1, s1, st1, sp1, h1, pb1."""

    eigene: str
    """
    Womit der Name eines eigenen Materials beginnt: BE1, S1, ST1 (Benutzer,
    2026-10-16), SP1 beim Spannstahl, H1 beim Holz, PB1 beim Profilblechstahl.
    """

    grundlage: str
    """Worauf die Kennwerte einer Normsorte stehen -- so steht es in der Oberflaeche."""

    grundlagen: Mapping[str, str] = field(default_factory=dict)
    """
    Je Sorte, deren Kennwerte anderswo stehen, worauf -- beim Betonstahl der
    «Stahl II» aus SIA 269/2:2011 (:data:`~opencivil.material.betonstahl.STAHL_II`).
    """

    erzeugnisse: Mapping[str, Tuple[Erzeugnis, ...]] = field(default_factory=dict)
    """
    Je Sorte, in welchen Erzeugnissen es sie gibt -- beim Spannstahl Draehte,
    Litzen und Staebe nach Tabelle 7; die anderen Arten haben keine Liste.
    """

    erzeugnisquelle: str = ""
    """Wo die Erzeugnisse stehen."""

    saechlich: bool = False
    """
    Ob die Art «das» heisst: «Neues Holz», «ein Holz» -- die anderen sind
    maennlich. Bis 2026-11-26 stand «Neuer» und «einen» fest im Text.
    """

    @property
    def titel(self) -> str:
        return self.art.beschriftung

    def grundlage_von(self, sorte: str) -> str:
        """Worauf die Kennwerte der Normsorte ``sorte`` stehen -- ihre eigene oder die der Art."""
        return self.grundlagen.get(sorte, self.grundlage)

    @property
    def neu(self) -> str:
        """«Neuer Beton», «Neues Holz»."""
        return f"{'Neues' if self.saechlich else 'Neuer'} {self.titel}"

    @property
    def eigen(self) -> str:
        """«Eigener Beton», «Eigenes Holz»."""
        return f"{'Eigenes' if self.saechlich else 'Eigener'} {self.titel}"

    @property
    def einen(self) -> str:
        """Im Akkusativ: «einen Beton», «ein Holz»."""
        return f"{'ein' if self.saechlich else 'einen'} {self.titel}"

    @property
    def keinen(self) -> str:
        """Im Akkusativ: «keinen Beton», «kein Holz»."""
        return f"k{self.einen}"


MATERIALARTEN: Dict[str, Materialart] = {a.art.value: a for a in (
    Materialart(Baustoffart.BETON, BETONSORTEN, BETON_VORLAGEN, beton,
                tuple(betonsorten_zum_anlegen()), kennung="b", eigene="BE",
                grundlage="Kennwerte nach SIA 262:2025, die Dichten und k_E nach Vorgabe"),
    Materialart(Baustoffart.BETONSTAHL, STAHLSORTEN, STAHL_VORLAGEN, betonstahl,
                tuple(stahlsorten_zum_anlegen()), kennung="s", eigene="S",
                grundlage="Kennwerte nach SIA 262:2025, die Dichte nach Vorgabe",
                grundlagen={s: v.grundlage for s, v in STAHLSORTEN.items() if v.grundlage}),
    Materialart(Baustoffart.BAUSTAHL, BAUSTAHLSORTEN, BAUSTAHL_VORLAGEN, baustahl,
                tuple(baustahlsorten_zum_anlegen()), kennung="st", eigene="ST",
                grundlage="Kennwerte nach SIA 263:2013"),
    Materialart(Baustoffart.SPANNSTAHL, SPANNSTAHLSORTEN, SPANNSTAHL_VORLAGEN, spannstahl,
                tuple(spannstahlsorten_zum_anlegen()), kennung="sp", eigene="SP",
                grundlage="Kennwerte nach SIA 262:2025",
                erzeugnisse={s: v.erzeugnisse for s, v in SPANNSTAHLSORTEN.items()},
                erzeugnisquelle=TABELLE_7),
    Materialart(Baustoffart.HOLZ, HOLZSORTEN, HOLZ_VORLAGEN, holz,
                tuple(holzsorten_zum_anlegen()), kennung="h", eigene="H",
                grundlage=("Bemessungswerte nach SIA 265:2012 für Feuchteklasse 1, "
                           "die Dichte nach SIA 261:2020"),
                saechlich=True),
    Materialart(Baustoffart.PROFILBLECH, PROFILBLECHSORTEN, PROFILBLECH_VORLAGEN, profilblech,
                tuple(profilblechsorten_zum_anlegen()), kennung="pb", eigene="PB",
                grundlage="Kennwerte nach SIA 264:2014, E_a nach SIA 263:2013"),
)}

