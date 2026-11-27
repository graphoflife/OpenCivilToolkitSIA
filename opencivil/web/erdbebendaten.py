"""
opencivil/web/erdbebendaten.py -- was die Oberflaeche von einem Gebaeude im Erdbeben zeichnet.

VERANTWORTUNG:
Je Gebaeude die Zahlen der Ansicht, in den Einheiten der Anzeige -- m, kN,
kNm und t: Hoehe, Gewicht und Masse jedes Geschosses, auch solange es noch
nicht rechnet -- man sieht die Massen, sobald man Geschosse eingibt --, je
Richtung die Kraefte F_d,i, Querkraft und Moment unter jedem Geschoss und was jeder
getrennte Teil des Kerns am Fuss traegt. Dazu je Geschoss, warum sein Kern
nicht rechnet, und je Kern, der rechnet, sein Umriss im Grundriss, in mm um
seinen Schwerpunkt, mit den Teilen; die Meldungen -- rot, was falsch ist,
grau, was fehlt oder hier nicht gerechnet wird -- und die Legenden unter den
Bildern (:mod:`opencivil.web.anzeige`). Namen, Hoehen und Kerne der
Geschosse liest die Oberflaeche aus dem Eintrag; was der Kern daraus macht,
kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: Querkraefte und
Momente kommen aus :func:`opencivil.erdbeben.kragarm.querkraefte` und
:func:`~opencivil.erdbeben.kragarm.momente`, wie in der Tabelle der
Herleitung, der Grund eines Kerns aus
:func:`opencivil.projekt.aufbau.erdbeben.kerne`, wie beim Bauen, und sein
Umriss aus derselben Zeichnung wie das Bild seiner Analyse
(:func:`opencivil.web.diagrammdaten.zeichnung`). Das Gewicht eines
Geschosses kommt aus dem Befund, solange es keinen gibt aus derselben Regel
(:func:`opencivil.erdbeben.ersatzkraft.gewicht`); die Masse ist das Gewicht
durch g, wie beim Eigengewicht (:data:`~opencivil.material.basis.ERDBESCHLEUNIGUNG`).
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Sequence, Tuple

from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, S, T
from opencivil.core.latex import Mathe
from opencivil.core.nachweis import OHNE_EINWIRKUNG
from opencivil.core.rechenwerk import Loesung
from opencivil.erdbeben.ersatzkraft import (
    NICHT_GERECHNET, NICHT_ZULAESSIG, Erdbebenbefund, Richtungsbefund, gewicht,
)
from opencivil.erdbeben.kern import Kerndaten
from opencivil.erdbeben.kragarm import momente, querkraefte
from opencivil.material.basis import ERDBESCHLEUNIGUNG
from opencivil.projekt import Aufbau
from opencivil.projekt.aufbau.erdbeben import Kernbefund, kerne
from opencivil.projekt.aufbau.kern import Grund
from opencivil.projekt.lesen import als_groesse
from opencivil.web.anzeige import masszahl, urteil, zahl, zahlformel, zeile
from opencivil.web.diagrammdaten import zeichnung


def ansicht(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Ansicht eines Gebaeudes braucht. Ohne Nachweis -- es fehlt ein
    Geschoss oder ein Kern -- nur, was fehlt, und die Kerne, die rechnen.
    """
    teil = aufbau.teile[kennung]
    eintrag = teil.eintrag
    befunde = kerne(eintrag, aufbau)
    # Mit der Analyse, zu der der Grund gehoert: nach einer anderen Wahl gilt er nicht mehr.
    je_geschoss = [{"analyse": s.kern, "grund": b.text, "fehler": b.falsch}
                   if isinstance(b, Grund) else None
                   for s, b in zip(eintrag.geschosse, befunde)]
    grundrisse = {b.kennung: _grundriss(b, aufbau.querschnittsanalysen[b.kennung])
                  for b in befunde if isinstance(b, Kerndaten)}
    namen = [s.name for s in eintrag.geschosse]
    nachweis = aufbau.feld("erdbeben").get(kennung)
    befund: Optional[Erdbebenbefund] = (
        loesung.befunde.get(nachweis.id) if nachweis is not None else None)
    if befund is None:
        fehlt = _kernmeldungen(namen, befunde) or (
            [{"text": f"{teil.ohne_nachweis[0].upper()}{teil.ohne_nachweis[1:]} → kein Nachweis.",
              "fehler": False}] if teil.ohne_nachweis else [])
        g = [{f: als_groesse(s, f).si for f in ("h", "G_k", "Q_k", "psi_2")}
             for s in eintrag.geschosse]
        return {"kerne": je_geschoss, "grundrisse": grundrisse,
                "geschosse": _geschosse(list(itertools.accumulate(s["h"] for s in g)),
                                        [gewicht(s["G_k"], s["Q_k"], s["psi_2"]) for s in g]),
                "richtungen": [], "zulaessig": None, "meldungen": fehlt, "legende": [],
                "verlaufslegende": []}
    meldungen: List[dict] = []
    if befund.ohne_einwirkung:
        meldungen.append({"text": OHNE_EINWIRKUNG, "fehler": False})
    if not befund.zulaessig:
        satz = f"{NICHT_ZULAESSIG}: {'; '.join(befund.gruende)}"
        meldungen.append({"text": f"{satz[0].upper()}{satz[1:]}.", "fehler": True})
    meldungen += [{"text": h, "fehler": False} for h in befund.hinweise]
    meldungen.append({"text": NICHT_GERECHNET, "fehler": False})
    return {
        "kerne": je_geschoss,
        "grundrisse": grundrisse,
        "geschosse": _geschosse(befund.z, befund.W),
        "richtungen": [_richtung(b, befund.z) for b in befund.richtungen],
        "zulaessig": befund.zulaessig,
        "meldungen": meldungen,
        "legende": [z for b in befund.richtungen for z in _legende(b, nachweis, loesung)],
        "verlaufslegende": _verlaufslegende(namen, befunde, befund),
    }


