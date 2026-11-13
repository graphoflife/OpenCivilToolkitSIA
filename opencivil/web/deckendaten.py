"""
opencivil/web/deckendaten.py -- was die Oberflaeche von einer Decke zeichnet.

VERANTWORTUNG:
Aus dem Befund einer Decke die Daten ihrer Bilder, in m: wie die Last auf
die zwei Richtungen geht -- je Zelle der automatischen Aufteilung, je
Platte bei fester, und in den Zonen --, wo die Grenzen der Streifen
verlaufen, die Flaechen der Unterzuege und die Stuetzenbereiche, dazu die
Meldungen. Was in eine Rechnung eingeht, rechnet hier niemand; geschnitten
wird nur fuers Bild.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from opencivil.core.rechenwerk import Loesung
from opencivil.decke import geometrie as geo
from opencivil.decke.modell import Aufteilung
from opencivil.decke.rechnung import Ergebnis
from opencivil.decke.werk import Deckenbefund
from opencivil.projekt import Aufbau

#: Auf einen Zehntelmillimeter -- fuers Bild genug, und die Antwort bleibt klein.
STELLEN = 4


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
    zweier Streifen eine Strecke), ``unterzuege`` und ``stuetzenbereiche``.
    Die Zonen zeichnet die Oberflaeche nach dem Projekt.
    """
    if befund is None:
        return {"gerechnet": False, "meldungen": []}
    meldungen = [{"text": m.text, "elemente": list(m.elemente), "fehler": m.fehler}
                 for m in befund.meldungen]
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
    }


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
