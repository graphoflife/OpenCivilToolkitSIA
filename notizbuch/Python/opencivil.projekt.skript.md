---
erzeugt: f475dc6eb980
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/skript.py
> ein Python-Skript der App «Python», wie es
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/skript.py)

gespeichert wird.


## VERANTWORTUNG

Kennung, Name und Code. Ausgeführt wird es nicht im Rechenkern, sondern in
der Konsole der Oberfläche ([[opencivil.konsole]]); was es ausgibt, steht
in keinem Bericht. Gespeichert wird es mit dem Projekt, damit es beim
nächsten Öffnen wieder da ist (Benutzer, 2026-10-15).

## Inhalt

### SkriptEintrag

```python
@dataclass
class SkriptEintrag(Beschreibung)
```

Ein Skript: Name und Code.

- `kennung: str`
- `name: str = ''`
- `code: str = ''`

#### SkriptEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> 'SkriptEintrag'
```

Ein neues Skript, mit der [[opencivil.projekt.skript#Konstanten|VORLAGE]] darin.

#### SkriptEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'SkriptEintrag'
```


## Konstanten

- `VORLAGE = '# Python im Browser: die Standardbibliothek, numpy, pandas und openc…` – Was ein neues Skript schon enthält: ein Diagramm ohne Download -- numpy und pandas kosten beim ersten Einbinden ein paar Megabyte.

## Braucht

- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.projekt]]
