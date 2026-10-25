---
erzeugt: 105bb6182600
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/biegung.py
> wie ein gezeichneter Querschnitt biegt.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/biegung.py)

## VERANTWORTUNG

Ein gezeichneter Querschnitt biegt schief ([[opencivil.querschnitt.biegung#Konstanten|SCHIEF]]): unter reiner
Biegung kippt die Nulllinie, bis kein Moment um die andere Achse bleibt, und
jede Seite kann gezogen werden. Oder er biegt «einachsig» um y
([[opencivil.querschnitt.biegung#Konstanten|EINACHSIG]]): die Nulllinie bleibt waagrecht, `M_z` und `V_y`
zaehlen nicht, und gezogen wird nur unten oder oben -- wie bei der Platte.

Was davon abhaengt, steht hier, je einmal: welche Momente und Querkraefte
zaehlen, der Betrag des Moments, welche Seiten ein Nachweis ziehen laesst,
ob die Zugrichtung feststeht und welcher Bruchzustand zu einer Einwirkung
gehoert. Gewaehlt wird einmal, im Aufbau der Analyse
([[opencivil.querschnitt.analyse#Querschnittsanalyse|biegung]]). Bis
2026-10-25 fragten 17 Dateien ein `einachsig` ab, und die Regel fuer den
Bruchzustand stand dreimal da, der Betrag des Moments viermal.

Wo eine Herleitung je Art anders lautet -- die Spannung am ungerissenen
Querschnitt, der Riss der Spannung-Dehnung-Analyse --, fragt sie
[[opencivil.querschnitt.biegung#Biegung|Biegung.einachsig]].

## Inhalt

### Biegung

```python
class Biegung(ABC)
```

Wie ein gezeichneter Querschnitt biegt -- siehe Dateikopf.

- `einachsig: bool` – Ob die Nulllinie waagrecht bleibt -- fuer die Herleitungen, die je Art anders lauten.
- `zugseiten: Tuple[Zugseite, ...]` – Die Seiten, die je ein Nachweis ziehen laesst -- einachsig nur unten und oben, um z wird dann nicht nachgewiesen. Ihre Namen, «Zug unten», sind die der Faelle; die Kennungen «Zug_unten».

#### Biegung.momente

```python
@abstractmethod
def momente(self, M_y: float, M_z: float) -> Tuple[Tuple[str, float], ...]
```

Die Momente, die zaehlen, je mit ihrer Achse: `(("y", M_y), ("z", M_z))`.

#### Biegung.wirkt

```python
def wirkt(self, M_y: float, M_z: float) -> Tuple[float, float]
```

`(M_y, M_z)`, wie nachgewiesen -- was nicht zaehlt, ist null.

#### Biegung.betrag

```python
def betrag(self, M_y: float, M_z: float) -> float
```

Der Betrag des Moments, das zaehlt -- einachsig `|M_y|`.

#### Biegung.querkraft_y

```python
@abstractmethod
def querkraft_y(self, V_y: float) -> float
```

Die Querkraft in y, wie nachgewiesen -- einachsig null.

#### Biegung.neigung

```python
@abstractmethod
def neigung(self, M_y: float) -> Optional[float]
```

Die Zugrichtung, wenn sie feststeht: einachsig die der Seite, die
`M_y` zieht -- bei `M_y = 0` die untere. Sonst `None`: dann wird
sie gesucht.

#### Biegung.bruchpunkt

```python
def bruchpunkt(self, q: Any, N: float, M_y: float, M_z: float)
```

Der Bruchzustand des Querschnitts `q` bei `N`, der zum Moment
`(M_y, M_z)` gehoert: auf dem Faecher der festen Zugrichtung, sonst
in der Richtung des Moments gesucht
([[opencivil.querschnitt.interaktion#Querschnitt.in_richtung|in_richtung]]).
`None`, wenn N jenseits der reinen Zug- oder Druckkraft liegt.

#### Biegung.bei_reiner_biegung

```python
def bei_reiner_biegung(self, q: Any, seite: Zugseite)
```

Der Bruchzustand bei N = 0, der diese Seite zieht.

### Schief

```python
class Schief(Biegung)
```

Schiefe Biegung: die Nulllinie kippt, jede Seite kann gezogen werden.

- `einachsig = False`
- `zugseiten = tuple(Zugseite)`

#### Schief.momente

```python
def momente(self, M_y: float, M_z: float) -> Tuple[Tuple[str, float], ...]
```

#### Schief.querkraft_y

```python
def querkraft_y(self, V_y: float) -> float
```

#### Schief.neigung

```python
def neigung(self, M_y: float) -> Optional[float]
```

### Einachsig

```python
class Einachsig(Biegung)
```

Biegung um y allein: die Nulllinie bleibt waagrecht, M_z und V_y zaehlen nicht.

- `einachsig = True`
- `zugseiten = UM_Y`

#### Einachsig.momente

```python
def momente(self, M_y: float, M_z: float) -> Tuple[Tuple[str, float], ...]
```

#### Einachsig.querkraft_y

```python
def querkraft_y(self, V_y: float) -> float
```

#### Einachsig.neigung

```python
def neigung(self, M_y: float) -> Optional[float]
```


## Konstanten

- `SCHIEF = Schief()`
- `EINACHSIG = Einachsig()`

## Braucht

- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.nachweis.gebrauchsebene]]
- [[opencivil.nachweis.qa_kennzahlen]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
