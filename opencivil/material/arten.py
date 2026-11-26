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
    """Womit die Kennung beginnt: b1, s1, st1, sp1."""

    eigene: str
    """
    Womit der Name eines eigenen Materials beginnt: BE1, S1, ST1 (Benutzer,
    2026-10-16), SP1 beim Spannstahl.
    """

    grundlage: str
    """Worauf die Kennwerte einer Normsorte stehen -- so steht es in der Oberflaeche."""

    erzeugnisse: Mapping[str, Tuple[Erzeugnis, ...]] = field(default_factory=dict)
    """
    Je Sorte, in welchen Erzeugnissen es sie gibt -- beim Spannstahl Draehte,
    Litzen und Staebe nach Tabelle 7; die anderen Arten haben keine Liste.
    """

    erzeugnisquelle: str = ""
    """Wo die Erzeugnisse stehen."""

    @property
    def titel(self) -> str:
        return self.art.beschriftung


MATERIALARTEN: Dict[str, Materialart] = {a.art.value: a for a in (
    Materialart(Baustoffart.BETON, BETONSORTEN, BETON_VORLAGEN, beton,
                tuple(betonsorten_zum_anlegen()), kennung="b", eigene="BE",
                grundlage="Kennwerte nach SIA 262:2025, die Dichten und k_E nach Vorgabe"),
    Materialart(Baustoffart.BETONSTAHL, STAHLSORTEN, STAHL_VORLAGEN, betonstahl,
                tuple(stahlsorten_zum_anlegen()), kennung="s", eigene="S",
                grundlage="Kennwerte nach SIA 262:2025, die Dichte nach Vorgabe"),
    Materialart(Baustoffart.BAUSTAHL, BAUSTAHLSORTEN, BAUSTAHL_VORLAGEN, baustahl,
                tuple(baustahlsorten_zum_anlegen()), kennung="st", eigene="ST",
                grundlage="Kennwerte nach SIA 263:2013"),
    Materialart(Baustoffart.SPANNSTAHL, SPANNSTAHLSORTEN, SPANNSTAHL_VORLAGEN, spannstahl,
                tuple(spannstahlsorten_zum_anlegen()), kennung="sp", eigene="SP",
                grundlage="Kennwerte nach SIA 262:2025",
                erzeugnisse={s: v.erzeugnisse for s, v in SPANNSTAHLSORTEN.items()},
                erzeugnisquelle=TABELLE_7),
)}

