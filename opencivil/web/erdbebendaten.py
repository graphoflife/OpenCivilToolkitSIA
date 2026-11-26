"""
opencivil/web/erdbebendaten.py -- was die Oberflaeche von einem Gebaeude im Erdbeben zeichnet.

VERANTWORTUNG:
Je Gebaeude die Zahlen der Ansicht, in den Einheiten der Anzeige -- m, kN
und kNm: Hoehe und Gewicht jedes Geschosses, je Richtung die Kraefte
F_d,i, Querkraft und Moment unter jedem Geschoss und was jede Wand am Fuss
traegt. Dazu je Wand, warum sie nicht rechnet, oder ihr Umriss im
Grundriss, in mm um ihren Schwerpunkt und gedreht nach ihrer Lage; die
Meldungen -- rot, was falsch ist, grau, was fehlt oder hier nicht gerechnet
wird -- und die Legenden unter den Bildern (:mod:`opencivil.web.anzeige`).
Namen und Hoehen der Geschosse liest die Oberflaeche aus dem Eintrag; was
der Kern daraus macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: Querkraefte und
Momente kommen aus :func:`opencivil.erdbeben.ersatzkraft.querkraefte` und
:func:`~opencivil.erdbeben.ersatzkraft.momente`, wie in der Tabelle der
Herleitung, der Grund einer Wand aus
:func:`opencivil.projekt.aufbau.erdbeben.wandquerschnitt`, wie beim Bauen,
und ihr Umriss aus derselben Zeichnung wie das Bild ihrer Analyse
(:func:`opencivil.web.diagrammdaten.zeichnung`).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, S
from opencivil.core.latex import Mathe
from opencivil.core.nachweis import OHNE_EINWIRKUNG
from opencivil.core.rechenwerk import Loesung
from opencivil.erdbeben.ersatzkraft import (
    NICHT_GERECHNET, NICHT_ZULAESSIG, Erdbebenbefund, Richtungsbefund, momente, querkraefte,
)
from opencivil.projekt import Aufbau
from opencivil.projekt.aufbau.erdbeben import wandquerschnitt
from opencivil.projekt.aufbau.kern import Grund
from opencivil.projekt.erdbeben import TragwandEintrag
from opencivil.web.anzeige import masszahl, urteil, zahl, zahlformel, zeile
from opencivil.web.diagrammdaten import zeichnung


def ansicht(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Ansicht eines Gebaeudes braucht. Ohne Nachweis -- es fehlt ein
    Geschoss, eine Wand oder ihr Querschnitt -- nur, was fehlt.
    """
    teil = aufbau.teile[kennung]
    gruende = [wandquerschnitt(w, aufbau) for w in teil.eintrag.waende]
    # Mit der Analyse, zu der der Grund gehoert: nach einer anderen Wahl gilt er nicht mehr.
    waende = [{"analyse": w.analyse, "grund": g.text, "fehler": g.falsch}
              if isinstance(g, Grund) else None
              for w, g in zip(teil.eintrag.waende, gruende)]
    wandmeldungen = [{"text": f"«{w.name}»: {g['grund']}.", "fehler": g["fehler"]}
                     for w, g in zip(teil.eintrag.waende, waende) if g is not None]
    # Was rechnet, hat einen Umriss -- das Bild zeigt ihn in jedem Geschoss.
    grundrisse = [None if isinstance(g, Grund)
                  else _grundriss(nummer, w, aufbau.querschnittsanalysen[w.analyse])
                  for nummer, (w, g) in enumerate(zip(teil.eintrag.waende, gruende), start=1)]
    nachweis = aufbau.feld("erdbeben").get(kennung)
    befund: Optional[Erdbebenbefund] = (
        loesung.befunde.get(nachweis.id) if nachweis is not None else None)
    if befund is None:
        fehlt = wandmeldungen or ([{"text": f"{teil.ohne_nachweis[0].upper()}"
                                            f"{teil.ohne_nachweis[1:]} → kein Nachweis.",
                                    "fehler": False}] if teil.ohne_nachweis else [])
        return {"waende": waende, "grundrisse": grundrisse, "geschosse": [], "richtungen": [],
                "zulaessig": None, "meldungen": fehlt, "legende": [], "verlaufslegende": []}
    meldungen: List[dict] = []
    if befund.ohne_einwirkung:
        meldungen.append({"text": OHNE_EINWIRKUNG, "fehler": False})
    if not befund.zulaessig:
        satz = f"{NICHT_ZULAESSIG}: {'; '.join(befund.gruende)}"
        meldungen.append({"text": f"{satz[0].upper()}{satz[1:]}.", "fehler": True})
    meldungen += [{"text": h, "fehler": False} for h in befund.hinweise]
    meldungen.append({"text": NICHT_GERECHNET, "fehler": False})
    return {
        "waende": waende,
        "grundrisse": grundrisse,
        "geschosse": [{"z": z, "W": zahl(W, KN)} for z, W in zip(befund.z, befund.W)],
        "richtungen": [_richtung(b, befund.z) for b in befund.richtungen],
        "zulaessig": befund.zulaessig,
        "meldungen": meldungen,
        "legende": [z for b in befund.richtungen for z in _legende(b, nachweis, loesung)],
        "verlaufslegende": _verlaufslegende(grundrisse, befund),
    }


