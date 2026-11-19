"""
opencivil/projekt/aufbau -- aus der Beschreibung ein Rechenwerk.

VERANTWORTUNG:
:func:`aufbauen` macht aus einem :class:`Projekt` Baustoffe, Querschnitte,
Nachweise, Balkensysteme und Decken und meldet sie in einem :class:`Rechenwerk` an.
Heraus kommt ein :class:`Aufbau` -- das Werk samt allen Nachweisobjekten und
Systemen, nach Bauteil und Art abgelegt, damit Schnittstelle,
Zwischenspeicher und Bewehrungssuche sie wiederfinden.

Die Beschreibung selbst rechnet nichts; hier wird sie zum ersten Mal
Rechnung. Darum stehen auch die Pruefungen hier, die erst beim Bauen
auffallen koennen -- ein Verweis auf ein geloeschtes Material, eine Platte
ohne Bewehrung.

DIE BAUTEILARTEN:
Platte, Querschnittsanalyse, 2D- und 3D-Balkensystem, Decke, Durchstanzen, Grundbruch,
Setzung und Pfahl haben je einen Steckbrief
(:class:`Bauteilart`) in :data:`BAUTEILE` -- Liste in der Datei, Klasse der
Eintraege, Vorsilbe der Kennungen, Namensraum, Baufunktion. Wer alle
Bauteile durchgeht, geht diese Liste durch. Gebaut wird je Eintrag ein
:class:`Bauteil`, das seine Nachweise, Ziele und Bezuege selbst fuehrt.

Was Bericht und Oberflaeche je Art brauchen, kennt der Kern nicht; es steht
in ihren Schichten, je an einer Stelle: was ueber der Nachweistabelle steht
(:data:`~opencivil.bericht.zusammenfassung.ANGABEN`), was gezeichnet wird
(:data:`~opencivil.web.zeichendaten.ZEICHENDATEN`), in der Oberflaeche ihr
Eintrag in arten.js und ihre Zeile in apps.js mit Editor und Karten. Fehlt
eine neue Art dort, meldet es sich -- beim Laden oder in
tests/test_bauteilarten.py; ihre Vorlage im Katalog entsteht von selbst.

WO WAS STEHT:
Hier der Steckbrief, die Liste der Arten und :func:`aufbauen`, das sie
durchgeht. Je Art ein Modul mit ihrer Baufunktion ``bauen``
(:mod:`~opencivil.projekt.aufbau.platte`,
:mod:`~opencivil.projekt.aufbau.querschnittsanalyse`,
:mod:`~opencivil.projekt.aufbau.balkensystem`,
:mod:`~opencivil.projekt.aufbau.balkensystem3d`,
:mod:`~opencivil.projekt.aufbau.decke`,
:mod:`~opencivil.projekt.aufbau.durchstanzen`,
:mod:`~opencivil.projekt.aufbau.grundbruch`,
:mod:`~opencivil.projekt.aufbau.setzung`,
:mod:`~opencivil.projekt.aufbau.pfahl`); was mehr als eine braucht, im
Kern (:mod:`~opencivil.projekt.aufbau.kern`): der Aufbau, das Bauteil, die
Baustoffe, die Stahlspannungen und der Knickfall. Bis 2026-10-17 stand alles
in einer Datei von ueber tausend Zeilen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple

from opencivil.core.rechenwerk import Rechenwerk
from opencivil.projekt.balkensystem import BalkensystemEintrag
from opencivil.projekt.balkensystem3d import Balkensystem3dEintrag
from opencivil.projekt.decke import DeckeEintrag
from opencivil.projekt.durchstanzen import DurchstanzEintrag
from opencivil.projekt.grundbruch import GrundbruchEintrag
from opencivil.projekt.pfahl import PfahlEintrag
from opencivil.projekt.platte import QuerschnittEintrag
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.projekt.setzung import SetzungEintrag

from opencivil.projekt.aufbau import (
    balkensystem, balkensystem3d, decke, durchstanzen, grundbruch, pfahl, platte,
    querschnittsanalyse, setzung,
)
from opencivil.projekt.aufbau.kern import (
    Aufbau, Bauteil, baustoff_bauen, ohne_ort, ueberschreibungen_setzen,
)
from opencivil.projekt.lesen import ProjektFehler, inhalt_pruefen, ort_von

if TYPE_CHECKING:
    from opencivil.projekt.projekt import Projekt

__all__ = [
    "ANALYSE", "Aufbau", "BALKENSYSTEM", "BALKENSYSTEM3D", "BAUTEILE", "Bauteil", "Bauteilart",
    "DECKE", "DURCHSTANZEN",
    "GRUNDBRUCH", "PFAHL", "PLATTE", "SETZUNG", "aufbauen",
]


def aufbauen(projekt: "Projekt", *, schnell: bool = False) -> Aufbau:
    """
    Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

    Wirft :class:`~opencivil.projekt.lesen.ProjektFehler`, wenn die Form
    der Beschreibung nicht stimmt oder was alle teilen -- zwei Materialien
    mit demselben Namen. Was nur ein Material oder ein Bauteil betrifft,
    haelt nur dieses an (:meth:`Aufbau.unfertig`): ein Wert, den der Kern
    abweist, ein Verweis auf ein Material, das es nicht mehr gibt oder das
    selbst nicht rechnet, alles, was beim Bauen eines Bauteils scheitert
    (Benutzer, 2026-11-19: der Rest rechnet weiter).

    Mit ``schnell`` lassen Nachweise teure Nebenrechnungen weg, die das
    Urteil nicht aendern -- die Suche nach der Knickgrenzkraft und die
    genaue Resistenzlinie --, und ganz stille Nachweise entstehen gar
    nicht erst. Gedacht fuer das Bewehrungswerkzeug, das hundertfach
    rechnet und nur wissen muss, ob es aufgeht. Fuer eine Herleitung ist
    das nichts: dort soll die Zahl stehen, die auch in der Tabelle steht.
    """
    projekt.pruefen()
    inhalt_pruefen(projekt, "Projekt", ohne={"materialien", *(art.liste for art in BAUTEILE)})
    werk = Rechenwerk()
    aufbau = Aufbau(werk=werk, schnell=schnell)

    # Nur wenn mehrere Materialien derselben Art vorkommen, braucht es
    # Indizes an den Symbolen -- sonst waere f_{cd,C30/37} bloss Ballast.
    je_art: Dict[str, int] = {}
    for m in projekt.materialien:
        je_art[m.art] = je_art.get(m.art, 0) + 1
    for eintrag in projekt.materialien:
        index = eintrag.anzeigename if je_art[eintrag.art] > 1 else ""
        wo = ort_von(eintrag)
        try:
            inhalt_pruefen(eintrag, wo)
            aufbau.baustoffe[eintrag.kennung] = baustoff_bauen(eintrag, index, wo)
        except ProjektFehler as fehler:
            aufbau.unfertig("materialien", eintrag, wo, ohne_ort(fehler, wo))

    # Auch im schnellen Aufbau jedes Bauteil: die Formelsammlung entsteht aus
    # ihm. Die Bewehrungssuche loest nur Nachweisziele, ein System kostet sie
    # also nur das Anmelden.
    for art in BAUTEILE:
        for eintrag in getattr(projekt, art.liste):
            wo = ort_von(eintrag)
            try:
                _vorab_pruefen(eintrag, wo, aufbau)
                teil = art.bauen(art, eintrag, aufbau)
            except ProjektFehler as fehler:
                aufbau.unfertig(art.liste, eintrag, wo, ohne_ort(fehler, wo))
                continue
            if teil is not None:
                aufbau.teile[eintrag.kennung] = teil

    for baustoff in aufbau.baustoffe.values():
        baustoff.ins_rechenwerk(werk)

    ueberschreibungen_setzen(projekt, werk, aufbau)
    return aufbau


def _vorab_pruefen(eintrag: Any, wo: str, aufbau: Aufbau) -> None:
    """
    Was ein Bauteil aufhaelt, bevor es gebaut wird: ein Material, das selbst
    nicht rechnet, und ein Wert, den der Kern abweist
    (:func:`~opencivil.projekt.lesen.inhalt_pruefen`). Ein Verweis auf ein
    Material, das es nicht mehr gibt, meldet sich beim Bauen, mit dem, was
    darauf zeigt (:func:`~opencivil.projekt.aufbau.kern.material`).

    Bis 2026-11-19 hielt jedes davon das ganze Projekt an -- auch einen
    Verweis ins Leere erreichte die Bedienung: der Beton eines Pfahls, der
    als Mikropfahl keinen braucht und darum loeschen liess.
    """
    for kennung in eintrag.materialien():
        stoff = aufbau.unfertige.get(kennung)
        if stoff is not None:
            raise ProjektFehler(f"{wo}: das Material «{stoff.name}» rechnet nicht – warum, "
                                f"steht bei ihm.")
    inhalt_pruefen(eintrag, wo)


# ===========================================================================
# Die Bauteilarten
# ===========================================================================


@dataclass(frozen=True)
class Bauteilart:
    """
    Der Steckbrief einer Bauteilart: was der Kern ausserhalb ihres Eintrags
    und ihrer Baufunktion von ihr wissen muss. Eine neue Art kommt in
    :data:`BAUTEILE` dazu -- und in die Verzeichnisse von Bericht und
    Oberflaeche, siehe Dateikopf.
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
#: Die Kennungen u1, u2 ...: «r» tragen die Rahmen in der Ebene.
BALKENSYSTEM3D = Bauteilart("balkensystem3d", "balkensysteme3d", Balkensystem3dEintrag, "u",
                            "balkensystem3d", "3D-Balkensysteme", balkensystem3d.bauen)
