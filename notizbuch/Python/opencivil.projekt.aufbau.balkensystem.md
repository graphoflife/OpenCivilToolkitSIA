---
erzeugt: 43e8d36d5d02
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/balkensystem.py
> ein Balkensystem wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/balkensystem.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.balkensystem#BalkensystemEintrag|BalkensystemEintrag]] das
Stabwerk in SI mit seinen Meldungen ([[opencivil.projekt.aufbau.balkensystem#modell_von|modell_von]]) und daraus die
Rechnung mit aufgeloesten Materialien und Querschnitten ([[opencivil.projekt.aufbau.balkensystem#bauen|bauen]]). Ein
Material ist ein Beton des Projekts oder ein eigenes. Die Art eines
Querschnitts wird hier aufgeloest, einmal: je Art eine Klasse
([[opencivil.stabwerk.stabquerschnitt|stabquerschnitt]]). Ein Querschnitt kann eine
Platte oder eine Querschnittsanalyse des Projekts nehmen; die muessen dann
schon gebaut sein -- darum kommt das Balkensystem in
[[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] nach ihnen. Von dort kommt auch
das Material einer Linie «gemäss Querschnitt»: der Beton der Platte oder
der Analyse.

## Inhalt

### Modell

```python
@dataclass
class Modell
```

Das Stabwerk der Beschreibung, in N, m und rad -- noch ohne
Steifigkeiten: `EA` und `EI` jedes Stabs kommen aus dem Rechenwerk,
je Paar aus Querschnitt und Material (`paare`). Was sich nicht
uebersetzen laesst, steht in `meldungen`, wie die des Rechenkerns.

- `system: System`
- `paare: Dict[str, Tuple[str, str]] = field(default_factory=dict)` – Je tragenden Stab die Kennungen seines Querschnitts und seines Materials.
- `meldungen: List[Meldung] = field(default_factory=list)`
- `eigengewicht: Optional[str] = None` – Der Name des Lastfalls, der das Eigengewicht der Staebe bekommt -- oder keiner.

#### Modell.gueltig

```python
@property
def gueltig(self) -> bool
```

### modell_von

```python
def modell_von(eintrag: BalkensystemEintrag) -> Modell
```

Das Stabwerk zum Rechnen, in SI ([[opencivil.stabwerk.modell]]).

Ein Stab ohne Querschnitt oder Material -- oder mit einem Material,
das es im System nicht gibt --, ein Querschnitt mit unmoeglichen
Massen und eine Feder ohne Steifigkeit sind Fehler, die die Meldungen
nennen: gerechnet wird dann nicht -- und nicht etwa mit einem Stab
weniger. Ob ein Material traegt, weiss erst der Aufbau: er kennt die
Betone des Projekts. Eine Last, deren Lastfall es nicht gibt, und ein
Beiwert dafuer bleiben mit einem Hinweis weg.

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: BalkensystemEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Balkensystem: das Stabwerk der Beschreibung, seine Materialien und
Querschnitte aufgeloest. Hart scheitert nur ein Verweis, den es nicht
gibt -- ein Beton, eine Platte, eine Querschnittsanalyse --; was dem
System selbst fehlt, steht in seinen Meldungen, und der Rest des
Projekts rechnet.

### _stabquerschnitt

```python
def _stabquerschnitt(q: StabquerschnittEintrag, aufbau: Aufbau, wo: str) -> Stabquerschnitt
```

Woher A und I eines Querschnitts kommen -- hier wird seine Art
aufgeloest. Die Platte oder Analyse dazu muss es geben.

### _modulfrage

```python
def _modulfrage(q: StabquerschnittEintrag, quelle) -> Optional[Modulfrage]
```

Die Frage nach dem E_eq eines Querschnitts -- nur, wenn er es nehmen soll.

### _paare

```python
def _paare(eintrag: BalkensystemEintrag, modell: Modell, aufbau: Aufbau, wo: str) -> Tuple[Dict[str, Tuple[str, Stabmaterial]], List[Meldung]]
```

Je tragenden Stab sein Querschnitt und sein Material, aufgeloest --
«gemäss Querschnitt» wird zum Beton der Platte oder Analyse. Traegt das
Material nicht, sagt es eine Meldung, und das System rechnet nicht.

### _beton

```python
def _beton(kennung: str, aufbau: Aufbau, wo: str) -> Baustoff
```

Ein Beton des Projekts -- einen Verweis ins Leere gibt es nicht.

### _stabmaterial

```python
def _stabmaterial(m: StabmaterialEintrag, aufbau: Aufbau, wo: str) -> Tuple[Optional[Stabmaterial], str]
```

Ein Material des Systems, aufgeloest: ein Beton des Projekts oder ein
eigenes. Traegt es nicht, ist es `None`, und der zweite Teil sagt
warum -- klein beginnend, er folgt auf ein «aber».

### _material_des_querschnitts

```python
def _material_des_querschnitts(q: StabquerschnittEintrag, aufbau: Aufbau) -> Tuple[Optional[Stabmaterial], str]
```

Das Material, das ein Querschnitt mitbringt: der Beton einer Platte, das
eine Material der Flaechen einer Analyse. Sonst `None`, und der zweite
Teil sagt, warum.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.basis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.faelle]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.lesen]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.stabquerschnitt]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
