"""
opencivil/core/sprache.py -- wie das Werkzeug eine Liste von Woertern in einen Satz setzt.

VERANTWORTUNG:
«A, B und C», «Beton, Baustahl oder Holz»: die eine Stelle, an der eine
Aufzaehlung zum Satzteil wird. Bis 2026-11-27 stand dieselbe Zeile an fuenf
Stellen, zweimal als eigene Hilfe.
"""

from __future__ import annotations

from typing import Sequence


def aufgezaehlt(teile: Sequence[str], wort: str = "und") -> str:
    """«A», «A und B», «A, B und C» -- mit ``wort`` «oder»: «A, B oder C»."""
    return f" {wort} ".join(filter(None, (", ".join(teile[:-1]), teile[-1])))
