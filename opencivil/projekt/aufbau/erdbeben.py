"""
opencivil/projekt/aufbau/erdbeben.py -- ein Gebaeude im Erdbeben wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.erdbeben.ErdbebenEintrag` das
:class:`~opencivil.erdbeben.ersatzkraft.Gebaeude` und sein
Ersatzkraftverfahren (:func:`bauen`). Jedes Geschoss nimmt seinen Kern aus
einer Querschnittsanalyse des Projekts, mit deren Beton und ihren Teilen --
was ihm dazu fehlt, sagt :func:`kerne`, fuer die Rechnung und fuer das Bild.
"""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from opencivil.erdbeben.ersatzkraft import Ersatzkraft, Gebaeude, Geschoss, Schwingzeit
from opencivil.erdbeben.kern import Kerndaten, teile
from opencivil.material.basis import Baustoffart
from opencivil.projekt.erdbeben import ErdbebenEintrag
from opencivil.projekt.lesen import als_groesse, ort_von
from opencivil.querschnitt.bauweise import Bauweise

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil, Grund

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart

#: Was ein Geschoss von seinem Kern weiss: was er gibt, warum er nichts gibt
#: -- oder nichts, wo kein Geschoss einen Kern hat.
Kernbefund = Optional[Union[Kerndaten, Grund]]


def bauen(art: "Bauteilart", eintrag: ErdbebenEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Gebaeude und sein Ersatzkraftverfahren, sobald es ein Geschoss hat
    und jedes Geschoss einen Kern, der rechnet. Rechnet einer nicht, rechnet
    das Gebaeude nicht: ohne ihn stimmten Schwingzeit und Verteilung nicht,
    und die Zahlen saehen doch richtig aus. Ohne Kern in allen Geschossen
    rechnet es nur mit T_1 von Hand -- die Kraefte je Geschoss, ohne
    Verteilung. Gleiche Gruende mehrerer Geschosse stehen einmal da, mit
    allen Namen.
    """
    g = partial(als_groesse, eintrag)
    befunde = kerne(eintrag, aufbau)
    fehlt: Dict[str, List[str]] = {}
    for s, b in zip(eintrag.geschosse, befunde):
        if isinstance(b, Grund):
            fehlt.setdefault(b.text, []).append(s.name)
    gruende = [f"{text} («{'», «'.join(namen)}»)" for text, namen in fehlt.items()]
    gebaeude = Gebaeude(
        name=eintrag.name, zone=eintrag.zone, baugrund=eintrag.baugrund,
        bauwerksklasse=eintrag.bauwerksklasse, schwingzeit=eintrag.schwingzeit,
        grundriss_regelmaessig=eintrag.grundriss_regelmaessig,
        aufriss_regelmaessig=eintrag.aufriss_regelmaessig,
        q_x=g("q_x"), q_y=g("q_y"), T1_x=g("T1_x"), T1_y=g("T1_y"),
        geschosse=[Geschoss(name=s.name, h=als_groesse(s, "h"), G_k=als_groesse(s, "G_k"),
                            Q_k=als_groesse(s, "Q_k"), psi_2=als_groesse(s, "psi_2"),
                            eta_EI=als_groesse(s, "eta_EI"),
                            kern=s.kern if isinstance(b, Kerndaten) else None)
                   for s, b in zip(eintrag.geschosse, befunde)],
        kerne={b.kennung: b for b in befunde if isinstance(b, Kerndaten)},
        praefix=f"{art.raum}.{eintrag.kennung}")
    gebaeude.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag, art, gebaeude)
    wo = ort_von(eintrag)
    if not eintrag.geschosse:
        aufbau.ohne_nachweis(teil, wo, "noch kein Geschoss – unter «Geschosse» eines anlegen")
    elif gruende:
        aufbau.ohne_nachweis(teil, wo, "; ".join(gruende))
    elif not gebaeude.mit_kern and eintrag.schwingzeit is Schwingzeit.KERN:
        aufbau.ohne_nachweis(teil, wo, "noch kein Kern – unter «Kern» je Geschoss eine "
                                       "Querschnittsanalyse wählen, oder T₁ von Hand angeben")
    else:
        aufbau.eintragen(teil, "erdbeben", eintrag.kennung, Ersatzkraft(gebaeude))
    return teil


def kerne(eintrag: ErdbebenEintrag, aufbau: Aufbau) -> List[Kernbefund]:
    """
    Je Geschoss, von unten, was sein Kern gibt oder warum er nichts gibt --
    ``None`` in jedem, wo keines einen hat: dann rechnet das Gebaeude nur mit
    T_1 von Hand. Hat eines einen, braucht jedes einen. Jede Analyse wird
    einmal geprueft, auch wo viele Geschosse sie nehmen.
    """
    if not any(s.kern for s in eintrag.geschosse):
        return [None] * len(eintrag.geschosse)
    je_analyse: Dict[str, Union[Kerndaten, Grund]] = {}
    for s in eintrag.geschosse:
        if s.kern not in je_analyse:
            je_analyse[s.kern] = kernquerschnitt(s.kern, aufbau)
    return [je_analyse[s.kern] for s in eintrag.geschosse]


def kernquerschnitt(kennung: str, aufbau: Aufbau) -> Union[Kerndaten, Grund]:
    """
    Was ein Kern aus seiner Querschnittsanalyse nimmt -- oder warum er
    nichts nehmen kann, klein beginnend: noch keine gewaehlt, eine, die es
    nicht mehr gibt oder die nicht rechnet, oder eine mit mehr als einem
    Beton -- E_cm gilt nur fuer einen. Das fehlt nur. Falsch ist eine
    Analyse aus Holz, Stahl oder im Verbund
    (:mod:`~opencivil.querschnitt.bauweise`): die Steifigkeit des Kerns
    nimmt E_cm, er ist aus Stahlbeton -- und hat damit einen Beton.
    """
    if not kennung:
        return Grund("noch keine Querschnittsanalyse gewählt")
    analyse = aufbau.querschnittsanalysen.get(kennung)
    if analyse is None:
        unfertig = aufbau.unfertige.get(kennung)
        if unfertig is None:
            return Grund("die gewählte Querschnittsanalyse gibt es nicht mehr – eine andere wählen")
        return Grund(f"die Querschnittsanalyse «{unfertig.name}» rechnet nicht ({unfertig.grund})")
    if analyse.bauweise is not Bauweise.STAHLBETON:
        return Grund(f"die Querschnittsanalyse «{analyse.name}» ist ein "
                     f"{analyse.bauweise.querschnitt} – einen Kern rechnet das Werkzeug nur aus "
                     f"Stahlbeton", falsch=True)
    betone = list({f.stoff.id: f.stoff for f in analyse.flaechen
                   if f.stoff is not None and f.stoff.art is Baustoffart.BETON}.values())
    if len(betone) > 1:
        namen = "», «".join(b.name for b in betone)
        return Grund(f"die Querschnittsanalyse «{analyse.name}» hat mehr als einen Beton "
                     f"(«{namen}») – für E_cm braucht es genau einen")
    beton, = betone
    z = analyse.zeichnung
    return Kerndaten(kennung=kennung, analyse=analyse.name, beton=beton.name,
                     E_cm=beton.id_von("E_cm"),
                     teile=teile(z.punkte, z.namen, z.eltern, z.gewicht))
