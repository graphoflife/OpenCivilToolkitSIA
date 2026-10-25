"""
opencivil/projekt/aufbau/balkensystem.py -- ein Balkensystem wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.balkensystem.BalkensystemEintrag` das
Stabwerk mit aufgeloesten Materialien und Querschnitten (:func:`bauen`). Ein
Material ist ein Beton des Projekts oder ein eigenes. Die Art eines
Querschnitts wird hier aufgeloest, einmal: je Art eine Klasse
(:mod:`~opencivil.stabwerk.stabquerschnitt`). Ein Querschnitt kann eine
Platte oder eine Querschnittsanalyse des Projekts nehmen; die muessen dann
schon gebaut sein -- darum kommt das Balkensystem in
:data:`~opencivil.projekt.aufbau.BAUTEILE` nach ihnen. Von dort kommt auch
das Material einer Linie «gemäss Querschnitt»: der Beton der Platte oder
der Analyse.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from opencivil.material.basis import Baustoff
from opencivil.projekt.balkensystem import (
    MATERIAL_DES_QUERSCHNITTS, BalkensystemEintrag, Modell, Querschnittsart, StabmaterialEintrag,
    StabquerschnittEintrag,
)
from opencivil.projekt.lesen import ProjektFehler
from opencivil.spannungsanalyse.modul import ModulAusAnalyse, ModulAusPlatte, Modulfrage
from opencivil.stabwerk.rechnung import Balkensystem, Stabmaterial
from opencivil.stabwerk.stabquerschnitt import (
    AusAnalyse, AusPlatte, NachVorlage, Stabquerschnitt, VonHand,
)
from opencivil.stabwerk.system import Meldung

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: BalkensystemEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Balkensystem: das Stabwerk der Beschreibung, seine Materialien und
    Querschnitte aufgeloest. Hart scheitert nur ein Verweis, den es nicht
    gibt -- ein Beton, eine Platte, eine Querschnittsanalyse --; was dem
    System selbst fehlt, steht in seinen Meldungen, und der Rest des
    Projekts rechnet.
    """
    wo = f"Balkensystem '{eintrag.name}'"
    modell = eintrag.modell()
    querschnitte = [_stabquerschnitt(q, aufbau, wo) for q in eintrag.querschnitte]
    paare, meldungen = _paare(eintrag, modell, aufbau, wo)
    system = Balkensystem(
        name=eintrag.name, kennung=eintrag.kennung, praefix=f"{art.raum}.{eintrag.kennung}",
        system=modell.system, paare=paare, meldungen=meldungen, querschnitte=querschnitte,
        eigengewicht=modell.eigengewicht)
    system.ins_rechenwerk(aufbau.werk)
    return Bauteil(eintrag.kennung, eintrag.name, art, system,
                   weitere_ziele=system.ziele(), bezuege=tuple(system.bezuege))


def _stabquerschnitt(q: StabquerschnittEintrag, aufbau: Aufbau, wo: str) -> Stabquerschnitt:
    """
    Woher A und I eines Querschnitts kommen -- hier wird seine Art
    aufgeloest. Die Platte oder Analyse dazu muss es geben.
    """
    if q.art is Querschnittsart.VORLAGE:
        vorlage = q.stabvorlage()
        return NachVorlage(kennung=q.kennung, name=q.name, herkunft=vorlage.name,
                           fehler=q.fehler() or "", vorlage=vorlage,
                           masse=q.masse_mit_vorgaben())
    if q.art is Querschnittsart.KENNWERTE:
        return VonHand(kennung=q.kennung, name=q.name, herkunft="von Hand",
                       fehler=q.fehler() or "", masse=dict(q.masse))
    if q.art is Querschnittsart.PLATTE:
        platte = aufbau.querschnitte.get(q.bezug)
        if platte is None:
            raise ProjektFehler(f"{wo}: der Querschnitt «{q.name}» nimmt die Platte "
                                f"'{q.bezug}', die es im Projekt nicht gibt.")
        return AusPlatte(kennung=q.kennung, name=q.name, herkunft=f"Platte «{platte.name}»",
                         bezug=q.bezug,
                         quelle={"b": platte.id_von("b"), "h": platte.id_von("h")},
                         eq=_modulfrage(q, ModulAusPlatte(platte)))
    analyse = aufbau.querschnittsanalysen.get(q.bezug)
    if analyse is None and q.bezug in aufbau.leere_analysen:
        # Eine leere Analyse gibt es, nur traegt sie noch nichts: der Stab
        # rechnet nicht, das Projekt schon.
        name = aufbau.leere_analysen[q.bezug]
        return AusAnalyse(kennung=q.kennung, name=q.name,
                          herkunft=f"Querschnittsanalyse «{name}»", bezug=q.bezug,
                          fehler=f"Die Querschnittsanalyse «{name}» ist noch leer.")
    if analyse is None:
        raise ProjektFehler(f"{wo}: der Querschnitt «{q.name}» nimmt die Querschnittsanalyse "
                            f"'{q.bezug}', die es im Projekt nicht gibt.")
    return AusAnalyse(kennung=q.kennung, name=q.name,
                      herkunft=f"Querschnittsanalyse «{analyse.name}»", bezug=q.bezug,
                      quelle={"A": analyse.id_von("A"), "I": analyse.id_von("I_y")},
                      eq=_modulfrage(q, ModulAusAnalyse(analyse)),
                      flaechen=tuple(f.punkte for f in analyse.flaechen))


