"""
opencivil/projekt/aufbau/fachwerkmodell.py -- ein Fachwerkmodell wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.fachwerkmodell.FachwerkmodellEintrag`
das Modell in SI (:func:`modell_von`) und das Bauteil im Rechenwerk
(:func:`bauen`). Hart scheitert nichts: was dem Modell fehlt -- ein
Knoten, auf den etwas zeigt --, steht in seinen Meldungen, und der Rest des
Projekts rechnet.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple

from opencivil.decke.geometrie import Punkt
from opencivil.fachwerkmodell.modell import Lager, Last, Modell, Umriss
from opencivil.fachwerkmodell.werk import Fachwerksystem
from opencivil.projekt.fachwerkmodell import FachwerkmodellEintrag
from opencivil.stabwerk.system import Meldung

from opencivil.projekt.aufbau.faelle import doppelte_kennungen
from opencivil.projekt.aufbau.kern import Aufbau, Bauteil

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def modell_von(eintrag: FachwerkmodellEintrag) -> Tuple[Modell, List[Meldung]]:
    """
    Das Modell der Beschreibung in SI: Kräfte in N, die senkrechte nach
    oben positiv. Ein Teil, das auf einen Knoten zeigt, den es nicht gibt,
    fehlt im Modell; die Meldung sagt es.
    """
    lagen = eintrag.lagen()
    meldungen: List[Meldung] = []
    for was, liste in (("Knoten", eintrag.knoten), ("Scheiben", eintrag.scheiben),
                       ("Löcher", eintrag.loecher), ("Lager", eintrag.lager),
                       ("Lasten", eintrag.lasten)):
        meldungen.extend(doppelte_kennungen(was, liste))

    def orte(teil, knoten: Sequence[str]) -> Optional[Tuple[Punkt, ...]]:
        fehlt = [k for k in knoten if k not in lagen]
        if fehlt:
            meldungen.append(Meldung(f"{teil.kennung} zeigt auf {', '.join(fehlt)} – einen solchen "
                                     f"Knoten gibt es nicht.", (teil.kennung,)))
            return None
        return tuple(lagen[k] for k in knoten)

    modell = Modell(
        scheiben=tuple(Umriss(s.kennung, ecken) for s in eintrag.scheiben
                       if (ecken := orte(s, s.knoten)) is not None),
        loecher=tuple(Umriss(l.kennung, ecken) for l in eintrag.loecher
                      if (ecken := orte(l, l.knoten)) is not None),
        lager=tuple(Lager(a.kennung, ort[0], a.halt) for a in eintrag.lager
                    if (ort := orte(a, (a.knoten,))) is not None),
        lasten=tuple(Last(f.kennung, ort[0], f.si("F_h"), -f.si("F_v")) for f in eintrag.lasten
                     if (ort := orte(f, (f.knoten,))) is not None))
    return modell, meldungen


def bauen(art: "Bauteilart", eintrag: FachwerkmodellEintrag, aufbau: Aufbau) -> Bauteil:
    """Ein Fachwerkmodell: sein Modell, angemeldet im Rechenwerk."""
    modell, meldungen = modell_von(eintrag)
    system = Fachwerksystem(name=eintrag.name, kennung=eintrag.kennung,
                            praefix=f"{art.raum}.{eintrag.kennung}", modell=modell,
                            meldungen=meldungen)
    system.ins_rechenwerk(aufbau.werk)
    return Bauteil(eintrag, art, system, weitere_ziele=system.ziele())
