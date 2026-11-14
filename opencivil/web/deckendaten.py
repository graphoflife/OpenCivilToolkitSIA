"""
opencivil/web/deckendaten.py -- was die Oberflaeche von einer Decke zeichnet.

VERANTWORTUNG:
Aus dem Befund einer Decke die Daten ihrer Bilder, in m: wie die Last auf
die zwei Richtungen geht -- je Zelle der automatischen Aufteilung, je
Platte bei fester, und in den Zonen --, wo die Grenzen der Streifen
verlaufen, die Flaechen der Unterzuege und die Stuetzenbereiche, dazu die
Meldungen -- die der Decke und je Lastfall und Kombination die eigenen,
samt Last und Lagerkraft, auch je Lager.

Auf Anfrage die Bilder eines Falls (:func:`ergebnis`): die Momente und
Querkraefte in Zellen ueber die Platten, ihre groessten Werte mit Ort, die
Kraft jeder Stuetze und der Verlauf laengs jedes Linienlagers. Die Zellen
sind gross; mit jeder Rechnung mitgeliefert, machten sie jede Eingabe
langsamer -- dasselbe wie beim Verlauf des Balkensystems.

Was in eine Rechnung eingeht, rechnet hier niemand; geschnitten wird nur
fuers Bild, und die Werte an einer Stelle kommen aus
:mod:`opencivil.decke.feld`.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from opencivil.core.einheiten import KN, KN_PRO_M, KNM_PRO_M
from opencivil.core.rechenwerk import Loesung
from opencivil.decke import feld
from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Aufteilung, Linienlager
from opencivil.decke.rechnung import Ergebnis, Fallergebnis, lagerverlauf
from opencivil.decke.werk import Deckenbefund
from opencivil.projekt import Aufbau
from opencivil.stabwerk.system import Meldung
from opencivil.web.anzeige import zahl

#: Auf einen Zehntelmillimeter -- fuers Bild genug, und die Antwort bleibt klein.
STELLEN = 4

#: So viele Zellen hat ein Bild der Schnittkraefte ueber die laengere Seite
#: der Decke mindestens -- breitere Streifen werden dafuer geteilt. Mehr
#: machten die Antwort gross: bei 40 waren es fuer die Decke des
#: Kolloquiums 4 (9 m, Streifen 0.25 m) 3168 Zellen und 330 kB.
ZELLEN = 24

#: Die Einheit der Anzeige je Groesse: Momente in kNm/m, Querkraefte in kN/m.
EINHEITEN = {g: KNM_PRO_M if g.startswith("m") else KN_PRO_M for g in feld.GROESSEN}


def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """Was die Zeichnung einer Decke unter ihre Teile legt -- auch wenn sie nicht rechnet."""
    return uebersicht(loesung.befunde.get(aufbau.decken[kennung].rechnung.id))


def _punkte(ecken: Sequence[Tuple[float, float]]) -> List[List[float]]:
    return [[round(x, STELLEN), round(y, STELLEN)] for x, y in ecken]


def uebersicht(befund: Optional[Deckenbefund]) -> Dict[str, Any]:
    """
    ``gerechnet`` und ``meldungen`` (``{text, elemente, fehler}``) immer;
    wenn die Decke in Streifen zerfiel, dazu ``richtungen``, ``anteile``
    (Vieleck und Anteil in Richtung 1, in %), ``grenzen`` (je Grenze
    zweier Streifen eine Strecke), ``unterzuege``, ``stuetzenbereiche`` und
    ``faelle``: je Lastfall und Kombination ``name``, die Last ``summe``,
    was davon ``daneben`` liegt und ``nicht_getragen`` wird, und was die
    ``lager`` tragen, in kN, auch ``je_lager`` (:func:`_je_lager`) -- und
    seine ``meldungen``. Die Zonen und Lasten zeichnet die Oberflaeche nach
    dem Projekt.
    """
    if befund is None:
        return {"gerechnet": False, "meldungen": []}
    meldungen = _meldungen(befund.meldungen)
    e = befund.ergebnis
    if e is None or e.aufteilungen is None:
        return {"gerechnet": False, "meldungen": meldungen}
    z = e.zerlegung
    return {
        "gerechnet": True,
        "meldungen": meldungen,
        "richtungen": [{"name": r.name, "streifen": len(z.feldstreifen(r))} for r in z.richtungen],
        "anteile": [{"ecken": _punkte(ecken), "anteil": round(100.0 * wert, 6)}
                    for ecken, wert in _anteile(e)],
        "grenzen": _grenzen(e),
        "unterzuege": [{"name": u.name, "ecken": _punkte(u.gebiet)} for u in z.unterzuege],
        "stuetzenbereiche": [{"name": name, "ecken": _punkte(ecken)}
                             for name, ecken in z.stuetzenbereiche.items()],
        "faelle": [{"name": f.name, "summe": zahl(f.summe, KN), "daneben": zahl(f.daneben, KN),
                    "nicht_getragen": zahl(f.nicht_getragen, KN), "lager": zahl(f.lagerkraft, KN),
                    "je_lager": _je_lager(e, f), "meldungen": _meldungen(f.meldungen)}
                   for f in e.faelle],
    }


def faelle(befund: Optional[Deckenbefund]) -> List[str]:
    """Die Namen der gerechneten Faelle, Lastfaelle zuerst -- leer, wenn die Decke nicht rechnet."""
    e = befund.ergebnis if befund is not None else None
    return [f.name for f in e.faelle] if e is not None else []


def _je_lager(e: Ergebnis, f: Fallergebnis) -> List[Dict[str, Any]]:
    """Was jedes Lager traegt, in kN: jede Stuetze, jedes Linienlager -- auch, was nichts traegt."""
    return ([{"name": s.name, "art": "stuetze", "F": zahl(f.stuetzenkraft(s.name), KN)}
             for s in e.decke.stuetzen]
            + [{"name": l.name, "art": "linienlager", "F": zahl(f.wandkraft(l.name), KN)}
               for l in e.decke.linienlager])


def ergebnis(befund: Deckenbefund, name: str) -> Dict[str, Any]:
    """
    Die Bilder des Falls ``name``, Lastfall oder Kombination: ``zellen``, je
    Zelle ihre Ecken, und ``werte``, je Groesse
    (:data:`~opencivil.decke.feld.GROESSEN`) der Wert am Schwerpunkt jeder
    Zelle; ``extreme``, je Groesse der groesste und der kleinste Wert mit
    seinem Ort -- gesucht unter den Schwerpunkten und den Stellen, an denen
    ein Traeger springt oder sein Extremum hat (:func:`~opencivil.decke.feld.stellen`).
    Dazu je Stuetze ihre Kraft ``F`` und je Linienlager, was
    :func:`_linienlager` sagt. Momente in kNm/m, Querkraefte und ``r`` in
    kN/m, Kraefte in kN -- wie ``einheiten`` sagt.
    """
    e = befund.ergebnis
    fall = e.fall(name)
    zellen = _zellen(e)
    mitten = [geo.schwerpunkt(z) for z in zellen]
    werte = [feld.an_stelle(e, fall, p) for p in mitten]
    platten = [list(p.ecken) for p in e.decke.platten]
    stellen = [p for p in feld.stellen(e, fall) if any(geo.innen(p, v) for v in platten)]
    proben = list(zip(mitten, werte)) + [(p, feld.an_stelle(e, fall, p)) for p in stellen]
    return {
        "fall": name,
        "einheiten": {g: EINHEITEN[g].beschriftung for g in feld.GROESSEN},
        "zellen": [_punkte(z) for z in zellen],
        "werte": {g: [_wert(k.groesse(g), g) for k in werte] for g in feld.GROESSEN},
        "extreme": {g: _extreme(proben, g) for g in feld.GROESSEN} if proben else {},
        "stuetzen": [{"name": s.name, "F": zahl(fall.stuetzenkraft(s.name), KN)} for s in e.decke.stuetzen],
        "linienlager": [_linienlager(l, fall) for l in e.decke.linienlager],
    }


def _linienlager(lager: Linienlager, fall: Fallergebnis) -> Dict[str, Any]:
    """
    Ein Linienlager im Bild eines Falls: seine Summe ``F``, seine Stufen
    ``[u_a, u_b, r, m]`` (:func:`~opencivil.decke.rechnung.lagerverlauf`),
    ``r_max``, der Wert von r mit dem groessten Betrag, und ``m_max``, der
    groesste Betrag von m -- nur der Betrag: das Vorzeichen von m haengt an
    der Richtung a -> b, die niemand sieht.
    """
    stufen = lagerverlauf(lager, fall.linienlager.get(lager.name, ()))
    return {"name": lager.name, "a": _punkte([lager.a])[0], "b": _punkte([lager.b])[0],
            "eingespannt": lager.eingespannt, "F": zahl(fall.wandkraft(lager.name), KN),
            "stufen": [[round(ua, STELLEN), round(ub, STELLEN), zahl(r, KN_PRO_M), zahl(m, KNM_PRO_M)]
                       for ua, ub, r, m in stufen],
            "r_max": zahl(max((r for _, _, r, _ in stufen), key=abs, default=0.0), KN_PRO_M),
            "m_max": zahl(max((abs(m) for *_, m in stufen), default=0.0), KNM_PRO_M)}


def _wert(si: float, groesse: str) -> float:
    return round(zahl(si, EINHEITEN[groesse]), 3)


def _extreme(proben: Sequence[Tuple[Punkt, feld.Schnittkraefte]], groesse: str) -> Dict[str, Any]:
    """Der groesste und der kleinste Wert einer Groesse unter den Proben, je mit Ort."""
    def eintrag(probe: Tuple[Punkt, feld.Schnittkraefte]) -> Dict[str, Any]:
        return {"wert": _wert(probe[1].groesse(groesse), groesse), "ort": _punkte([probe[0]])[0]}
    return {"groesst": eintrag(max(proben, key=lambda pk: pk[1].groesse(groesse))),
            "kleinst": eintrag(min(proben, key=lambda pk: pk[1].groesse(groesse)))}


def _zellen(e: Ergebnis) -> List[List[Punkt]]:
    """
    Die Zellen der Bilder: je Gruppe die Feldstreifen ihrer beiden
    Richtungen, die breiten geteilt (:data:`ZELLEN`), gekreuzt und mit den
    konvexen Stuecken ihrer Platten geschnitten. So liegt jede Zelle in
    einem Streifen jeder Richtung, und ihr Wert gilt fuer sie ganz.
    """
    z = e.zerlegung
    ecken = [p for platte in e.decke.platten for p in platte.ecken]
    weite = max(max(p[0] for p in ecken) - min(p[0] for p in ecken),
                max(p[1] for p in ecken) - min(p[1] for p in ecken)) / ZELLEN
    heraus: List[List[Punkt]] = []
    for gruppe in z.gruppen:
        r1, r2 = gruppe.richtungen
        baender1, baender2 = (_baender(z.feldstreifen(r), weite) for r in (r1, r2))
        for stueck in gruppe.stuecke:
            for a1, b1 in baender1:
                band = geo.im_band(stueck, r1.t, a1, b1)
                for a2, b2 in baender2 if band else ():
                    zelle = geo.im_band(band, r2.t, a2, b2)
                    if zelle:
                        heraus.append(zelle)
    return heraus


def _baender(streifen: Sequence[Any], weite: float) -> List[Tuple[float, float]]:
    """Die Feldstreifen einer Richtung quer in Baender, keines breiter als ``weite``."""
    heraus = []
    for s in streifen:
        n = max(1, math.ceil(s.breite / weite - 1e-9))
        heraus.extend((s.von + s.breite * i / n, s.von + s.breite * (i + 1) / n) for i in range(n))
    return heraus


def _meldungen(meldungen: Sequence[Meldung]) -> List[Dict[str, Any]]:
    return [{"text": m.text, "elemente": list(m.elemente), "fehler": m.fehler} for m in meldungen]


def _anteile(e: Ergebnis) -> List[Tuple[Sequence[Tuple[float, float]], float]]:
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
