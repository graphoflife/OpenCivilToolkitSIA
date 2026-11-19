---
erzeugt: 2a5fc787d514
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/fallnamen.py
> Die Namen der Faelle eines Bauteils -- je Liste verschieden, auch als Kennung.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/fallnamen.py)

Die Nachweise legen ihre Ergebniswerte unter dem Fallnamen ab -- M-N,
Querkraft und Stahlspannung alle drei. Zwei Kombinationen gleichen Namens
fielen darum auf einen Eintrag zusammen: der zweite ueberschrieb den ersten,
und in der Tabelle fehlte eine Zeile. Kein Fehler, keine Warnung, eine Zahl
weniger.

Verschiedene Namen koennen dieselbe Kennung ergeben: «Wand A» und «Wand-A»
werden beide zu «Wand_A» ([[opencivil.core.wert#kennung_aus|kennung_aus]]). Das
Rechenwerk wiese den zweiten zurueck, aber mit einer Meldung ueber Wert-IDs,
die an der Maske niemand versteht. Bis 2026-10-17 pruefte das nur drei der
neun Listen.

Gemeldet statt umbenannt: welcher der beiden gemeint war, weiss nur der
Benutzer, und ein von selbst angehaengtes «(2)» stuende danach in seinem
Bericht. Eine Regel, an zwei Orten gefragt:

* am Namensfeld, bevor es einen Namen uebernimmt ([[opencivil.projekt.fallnamen#Fallnamen.grund|Fallnamen.grund]],
  `fallname` im Dienst). Bis 2026-11-19 nahm das Feld jeden Namen, und erst
  das Bauteil sagte oben im Fenster, dass er doppelt ist -- die sechs Fenster
  der Spannung-Dehnung-Analysen teilen sich aber eine Liste, und der
  Doppelgaenger stand oft in einem, das nicht offen war. Darum sagt die
  Meldung, wo der andere steht (Benutzer, 2026-11-19);
* vor dem Rechnen ([[opencivil.projekt.fallnamen#Fallnamen.pruefen|Fallnamen.pruefen]]), fuer eine bearbeitete Datei.
  Nicht beim Oeffnen: ein Projekt, das sich wegen zweier gleicher Namen
  nicht mehr oeffnen liesse, waere schlimmer als eine Meldung.

Welche Listen ein Bauteil hat, sagt es selbst (`fallnamen()` jedes
Eintrags, ohne eigene keine).

## Inhalt

### Fallnamen

```python
@dataclass(frozen=True)
class Fallnamen
```

Eine Liste von Faellen eines Bauteils, deren Namen sich unterscheiden muessen.

- `pfad: str` – Wo die Liste im Bauteil steht, mit Punkten: `knickfaelle`, `verformung.faelle`.
- `was: str` – Wie ein Fall der Liste in der Meldung heisst: «Knicknachweis».
- `namen: Tuple[Benannt, ...]` – Je Fall der Liste Name und Ort, in ihrer Reihenfolge.
- `vergeben: Tuple[Benannt, ...] = ()` – Namen, die in der Liste schon gelten, ohne dass ein Fall darin sie traegt -- die aus der Tragsicherheit abgeleiteten Lastfaelle.

#### Fallnamen.aus

```python
@classmethod
def aus(cls, pfad: str, was: str, faelle: Iterable[Any], ort: Callable[[Any], str]=lambda fall: '', vergeben: Iterable[Benannt]=()) -> Fallnamen
```

Aus den Faellen selbst; `ort` sagt je Fall, wo er steht.

#### Fallnamen.grund

```python
def grund(self, index: int, name: str) -> str
```

Warum der Fall an `index` nicht `name` heissen darf -- leer, wenn
er darf. Fuer das Namensfeld: der Name gegen jeden anderen der Liste.

#### Fallnamen.pruefen

```python
def pruefen(self, wo: str) -> None
```

Vor dem Rechnen: jeder Name gegen die vor ihm. `wo` nennt das Bauteil.

#### Fallnamen._grund

```python
def _grund(self, name: str, andere: Iterable[Benannt]) -> str
```

«Feld» ist als Verformungsfall schon vergeben -- oder leer.


## Konstanten

- `Benannt = Tuple[str, str]` – Ein Name und was die Meldung ueber seinen Ort sagt -- leer, wo alle Faelle der Liste in einem Fenster stehen: «, im Fenster «Momenten-Krümmungs-Linie»».

## Braucht

- [[opencivil.core.wert]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.pfahl]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.querschnittsanalyse]]
