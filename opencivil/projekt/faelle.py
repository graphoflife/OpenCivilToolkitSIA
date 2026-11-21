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
from opencivil.projekt.netz import neue_kennung


def kennung_von(eintrag: Any) -> str:
    """Die Kennung eines Eintrags -- oder die Kennung selbst."""
    return eintrag if isinstance(eintrag, str) else eintrag.kennung


@dataclass
class LastfallEintrag(Beschreibung):
    """Ein Lastfall: eine Kennung, auf die die Lasten zeigen, und ein Name."""

    IM_ORT = "Lastfall"

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

    IM_ORT = "Kombination"

    kennung: str = ""
    name: str = ""
    faktoren: Dict[str, float] = field(default_factory=dict)


class MitFaellen:
    """Der Baukasten der Faelle -- fuer ein Bauteil mit ``lastfaelle`` und ``kombinationen``."""

    lastfaelle: List[LastfallEintrag]
    kombinationen: List[LastkombinationEintrag]

    def lastfall(self, name: str, *, eigengewicht: bool = False) -> LastfallEintrag:
        eintrag = LastfallEintrag(kennung=neue_kennung(self, "LF", (lf.kennung for lf in self.lastfaelle)),
                                  name=name, eigengewicht=eigengewicht)
        self.lastfaelle.append(eintrag)
        return eintrag

    def kombination(self, name: str, *faktoren: Tuple[Any, float]) -> LastkombinationEintrag:
        """Eine Kombination -- je Lastfall (Eintrag oder Kennung) ein Beiwert: ``(g, 1.35), (w, 1.5)``."""
        eintrag = LastkombinationEintrag(
            kennung=neue_kennung(self, "LK", (k.kennung for k in self.kombinationen)), name=name,
            faktoren={kennung_von(lf): float(beiwert) for lf, beiwert in faktoren})
        self.kombinationen.append(eintrag)
        return eintrag

    def standardfaelle(self) -> LastkombinationEintrag:
        """
        Die Faelle eines frischen Bauteils (Benutzer, 2026-10-23): Eigengewicht
        -- es kommt von selbst --, Auflast und Nutzlast, die beiden ohne Last,
        und die Kombination GZT mit 1.35, 1.35 und 1.5. Zurueck kommt die GZT.
        """
        g = self.lastfall("Eigengewicht", eigengewicht=True)
        auflast = self.lastfall("Auflast")
        nutzlast = self.lastfall("Nutzlast")
        return self.kombination("GZT", (g, 1.35), (auflast, 1.35), (nutzlast, 1.5))

    def gebrauchskombination(self) -> LastkombinationEintrag:
        """Die Kombination GZG eines frischen Balkensystems: jeder Lastfall mit 1.0 (Benutzer, 2026-10-23)."""
        return self.kombination("GZG", *((lf, 1.0) for lf in self.lastfaelle))
