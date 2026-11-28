"""
opencivil/web/fachwerkdaten.py -- was die Oberflaeche von einem Fachwerkmodell zeichnet.

VERANTWORTUNG:
Aus dem Befund eines Fachwerkmodells die Daten seiner Zeichnung: seine
Meldungen, ob es bereit ist, ein Fachwerk zu suchen -- keine Meldung des
Modells haelt es auf --, und das gefundene Fachwerk, nachgerechnet
(:func:`uebersicht`). Dazu eine Runde der Suche (:func:`suchen`) und der
Teil des Katalogs, den nur das Fachwerkmodell braucht (:func:`katalog`).
Scheiben, Lager und Lasten zeichnet die Oberflaeche nach dem Projekt.

EIN FACHWERK, ZWEI WEGE:
Was eine Runde gibt und was die Rechnung nachgerechnet hat, hat dieselbe
Form (:func:`_fachwerk`): Knoten ``{x, y}`` in m, Staebe ``{von, bis, N,
l}`` mit N in kN, Zug positiv, und l in m -- so zeichnet die Seite beide
mit einem Bild, waehrend gesucht wird und danach.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Mapping, Optional

from opencivil.core.einheiten import KN, KNM
from opencivil.core.rechenwerk import Loesung
from opencivil.fachwerkmodell.grundstruktur import ZuVieleKnoten
from opencivil.fachwerkmodell.modell import Halt
from opencivil.fachwerkmodell.nachrechnung import Nachrechnung, nachrechnen
from opencivil.fachwerkmodell.pruefen import pruefen
from opencivil.fachwerkmodell.suche import (ZUG_ACHSPARALLEL, ZUG_ACHSPARALLEL_ERKLAERUNG,
                                            Suchzustand, abdruck, runde)
from opencivil.fachwerkmodell.werk import Fachwerkbefund, offen_meldungen
from opencivil.projekt import Aufbau
from opencivil.projekt.aufbau.fachwerkmodell import einstellung_von, modell_von
from opencivil.projekt.fachwerkmodell import VORSILBEN, FachwerkmodellEintrag, GefundenesFachwerk
from opencivil.projekt.lesen import ProjektFehler
from opencivil.stabwerk.system import Meldung
from opencivil.web.anzeige import zahl


def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """Was die Zeichnung eines Fachwerkmodells unter seine Teile legt -- auch wenn es nicht rechnet."""
    return uebersicht(loesung.befunde.get(aufbau.fachwerkmodelle[kennung].rechnung.id))


def uebersicht(befund: Optional[Fachwerkbefund]) -> Dict[str, Any]:
    """
    ``bereit``; ``meldungen`` des Modells und ``zum_fachwerk``, was zum
    Fachwerk zu sagen ist, je ``{text, elemente, fehler, unfertig}``;
    ``abdruck`` von Modell und Verfahren und ``stand`` -- ``keines``,
    ``veraltet``, ``unlesbar``, ``gefunden`` oder leer
    (:class:`Fachwerkbefund`); und ``fachwerk``: nachgerechnet, mit ``V``
    in kNm, den Kraeften der Lager, den Runden und wie viele Staebe es gab
    -- oder ``None``. Ohne Befund leer.

    Am Abdruck erkennt die Seite, ob das Fachwerk, das eine Suche eben gab,
    zum Modell der letzten Rechnung gehoert -- und zeigt es, bis die
    Rechnung es nachgerechnet hat.
    """
    if befund is None:
        return {"bereit": False, "meldungen": [], "zum_fachwerk": [], "abdruck": "", "stand": "",
                "fachwerk": None}
    gefunden, n = befund.gefunden, befund.nachrechnung
    fachwerk = None
    if gefunden is not None and n is not None:
        fachwerk = {**_fachwerk(n), "runden": gefunden.runden, "fertig": gefunden.fertig,
                    "moeglich": gefunden.moeglich, "im_modell": gefunden.im_modell}
    return {"bereit": befund.bereit, "meldungen": [m.als_dict() for m in befund.meldungen],
            "zum_fachwerk": [m.als_dict() for m in befund.zum_fachwerk],
            "abdruck": befund.abdruck, "stand": befund.stand, "fachwerk": fachwerk}


def _fachwerk(n: Nachrechnung) -> Dict[str, Any]:
    """Siehe Dateikopf -- dazu ``V`` in kNm und je Lager ``{lager, R_x, R_y}`` in kN."""
    fw = n.fachwerk
    return {
        "knoten": [{"x": x, "y": y} for x, y in fw.knoten],
        "staebe": [{"von": a, "bis": b, "N": zahl(N, KN), "l": l}
                   for (a, b, N), l in zip(fw.staebe, n.laengen)],
        "V": zahl(n.V, KNM),
        "lagerkraefte": [{"lager": k.lager.name, "R_x": zahl(k.R_x, KN), "R_y": zahl(k.R_y, KN)}
                         for k in n.lagerkraefte],
    }


def suchen(eintrag: FachwerkmodellEintrag, zustand: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """
    Eine Runde der Suche (:func:`~opencivil.fachwerkmodell.suche.runde`):
    der ``zustand`` der letzten hinein -- ``None`` fuer die erste --, heraus

    - ``fertig``: ob die Suche zu Ende ist -- auch, wenn sie nicht beginnen kann;
    - ``abdruck``: von Modell und Verfahren, wie in :func:`uebersicht` --
      leer, wenn das Modell nicht bereit ist;
    - ``zustand``: fuer die naechste Runde;
    - ``gefunden``: was die Seite im Eintrag ablegt, wenn sie aufhoert
      (:class:`~opencivil.projekt.fachwerkmodell.GefundenesFachwerk`);
    - ``fachwerk``: dasselbe zum Zeichnen, nachgerechnet (:func:`_fachwerk`);
    - ``stand``: Runde, Staebe im Modell, moegliche, wie viele dazukommen;
    - ``meldungen``: was dem Suchen im Weg steht oder offen bleibt.
    """
    modell, meldungen = modell_von(eintrag)
    meldungen += pruefen(modell)
    if any(m.haelt_an for m in meldungen):
        return _ohne(meldungen)
    einstellung = einstellung_von(eintrag)
    try:
        r = runde(modell, einstellung, _zustand(zustand))
    except ZuVieleKnoten as fehler:
        return _ohne([Meldung(str(fehler))], abdruck(modell, einstellung))
    e = r.ergebnis
    n = nachrechnen(modell, e.fachwerk, einstellung.w_Z)
    return {
        "fertig": e.fertig,
        "abdruck": e.abdruck,
        "zustand": {"abdruck": r.zustand.abdruck, "runde": r.zustand.runde,
                    "aktiv": list(r.zustand.aktiv)},
        "gefunden": asdict(GefundenesFachwerk.aus(e)),
        "fachwerk": _fachwerk(n),
        "stand": {"runde": e.runden, "im_modell": e.im_modell, "moeglich": e.moeglich,
                  "dazu": r.dazu},
        "meldungen": [m.als_dict() for m in offen_meldungen(n, einstellung)],
    }


def _ohne(meldungen, abdruck_: str = "") -> Dict[str, Any]:
    """Die Antwort, wenn die Suche nicht beginnen kann: nur, warum."""
    return {"fertig": True, "abdruck": abdruck_, "zustand": None, "gefunden": None,
            "fachwerk": None, "stand": None, "meldungen": [m.als_dict() for m in meldungen]}


def _zustand(roh: Optional[Mapping[str, Any]]) -> Optional[Suchzustand]:
    """Der Zustand, wie die Seite ihn zurueckschickt -- streng gelesen: sie hat ihn so bekommen."""
    if roh is None:
        return None
    try:
        aktiv = tuple(roh["aktiv"])
        if not (isinstance(roh["abdruck"], str) and isinstance(roh["runde"], int)
                and all(isinstance(i, int) and i >= 0 for i in aktiv)):
            raise TypeError
        return Suchzustand(roh["abdruck"], roh["runde"], aktiv)
    except (KeyError, TypeError):
        raise ProjektFehler("Der Zustand der Suche ist nicht lesbar.") from None


def katalog() -> Dict[str, Any]:
    """
    Womit die Kennungen der Teile beginnen, je Liste, wie ein Lager halten
    kann und wie der Schalter des Verfahrens heisst.
    """
    return {"vorsilben": dict(VORSILBEN),
            "halt": [{"wert": h.value, "beschriftung": h.beschriftung, "titel": h.erklaerung}
                     for h in Halt],
            "zug": {"beschriftung": ZUG_ACHSPARALLEL, "titel": ZUG_ACHSPARALLEL_ERKLAERUNG}}