def _geschosse(z: Sequence[float], W: Sequence[float]) -> List[dict]:
    """Je Geschoss, von unten, die Hoehe seiner Decke in m, sein Gewicht in kN, seine Masse in t."""
    return [{"z": zi, "W": zahl(Wi, KN), "m": zahl(Wi / ERDBESCHLEUNIGUNG.si, T)}
            for zi, Wi in zip(z, W)]


def _kernmeldungen(namen: Sequence[str], befunde: Sequence[Kernbefund]) -> List[dict]:
    """Je Grund, warum ein Kern nicht rechnet, ein Satz -- mit allen Geschossen, die er trifft."""
    fehlt: Dict[Tuple[str, bool], List[str]] = {}
    for name, b in zip(namen, befunde):
        if isinstance(b, Grund):
            fehlt.setdefault((b.text, b.falsch), []).append(name)
    return [{"text": f"«{'», «'.join(geschosse)}»: {text}.", "fehler": falsch}
            for (text, falsch), geschosse in fehlt.items()]


def _grundriss(kern: Kerndaten, analyse: Any) -> Dict[str, Any]:
    """
    Ein Kern im Grundriss, in mm: die Flaechen seiner Analyse um deren
    Schwerpunkt, wie gezeichnet -- y der Analyse nach rechts, in x des
    Gebaeudes, z nach oben. Wo er aus getrennten Teilen besteht, je Teil
    seine Nummer und sein Schwerpunkt.
    """
    schnitt = zeichnung(analyse)
    y_S, z_S = schnitt["schwerpunkt"]
    return {"name": kern.analyse,
            "polygone": [{**p, "punkte": [[y - y_S, z - z_S] for y, z in p["punkte"]]}
                         for p in schnitt["polygone"]],
            "teile": [{"nummer": t.nummer, "mitte": [t.werte.y_S - y_S, t.werte.z_S - z_S]}
                      for t in kern.teile] if len(kern.teile) > 1 else []}


def _verlaufslegende(namen: Sequence[str], befunde: Sequence[Kernbefund],
                     befund: Erdbebenbefund) -> List[list]:
    """Was das Bild der Kerne, Querkraefte und Momente zeigt -- die Kerne mit ihren Geschossen."""
    je_kern: Dict[str, List[str]] = {}
    for name, b in zip(namen, befunde):
        if isinstance(b, Kerndaten):
            je_kern.setdefault(b.analyse, []).append(name)
    zeilen = []
    if je_kern:
        wo = (f"«{next(iter(je_kern))}» in jedem" if len(je_kern) == 1 else
              ", ".join(f"«{kern}» in «{'», «'.join(geschosse)}»"
                        for kern, geschosse in je_kern.items()))
        zeilen.append(zeile("Je Geschoss sein Kern im Grundriss, verkleinert und alle im selben "
                            f"Massstab, x nach rechts und y nach oben: {wo}. Am Fuss die Nummern "
                            "seiner getrennten Teile, wo er aus mehreren besteht."))
    if befund.richtungen:
        zeilen.append(zeile("Daneben je Richtung die Querkraft V und das Moment M des Kerns, "
                            "unter jedem Geschoss; der Kragarm ist unten eingespannt. "
                            "Angeschrieben ist der Wert am Fuss, M am Fuss ist ",
                            Mathe("M_0"), "."))
    return zeilen


def _richtung(b: Richtungsbefund, z: Sequence[float]) -> Dict[str, Any]:
    """
    Eine Richtung in den Einheiten der Anzeige: Kraefte, Querkraefte und
    Momente von unten, die Teile am Fuss. ``z`` sind die Hoehen der Decken, m.
    """
    return {
        "richtung": b.richtung,
        "kraefte": [zahl(F, KN) for F in b.kraefte],
        "querkraefte": [zahl(V, KN) for V in querkraefte(b.kraefte)],
        "momente": [zahl(M, KNM) for M in momente(b.kraefte, z)],
        "F_d": zahl(b.F_d, KN), "M_0": zahl(b.M_0, KNM),
        "teile": [{"nummer": a.nummer, "anteil": a.anteil, "V": zahl(a.V, KN),
                   "M": zahl(a.M, KNM)} for a in b.teile],
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
