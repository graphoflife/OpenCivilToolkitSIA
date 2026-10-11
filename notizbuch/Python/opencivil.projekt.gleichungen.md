---
erzeugt: 55f4a60f5068
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/gleichungen.py
> ein Blatt analytischer Gleichungen, wie es
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/gleichungen.py)

gespeichert wird.


## VERANTWORTUNG

Die Beschreibung eines Blatts: Kennung, Name und die Zeilen. Gerechnet wird in
[[opencivil.gleichungen.blatt]]; hier steht nur, was in der Datei steht.

## Inhalt

### GleichungszeileEintrag

```python
@dataclass
class GleichungszeileEintrag(Beschreibung)
```

Eine Zeile des Blatts.

* `formel`: `latex` wie der Editor es schreibt -- eine Definition
  (`b = 2a + 1\,\mathrm{m}`) oder eine Auswertung (`a \cdot b =`);
  `einheit` die gewuenschte Einheit des Ergebnisses, leer heisst frei.
* `projektwert`: ein gerechneter Wert des Projekts (`wert_id`), im
  Blatt unter `name` (LaTeX, etwa `f_{cd}`).
* `text`: ein Satz dazwischen.

- `art: str = 'formel'`
- `latex: str = ''`
- `einheit: str = ''`
- `name: str = ''`
- `wert_id: str = ''`
- `text: str = ''`

#### GleichungszeileEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'GleichungszeileEintrag'
```

### GleichungsblattEintrag

```python
@dataclass
class GleichungsblattEintrag(Beschreibung)
```

Ein Blatt: Zeile fuer Zeile Gleichungen, Projektwerte, Text.

- `kennung: str`
- `name: str`
- `zeilen: List[GleichungszeileEintrag] = field(default_factory=list)`

#### GleichungsblattEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'GleichungsblattEintrag'
```


## Konstanten

- `ZEILENARTEN = ('formel', 'projektwert', 'text')` – Was eine Zeile sein kann.

## Braucht

- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.gleichungen.blatt]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
