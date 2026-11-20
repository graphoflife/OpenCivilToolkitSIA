---
erzeugt: 2874e965dc96
art: modul
tags: [modul]
---
> [!abstract] opencivil/geotechnik/verhalten.py
> wie ein Boden traegt.
> Paket [[opencivil.geotechnik]] · [Quelltext](../../opencivil/geotechnik/verhalten.py)

## VERANTWORTUNG

Die eine Wahl, die Pfahl und Grundbruch teilen ([[opencivil.geotechnik.verhalten#Verhalten|Verhalten]]):
drainiert mit wirksamen Spannungen, Reibungswinkel und Kohaesion;
undrainiert mit totalen Spannungen und der undrainierten Scherfestigkeit
s_u. Beide zeigen sie als denselben Schalter (Benutzer, 2026-11-19); bis
dahin hiess im Grundbruch phi = 0 undrainiert.

## Inhalt

### Verhalten

```python
class Verhalten(Wahl)
```

Womit ein Boden traegt: drainiert mit Reibung und Kohaesion, undrainiert mit s_u.

- `DRAINIERT = 'drainiert'`
- `UNDRAINIERT = 'undrainiert'`

#### Verhalten.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Verhalten.erklaerung

```python
@property
def erklaerung(self) -> str
```


## Braucht

- [[opencivil.core.wahl]]

## Gebraucht von

- [[opencivil.geotechnik.fundament]]
- [[opencivil.geotechnik.gleiten]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.pfahl.boden]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.pfahl]]
- [[opencivil.web.api]]
