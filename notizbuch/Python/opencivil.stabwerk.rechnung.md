---
erzeugt: 3dc38943433d
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/rechnung.py
> das Balkensystem im Rechenwerk.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/rechnung.py)

## VERANTWORTUNG

Was ein Balkensystem im Rechenwerk anmeldet: je Querschnitt die Flaeche
`A` und das Traegheitsmoment `I`, je Paar aus Querschnitt und Material
die Dehn- und die Biegesteifigkeit `EA` und `EI`, und eine Prozedur, die
das System nach der Steifigkeitsmethode rechnet
([[opencivil.stabwerk.system|system]]) und ihre Herleitung schreibt
([[opencivil.stabwerk.herleitung|herleitung]]).


## WOHER A UND I KOMMEN

* nach Vorlage -- die Formeln der Vorlage
  ([[opencivil.stabwerk.querschnitte|querschnitte]]), die Masse als Vorgaben;
* von Hand -- A und I als Eingaben;
* aus einer Platte -- die Formeln des Rechtecks mit `b` und `h` der
  Platte;
* aus einer Querschnittsanalyse -- `A` und `I_y` ihres
  Bruttoquerschnitts.

Ueber die Werte der Platte und der Analyse haengt das System im Rechengraph
an ihnen: aendert sich deren Dicke, rechnet es neu.


## STEIFIGKEIT -- NACH VORGABE, NICHT NACHGESCHLAGEN

`E_cm` fuer Beton und `E_s` fuer Betonstahl ([[opencivil.stabwerk.rechnung#Konstanten|E_MODUL]]), am
ungerissenen Bruttoquerschnitt, ohne Schubverformung, Gleichgewicht am
unverformten System. Die Herleitung sagt es, das TODO fuehrt es.


## DAS ERGEBNIS

kommt als Befund in die Loesung ([[opencivil.stabwerk.rechnung#Systembefund|Systembefund]]); Zusammenfassung,
Bilder und Zwischenspeicher lesen es dort. Als Wert des Rechenwerks liefert
die Prozedur nur die Zahl der Unbekannten -- die gibt es immer, auch bei
einem beweglichen System. Das ist ein Ergebnis mit Meldung und keine
Ausnahme: der Rest des Projekts rechnet weiter.

## Inhalt

### Stabquerschnitt

```python
@dataclass(frozen=True)
class Stabquerschnitt
```

Ein Querschnitt der Staebe, aufgeloest: woher `A` und `I` kommen.

- `kennung: str`
- `name: str`
- `art: str` – `vorlage`, `kennwerte`, `platte` oder `analyse`.
- `vorlage: Optional[Stabvorlage] = None`
- `masse: Mapping[str, float] = field(default_factory=dict)` – Die Masse der Vorlage in mm -- bei Kennwerten `A` in mm² und `I` in 10⁶ mm⁴.
- `quelle: Mapping[str, str] = field(default_factory=dict)` – Die Wert-IDs, aus denen er rechnet: `b` und `h` einer Platte, `A` und `I` einer Analyse.
- `bezug: str = ''` – Die Kennung der Platte oder Analyse, aus der er kommt.
- `herkunft: str = ''` – Woher, in Worten -- «Rechteck», «von Hand», «Platte «Decke»».
- `fehler: str = ''` – Was an seinen Massen nicht geht -- dann rechnet er nicht, und kein Stab mit ihm.

### Steifigkeit

```python
@dataclass(frozen=True)
class Steifigkeit
```

Ein Paar aus Querschnitt und Material und die Wert-IDs seiner Steifigkeiten.

- `querschnitt: str`
- `material: str` – Die Kennung des Materials im Projekt.
- `EA: str`
- `EI: str`

### Systembefund

```python
@dataclass
class Systembefund
```

Was die Steifigkeitsmethode im Lauf fand: das System mit seinen
Steifigkeiten, wie es gerechnet wurde, und sein Ergebnis -- Meldungen,
Faelle mit Verschiebungen und Lagerkraeften, in SI. Die Verlaeufe eines
Falls rechnet [[opencivil.stabwerk.rechnung#Systembefund.verlaeufe|verlaeufe]] einmal, wenn jemand sie braucht.

- `gerechnet: System`
- `ergebnis: Ergebnis`
- `_verlaeufe: Dict[str, Dict[str, Stabverlauf]] = field(default_factory=dict, repr=False)`

#### Systembefund.verlaeufe

```python
def verlaeufe(self, fall: str) -> Dict[str, Stabverlauf]
```

Je Stab der Verlauf der Schnittgroessen und der Biegelinie in einem Fall -- einmal gerechnet.

### SteifigkeitsmethodeProzedur

```python
class SteifigkeitsmethodeProzedur(Prozedur)
```

Das ganze System, gerechnet und aufgeschrieben.

- `THEMA = STEIFIGKEITSMETHODE`

#### SteifigkeitsmethodeProzedur.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

### Balkensystem

```python
class Balkensystem
```

Ein Balkensystem, fertig fuer das Rechenwerk.

#### Balkensystem.abschnitt

```python
def abschnitt(self, thema: str=STEIFIGKEITSMETHODE) -> Abschnitt
```

Ein Abschnitt fuer alles -- das Thema sagt nur, wo die Formeln gesammelt stehen.

#### Balkensystem.bezuege

```python
@property
def bezuege(self) -> List[str]
```

Die Platten und Analysen, deren Werte das System liest.

#### Balkensystem._querschnitt

```python
def _querschnitt(self, q: Stabquerschnitt, index: str) -> Tuple[str, str]
```

Die Berechnungen fuer A und I eines Querschnitts -- und ihre Wert-IDs.

#### Balkensystem._steifigkeit

```python
def _steifigkeit(self, q: str, material: str, index: str) -> Steifigkeit
```

EA und EI eines Paars aus Querschnitt und Material.

#### Balkensystem.ins_rechenwerk

```python
def ins_rechenwerk(self, werk) -> 'Balkensystem'
```

#### Balkensystem.ziele

```python
def ziele(self) -> List[str]
```

Was ein Lauf rechnen muss: jeder Querschnitt -- auch einer, den kein Stab nimmt -- und das System.

#### Balkensystem.rechnen_und_schreiben

```python
def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

Die Steifigkeiten in die Staebe, das System gerechnet, die Herleitung
geschrieben. Haelt eine Meldung der Beschreibung die Rechnung auf,
bleibt es bei ihr.


## Konstanten

- `E_MODUL = {'beton': 'E_cm', 'betonstahl': 'E_s'}` – Welcher E-Modul in die Steifigkeit eingeht, je Art des Materials -- nach Vorgabe, nicht nachgeschlagen.
- `QUERSCHNITTE = 'Stabquerschnitte'` – Die Themen der Formelsammlung: was am Querschnitt haengt, und die Rechnung.
- `STEIFIGKEITSMETHODE = 'Steifigkeitsmethode'`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk.verlauf]]

## Gebraucht von

- [[opencivil.ergebnis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.web.balkendaten]]

## Formeln aus diesem Modul

- [[Biegesteifigkeit]] · `_biegesteifigkeit`
- [[Dehnsteifigkeit]] · `_dehnsteifigkeit`
