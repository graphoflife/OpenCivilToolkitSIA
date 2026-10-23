"""
opencivil/projekt/aufbau -- aus der Beschreibung ein Rechenwerk.

VERANTWORTUNG:
:func:`aufbauen` macht aus einem :class:`Projekt` Baustoffe, Querschnitte,
Nachweise und Balkensysteme und meldet sie in einem :class:`Rechenwerk` an.
Heraus kommt ein :class:`Aufbau` -- das Werk samt allen Nachweisobjekten und
Systemen, nach Bauteil und Art abgelegt, damit Schnittstelle,
Zwischenspeicher und Bewehrungssuche sie wiederfinden.

Die Beschreibung selbst rechnet nichts; hier wird sie zum ersten Mal
Rechnung. Darum stehen auch die Pruefungen hier, die erst beim Bauen
auffallen koennen -- ein Verweis auf ein geloeschtes Material, eine Platte
ohne Bewehrung.

DIE BAUTEILARTEN:
Platte, Querschnittsanalyse, Balkensystem, Grundbruch und Setzung haben je einen Steckbrief
(:class:`Bauteilart`) in :data:`BAUTEILE` -- Liste in der Datei, Klasse der
Eintraege, Vorsilbe der Kennungen, Namensraum, Baufunktion. Wer alle
Bauteile durchgeht, geht diese Liste durch; eine neue Art kommt dort dazu
und nirgends sonst. Gebaut wird je Eintrag ein :class:`Bauteil`, das seine
Nachweise, Ziele und Bezuege selbst fuehrt.

WO WAS STEHT:
Hier der Steckbrief, die Liste der Arten und :func:`aufbauen`, das sie
durchgeht. Je Art ein Modul mit ihrer Baufunktion ``bauen``
(:mod:`~opencivil.projekt.aufbau.platte`,
:mod:`~opencivil.projekt.aufbau.querschnittsanalyse`,
:mod:`~opencivil.projekt.aufbau.balkensystem`,
:mod:`~opencivil.projekt.aufbau.grundbruch`,
:mod:`~opencivil.projekt.aufbau.setzung`); was mehr als eine braucht, im
Kern (:mod:`~opencivil.projekt.aufbau.kern`): der Aufbau, das Bauteil, die
Baustoffe, die Stahlspannungen und der Knickfall. Bis 2026-10-17 stand alles
in einer Datei von ueber tausend Zeilen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple

from opencivil.core.rechenwerk import Rechenwerk
from opencivil.projekt.balkensystem import BalkensystemEintrag
from opencivil.projekt.grundbruch import GrundbruchEintrag
from opencivil.projekt.platte import QuerschnittEintrag
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.projekt.setzung import SetzungEintrag

from opencivil.projekt.aufbau import (
    balkensystem, grundbruch, platte, querschnittsanalyse, setzung,
)
from opencivil.projekt.aufbau.kern import Aufbau, Bauteil, baustoff_bauen, ueberschreibungen_setzen

if TYPE_CHECKING:
    from opencivil.projekt.projekt import Projekt

__all__ = [
    "ANALYSE", "Aufbau", "BALKENSYSTEM", "BAUTEILE", "Bauteil", "Bauteilart", "GRUNDBRUCH",
    "PLATTE", "SETZUNG", "aufbauen",
]


def aufbauen(projekt: "Projekt", *, schnell: bool = False) -> Aufbau:
    """
    Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

    Wirft :class:`~opencivil.projekt.lesen.ProjektFehler`, wenn die
    Beschreibung nicht stimmig ist -- etwa wenn ein Querschnitt auf ein
    geloeschtes Material verweist.

    Mit ``schnell`` lassen Nachweise teure Nebenrechnungen weg, die das
    Urteil nicht aendern -- die Suche nach der Knickgrenzkraft und die
    genaue Resistenzlinie --, und ganz stille Nachweise entstehen gar
    nicht erst. Gedacht fuer das Bewehrungswerkzeug, das hundertfach
    rechnet und nur wissen muss, ob es aufgeht. Fuer eine Herleitung ist
    das nichts: dort soll die Zahl stehen, die auch in der Tabelle steht.
    """
    projekt.pruefen()
    projekt.inhalt_pruefen()
    werk = Rechenwerk()
    aufbau = Aufbau(werk=werk, schnell=schnell)

    # Nur wenn mehrere Materialien derselben Art vorkommen, braucht es
    # Indizes an den Symbolen -- sonst waere f_{cd,C30/37} bloss Ballast.
    je_art: Dict[str, int] = {}
    for m in projekt.materialien:
        je_art[m.art] = je_art.get(m.art, 0) + 1
    for eintrag in projekt.materialien:
        index = eintrag.anzeigename if je_art[eintrag.art] > 1 else ""
        aufbau.baustoffe[eintrag.kennung] = baustoff_bauen(eintrag, index)

    # Auch im schnellen Aufbau jedes Bauteil: die Formelsammlung entsteht aus
    # ihm. Die Bewehrungssuche loest nur Nachweisziele, ein System kostet sie
    # also nur das Anmelden.
    for art in BAUTEILE:
        for eintrag in getattr(projekt, art.liste):
            teil = art.bauen(art, eintrag, aufbau)
            if teil is not None:
                aufbau.teile[eintrag.kennung] = teil

    for baustoff in aufbau.baustoffe.values():
        baustoff.ins_rechenwerk(werk)

    ueberschreibungen_setzen(projekt, werk, aufbau)
    return aufbau


# ===========================================================================
# Die Bauteilarten
# ===========================================================================


@dataclass(frozen=True)
class Bauteilart:
    """
    Der Steckbrief einer Bauteilart: was ausserhalb ihres Eintrags und ihrer
    Baufunktion von ihr bekannt sein muss. Eine neue Art kommt in
    :data:`BAUTEILE` dazu und nirgends sonst.
    """

    name: str
    """Wie sie im Aufbau, im Bericht und in der Oberflaeche heisst: ``platte``."""

    liste: str
    """Ihre Liste im :class:`Projekt` und in der Datei: ``querschnitte``."""

    eintrag: type
    """Die Klasse ihrer Eintraege -- sie liest einen Eintrag aus der Datei."""

    vorsilbe: str
    """Womit ihre Kennungen beginnen: ``q`` fuer q1, q2 ..."""

    raum: str
    """Womit ihre Namensraeume beginnen: ``querschnitt`` fuer querschnitt.q1."""

    bereich: str
    """Wie ihr Abschnitt in der Formelsammlung heisst."""

    bauen: Callable[["Bauteilart", Any, Aufbau], Optional[Bauteil]]
    """
    Aus dem Eintrag das Bauteil -- Objekt und Nachweise, angemeldet im Werk.
    ``None``, wo es nichts zu rechnen gibt: eine Querschnittsanalyse, in der
    noch nichts gezeichnet ist.
    """


PLATTE = Bauteilart("platte", "querschnitte", QuerschnittEintrag, "q",
                    "querschnitt", "Platte", platte.bauen)
ANALYSE = Bauteilart("querschnittsanalyse", "querschnittsanalysen",
                     QuerschnittsanalyseEintrag, "a", "querschnittsanalyse",
                     "Querschnittsanalyse", querschnittsanalyse.bauen)
BALKENSYSTEM = Bauteilart("balkensystem", "balkensysteme", BalkensystemEintrag, "r",
                          "balkensystem", "Balkensysteme", balkensystem.bauen)
GRUNDBRUCH = Bauteilart("grundbruch", "grundbrueche", GrundbruchEintrag, "g",
                        "grundbruch", "Grundbruch", grundbruch.bauen)
#: Die Kennungen w1, w2 ...: «s» tragen schon die Betonstaehle.
SETZUNG = Bauteilart("setzung", "setzungen", SetzungEintrag, "w", "setzung", "Setzung",
                     setzung.bauen)

#: Die Bauteilarten, in der Reihenfolge von Baum, Bericht und Rechnung -- ein
#: Balkensystem liest Werte der Platten und Analysen, also kommt es nach
#: ihnen; Grundbruch und Setzung lesen nichts von den anderen.
#: Wer alle Bauteile durchgeht (Lesen, Kennungen, Aufbau, Zwischenspeicher,
#: Erkennen einer Datei), geht diese Liste durch.
BAUTEILE: Tuple[Bauteilart, ...] = (PLATTE, ANALYSE, BALKENSYSTEM, GRUNDBRUCH, SETZUNG)
