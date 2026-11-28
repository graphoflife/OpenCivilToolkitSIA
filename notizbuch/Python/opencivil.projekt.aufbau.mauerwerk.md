---
erzeugt: fbb550b83183
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/mauerwerk.py
> eine Mauerwerkswand wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/mauerwerk.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.mauerwerk#MauerwerkEintrag|MauerwerkEintrag]] die Wand
in SI ([[opencivil.projekt.aufbau.mauerwerk#wand_von|wand_von]]) und das Bauteil im Rechenwerk ([[opencivil.projekt.aufbau.mauerwerk#bauen|bauen]]).
Ohne Mauerwerk rechnet die Wand nicht, und der Hinweis sagt es
([[opencivil.projekt.aufbau.kern#Aufbau.unfertig|unfertig]]); was ihrer
Zeichnung fehlt – ein Knoten, auf den etwas zeigt –, steht in ihren
Meldungen, und der Rest des Projekts rechnet.

## Inhalt

### wand_von

```python
def wand_von(eintrag: MauerwerkEintrag) -> Tuple[Wand, List[Meldung]]
```

Die Wand der Beschreibung in SI: Masse in m. Ein Umriss, der auf einen
Knoten zeigt, den es nicht gibt, fehlt in der Wand; die Meldung sagt es.

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: MauerwerkEintrag, aufbau: Aufbau) -> Bauteil
```

Eine Wand: Mauerwerk und Zeichnung, angemeldet im Rechenwerk – noch ohne Nachweis.


## Konstanten

- `OHNE_NACHWEIS = 'die Nachweise des Mauerwerks rechnet das Werkzeug noch nicht'` – Warum die Wand noch keinen Nachweis führt – bis die Nachweise kommen (Plan vom 2026-11-27, Schritt 14 b–e).

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.werk]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.faelle]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.mauerwerk]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
