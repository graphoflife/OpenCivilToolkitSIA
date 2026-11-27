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

DER UMRECHNUNGSFAKTOR EINES PFAHLS (2026-11-27):
Bis dahin war η_a eines Pfahls immer eine Zahl von Hand, Vorgabe 0.7.
Seither waehlt ein Schalter (``umrechnung``), ob η_a der Grenzwert der
Grundlage ist oder von Hand kommt; neu angelegt aus der Grundlage. Ein Pfahl
ohne den Schalter behaelt seine Zahl von Hand, wo sie vom Grenzwert
abweicht, sonst nimmt er den Grenzwert -- so rechnet er wie zuvor
(:func:`umrechnung_setzen`).

DIE WAENDE EINES GEBAEUDES (2026-11-27):
Bis dahin trug ein Gebaeude im Erdbeben Waende (``waende``): je eine
Querschnittsanalyse, ``n`` gleiche in der Lage 0 oder 90 Grad, mit ihrem
η_EI, ueber die ganze Hoehe; die Grundschwingzeit aus den Waenden hiess
``waende``. Seither nimmt jedes Geschoss einen Kern -- eine Analyse mit
allen Waenden, wie sie im Grundriss liegen -- und sein η_EI; die
Grundschwingzeit heisst ``kern`` (:mod:`opencivil.projekt.erdbeben`). Die
Waende werden ein Kern (:func:`kern_einsetzen`): eine neue Analyse, darin
jede Wand ``n`` mal, die in 90 Grad gedreht, nebeneinander und 1 m
auseinander. So bleiben sie getrennte Teile, jeder zaehlt um seinen eigenen
Schwerpunkt wie zuvor jede Wand, und das Gebaeude rechnet wie zuvor -- nur
zaehlt eine Analyse aus getrennten Polygonen nun auch je Teil, wie in jedem
Kern. Jedes Geschoss nimmt ihn mit dem η_EI der Waende. Waende ohne Analyse
fallen weg: sie trugen nichts bei. Verschiedene η_EI, eine Analyse, die es
nicht gibt, oder eine Wand, die sich nicht lesen laesst, gehen nicht ohne
Rueckfrage in einen Kern: die Datei meldet sich dann beim Lesen.
"""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, AbstractSet, Any, Dict, List, Mapping, Optional, Tuple

from opencivil.material.basis import ERDBESCHLEUNIGUNG, Baustoffart
from opencivil.material.fluessigkeit import ERSTE_FLUESSIGKEIT, FLUESSIGKEITSSORTEN
from opencivil.material.spannstahl import SPANNSTAHLSORTEN
from opencivil.pfahl.pfahl import Grundlage, Umrechnung
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
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


#: η_a eines Pfahls ohne Zahl in der Datei, bis 2026-11-27.
_ETA_A_BIS_DAHIN = 0.7


def umrechnung_setzen(roh: Any) -> Any:
    """``roh`` mit dem Schalter η_a an jedem Pfahl, der keinen hat -- siehe Dateikopf."""
    if not isinstance(roh, Mapping) or not isinstance(roh.get("pfaehle"), list):
        return roh
    return {**roh, "pfaehle": [_umrechnung(t) for t in roh["pfaehle"]]}


def _umrechnung(pfahl: Any) -> Any:
    """
    Ein Pfahl mit dem Schalter -- ``pfahl`` selbst, wo er ihn schon hat oder
    die Grundlage keine ist: das meldet dann das Lesen.
    """
    if not isinstance(pfahl, Mapping) or "umrechnung" in pfahl:
        return pfahl
    try:
        grenze = Grundlage(pfahl.get("grundlage", Grundlage.BERECHNUNG.value)).eta_grenze
    except ValueError:
        return pfahl
    eta = pfahl.get("eta_a", _ETA_A_BIS_DAHIN)
    wahl = Umrechnung.GRUNDLAGE if eta == grenze else Umrechnung.HAND
    return {**pfahl, "umrechnung": wahl.value, "eta_a": eta}


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


#: So weit liegen die Waende von frueher im Kern auseinander, in mm: sie
#: beruehren sich nicht und bleiben getrennte Teile.
_ABSTAND = 1000.0

#: Je Wand von frueher mit Analyse: deren Kennung, ob sie um 90 Grad gedreht
#: lag, und wie oft sie zaehlte.
Wand = Tuple[str, bool, int]

#: Ein Gebaeude mit Waenden von frueher: seine Stelle in der Liste und seine Waende.
Waende = Tuple[int, List[Wand]]


def waende_heraus(roh: Any) -> Tuple[Any, List[Waende]]:
    """
    ``roh`` ohne die Waende der Gebaeude, mit ``kern`` statt ``waende`` als
    Grundschwingzeit und dem η_EI der Waende in jedem Geschoss, dazu je
    Gebaeude mit Waenden, die eine Analyse haben, wo es steht und welche --
    siehe Dateikopf. Was sich nicht so lesen laesst, bleibt stehen und
    meldet sich beim Lesen.
    """
    if not isinstance(roh, Mapping) or not isinstance(roh.get("erdbeben"), list):
        return roh, []
    analysen = {a.get("kennung") for a in roh.get("querschnittsanalysen") or []
                if isinstance(a, Mapping)}
    alte: List[Waende] = []
    gebaeude = []
    for i, e in enumerate(roh["erdbeben"]):
        if isinstance(e, Mapping) and e.get("schwingzeit") == "waende":
            e = {**e, "schwingzeit": "kern"}
        gelesen = _waende(e, analysen)
        if gelesen is not None:
            eta, waende = gelesen
            e = {k: v for k, v in e.items() if k != "waende"}
            if waende and isinstance(e.get("geschosse"), list):
                e["geschosse"] = [{**g, "eta_EI": eta} if isinstance(g, Mapping) else g
                                  for g in e["geschosse"]]
            if waende:
                alte.append((i, waende))
        gebaeude.append(e)
    return {**roh, "erdbeben": gebaeude}, alte


def _waende(gebaeude: Any, analysen: AbstractSet[Any]) -> Optional[Tuple[Any, List[Wand]]]:
    """
    Das gemeinsame η_EI der Waende eines Gebaeudes und je Wand mit Analyse,
    was der Kern von ihr braucht -- ``None``, wo es keine Waende hat oder
    sie nicht ohne Rueckfrage in einen Kern gehen.
    """
    waende = gebaeude.get("waende") if isinstance(gebaeude, Mapping) else None
    if not isinstance(waende, list) or not all(isinstance(w, Mapping) for w in waende):
        return None
    mit = [w for w in waende if w.get("analyse")]
    etas = [w.get("eta_EI", 0.5) for w in mit]
    anzahlen = [w.get("n", 1) for w in mit]
    if (not all(_zahl(eta) for eta in etas) or len(set(etas)) > 1
            or any(w["analyse"] not in analysen or w.get("lage", "0") not in ("0", "90")
                   for w in mit)
            or not all(_zahl(n) and n >= 1 and n == int(n) for n in anzahlen)):
        return None
    return (etas[0] if etas else None,
            [(w["analyse"], w.get("lage", "0") == "90", int(n)) for w, n in zip(mit, anzahlen)])


def kern_einsetzen(projekt: "Projekt", alte: List[Waende]) -> None:
    """
    Je Gebaeude mit Waenden von frueher ein Kern aus ihnen, den jedes
    Geschoss nimmt -- eine neue Analyse «Kern …» mit dem Namen des
    Gebaeudes, siehe Dateikopf.
    """
    for i, waende in alte:
        gebaeude = projekt.erdbeben[i]
        namen = {a.name for a in projekt.querschnittsanalysen}
        name = next(n for n in itertools.chain([f"Kern {gebaeude.name}"],
                                               (f"Kern {gebaeude.name} {k}"
                                                for k in itertools.count(2)))
                    if n not in namen)
        kern = QuerschnittsanalyseEintrag.neu(kennung=projekt.freie_kennung("a"), name=name)
        je_kennung = {a.kennung: a for a in projekt.querschnittsanalysen}
        links = 0.0
        for kennung, gedreht, n in waende:
            for _ in range(n):
                links = _kopieren(je_kennung[kennung], kern, gedreht, links) + _ABSTAND
        projekt.querschnittsanalysen.append(kern)
        for g in gebaeude.geschosse:
            g.kern = kern.kennung


def _kopieren(wand: QuerschnittsanalyseEintrag, kern: QuerschnittsanalyseEintrag,
              gedreht: bool, links: float) -> float:
    """
    Polygone, Staebe und Stablinien einer Wand in den Kern -- um 90 Grad
    gedreht, wo sie so lag, rechts von ``links`` und unten auf z = 0. Gibt
    zurueck, wo sie rechts endet, in mm.
    """
    orte = {k.kennung: ((-k.z, k.y) if gedreht else (k.y, k.z)) for k in wand.knoten}
    ecken = [orte[k] for f in wand.flaechen for k in f.knoten]
    if not ecken:
        return links
    dy, dz = links - min(y for y, _ in ecken), -min(z for _, z in ecken)

    def hin(knoten: str) -> List[float]:
        y, z = orte[knoten]
        return [y + dy, z + dz]

    for f in wand.flaechen:
        kern.polygon([hin(k) for k in f.knoten], material=f.material).ueberdeckung = f.ueberdeckung
    for s in wand.staebe:
        kern.stab(*hin(s.knoten), **_ohne(s.als_dict(), "knoten"))
    for linie in wand.stablinien:
        kern.stablinie(hin(linie.von), hin(linie.bis), **_ohne(linie.als_dict(), "von", "bis"))
    return max(y for y, _ in ecken) + dy


def _ohne(felder: Mapping[str, Any], *weg: str) -> Dict[str, Any]:
    """Die Felder eines Elements ohne seine Kennung und ohne ``weg``."""
    return {k: v for k, v in felder.items() if k not in ("kennung", *weg)}
