"""
opencivil/projekt/aufbau/durchstanzen.py -- eine Durchstanzstelle wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.durchstanzen.DurchstanzEintrag` die
Durchstanzstelle mit ihren Vorgaben und ihr Nachweis (:func:`bauen`). Hier
werden die Aussparungen aus ihren Knoten gelesen und geprüft: eine
Aussparung braucht drei Ecken, darf sich nicht selbst schneiden und nicht
über die gestützte Fläche reichen.
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Dict, List, Tuple

from opencivil.durchstanzen.nachweis import Durchstanzen
from opencivil.durchstanzen.stelle import Durchstanzstelle
from opencivil.projekt.durchstanzen import DurchstanzEintrag
from opencivil.projekt.lesen import ProjektFehler, als_groesse
from opencivil.querschnitt.geometrie import GeometrieFehler, polygon_pruefen

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil, material

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart

#: mm in m.
MM = 1e-3


def aussparungen(eintrag: DurchstanzEintrag) -> List[List[Tuple[float, float]]]:
    """Die Aussparungen als Ecken in m -- geprüft, sonst ein Satz, was nicht stimmt."""
    lage: Dict[str, Tuple[float, float]] = {k.kennung: (k.x * MM, k.y * MM) for k in eintrag.knoten}
    ergebnis = []
    for a in eintrag.aussparungen:
        wo = f"Durchstanzen '{eintrag.name}', Aussparung {a.kennung}"
        fehlt = [k for k in a.knoten if k not in lage]
        if fehlt:
            raise ProjektFehler(f"{wo}: die Knoten {', '.join(fehlt)} gibt es nicht.")
        punkte = [lage[k] for k in a.knoten]
        try:
            polygon_pruefen(punkte, wo)
        except GeometrieFehler as fehler:
            raise ProjektFehler(str(fehler)) from None
        ergebnis.append(punkte)
    return ergebnis


def bauen(art: "Bauteilart", eintrag: DurchstanzEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Eine Durchstanzstelle und ihr Nachweis. Jede Zahl in der Einheit ihres
    Feldes (:func:`~opencivil.projekt.lesen.als_groesse`).
    """
    g = partial(als_groesse, eintrag)
    wo = f"Durchstanzen '{eintrag.name}'"
    stelle = Durchstanzstelle(
        name=eintrag.name, praefix=f"{art.raum}.{eintrag.kennung}",
        plattenart=eintrag.plattenart,
        beton=material(aufbau.baustoffe, eintrag.beton, "beton", wo),
        stahl=material(aufbau.baustoffe, eintrag.stahl, "betonstahl", wo),
        h=g("h"), c=g("c"), c_v=g("c_v"), D_max=g("D_max"),
        phi_x=g("phi_x"), s_x=g("s_x"), phi_y=g("phi_y"), s_y=g("s_y"), aussen=eintrag.aussen,
        form=eintrag.form, lage=eintrag.lage, b_x=g("b_x"), b_y=g("b_y"), D=g("D"), t=g("t"),
        a_x=g("a_x"), a_y=g("a_y"), l_x=g("l_x"), l_y=g("l_y"), stufe=eintrag.stufe,
        r_sx=g("r_sx"), r_sy=g("r_sy"), m_sdx=g("m_sdx"), m_sdy=g("m_sdy"),
        V_d=g("V_d"), q_d=g("q_d"), ke=eintrag.ke, e_x=g("e_x"), e_y=g("e_y"),
        aussparungen=aussparungen(eintrag))
    stelle.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag.kennung, eintrag.name, art, stelle)
    aufbau.eintragen(teil, "durchstanzen", eintrag.kennung, Durchstanzen(stelle))
    return teil
