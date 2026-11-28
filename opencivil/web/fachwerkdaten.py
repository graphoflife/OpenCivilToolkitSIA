"""
opencivil/web/fachwerkdaten.py -- was die Oberflaeche von einem Fachwerkmodell zeichnet.

VERANTWORTUNG:
Aus dem Befund eines Fachwerkmodells die Daten seiner Zeichnung: seine
Meldungen, ob es bereit ist, ein Fachwerk zu suchen -- keine Meldung des
Modells haelt es auf --, und das gefundene Fachwerk, nachgerechnet
(:func:`uebersicht`). Dazu eine Runde der Suche (:func:`suchen`), beim
Verfahren SIMP Schritte, und der Teil des Katalogs, den nur das
Fachwerkmodell braucht (:func:`katalog`). Scheiben, Lager und Lasten
zeichnet die Oberflaeche nach dem Projekt.

EIN FACHWERK, ZWEI WEGE:
Was eine Runde gibt und was die Rechnung nachgerechnet hat, hat dieselbe
Form (:func:`_fachwerk`): Knoten ``{x, y}`` in m, Staebe ``{von, bis, N,
l}`` mit N in kN, Zug positiv, und l in m -- so zeichnet die Seite beide
mit einem Bild, waehrend gesucht wird und danach. Ebenso die Form des
Verfahrens SIMP (:func:`_formbild`).
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Mapping, Optional

from opencivil.core.einheiten import KN, KNM
from opencivil.core.rechenwerk import Loesung
from opencivil.fachwerkmodell import simp
from opencivil.fachwerkmodell.form import GENUG, Formeinstellung, Formzustand, schritte
from opencivil.fachwerkmodell.grundstruktur import ZuVieleKnoten
from opencivil.fachwerkmodell.modell import Halt, Modell
from opencivil.fachwerkmodell.nachrechnung import Nachrechnung, nachrechnen
from opencivil.fachwerkmodell.pruefen import pruefen
from opencivil.fachwerkmodell.suche import (ZUG_ACHSPARALLEL, ZUG_ACHSPARALLEL_ERKLAERUNG,
                                            Einstellung, Suchzustand, abdruck, runde)
from opencivil.fachwerkmodell.verfahren import Verfahren
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
    ``abdruck`` von Modell und Verfahren, das ``verfahren`` und ``stand`` --
    ``keines``, ``veraltet``, ``unlesbar``, ``gefunden`` oder leer
    (:class:`Fachwerkbefund`); ``fachwerk``: nachgerechnet, mit ``V`` in
    kNm, den Kraeften der Lager, den Runden und wie viele Staebe es gab --
    oder ``None``; und ``form``, aus der es beim Verfahren SIMP kommt
    (:func:`_formbild`), sonst ``None``. Ohne Befund leer.

    Am Abdruck erkennt die Seite, ob das Fachwerk, das eine Suche eben gab,
    zum Modell der letzten Rechnung gehoert -- und zeigt es, bis die
    Rechnung es nachgerechnet hat.
    """
    if befund is None:
        return {"bereit": False, "meldungen": [], "zum_fachwerk": [], "abdruck": "", "verfahren": "",
                "stand": "", "fachwerk": None, "form": None}
    gefunden, n = befund.gefunden, befund.nachrechnung
    fachwerk = form = None
    if gefunden is not None and n is not None:
        fachwerk = {**_fachwerk(n), "runden": gefunden.runden, "fertig": gefunden.fertig,
                    "moeglich": gefunden.moeglich, "im_modell": gefunden.im_modell}
        if gefunden.form:
            form = _formbild(befund.modell, befund.einstellung.weite, gefunden.form)
    return {"bereit": befund.bereit, "meldungen": [m.als_dict() for m in befund.meldungen],
            "zum_fachwerk": [m.als_dict() for m in befund.zum_fachwerk],
            "abdruck": befund.abdruck, "verfahren": befund.einstellung.verfahren.value,
            "stand": befund.stand, "fachwerk": fachwerk, "form": form}


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


