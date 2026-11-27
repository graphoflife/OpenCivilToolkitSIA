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

DIE SPANNUNGEN DER SPANNGLIEDER (2026-11-27):
Bis dahin hatte ein Spannglied die Spannungen ``sigma_p0`` und
``sigma_pinf`` in N/mm², leer die Vorgabe. Seither die Faktoren
``anteil_p0`` und ``anteil_pinf`` (:mod:`opencivil.projekt.spannglieder`).
Eine leere Spannung wird die Vorgabe ihres Faktors, eine Zahl der Faktor,
der sie ergibt -- mit f_pk des Spannstahls, wie die Datei ihn nennt
(:func:`spannungen_als_faktoren`). So rechnet das Glied wie zuvor, auch wo
der Faktor dann 0.7258… heisst.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Tuple

from opencivil.material.basis import ERDBESCHLEUNIGUNG, Baustoffart
from opencivil.material.fluessigkeit import ERSTE_FLUESSIGKEIT, FLUESSIGKEITSSORTEN
from opencivil.material.spannstahl import SPANNSTAHLSORTEN
from opencivil.querschnitt.spannglieder import ANTEIL_SPANNEN

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
    return _zahl(eintrag.get("gamma_w"))


def _zahl(wert: Any) -> bool:
    return isinstance(wert, (int, float)) and not isinstance(wert, bool)


#: Was ein Spannglied bis 2026-11-27 statt seiner Faktoren hatte.
_SPANNUNGEN = ("sigma_p0", "sigma_pinf")


def spannungen_als_faktoren(roh: Any) -> Any:
    """
    ``roh`` mit Faktoren statt der Spannungen der Spannglieder -- siehe
    Dateikopf. Was sich nicht umrechnen laesst, weil der Spannstahl fehlt
    oder eine Spannung keine Zahl ist, bleibt stehen und meldet sich beim
    Lesen.
    """
    if not isinstance(roh, Mapping) or not isinstance(roh.get("querschnittsanalysen"), list):
        return roh
    f_pk = _zugfestigkeiten(roh.get("materialien"))
    analysen = []
    for a in roh["querschnittsanalysen"]:
        glieder = a.get("spannglieder") if isinstance(a, Mapping) else None
        if isinstance(glieder, list):
            a = {**a, "spannglieder": [_faktoren(g, f_pk) for g in glieder]}
        analysen.append(a)
    return {**roh, "querschnittsanalysen": analysen}


def _zugfestigkeiten(materialien: Any) -> Dict[str, float]:
    """Je Spannstahl der Datei sein f_pk in N/mm²: ueberschrieben, abgewichen oder der Sorte."""
    heraus: Dict[str, float] = {}
    for m in materialien if isinstance(materialien, list) else []:
        if not isinstance(m, Mapping) or m.get("art") != Baustoffart.SPANNSTAHL.value:
            continue
        sorte = SPANNSTAHLSORTEN.get(m.get("sorte"))
        zahlen = [d.get("f_pk") for d in (m.get("ueberschreibungen"), m.get("abweichungen"))
                  if isinstance(d, Mapping)]
        zahlen += [sorte.f_pk] if sorte is not None else []
        gefunden = next((z for z in zahlen if _zahl(z)), None)
        if gefunden is not None:
            heraus[m.get("kennung")] = float(gefunden)
    return heraus


def _faktoren(glied: Any, f_pk: Mapping[str, float]) -> Any:
    """Ein Glied mit Faktoren statt Spannungen -- ``glied`` selbst, wo das nicht geht."""
    if not isinstance(glied, Mapping) or not any(k in glied for k in _SPANNUNGEN):
        return glied
    p0, pinf = glied.get("sigma_p0"), glied.get("sigma_pinf")
    zug = f_pk.get(glied.get("stahl"))
    if not all(s is None or _zahl(s) for s in (p0, pinf)) or (
            zug is None and (p0, pinf) != (None, None)):
        return glied
    neu = {k: v for k, v in glied.items() if k not in _SPANNUNGEN}
    if p0 is not None:
        neu["anteil_p0"] = p0 / zug
    if pinf is not None:
        neu["anteil_pinf"] = pinf / (ANTEIL_SPANNEN * zug if p0 is None else p0)
    return neu
