"""
opencivil/web/mauerwerkdaten.py -- was die Oberflaeche von einer Wand aus Mauerwerk zeichnet.

VERANTWORTUNG:
Aus dem Befund einer Wand die Daten ihrer Zeichnung (:func:`uebersicht`):
ihre Meldungen -- die zu Mauerwerk und Dicke auch fuer sich, fuer die
Kachel der Maske --, ob sie rechnet, ihre Pfeiler und je Oeffnung die
Flaeche ihres Sturzes -- der Kern weiss, wie weit er aufliegt; die Seite zeichnet
ihn nur. Dazu je Pfeiler und Sturzauflager das Urteil, das an ihm gilt
(:func:`urteile`), fuer die Farbe im Bild, und der Teil des Katalogs, den
nur die Wand braucht (:func:`katalog`). Umriss, Oeffnungen und Lasten
zeichnet die Oberflaeche nach dem Projekt; die Bemessungswerte stehen in
der Zusammenfassung ueber den Nachweisen (:mod:`opencivil.mauerwerk.uebersicht`).

EINHEITEN:
In m, wie im Zeichenfenster; die ueblichen Dicken in mm, wie das Feld.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from opencivil.core.nachweis import OHNE_EINWIRKUNG, Nachweis, NachweisUrteil
from opencivil.core.rechenwerk import Loesung
from opencivil.core.sprache import satzanfang
from opencivil.mauerwerk.modell import Halterung, Mauerung, Seitenrand, Stossfugen, Sturzart
from opencivil.mauerwerk.nachweise import Stelle
from opencivil.mauerwerk.pruefen import UEBLICHE_DICKEN
from opencivil.mauerwerk.werk import Wandbefund
from opencivil.projekt import Aufbau
from opencivil.projekt.mauerwerk import VORSILBEN
from opencivil.stabwerk.system import Meldung

def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Zeichnung einer Wand unter ihre Teile legt -- auch wenn sie
    nicht rechnet: :func:`uebersicht` und die Urteile (:func:`urteile`).
    """
    befund = loesung.befunde.get(aufbau.mauerwerke[kennung].rechnung.id)
    return {**uebersicht(befund),
            "urteile": urteile([n for _, _, n in aufbau.teile[kennung].nachweise], loesung.urteile)}


def urteile(nachweise: Sequence[Nachweis],
            alle: Sequence[NachweisUrteil]) -> Dict[str, Dict[str, str]]:
    """
    Je Pfeiler und Sturzauflager («O1 links») das Urteil, das an ihm gilt:
    das ungünstigste über seine Nachweise und Kombinationen -- ein
    verfehltes vor einem offenen, ein offenes vor dem kleinsten Grad. Je Ort
    ``{zustand, grad, titel}``: ``zustand`` ist ``verfehlt``, ``offen``,
    ``erfuellt`` oder ``ohne`` -- keine Kombination wirkt dort ein --,
    ``titel`` sagt in Worten, welcher Nachweis in welcher Kombination.
    """
    stellen = {(n.id, s.name): s for n in nachweise for s in n.stellen}
    je_ort: Dict[str, List[Tuple[NachweisUrteil, Stelle]]] = {}
    for u in alle:
        s = stellen.get((u.raum, u.fall))
        if s is not None:
            je_ort.setdefault(s.ort, []).append((u, s))
    return {ort: _massgebend(liste) for ort, liste in je_ort.items()}


def _massgebend(liste: Sequence[Tuple[NachweisUrteil, Stelle]]) -> Dict[str, str]:
    """Das Urteil, das an einem Ort gilt -- siehe :func:`urteile`."""
    u, s = min(liste, key=lambda e: (0 if e[0].verfehlt else 1 if e[0].offen else 2,
                                      e[0].erfuellungsgrad.si))
    if not u.offen and not math.isfinite(u.erfuellungsgrad.si):
        return {"zustand": "ohne", "grad": "", "titel": OHNE_EINWIRKUNG}
    return {"zustand": "verfehlt" if u.verfehlt else "offen" if u.offen else "erfuellt",
            "grad": u.gradtext(),
            "titel": f"{u.langname} – {s.kombination}: {u.urteilswort}, {u.gradtext()}"}


def uebersicht(befund: Optional[Wandbefund]) -> Dict[str, Any]:
    """
    ``bereit``: ob die Wand rechnet; ``meldungen`` alle je ``{text,
    elemente, fehler, unfertig}``, ``zum_mauerwerk`` die zu Mauerwerk und
    Dicke darunter noch einmal; ``pfeiler`` je ``{name, x0, x1, y0, y1, b}``
    und ``stuerze`` je ``{oeffnung, sturz, x0, y0, x1, y1}`` in m -- leer,
    solange die Zeichnung nicht rechnet. Ohne Befund ist alles leer.
    """
    if befund is None:
        return {"bereit": False, "meldungen": [], "zum_mauerwerk": [], "pfeiler": [], "stuerze": []}
    return {
        "bereit": befund.bereit,
        "meldungen": [m.als_dict() for m in befund.alle_meldungen],
        "zum_mauerwerk": [m.als_dict() for m in befund.zum_mauerwerk],
        "pfeiler": [{"name": e.name, "x0": e.x0, "x1": e.x1, "y0": e.y0, "y1": e.y1, "b": e.b}
                    for e in befund.pfeiler],
        "stuerze": [{"oeffnung": o.name, "sturz": o.sturz.value, "x0": s.x0, "y0": s.y0,
                     "x1": s.x1, "y1": s.y1}
                    for o in befund.wand.oeffnungen
                    if befund.gezeichnet and (s := o.sturzflaeche()) is not None],
    }


def unfertig(grund: str) -> Dict[str, Any]:
    """
    Die Uebersicht einer Wand, die nicht rechnet, weil ihr etwas fehlt --
    ``grund`` ein Satzteil ohne Punkt: grau, kein Fehler (Benutzer, 2026-11-19).
    """
    meldung = Meldung(f"{satzanfang(grund)}.", fehler=False, unfertig=True)
    return {**uebersicht(None), "meldungen": [meldung.als_dict()], "urteile": {}}


def katalog() -> Dict[str, Any]:
    """
    Womit die Kennungen der Teile beginnen, je Liste, die Stellungen der
    Schalter -- wie gemauert, die Stossfugen, Kopf und Fuss, die Ränder links
    und rechts, die Art eines Sturzes -- und je Sorte die üblichen Dicken in mm.
    """
    def stellungen(wahl) -> list:
        return [{"wert": w.value, "beschriftung": w.beschriftung, "titel": w.erklaerung}
                for w in wahl]

    return {"vorsilben": dict(VORSILBEN), "mauerung": stellungen(Mauerung),
            "stossfugen": stellungen(Stossfugen), "halterung": stellungen(Halterung),
            "seitenrand": stellungen(Seitenrand), "sturz": stellungen(Sturzart),
            "dicken": {sorte: list(dicken) for sorte, dicken in UEBLICHE_DICKEN.items()}}
