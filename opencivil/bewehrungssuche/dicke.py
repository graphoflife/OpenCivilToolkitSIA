"""
opencivil/bewehrungssuche/dicke.py -- die duennste Platte suchen.

VERANTWORTUNG:
Zwei Modi suchen zusaetzlich die Dicke. Je Dicke laeuft dieselbe
Bewehrungssuche (:func:`~opencivil.bewehrungssuche.laengs.suche`); gesucht
wird die duennste Platte, bei der sie eine Loesung findet.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from opencivil.bewehrungssuche.laengs import Suchergebnis, Suchmodus, suche

# ===========================================================================
# Plattendicke
# ===========================================================================

#: Das Raster der Plattendicke in mm. Gefunden wird die kleinste Dicke auf
#: diesem Raster, bei der alles aufgeht -- also auf den Zentimeter aufgerundet.
DICKENRASTER = 10.0

#: Bis wohin beim Verdoppeln gesucht wird, in mm. Dicker ist nicht immer
#: leichter: die Mindestbewehrung waechst mit der Dicke, und mit einer
#: Obergrenze kann eine sehr dicke Platte wieder durchfallen.
DICKE_HOECHSTENS = 2000.0


@dataclass
class Dickenversuch:
    """Eine gepruefte Dicke -- fuer die Meldung, welche es waren."""

    h: float
    """Plattendicke in mm."""

    geht: bool


@dataclass
class Dickenergebnis:
    """Die duennste Platte -- und die Bewehrungssuche bei ihr."""

    modus: Suchmodus
    h: Optional[float] = None
    """Gefundene Dicke in mm -- ``None``: keine gefunden."""

    suche: Optional[Suchergebnis] = None
    """Die Bewehrungssuche bei der gefundenen Dicke, sonst bei der letzten."""

    versuche: List[Dickenversuch] = field(default_factory=list)
    begruendung: str = ""

    @property
    def gefunden(self) -> bool:
        return self.h is not None


def _auf_raster(h: float, *, auf: bool) -> float:
    teile = h / DICKENRASTER
    return (math.ceil(teile - 1e-9) if auf else math.floor(teile + 1e-9)) * DICKENRASTER


def dicke_suchen(projekt, kennung: str, *, modus: Suchmodus,
                 **wie) -> Dickenergebnis:
    """
    Die duennste Platte auf dem Zentimeter, bei der die Bewehrungssuche eine
    Loesung findet -- mit allen eingeschalteten Nachweisen, innerhalb der
    Obergrenze, und mit Duktilitaet, wenn sie eingeschaltet ist.

    Von der eingegebenen Dicke aus: geht es, wird halbiert, bis es nicht mehr
    geht -- nie unter die Mindestdicke der Platte (``automatik_mindestdicke``);
    geht schon sie, ist sie das Ergebnis. Geht es nicht, wird verdoppelt, bis
    es geht -- hoechstens bis :data:`DICKE_HOECHSTENS`. Eine Platte, die
    duenner eingegeben ist als die Mindestdicke, beginnt bei ihr. Dazwischen
    Bisektion auf dem Raster. Das setzt
    voraus, dass es innerhalb einer Verdopplung nur einmal von «geht nicht»
    zu «geht» wechselt: bei Biegung und Querkraft sicher, bei der
    Mindestbewehrung, die mit der Dicke waechst, erst bei sehr dicken Platten
    nicht mehr.

    ``wie`` geht an :func:`suche` (Teilungen, Durchmesser); das Projekt
    bleibt unberuehrt.
    """
    modus = Suchmodus(modus)
    ergebnis = Dickenergebnis(modus=modus)
    eintrag = projekt.querschnitt(kennung)
    duktil = eintrag.duktilitaet
    geprueft: Dict[float, bool] = {}
    suchen: Dict[float, Suchergebnis] = {}

    def geht(h: float) -> bool:
        if h not in geprueft:
            probe = copy.deepcopy(projekt)
            probe.querschnitt(kennung).h = h
            such = suche(probe, kennung, modus=modus.bewehrung, **wie)
            # Die Suche geht der Duktilitaet aus dem Weg (sie wird mit mehr
            # Stahl schlechter); hier zaehlt sie, wenn sie eingeschaltet ist --
            # eine dickere Platte ist das Mittel gegen sie.
            geprueft[h] = such.gefunden and not (duktil and such.duktilitaet_erfuellt is False)
            suchen[h] = such
            ergebnis.versuche.append(Dickenversuch(h, geprueft[h]))
        return geprueft[h]

    untergrenze = max(_auf_raster(eintrag.automatik_mindestdicke, auf=True), DICKENRASTER)
    start = max(_auf_raster(eintrag.h, auf=True), untergrenze)
    if geht(start):
        oben = start
        while oben > untergrenze:
            kandidat = max(_auf_raster(oben / 2.0, auf=False), untergrenze)
            if not geht(kandidat):
                unten = kandidat
                break
            oben = kandidat
        else:
            # Schon die Mindestdicke geht -- duenner darf es nicht werden.
            unten = oben - DICKENRASTER
    else:
        unten = start
        while True:
            oben = min(unten * 2.0, DICKE_HOECHSTENS)
            if oben <= unten:
                ergebnis.suche = suchen[unten]
                ergebnis.begruendung = (
                    f"Bis {DICKE_HOECHSTENS:.0f} mm keine Dicke, bei der alles "
                    f"aufgeht ({_versuche_text(ergebnis)}).")
                return ergebnis
            if geht(oben):
                break
            unten = oben

    while oben - unten > DICKENRASTER:
        mitte = _auf_raster((unten + oben) / 2.0, auf=False)
        if geht(mitte):
            oben = mitte
        else:
            unten = mitte

    ergebnis.h = oben
    ergebnis.suche = suchen[oben]
    ergebnis.begruendung = (f"h = {oben:.0f} mm ({_versuche_text(ergebnis)}). "
                            + ergebnis.suche.begruendung)
    return ergebnis


def _versuche_text(ergebnis: Dickenergebnis) -> str:
    """«300 ✓, 150 ✗, 220 ✓» -- die geprueften Dicken in mm, der Reihe nach."""
    return ", ".join(f"{v.h:.0f} {'✓' if v.geht else '✗'}" for v in ergebnis.versuche)
