"""
opencivil/querschnitt/bauweise.py -- woraus ein gezeichneter Querschnitt besteht.

VERANTWORTUNG:
Die Bauweise eines gezeichneten Querschnitts aus den Arten seiner Baustoffe
(:func:`bauweise`): Stahlbeton, Stahl, Verbund, Blechverbund oder Holz. Nach ihr richtet
sich, welche Nachweise er hat und nach welcher Norm. Eine Mischung, die
keine davon ist, rechnet das Werkzeug nicht; der Satz dazu nennt die
Materialien beim Namen.

DIE REGEL (Benutzer, 2026-11-25):
* Beton, mit oder ohne Betonstahl und Spannstahl: Stahlbeton -- auch ohne
  Bewehrung, wie bisher; seine Nachweise sagen dann, was ihnen fehlt.
* nur Baustahl: Stahl.
* Baustahl mit Beton, mit oder ohne Betonstahl: Verbund.
* nur Holz: Holz.
* Profilblechstahl mit Beton, mit oder ohne Betonstahl: Blechverbund -- eine
  Blechverbunddecke nach SIA 264:2014, 5.4 (2026-11-27). Mit Baustahl dazu
  waere es ein Verbundtraeger mit Profilblech (6.1.3); den rechnet das
  Werkzeug noch nicht.

Holz mit einem anderen Baustoff ist keine davon, ebenso Spannstahl neben
Baustahl. Ohne Material hat ein Querschnitt keine Bauweise: es gibt nichts,
was traegt, und das sagt schon die Zeichnung
(:class:`~opencivil.querschnitt.analyse.Zeichnung`).

Welche Arten eine Flaeche nehmen darf, steht an ihrem Feld
(:func:`~opencivil.projekt.lesen.materialfeld`), nicht hier; worin
Bewehrung liegt, in :data:`BEWEHRT`.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from opencivil.core.sprache import aufgezaehlt
from opencivil.core.wahl import Wahl
from opencivil.material.basis import Baustoffart


#: Worin Bewehrung liegt -- Stab, Stablinie, Schubwand und Spannglied: nur
#: im Beton, nicht in Holz und nicht in Baustahl (Benutzer, 2026-11-25). Die
#: Zeichnung prueft es (:class:`~opencivil.querschnitt.analyse.Zeichnung`),
#: und eine Vorlage aus anderem kommt ohne Bewehrung.
BEWEHRT = Baustoffart.BETON


class Bauweise(Wahl):
    """Woraus ein gezeichneter Querschnitt besteht -- siehe Dateikopf."""

    STAHLBETON = "stahlbeton"
    STAHL = "stahl"
    VERBUND = "verbund"
    BLECHVERBUND = "blechverbund"
    HOLZ = "holz"

    @property
    def querschnitt(self) -> str:
        """Wie ein Satz einen Querschnitt dieser Bauweise nennt: «ein Holzquerschnitt»."""
        return {
            Bauweise.STAHLBETON: "Stahlbetonquerschnitt",
            Bauweise.STAHL: "Stahlquerschnitt",
            Bauweise.VERBUND: "Verbundquerschnitt",
            Bauweise.BLECHVERBUND: "Blechverbundquerschnitt",
            Bauweise.HOLZ: "Holzquerschnitt",
        }[self]

    @property
    def norm(self) -> str:
        """Die Norm, nach der ein Querschnitt dieser Bauweise nachgewiesen wird."""
        return {
            Bauweise.STAHLBETON: "SIA 262:2025",
            Bauweise.STAHL: "SIA 263:2013",
            Bauweise.VERBUND: "SIA 264:2014",
            Bauweise.BLECHVERBUND: "SIA 264:2014",
            Bauweise.HOLZ: "SIA 265:2012",
        }[self]


#: Woraus eine Blechverbunddecke sein darf -- Beton muss dabei sein.
BLECHVERBUND = frozenset({Baustoffart.PROFILBLECH, Baustoffart.BETON, Baustoffart.BETONSTAHL})


class Mischung(ValueError):
    """Baustoffe, die zusammen keine Bauweise sind -- der Text nennt sie."""


def bauweise(stoffe: Iterable[Tuple[Baustoffart, str]]) -> Optional[Bauweise]:
    """
    Die Bauweise aus Art und Name jedes Baustoffs eines Querschnitts --
    ``None`` ohne Baustoff. Ist die Mischung keine Bauweise, eine
    :class:`Mischung`, die jede Art mit ihren Materialien nennt: «Einen
    Querschnitt aus Holz («C24») und Beton («C30/37») rechnet das Werkzeug
    nicht.»
    """
    namen: Dict[Baustoffart, List[str]] = {}
    for art, name in stoffe:
        liste = namen.setdefault(Baustoffart(art), [])
        if name not in liste:
            liste.append(name)
    arten = set(namen)
    if not arten:
        return None
    if Baustoffart.PROFILBLECH in arten:
        if Baustoffart.BETON in arten and arten <= BLECHVERBUND:
            return Bauweise.BLECHVERBUND
    elif arten == {Baustoffart.HOLZ}:
        return Bauweise.HOLZ
    elif Baustoffart.HOLZ not in arten:
        if arten == {Baustoffart.BAUSTAHL}:
            return Bauweise.STAHL
        if Baustoffart.BAUSTAHL not in arten:
            return Bauweise.STAHLBETON
        if Baustoffart.BETON in arten and Baustoffart.SPANNSTAHL not in arten:
            return Bauweise.VERBUND
    teile = [f"{art.beschriftung} ({', '.join(f'«{n}»' for n in liste)})"
             for art, liste in namen.items()]
    raise Mischung(f"Einen Querschnitt aus {aufgezaehlt(teile)} rechnet das Werkzeug nicht.")
