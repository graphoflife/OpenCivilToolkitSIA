---
erzeugt: b43776db6d5e
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/balkensystem3d.py
> ein 3D-Balkensystem wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/balkensystem3d.py)

## VERANTWORTUNG

Wie ein 2D-Balkensystem ([[opencivil.projekt.aufbau.balkensystem|balkensystem]]),
im Raum: aus einem
[[opencivil.projekt.balkensystem3d#Balkensystem3dEintrag|Balkensystem3dEintrag]] das
Stabwerk in SI ([[opencivil.projekt.aufbau.balkensystem3d#modell_von|modell_von]]) und daraus die Rechnung mit
aufgeloesten Materialien und Querschnitten ([[opencivil.projekt.aufbau.balkensystem3d#bauen|bauen]]). Was beide gleich
pruefen und aufloesen, kommt von dort -- auch ein Querschnitt aus einer
Platte oder Querschnittsanalyse, deren I_T sie dann rechnet, und das
Material «gemäss Querschnitt»; hier
steht nur, was der Raum anders macht: der Drehwinkel in rad, eine Last an
einem Knoten als Vektor, ein Profil, das sich um beide Achsen biegt.

## Inhalt

### modell_von

```python
def modell_von(eintrag: Balkensystem3dEintrag) -> Modell
```

Das Stabwerk zum Rechnen, in SI ([[opencivil.stabwerk3d.modell]]).

### _knotenlast

```python
def _knotenlast(p: RaumknotenlastEintrag, wert: float) -> Knotenlast
```

Eine Kraft in ihre Richtung oder ein Moment um sie -- in den Achsen des Systems.

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: Balkensystem3dEintrag, aufbau: Aufbau) -> Bauteil
```

Ein 3D-Balkensystem -- seine Querschnitte aufgeloest wie in der Ebene.


## Braucht

- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.projekt.staebe]]
- [[opencivil.stabwerk3d.modell]]
- [[opencivil.stabwerk3d.raum]]
- [[opencivil.stabwerk3d.rechnung]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
