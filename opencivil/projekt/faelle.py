"""
opencivil/projekt/faelle.py -- Lastfaelle und Kombinationen eines Bauteils.

VERANTWORTUNG:
Was Balkensystem und Decke an Faellen gleich fuehren: der Lastfall -- eine
Kennung, auf die die Lasten zeigen, ein Name, und ob er das Eigengewicht
bekommt -- und die Kombination mit je Lastfall einem Beiwert. Dazu der
Baukasten, mit dem ein Bauteil in Python seine Faelle anlegt
(:class:`MitFaellen`), samt den Faellen, die ein frisches Bauteil
mitbringt. Geprueft werden sie beim Bauen
(:mod:`opencivil.projekt.aufbau.faelle`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from opencivil.projekt.eintraege import Beschreibung
from opencivil.projekt.netz import naechste_kennung


def kennung_von(eintrag: Any) -> str:
    """Die Kennung eines Eintrags -- oder die Kennung selbst."""
    return eintrag if isinstance(eintrag, str) else eintrag.kennung


@dataclass
class LastfallEintrag(Beschreibung):
    """Ein Lastfall: eine Kennung, auf die die Lasten zeigen, und ein Name."""

    kennung: str = ""
    name: str = ""
    eigengewicht: bool = False
    """
    Ob der Lastfall das Eigengewicht bekommt -- von selbst, aus Dichte und
    Querschnitt (Benutzer, 2026-10-23). Ein Bauteil hat einen davon.
    """


@dataclass
class LastkombinationEintrag(Beschreibung):
    """Eine Kombination: je Lastfall (Kennung) ein Beiwert, von Hand."""

    kennung: str = ""
    name: str = ""
    faktoren: Dict[str, float] = field(default_factory=dict)


class MitFaellen:
    """Der Baukasten der Faelle -- fuer ein Bauteil mit ``lastfaelle`` und ``kombinationen``."""

    lastfaelle: List[LastfallEintrag]
    kombinationen: List[LastkombinationEintrag]

    def lastfall(self, name: str, *, eigengewicht: bool = False) -> LastfallEintrag:
        eintrag = LastfallEintrag(kennung=naechste_kennung((lf.kennung for lf in self.lastfaelle), "LF"),
                                  name=name, eigengewicht=eigengewicht)
        self.lastfaelle.append(eintrag)
        return eintrag

    def kombination(self, name: str, *faktoren: Tuple[Any, float]) -> LastkombinationEintrag:
        """Eine Kombination -- je Lastfall (Eintrag oder Kennung) ein Beiwert: ``(g, 1.35), (w, 1.5)``."""
        eintrag = LastkombinationEintrag(
            kennung=naechste_kennung((k.kennung for k in self.kombinationen), "LK"), name=name,
            faktoren={kennung_von(lf): float(beiwert) for lf, beiwert in faktoren})
        self.kombinationen.append(eintrag)
        return eintrag

    def standardfaelle(self) -> Tuple[LastkombinationEintrag, LastkombinationEintrag]:
        """
        Die Faelle eines frischen Bauteils (Benutzer, 2026-10-23): Eigengewicht
        -- es kommt von selbst --, Auflast und Nutzlast, die beiden ohne Last,
        und die Kombinationen GZT mit 1.35, 1.35 und 1.5 und GZG mit je 1.0.
        Zurueck kommen GZT und GZG.
        """
        g = self.lastfall("Eigengewicht", eigengewicht=True)
        auflast = self.lastfall("Auflast")
        nutzlast = self.lastfall("Nutzlast")
        gzt = self.kombination("GZT", (g, 1.35), (auflast, 1.35), (nutzlast, 1.5))
        gzg = self.kombination("GZG", (g, 1.0), (auflast, 1.0), (nutzlast, 1.0))
        return gzt, gzg
