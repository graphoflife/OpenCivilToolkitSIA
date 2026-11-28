---
erzeugt: 4b2b52c1f922
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/durchstanzen.py
> eine Durchstanzstelle wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/durchstanzen.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.durchstanzen#DurchstanzEintrag|DurchstanzEintrag]] die
Durchstanzstelle mit ihren Vorgaben und ihr Nachweis ([[opencivil.projekt.aufbau.durchstanzen#bauen|bauen]]). Hier
werden Aussparungen und Plattenbereiche aus ihren Knoten gelesen und
geprüft: jedes braucht drei Ecken und darf sich nicht selbst schneiden.
Plattenbereiche dürfen ineinander liegen, sich aber nicht teilweise
überdecken, und die Stütze liegt ganz in einem Bereich oder ganz neben ihm.

## Inhalt

### _ecken

```python
def _ecken(eintrag: DurchstanzEintrag, knoten: List[str], name: str) -> List[Tuple[float, float]]
```

Die Ecken eines Polygons in m – geprüft, sonst ein Satz, was nicht stimmt.

### aussparungen

```python
def aussparungen(eintrag: DurchstanzEintrag) -> List[List[Tuple[float, float]]]
```

Die Aussparungen als Ecken in m.

### bereiche

```python
def bereiche(eintrag: DurchstanzEintrag, flaeche: GestuetzteFlaeche, masse: Masse) -> List[Plattenbereich]
```

Die Plattenbereiche mit ihren Ecken und ihrer Dicke in m – geprüft wie
im Dateikopf. An einer Wand prüft es nur die Bereiche selbst: dort
rechnet der Nachweis sie noch nicht.

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: DurchstanzEintrag, aufbau: Aufbau) -> Bauteil
```

Eine Durchstanzstelle und ihr Nachweis. Jede Zahl in der Einheit ihres
Feldes ([[opencivil.projekt.lesen#als_groesse|als_groesse]]).


## Konstanten

- `MM = 0.001` – mm in m.

## Braucht

- [[opencivil.durchstanzen.bereiche]]
- [[opencivil.durchstanzen.flaeche]]
- [[opencivil.durchstanzen.kennzahl]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
