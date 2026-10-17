"""
opencivil/projekt/aufbau/balkensystem.py -- ein Balkensystem wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.balkensystem.BalkensystemEintrag` das
Stabwerk mit aufgeloesten Querschnitten (:func:`bauen`). Ein Querschnitt kann
eine Platte oder eine Querschnittsanalyse des Projekts nehmen; die muessen
dann schon gebaut sein -- darum kommt das Balkensystem in
:data:`~opencivil.projekt.aufbau.BAUTEILE` nach ihnen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from opencivil.material.basis import Baustoff
from opencivil.projekt.balkensystem import BalkensystemEintrag, StabquerschnittEintrag
from opencivil.projekt.lesen import ProjektFehler
from opencivil.stabwerk.rechnung import Balkensystem, Stabquerschnitt

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: BalkensystemEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Balkensystem: das Stabwerk der Beschreibung, seine Querschnitte
    aufgeloest. Hart scheitert nur ein Verweis, den es nicht gibt -- ein
    Material, eine Platte, eine Querschnittsanalyse --; was dem System selbst
    fehlt, steht in seinen Meldungen, und der Rest des Projekts rechnet.
    """
    wo = f"Balkensystem '{eintrag.name}'"
    modell = eintrag.modell()
    stoffe: Dict[str, Baustoff] = {}
    for _, material in modell.paare.values():
        stoff = aufbau.baustoffe.get(material)
        if stoff is None:
            raise ProjektFehler(f"{wo}: das Material '{material}' gibt es im Projekt nicht.")
        stoffe[material] = stoff
    system = Balkensystem(
        name=eintrag.name, kennung=eintrag.kennung, praefix=f"{art.raum}.{eintrag.kennung}",
        system=modell.system, paare=modell.paare, meldungen=modell.meldungen,
        querschnitte=[_stabquerschnitt(q, aufbau, wo) for q in eintrag.querschnitte],
        stoffe=stoffe)
    aufbau.balkensysteme[eintrag.kennung] = system
    system.ins_rechenwerk(aufbau.werk)
    return Bauteil(eintrag.kennung, eintrag.name, art, system,
                   weitere_ziele=system.ziele(), bezuege=tuple(system.bezuege))


def _stabquerschnitt(q: StabquerschnittEintrag, aufbau: Aufbau, wo: str) -> Stabquerschnitt:
    """Woher A und I eines Querschnitts kommen -- die Platte oder Analyse dazu muss es geben."""
    if q.art == "vorlage":
        vorlage = q.stabvorlage()
        return Stabquerschnitt(q.kennung, q.name, q.art, vorlage=vorlage,
                               masse=q.masse_mit_vorgaben(), herkunft=vorlage.name,
                               fehler=q.fehler() or "")
    if q.art == "kennwerte":
        return Stabquerschnitt(q.kennung, q.name, q.art, masse=dict(q.masse),
                               herkunft="von Hand", fehler=q.fehler() or "")
    if q.art == "platte":
        platte = aufbau.querschnitte.get(q.bezug)
        if platte is None:
            raise ProjektFehler(f"{wo}: der Querschnitt «{q.name}» nimmt die Platte "
                                f"'{q.bezug}', die es im Projekt nicht gibt.")
        return Stabquerschnitt(q.kennung, q.name, q.art, bezug=q.bezug,
                               quelle={"b": platte.id_von("b"), "h": platte.id_von("h")},
                               herkunft=f"Platte «{platte.name}»")
    analyse = aufbau.querschnittsanalysen.get(q.bezug)
    if analyse is None:
        raise ProjektFehler(f"{wo}: der Querschnitt «{q.name}» nimmt die Querschnittsanalyse "
                            f"'{q.bezug}', die es im Projekt nicht gibt.")
    return Stabquerschnitt(q.kennung, q.name, q.art, bezug=q.bezug,
                           quelle={"A": analyse.id_von("A"), "I": analyse.id_von("I_y")},
                           herkunft=f"Querschnittsanalyse «{analyse.name}»")
