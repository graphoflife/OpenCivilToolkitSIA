"""
werkzeug/werteabdruck.py -- jede Zahl der Prüfprojekte, auf die letzte Stelle.

Die Schnappschüsse (``tests/test_schnappschuss.py``) vergleichen den Bericht
als Text, also gerundet. Ein Umbau, der verspricht, keine Zahl zu ändern,
soll das auf die letzte Stelle belegen. Hier wird darum für die beiden
Prüfprojekte jeder Wert und jedes Urteil der Berichtsziele abgelegt, dazu die
ganze Antwort des Dienstes «rechnen» -- mit den Linien und Bildern, die der
Bericht nicht zeigt -- und der Katalog. Ein zweiter Lauf sagt, was sich
bewegt hat::

    python3 werkzeug/werteabdruck.py --schreiben     # vor dem Umbau
    python3 werkzeug/werteabdruck.py --vergleichen   # danach

Abgelegt wird unter ``ausgabe/werteabdruck/``; der Ordner gehört nicht ins
Repo. Gleitkommazahlen schreibt ``json`` umkehrbar genau. Verglichen wird
genau, nicht mit Toleranz: «keine Zahl ändert sich» heisst bis aufs letzte
Bit.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

WURZEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WURZEL))

ORDNER = WURZEL / "ausgabe" / "werteabdruck"

#: So viele Abweichungen stehen je Datei da; die Zahl aller kommt dazu.
ZEIGEN = 30


def _projekte() -> Dict[str, Any]:
    """Dieselben Projekte wie der Schnappschuss."""
    from opencivil.projekt import Projekt

    return {"beispiel": Projekt.beispiel(), "voll": Projekt.jeder_nachweis()}


def _dienst(name: str, rumpf: dict) -> Any:
    """Die Antwort eines Dienstes, so wie die Oberfläche sie liest."""
    from opencivil.web import dienst

    return json.loads(dienst.bearbeite_json(name, json.dumps(rumpf)))


def _wert(wert) -> dict:
    return {"si": wert.groesse.si, "symbol": wert.definition.symbol,
            "einheit": wert.definition.einheit.name}


def _abdruck(projekt) -> dict:
    """Werte und Urteile der Berichtsziele und die Antwort von «rechnen»."""
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.berichtsziele())
    return {
        "werte": {wid: _wert(w) for wid, w in sorted(loesung.werte.items())},
        "urteile": [{
            "ziel": u.ziel, "fall": u.fall, "art": u.art, "erfuellt": u.erfuellt,
            "erfuellungsgrad": u.erfuellungsgrad.si,
            "einwirkung": _wert(u.einwirkung) if u.einwirkung else None,
            "widerstand": _wert(u.widerstand) if u.widerstand else None,
        } for u in loesung.urteile],
        "rechnen": _dienst("rechnen", {"projekt": projekt.als_dict()}),
    }


def abdruecke() -> Dict[str, Any]:
    """Dateiname auf Inhalt -- alles, was abgelegt und verglichen wird."""
    dateien = {f"{name}.json": _abdruck(p) for name, p in _projekte().items()}
    dateien["katalog.json"] = _dienst("katalog", {})
    return dateien


def _unterschiede(alt: Any, neu: Any, pfad: str = "") -> Iterator[Tuple[str, Any, Any]]:
    """Jede Stelle, an der sich ``neu`` von ``alt`` unterscheidet, mit beiden Werten."""
    if isinstance(alt, dict) and isinstance(neu, dict):
        for schluessel in sorted(set(alt) | set(neu), key=str):
            unten = f"{pfad}/{schluessel}"
            if schluessel not in neu:
                yield unten, alt[schluessel], "(fehlt)"
            elif schluessel not in alt:
                yield unten, "(neu)", neu[schluessel]
            else:
                yield from _unterschiede(alt[schluessel], neu[schluessel], unten)
    elif isinstance(alt, list) and isinstance(neu, list):
        if len(alt) != len(neu):
            yield f"{pfad} (Länge)", len(alt), len(neu)
        for i, (a, n) in enumerate(zip(alt, neu)):
            yield from _unterschiede(a, n, f"{pfad}[{i}]")
    elif type(alt) is not type(neu) or alt != neu:
        yield pfad, alt, neu


def _kurz(wert: Any) -> str:
    text = json.dumps(wert, ensure_ascii=False)
    return text if len(text) <= 80 else text[:77] + "..."


def schreiben() -> None:
    ORDNER.mkdir(parents=True, exist_ok=True)
    for datei, inhalt in abdruecke().items():
        (ORDNER / datei).write_text(json.dumps(inhalt, ensure_ascii=False, indent=1,
                                               sort_keys=True), encoding="utf-8")
        print(f"geschrieben: {ORDNER / datei}")


def vergleichen() -> int:
    """Gibt die Zahl der Abweichungen zurück -- null heisst: alles gleich."""
    gesamt = 0
    for datei, neu in abdruecke().items():
        pfad = ORDNER / datei
        if not pfad.exists():
            print(f"{datei}: kein Abdruck da -- zuerst --schreiben.")
            gesamt += 1
            continue
        alt = json.loads(pfad.read_text(encoding="utf-8"))
        neu = json.loads(json.dumps(neu, ensure_ascii=False))
        liste: List[Tuple[str, Any, Any]] = list(_unterschiede(alt, neu))
        gesamt += len(liste)
        if not liste:
            print(f"{datei}: gleich")
            continue
        print(f"{datei}: {len(liste)} Abweichungen")
        for stelle, a, n in liste[:ZEIGEN]:
            print(f"  {stelle}: {_kurz(a)} -> {_kurz(n)}")
        if len(liste) > ZEIGEN:
            print(f"  ... und {len(liste) - ZEIGEN} weitere")
    return gesamt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    wahl = parser.add_mutually_exclusive_group(required=True)
    wahl.add_argument("--schreiben", action="store_true", help="den Abdruck ablegen")
    wahl.add_argument("--vergleichen", action="store_true", help="gegen den Abdruck prüfen")
    if parser.parse_args().schreiben:
        schreiben()
        return 0
    return 1 if vergleichen() else 0


if __name__ == "__main__":
    raise SystemExit(main())