def suchen(eintrag: FachwerkmodellEintrag, zustand: Optional[Mapping[str, Any]],
           abschliessen: bool = False) -> Dict[str, Any]:
    """
    Eine Runde der Suche (:func:`~opencivil.fachwerkmodell.suche.runde`),
    beim Verfahren SIMP die Schritte einer Anfrage
    (:func:`~opencivil.fachwerkmodell.form.schritte`): der ``zustand`` der
    letzten hinein -- ``None`` fuer die erste; gehoert er zum anderen
    Verfahren, beginnt die Suche von vorn --, heraus

    - ``verfahren``: welches suchte;
    - ``fertig``: ob die Suche zu Ende ist -- auch, wenn sie nicht beginnen kann;
    - ``abdruck``: von Modell und Verfahren, wie in :func:`uebersicht` --
      leer, wenn das Modell nicht bereit ist;
    - ``zustand``: fuer die naechste Runde;
    - ``gefunden``: was die Seite im Eintrag ablegt, wenn sie aufhoert
      (:class:`~opencivil.projekt.fachwerkmodell.GefundenesFachwerk`);
    - ``fachwerk``: dasselbe zum Zeichnen, nachgerechnet (:func:`_fachwerk`);
    - ``form``: beim Verfahren SIMP die Form (:func:`_formbild`), sonst ``None``;
    - ``stand``: Runde, Staebe im Modell, moegliche, wie viele dazukommen --
      bei SIMP Schritt, wie stark sich die Dichten zuletzt aenderten, ab
      wann es genug ist und wie viele Elemente es sind;
    - ``meldungen``: was dem Suchen im Weg steht oder offen bleibt.

    SIMP gibt das Fachwerk erst, wenn die Form fertig ist -- oder mit
    ``abschliessen``: dann ohne weiteren Schritt aus der Form, wie sie ist.
    """
    modell, meldungen = modell_von(eintrag)
    meldungen += pruefen(modell)
    if any(m.haelt_an for m in meldungen):
        return _ohne(meldungen)
    einstellung = einstellung_von(eintrag)
    roh = _vom_verfahren(zustand, einstellung.verfahren)
    try:
        if isinstance(einstellung, Formeinstellung):
            return _formen(modell, einstellung, _formzustand(roh), abschliessen)
        return _gesucht(modell, einstellung, _zustand(roh))
    except (ZuVieleKnoten, simp.NetzFehler) as fehler:
        return _ohne([Meldung(str(fehler))], abdruck(modell, einstellung))


def _gesucht(modell: Modell, einstellung: Einstellung, zustand: Optional[Suchzustand]) -> Dict[str, Any]:
    """Eine Runde der Ground Structure -- siehe :func:`suchen`."""
    r = runde(modell, einstellung, zustand)
    e = r.ergebnis
    n = nachrechnen(modell, e.fachwerk, einstellung.w_Z)
    return {
        "verfahren": Verfahren.GROUND_STRUCTURE.value,
        "fertig": e.fertig,
        "abdruck": e.abdruck,
        "zustand": {"verfahren": Verfahren.GROUND_STRUCTURE.value, "abdruck": r.zustand.abdruck,
                    "runde": r.zustand.runde, "aktiv": list(r.zustand.aktiv)},
        "gefunden": asdict(GefundenesFachwerk.aus(e)),
        "fachwerk": _fachwerk(n),
        "form": None,
        "stand": {"runde": e.runden, "im_modell": e.im_modell, "moeglich": e.moeglich,
                  "dazu": r.dazu},
        "meldungen": [m.als_dict() for m in offen_meldungen(n, einstellung)],
    }


