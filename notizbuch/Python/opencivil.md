---
erzeugt: 78b15069e639
art: modul
tags: [modul]
---
> [!abstract] opencivil/__init__.py
> Nachweise nach SIA 262, jede Zahl mit ihrer Herleitung.
> [Quelltext](../../opencivil/__init__.py)

Der Einstieg ohne Oberflaeche:

```python
from opencivil import Projekt

p = Projekt("Decke über EG")
p.beton("C30/37")
p.stahl("B500B")
q = p.platte("Decke", h=300, x=[18, 12], y=[12, 12])
q.einwirkung("Feld", M_Ed=100)
print(p.rechnen().zusammenfassung())
```

`Projekt` wird erst beim Zugriff geladen: wer nur `opencivil.core`
braucht, soll dafuer nicht alle Nachweise importieren.


## RECHENWEG

Ein [[opencivil.projekt.projekt#Projekt|Projekt]] ist eine Beschreibung -- Baustoffe,
Platten, gezeichnete Querschnitte, Einwirkungen --, so wie die Oberflaeche
sie speichert. [[opencivil.projekt.projekt#Projekt.aufbauen|Projekt.aufbauen]] macht daraus einen
[[opencivil.projekt.aufbau#Aufbau|Aufbau]]: ein
[[opencivil.core.rechenwerk#Rechenwerk|Rechenwerk]] voller Berechnungen, je
Kennwert, je Lage, je Nachweis eine.

Gefragt wird rueckwaerts: [[opencivil.core.rechenwerk#Rechenwerk.loese|Rechenwerk.loese]] verfolgt, was ein Ziel
braucht, und rechnet genau das. Jede Berechnung schreibt dabei ihre
Herleitung ins [[opencivil.core.protokoll#Protokoll|Protokoll]] -- Formel,
Zahlen, Ergebnis. Heraus kommt eine
[[opencivil.core.rechenwerk#Loesung|Loesung]]: die Werte, die Urteile und das
Protokoll.

Daraus setzt [[opencivil.bericht]] den Bericht und [[opencivil.web]]
die Oberflaeche -- ohne selbst zu rechnen. Daneben zeigt
[[opencivil.spannungsanalyse]], was ein Querschnitt tut, ohne ihn
nachzuweisen, und [[opencivil.bewehrungssuche]] sucht eine Bewehrung,
statt sie zu setzen. Das Notizbuch ([[opencivil.notizbuch]]) schreibt aus
alldem die Formelsammlung und diese Seiten.

## Module

- [[opencivil.bericht]] – was aus einer Loesung zu lesen ist.
- [[opencivil.bewehrungssuche]] – die Bewehrung suchen statt sie zu setzen.
- [[opencivil.core]] – das Geruest, auf dem jede Rechnung steht.
- [[opencivil.ergebnis]] – ein gerechnetes Projekt, wie man es ohne Oberflaeche braucht.
- [[opencivil.material]] – die Baustoffe: Beton und Betonstahl.
- [[opencivil.nachweis]] – die Nachweise der Platte und des gezeichneten Querschnitts.
- [[opencivil.notizbuch]] – das Notizbuch: Formelsammlung und Python-Doku als Markdown.
- [[opencivil.projekt]] – Serialisierbare Beschreibung eines ganzen Projekts.
- [[opencivil.querschnitt]] – die Querschnitte: die Platte und der gezeichnete.
- [[opencivil.spannungsanalyse]] – den Querschnitt ansehen, ohne ihn nachzuweisen.
- [[opencivil.stabwerk]] – ebene Stabwerke nach der Steifigkeitsmethode.
- [[opencivil.web]] – die Oberflaeche, von der Seite des Rechenkerns.

## Braucht

- [[opencivil.projekt]]
