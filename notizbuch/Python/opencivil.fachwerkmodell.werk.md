---
erzeugt: d7a57aca9d19
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/werk.py
> das Fachwerkmodell im Rechenwerk.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/werk.py)

## VERANTWORTUNG

Was ein Fachwerkmodell im Rechenwerk anmeldet: eine Prozedur, die sein
Modell prüft ([[opencivil.fachwerkmodell.pruefen|pruefen]]) und die Herleitung
schreibt ([[opencivil.fachwerkmodell.herleitung|herleitung]]). Es liest nichts von
aussen – kein Material, keine Dicke (Plan vom 2026-11-27, Entscheid 11).


## DAS ERGEBNIS

kommt als Befund in die Lösung ([[opencivil.fachwerkmodell.werk#Fachwerkbefund|Fachwerkbefund]]); Zeichnung und
Zusammenfassung lesen es dort. Ein Modell, dem etwas fehlt, ist ein Befund
mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.

## Inhalt

### Fachwerkbefund

```python
@dataclass
class Fachwerkbefund
```

Was die Rechnung fand: das Modell und die Meldungen – die der Beschreibung zuerst.

- `modell: Modell`
- `meldungen: List[Meldung]`

#### Fachwerkbefund.haelt_an

```python
@property
def haelt_an(self) -> bool
```

Ob eine Meldung die Suche nach einem Fachwerk aufhält.

### FachwerkProzedur

```python
class FachwerkProzedur(Prozedur)
```

Das ganze Fachwerkmodell, geprüft und aufgeschrieben.

#### FachwerkProzedur.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

### Fachwerksystem

```python
class Fachwerksystem(Rechenobjekt)
```

Ein Fachwerkmodell, fertig für das Rechenwerk.

- `WAS = 'Fachwerkmodell'`

#### Fachwerksystem.abschnitt

```python
def abschnitt(self) -> Abschnitt
```

#### Fachwerksystem.ziele

```python
def ziele(self) -> List[str]
```

Was ein Lauf rechnen muss: das Modell.

#### Fachwerksystem.rechnen_und_schreiben

```python
def rechnen_und_schreiben(self, p: Protokoll) -> Ausfuehrung
```

Das Modell geprüft, die Herleitung geschrieben.


## Konstanten

- `THEMA = 'Fachwerkmodell'` – Unter welchem Thema seine Herleitung in der Formelsammlung steht.
- `OHNE_VERFAHREN = 'Noch ohne Verfahren: geprüft sind Scheibe, Lager und Lasten, ein Fac…` – Solange kein Verfahren das Fachwerk sucht – ein Hinweis, wenn sonst nichts fehlt.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.wert]]
- [[opencivil.fachwerkmodell.herleitung]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.pruefen]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.fachwerkmodell.herleitung]]
- [[opencivil.projekt.aufbau.fachwerkmodell]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.web.fachwerkdaten]]
