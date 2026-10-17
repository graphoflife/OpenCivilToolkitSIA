"""
opencivil/web/umschlag.py -- wie eine Antwort an die Oberfläche verpackt wird.

VERANTWORTUNG:
Der Umschlag jeder Antwort: ``{"status": …, "daten": …}`` als JSON, ohne
``NaN`` und ``Infinity``, und im Fehlerfall ``{"fehler", "spur"}`` als Daten.
Der Rechenkern (:mod:`opencivil.web.dienst`, auch hinter dem Server) und die
Konsole der App «Python» (:mod:`opencivil.konsole.dienst`) packen beide hier.
Bis 2026-10-17 baute die Konsole ihren Umschlag selbst, ohne den Riegel
gegen ``NaN`` -- eine Linie mit ``lw=float("nan")`` kam als Antwort an, die
``JSON.parse`` ablehnte, und die Konsole blieb bei «Läuft …» stehen.

LEICHT:
Nur ``json``, ``math`` und ``traceback``. Der Faden der Konsole lädt dieses
Modul und nicht den Rechenkern; ein Test hält das fest.
"""

from __future__ import annotations

import json
import math
import traceback
from typing import Any, Dict


def endlich(daten: Any) -> Any:
    """
    Ersetzt unendliche und undefinierte Zahlen durch ``None``.

    ``json.dumps`` schreibt dafuer sonst ``Infinity`` bzw. ``NaN`` -- eine
    Erweiterung, die Python selbst wieder liest, ``JSON.parse`` im Browser aber
    ablehnt. Die Antwort kaeme mit Status 200 an und waere dennoch unbrauchbar.

    Solche Werte entstehen ganz regulaer: ein Erfuellungsgrad ist unendlich,
    wenn die Einwirkung null ist. In JSON wird daraus ``null``, und die
    Oberflaeche zeigt dafuer das Unendlichkeitszeichen.
    """
    if isinstance(daten, float):
        return daten if math.isfinite(daten) else None
    if isinstance(daten, dict):
        return {k: endlich(v) for k, v in daten.items()}
    if isinstance(daten, (list, tuple)):
        return [endlich(v) for v in daten]
    return daten


def nach_json(daten: Any) -> str:
    """
    Wandelt eine Antwort in JSON.

    ``allow_nan=False`` ist Absicht: ``json.dumps`` schriebe sonst ``Infinity``
    und ``NaN``. Python liest das wieder, ``JSON.parse`` im Browser lehnt es ab
    -- die Antwort kaeme heil an und waere trotzdem unbrauchbar. Lieber hier
    laut scheitern als dort stumm. :func:`endlich` raeumt die Faelle vorher weg,
    sodass der Riegel nur zuschlaegt, wenn wirklich etwas Neues auftaucht.
    """
    return json.dumps(endlich(daten), ensure_ascii=False, allow_nan=False)


def fehlerdaten(meldung: str, spur: str = "") -> Dict[str, str]:
    """Was eine Anfrage zurueckgibt, die nicht gelang -- an jedem Dienst dieselbe Form."""
    return {"fehler": meldung, "spur": spur}


def umschlag(status: int, daten: Any) -> str:
    """
    Der Umschlag als JSON, wie ``web/js/kern.js`` ihn liest. Laesst sich
    ``daten`` nicht schreiben, wird daraus eine Antwort 500 mit dem Grund --
    eine Anfrage soll nie ohne lesbare Antwort bleiben.
    """
    try:
        return nach_json({"status": status, "daten": daten})
    except (TypeError, ValueError) as exc:
        return nach_json({"status": 500, "daten": fehlerdaten(
            f"Die Antwort liess sich nicht als JSON schreiben: {exc}",
            traceback.format_exc())})
