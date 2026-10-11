---
erzeugt: 5acd2280f9ae
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/netz.py
> Knoten mit Kennungen, und wie neue dazukommen.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/netz.py)

## VERANTWORTUNG

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
denselben Regeln (`web/js/cad_modell.js`), damit es nichts anlegt, was der
Kern anders saehe; der Kern haengt von ihm nicht ab.

## Inhalt

### nummer

```python
def nummer(kennung: str, vorsilbe: str) -> Optional[int]
```

Die Zahl hinter der Vorsilbe -- `None`, wenn die Kennung anders gebaut ist.

### naechste_kennung

```python
def naechste_kennung(vorhandene: Iterable[str], vorsilbe: str) -> str
```

Die naechste Kennung mit dieser Vorsilbe: die groesste bisherige plus eins.

### Netz

```python
class Netz
```

Die Knoten einer Zeichnung -- mit dem Zusammenfuehren gleicher Koordinaten.

`knoten` ist die Liste der Beschreibung; neue Knoten werden an sie
angehaengt. Jeder Knoten hat `kennung`, `y` und `z`. `neu` baut
einen aus Kennung und Lage -- so bleibt der Baukasten bei der Klasse, die
die Beschreibung speichert, ohne sie zu kennen.

#### Netz.an

```python
def an(self, y: float, z: float) -> str
```

Die Kennung des Knotens an `(y, z)` -- angelegt, wenn es dort noch keinen gibt.

#### Netz.lage

```python
def lage(self, kennung: str) -> Optional[Tuple[float, float]]
```

Wo der Knoten liegt -- `None`, wenn es ihn nicht gibt.


## Gebraucht von

- [[opencivil.projekt.querschnittsanalyse]]