def _modulfrage(q: StabquerschnittEintrag, quelle) -> Optional[Modulfrage]:
    """Die Frage nach dem E_eq eines Querschnitts -- nur, wenn er es nehmen soll."""
    return Modulfrage(quelle, q.eq.N, q.eq.M, q.eq.wahl) if q.e_modul == "e_eq" else None


def _paare(eintrag: BalkensystemEintrag, modell: Modell, aufbau: Aufbau,
           wo: str) -> Tuple[Dict[str, Tuple[str, Stabmaterial]], List[Meldung]]:
    """
    Je tragenden Stab sein Querschnitt und sein Material, aufgeloest --
    «gemäss Querschnitt» wird zum Beton der Platte oder Analyse. Traegt das
    Material nicht, sagt es eine Meldung, und das System rechnet nicht.
    """
    querschnitte = {q.kennung: q for q in eintrag.querschnitte}
    materialien = {m.kennung: m for m in eintrag.stabmaterialien}
    paare: Dict[str, Tuple[str, Stabmaterial]] = {}
    meldungen = list(modell.meldungen)
    for stab, (q, kennung) in modell.paare.items():
        if kennung == MATERIAL_DES_QUERSCHNITTS:
            material, grund = _material_des_querschnitts(querschnitte[q], aufbau)
            if grund:
                grund = f"{stab} nimmt das Material gemäss Querschnitt, aber {grund}"
        else:
            material, grund = _stabmaterial(materialien[kennung], aufbau, wo)
            if grund:
                grund = f"{stab} nimmt das Material {kennung}, aber {grund}"
        if material is None:
            meldungen.append(Meldung(grund, (stab, q, kennung), True))
            continue
        paare[stab] = (q, material)
    return paare, meldungen


def _beton(kennung: str, aufbau: Aufbau, wo: str) -> Baustoff:
    """Ein Beton des Projekts -- einen Verweis ins Leere gibt es nicht."""
    stoff = aufbau.baustoffe.get(kennung)
    if stoff is None:
        raise ProjektFehler(f"{wo}: das Material '{kennung}' gibt es im Projekt nicht.")
    return stoff


def _stabmaterial(m: StabmaterialEintrag, aufbau: Aufbau,
                  wo: str) -> Tuple[Optional[Stabmaterial], str]:
    """
    Ein Material des Systems, aufgeloest: ein Beton des Projekts oder ein
    eigenes. Traegt es nicht, ist es ``None``, und der zweite Teil sagt
    warum -- klein beginnend, er folgt auf ein «aber».
    """
    if m.art == "eigen":
        return Stabmaterial(m.kennung, m.name or m.kennung, E=m.E, rho=m.rho), ""
    if not m.beton:
        return None, "bei ihm ist kein Beton gewählt."
    stoff = _beton(m.beton, aufbau, wo)
    if stoff.art.value != "beton":
        return None, (f"«{stoff.name}» ist kein Beton – ein Material des Systems ist ein "
                      f"Beton des Projekts oder ein eigenes.")
    return Stabmaterial(m.kennung, stoff.name, stoff=stoff), ""


def _material_des_querschnitts(q: StabquerschnittEintrag,
                               aufbau: Aufbau) -> Tuple[Optional[Stabmaterial], str]:
    """
    Das Material, das ein Querschnitt mitbringt: der Beton einer Platte, das
    eine Material der Flaechen einer Analyse. Sonst ``None``, und der zweite
    Teil sagt, warum.
    """
    if not q.art.aus_bauteil:
        return None, (f"«{q.name}» ist "
                      f"{'nach Vorlage' if q.art is Querschnittsart.VORLAGE else 'von Hand'} und "
                      f"bringt keines mit – das tut nur eine Platte oder Querschnittsanalyse.")
    if q.art is Querschnittsart.PLATTE:
        platte = aufbau.querschnitte.get(q.bezug)
        stoffe = [platte.beton] if platte is not None else []
    else:
        analyse = aufbau.querschnittsanalysen.get(q.bezug)
        if analyse is None:
            return None, f"die Querschnittsanalyse von «{q.name}» ist noch leer."
        stoffe = list({id(f.stoff): f.stoff for f in analyse.flaechen if f.stoff is not None}.values())
        if len(stoffe) > 1:
            return None, (f"die Flächen von «{q.name}» sind aus "
                          f"{' und '.join(s.name for s in stoffe)} – das Material von Hand wählen.")
    if not stoffe:
        return None, f"«{q.name}» bringt keines mit."
    return Stabmaterial(MATERIAL_DES_QUERSCHNITTS, stoffe[0].name, stoff=stoffe[0],
                        vom_querschnitt=True), ""
