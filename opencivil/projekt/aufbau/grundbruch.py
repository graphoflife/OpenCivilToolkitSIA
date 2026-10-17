"""
opencivil/projekt/aufbau/grundbruch.py -- ein Fundament wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.grundbruch.GrundbruchEintrag` das
Fundament und seine beiden Nachweise, Grundbruch und Gleiten (:func:`bauen`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from opencivil.core.einheiten import EINHEITSLOS, GRAD, KN, KN_PRO_M3, KPA, M, Groesse
from opencivil.projekt.grundbruch import GrundbruchEintrag
from opencivil.geotechnik.grundbruch import Fundament, Gleiten, Grundbruch, Kombination

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: GrundbruchEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Fundament und seine beiden Nachweise -- Grundbruch und Gleiten --,
    sobald eine Kombination eingeschaltet ist. Ohne sie steht das Fundament
    allein da, wie eine Platte ohne Einwirkung.
    """
    fundament = Fundament(
        name=eintrag.name,
        phi_k=Groesse(eintrag.phi_k, GRAD), gamma_phi=Groesse(eintrag.gamma_phi, EINHEITSLOS),
        c_k=Groesse(eintrag.c_k, KPA), gamma_c=Groesse(eintrag.gamma_c, EINHEITSLOS),
        gamma=Groesse(eintrag.gamma, KN_PRO_M3), gamma_w=Groesse(eintrag.gamma_w, KN_PRO_M3),
        q_Ed=Groesse(eintrag.q_Ed, KPA), b=Groesse(eintrag.b, M), L=Groesse(eintrag.L, M),
        t1=Groesse(eintrag.t1, M), t=Groesse(eintrag.t, M),
        alpha=Groesse(eintrag.alpha, GRAD), beta=Groesse(eintrag.beta, GRAD),
        delta_faktor=Groesse(eintrag.delta_faktor, EINHEITSLOS),
        praefix=f"{art.raum}.{eintrag.kennung}")
    aufbau.grundbrueche[eintrag.kennung] = fundament
    fundament.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag.kennung, eintrag.name, art, fundament)
    kombinationen = [Kombination(name=k.name, N_Ed=Groesse(k.N_Ed, KN), T_Ed=Groesse(k.T_Ed, KN))
                     for k in eintrag.kombinationen if k.aktiv]
    if kombinationen:
        aufbau.eintragen(teil, "grundbruch", eintrag.kennung, Grundbruch(fundament, kombinationen))
        aufbau.eintragen(teil, "gleiten", eintrag.kennung, Gleiten(fundament, kombinationen))
    else:
        aufbau.warnungen.append(
            f"Grundbruch '{eintrag.name}': keine Kombination → kein Nachweis.")
    return teil
