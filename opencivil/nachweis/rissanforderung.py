"""
opencivil/nachweis/rissanforderung.py -- die Anforderung an die Rissbildung.

VERANTWORTUNG:
Die drei Stufen und was jede verlangt, an einer Stelle: wie sie heisst,
welche nominelle Rissbreite sie begrenzt und ob sie den Nachweis gegen
Fliessen unter haeufiger Einwirkung verlangt.

Vorher stand das in vier Tabellen -- die Rissbreite in der Mindestbewehrung,
der Fliessnachweis in der Spannungsbegrenzung, die Beschriftung im Leser,
die Liste fuer die Maske daraus gebaut --, und eine unbekannte Stufe wurde
an zwei Stellen ueber ``.get`` zur mildesten. Jetzt ist eine unbekannte
Stufe ein Fehler, wo immer sie auftaucht.

Die Rissbreiten 0.5 und 0.2 mm sind nach Vorgabe eingebaut, nicht
nachgeschlagen; dass bei normaler Anforderung kein Nachweis gegen Fliessen
gefuehrt wird, steht in SIA 262:2025, Tabelle 17 (ein Strich).
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


class Rissanforderung(str, Enum):
    """Normal, erhoeht oder hoch -- wie die Maske und die Datei sie schreiben."""

    NORMAL = "normal"
    ERHOEHT = "erhoeht"
    HOCH = "hoch"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def _missing_(cls, wert: object) -> "Rissanforderung":
        raise ValueError(f"Unbekannte Rissanforderung '{wert}'. Möglich sind: "
                         f"{', '.join(a.value for a in cls)}.")

    @property
    def beschriftung(self) -> str:
        """Wie sie an der Maske heisst."""
        return {Rissanforderung.NORMAL: "Normal", Rissanforderung.ERHOEHT: "Erhöht",
                Rissanforderung.HOCH: "Hoch"}[self]

    @property
    def rissbreite(self) -> Optional[float]:
        """
        Die nominelle Rissbreite w_nom in m -- ``None`` heisst: keine Grenze aus
        der Rissbreite, dann gilt allein ``f_yk``. Nach Vorgabe, nicht
        nachgeschlagen.
        """
        return {Rissanforderung.NORMAL: None, Rissanforderung.ERHOEHT: 0.5e-3,
                Rissanforderung.HOCH: 0.2e-3}[self]

    @property
    def gegen_fliessen(self) -> bool:
        """Ob der Nachweis gegen Fliessen unter haeufiger Einwirkung verlangt ist (Tabelle 17)."""
        return self is not Rissanforderung.NORMAL


#: Die Stufen, wie sie in der Datei stehen -- fuer die Wahl am Feld.
RISSANFORDERUNGEN = tuple(a.value for a in Rissanforderung)
