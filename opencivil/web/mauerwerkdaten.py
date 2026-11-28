"""
opencivil/web/mauerwerkdaten.py -- was die Oberflaeche von einer Wand aus Mauerwerk zeichnet.

VERANTWORTUNG:
Aus dem Befund einer Wand die Daten ihrer Zeichnung (:func:`uebersicht`):
ihre Meldungen -- die zu Mauerwerk und Dicke auch fuer sich, fuer die
Kachel der Maske --, ob sie rechnet, ihre Pfeiler und je Oeffnung die
Flaeche ihres Sturzes -- der Kern weiss, wie weit er aufliegt; die Seite zeichnet
ihn nur. Dazu der Teil des Katalogs, den nur die Wand braucht
(:func:`katalog`). Umriss und Oeffnungen zeichnet die Oberflaeche nach dem
Projekt.

EINHEITEN:
In m, wie im Zeichenfenster; die ueblichen Dicken in mm, wie das Feld.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from opencivil.core.rechenwerk import Loesung
from opencivil.core.sprache import satzanfang
from opencivil.mauerwerk.kennwerte import quelle
from opencivil.mauerwerk.modell import Halterung, Mauerung, Seitenrand, Stossfugen, Sturzart
from opencivil.mauerwerk.pruefen import UEBLICHE_DICKEN
from opencivil.mauerwerk.werk import Wandbefund
from opencivil.projekt import Aufbau
from opencivil.projekt.mauerwerk import VORSILBEN
from opencivil.stabwerk.system import Meldung

#: Was die Zusammenfassung von den Bemessungswerten zeigt: Kurzname, Zeichen, Stellen.
WERTE = (("f_xd", "f_xd", 2), ("f_yd", "f_yd", 2), ("E_xd", "E_xd", 0), ("G_d", "G_d", 0),
         ("mu_d", "μ_d", 2))


def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """Was die Zeichnung einer Wand unter ihre Teile legt -- auch wenn sie nicht rechnet."""
    return uebersicht(loesung.befunde.get(aufbau.mauerwerke[kennung].rechnung.id))


def uebersicht(befund: Optional[Wandbefund]) -> Dict[str, Any]:
    """
    ``bereit``: ob die Wand rechnet; ``werte`` ihre Bemessungswerte
    (:func:`_werte`); ``meldungen`` alle je ``{text,
    elemente, fehler, unfertig}``, ``zum_mauerwerk`` die zu Mauerwerk und
    Dicke darunter noch einmal; ``pfeiler`` je ``{name, x0, x1, y0, y1, b}``
    und ``stuerze`` je ``{oeffnung, sturz, x0, y0, x1, y1}`` in m -- leer,
    solange die Zeichnung nicht rechnet. Ohne Befund ist alles leer.
    """
    if befund is None:
        return {"bereit": False, "meldungen": [], "zum_mauerwerk": [], "pfeiler": [], "stuerze": [],
                "werte": None}
    return {
        "bereit": befund.bereit,
        "werte": _werte(befund),
        "meldungen": [m.als_dict() for m in befund.alle_meldungen],
        "zum_mauerwerk": [m.als_dict() for m in befund.zum_mauerwerk],
        "pfeiler": [{"name": e.name, "x0": e.x0, "x1": e.x1, "y0": e.y0, "y1": e.y1, "b": e.b}
                    for e in befund.pfeiler],
        "stuerze": [{"oeffnung": o.name, "sturz": o.sturz.value, "x0": s.x0, "y0": s.y0,
                     "x1": s.x1, "y1": s.y1}
                    for o in befund.wand.oeffnungen
                    if befund.gezeichnet and (s := o.sturzflaeche()) is not None],
    }


def _werte(befund: Wandbefund) -> Dict[str, Any]:
    """
    Die Bemessungswerte: der Name des Mauerwerks, der Faktor des Verbands und
    je Wert ``{zeichen, mauerwerk, wand, stellen}`` -- der des Mauerwerks und
    der, mit dem die Wand rechnet, in N/mm², ``mu_d`` ohne Einheit.
    """
    vollfugig = befund.wand.vollfugig
    return {"mauerwerk": befund.mauerwerk, "faktor": befund.werte.faktor, "zeilen": [
        {"zeichen": zeichen if quelle(kurz, vollfugig) == kurz else f"{zeichen}, vollfugig",
         "mauerwerk": befund.material[quelle(kurz, vollfugig)], "wand": getattr(befund.werte, kurz),
         "stellen": stellen}
        for kurz, zeichen, stellen in WERTE]}


def unfertig(grund: str) -> Dict[str, Any]:
    """
    Die Uebersicht einer Wand, die nicht rechnet, weil ihr etwas fehlt --
    ``grund`` ein Satzteil ohne Punkt: grau, kein Fehler (Benutzer, 2026-11-19).
    """
    meldung = Meldung(f"{satzanfang(grund)}.", fehler=False, unfertig=True)
    return {**uebersicht(None), "meldungen": [meldung.als_dict()]}


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
