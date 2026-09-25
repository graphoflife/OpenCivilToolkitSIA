"""
opencivil/ergebnis.py -- ein gerechnetes Projekt, wie man es ohne Oberflaeche braucht.

VERANTWORTUNG:
Buendelt, was :meth:`Projekt.rechnen` liefert -- die Beschreibung, den Aufbau
und die Loesung -- und die drei Arten, sie anzusehen: die Zusammenfassung,
den vollstaendigen Bericht und das LaTeX-Dokument.

KEINE EIGENE RECHNUNG, KEINE EIGENE DARSTELLUNG:
Alles hier ruft auf, was Oberflaeche und Berichte auch benutzen. Ein zweiter
Weg zu denselben Zahlen waere ein zweiter Ort, an dem sie auseinanderlaufen.

    from opencivil import Projekt

    p = Projekt("Decke über EG")
    p.beton("C30/37")
    p.stahl("B500B")
    q = p.platte("Decke", h=300, x=[18, 12], y=[12, 12])
    q.einwirkung("Feld", M_Ed=100)
    ergebnis = p.rechnen()
    print(ergebnis.zusammenfassung())
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List

from opencivil import spannungsanalyse
from opencivil.bericht import konsole
from opencivil.bericht.latex_dokument import Ausgabeergebnis, schreibe
from opencivil.bericht.zusammenfassung import zusammenfassen
from opencivil.core.berechnung import NachweisUrteil
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert
from opencivil.spannungsanalyse import Analyse

if TYPE_CHECKING:
    from opencivil.projekt import Aufbau, Projekt


@dataclass
class Ergebnis:
    """Ein gerechnetes Projekt."""

    projekt: "Projekt"
    aufbau: "Aufbau"
    loesung: Loesung

    # -- Urteile ------------------------------------------------------------

    @property
    def erfuellt(self) -> bool:
        """Ob alle gefuehrten Nachweise aufgehen -- die ausgeschalteten zaehlen nicht."""
        return self.loesung.alle_nachweise_erfuellt

    @property
    def urteile(self) -> List[NachweisUrteil]:
        """Die gefuehrten Urteile, so wie sie in der Zusammenfassung stehen."""
        return self.loesung.gefuehrte_urteile

    @property
    def stille_maengel(self) -> List[NachweisUrteil]:
        """Was ausgeschaltet ist und trotzdem nicht aufgeht."""
        return self.loesung.stille_maengel

    @property
    def warnungen(self) -> List[str]:
        """Was beim Aufbau aufgefallen ist -- etwa eine Platte ohne Einwirkung."""
        return list(self.aufbau.warnungen)

    def urteile_von(self, platte: str) -> List[NachweisUrteil]:
        """Die gefuehrten Urteile einer Platte -- nach Name oder Kennung."""
        for eintrag in self.projekt.querschnitte:
            if platte in (eintrag.kennung, eintrag.name):
                return self.aufbau.urteile_von(eintrag.kennung, self.urteile)
        namen = ", ".join(f"'{q.name}'" for q in self.projekt.querschnitte)
        raise KeyError(f"Eine Platte '{platte}' gibt es nicht. Vorhanden: {namen}.")

    def wert(self, wert_id: str) -> Wert:
        """Ein einzelner gerechneter Wert, mit Einheit, Herkunft und Norm."""
        return self.loesung.wert(wert_id)

    def analysen(self) -> Dict[str, List[Analyse]]:
        """
        Die Spannung-Dehnung-Analysen je Platte -- Bilder, keine Nachweise.

        Dieselben, die die Oberflaeche zeichnet: je Fall das Querschnittsbild
        (Dehnungsebene, Spannungen, Schnittgroessen) oder die
        Momenten-Kruemmungs-Linie, in SI.
        """
        return spannungsanalyse.analysen(self.aufbau, self.loesung)

    # -- Ansehen ------------------------------------------------------------

    def zusammenfassung(self) -> str:
        """Je Platte eine Tabelle der Nachweise -- wie in der Oberflaeche."""
        return konsole.zusammenfassung(zusammenfassen(self.aufbau, self.loesung))

    def bericht(self) -> str:
        """Der vollstaendige Bericht mit Herleitung, als Text."""
        return konsole.als_text(self.loesung, titel=self.projekt.name,
                                aufbau=self.aufbau)

    def latex(self, pfad: str | Path, *, pdf: bool = False) -> Ausgabeergebnis:
        """
        Das LaTeX-Dokument, auf Wunsch auch als PDF.

        ``pdf`` ist aus, solange niemand es verlangt: uebersetzt wird mit dem,
        was auf dem Rechner an TeX liegt, und das ist nicht ueberall etwas.
        """
        return schreibe(self.loesung, pfad, titel=self.projekt.name, pdf=pdf,
                        aufbau=self.aufbau)

    def __str__(self) -> str:
        return self.zusammenfassung()
