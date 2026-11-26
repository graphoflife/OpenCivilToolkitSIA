"""
opencivil/projekt/aufbau/erdbeben.py -- ein Gebaeude im Erdbeben wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.erdbeben.ErdbebenEintrag` das
:class:`~opencivil.erdbeben.ersatzkraft.Gebaeude` und sein
Ersatzkraftverfahren (:func:`bauen`). Jede Wand nimmt ihren Querschnitt aus
einer Querschnittsanalyse des Projekts, mit deren Beton -- was ihr dazu
fehlt, sagt :func:`wandquerschnitt`, fuer die Rechnung und fuer das Bild.
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Dict, List, Union

from opencivil.erdbeben.ersatzkraft import (
    Ersatzkraft, Gebaeude, Geschoss, Schwingzeit, Wand, Wandquerschnitt,
)
from opencivil.material.basis import Baustoffart
from opencivil.projekt.erdbeben import ErdbebenEintrag, TragwandEintrag
from opencivil.projekt.lesen import als_groesse, ort_von
from opencivil.querschnitt.bauweise import Bauweise

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil, Grund

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def bauen(art: "Bauteilart", eintrag: ErdbebenEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Gebaeude und sein Ersatzkraftverfahren, sobald es ein Geschoss hat
    und jede Wand einen Querschnitt. Rechnet eine Wand nicht, rechnet das
    Gebaeude nicht: ohne sie stimmten Schwingzeit und Verteilung nicht, und
    die Zahlen saehen doch richtig aus. Ohne Wand rechnet es nur mit T_1 von
    Hand -- die Kraefte je Geschoss, ohne Verteilung. Gleiche Gruende
    mehrerer Waende stehen einmal da, mit allen Namen.
    """
    g = partial(als_groesse, eintrag)
    waende: List[Wand] = []
    fehlt: Dict[str, List[str]] = {}
    for nummer, w in enumerate(eintrag.waende, start=1):
        q = wandquerschnitt(w, aufbau)
        if isinstance(q, Grund):
            fehlt.setdefault(q.text, []).append(w.name)
        else:
            waende.append(Wand(nummer=nummer, name=w.name, lage=w.lage, n=als_groesse(w, "n"),
                               eta_EI=als_groesse(w, "eta_EI"), querschnitt=q))
    gruende = [f"{text} («{'», «'.join(namen)}»)" for text, namen in fehlt.items()]
    gebaeude = Gebaeude(
        name=eintrag.name, zone=eintrag.zone, baugrund=eintrag.baugrund,
        bauwerksklasse=eintrag.bauwerksklasse, schwingzeit=eintrag.schwingzeit,
        grundriss_regelmaessig=eintrag.grundriss_regelmaessig,
        aufriss_regelmaessig=eintrag.aufriss_regelmaessig,
        q_x=g("q_x"), q_y=g("q_y"), T1_x=g("T1_x"), T1_y=g("T1_y"),
        geschosse=[Geschoss(name=s.name, h=als_groesse(s, "h"), G_k=als_groesse(s, "G_k"),
                            Q_k=als_groesse(s, "Q_k"), psi_2=als_groesse(s, "psi_2"))
                   for s in eintrag.geschosse],
        waende=waende, praefix=f"{art.raum}.{eintrag.kennung}")
    gebaeude.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag, art, gebaeude)
    wo = ort_von(eintrag)
    if not eintrag.geschosse:
        aufbau.ohne_nachweis(teil, wo, "noch kein Geschoss – unter «Geschosse» eines anlegen")
    elif gruende:
        aufbau.ohne_nachweis(teil, wo, "; ".join(gruende))
    elif not waende and eintrag.schwingzeit is Schwingzeit.WAENDE:
        aufbau.ohne_nachweis(teil, wo, "noch keine Wand – unter «Wände» eine anlegen, "
                                       "oder T₁ von Hand angeben")
    else:
        aufbau.eintragen(teil, "erdbeben", eintrag.kennung, Ersatzkraft(gebaeude))
    return teil


def wandquerschnitt(wand: TragwandEintrag, aufbau: Aufbau) -> Union[Wandquerschnitt, Grund]:
    """
    Was eine Wand aus ihrer Querschnittsanalyse nimmt -- oder warum sie
    nichts nehmen kann, klein beginnend: noch keine gewaehlt, eine, die es
    nicht mehr gibt oder die nicht rechnet, oder eine mit mehr als einem
    Beton -- E_cm gilt nur fuer einen. Das fehlt nur. Falsch ist eine
    Analyse aus Holz, Stahl oder im Verbund
    (:mod:`~opencivil.querschnitt.bauweise`): die Steifigkeit einer Wand
    nimmt E_cm, sie ist aus Stahlbeton -- und hat damit einen Beton.
    """
    if not wand.analyse:
        return Grund("noch keine Querschnittsanalyse gewählt")
    analyse = aufbau.querschnittsanalysen.get(wand.analyse)
    if analyse is None:
        unfertig = aufbau.unfertige.get(wand.analyse)
        if unfertig is None:
            return Grund("die gewählte Querschnittsanalyse gibt es nicht mehr – eine andere wählen")
        return Grund(f"die Querschnittsanalyse «{unfertig.name}» rechnet nicht ({unfertig.grund})")
    if analyse.bauweise is not Bauweise.STAHLBETON:
        return Grund(f"die Querschnittsanalyse «{analyse.name}» ist ein "
                     f"{analyse.bauweise.querschnitt} – eine Wand rechnet das Werkzeug nur aus "
                     f"Stahlbeton", falsch=True)
    betone = list({f.stoff.id: f.stoff for f in analyse.flaechen
                   if f.stoff is not None and f.stoff.art is Baustoffart.BETON}.values())
    if len(betone) > 1:
        namen = "», «".join(b.name for b in betone)
        return Grund(f"die Querschnittsanalyse «{analyse.name}» hat mehr als einen Beton "
                     f"(«{namen}») – für E_cm braucht es genau einen")
    beton, = betone
    return Wandquerschnitt(analyse=analyse.name, beton=beton.name,
                           I_y=analyse.id_von("I_y"), I_z=analyse.id_von("I_z"),
                           I_yz=analyse.id_von("I_yz"), E_cm=beton.id_von("E_cm"))
