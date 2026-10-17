"""
opencivil/konsole/dienst.py -- die Konsole als Dienst für ihren Faden.

VERANTWORTUNG:
Nimmt die Anfragen der App «Python» an, wie :mod:`opencivil.web.dienst` die
des Rechenkerns: Name und Rumpf als JSON hinein, ``{"status", "daten"}`` als
JSON heraus. Derselbe Faden (``web/js/kern_arbeiter.js``) trägt beide; die
Konsole bekommt einen eigenen, damit eine Endlosschleife im Skript weder die
Seite noch den Rechenkern anhält -- und damit «Abbrechen» ihn einfach
beenden kann.

ANFRAGEN:
``ausfuehren`` {code, name, eingabe}
    Lädt die Pakete, die der Code einbindet, und führt ihn aus. Zurück
    kommen die Ereignisse des Laufs und die Variablen danach.
``zuruecksetzen`` {}
    Leert den Namensraum.

Asynchron, weil das Laden der Pakete im Browser wartet; der Faden wartet auf
jede Antwort, beim Rechenkern auf eine fertige Zeichenkette. Verpackt wird
wie beim Rechenkern (:mod:`opencivil.web.umschlag`).
"""

from __future__ import annotations

import json
import traceback
from typing import Any, Dict

from opencivil.konsole import pakete
from opencivil.konsole.sitzung import Sitzung
from opencivil.web.umschlag import fehlerdaten, umschlag

SITZUNG = Sitzung()


async def bearbeite_json(name: str, rumpf: str) -> str:
    """Eine Anfrage, als JSON hinein und hinaus -- Fehler kommen als Antwort, nie als Absturz."""
    try:
        daten = json.loads(rumpf or "{}")
        if name == "ausfuehren":
            code = str(daten.get("code") or "")
            await pakete.laden(code)
            lauf = SITZUNG.ausfuehren(code, name=str(daten.get("name") or "Konsole"),
                                      eingabe=bool(daten.get("eingabe")))
            antwort: Dict[str, Any] = {"ereignisse": lauf.ereignisse,
                                       "fehlerfrei": lauf.fehlerfrei}
        elif name == "zuruecksetzen":
            SITZUNG.zuruecksetzen()
            antwort = {}
        else:
            return umschlag(404, fehlerdaten(f"Die Konsole kennt die Anfrage '{name}' nicht."))
        antwort["variablen"] = SITZUNG.variablen()
        return umschlag(200, antwort)
    except Exception as fehler:  # noqa: BLE001 -- jede Panne wird eine Antwort
        return umschlag(500, fehlerdaten(f"{type(fehler).__name__}: {fehler}",
                                         traceback.format_exc()))
