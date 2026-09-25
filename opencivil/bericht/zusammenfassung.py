"""
opencivil/bericht/zusammenfassung.py -- welche Zeilen in der Zusammenfassung stehen.

VERANTWORTUNG:
Je Platte die gefuehrten Urteile und darunter die still verfehlten -- als
Daten, nicht als Text. Die Oberflaeche setzt daraus LaTeX-Zellen
(:func:`opencivil.web.api.zusammenfassungen`), die Konsole eine Texttabelle
(:func:`opencivil.bericht.konsole.zusammenfassung`).

WARUM EIN EIGENES MODUL:
Vorher baute jede Darstellung ihre Zeilen selbst, und sie liefen schon
auseinander, bevor jemand es merkte: die Oberflaeche nannte einen still
verfehlten Nachweis mit seinem ausgeschriebenen Namen, die Konsole mit dem
langen Urteilsnamen; die eine liess leere Platten weg, die andere nicht.
Welche Urteile zu einer Platte gehoeren und wie ein Nachweis in der Spalte
heisst, steht jetzt hier und nur hier. Wie es aussieht, entscheidet die
Darstellung.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from opencivil.core.berechnung import NachweisUrteil
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert

if TYPE_CHECKING:
    from opencivil.projekt import Aufbau


@dataclass(frozen=True)
class Zeile:
    """Ein Urteil, wie es in der Zusammenfassung steht."""

    nachweis: str
    """Die Nachweisart ausgeschrieben -- faellt sie aus, das Kuerzel, dann der Name."""

    fall: str
    """Der Fall oder die Lage; leer, wo es keinen gibt."""

    widerstand: Optional[Wert]
    einwirkung: Optional[Wert]
    urteil: NachweisUrteil
    """Fuer alles Weitere: erfuellt, Grad, Begruendung, Hinweis."""

    @classmethod
    def aus(cls, urteil: NachweisUrteil) -> "Zeile":
        return cls(nachweis=urteil.langname or urteil.art or urteil.name,
                   fall=urteil.fall, widerstand=urteil.widerstand,
                   einwirkung=urteil.einwirkung, urteil=urteil)


@dataclass(frozen=True)
class Platte:
    """Die Zusammenfassung einer Platte."""

    kennung: str
    name: str
    zeilen: List[Zeile]
    """Die gefuehrten Urteile -- je Nachweis mit Lagen nur die schlechtere."""

    stille: List[Zeile]
    """Was ausgeschaltet ist und trotzdem nicht aufgeht."""

    @property
    def leer(self) -> bool:
        return not self.zeilen and not self.stille


@dataclass(frozen=True)
class Zusammenfassung:
    """Alle Platten, das Gesamturteil und was beim Aufbau auffiel."""

    platten: List[Platte]
    erfuellt: bool
    """Ob alle gefuehrten Nachweise aufgehen."""

    gefuehrt: bool
    """Ob ueberhaupt einer gefuehrt wurde -- sonst gibt es kein Gesamturteil."""

    warnungen: List[str]


def zusammenfassen(aufbau: "Aufbau", loesung: Loesung) -> Zusammenfassung:
    """
    Die Zeilen je Platte, in der Reihenfolge der Beschreibung.

    Die Urteile kommen fertig aus der Loesung: ohne die stillen, und je
    Nachweis, der seine Lagen sammelt, nur die schlechteste. Hier zu filtern
    hiesse, diese Regel ein zweites Mal zu schreiben.
    """
    platten = [
        Platte(
            kennung=kennung,
            name=querschnitt.name,
            zeilen=[Zeile.aus(u) for u in
                    aufbau.urteile_von(kennung, loesung.gefuehrte_urteile)],
            stille=[Zeile.aus(u) for u in
                    aufbau.urteile_von(kennung, loesung.stille_maengel)],
        )
        for kennung, querschnitt in aufbau.querschnitte.items()
    ]
    return Zusammenfassung(
        platten=platten,
        erfuellt=loesung.alle_nachweise_erfuellt,
        gefuehrt=bool(loesung.gefuehrte_urteile),
        warnungen=list(aufbau.warnungen),
    )
