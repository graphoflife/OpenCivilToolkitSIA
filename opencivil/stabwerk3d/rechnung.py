"""
opencivil/stabwerk3d/rechnung.py -- das 3D-Balkensystem im Rechenwerk.

VERANTWORTUNG:
Wie das ebene Balkensystem (:mod:`opencivil.stabwerk.rechnung`), im Raum:
je Querschnitt ``A``, ``I_y``, ``I_z`` und ``I_T``, je Paar aus
Querschnitt und Material ``EA``, ``EI_y``, ``EI_z`` und ``GI_T`` und das
Eigengewicht, und eine Prozedur, die das System rechnet
(:mod:`~opencivil.stabwerk3d.system`) und ihre Herleitung schreibt
(:mod:`~opencivil.stabwerk3d.herleitung`). Was beide gleich tun, steht in
:class:`~opencivil.stabwerk.rechnung.Stabwerksrechnung`.

STEIFIGKEIT -- NACH VORGABE, NICHT NACHGESCHLAGEN:
Wie in der Ebene, die Torsion mit ``G_cm`` des Betons, ``G_a`` des
Baustahls oder G von Hand -- am ungerissenen Querschnitt und nach St.
Venant, ohne Woelbkrafttorsion. Die Herleitung sagt es, das TODO fuehrt es.
"""

from __future__ import annotations

from typing import Dict, List

from opencivil.core.einheiten import KNM2
from opencivil.core.protokoll import Protokoll
from opencivil.stabwerk.modell import Lastart
from opencivil.stabwerk.rechnung import (
    DEHNSTEIFIGKEIT, DICHTE, E_MODUL, SCHUBMODUL, Stabwerksrechnung, Steifigkeitsformel,
    Systembefund, stoffkennwerte,
)
from opencivil.stabwerk.stabquerschnitt import RAEUMLICH
from opencivil.stabwerk.system import Meldung
from opencivil.stabwerk3d import herleitung
from opencivil.stabwerk3d.modell import Richtung, Stablast, System
from opencivil.stabwerk3d.system import Ergebnis, Fall, rechnen
from opencivil.stabwerk3d.verlauf import Stabverlauf, verlaeufe

#: Welche Kennwerte eines Baustoffs ein Stab im Raum aus ihm nimmt.
RAUMKENNWERTE = stoffkennwerte((E_MODUL, DICHTE, SCHUBMODUL))


class Raumbefund(Systembefund):
    """Was die Rechnung im Raum fand -- wie in der Ebene, mit den Verlaeufen des Raums."""

    @staticmethod
    def _verlaeufe_von(fall: Fall) -> Dict[str, Stabverlauf]:
        return verlaeufe(fall)


class Balkensystem3d(Stabwerksrechnung):
    """Ein 3D-Balkensystem, fertig fuer das Rechenwerk."""

    WAS = "3D-Balkensystem"
    KENNWERTE = RAEUMLICH
    STEIFIGKEITEN = (
        DEHNSTEIFIGKEIT,
        Steifigkeitsformel("EI_y", KNM2, "Biegesteifigkeit um y", "E", "I_y"),
        Steifigkeitsformel("EI_z", KNM2, "Biegesteifigkeit um z", "E", "I_z"),
        Steifigkeitsformel("GI_T", KNM2, "Torsionssteifigkeit", "G", "I_T"),
    )
    MATERIALKENNWERTE = (E_MODUL, DICHTE, SCHUBMODUL)

    def _rechnen(self, system: System) -> Ergebnis:
        return rechnen(system)

    def _leer(self, meldungen: List[Meldung]) -> Ergebnis:
        return Ergebnis(meldungen=meldungen)

    def _eigenlast(self, stab: str, g: float) -> Stablast:
        return Stablast(stab=stab, art=Lastart.LINIENLAST, wert_a=g, richtung=Richtung.SENKRECHT)

    def _befund(self, gerechnet: System, ergebnis: Ergebnis,
                eigengewicht: Dict[str, float]) -> Raumbefund:
        return Raumbefund(gerechnet, ergebnis, eigengewicht=eigengewicht)

    def _schreiben(self, p: Protokoll, befund: Systembefund) -> None:
        herleitung.schreiben(p, self, befund)