def _formen(modell: Modell, einstellung: Formeinstellung, zustand: Optional[Formzustand],
            abschliessen: bool) -> Dict[str, Any]:
    """Die Schritte einer Anfrage im Verfahren SIMP, mit dem Fachwerk, wenn es eines gibt -- siehe :func:`suchen`."""
    r = schritte(modell, einstellung, zustand, abschliessen=abschliessen)
    e = r.ergebnis
    n = nachrechnen(modell, e.fachwerk, einstellung.w_Z) if e is not None else None
    return {
        "verfahren": Verfahren.SIMP.value,
        "fertig": r.fertig,
        "abdruck": r.zustand.abdruck,
        "zustand": {"verfahren": Verfahren.SIMP.value, "abdruck": r.zustand.abdruck,
                    "schritt": r.zustand.schritt, "dichte": list(r.zustand.dichte)},
        "gefunden": asdict(GefundenesFachwerk.aus(e)) if e is not None else None,
        "fachwerk": _fachwerk(n) if n is not None else None,
        "form": _formbild(modell, einstellung.weite, r.form),
        "stand": {"schritt": r.zustand.schritt, "aenderung": r.aenderung, "genug": GENUG,
                  "elemente": r.elemente},
        "meldungen": [m.als_dict() for m in offen_meldungen(n, einstellung)] if n is not None else [],
    }


def _formbild(modell: Modell, weite: float, werte: str) -> Optional[Dict[str, Any]]:
    """
    Die Form zum Zeichnen: die Ecke unten links ``x0``, ``y0`` und die
    Netzweite ``h`` in m, ``spalten`` und ``zeilen`` und je Feld sein
    Zeichen (:func:`~opencivil.fachwerkmodell.form.formtext`) -- ``None``,
    wenn die Zeichen nicht zum Raster passen.
    """
    (x0, y0), spalten, zeilen = simp.raster(modell, weite)
    if len(werte) != spalten * zeilen:
        return None
    return {"x0": x0, "y0": y0, "h": weite, "spalten": spalten, "zeilen": zeilen, "werte": werte}


def _ohne(meldungen, abdruck_: str = "") -> Dict[str, Any]:
    """Die Antwort, wenn die Suche nicht beginnen kann: nur, warum."""
    return {"verfahren": "", "fertig": True, "abdruck": abdruck_, "zustand": None, "gefunden": None,
            "fachwerk": None, "form": None, "stand": None,
            "meldungen": [m.als_dict() for m in meldungen]}


def _vom_verfahren(roh: Any, verfahren: Verfahren) -> Optional[Mapping[str, Any]]:
    """
    Der Zustand, wenn er zu ``verfahren`` gehoert -- ``None``, wenn er zum
    anderen gehoert: dann beginnt die Suche von vorn.
    """
    if roh is None:
        return None
    if not isinstance(roh, Mapping) or roh.get("verfahren") not in {v.value for v in Verfahren}:
        raise ProjektFehler("Der Zustand der Suche ist nicht lesbar.")
    return roh if roh["verfahren"] == verfahren.value else None


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


def _formzustand(roh: Optional[Mapping[str, Any]]) -> Optional[Formzustand]:
    """Der Zustand der Form, wie die Seite ihn zurueckschickt -- ebenso streng gelesen."""
    if roh is None:
        return None
    try:
        dichte = tuple(roh["dichte"])
        if not (isinstance(roh["abdruck"], str) and isinstance(roh["schritt"], int)
                and all(isinstance(d, (int, float)) and not isinstance(d, bool) for d in dichte)):
            raise TypeError
        return Formzustand(roh["abdruck"], roh["schritt"], tuple(float(d) for d in dichte))
    except (KeyError, TypeError):
        raise ProjektFehler("Der Zustand der Suche ist nicht lesbar.") from None


def katalog() -> Dict[str, Any]:
    """
    Womit die Kennungen der Teile beginnen, je Liste, wie ein Lager halten
    kann, welche Verfahren es gibt und wie der Schalter der Ground
    Structure heisst.
    """
    return {"vorsilben": dict(VORSILBEN),
            "halt": [{"wert": h.value, "beschriftung": h.beschriftung, "titel": h.erklaerung}
                     for h in Halt],
            "verfahren": [{"wert": v.value, "beschriftung": v.beschriftung, "titel": v.erklaerung}
                          for v in Verfahren],
            "zug": {"beschriftung": ZUG_ACHSPARALLEL, "titel": ZUG_ACHSPARALLEL_ERKLAERUNG}}
