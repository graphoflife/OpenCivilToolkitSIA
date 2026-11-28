"""
opencivil/projekt/aufbau/mauerwerk.py -- eine Mauerwerkswand wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.mauerwerk.MauerwerkEintrag` die Wand
in SI (:func:`wand_von`) und das Bauteil im Rechenwerk (:func:`bauen`).
Ohne Mauerwerk rechnet die Wand nicht, und der Hinweis sagt es
(:meth:`~opencivil.projekt.aufbau.kern.Aufbau.unfertig`); was ihrer
Zeichnung fehlt -- ein Knoten, auf den etwas zeigt --, steht in ihren
Meldungen, und der Rest des Projekts rechnet.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple

from opencivil.decke.geometrie import Punkt
from opencivil.mauerwerk.modell import Oeffnung, Umriss, Wand
from opencivil.mauerwerk.werk import VORGABEN, Mauerwerkswand
from opencivil.projekt.lesen import als_groesse, ort_von
from opencivil.projekt.mauerwerk import MauerwerkEintrag
from opencivil.stabwerk.system import Meldung

from opencivil.projekt.aufbau.faelle import doppelte_kennungen
from opencivil.projekt.aufbau.kern import Aufbau, Bauteil, material

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart

#: Warum die Wand noch keinen Nachweis führt -- bis die Nachweise kommen
#: (Plan vom 2026-11-27, Schritt 14 b–e).
OHNE_NACHWEIS = "die Nachweise des Mauerwerks rechnet das Werkzeug noch nicht"


def wand_von(eintrag: MauerwerkEintrag) -> Tuple[Wand, List[Meldung]]:
    """
    Die Wand der Beschreibung in SI: Masse in m. Ein Umriss, der auf einen
    Knoten zeigt, den es nicht gibt, fehlt in der Wand; die Meldung sagt es.
    """
    lagen = eintrag.lagen()
    meldungen: List[Meldung] = []
    for was, liste in (("Knoten", eintrag.knoten), ("Wände", eintrag.waende),
                       ("Öffnungen", eintrag.oeffnungen)):
        meldungen.extend(doppelte_kennungen(was, liste))

    def orte(teil, knoten: Sequence[str]) -> Optional[Tuple[Punkt, ...]]:
        fehlt = [k for k in knoten if k not in lagen]
        if fehlt:
            meldungen.append(Meldung(f"{teil.kennung} zeigt auf {', '.join(fehlt)} – einen solchen "
                                     f"Knoten gibt es nicht.", (teil.kennung,)))
            return None
        return tuple(lagen[k] for k in knoten)

    wand = Wand(
        umrisse=tuple(Umriss(w.kennung, ecken) for w in eintrag.waende
                      if (ecken := orte(w, w.knoten)) is not None),
        oeffnungen=tuple(Oeffnung(o.kennung, ecken, sturz=o.sturz, h_St=o.si("h_St"), a=o.si("a"))
                         for o in eintrag.oeffnungen if (ecken := orte(o, o.knoten)) is not None),
        mauerung=eintrag.mauerung, stossfugen=eintrag.stossfugen,
        kopf=eintrag.kopf, fuss=eintrag.fuss, links=eintrag.links, rechts=eintrag.rechts)
    return wand, meldungen


def bauen(art: "Bauteilart", eintrag: MauerwerkEintrag, aufbau: Aufbau) -> Bauteil:
    """Eine Wand: Mauerwerk und Zeichnung, angemeldet im Rechenwerk -- noch ohne Nachweis."""
    wo = ort_von(eintrag)
    stoff = material(aufbau.baustoffe, eintrag.material, "mauerwerk", wo, "Mauerwerk")
    wand, meldungen = wand_von(eintrag)
    objekt = Mauerwerkswand(
        name=eintrag.name, kennung=eintrag.kennung, praefix=f"{art.raum}.{eintrag.kennung}",
        wand=wand, mauerwerk=stoff, meldungen=meldungen,
        vorgaben={f.kurz: als_groesse(eintrag, f.kurz) for g in VORGABEN for f in g.fuer(eintrag)})
    objekt.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag, art, objekt, weitere_ziele=objekt.ziele())
    aufbau.ohne_nachweis(teil, wo, OHNE_NACHWEIS)
    return teil
