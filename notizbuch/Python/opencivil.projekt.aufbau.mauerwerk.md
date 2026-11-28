---
erzeugt: 5e25facdd519
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/mauerwerk.py
> eine Mauerwerkswand wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/mauerwerk.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.mauerwerk#MauerwerkEintrag|MauerwerkEintrag]] die Wand
in SI samt ihren Lasten ([[opencivil.projekt.aufbau.mauerwerk#wand_von|wand_von]]) und das Bauteil im Rechenwerk mit
seinen Nachweisen ([[opencivil.projekt.aufbau.mauerwerk#bauen|bauen]]). Ohne Mauerwerk rechnet die Wand nicht,
und der Hinweis sagt es ([[opencivil.projekt.aufbau.kern#Aufbau.unfertig|unfertig]]);
was ihrer Zeichnung fehlt – ein Knoten, auf den etwas zeigt –, steht in
ihren Meldungen, und der Rest des Projekts rechnet. Die Regeln der
Lastfälle teilt sie mit Balkensystem und Decke
([[opencivil.projekt.aufbau.faelle]]).


## DIE NACHWEISE

Je Pfeiler und Kombination die Normalkraft, je Sturzauflager und
Kombination die Teilflächenpressung ([[opencivil.mauerwerk.nachweise]]);
je Pfeiler und Kombination, in der eine Last waagrecht schiebt, auch Schub
und Gleiten ([[opencivil.mauerwerk.schub]]). Wo sie stehen, hängt nur an der
Zeichnung; darum werden sie hier gebaut, sobald die Zeichnung rechnet. Sonst
sagt die Zusammenfassung, warum es noch keinen Nachweis gibt.

## Inhalt

### wand_von

```python
def wand_von(eintrag: MauerwerkEintrag) -> Tuple[Wand, List[Meldung]]
```

Die Wand der Beschreibung in SI: Masse in m, Lasten in N. Ein Teil, das
auf einen Knoten zeigt, den es nicht gibt, fehlt in der Wand; die Meldung
sagt es. Eine Last heisst nach ihrer Kennung; eine, deren Lastfall es
nicht gibt, und ein Beiwert dafür bleiben mit einem Hinweis weg.

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: MauerwerkEintrag, aufbau: Aufbau) -> Bauteil
```

Eine Wand: Mauerwerk, Zeichnung und Lasten, angemeldet im Rechenwerk –
mit ihren Nachweisen, sobald ihre Zeichnung rechnet und sie eine
Kombination hat.

### _nachweise

```python
def _nachweise(teil: Bauteil, objekt: Mauerwerkswand, wand: Wand, aufbau: Aufbau) -> None
```

Je Pfeiler und Kombination die Normalkraft – wo eine Last waagrecht
schiebt, auch Schub und Gleiten –, je Sturzauflager die Teilflächen.


## Konstanten

- `OHNE_WAND = 'noch keine Wand – ihren Umriss im Zeichenfenster zeichnen'` – Warum eine Wand keinen Nachweis führt: ihre Zeichnung rechnet nicht, oder es fehlt eine Kombination.
- `FALSCH_GEZEICHNET = 'an der Zeichnung stimmt etwas nicht – siehe die Meldungen der Wand'`
- `OHNE_KOMBINATION = 'noch keine Kombination – unter «Lastkombinationen» eine anlegen'`

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.mauerwerk.lasten]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.nachweise]]
- [[opencivil.mauerwerk.pruefen]]
- [[opencivil.mauerwerk.schub]]
- [[opencivil.mauerwerk.werk]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.faelle]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.mauerwerk]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
