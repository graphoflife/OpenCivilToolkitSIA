---
erzeugt: 433895654887
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/analysen.py
> die Analysen eines Projekts.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/analysen.py)

## VERANTWORTUNG

Je Bauteil -- Platte oder gezeichneter Querschnitt -- und je Fall die eine
Frage, mit dem Paar seiner Richtung und seiner Wahl, dazu die Herleitung
jeder Linie ([[opencivil.spannungsanalyse.analysen#analysen|analysen]]).

## Inhalt

### Analyse

```python
@dataclass
class Analyse
```

Ein Spannungsfall der Beschreibung -- und was die Auswertung ergab.

- `fall: Any` – Der [[opencivil.spannungsanalyse.analysen#Analyse|SpannungsfallEintrag]], wie er in der Beschreibung steht.
- `art: Analyseart`
- `richtung: Any` – Die Tragrichtung einer Platte ([[opencivil.spannungsanalyse.analysen#Analyse|Richtung]]) oder die Zugseite eines gezeichneten Querschnitts ([[opencivil.querschnitt.zugseite#Zugseite|Zugseite]]).
- `richtung_text: str = ''` – Wie sie neben dem Titel steht -- «x», «Zug unten».
- `raender: Tuple[str, str] = Zugseite.UNTEN.raender` – Wie die Raender heissen, zwischen denen das Bild laeuft: der bei z = 0 und der bei z = h -- dieselben Namen wie die Randdehnungen der Eingabe. Die Platte zaehlt z immer ab oben; der gezeichnete Querschnitt ab dem Rand gegenueber seiner Zugseite. Bis 2026-11-19 schrieb das Bild immer «ab Oberkante», auch bei Zug oben, links oder rechts.
- `bild: Optional[Querschnittsbild] = None`
- `kurve: Optional[Union[Linie, 'Modullinie']] = None` – Die M-chi- oder N-eps-Linie -- oder der aequivalente Modul daraus.
- `paar: Optional[Paar] = None` – Womit gerechnet wurde -- das Paar mit Kriechzahl, Wertesatz, Betongesetz: das der Platte oder das des gezeichneten Querschnitts.
- `hinweis: str = ''` – Warum es nichts auszuwerten gab, falls es nichts gab.

#### Analyse.moeglich

```python
@property
def moeglich(self) -> bool
```

### auswerten

```python
def auswerten(fall, art: Analyseart, paar: Paar) -> Tuple[Optional[Querschnittsbild], Optional[Union[Linie, Modullinie]]]
```

Die eine der sechs Fragen stellen, die dieser Fall stellt -- in SI, an
das Paar einer Platte oder eines gezeichneten Querschnitts. Gelesen wird
nur, was die Frage braucht ([[opencivil.spannungsanalyse.art#Analyseart.eingaben|Analyseart.eingaben]]), und in der
Einheit seines Feldes: in der zeigt die Maske die Zahl. Bis 2026-10-18
rechnete hier ein eigenes `* 1e3` -- eine zweite Angabe der Einheit,
die still um 10³ haette abweichen koennen, wie zuvor beim Grundbruch.

### _Bauteilart

```python
@dataclass(frozen=True)
class _Bauteilart
```

Wie eine Analyse zu ihrem Bauteil kommt: wo es im Aufbau steht, wie sein
Paar je Richtung entsteht, wie die Richtung neben dem Titel heisst, wie
die Raender des Bildes heissen und was dasteht, wo es kein Paar gibt.

- `teile: Callable[['Aufbau'], Mapping[str, Any]]`
- `paar: Callable[..., Optional[Paar]]`
- `richtung_text: Callable[[Any], str]`
- `raender: Callable[[Any], Tuple[str, str]]`
- `ohne_bewehrung: Callable[[Any], str]`

### analysen

```python
def analysen(aufbau: 'Aufbau', loesung: 'Loesung', protokoll: Optional[Protokoll]=None, *, nur: Optional[Collection[str]]=None) -> Dict[str, List[Analyse]]
```

Die Auswertungen am Querschnitt, je Platte und je gezeichnetem Querschnitt.

Kein Nachweis: hier steht kein Erfuellungsgrad und kein Urteil, sondern
eine Antwort auf die Frage, was im Querschnitt geschieht. Gerechnet wird
trotzdem mit demselben Faserintegral und denselben Werkstoffgesetzen wie
in den Nachweisen -- ein zweites Modell daneben waere eine zweite
Wahrheit ueber denselben Querschnitt.

Mit `protokoll` schreibt jede Linie dorthin, wie sie entstand -- daraus
sammelt die Formelsammlung ihr Thema. `nur` rechnet nur diese Bauteile:
die uebrigen hat der Zwischenspeicher der Oberflaeche noch
([[opencivil.web.dienst#rechnen|opencivil.web.dienst.rechnen]]). Eine Schleife fuer beide
Bauteilarten ([[opencivil.spannungsanalyse.analysen#Konstanten|_BAUTEILARTEN]]); bis 2026-10-17 stand die des
gezeichneten Querschnitts ein zweites Mal in dessen Modul, geladen mit
einem Import in dieser Funktion.


## Konstanten

- `_BAUTEILARTEN = (_Bauteilart(teile=lambda aufbau: aufbau.querschnitte, paar=loeserpaa…` – Die Platte je Tragrichtung, der gezeichnete Querschnitt je Zugseite.

## Braucht

- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.projekt]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse.art]]
- [[opencivil.spannungsanalyse.bild]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
