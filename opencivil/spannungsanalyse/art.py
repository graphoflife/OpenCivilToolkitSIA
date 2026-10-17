"""
opencivil/spannungsanalyse/art.py -- welche der sechs Fragen eine Analyse stellt.

VERANTWORTUNG:
Die Wahl einer Spannung-Dehnung-Analyse: aus Schnittgroessen, aus
Randdehnungen, die beiden Linien und der aequivalente Modul ueber jeder
(:class:`Analyseart`).
"""

from __future__ import annotations

from typing import Optional

from opencivil.core.wahl import Wahl


class Analyseart(Wahl):
    """Welche der sechs Fragen gestellt wird."""

    SCHNITTGROESSEN = "schnittgroessen"
    DEHNUNGEN = "dehnungen"
    MOMENT_KRUEMMUNG = "moment_kruemmung"
    NORMALKRAFT_DEHNUNG = "normalkraft_dehnung"
    MOMENT_EMODUL = "moment_emodul"
    NORMALKRAFT_EMODUL = "normalkraft_emodul"

    @property
    def beschriftung(self) -> str:
        return {
            Analyseart.SCHNITTGROESSEN: "Aus N und M",
            Analyseart.DEHNUNGEN: "Aus Randdehnungen",
            Analyseart.MOMENT_KRUEMMUNG: "Momenten-Krümmungs-Linie",
            Analyseart.NORMALKRAFT_DEHNUNG: "Normalkraft-Dehnungs-Linie",
            Analyseart.MOMENT_EMODUL: "Äquivalenter E-Modul über dem Moment",
            Analyseart.NORMALKRAFT_EMODUL: "Äquivalenter E-Modul über der Normalkraft",
        }[self]

    @property
    def kurz(self) -> str:
        """Fuer die Auswahl in der Zeile."""
        return {
            Analyseart.SCHNITTGROESSEN: "N, M",
            Analyseart.DEHNUNGEN: "ε oben/unten",
            Analyseart.MOMENT_KRUEMMUNG: "M–χ",
            Analyseart.NORMALKRAFT_DEHNUNG: "N–ε",
            Analyseart.MOMENT_EMODUL: "M–E_eq",
            Analyseart.NORMALKRAFT_EMODUL: "N–E_eq",
        }[self]

    @property
    def linie(self) -> Optional["Analyseart"]:
        """
        Die Linie, auf der diese Frage laeuft: M-chi oder N-eps -- der Modul
        ist dieselbe Linie, umgerechnet. ``None`` fuer die beiden Bilder.
        """
        return {
            Analyseart.MOMENT_KRUEMMUNG: Analyseart.MOMENT_KRUEMMUNG,
            Analyseart.MOMENT_EMODUL: Analyseart.MOMENT_KRUEMMUNG,
            Analyseart.NORMALKRAFT_DEHNUNG: Analyseart.NORMALKRAFT_DEHNUNG,
            Analyseart.NORMALKRAFT_EMODUL: Analyseart.NORMALKRAFT_DEHNUNG,
        }.get(self)

    @property
    def modul(self) -> bool:
        """Ob gefragt ist, welchen E-Modul ein reiner Betonquerschnitt braeuchte."""
        return self in (Analyseart.MOMENT_EMODUL, Analyseart.NORMALKRAFT_EMODUL)
