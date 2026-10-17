"""
opencivil/core/wahl.py -- was ein Wahlfeld annehmen kann.

VERANTWORTUNG:
Die Grundlage jeder Wahl im Projekt: Rechenart, Wertesatz, Zugseite,
Rissanforderung und die übrigen. Ein Mitglied ist zugleich sein Text --
``Rechenart.BLOCK == "block"``, und ``json.dumps`` schreibt ``"block"`` --,
und es gibt sich als dieser Text aus, in Meldungen und in Formeln. Ein
Text, den es nicht gibt, meldet sich mit den möglichen Werten.

Bis 2026-10-17 trug jede Wahl ihr eigenes ``__str__`` oder keines: acht von
zwölf schrieben sich in einer Meldung als «Rechenart.BLOCK».
"""

from __future__ import annotations

from enum import StrEnum


class Wahl(StrEnum):
    """Eine Wahl: das Mitglied ist sein Text."""

    @classmethod
    def _missing_(cls, wert: object) -> "Wahl":
        raise ValueError(f"{wert!r} gibt es als {cls.__name__} nicht. Möglich sind: "
                         f"{', '.join(m.value for m in cls)}.")
