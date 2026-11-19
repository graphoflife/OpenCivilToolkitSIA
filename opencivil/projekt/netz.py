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
   zufaellig dieselbe Kennung erbte.
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

from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


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
