---
erzeugt: bedbb0471a4b
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/platte.py
> eine Platte wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/platte.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.platte#QuerschnittEintrag|QuerschnittEintrag]] der
Plattenquerschnitt und alle Nachweise, die an ihm haengen: M-N, Querkraft,
die Nachweise je x-Lage, die Stahlspannungen, Verformung und Knicken, dazu
Vergroesserungsfaktor und Kennzahlen. Nachgewiesen wird nur die
Tragrichtung x ([[opencivil.projekt.aufbau.platte#bauen|bauen]]).

## Inhalt

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: QuerschnittEintrag, aufbau: Aufbau) -> Bauteil
```

Eine Platte: der Querschnitt und alle Nachweise, die an ihm haengen.

Nachgewiesen wird nur die Tragrichtung x. Die y-Lagen stehen im
Querschnitt -- sie tragen zum Bewehrungsgehalt bei und druecken die
statische Hoehe von x nach innen --, aber kein Nachweis fragt nach ihnen.
Vorher lief hier alles doppelt, einmal je Richtung, und die Haelfte der
Tabelle handelte von einer Richtung, fuer die niemand Schnittgroessen
hatte.

### _lagennachweise

```python
def _lagennachweise(eintrag: QuerschnittEintrag, querschnitt: Plattenquerschnitt, richtung: Richtung, nachweis: BiegungNormalkraft, aufbau: Aufbau, teil: Bauteil) -> None
```

Die Nachweise je x-Lage: sproedes Versagen, Zwaengung auf Biegung und
auf Normalkraft, Duktilitaet.

Die x-Lagen von unten nach oben; in die Zusammenfassung kommt die
unguenstigere. Ausgeschaltet heisst still -- gerechnet wird trotzdem,
damit ein Hinweis stehen kann.

**Eine Lage ohne Stahl lassen sproedes Versagen, Zwaengung auf Biegung
und Duktilitaet weg** (Benutzer, 2026-10-19): sie wird nicht
nachgewiesen und steht nicht in der Tabelle. Bis dahin bekam sie ein
Urteil «ohne Bewehrung → kein Nachweis», das als nicht erfuellt zaehlte --
eine Platte nur mit unterer Bewehrung galt so als nicht erfuellt. Die
Zwaengung auf Normalkraft waehlt ihre Lagen selbst und prueft jede.

### _verformungsfall

```python
def _verformungsfall(f: VerformungsfallEintrag) -> Verformungsfall
```

Ein Verformungsfall aus seiner Beschreibung -- w in mm, die Spannweite in m.

### _ausgefallene

```python
def _ausgefallene(kombinationen: Sequence[KombinationEintrag], richtung: Richtung) -> List[Ausgefallen]
```

Welche Nachweise in dieser unbewehrten Richtung ausfallen.

Je Kombination der M-N-Nachweis, und wo eine Querkraft angegeben ist,
auch der Querkraftnachweis: ohne Bewehrung gibt es keine statische
Hoehe, also auch keinen Querkraftwiderstand. Beide Zeilen gehoeren in
die Tabelle -- eine davon wegzulassen hiesse, die Luecke nur zur
Haelfte zu schliessen.

### _kombination

```python
def _kombination(eintrag: KombinationEintrag) -> Schnittgroessen
```

Eine Einwirkung -- welche Massstaebe es gibt, prueft ihr Feld.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.dehnungsfaecher]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.platte]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
