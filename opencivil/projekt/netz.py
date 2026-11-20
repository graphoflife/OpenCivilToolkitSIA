"""
opencivil/projekt/netz.py -- Knoten mit Kennungen, und wie neue dazukommen.

VERANTWORTUNG:
Eine Zeichnung aus Knoten und Elementen, die auf sie verweisen, braucht zwei
Regeln. Jede steht hier einmal:

1. **Eine Kennung kommt nie wieder** (Benutzer, 2026-11-19). Wer Kennungen
   vergibt -- das Projekt, ein Bauteil --, merkt sich je Vorsilbe die
   hoechste je vergebene Nummer (``vergeben``); die neue liegt darueber. Nach
   K1, K2, K7 kommt K8, nicht K3 -- und nach dem Loeschen von K8 kommt K9,
   nicht wieder K8. Bis 2026-11-19 zaehlte nur, was noch da war. Eine
   Meldung, eine Auswahl oder eine Diagrammzeile, die auf ein geloeschtes
   Element zeigt, zeigt dann ins Leere -- und nicht auf ein anderes, das
   zufaellig dieselbe Kennung erbte. Wer Kennungen selbst schreibt, statt
   sie vergeben zu lassen -- der MCP-Zugang --, haelt sich an dieselbe
   Regel (:func:`von_hand`).
2. **Gleiche Koordinaten sind ein Knoten.** Wer einen Punkt anlegt, der genau
   auf einem bestehenden Knoten liegt, bekommt diesen. So haengen Elemente,
   die sich in einem Punkt treffen, am selben Knoten und bewegen sich
   gemeinsam.

Genau gleich, nicht beinahe: was zusammengehoert, faengt das Zeichenfenster
beim Zeichnen. Eine Toleranz hier wuerde zwei Punkte, die jemand absichtlich
einen Hundertstelmillimeter auseinander gesetzt hat, stillschweigend vereinen.

Allgemein gehalten: der Baukasten kennt weder Beton noch Querschnitt, nur
Knoten mit Kennung und Koordinaten -- zwei in der Ebene, drei im Raum. Das Zeichenfenster im Browser folgt
denselben Regeln (``web/js/cad_modell.js``), damit es nichts anlegt, was der
Kern anders saehe; der Kern haengt von ihm nicht ab.
"""

from __future__ import annotations

import dataclasses
import re
from typing import Any, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Tuple

from opencivil.projekt.lesen import ProjektFehler

#: Wie eine Kennung gebaut ist, die :func:`neue_kennung` vergibt: Vorsilbe und Nummer, ``LF3``.
_GEBAUT = re.compile(r"(\D+)(\d+)")


def nummer(kennung: str, vorsilbe: str) -> Optional[int]:
    """Die Zahl hinter der Vorsilbe -- ``None``, wenn die Kennung anders gebaut ist."""
    rest = kennung[len(vorsilbe):]
    return int(rest) if kennung.startswith(vorsilbe) and rest.isdigit() else None


def neue_kennung(besitzer: Any, vorsilbe: str, vorhandene: Iterable[str]) -> str:
    """
    Eine neue Kennung mit dieser Vorsilbe -- ueber jeder, die ``besitzer`` je
    vergeben hat, und ueber jeder der ``vorhandene``n: eine Datei, die noch
    keine Zaehlung kennt, hat nur sie. Der Besitzer merkt sich die neue.
    """
    n = max([besitzer.vergeben.get(vorsilbe, 0),
             *(nummer(k, vorsilbe) or 0 for k in vorhandene)]) + 1
    besitzer.vergeben[vorsilbe] = n
    return f"{vorsilbe}{n}"


