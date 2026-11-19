"""
opencivil/geotechnik/verhalten.py -- wie ein Boden traegt.

VERANTWORTUNG:
Die eine Wahl, die Pfahl und Grundbruch teilen (:class:`Verhalten`):
drainiert mit wirksamen Spannungen, Reibungswinkel und Kohaesion;
undrainiert mit totalen Spannungen und der undrainierten Scherfestigkeit
s_u. Beide zeigen sie als denselben Schalter (Benutzer, 2026-11-19); bis
dahin hiess im Grundbruch phi = 0 undrainiert.
"""

from __future__ import annotations

from opencivil.core.wahl import Wahl


class Verhalten(Wahl):
    """Womit ein Boden traegt: drainiert mit Reibung und Kohaesion, undrainiert mit s_u."""

    DRAINIERT = "drainiert"
    UNDRAINIERT = "undrainiert"

    @property
    def beschriftung(self) -> str:
        return {Verhalten.DRAINIERT: "drainiert", Verhalten.UNDRAINIERT: "undrainiert"}[self]

    @property
    def erklaerung(self) -> str:
        # Ohne Zeichen: der Pfahl schreibt φ'_k, der Grundbruch φ_k.
        return {Verhalten.DRAINIERT: "Wirksame Spannungen, mit Reibungswinkel und Kohäsion",
                Verhalten.UNDRAINIERT: "Totale Spannungen, mit der undrainierten "
                                       "Scherfestigkeit s_u,k"}[self]
