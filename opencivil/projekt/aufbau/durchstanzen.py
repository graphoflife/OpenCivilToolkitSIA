"""
opencivil/projekt/aufbau/durchstanzen.py -- eine Durchstanzstelle wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.durchstanzen.DurchstanzEintrag` die
Durchstanzstelle mit ihren Vorgaben und ihr Nachweis (:func:`bauen`). Hier
werden Aussparungen und Plattenbereiche aus ihren Knoten gelesen und
geprüft: jedes braucht drei Ecken und darf sich nicht selbst schneiden.
Plattenbereiche dürfen ineinander liegen, sich aber nicht teilweise
überdecken, und die Stütze liegt ganz in einem Bereich oder ganz neben ihm.
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Dict, List, Tuple

from opencivil.durchstanzen.bereiche import Plattenbereich
from opencivil.durchstanzen.flaeche import GestuetzteFlaeche, Masse
from opencivil.durchstanzen.kennzahl import Durchstanzkennzahl
from opencivil.durchstanzen.nachweis import Durchstanzen
from opencivil.durchstanzen.stelle import Durchstanzstelle
from opencivil.projekt.durchstanzen import DurchstanzEintrag
from opencivil.projekt.lesen import ProjektFehler, als_groesse, ort_von
from opencivil.querschnitt.geometrie import (
    Beziehung, GeometrieFehler, beziehung, polygon_pruefen, verschachteln,
)

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil, material

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart

#: mm in m.
MM = 1e-3


def _ecken(eintrag: DurchstanzEintrag, knoten: List[str], name: str) -> List[Tuple[float, float]]:
    """Die Ecken eines Polygons in m -- geprüft, sonst ein Satz, was nicht stimmt."""
    lage: Dict[str, Tuple[float, float]] = {k.kennung: (k.x * MM, k.y * MM) for k in eintrag.knoten}
    wo = ort_von(eintrag)
    fehlt = [k for k in knoten if k not in lage]
    if fehlt:
        raise ProjektFehler(f"{name}: die Knoten {', '.join(fehlt)} gibt es nicht.", wo=wo)
    punkte = [lage[k] for k in knoten]
    try:
        polygon_pruefen(punkte, name)
    except GeometrieFehler as fehler:
        raise ProjektFehler(str(fehler), wo=wo) from None
    return punkte


def aussparungen(eintrag: DurchstanzEintrag) -> List[List[Tuple[float, float]]]:
    """Die Aussparungen als Ecken in m."""
    return [_ecken(eintrag, a.knoten, f"Aussparung {a.kennung}") for a in eintrag.aussparungen]


def bereiche(eintrag: DurchstanzEintrag, flaeche: GestuetzteFlaeche,
             masse: Masse) -> List[Plattenbereich]:
    """
    Die Plattenbereiche mit ihren Ecken und ihrer Dicke in m -- geprüft wie
    im Dateikopf. An einer Wand prüft es nur die Bereiche selbst: dort
    rechnet der Nachweis sie noch nicht.
    """
    wo = ort_von(eintrag)
    ergebnis = [Plattenbereich(b.kennung, tuple(_ecken(eintrag, b.knoten, f"Bereich {b.kennung}")),
                               b.h * MM, b.seite) for b in eintrag.plattenbereiche]
    try:
        verschachteln([b.ecken for b in ergebnis], [b.titel for b in ergebnis])
    except GeometrieFehler as fehler:
        raise ProjektFehler(str(fehler), wo=wo) from None
    if flaeche.hat_form:
        umriss = flaeche.umriss(masse, 0.0)
        for b in ergebnis:
            if beziehung(umriss, b.ecken) not in (Beziehung.ERSTES_IM_ZWEITEN, Beziehung.GETRENNT):
                raise ProjektFehler(f"{b.titel} schneidet die Stütze: ein Bereich umschliesst sie "
                                    f"ganz oder liegt neben ihr.", wo=wo)
    return ergebnis


def bauen(art: "Bauteilart", eintrag: DurchstanzEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Eine Durchstanzstelle und ihr Nachweis. Jede Zahl in der Einheit ihres
    Feldes (:func:`~opencivil.projekt.lesen.als_groesse`).
    """
    g = partial(als_groesse, eintrag)
    wo = ort_von(eintrag)
    flaeche = eintrag.lage.flaeche(eintrag.form)
    masse = {k: g(k).si for k in flaeche.masse}
    stelle = Durchstanzstelle(
        name=eintrag.name, praefix=f"{art.raum}.{eintrag.kennung}",
        plattenart=eintrag.plattenart, system=eintrag.system,
        beton=material(aufbau.baustoffe, eintrag.beton, "beton", wo, "Beton"),
        stahl=material(aufbau.baustoffe, eintrag.stahl, "betonstahl", wo, "Betonstahl"),
        h=g("h"), c=g("c"), c_v=g("c_v"), D_max=g("D_max"),
        phi_x=g("phi_x"), s_x=g("s_x"), phi_y=g("phi_y"), s_y=g("s_y"), aussen=eintrag.aussen,
        flaeche=flaeche, b_x=g("b_x"), b_y=g("b_y"), D=g("D"), t=g("t"),
        a_x=g("a_x"), a_y=g("a_y"), l_x=g("l_x"), l_y=g("l_y"), stufe=eintrag.stufe,
        r_sx=g("r_sx"), r_sy=g("r_sy"), m_sdx=g("m_sdx"), m_sdy=g("m_sdy"),
        V_d=g("V_d"), q_d=g("q_d"), ke=eintrag.ke, e_x=g("e_x"), e_y=g("e_y"),
        aussparungen=aussparungen(eintrag), bereiche=bereiche(eintrag, flaeche, masse))
    stelle.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag, art, stelle)
    aufbau.eintragen(teil, "durchstanzen", eintrag.kennung, Durchstanzen(stelle))
    # Der Widerstand am Schnittpunkt, auch ohne Einwirkung (Benutzer, 2026-11-27).
    aufbau.kennzahlen_eintragen(teil, Durchstanzkennzahl(stelle))
    return teil
