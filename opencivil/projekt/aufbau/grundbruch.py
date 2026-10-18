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
from opencivil.projekt.lesen import als_groesse
from opencivil.geotechnik.grundbruch import Fundament, Gleiten, Grundbruch, Kombination

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: GrundbruchEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Fundament und seine beiden Nachweise -- Grundbruch und Gleiten --,
    sobald eine Kombination eingeschaltet ist. Ohne sie steht das Fundament
    allein da, wie eine Platte ohne Einwirkung.

    Jede Zahl in der Einheit ihres Feldes (:func:`~opencivil.projekt.lesen.als_groesse`)
    -- bis 2026-10-18 stand sie hier ein zweites Mal.
    """
    g = partial(als_groesse, eintrag)
    fundament = Fundament(
        name=eintrag.name,
        phi_k=g("phi_k"), gamma_phi=g("gamma_phi"), c_k=g("c_k"), gamma_c=g("gamma_c"),
        gamma=g("gamma"), gamma_w=g("gamma_w"), q_Ed=g("q_Ed"), b=g("b"), L=g("L"),
        t1=g("t1"), t=g("t"), alpha=g("alpha"), beta=g("beta"),
        delta_faktor=g("delta_faktor"),
        praefix=f"{art.raum}.{eintrag.kennung}")
    aufbau.grundbrueche[eintrag.kennung] = fundament
    fundament.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag.kennung, eintrag.name, art, fundament)
    kombinationen = [Kombination(name=k.name, N_Ed=als_groesse(k, "N_Ed"),
                                 T_Ed=als_groesse(k, "T_Ed"))
                     for k in eintrag.kombinationen if k.aktiv]
    if kombinationen:
        aufbau.eintragen(teil, "grundbruch", eintrag.kennung, Grundbruch(fundament, kombinationen))
        aufbau.eintragen(teil, "gleiten", eintrag.kennung, Gleiten(fundament, kombinationen))
    else:
        aufbau.warnungen.append(
            f"Grundbruch '{eintrag.name}': keine Kombination → kein Nachweis.")
    return teil
