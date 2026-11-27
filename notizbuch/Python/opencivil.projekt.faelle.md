---
erzeugt: 4a22f8f243d6
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/faelle.py
> Lastfaelle und Kombinationen eines Bauteils.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/faelle.py)

## VERANTWORTUNG

Was Balkensystem und Decke an Faellen gleich fuehren: der Lastfall – eine
Kennung, auf die die Lasten zeigen, ein Name, und ob er das Eigengewicht
bekommt – und die Kombination mit je Lastfall einem Beiwert. Dazu der
Baukasten, mit dem ein Bauteil in Python seine Faelle anlegt
([[opencivil.projekt.faelle#MitFaellen|MitFaellen]]), samt den Faellen, die ein frisches Bauteil
mitbringt. Geprueft werden sie beim Bauen
([[opencivil.projekt.aufbau.faelle]]).

## Inhalt

### kennung_von

```python
def kennung_von(eintrag: Any) -> str
```

Die Kennung eines Eintrags – oder die Kennung selbst.

### LastfallEintrag

```python
@dataclass
class LastfallEintrag(Beschreibung)
```

Ein Lastfall: eine Kennung, auf die die Lasten zeigen, und ein Name.

- `IM_ORT = 'Lastfall'`
- `kennung: str = ''`
- `name: str = ''`
- `eigengewicht: bool = False` – Ob der Lastfall das Eigengewicht bekommt – von selbst, aus Dichte und Querschnitt (Benutzer, 2026-10-23). Ein Bauteil hat einen davon.

### LastkombinationEintrag

```python
@dataclass
class LastkombinationEintrag(Beschreibung)
```

Eine Kombination: je Lastfall (Kennung) ein Beiwert, von Hand.

- `IM_ORT = 'Kombination'`
- `kennung: str = ''`
- `name: str = ''`
- `faktoren: Dict[str, float] = field(default_factory=dict)`

### MitFaellen

```python
class MitFaellen
```

Der Baukasten der Faelle – fuer ein Bauteil mit `lastfaelle` und `kombinationen`.

- `lastfaelle: List[LastfallEintrag]`
- `kombinationen: List[LastkombinationEintrag]`

#### MitFaellen.lastfall

```python
def lastfall(self, name: str, *, eigengewicht: bool=False) -> LastfallEintrag
```

#### MitFaellen.kombination

```python
def kombination(self, name: str, *faktoren: Tuple[Any, float]) -> LastkombinationEintrag
```

Eine Kombination – je Lastfall (Eintrag oder Kennung) ein Beiwert: `(g, 1.35), (w, 1.5)`.

#### MitFaellen.standardfaelle

```python
def standardfaelle(self) -> LastkombinationEintrag
```

Die Faelle eines frischen Bauteils (Benutzer, 2026-10-23): Eigengewicht
– es kommt von selbst –, Auflast und Nutzlast, die beiden ohne Last,
und die Kombination GZT mit 1.35, 1.35 und 1.5. Zurueck kommt die GZT.

#### MitFaellen.gebrauchskombination

```python
def gebrauchskombination(self) -> LastkombinationEintrag
```

Die Kombination GZG eines frischen Balkensystems: jeder Lastfall mit 1.0 (Benutzer, 2026-10-23).


## Braucht

- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.netz]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau.faelle]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.projekt.decke]]
- [[opencivil.projekt.staebe]]
