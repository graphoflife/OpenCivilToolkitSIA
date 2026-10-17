---
erzeugt: 444d7b5e5d75
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/bild.py
> das Bild eines Querschnitts.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/bild.py)

## VERANTWORTUNG

Die ersten zwei Fragen: aus Schnittgroessen oder aus Randdehnungen die
Dehnung und die Spannung ueber die Hoehe, die Kraefte des Stahls und die
Nulllinie ([[opencivil.spannungsanalyse.bild#Querschnittsbild|Querschnittsbild]]).

## Inhalt

### Faserpunkt

```python
@dataclass(frozen=True)
class Faserpunkt
```

Eine Stelle ueber die Hoehe, mit dem, was dort geschieht.

- `z: float` – Abstand vom **oberen Rand**, in m -- dem gedrueckten bei positivem Moment. Dieselbe Achse, die der Loeser und der Lagenaufbau benutzen. Fuer eine Platte ist es die Oberkante: die 1. Lage liegt bei `z = h - Randabstand` und die 4. bei `z = Randabstand`. Wer hier umdrehte, bekaeme ein Bild, das zum Nachweis nicht passt. Beim gezeichneten Querschnitt der Rand gegenueber der Zugseite.
- `eps: float`
- `sigma: float` – in Pa, Zug positiv.

### Stahlpunkt

```python
@dataclass(frozen=True)
class Stahlpunkt(Faserpunkt)
```

Dasselbe fuer eine Bewehrungslage.

- `nummer: int`
- `a_s: float`
- `kraft: float` – `sigma * a_s` in N -- was die Lage traegt.
- `name: str = ''` – Wie die Lage heisst -- «2. Lage Grundbewehrung», «Linie 1».

### Querschnittsbild

```python
@dataclass
class Querschnittsbild
```

Dehnungsebene, Spannungen und die daraus entstehenden Schnittgroessen.

- `eps_m: float`
- `chi: float`
- `N: float`
- `M: float`
- `beton: List[Faserpunkt] = field(default_factory=list)`
- `stahl: List[Stahlpunkt] = field(default_factory=list)`
- `konvergiert: bool = True`
- `hinweis: str = ''`

#### Querschnittsbild.nulllinie

```python
@property
def nulllinie(self) -> Optional[float]
```

Wo die Dehnung null wird, von der Oberkante aus.

`None`, wenn der ganze Querschnitt auf einer Seite liegt -- dann
gibt es keine Nulllinie, und eine hinzurechnen hiesse, eine Zahl zu
zeigen, die es nicht gibt.

### _bild

```python
def _bild(loeser: Faserloeser, eps_m: float, chi: float) -> Querschnittsbild
```

Dehnungen und Spannungen zu einer gegebenen Ebene -- ohne jede Suche.

### aus_schnittgroessen

```python
def aus_schnittgroessen(loeser: Faserloeser, *, N: float, M: float, art: Rechenart) -> Querschnittsbild
```

Die Dehnungsebene zu `N` und `M`, samt allem, was darauf steht.

Gesucht wird mit demselben Verfahren wie in den Nachweisen. Findet sich
keine Ebene, kommt das Bild leer zurueck und sagt warum -- geraten wird
nicht. Verfehlt die Suche ihre Ebene, sagt es die Rechenart `art`
([[opencivil.querschnitt.gesetzwahl#Rechenart.ohne_ebene|Rechenart.ohne_ebene]]).

### aus_dehnungen

```python
def aus_dehnungen(loeser: Faserloeser, *, eps_oben: float, eps_unten: float) -> Querschnittsbild
```

Der umgekehrte Weg: die Ebene ist gegeben, gesucht sind die Kraefte.

Hier gibt es nichts zu suchen -- aus den beiden Randdehnungen folgen
Mitteldehnung und Kruemmung unmittelbar, und das Faserintegral liefert
Normalkraft und Moment in einem Durchgang.


## Konstanten

- `STUETZSTELLEN = 41` – Punkte ueber die Hoehe, mit denen Dehnung und Spannung gezeichnet werden. Die Betonspannung hat am Nulldurchgang einen Knick; 41 Punkte zeigen ihn, ohne dass die Kurve eckig wird.

## Braucht

- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]
