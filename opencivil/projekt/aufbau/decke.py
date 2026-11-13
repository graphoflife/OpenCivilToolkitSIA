"""
opencivil/projekt/aufbau/decke.py -- eine Decke wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.decke.DeckeEintrag` das Modell der
Streifenmethode in SI (:func:`modell_von`) und das Bauteil im Rechenwerk
(:func:`bauen`). Hart scheitert nur ein Verweis auf einen Beton, den es im
Projekt nicht gibt -- wie im Balkensystem. Was der Decke selbst fehlt --
ein Knoten, eine Platte ohne Beton --, steht in ihren Meldungen, und der
Rest des Projekts rechnet.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple

from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Decke, Linienlager, Platte, Stuetze, Unterzug, Zone
from opencivil.decke.werk import Deckensystem
from opencivil.material.basis import Baustoff
from opencivil.projekt.decke import DeckeEintrag
from opencivil.projekt.lesen import ProjektFehler
from opencivil.stabwerk.system import Meldung

from opencivil.projekt.aufbau.kern import Aufbau, Bauteil

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def modell_von(eintrag: DeckeEintrag) -> Tuple[Decke, List[Meldung]]:
    """
    Die Decke der Beschreibung in SI -- E und Gewicht der Platten null, die
    kommen beim Rechnen von ihrem Beton. Ein Teil, das auf einen Knoten
    zeigt, den es nicht gibt, fehlt im Modell; die Meldung sagt es.
    """
    lagen = eintrag.lagen()
    meldungen: List[Meldung] = []

    def orte(teil, knoten: Sequence[str]) -> Optional[Tuple[Punkt, ...]]:
        fehlt = [k for k in knoten if k not in lagen]
        if fehlt:
            meldungen.append(Meldung(f"{teil.kennung} zeigt auf {', '.join(fehlt)} -- einen solchen "
                                     f"Knoten gibt es nicht.", (teil.kennung,)))
            return None
        return tuple(lagen[k] for k in knoten)

    platten = [Platte(p.kennung, ecken, p.si("h"), 0.0, 0.0, (p.si("richtung_1"), p.si("richtung_2")))
               for p in eintrag.platten if (ecken := orte(p, p.knoten)) is not None]
    linienlager = [Linienlager(l.kennung, *ab, vertikal=l.vertikal, eingespannt=l.eingespannt)
                   for l in eintrag.linienlager if (ab := orte(l, (l.von, l.bis))) is not None]
    stuetzen = [Stuetze(s.kennung, ort[0], s.si("b_x"), s.si("b_y"),
                        *((s.si("l_x"), s.si("l_y")) if s.bereich_von_hand else (None, None)))
                for s in eintrag.stuetzen if (ort := orte(s, (s.knoten,))) is not None]
    unterzuege = [Unterzug(u.kennung, *ab, u.si("breite"), u.stufe)
                  for u in eintrag.unterzuege if (ab := orte(u, (u.von, u.bis))) is not None]
    zonen = [Zone(z.kennung, ecken, z.si("anteil"))
             for z in eintrag.zonen if (ecken := orte(z, z.knoten)) is not None]
    decke = Decke(platten=platten, linienlager=linienlager, stuetzen=stuetzen,
                  unterzuege=unterzuege, zonen=zonen, streifenbreite=eintrag.si("streifenbreite"),
                  aufteilung=eintrag.aufteilung, anteil=eintrag.si("anteil"))
    return decke, meldungen


def _betone(eintrag: DeckeEintrag, aufbau: Aufbau) -> Tuple[Dict[str, Baustoff], List[Meldung]]:
    """Je Platte ihr Beton -- und eine Meldung je Platte, die keinen hat."""
    betone: Dict[str, Baustoff] = {}
    meldungen: List[Meldung] = []
    for p in eintrag.platten:
        if not p.beton:
            meldungen.append(Meldung(f"Platte {p.kennung}: kein Beton gewählt.", (p.kennung,)))
            continue
        stoff = aufbau.baustoffe.get(p.beton)
        if stoff is None:
            raise ProjektFehler(f"Decke '{eintrag.name}': das Material '{p.beton}' gibt es im "
                                f"Projekt nicht.")
        if stoff.art.value != "beton":
            meldungen.append(Meldung(f"Platte {p.kennung}: «{stoff.name}» ist kein Beton.", (p.kennung,)))
            continue
        betone[p.kennung] = stoff
    return betone, meldungen


def bauen(art: "Bauteilart", eintrag: DeckeEintrag, aufbau: Aufbau) -> Bauteil:
    """Eine Decke: ihr Modell, ihre Betone, angemeldet im Rechenwerk."""
    decke, meldungen = modell_von(eintrag)
    betone, ohne = _betone(eintrag, aufbau)
    system = Deckensystem(name=eintrag.name, kennung=eintrag.kennung,
                          praefix=f"{art.raum}.{eintrag.kennung}", decke=decke, betone=betone,
                          meldungen=meldungen + ohne)
    system.ins_rechenwerk(aufbau.werk)
    return Bauteil(eintrag.kennung, eintrag.name, art, system, weitere_ziele=system.ziele())