#: Die Kennungen e1, e2 ...: «d» tragen schon die Durchstanzstellen.
DECKE = Bauteilart("decke", "decken", DeckeEintrag, "e", "decke", "Decken", decke.bauen)
GRUNDBRUCH = Bauteilart("grundbruch", "grundbrueche", GrundbruchEintrag, "g",
                        "grundbruch", "Grundbruch", grundbruch.bauen)
#: Die Kennungen w1, w2 ...: «s» tragen schon die Betonstaehle.
SETZUNG = Bauteilart("setzung", "setzungen", SetzungEintrag, "w", "setzung", "Setzung",
                     setzung.bauen)
DURCHSTANZEN = Bauteilart("durchstanzen", "durchstanzstellen", DurchstanzEintrag, "d",
                          "durchstanzen", "Durchstanzen", durchstanzen.bauen)
#: Die Kennungen t1, t2 ...: «p» tragen schon die Skripte.
PFAHL = Bauteilart("pfahl", "pfaehle", PfahlEintrag, "t", "pfahl", "Pfähle", pfahl.bauen)

#: Die Bauteilarten, in der Reihenfolge von Baum, Bericht und Rechnung -- ein
#: Balkensystem liest Werte der Platten und Analysen, also kommt es nach
#: ihnen; Decke, Durchstanzen, Grundbruch, Setzung und Pfahl lesen nichts von
#: den anderen.
#: Wer alle Bauteile durchgeht (Lesen, Kennungen, Aufbau, Zwischenspeicher,
#: Erkennen einer Datei), geht diese Liste durch.
BAUTEILE: Tuple[Bauteilart, ...] = (PLATTE, ANALYSE, BALKENSYSTEM, BALKENSYSTEM3D, DECKE,
                                     DURCHSTANZEN, GRUNDBRUCH, SETZUNG, PFAHL)
