"""
opencivil/projekt/frueher.py -- was eine Projektdatei von frueher anders schreibt.

VERANTWORTUNG:
Alte Speicherstaende muessen nicht weiter gehen (Benutzer, 2026-10-11). Wo
sich eine alte Angabe ohne Rueckfrage in die neue Form bringen laesst und
dasselbe rechnet, liest das Projekt sie trotzdem
(:meth:`~opencivil.projekt.projekt.Projekt.aus_dict`): vor dem strengen
Lesen nimmt es sie heraus, danach setzt es sie in der neuen Form ein -- mit
denselben Methoden, mit denen man ein Projekt in Python baut.

DAS WASSER (2026-11-27):
Bis dahin hatten Grundbruch und Pfahl je eine Zahl ``gamma_w``, die Raumlast
des Grundwassers, mit 10 kN/m³ als Vorgabe. Seither waehlen sie eine
Fluessigkeit aus den Materialien (``wasser``, :mod:`opencivil.material.fluessigkeit`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Tuple

from opencivil.material.basis import ERDBESCHLEUNIGUNG, Baustoffart
from opencivil.material.fluessigkeit import ERSTE_FLUESSIGKEIT, FLUESSIGKEITSSORTEN

if TYPE_CHECKING:
    from opencivil.projekt.projekt import Projekt

#: Die Listen, deren Eintraege bis 2026-11-27 ein ``gamma_w`` hatten.
_MIT_WASSER = ("grundbrueche", "pfaehle")

#: Wo ein Eintrag mit einer alten Zahl stand: Liste, Stelle, Zahl in kN/m³.
Alt = Tuple[str, int, float]


def gamma_w_heraus(roh: Any) -> Tuple[Any, List[Alt]]:
    """
    ``roh`` ohne die Zahlen ``gamma_w``, dazu je Eintrag, der eine hatte, wo
    er steht und welche. Was keine Zahl ist, bleibt stehen und meldet sich
    beim Lesen.
    """
    alte: List[Alt] = []
    if not isinstance(roh, Mapping):
        return roh, alte
    neu: Dict[str, Any] = dict(roh)
    for liste in _MIT_WASSER:
        eintraege = roh.get(liste)
        if not isinstance(eintraege, list):
            continue
        neu[liste] = []
        for i, e in enumerate(eintraege):
            if _alt(e):
                alte.append((liste, i, float(e["gamma_w"])))
                e = {k: v for k, v in e.items() if k != "gamma_w"}
            neu[liste].append(e)
    return (neu if alte else roh), alte


def wasser_einsetzen(projekt: "Projekt", alte: List[Alt]) -> None:
    """
    Je Zahl eine Fluessigkeit, die so viel wiegt: zu 10 kN/m³, der Vorgabe
    von damals, das Wasser -- das des Projekts, wenn es schon eines hat --,
    zu einer anderen eine eigene Fluessigkeit mit der Dichte dazu. Jeder
    Eintrag nimmt die seine; so rechnet die Datei wie zuvor.
    """
    wasser = FLUESSIGKEITSSORTEN[ERSTE_FLUESSIGKEIT].rho_fl
    je_zahl: Dict[float, str] = {}
    for liste, i, zahl in alte:
        if zahl not in je_zahl:
            dichte = round(zahl * 1000.0 / ERDBESCHLEUNIGUNG.si, 6)
            if dichte == wasser:
                da = next((m for m in projekt.materialien
                           if m.art is Baustoffart.FLUESSIGKEIT and m.ist_normsorte
                           and m.sorte == ERSTE_FLUESSIGKEIT), None)
                da = da or projekt.fluessigkeit(ERSTE_FLUESSIGKEIT)
            else:
                da = projekt.eigene_fluessigkeit(ERSTE_FLUESSIGKEIT)
                da.abweichungen["rho_fl"] = dichte
            je_zahl[zahl] = da.kennung
        getattr(projekt, liste)[i].wasser = je_zahl[zahl]


def _alt(eintrag: Any) -> bool:
    """Ob ein Eintrag noch eine Zahl ``gamma_w`` hat und keine Fluessigkeit."""
    if not isinstance(eintrag, Mapping) or "wasser" in eintrag:
        return False
    zahl = eintrag.get("gamma_w")
    return isinstance(zahl, (int, float)) and not isinstance(zahl, bool)
