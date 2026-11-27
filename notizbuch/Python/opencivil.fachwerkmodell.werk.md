---
erzeugt: 3da3b97af48c
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/werk.py
> das Fachwerkmodell im Rechenwerk.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/werk.py)

## VERANTWORTUNG

Was ein Fachwerkmodell im Rechenwerk anmeldet: die Zahlen seines
Verfahrens als Vorgaben ([[opencivil.fachwerkmodell.suche#Konstanten|VORGABEN]])
und eine Prozedur, die sein Modell prüft
([[opencivil.fachwerkmodell.pruefen|pruefen]]), das gefundene Fachwerk
nachrechnet ([[opencivil.fachwerkmodell.nachrechnung|nachrechnung]]) und die
Herleitung schreibt ([[opencivil.fachwerkmodell.herleitung|herleitung]]). Es liest
nichts von aussen – kein Material, keine Dicke (Plan vom 2026-11-27,
Entscheid 11).


## GESUCHT WIRD DANEBEN

Die Suche läuft nicht hier, sondern Runde um Runde auf Anfrage der Seite
([[opencivil.fachwerkmodell.suche#runde|runde]]); was sie zuletzt fand,
steht im Projekt. Hier zählt es nur, wenn sein Abdruck zu Modell und
Verfahren passt – sonst sagt eine Meldung, dass es zu einem früheren
Stand gehört, und es steht nirgends.


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

Was die Rechnung fand: das Modell, seine Meldungen und das Fachwerk, mit dem, was dazu zu sagen ist.

- `modell: Modell`
- `meldungen: List[Meldung]` – Was das Modell meldet – die Meldungen der Beschreibung zuerst.
- `bereit: bool` – Ob sich ein Fachwerk suchen lässt: keine Meldung des Modells hält es auf.
- `abdruck: str = ''` – Der Abdruck von Modell und Verfahren – leer, solange das Modell nicht bereit ist.
- `stand: str = ''` – Wie es um das Fachwerk steht: `keines`, `veraltet`, `unlesbar` oder `gefunden` – leer, solange das Modell nicht bereit ist.
- `zum_fachwerk: List[Meldung] = field(default_factory=list)` – Was zum Fachwerk zu sagen ist: dass noch keines gesucht ist oder es zu einem früheren Stand gehört, wo sein Gleichgewicht nicht aufgeht, dass die Suche angehalten wurde.
- `gefunden: Optional[Suchergebnis] = None` – Was die Suche fand – nur, wenn es zu Modell und Verfahren gehört.
- `nachrechnung: Optional[Nachrechnung] = None`

### offen_meldungen

```python
def offen_meldungen(n: Nachrechnung) -> List[Meldung]
```

Wo das Gleichgewicht nicht aufgeht, rot: je Last, die es nicht ganz trägt, eine Meldung.

### FachwerkProzedur

```python
class FachwerkProzedur(Prozedur)
```

Das ganze Fachwerkmodell, geprüft, nachgerechnet und aufgeschrieben.

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

Das Modell geprüft, das Fachwerk nachgerechnet, die Herleitung geschrieben.

#### Fachwerksystem._fachwerk

```python
def _fachwerk(self, befund: Fachwerkbefund) -> None
```

Was im Projekt steht, wenn es zu Modell und Verfahren gehört, nachgerechnet – sonst warum nicht.

#### Fachwerksystem._zum_fachwerk

```python
def _zum_fachwerk(self, gefunden: Suchergebnis) -> List[Meldung]
```

Was sonst am gefundenen Fachwerk zu sagen ist: wo die Suche anhielt, was dünn blieb.


## Konstanten

- `THEMA = 'Fachwerkmodell'` – Unter welchem Thema seine Herleitung in der Formelsammlung steht.
- `IM_FENSTER = 'im Fenster «Verfahren» mit «Fachwerk suchen»'` – Wo die Suche beginnt – in den Meldungen genannt.
- `NOCH_KEINES = f'Noch kein Fachwerk gesucht – {IM_FENSTER}.'`
- `VERALTET = f'Das Fachwerk gehört zu einem früheren Stand: Scheibe, Lager, Lasten…`
- `UNLESBAR = f'Das gespeicherte Fachwerk lässt sich nicht lesen – neu suchen {IM_F…`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.wert]]
- [[opencivil.decke.herleitung]]
- [[opencivil.fachwerkmodell.herleitung]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.nachrechnung]]
- [[opencivil.fachwerkmodell.pruefen]]
- [[opencivil.fachwerkmodell.suche]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.fachwerkmodell.herleitung]]
- [[opencivil.projekt.aufbau.fachwerkmodell]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.web.fachwerkdaten]]