def _grundriss(nummer: int, wand: TragwandEintrag, analyse: Any) -> Dict[str, Any]:
    """
    Eine Wand im Grundriss, in mm: die Flaechen ihrer Analyse um deren
    Schwerpunkt, gedreht nach ihrer Lage -- x nach rechts, y nach oben.
    ``nummer`` ist ihr Platz in der Liste, ab 1, wie in der Herleitung.
    """
    schnitt = zeichnung(analyse)
    y_S, z_S = schnitt["schwerpunkt"]
    return {"nummer": nummer, "name": wand.name, "n": wand.n, "lage": wand.lage.beschriftung,
            "polygone": [{**p, "punkte": [list(wand.lage.im_grundriss(y - y_S, z - z_S))
                                          for y, z in p["punkte"]]}
                         for p in schnitt["polygone"]]}


def _verlaufslegende(grundrisse: List[Optional[dict]], befund: Erdbebenbefund) -> List[list]:
    """Was das Bild der Waende, Querkraefte und Momente zeigt -- die Waende mit Namen."""
    waende = [f"{g['nummer']} «{g['name']}» ({g['n']}×, {g['lage']})" if g["n"] > 1
              else f"{g['nummer']} «{g['name']}» ({g['lage']})" for g in grundrisse if g]
    zeilen = []
    if waende:
        zeilen.append(zeile("Je Geschoss die Wände im Grundriss, nebeneinander statt an ihrem "
                            "Ort, x nach rechts und y nach oben; sie gehen über die ganze "
                            f"Höhe: {', '.join(waende)}."))
    if befund.richtungen:
        zeilen.append(zeile("Daneben je Richtung die Querkraft V und das Moment M aller Wände "
                            "zusammen, unter jedem Geschoss; der Kragarm ist unten "
                            "eingespannt. Angeschrieben ist der Wert am Fuss, M am Fuss ist ",
                            Mathe("M_0"), "."))
    return zeilen


def _richtung(b: Richtungsbefund, z: Sequence[float]) -> Dict[str, Any]:
    """
    Eine Richtung in den Einheiten der Anzeige: Kraefte, Querkraefte und
    Momente von unten, die Waende. ``z`` sind die Hoehen der Decken, m.
    """
    return {
        "richtung": b.richtung,
        "kraefte": [zahl(F, KN) for F in b.kraefte],
        "querkraefte": [zahl(V, KN) for V in querkraefte(b.kraefte)],
        "momente": [zahl(M, KNM) for M in momente(b.kraefte, z)],
        "F_d": zahl(b.F_d, KN), "M_0": zahl(b.M_0, KNM),
        "waende": [{"name": a.name, "n": a.n, "anteil": a.anteil, "V": zahl(a.V, KN),
                    "M": zahl(a.M, KNM)} for a in b.waende],
    }


def _legende(b: Richtungsbefund, nachweis, loesung: Loesung) -> List[list]:
    """Je Richtung: T_1 gegen 4 T_C mit dem Urteil (39), dann F_d und M_0 -- mit q und mit q = 1."""
    r = b.richtung
    gefunden = next(u for u in loesung.urteile if u.ziel == nachweis.d_grad[r].id)
    return [
        zeile(f"Richtung {r}: ", *urteil(
            rf"T_{{1,{r}}} = {masszahl(b.T1, S, 3)}", r"\le",
            rf"T_{{1,max}} = 4 \cdot T_C = {masszahl(gefunden.widerstand.groesse.si, S, 2)}",
            gefunden.erfuellt, gefunden.gradtext(latex=True)), " (39)."),
        zeile(zahlformel(f"S_{{d,{r}}}", b.S_d, EINHEITSLOS, 3), ", ",
              zahlformel(f"F_{{d,{r}}}", b.F_d, KN, 0), ", ",
              zahlformel(f"M_{{0,{r}}}", b.M_0, KNM, 0), " – mit q = 1.0 für Abheben und "
              "Kippen (16.5.1.9): ", zahlformel("F_d", b.F_d_1, KN, 0), ", ",
              zahlformel("M_0", b.M_0_1, KNM, 0), "."),
    ]
