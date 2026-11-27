---
erzeugt: cb445d416439
art: modul
tags: [modul]
---
> [!abstract] opencivil/mcp/ausgabe.py
> was die Werkzeuge als Text zurueckgeben.
> Paket [[opencivil.mcp]] · [Quelltext](../../opencivil/mcp/ausgabe.py)

Kurz und in Markdown: eine KI liest es, und ein Mensch, der mitliest, soll
es auch koennen. Die Rechnung kommt nicht als ganze Antwort des Dienstes –
beim Beispiel rund 870 kB –, sondern je Bauteil als die Tabelle seiner
Nachweise, wie die Zusammenfassung der Seite sie zeigt, mit dem, was der
Kern dazu sagt ([[opencivil.mcp.ausgabe#rechnung|rechnung]]).

## Inhalt

### arten

```python
def arten() -> str
```

Die Apps: wie `app` sie nennt, wie ihre Felder heissen, und die Sorten der Materialien.

### ueberblick

```python
def ueberblick(sitzung: Sitzung) -> str
```

Die Mappe in einer Zeile: ihre Datei, ihre Projekte, welches gewaehlt ist.

### eintraege

```python
def eintraege(sitzung: Sitzung, listen: Iterable[str]) -> str
```

Je App die Eintraege des gewaehlten Projekts, mit Kennung – die Sandbox heisst so.

### rechnung

```python
def rechnung(daten: Mapping[str, Any], projekt: Projekt, nur: str='') -> str
```

Was `rechnen` zurueckgibt: je Bauteil von `projekt` die Tabelle
seiner Nachweise aus der Antwort `daten` des Dienstes, darunter seine
Hinweise – auch, was ihm fehlt. Mit `nur` dieses eine Bauteil. Ein
Material nur, wo der Kern etwas zu ihm sagt: rechnet es nicht, sagt das
Bauteil, das es nimmt, nur «warum, steht bei ihm».

### _stand

```python
def _stand(urteile: List[dict]) -> str
```

«3 Nachweise, alle erfüllt», «1 von 4 Nachweisen nicht erfüllt, 1 nicht
geführt», «kein Nachweis» – was sich nicht fuehren liess, zaehlt fuer
sich (`offen`).

### _je_eintrag

```python
def _je_eintrag(stuecke: Iterable[dict]) -> Dict[str, List[dict]]
```

Urteile oder Hinweise nach dem Eintrag, dem ihr Namensraum gehoert (`raum`).


## Braucht

- [[opencivil.material.arten]]
- [[opencivil.mcp.sitzung]]
- [[opencivil.projekt]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.mcp.werkzeuge]]
