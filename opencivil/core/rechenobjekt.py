"""
opencivil/core/rechenobjekt.py -- was ein Bauteil im Rechenwerk ist.

VERANTWORTUNG:
Ein Rechenobjekt -- ein Fundament, eine Platte, ein Balkensystem, ein
Baustoff -- traegt seine Werte nach Kurzname (``definitionen``) und seine
Berechnungen (``berechnungen``) und meldet beides beim Rechenwerk an, nach
den Baustoffen, die es braucht. :class:`Rechenobjekt` sagt das einmal: die
Kennung eines Werts (:meth:`~Rechenobjekt.id_von`) und das Anmelden
(:meth:`~Rechenobjekt.ins_rechenwerk`).

Bis 2026-11-10 schrieben sieben Klassen beides von Hand. Zwei nannten bei
einem unbekannten Kurznamen die bekannten, die uebrigen warfen einen
blanken ``KeyError`` mit dem Kurznamen allein.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Sequence

if TYPE_CHECKING:
    from opencivil.core.berechnung import Berechnung
    from opencivil.core.wert import WertDef


class Rechenobjekt:
    """
    Siehe Dateikopf. Wer erbt, hat ``name``, ``definitionen`` und
    ``berechnungen`` -- als Felder seiner Datenklasse oder aus seinem
    ``__init__``.
    """

    #: Wie eine Meldung das Objekt nennt: «Querschnitt 'Decke' kennt …».
    WAS: ClassVar[str] = "Bauteil"

    name: str
    definitionen: Dict[str, "WertDef"]
    berechnungen: List["Berechnung"]

    def id_von(self, kurzname: str) -> str:
        """Die Wert-ID zu einem Kurznamen, etwa ``f_cd`` -> ``beton.C30_37.f_cd``."""
        if kurzname not in self.definitionen:
            raise KeyError(f"{self.WAS} '{self.name}' kennt keinen Wert '{kurzname}'. "
                           f"Bekannt: {sorted(self.definitionen)}.")
        return self.definitionen[kurzname].id

    @property
    def baustoffe(self) -> Sequence[Any]:
        """Die Baustoffe, die es braucht -- angemeldet vor ihm. Ohne Angabe keine."""
        return ()

    def ins_rechenwerk(self, werk) -> Any:
        """
        Meldet erst die Baustoffe an, dann die eigenen Werte und Berechnungen.
        Einen Baustoff zweimal anzumelden ist wirkungslos -- eine Platte weiss
        nicht, ob eine andere ihren Beton schon angemeldet hat.
        """
        for stoff in self.baustoffe:
            stoff.ins_rechenwerk(werk)
        werk.definiere(*self.definitionen.values())
        werk.registriere(*self.berechnungen)
        return self
