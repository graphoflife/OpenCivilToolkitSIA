"""
opencivil/projekt/aufbau/grundbruch.py -- ein Fundament wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.grundbruch.GrundbruchEintrag` das
Fundament und seine beiden Nachweise, Grundbruch und Gleiten (:func:`bauen`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from functools import partial

from opencivil.projekt.grundbruch import GrundbruchEintrag
from opencivil.projekt.lesen import als_groesse, ort_von
from opencivil.geotechnik.fundament import Fundament, Kombination
from opencivil.geotechnik.gleiten import Gleiten
from opencivil.geotechnik.grundbruch import Grundbruch

from opencivil.projekt.aufbau.kern import (
    Aufbau, Bauteil, material, ohne_kombination, schwerer_als_wasser,
)

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: GrundbruchEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Fundament und seine beiden Nachweise -- Grundbruch und Gleiten --,
    sobald eine Kombination eingeschaltet ist. Ohne sie steht das Fundament
    allein da, wie eine Platte ohne Einwirkung.

    Jede Zahl in der Einheit ihres Feldes (:func:`~opencivil.projekt.lesen.als_groesse`)
    -- bis 2026-10-18 stand sie hier ein zweites Mal. Das Wasser nur
    drainiert: undrainiert wirkt es nicht.
    """
    g = partial(als_groesse, eintrag)
    wasser = None
    if eintrag.drainiert:
        wo = ort_von(eintrag)
        wasser = material(aufbau.baustoffe, eintrag.wasser, "fluessigkeit", wo, "Wasser")
        schwerer_als_wasser(eintrag.gamma, wasser, aufbau, wo)
    fundament = Fundament(
        name=eintrag.name, verhalten=eintrag.verhalten,
        phi_k=g("phi_k"), gamma_phi=g("gamma_phi"), c_k=g("c_k"), gamma_c=g("gamma_c"),
        s_u=g("s_u"), gamma_cu=g("gamma_cu"),
        gamma=g("gamma"), wasser=wasser, q_Ed=g("q_Ed"), b=g("b"), L=g("L"),
        t1=g("t1"), t=g("t"), alpha=g("alpha"), beta=g("beta"),
        delta_faktor=g("delta_faktor"),
        praefix=f"{art.raum}.{eintrag.kennung}")
    fundament.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag, art, fundament)
    kombinationen = [Kombination(name=k.name, N_Ed=als_groesse(k, "N_Ed"),
                                 T_Ed=als_groesse(k, "T_Ed"))
                     for k in eintrag.kombinationen if k.aktiv]
    if kombinationen:
        aufbau.eintragen(teil, "grundbruch", eintrag.kennung, Grundbruch(fundament, kombinationen))
        aufbau.eintragen(teil, "gleiten", eintrag.kennung, Gleiten(fundament, kombinationen))
    else:
        aufbau.ohne_nachweis(teil, f"Grundbruch '{eintrag.name}'", ohne_kombination(eintrag.kombinationen))
    return teil