def von_hand(alt: Any, neu: Any, wo: str) -> None:
    """
    Regel 1 fuer ein Bauteil, das jemand als Ganzes selbst schreibt, mit den
    Kennungen seiner Elemente -- ueber den MCP-Zugang (:mod:`opencivil.mcp`):
    jede Kennung in ``neu``, die ``alt`` nicht hat, liegt ueber jeder Nummer,
    die ``alt`` je vergeben hat. Sonst traefe ein Diagramm, das noch auf
    einen geloeschten Lastfall zeigt, einen neuen. ``neu`` merkt sich danach
    je Vorsilbe die hoechste Nummer. Eine Kennung anderer Form als ``LF3``
    vergibt :func:`neue_kennung` nie; sie zaehlt hier nicht.
    """
    alte = set(_kennungen(alt))
    hoechste = _hoechste(alt.vergeben, alte)
    for kennung in _kennungen(neu):
        gebaut = _GEBAUT.fullmatch(kennung)
        if kennung in alte or gebaut is None:
            continue
        vorsilbe, n = gebaut[1], int(gebaut[2])
        if n <= hoechste.get(vorsilbe, 0):
            raise ProjektFehler(f"die Kennung '{kennung}' gab es hier schon – eine Kennung kommt "
                                f"nie wieder. Frei ist '{vorsilbe}{hoechste[vorsilbe] + 1}'.", wo=wo)
    for vorsilbe, n in neu.vergeben.items():
        hoechste[vorsilbe] = max(n, hoechste.get(vorsilbe, 0))
    neu.vergeben = _hoechste(hoechste, _kennungen(neu))


def _hoechste(vergeben: Mapping[str, int], kennungen: Iterable[str]) -> Dict[str, int]:
    """``vergeben``, hochgezaehlt auf die Nummer jeder dieser Kennungen, wo sie darueber liegt."""
    hoechste = dict(vergeben)
    for kennung in kennungen:
        gebaut = _GEBAUT.fullmatch(kennung)
        if gebaut is not None:
            hoechste[gebaut[1]] = max(int(gebaut[2]), hoechste.get(gebaut[1], 0))
    return hoechste


def _kennungen(eintrag: Any) -> Iterator[str]:
    """Die Kennungen der Elemente unter ``eintrag``, auch tiefer -- nicht seine eigene."""
    for f in dataclasses.fields(eintrag):
        yield from _darin(getattr(eintrag, f.name))


def _darin(wert: Any) -> Iterator[str]:
    if dataclasses.is_dataclass(wert):
        if isinstance(getattr(wert, "kennung", None), str):
            yield wert.kennung
        yield from _kennungen(wert)
    elif isinstance(wert, (list, tuple, dict)):
        for teil in wert.values() if isinstance(wert, dict) else wert:
            yield from _darin(teil)


class Netz:
    """
    Die Knoten einer Zeichnung -- mit dem Zusammenfuehren gleicher Koordinaten.

    ``besitzer`` ist das Bauteil: neue Knoten werden an seine Liste
    ``knoten`` angehaengt, ihre Kennung zaehlt es (:func:`neue_kennung`).
    Jeder Knoten hat ``kennung`` und seine Koordinaten -- wie sie
    heissen, sagt ``achsen``: ``y`` und ``z`` im Querschnitt, ``x`` und ``z``
    im Balkensystem, ``x``, ``y`` und ``z`` im 3D-Balkensystem. ``neu`` baut
    einen aus Kennung und Lage -- so bleibt der Baukasten bei der Klasse, die
    die Beschreibung speichert, ohne sie zu kennen.
    """

    def __init__(self, besitzer: Any, neu: Callable[..., Any], vorsilbe: str = "K",
                 achsen: Tuple[str, ...] = ("y", "z")) -> None:
        self.besitzer = besitzer
        self.knoten: List[Any] = besitzer.knoten
        self.neu = neu
        self.vorsilbe = vorsilbe
        self.achsen = achsen
        self._an: Dict[Tuple[float, ...], str] = {}
        self._lage: Dict[str, Tuple[float, ...]] = {}
        for k in self.knoten:
            self._merken(k)

    def _merken(self, k: Any) -> None:
        lage = tuple(float(getattr(k, achse)) for achse in self.achsen)
        self._an.setdefault(lage, k.kennung)
        self._lage[k.kennung] = lage

    def an(self, *koordinaten: float) -> str:
        """Die Kennung des Knotens an diesen Koordinaten -- angelegt, wenn es dort noch keinen gibt."""
        lage = tuple(float(c) for c in koordinaten)
        if len(lage) != len(self.achsen):
            raise ValueError(f"Ein Knoten hat {len(self.achsen)} Koordinaten "
                             f"({', '.join(self.achsen)}), nicht {len(lage)}.")
        if lage not in self._an:
            k = self.neu(neue_kennung(self.besitzer, self.vorsilbe, self._lage), *lage)
            self.knoten.append(k)
            self._merken(k)
        return self._an[lage]

    def lage(self, kennung: str) -> Optional[Tuple[float, ...]]:
        """Wo der Knoten liegt -- ``None``, wenn es ihn nicht gibt."""
        return self._lage.get(kennung)
