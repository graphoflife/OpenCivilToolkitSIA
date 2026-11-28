---
erzeugt: c49cf7d4d9d2
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aus_system.py
> was eine Querschnittsanalyse aus einem Balkensystem nimmt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/aus_system.py)

## VERANTWORTUNG

Das ebene oder raeumliche Balkensystem einer Querschnittsanalyse und seine
Staebe ([[opencivil.projekt.aus_system#AusSystemEintrag|AusSystemEintrag]]): alle, deren Querschnitt diese Analyse
ist, oder gewaehlte ([[opencivil.projekt.aus_system#Stabwahl|Stabwahl]]). Je Kombination werden ihre
massgebenden Stellen Lastfaelle der Analyse (Plan vom 2026-11-27, Schritt
12) – gebaut in [[opencivil.projekt.aufbau.aus_system]], gewaehlt in
[[opencivil.stabwerk.stellen]].

## Inhalt

### Stabwahl

```python
class Stabwahl(Wahl)
```

Welche Staebe des Systems zaehlen.

- `MIT_QUERSCHNITT = 'mit_querschnitt'`
- `GEWAEHLT = 'gewaehlt'`

#### Stabwahl.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Stabwahl.erklaerung

```python
@property
def erklaerung(self) -> str
```

### AusSystemEintrag

```python
@dataclass
class AusSystemEintrag(Beschreibung)
```

Das Balkensystem einer Analyse und seine Staebe – ohne System keines:
dann hat die Analyse nur ihre eigenen Lastfaelle.

- `system: str = ''` – Die Kennung eines ebenen (`r1`) oder raeumlichen (`u1`) Balkensystems; leer: keines.
- `stabwahl: Stabwahl = Stabwahl.MIT_QUERSCHNITT`
- `staebe: List[str] = field(default_factory=list)` – Mit [[opencivil.projekt.aus_system#Stabwahl|Stabwahl.GEWAEHLT]] die Kennungen der Linien (`L3`); sonst ohne Belang.

#### AusSystemEintrag.bezuege

```python
def bezuege(self) -> List[str]
```

Das System, dessen Schnittgroessen die Analyse liest – oder keines.


## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.projekt.eintraege]]

## Gebraucht von

- [[opencivil.projekt.aufbau.aus_system]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.web.api]]
