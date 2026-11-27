"""
opencivil/web/deckendaten.py -- was die Oberflaeche von einer Decke zeichnet.

VERANTWORTUNG:
Aus dem Befund einer Decke die Daten ihrer Bilder, in m. In der
Streifenmethode: wie die Last auf die zwei Richtungen geht -- je Zelle der
automatischen Aufteilung, je Platte bei fester, und in den Zonen --, wo die
Grenzen der Streifen verlaufen, die Flaechen der Traeger und die
Stuetzenbereiche. In der FEM: das Netz und die Flaechen der Traeger. In
beiden die Meldungen -- die der Decke und je Lastfall und Kombination die
eigenen, samt Last und Lagerkraft, auch je Lager.

Auf Anfrage die Bilder eines Falls (:func:`ergebnis`): die Momente und
Querkraefte -- in der FEM auch die Durchbiegung -- in Zellen ueber die
Platten, je Zelle mit ihrem Gefaelle, ihre groessten Werte mit Ort, die
Kraft jeder Stuetze, der Verlauf laengs jedes Linienlagers, der laengs
jedes Schnitts und der jedes Traegers -- dieser ganz, nicht je Meter. Die
Zellen sind gross; mit jeder Rechnung mitgeliefert, machten sie jede
Eingabe langsamer -- dasselbe wie beim Verlauf des Balkensystems.

Was in eine Rechnung eingeht, rechnet hier niemand: Zellen, Werte und
groesste Werte kommen je Verfahren (:data:`_BILDER`) von derselben Stelle,
an der auch der Bericht sie holt -- in der Streifenmethode aus
:mod:`opencivil.decke.feld` und :mod:`opencivil.decke.schnitt`, in der FEM
aus :mod:`opencivil.decke.fem.auswertung`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from opencivil.core.einheiten import KN, KN_PRO_M, KNM, KNM_PRO_M, MM
from opencivil.core.rechenwerk import Loesung
from opencivil.decke import feld, schnitt
from opencivil.decke.baender import art
from opencivil.decke import geometrie as geo
from opencivil.decke.fem import auswertung
from opencivil.decke.fem.rechnung import GROESSEN as FEMGROESSEN
from opencivil.decke.fem.rechnung import Femergebnis
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Aufteilung, Linienlager, Verfahren
from opencivil.decke.rechnung import Ergebnis, Fall, Faelle, spitzen
from opencivil.decke.werk import Deckenbefund
from opencivil.projekt import Aufbau
from opencivil.stabwerk.system import Meldung
from opencivil.web.anzeige import zahl

#: Auf einen Zehntelmillimeter -- fuers Bild genug, und die Antwort bleibt klein.
STELLEN = 4

#: Die Einheit der Anzeige je Groesse: Momente der Platte in kNm/m, Querkraefte
#: in kN/m, die Durchbiegung in mm -- die eines ganzen Trägers in kNm und kN.
EINHEITEN = {**{g: KNM_PRO_M if g.startswith("m") else KN_PRO_M for g in feld.GROESSEN},
             "w": MM, "M": KNM, "V": KN}


def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """Was die Zeichnung einer Decke unter ihre Teile legt -- auch wenn sie nicht rechnet."""
    return uebersicht(loesung.befunde.get(aufbau.decken[kennung].rechnung.id))


def _punkte(ecken: Sequence[Tuple[float, float]]) -> List[List[float]]:
    return [[round(x, STELLEN), round(y, STELLEN)] for x, y in ecken]


def uebersicht(befund: Optional[Deckenbefund]) -> Dict[str, Any]:
    """
    ``gerechnet`` und ``meldungen`` (``{text, elemente, fehler}``) immer,
    mit einem Befund auch das ``verfahren``, nach dem er rechnete. Was die
    Decke je Verfahren dazu zeichnet, sagen :func:`_streifen` und
    :func:`_fem`; wenn sie rechnete, in beiden ``faelle``: je Lastfall und
    Kombination ``name``, die Last ``summe``, was davon ``daneben`` liegt
    und ``nicht_getragen`` wird, und was die ``lager`` tragen, in kN, auch
    ``je_lager`` (:func:`_je_lager`) -- und seine ``meldungen``;
    ``fallmeldungen`` sind dieselben, jede einmal, vorn ihre Faelle
    (:meth:`~opencivil.decke.rechnung.Faelle.fallmeldungen`). Die Zonen und
    Lasten zeichnet die Oberflaeche nach dem Projekt.
    """
    if befund is None:
        return {"gerechnet": False, "meldungen": []}
    heraus = {"gerechnet": False, "meldungen": _meldungen(befund.meldungen),
              "verfahren": befund.gerechnet.verfahren.value}
    e = befund.ergebnis
    if e is not None:
        heraus.update(_BILDER[befund.gerechnet.verfahren].uebersicht(e))
    if heraus["gerechnet"]:
        heraus.update(_faelle(e))
    return heraus


def _streifen(e: Ergebnis) -> Dict[str, Any]:
    """
    In der Streifenmethode ``von_selbst``: je Platte, die ihre Richtungen
    selbst wählt, die zwei in Grad gegen x; wenn die Decke in Streifen
    zerfiel, ``gerechnet`` und dazu ``richtungen``, ``anteile`` (Vieleck und
    Anteil in Richtung 1, in % -- ``None``, wo keine Richtung trägt),
    ``grenzen`` (je Grenze zweier Streifen eine Strecke), ``traeger`` -- die
    des Benutzers --, ``baender`` -- die die Rechnung selbst legte, mit
    ``achse``, ``art`` und ``breite`` in m -- und ``stuetzenbereiche``.
    """
    heraus: Dict[str, Any] = {"von_selbst": {p.name: [round(math.degrees(w), 6) for w in p.richtungen]
                                             for p in e.decke.platten if p.von_selbst}}
    if e.aufteilungen is None:
        return heraus
    z = e.zerlegung
    return {
        **heraus,
        "gerechnet": True,
        "richtungen": [{"name": r.name, "streifen": len(z.feldstreifen(r))} for r in z.richtungen],
        "anteile": [{"ecken": _punkte(ecken), "anteil": None if wert is None else round(100.0 * wert, 6)}
                    for ecken, wert in _anteile(e)],
        "grenzen": _grenzen(e),
        "traeger": [{"name": u.name, "ecken": _punkte(u.gebiet)} for u in z.traeger
                    if not u.traeger.von_selbst],
        "baender": [{"name": u.name, "ecken": _punkte(u.gebiet), "achse": _punkte([u.traeger.a, u.traeger.b]),
                     "art": art(u.traeger), "breite": round(u.traeger.breite, STELLEN)}
                    for u in z.traeger if u.traeger.von_selbst],
        "stuetzenbereiche": [{"name": name, "ecken": _punkte(ecken)}
                             for name, ecken in z.stuetzenbereiche.items()],
    }


def _fem(e: Femergebnis) -> Dict[str, Any]:
    """
    In der FEM, wenn ein Netz entstand, ``gerechnet`` und dazu das ``netz``
    -- seine ``weite`` und seine ``knoten`` in m, seine ``dreiecke``, je
    drei Nummern von Knoten -- und die ``traeger``, je die Flaeche ihrer
    Breite.
    """
    if e.netz is None:
        return {}
    return {
        "gerechnet": True,
        "netz": {"weite": e.netz.weite, "knoten": _punkte(e.netz.knoten),
                 "dreiecke": [list(d) for d in e.netz.dreiecke]},
        "traeger": [{"name": u.name, "ecken": _punkte(geo.rechteck(u.a, u.b, u.breite))}
                    for u in e.decke.traeger],
    }


def _faelle(e: Faelle) -> Dict[str, Any]:
    return {
        "faelle": [{"name": f.name, "summe": zahl(f.summe, KN), "daneben": zahl(f.daneben, KN),
                    "nicht_getragen": zahl(f.nicht_getragen, KN), "lager": zahl(f.lagerkraft, KN),
                    "je_lager": _je_lager(e, f), "meldungen": _meldungen(f.meldungen)}
                   for f in e.faelle],
        "fallmeldungen": _meldungen(e.fallmeldungen()),
    }


def verfahren_von(groesse: str) -> List[str]:
    """
    Die Verfahren, deren Bilder ``groesse`` zeigen: eine Groesse der Platte
    die, die sie rechnen -- die Lagerkraefte, M und V jedes.
    """
    platte = {g for b in _BILDER.values() for g in b.groessen}
    return [v.value for v, b in _BILDER.items() if groesse in b.groessen or groesse not in platte]


def faelle(befund: Optional[Deckenbefund]) -> List[str]:
    """Die Namen der gerechneten Faelle, Lastfaelle zuerst -- leer, wenn die Decke nicht rechnet."""
    e = befund.ergebnis if befund is not None else None
    return [f.name for f in e.faelle] if e is not None else []


def _je_lager(e: Faelle, f: Fall) -> List[Dict[str, Any]]:
    """Was jedes Lager traegt, in kN: jede Stuetze, jedes Linienlager -- auch, was nichts traegt."""
    return ([{"name": s.name, "art": "stuetze", "F": zahl(f.stuetzenkraft(s.name), KN)}
             for s in e.decke.stuetzen]
            + [{"name": l.name, "art": "linienlager", "F": zahl(f.wandkraft(l.name), KN)}
               for l in e.decke.linienlager])


def ergebnis(befund: Deckenbefund, name: str,
             schnitte: Sequence[Tuple[str, Punkt, Punkt]] = ()) -> Dict[str, Any]:
    """
    Die Bilder des Falls ``name``, Lastfall oder Kombination, nach dem
    Verfahren der Decke (:data:`_BILDER`): ``zellen``, je Zelle ihre Ecken,
    ``mitten``, je Zelle ihr Schwerpunkt, und ``werte``, je Groesse des
    Verfahrens der Wert dort; ``gefaelle``, je Groesse und Zelle
    ``[∂/∂x, ∂/∂y]`` in ihrer Einheit je m -- damit verlaeuft die Farbe ueber
    die Zelle; ``extreme``, je Groesse der groesste und der kleinste Wert mit
    seinem Ort -- gesucht an den Proben des Bilds
    (:class:`~opencivil.decke.feld.Bild`). Dazu je Stuetze ihre Kraft ``F``,
    je Linienlager, was :func:`_linienlager` sagt, je der ``schnitte`` --
    ``(Kennung, a, b)`` -- und je Traeger, was :func:`_verlauf` sagt.
    Momente in kNm/m, Querkraefte und ``r`` in kN/m, die Durchbiegung in
    mm, Kraefte in kN, die eines Traegers in kNm und kN -- wie
    ``einheiten`` sagt.
    """
    e = befund.ergebnis
    verfahren = _BILDER[befund.gerechnet.verfahren]
    groessen = verfahren.groessen
    fall = e.fall(name)
    bild = verfahren.bild(e, fall)
    return {
        "fall": name,
        "einheiten": {g: einheit.beschriftung for g, einheit in EINHEITEN.items()},
        "zellen": [_punkte(z) for z in bild.zellen],
        "mitten": _punkte([p for p, _ in bild.mitten]),
        "werte": {g: [_wert(k.groesse(g), g) for _, k in bild.mitten] for g in groessen},
        # Je m gerechnet wie die Groesse selbst: dieselbe Umrechnung. Null als
        # 0, nicht 0.0 oder -0.0 -- quer zu seinem Streifen hat fast jedes
        # Gefaelle eine, und die Antwort bleibt kleiner.
        "gefaelle": {g: [[_wert(f[g][0], g) or 0, _wert(f[g][1], g) or 0] for f in bild.gefaelle]
                     for g in groessen},
        "extreme": {g: _extreme(bild.proben, g) for g in groessen} if bild.proben else {},
        "stuetzen": [{"name": s.name, "F": zahl(fall.stuetzenkraft(s.name), KN)} for s in e.decke.stuetzen],
        "linienlager": [_linienlager(l, fall) for l in e.decke.linienlager],
        "schnitte": [_verlauf(verfahren.verlauf(e, fall, a, b), kennung, a, b, groessen)
                     for kennung, a, b in schnitte],
        "traeger": [_verlauf(v, kennung, a, b, schnitt.BALKENGROESSEN)
                    for kennung, a, b, v in verfahren.traeger(e, fall)],
    }


@dataclass(frozen=True)
class _Verfahren:
    """
    Woher die Bilder eines Verfahrens kommen: welche ``groessen`` sie
    zeigen, was die Uebersicht zeichnet, das Bild der Platte in einem Fall,
    der Verlauf laengs eines Schnitts und je Traeger ``(Name, a, b,
    Verlauf)``.
    """

    groessen: Sequence[str]
    uebersicht: Callable[[Any], Dict[str, Any]]
    bild: Callable[[Any, Any], feld.Bild]
    verlauf: Callable[[Any, Any, Punkt, Punkt], schnitt.Verlauf]
    traeger: Callable[[Any, Any], List[Tuple[str, Punkt, Punkt, schnitt.Verlauf]]]


#: Je Verfahren der Decke, woher ihre Bilder kommen -- einmal gewaehlt, je Anfrage.
_BILDER = {
    Verfahren.STREIFEN: _Verfahren(
        tuple(feld.GROESSEN), _streifen, feld.bild, schnitt.verlauf,
        lambda e, fall: [(u.name, u.traeger.a, u.traeger.b, schnitt.traeger(fall, u)) for u in e.zerlegung.traeger]),
    Verfahren.FEM: _Verfahren(
        tuple(FEMGROESSEN), _fem, auswertung.bild, auswertung.verlauf,
        lambda e, fall: [(u.name, u.a, u.b, auswertung.traeger(e, fall, u)) for u in e.decke.traeger]),
}


def _verlauf(v: schnitt.Verlauf, kennung: str, a: Punkt, b: Punkt,
             groessen: Sequence[str]) -> Dict[str, Any]:
    """
    Ein Schnitt oder ein Traeger im Bild eines Falls, alles in m ab ``a``:
    seine Enden ``a`` und ``b``, seine Laenge ``L``, wo er in einer Platte
    liegt (``stuecke``), die ``stellen``, an denen er hinsieht, und je der
    ``groessen`` die ``werte`` dort und die ``extreme`` mit Stelle ``u``;
    die ``lager``, die er kreuzt oder auf denen er liegt, und die
    ``traeger``. Zwei Stellen eines Sprungs fallen in der Rundung
    zusammen -- im Bild steht er senkrecht.
    """
    return {
        "kennung": kennung, "a": _punkte([a])[0], "b": _punkte([b])[0], "L": round(v.L, STELLEN),
        "stuecke": [[round(u0, STELLEN), round(u1, STELLEN)] for u0, u1 in v.stuecke],
        "stellen": [round(u, STELLEN) for u, _ in v.proben],
        "werte": {g: [_wert(k.groesse(g), g) for _, k in v.proben] for g in groessen},
        "extreme": {g: {art: {"wert": _wert(w, g), "u": round(u, STELLEN)}
                        for art, (u, w) in zip(("kleinst", "groesst"), v.extreme(g))}
                    for g in groessen} if v.proben else {},
        "lager": [{"u": round(l.u, STELLEN), "art": l.art, "name": l.name, "vertikal": l.vertikal,
                   "eingespannt": l.eingespannt} for l in v.lager],
        "traeger": [{"von": round(u0, STELLEN), "bis": round(u1, STELLEN), "name": name}
                    for u0, u1, name in v.traeger],
    }


def _linienlager(lager: Linienlager, fall: Fall) -> Dict[str, Any]:
    """
    Ein Linienlager im Bild eines Falls: seine Summe ``F``, seine Stufen
    ``[u_a, u_b, r, m]`` (:meth:`~opencivil.decke.rechnung.Fall.lagerstufen`),
    ``r_max`` und ``m_max`` (:func:`~opencivil.decke.rechnung.spitzen`).
    """
    stufen = fall.lagerstufen(lager)
    r_max, m_max = spitzen(stufen)
    return {"name": lager.name, "a": _punkte([lager.a])[0], "b": _punkte([lager.b])[0],
            "eingespannt": lager.eingespannt, "F": zahl(fall.wandkraft(lager.name), KN),
            "stufen": [[round(ua, STELLEN), round(ub, STELLEN), zahl(r, KN_PRO_M), zahl(m, KNM_PRO_M)]
                       for ua, ub, r, m in stufen],
            "r_max": zahl(r_max, KN_PRO_M), "m_max": zahl(m_max, KNM_PRO_M)}


def _wert(si: float, groesse: str) -> float:
    return round(zahl(si, EINHEITEN[groesse]), 3)


def _extreme(proben: Sequence[feld.Probe], groesse: str) -> Dict[str, Any]:
    """Der groesste und der kleinste Wert einer Groesse unter den Proben, je mit Ort."""
    kleinst, groesst = feld.extrem(proben, lambda k: k.groesse(groesse))
    return {art: {"wert": _wert(w, groesse), "ort": _punkte([ort])[0]}
            for art, (ort, w) in (("groesst", groesst), ("kleinst", kleinst))}


def _meldungen(meldungen: Sequence[Meldung]) -> List[Dict[str, Any]]:
    return [m.als_dict() for m in meldungen]


def _anteile(e: Ergebnis) -> List[Tuple[Sequence[Tuple[float, float]], Optional[float]]]:
    """Automatisch die Zellen der Aufteilung, fest jede Platte mit dem Anteil der Decke."""
    if e.decke.aufteilung is Aufteilung.FEST:
        return [(p.ecken, e.decke.anteil) for p in e.decke.platten]
    return list(e.aufteilungen.zellen)


def _grenzen(e: Ergebnis) -> List[Dict[str, Any]]:
    """
    Je Richtung jeder Platte die Grenzen ihrer Feldstreifen, als Strecken
    in der Platte -- in einem L zwei, wo die Grenze die Ecke quert.
    """
    heraus: List[Dict[str, Any]] = []
    z = e.zerlegung
    for gruppe in z.gruppen:
        for nummer, r in enumerate(gruppe.richtungen, start=1):
            grenzen = sorted({round(t, 9) for s in z.feldstreifen(r) for t in (s.von, s.bis)})
            for platte in gruppe.platten:
                lo, hi = geo.bereich(platte.ecken, r.n)
                for tau in grenzen:
                    a, b = r.punkt(lo - 1.0, tau), r.punkt(hi + 1.0, tau)
                    for u0, u1 in geo.strecke_im_vieleck(a, b, list(platte.ecken)):
                        if u1 - u0 <= geo.TOLERANZ:
                            continue
                        heraus.append({"richtung": nummer, "punkte": _punkte(
                            [(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u) for u in (u0, u1)])})
    return heraus
