---
erzeugt: 4c82502a84c2
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/__init__.py
> Serialisierbare Beschreibung eines ganzen Projekts.
> Paket [[opencivil]] · [Quelltext](../../opencivil/projekt/__init__.py)

## VERANTWORTUNG

Eine Oberflaeche braucht Materialien und Querschnitte als Daten: etwas, das sich
als JSON speichern, im Browser bearbeiten und wieder zu einem [[opencivil.core.rechenwerk#Rechenwerk|Rechenwerk]]
zusammenbauen laesst. Genau das ist ein [[opencivil.projekt.projekt#Projekt|Projekt]] -- eine reine
Beschreibung ohne Rechenlogik.


## AUFTEILUNG

Frueher eine Datei mit knapp zweitausend Zeilen und drei Aufgaben. Jetzt je
Aufgabe ein Modul:

```
lesen.py       was in einer Datei stehen darf und wie es gelesen wird,
               samt den alten Formaten
eintraege.py   die Teile: Material, Lagen, Buegel, Lastfaelle
platte.py      eine Platte mit ihren vier Lagen und allen Schaltern
querschnittsanalyse.py
               ein gezeichneter Querschnitt: Polygone, Bewehrung,
               Schubwaende, Lastfaelle
balkensystem.py
               ein ebener Rahmen: Knoten, Linien als Staebe und
               Linienlager, Lager, Lasten, Lastfaelle, Kombinationen
grundbruch.py  ein Flachfundament: Boden, Masse, Gelaende, Grundwasser
               und Einwirkungen fuer Grundbruch und Gleiten
netz.py        Knoten mit Kennungen, fuer beide Zeichnungen
skript.py      ein Python-Skript der App «Python»: gespeichert, nicht
               gerechnet
projekt.py     das Ganze: Zugriff, Rechnen ohne Oberflaeche, Pruefung,
               Speichern, das Beispiel
aufbau.py      aus der Beschreibung ein Rechenwerk
```

Die Abhaengigkeit laeuft in eine Richtung: lesen \<- eintraege \<- platte \<-
aufbau \<- projekt. Wer von aussen kommt, importiert aus dem Paket, nicht aus den
Modulen: `from opencivil.projekt import Projekt`.


## NORMSORTE ODER EIGENES MATERIAL

Ein Material ist entweder eine unveraenderte Normsorte oder ein eigenes. Nur die
unveraenderte darf die Sortenbezeichnung tragen: steht 'C30/37' auf einem
Bauteil, muessen die Kennwerte auch die der Norm sein. Wer abweichen will, macht
das Material mit [[opencivil.projekt.projekt#Projekt.material_loesen|Projekt.material_loesen]] eigenstaendig; es bekommt dann
einen eigenen Namen wie `C30/37_1`. So kann keine abgeaenderte Festigkeit unter
dem Deckmantel einer Normbezeichnung im Bericht landen.


## EINHEITEN IN DER BESCHREIBUNG

Alle Zahlen stehen in der Anzeige-Einheit des jeweiligen Kennwerts (mm, N/mm^2,
kNm, ...) -- also so, wie der Benutzer sie eintippt. Die Umrechnung in SI
geschieht erst beim Aufbau, ueber die [[opencivil.core.einheiten#Groesse|Groesse]].

## Module

- [[opencivil.projekt.aufbau]] – aus der Beschreibung ein Rechenwerk.
- [[opencivil.projekt.balkensystem]] – ein 2D-Balkensystem, wie die Oberflaeche es beschreibt.
- [[opencivil.projekt.eintraege]] – die Teile einer Projektbeschreibung.
- [[opencivil.projekt.grundbruch]] – ein Grundbruchnachweis, wie die Oberflaeche ihn beschreibt.
- [[opencivil.projekt.lesen]] – was in einer Projektdatei stehen darf, und wie es gelesen wird.
- [[opencivil.projekt.netz]] – Knoten mit Kennungen, und wie neue dazukommen.
- [[opencivil.projekt.platte]] – eine Platte, wie die Oberflaeche sie beschreibt.
- [[opencivil.projekt.projekt]] – das Projekt als Ganzes.
- [[opencivil.projekt.querschnittsanalyse]] – ein gezeichneter Querschnitt, wie die Oberflaeche ihn beschreibt.
- [[opencivil.projekt.skript]] – ein Python-Skript der App «Python», wie es

## Braucht

- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.skript]]

## Gebraucht von

- [[opencivil]]
- [[opencivil.bericht.formelsammlung]]
- [[opencivil.bericht.gliederung]]
- [[opencivil.bericht.konsole]]
- [[opencivil.bericht.latex_dokument]]
- [[opencivil.bericht.markdown]]
- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.bewehrungssuche.laengs]]
- [[opencivil.ergebnis]]
- [[opencivil.querschnitt.schnittanalyse]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.web.api]]
- [[opencivil.web.diagrammdaten]]
- [[opencivil.web.dienst]]
- [[opencivil.web.grundbruchdaten]]
- [[opencivil.web.speicher]]
