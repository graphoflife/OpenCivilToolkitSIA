---
erzeugt: 0a84bb32f13e
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/mappe.py
> mehrere Projekte in einer Datei.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/mappe.py)

## VERANTWORTUNG

Die [[opencivil.projekt.mappe#Mappe|Mappe]] haelt die Projekte, die zusammen gespeichert und geoeffnet
werden -- «Wohnhaus», «Halle». Gerechnet wird je Projekt, jedes fuer sich;
die Mappe prueft nur, was zwischen ihnen gilt: es gibt mindestens eines, und
jedes heisst anders. Am Namen erkennt man ein Projekt in der Oberflaeche, in
Meldungen und im Zwischenspeicher des Dienstes ([[opencivil.web.speicher]]).


## EINE DATEI, ZWEI FORMEN

Seit 2026-11-20 schreibt die Oberflaeche `{"projekte": [...]}`. Eine Datei
mit einem einzelnen Projekt, wie sie bis dahin geschrieben wurde, oeffnet als
Mappe mit diesem einen. Umgeschrieben werden muss dafuer nichts: jedes
Projekt steht in der Mappe so da wie vorher allein.

## Inhalt

### projekt_aus_datei

```python
def projekt_aus_datei(roh: Any) -> Projekt
```

Ein Projekt, wie es in einer Datei steht: erkannt ([[opencivil.projekt.mappe#Konstanten|KENNFELDER]]),
gelesen und geprueft -- durch denselben Leser wie alles andere
([[opencivil.projekt.lesen]]), nicht durch eine zweite Pruefung in
JavaScript. Alte Formate liest er nicht; eine solche Datei nennt das
erste Feld, das er nicht kennt.

### _wer

```python
def _wer(roh: Any, i: int) -> str
```

Wie das Projekt an Stelle `i` in Meldungen heisst: «Projekt 'Halle'», ohne Namen «Projekt 2».

### _im

```python
@contextmanager
def _im(wer: str) -> Iterator[None]
```

Ein Fehler darin nennt sein Projekt zuerst -- «Projekt 'Halle', Platte
'Decke': …»: in einer Mappe steht eine Platte 'Decke' vielleicht in
jedem Projekt. Wo der Ort schon das Projekt ist, steht es einmal.

### Mappe

```python
@dataclass
class Mappe
```

Die Projekte einer Datei, in der Reihenfolge, in der die Oberflaeche sie zeigt.

- `projekte: List[Projekt] = field(default_factory=list)`

#### Mappe.pruefen

```python
def pruefen(self) -> None
```

Prueft jedes Projekt ([[opencivil.projekt.projekt#Projekt.pruefen|Projekt.pruefen]]) und was zwischen ihnen gilt.

#### Mappe._zwischen_pruefen

```python
def _zwischen_pruefen(self) -> None
```

Mindestens ein Projekt, und jedes mit eigenem Namen: an ihm waehlt man
es aus. Ein leerer Name hiesse in der Oberflaeche ein leerer Knopf.

#### Mappe.als_dict

```python
def als_dict(self) -> Dict[str, Any]
```

#### Mappe.aus_dict

```python
@classmethod
def aus_dict(cls, roh: Any) -> 'Mappe'
```

Eine Mappe aus der Datei, gelesen und geprueft. Ohne `projekte` ist
es ein einzelnes Projekt, wie bis 2026-11-20 gespeichert -- die Mappe
hat dann dieses eine, und seine Meldungen lauten wie damals.


## Konstanten

- `KENNFELDER = ('name', 'materialien', *(art.liste for art in BAUTEILE))` – Woran ein Projekt in einer Datei zu erkennen ist -- mindestens eines davon muss dastehen. Jedes Feld eines Projekts hat eine Vorgabe, `{}` liest sich darum als leeres Projekt: wer beim Oeffnen eine falsche Datei erwischte, bekaeme wortlos ein leeres und haette seine Arbeit verloren.

## Braucht

- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.projekt]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.web.dienst]]
