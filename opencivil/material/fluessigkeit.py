"""
opencivil/material/fluessigkeit.py -- Fluessigkeiten: das Wasser und eigene.

VERANTWORTUNG:
Eine Fluessigkeit traegt nichts, sie wiegt nur. Ihr Kennwert ist die
Dichte ``rho_fl``; daraus folgt ihre Raumlast ``gamma_fl = rho_fl · g``,
eine gewoehnliche, einzeln ueberschreibbare Berechnung wie jeder Kennwert
(:mod:`opencivil.material.basis`). Grundbruch und Pfahl nehmen aus ihr die
Raumlast des Grundwassers (:mod:`opencivil.geotechnik.wasser`); bis
2026-11-27 stand dort je ein Feld γ_w = 10 kN/m³.

DIE SORTEN:
Nur das Wasser, mit 1000 kg/m³ -- nach Vorgabe, nicht nachgeschlagen. SIA
261:2020 rechnet den Wasserdruck mit der Raumlast des Wassers γ_w,k (4.4.2.1,
Gl. (8)), nennt dafuer aber keine Zahl; die fluessigen Stoffe in Anhang A,
Tabelle 30 sind Lagergueter, das Wasser steht nicht darunter. Eine andere
Fluessigkeit -- eine Bentonitsuspension, Salzwasser -- legt man als eigene
mit ihrer Dichte an.

g:
10 m/s² wie beim Eigengewicht (:data:`~opencivil.material.basis.ERDBESCHLEUNIGUNG`):
so wiegt das Wasser 10 kN/m³.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional

from opencivil.core.einheiten import KG_PRO_M3, KN_PRO_M3, M_PRO_S2, Groesse
from opencivil.material.basis import (
    ERDBESCHLEUNIGUNG, Baustoff, Baustoffart, KennwertVorlage, erzeuge,
)


@dataclass(frozen=True)
class Fluessigkeitssorte:
    """Eine Fluessigkeit: ihre Dichte in kg/m³."""

    rho_fl: float


#: Die Fluessigkeiten, die das Werkzeug kennt -- siehe Dateikopf.
FLUESSIGKEITSSORTEN: Dict[str, Fluessigkeitssorte] = {
    "Wasser": Fluessigkeitssorte(1000.0),
}

#: Womit eine neue Fluessigkeit anfaengt.
ERSTE_FLUESSIGKEIT = "Wasser"


def fluessigkeitssorten_zum_anlegen() -> List[str]:
    """Die Sorten in der Folge, in der neue angelegt werden: die erste, dann die uebrigen."""
    return [ERSTE_FLUESSIGKEIT] + [s for s in FLUESSIGKEITSSORTEN if s != ERSTE_FLUESSIGKEIT]


FLUESSIGKEIT_VORLAGEN: tuple[KennwertVorlage, ...] = (
    KennwertVorlage(kurzname="rho_fl", symbol=r"\rho_{fl}", einheit=KG_PRO_M3,
                    beschreibung="Dichte der Flüssigkeit", stellen=0),
    KennwertVorlage(kurzname="g", symbol="g", einheit=M_PRO_S2,
                    beschreibung="Erdbeschleunigung", stellen=0,
                    festwert=ERDBESCHLEUNIGUNG),
    KennwertVorlage(
        kurzname="gamma_fl",
        symbol=r"\gamma_{fl}",
        einheit=KN_PRO_M3,
        beschreibung="Raumlast der Flüssigkeit",
        stellen=1,
        eingaben=("rho_fl", "g"),
        vorlage_latex=r"@rho_fl \cdot @g",
        funktion=lambda rho_fl, g: rho_fl * g,
    ),
)


def fluessigkeit(
    sorte: str = ERSTE_FLUESSIGKEIT,
    *,
    name: Optional[str] = None,
    praefix: Optional[str] = None,
    abweichungen: Optional[Mapping[str, Groesse]] = None,
    symbol_index: str = "",
) -> Baustoff:
    """
    Erzeugt eine Fluessigkeit.

    :param sorte: Bezeichnung aus :data:`FLUESSIGKEITSSORTEN`, z.B. ``'Wasser'``.
    :param abweichungen: Zahlenwerte, die von der Sorte abweichen -- bei einer
                         eigenen Fluessigkeit ihre Dichte.
    """
    if sorte not in FLUESSIGKEITSSORTEN:
        raise ValueError(f"Unbekannte Flüssigkeit '{sorte}'. Verfügbar: "
                         f"{', '.join(FLUESSIGKEITSSORTEN)}.")
    werte: Dict[str, Groesse] = {"rho_fl": Groesse(FLUESSIGKEITSSORTEN[sorte].rho_fl, KG_PRO_M3)}
    werte.update(abweichungen or {})
    return erzeuge(
        art=Baustoffart.FLUESSIGKEIT,
        name=name or sorte,
        sorte=sorte,
        vorlagen=FLUESSIGKEIT_VORLAGEN,
        werte=werte,
        praefix=praefix,
        symbol_index=symbol_index,
    )
