"""
opencivil/projekt/aufbau/pfahl.py -- ein Pfahl wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.pfahl.PfahlEintrag` der Pfahl, seine
beiden Nachweise längs der Achse, äusserer und innerer Widerstand, und seine
Steifigkeit (:func:`bauen`).
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from opencivil.pfahl.aussen import AeussererWiderstand
from opencivil.pfahl.boden import Pfahlschicht
from opencivil.pfahl.innen import InnererWiderstand
from opencivil.pfahl.pfahl import Kombination, Pfahl
from opencivil.pfahl.steifigkeit import Pfahlsteifigkeit
from opencivil.projekt.lesen import als_groesse
from opencivil.projekt.pfahl import PfahlEintrag

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil, material

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: PfahlEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Pfahl und seine beiden Nachweise, sobald eine Kombination
    eingeschaltet ist -- ohne sie steht er allein da, wie ein Grundbruch
    ohne Kombination. Seine Steifigkeit, gleich ob mit Kombinationen, sobald
    unter dem Fuss Boden ist; sie liest nur die Schichten, auch wenn R_a,k
    aus einem Versuch kommt. Jede Zahl in der Einheit ihres Feldes
    (:func:`~opencivil.projekt.lesen.als_groesse`).
    """
    g = partial(als_groesse, eintrag)
    wo = f"Pfahl '{eintrag.name}'"
    schichten = [Pfahlschicht(name=s.name, verhalten=s.verhalten, mantel=s.mantel,
                              **{k: als_groesse(s, k) for k in (
                                  "d", "gamma", "phi_k", "c_k", "s_u", "q_s", "K",
                                  "delta_faktor", "alpha", "E_s")})
                 for s in eintrag.schichten]
    pfahl = Pfahl(
        name=eintrag.name, praefix=f"{art.raum}.{eintrag.kennung}", art=eintrag.art,
        D=g("D"), L=g("L"), t_K=g("t_K"), t_w=g("t_w"), gamma_w=g("gamma_w"),
        schichten=schichten, grundlage=eintrag.grundlage, eta_a=g("eta_a"), R_ak=g("R_ak"),
        R_ak_zug=g("R_ak_zug"), spitze=eintrag.spitze, abscheren=eintrag.abscheren,
        q_b=g("q_b"), eta_i=g("eta_i"),
        stahl=material(aufbau.baustoffe, eintrag.stahl, "betonstahl", wo),
        beton=(material(aufbau.baustoffe, eintrag.beton, "beton", wo) if eintrag.bohrpfahl
               else None),
        n=g("n"), phi_l=g("phi_l"), c=g("c"), phi_w=g("phi_w"), tragglied=eintrag.tragglied,
        d_a=g("d_a"), t_r=g("t_r"), dt=g("dt"), kopf=eintrag.kopf, t_red=g("t_red"))
    pfahl.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag.kennung, eintrag.name, art, pfahl)
    kombinationen = [Kombination(name=k.name, **{n: als_groesse(k, n)
                                                 for n in ("N_Ed", "H_Ed", "M_Ed")})
                     for k in eintrag.kombinationen if k.aktiv]
    if kombinationen:
        aufbau.eintragen(teil, "pfahl_aussen", eintrag.kennung,
                         AeussererWiderstand(pfahl, kombinationen))
        aufbau.eintragen(teil, "pfahl_innen", eintrag.kennung,
                         InnererWiderstand(pfahl, kombinationen))
    else:
        aufbau.warnungen.append(f"{wo}: keine Kombination → kein Nachweis.")
    if eintrag.boden_unter_dem_fuss:
        steifigkeit = Pfahlsteifigkeit(pfahl, kombinationen)
        aufbau.werk.registriere(steifigkeit)
        teil.weitere_ziele.append(steifigkeit.id)
        teil.kennzahlen += steifigkeit.kennzahlen
    else:
        aufbau.warnungen.append(f"{wo}: die Schichten reichen nicht bis unter den Fuss → "
                                f"keine Steifigkeit.")
    return teil
