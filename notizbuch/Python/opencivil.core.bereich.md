---
erzeugt: 2dbd81474d3a
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/bereich.py
> wo eine Zahl liegen muss.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/bereich.py)

## VERANTWORTUNG

Ein [[opencivil.core.bereich#Bereich|Bereich]] sagt von einer Zahl, die jemand eingibt, wie sie heisst,
in welcher Einheit sie gemeint ist und wo sie liegen muss -- und mit welchem
Satz er sie abweist ([[opencivil.core.bereich#Bereich.grund|Bereich.grund]]). Derselbe Bereich beschreibt das
Feld eines Eintrags ([[opencivil.projekt.lesen#bereich|opencivil.projekt.lesen.bereich]]), den Kennwert
eines Baustoffs, das Mass einer Vorlage
([[opencivil.querschnitt.vorlagen#Mass|opencivil.querschnitt.vorlagen.Mass]]) und den Kennwert eines
Stabquerschnitts von Hand ([[opencivil.stabwerk.stabquerschnitt#Kennwert|opencivil.stabwerk.stabquerschnitt.Kennwert]]).
Die Oberflaeche bekommt von jedem dieselbe Angabe ([[opencivil.core.bereich#Bereich.angabe|Bereich.angabe]])
und weist eine Zahl schon am Feld mit dem Satz ab, der sonst beim Rechnen
kaeme.

Bis 2026-11-20 stand er bei den Feldern des Projekts, und die Vorlagen
prueften ihre Masse selbst: mit eigenen Saetzen, und die Oberflaeche mit
eigenen Mindestwerten -- 1 in der Querschnittsanalyse, 0 im Balkensystem.

## Inhalt

### Bereich

```python
@dataclasses.dataclass(frozen=True)
class Bereich
```

Wo eine Zahl liegen muss -- jede Grenze darf fehlen, `ueber` und
`unter` schliessen die Grenze aus, `ab` und `bis` ein.

- `heisst: str` – Wie die Zahl in der Meldung heisst -- wie an der Maske: «Dicke h».
- `einheit: Optional[Einheit] = None`
- `ueber: Optional[float] = None`
- `ab: Optional[float] = None`
- `bis: Optional[float] = None`
- `unter: Optional[float] = None`
- `bis_feld: Optional[str] = None` – Ein Feld desselben Eintrags, dessen Zahl diese nicht uebersteigen darf: α_min nicht ueber α_max. Die Regel steht so einmal, beim kleineren Feld. Die Maske weist sie an beiden Feldern ab ([[opencivil.projekt.lesen#feldangaben|feldangaben]]), die Pruefung vor dem Rechnen haelt eine Datei damit auf -- mit denselben Worten ([[opencivil.core.bereich#Bereich.gegen|gegen]]).

#### Bereich.grund

```python
def grund(self, wert: float) -> str
```

Was an `wert` nicht geht, als Satz mit Punkt -- leer, wenn er im Bereich liegt.

#### Bereich.verlangt

```python
@property
def verlangt(self) -> str
```

Was die Grenzen verlangen: «muss grösser als null sein».

#### Bereich.gegen

```python
def gegen(self, anderer: Bereich) -> Tuple[str, str]
```

Was [[opencivil.core.bereich#Bereich|bis_feld]] verlangt, an diesem Feld und am anderen
(`anderer`): «α_min darf nicht grösser sein als α_max», «α_max darf
nicht kleiner sein als α_min».

#### Bereich.grund_gegen

```python
def grund_gegen(self, wert: Optional[float], anderer: Bereich, grenze: Optional[float]) -> str
```

Was [[opencivil.core.bereich#Bereich|bis_feld]] verletzt -- die Zahl ueber der des anderen
Feldes --, als Satz mit Punkt; leer, wenn nichts.

#### Bereich.zahl

```python
def zahl(self, wert: float) -> str
```

Eine Zahl mit der Einheit: «300 mm», «30°», «0.9».

#### Bereich.angabe

```python
def angabe(self) -> Dict[str, Any]
```

Was die Oberflaeche von ihm wissen muss -- die Einheit, ob sie an der
Zahl klebt («30°»), und, hat er Grenzen, die Grenzen mit dem Satz, den
eine verletzte sagt.


## Braucht

- [[opencivil.core.einheiten]]

## Gebraucht von

- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.vorlagen]]
- [[opencivil.stabwerk.stabquerschnitt]]
