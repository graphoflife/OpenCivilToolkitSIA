---
erzeugt: f1f41968484a
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/matrix.py
> das Gleichungssystem eines Stabwerks.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/matrix.py)

## VERANTWORTUNG

Loest `K · x = f` fuer die Steifigkeitsmatrix eines Stabwerks: symmetrisch
und, solange das System haelt, positiv definit. Eine Zerlegung fuer alle
Lastfaelle; jeder ist danach nur noch eine Vorwaerts- und eine
Rueckwaertsrechnung.


## IM PROFIL GESPEICHERT

Ein Stab koppelt nur die Unbekannten seiner beiden Enden. In jeder Zeile von
K steht darum links der Diagonale wenig, und was links der ersten Zahl einer
Zeile steht, bleibt beim Zerlegen null. Gespeichert wird je Zeile nur das
Stueck von der ersten belegten Spalte bis zur Diagonale -- das Profil --,
und zerlegt wird darin. Bei 600 Unbekannten und einer Bandbreite von 30 sind
das Millisekunden; dicht gerechnet waeren es Sekunden, im Browser mehr.


## DIE NUMMERIERUNG

Wie schmal das Profil ist, haengt an der Reihenfolge der Unbekannten.
[[opencivil.stabwerk.matrix#nummerierung|nummerierung]] ordnet die Knoten nach der umgekehrten
Cuthill-McKee-Folge: Breitensuche von einem Randknoten aus, Nachbarn mit
kleinem Grad zuerst, am Ende umgedreht. Nachbarn liegen danach nahe
beieinander, gleich in welcher Reihenfolge sie gezeichnet wurden.


## SINGULAER

Ist das System beweglich, wird ein Pivot null -- bis auf Rundung. Als null
gilt `d_i <= SCHRANKE · K_ii`: gemessen an der Steifigkeit derselben
Unbekannten, nicht an einer festen Zahl, damit die Einheiten nicht zaehlen.
Dann wird nicht regularisiert -- eine Steifigkeit, die das System nicht hat,
waere erfunden --, sondern mit dieser Unbekannten festgehalten zu Ende
zerlegt. Daraus folgt die freie Bewegung ([[opencivil.stabwerk.matrix#Zerlegung.bewegung|Zerlegung.bewegung]]): die
festgehaltene Unbekannte auf eins, die uebrigen aus `K_FF · x_F = -K_Fs`.
Die Probe `|K · x|` sagt, ob es wirklich eine ist.

## Inhalt

### Profilmatrix

```python
class Profilmatrix
```

Eine symmetrische Matrix im Profil: je Zeile `i` die Werte der Spalten
`erste[i]` bis `i`. Was rechts der Diagonale steht, ist das Spiegelbild.

#### Profilmatrix.aus_gruppen

```python
@classmethod
def aus_gruppen(cls, n: int, gruppen: Iterable[Sequence[int]]) -> 'Profilmatrix'
```

Das Profil, das Gruppen gekoppelter Unbekannter brauchen -- je Stab
die seiner beiden Enden. Eine Unbekannte ohne Gruppe hat nur ihre
Diagonale.

#### Profilmatrix.addiere

```python
def addiere(self, i: int, j: int, wert: float) -> None
```

Addiert `wert` an `(i, j)` -- und damit an `(j, i)`.

#### Profilmatrix.addiere_block

```python
def addiere_block(self, indizes: Sequence[int], block: Sequence[Sequence[float]]) -> None
```

Addiert einen symmetrischen Block auf die Unbekannten `indizes`,
jedes Paar einmal. Die Indizes muessen verschieden sein -- sonst
zaehlte ein Wert doppelt.

#### Profilmatrix.wert

```python
def wert(self, i: int, j: int) -> float
```

#### Profilmatrix.diagonale

```python
def diagonale(self, i: int) -> float
```

#### Profilmatrix.mal

```python
def mal(self, x: Sequence[float]) -> List[float]
```

`K · x`.

#### Profilmatrix.eintraege

```python
@property
def eintraege(self) -> int
```

Wie viele Zahlen das Profil haelt -- ein Mass fuer die Arbeit.

### Bewegung

```python
@dataclass(frozen=True)
class Bewegung
```

Die freie Bewegung eines beweglichen Systems: eine Loesung von
`K · x = 0` mit `x_s = 1`.

- `index: int` – Die Unbekannte, an der die Zerlegung keinen Halt mehr fand.
- `x: List[float]`
- `rest: float` – `max|K · x|` bezogen auf `max K_ii · max|x|` -- nahe null bei einer echten.

### Zerlegung

```python
class Zerlegung
```

`K = L · D · Lᵀ` im Profil von `K`.

`singulaer` nennt die Unbekannten, an denen der Pivot null war; sie
sind festgehalten, und `loese` setzt sie null. Wer rechnet, prueft
vorher, ob die Liste leer ist.

#### Zerlegung.loese

```python
def loese(self, f: Sequence[float]) -> List[float]
```

`x` aus `K · x = f`; festgehaltene Unbekannte sind null.

#### Zerlegung.bewegung

```python
def bewegung(self) -> Optional[Bewegung]
```

Die freie Bewegung an der ersten Unbekannten ohne Halt -- `None`,
wenn das System haelt.

### _ebenen

```python
def _ebenen(start: H, nachbarn: Mapping[H, Iterable[H]]) -> List[List[H]]
```

Die Ebenen der Breitensuche von `start` aus.

### nummerierung

```python
def nummerierung(knoten: Sequence[H], nachbarn: Mapping[H, Iterable[H]]) -> List[H]
```

Die Knoten in umgekehrter Cuthill-McKee-Folge -- je zusammenhaengendem
Teil von einem Randknoten aus. Bei gleichem Grad entscheidet die
Reihenfolge von `knoten`; so ist die Folge fest.

### dicht

```python
def dicht(K: Profilmatrix) -> List[List[float]]
```

Die volle Matrix -- fuer die Herleitung kleiner Systeme und fuer Proben.


## Konstanten

- `SCHRANKE = 1e-10` – Unter diesem Anteil seiner eigenen Steifigkeit gilt ein Pivot als null. Zehn Groessenordnungen: so weit liegen Dehn- und Biegesteifigkeit eines schlanken Stabs nie auseinander, eine echte Bewegung aber immer -- dort bleibt nur die Rundung, rund 1e-16.
- `H = TypeVar('H', bound=Hashable)`

## Gebraucht von

- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk.system]]
