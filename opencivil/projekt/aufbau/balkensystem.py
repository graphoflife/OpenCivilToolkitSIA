"""
opencivil/projekt/aufbau/balkensystem.py -- ein Balkensystem wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.balkensystem.BalkensystemEintrag` das
Stabwerk mit aufgeloesten Querschnitten (:func:`bauen`). Ein Querschnitt kann
eine Platte oder eine Querschnittsanalyse des Projekts nehmen; die muessen
dann schon gebaut sein -- darum kommt das Balkensystem in
:data:`~opencivil.projekt.aufbau.BAUTEILE` nach ihnen. Von dort kommt auch
das Material einer Linie «gemäss Querschnitt»: der Beton der Platte oder
der Analyse.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Dict, List, Tuple

from opencivil.material.basis import Baustoff
from opencivil.projekt.balkensystem import (
    MATERIAL_DES_QUERSCHNITTS, MIT_MATERIAL, BalkensystemEintrag, Modell, StabquerschnittEintrag,
)
from opencivil.projekt.lesen import ProjektFehler
from opencivil.stabwerk.rechnung import Balkensystem, Stabquerschnitt
from opencivil.stabwerk.system import Meldung

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
    querschnitte = [replace(_stabquerschnitt(q, aufbau, wo), E=q.E_von_hand)
                    for q in eintrag.querschnitte]
    paare, meldungen = _paare(eintrag, modell, aufbau)
    stoffe: Dict[str, Baustoff] = {}
    for _, material in paare.values():
        stoff = aufbau.baustoffe.get(material)
        if stoff is None:
            raise ProjektFehler(f"{wo}: das Material '{material}' gibt es im Projekt nicht.")
        stoffe[material] = stoff
    system = Balkensystem(
        name=eintrag.name, kennung=eintrag.kennung, praefix=f"{art.raum}.{eintrag.kennung}",
        system=modell.system, paare=paare, meldungen=meldungen, querschnitte=querschnitte,
        stoffe=stoffe, eigengewicht=modell.eigengewicht)
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
    if analyse is None and q.bezug in aufbau.leere_analysen:
        # Eine leere Analyse gibt es, nur traegt sie noch nichts: der Stab
        # rechnet nicht, das Projekt schon.
        name = aufbau.leere_analysen[q.bezug]
        return Stabquerschnitt(q.kennung, q.name, q.art, bezug=q.bezug,
                               herkunft=f"Querschnittsanalyse «{name}»",
                               fehler=f"Die Querschnittsanalyse «{name}» ist noch leer.")
    if analyse is None:
        raise ProjektFehler(f"{wo}: der Querschnitt «{q.name}» nimmt die Querschnittsanalyse "
                            f"'{q.bezug}', die es im Projekt nicht gibt.")
    return Stabquerschnitt(q.kennung, q.name, q.art, bezug=q.bezug,
                           quelle={"A": analyse.id_von("A"), "I": analyse.id_von("I_y")},
                           herkunft=f"Querschnittsanalyse «{analyse.name}»")


def _paare(eintrag: BalkensystemEintrag, modell: Modell,
           aufbau: Aufbau) -> Tuple[Dict[str, Tuple[str, str]], List[Meldung]]:
    """
    Je tragenden Stab Querschnitt und Material -- «gemäss Querschnitt» wird
    zum Material der Platte oder Analyse. Bringt der Querschnitt keines mit,
    sagt es eine Meldung, und das System rechnet nicht.
    """
    querschnitte = {q.kennung: q for q in eintrag.querschnitte}
    paare: Dict[str, Tuple[str, str]] = {}
    meldungen = list(modell.meldungen)
    for stab, (q, material) in modell.paare.items():
        if material == MATERIAL_DES_QUERSCHNITTS:
            material, grund = _material_des_querschnitts(querschnitte[q], aufbau)
            if grund:
                meldungen.append(Meldung(f"{stab} nimmt das Material gemäss Querschnitt, aber {grund}",
                                         (stab, q), True))
                continue
        paare[stab] = (q, material)
    return paare, meldungen


def _material_des_querschnitts(q: StabquerschnittEintrag, aufbau: Aufbau) -> Tuple[str, str]:
    """
    Die Kennung des Materials, das ein Querschnitt mitbringt: der Beton einer
    Platte, das eine Material der Flaechen einer Analyse. Sonst leer, und
    der zweite Teil sagt, warum.
    """
    if q.art not in MIT_MATERIAL:
        return "", (f"«{q.name}» ist {'nach Vorlage' if q.art == 'vorlage' else 'von Hand'} und "
                    f"bringt keines mit -- das tut nur eine Platte oder Querschnittsanalyse.")
    if q.art == "platte":
        platte = aufbau.querschnitte.get(q.bezug)
        stoffe = [platte.beton] if platte is not None else []
    else:
        analyse = aufbau.querschnittsanalysen.get(q.bezug)
        if analyse is None:
            return "", f"die Querschnittsanalyse von «{q.name}» ist noch leer."
        stoffe = list({id(f.stoff): f.stoff for f in analyse.flaechen if f.stoff is not None}.values())
        if len(stoffe) > 1:
            return "", (f"die Flächen von «{q.name}» sind aus "
                        f"{' und '.join(s.name for s in stoffe)} -- das Material von Hand wählen.")
    if not stoffe:
        return "", f"«{q.name}» bringt keines mit."
    return next(k for k, s in aufbau.baustoffe.items() if s is stoffe[0]), ""
