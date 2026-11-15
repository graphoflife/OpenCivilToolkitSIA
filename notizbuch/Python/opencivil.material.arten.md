---
erzeugt: 158b81216390
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/arten.py
> die Materialarten des Projekts, je eine Zeile.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/arten.py)

## VERANTWORTUNG

Was Projekt, Aufbau und Oberflaeche ueber eine Materialart wissen muessen:
ihre Sorten und Kennwerte, wie ein Material entsteht, womit seine Kennung
und der Name eines eigenen beginnen, und worauf die Kennwerte stehen. Die
Oberflaeche liest dasselbe aus dem Katalog (`materialarten`).

Bis 2026-11-15 stand das an sieben Stellen je von Hand, als Zuordnung von
«beton» und «betonstahl» -- der Baustahl haette an jeder dazukommen muessen,
und eine vergessene fiele erst beim Anlegen auf.

## Inhalt

### Materialart

```python
@dataclass(frozen=True)
class Materialart
```

- `art: Baustoffart`
- `sorten: Mapping[str, Any]`
- `vorlagen: Tuple[KennwertVorlage, ...]`
- `bauen: Callable[..., Baustoff]` – Wie [[opencivil.material.beton#beton|beton]]: Sorte, dann Name, Praefix, Abweichungen.
- `anlegen: Tuple[str, ...]` – Die Sorten in der Folge, in der das Fenster «Neues Material» sie anbietet.
- `kennung: str` – Womit die Kennung beginnt: b1, s1, st1.
- `eigene: str` – Womit der Name eines eigenen Materials beginnt: BE1, S1, ST1 (Benutzer, 2026-10-16).
- `grundlage: str` – Worauf die Kennwerte einer Normsorte stehen -- so steht es in der Oberflaeche.

#### Materialart.titel

```python
@property
def titel(self) -> str
```


## Konstanten

- `MATERIALARTEN = {a.art.value: a for a in (Materialart(Baustoffart.BETON, BETONSORTEN,…`

## Braucht

- [[opencivil.material.basis]]
- [[opencivil.material.baustahl]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]

## Gebraucht von

- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
