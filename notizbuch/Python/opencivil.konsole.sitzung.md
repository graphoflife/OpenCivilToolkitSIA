---
erzeugt: b235ab4dd5d8
art: modul
tags: [modul]
---
> [!abstract] opencivil/konsole/sitzung.py
> eine Python-Sitzung für die App «Python».
> Paket [[opencivil.konsole]] · [Quelltext](../../opencivil/konsole/sitzung.py)

## VERANTWORTUNG

Führt aus, was der Benutzer schreibt -- ein Skript oder eine Zeile der
Konsole -- in einem Namensraum, der zwischen den Läufen bleibt: was Skript A
anlegt, sieht Skript B (Benutzer, 2026-10-15). Was dabei herauskommt, steht
der Reihe nach als Ereignis da -- Ausgabe, Fehlerausgabe, der Wert der
letzten Zeile, ein Fehler, ein Bild aus [[opencivil.konsole.zeichnen]] --,
und dazu die Variablen für den Beobachter rechts.


## WO SIE LÄUFT

Im Browser, in einem eigenen Faden mit Pyodide (`web/js/konsole.js`), nie
auf dem Rechner: über den lokalen Server könnte sonst jede Webseite Code auf
ihm ausführen. Getestet wird sie unter CPython; nur das Nachladen der Pakete
([[opencivil.konsole.pakete]]) gibt es dort nicht.


## REINES PYTHON

Im Namensraum liegt nichts vom Projekt (Benutzer, 2026-10-15). Wer will,
schreibt `import opencivil` -- der Rechenkern liegt im Faden bei.

## Inhalt

### Lauf

```python
@dataclass
class Lauf
```

Was ein Lauf ergab: die Ereignisse der Reihe nach, und ob er ohne Fehler durchkam.

- `ereignisse: List[Dict[str, Any]] = field(default_factory=list)`
- `fehlerfrei: bool = True`

#### Lauf.schreiben

```python
def schreiben(self, art: str, text: str) -> None
```

Text an die Ereignisse -- an das letzte gleicher Art, wenn es direkt davor steht.

### _Strom

```python
class _Strom
```

Was `print` erreicht: schreibt in den Lauf, unter seiner Art.

#### _Strom.write

```python
def write(self, text: str) -> int
```

#### _Strom.flush

```python
def flush(self) -> None
```

### Sitzung

```python
class Sitzung
```

Ein Namensraum und das Ausführen darin -- eine Konsole, ein Gedächtnis.

#### Sitzung.zuruecksetzen

```python
def zuruecksetzen(self) -> None
```

Ein leerer Namensraum -- alle Variablen weg, wie nach einem Neustart.

#### Sitzung.ausfuehren

```python
def ausfuehren(self, code: str, *, name: str='Konsole', eingabe: bool=False) -> Lauf
```

Führt `code` aus. `name` steht in einer Fehlermeldung als Datei:
der Name des Skripts. Mit `eingabe` -- einer Zeile der Konsole --
steht der Wert der letzten Zeile da, wenn sie ein Ausdruck ist, wie
in der Python-Konsole: `1 + 1` zeigt `2`.

#### Sitzung.variablen

```python
def variablen(self) -> List[Dict[str, str]]
```

Die Variablen des Namensraums, nach Namen: was der Benutzer angelegt
hat. Weggelassen werden Namen mit Unterstrich, Module, Funktionen und
Klassen -- wie im Variablen-Explorer von Spyder.

### _typ

```python
def _typ(wert: Any) -> str
```

Der Typ, wie man ihn sucht: `int`, `ndarray float64`, `DataFrame`.

### _groesse

```python
def _groesse(wert: Any) -> str
```

Wie gross: Form eines Feldes oder einer Tabelle, sonst die Länge -- leer bei Zahlen.

### _darstellung

```python
def _darstellung(wert: Any, laenge: int, *, einzeilig: bool=False) -> str
```

`repr` -- gekürzt, und für die Zeile des Beobachters in eine Zeile gelegt.

### _fehlertext

```python
def _fehlertext(fehler: BaseException, name: str) -> str
```

Die Fehlermeldung, wie Python sie schreibt -- ohne die Rahmen der Konsole
selbst: wer sein Skript liest, sucht seine Zeile, nicht unsere. Fehlt ein
Modul, steht dazu, was beiliegt.


## Konstanten

- `EIGENE = str(Path(__file__).resolve().parent)` – Wo die Konsole selbst liegt -- ihre Rahmen gehören in keine Fehlermeldung.
- `KURZ = 120` – Wie lang ein Wert in der Zeile des Beobachters wird -- und beim Darüberfahren.
- `LANG = 4000`
- `ZEICHENMODUL = 'zeichnen'` – Unter diesem Namen holt sich ein Skript das Zeichenmodul: `import zeichnen as plt`.

## Braucht

- [[opencivil.konsole.pakete]]
- [[opencivil.konsole.zeichnen]]

## Gebraucht von

- [[opencivil.konsole.dienst]]
