---
erzeugt: a90590df662d
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/faelle.py
> Lastfaelle und Kombinationen eines Bauteils.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/faelle.py)

## VERANTWORTUNG

Was Balkensystem und Decke an Faellen gleich fuehren: der Lastfall -- eine
Kennung, auf die die Lasten zeigen, ein Name, und ob er das Eigengewicht
bekommt -- und die Kombination mit je Lastfall einem Beiwert. Dazu der
Baukasten, mit dem ein Bauteil in Python seine Faelle anlegt
([[opencivil.projekt.faelle#MitFaellen|MitFaellen]]), samt den Faellen, die ein frisches Bauteil
mitbringt. Geprueft werden sie beim Bauen
([[opencivil.projekt.aufbau.faelle]]).

## Inhalt

### kennung_von

```python
def kennung_von(eintrag: Any) -> str
```

Die Kennung eines Eintrags -- oder die Kennung selbst.

### LastfallEintrag

```python
@dataclass
class LastfallEintrag(Beschreibung)
```

Ein Lastfall: eine Kennung, auf die die Lasten zeigen, und ein Name.

- `kennung: str = ''`
- `name: str = ''`
- `eigengewicht: bool = False` – Ob der Lastfall das Eigengewicht bekommt -- von selbst, aus Dichte und Querschnitt (Benutzer, 2026-10-23). Ein Bauteil hat einen davon.

### LastkombinationEintrag

```python
@dataclass
class LastkombinationEintrag(Beschreibung)
```

Eine Kombination: je Lastfall (Kennung) ein Beiwert, von Hand.

- `kennung: str = ''`
- `name: str = ''`
- `faktoren: Dict[str, float] = field(default_factory=dict)`

### MitFaellen

```python
class MitFaellen
```

Der Baukasten der Faelle -- fuer ein Bauteil mit `lastfaelle` und `kombinationen`.

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

Eine Kombination -- je Lastfall (Eintrag oder Kennung) ein Beiwert: `(g, 1.35), (w, 1.5)`.

#### MitFaellen.standardfaelle

```python
def standardfaelle(self) -> Tuple[LastkombinationEintrag, LastkombinationEintrag]
```

Die Faelle eines frischen Bauteils (Benutzer, 2026-10-23): Eigengewicht
-- es kommt von selbst --, Auflast und Nutzlast, die beiden ohne Last,
und die Kombinationen GZT mit 1.35, 1.35 und 1.5 und GZG mit je 1.0.
Zurueck kommen GZT und GZG.


## Braucht

- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.netz]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau.faelle]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.decke]]
