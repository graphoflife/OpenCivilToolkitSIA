"""
opencivil/projekt/netz.py -- Knoten mit Kennungen, und wie neue dazukommen.

VERANTWORTUNG:
Eine Zeichnung aus Knoten und Elementen, die auf sie verweisen, braucht zwei
Regeln. Jede steht hier einmal:

1. **Eine Kennung kommt nie wieder.** Die naechste ist die groesste bisherige
   plus eins, je Vorsilbe: nach K1, K2, K7 kommt K8, nicht K3. Eine Meldung
   oder eine Auswahl, die auf ein geloeschtes Element zeigt, zeigt dann ins
   Leere -- und nicht auf ein anderes, das zufaellig dieselbe Kennung erbte.
2. **Gleiche Koordinaten sind ein Knoten.** Wer einen Punkt anlegt, der genau
   auf einem bestehenden Knoten liegt, bekommt diesen. So haengen Elemente,
   die sich in einem Punkt treffen, am selben Knoten und bewegen sich
   gemeinsam.

Genau gleich, nicht beinahe: was zusammengehoert, faengt das Zeichenfenster
beim Zeichnen. Eine Toleranz hier wuerde zwei Punkte, die jemand absichtlich
einen Hundertstelmillimeter auseinander gesetzt hat, stillschweigend vereinen.

Allgemein gehalten: der Baukasten kennt weder Beton noch Querschnitt, nur
Knoten mit Kennung und zwei Koordinaten. Das Zeichenfenster im Browser folgt
denselben Regeln (``web/js/cad_modell.js``), damit es nichts anlegt, was der
Kern anders saehe; der Kern haengt von ihm nicht ab.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


def nummer(kennung: str, vorsilbe: str) -> Optional[int]:
    """Die Zahl hinter der Vorsilbe -- ``None``, wenn die Kennung anders gebaut ist."""
    rest = kennung[len(vorsilbe):]
    return int(rest) if kennung.startswith(vorsilbe) and rest.isdigit() else None


def naechste_kennung(vorhandene: Iterable[str], vorsilbe: str) -> str:
    """Die naechste Kennung mit dieser Vorsilbe: die groesste bisherige plus eins."""
    groesste = max((n for n in (nummer(k, vorsilbe) for k in vorhandene) if n is not None),
                   default=0)
    return f"{vorsilbe}{groesste + 1}"


class Netz:
    """
    Die Knoten einer Zeichnung -- mit dem Zusammenfuehren gleicher Koordinaten.

    ``knoten`` ist die Liste der Beschreibung; neue Knoten werden an sie
    angehaengt. Jeder Knoten hat ``kennung``, ``y`` und ``z``. ``neu`` baut
    einen aus Kennung und Lage -- so bleibt der Baukasten bei der Klasse, die
    die Beschreibung speichert, ohne sie zu kennen.
    """

    def __init__(self, knoten: List[Any],
                 neu: Callable[[str, float, float], Any], vorsilbe: str = "K") -> None:
        self.knoten = knoten
        self.neu = neu
        self.vorsilbe = vorsilbe
        self._an: Dict[Tuple[float, float], str] = {}
        self._lage: Dict[str, Tuple[float, float]] = {}
        self._groesste = 0
        for k in knoten:
            self._merken(k)

    def _merken(self, k: Any) -> None:
        lage = (float(k.y), float(k.z))
        self._an.setdefault(lage, k.kennung)
        self._lage[k.kennung] = lage
        n = nummer(k.kennung, self.vorsilbe)
        if n is not None:
            self._groesste = max(self._groesste, n)

    def an(self, y: float, z: float) -> str:
        """Die Kennung des Knotens an ``(y, z)`` -- angelegt, wenn es dort noch keinen gibt."""
        lage = (float(y), float(z))
        if lage not in self._an:
            self._groesste += 1
            k = self.neu(f"{self.vorsilbe}{self._groesste}", lage[0], lage[1])
            self.knoten.append(k)
            self._merken(k)
        return self._an[lage]

    def lage(self, kennung: str) -> Optional[Tuple[float, float]]:
        """Wo der Knoten liegt -- ``None``, wenn es ihn nicht gibt."""
        return self._lage.get(kennung)
