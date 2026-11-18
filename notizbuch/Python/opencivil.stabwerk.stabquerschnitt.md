---
erzeugt: e449d5eede3d
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/stabquerschnitt.py
> woher A und I eines Stabs kommen.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/stabquerschnitt.py)

## VERANTWORTUNG

Ein Querschnitt der Staebe, aufgeloest: je Art eine Klasse, die ihre
Berechnungen fuer die Kennwerte des Stabs und ihren Umriss selbst traegt.
Welche Kennwerte, sagt das System: der ebene Rahmen braucht `A` und `I`
([[opencivil.stabwerk.stabquerschnitt#Konstanten|EBEN]]), das Stabwerk im Raum `A`, `I_y`, `I_z` und `I_T`
([[opencivil.stabwerk.stabquerschnitt#Konstanten|RAEUMLICH]]). Die Arten --

* nach Vorlage ([[opencivil.stabwerk.stabquerschnitt#NachVorlage|NachVorlage]]) -- die Formeln der Vorlage
  ([[opencivil.stabwerk.querschnitte|querschnitte]]), die Masse als Vorgaben; ein
  Stahlprofil ebenso, mit den Massen aus der Tabelle
  ([[opencivil.stabwerk.profilformen|profilformen]]). Das `I` des ebenen Rahmens
  ist ihr `I_y` -- bei einem Profil, das sich um z biegt, ihr `I_z`;
* von Hand ([[opencivil.stabwerk.stabquerschnitt#VonHand|VonHand]]) -- die Kennwerte als Eingaben;
* aus einer Platte ([[opencivil.stabwerk.stabquerschnitt#AusPlatte|AusPlatte]]) -- die Formeln des Rechtecks mit
  `b` und `h` der Platte, im Raum mit `I_z` und `I_T` dazu;
* aus einer Querschnittsanalyse ([[opencivil.stabwerk.stabquerschnitt#AusAnalyse|AusAnalyse]]) -- `A` und `I_y`
  ihres Bruttoquerschnitts, im Raum `I_z` dazu und `I_T`, das sie dafuer
  numerisch rechnet ([[opencivil.querschnitt.torsion|torsion]]).

Ueber die Werte der Platte und der Analyse haengt das System im Rechengraph
an ihnen: aendert sich deren Dicke, rechnet es neu. Nur ein Querschnitt aus
einem Bauteil ([[opencivil.stabwerk.stabquerschnitt#AusBauteil|AusBauteil]]) kann ein E_eq haben.

Bis 2026-10-25 war die Art ein Text, und vier Schichten fragten ihn je fuer
sich ab: die Beschreibung, der Aufbau, das Rechenwerk und das Bildchen
einer Zeile. Jetzt loest der Aufbau ihn einmal auf
([[opencivil.projekt.aufbau.balkensystem]]).

## Inhalt

### Kennwert

```python
@dataclass(frozen=True)
class Kennwert
```

Ein Wert, den ein Stab von seinem Querschnitt braucht -- wie er heisst und gezeigt wird.

- `kurzname: str`
- `einheit: Einheit`
- `stellen: int`
- `beschreibung: str`

### Stabquerschnitt

```python
@dataclass(frozen=True, kw_only=True)
class Stabquerschnitt(ABC)
```

Ein Querschnitt der Staebe, aufgeloest: woher `A` und `I` kommen.

- `kennung: str`
- `name: str`
- `herkunft: str` – Woher, in Worten -- «Rechteck», «von Hand», «Platte «Decke»».
- `fehler: str = ''` – Was nicht geht -- dann rechnet er nicht, und kein Stab mit ihm.

#### Stabquerschnitt.bauteil

```python
@property
def bauteil(self) -> str
```

Die Kennung der Platte oder Analyse, deren Werte er liest -- leer bei einer Form.

#### Stabquerschnitt.modulfrage

```python
@property
def modulfrage(self) -> Optional[Any]
```

Die Frage nach seinem E_eq -- nur einer aus einem Bauteil kann eine haben.

#### Stabquerschnitt.flaechenwerte

```python
@abstractmethod
def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str, kennwerte: Sequence[Kennwert]=EBEN) -> Tuple[List[Berechnung], Werte]
```

Die Berechnungen fuer die `kennwerte` -- und je Kennwert seine Wert-ID.

#### Stabquerschnitt.umriss

```python
def umriss(self, loesung: Any) -> Umriss
```

Sein Umriss in mm, fuer das Bildchen seiner Zeile -- ohne einen leer.

#### Stabquerschnitt._formeln

```python
def _formeln(self, vorlage: Stabvorlage, quellen: Mapping[str, str], definieren: Definieren, abschnitt: Abschnitt, index: str, kennwerte: Sequence[Kennwert], traegheit: str='I_y') -> Tuple[List[Berechnung], Werte]
```

Die Formeln einer Vorlage, aus den Wert-IDs ihrer Masse -- je
Kennwert die mit seinem Kurznamen, als `I` des ebenen Rahmens die
mit dem Kurznamen `traegheit`. Gerechnet wird davon nur, was die
Kennwerte brauchen: das Rechenwerk folgt den Zielen.

#### Stabquerschnitt._je_kennwert

```python
def _je_kennwert(self, definieren: Definieren, index: str, kennwerte: Sequence[Kennwert], berechnung: Callable[[WertDef, Kennwert], Berechnung]) -> Tuple[List[Berechnung], Werte]
```

Jeder Kennwert als eine Berechnung -- von Hand eine Vorgabe, sonst ein Bezug.

### NachVorlage

```python
@dataclass(frozen=True, kw_only=True)
class NachVorlage(Stabquerschnitt)
```

Nach einer Vorlage: ihre Masse als Vorgaben, ihre Formeln.

- `vorlage: Stabvorlage`
- `masse: Mapping[str, float]` – Die Masse der Vorlage in mm -- was fehlte, mit seiner Vorgabe.
- `traegheit: str = 'I_y'` – Welche ihrer Formeln das `I` des ebenen Rahmens ist -- bei einem Profil um z `I_z`.

#### NachVorlage.flaechenwerte

```python
def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str, kennwerte: Sequence[Kennwert]=EBEN) -> Tuple[List[Berechnung], Werte]
```

#### NachVorlage.umriss

```python
def umriss(self, loesung: Any) -> Umriss
```

### VonHand

```python
@dataclass(frozen=True, kw_only=True)
class VonHand(Stabquerschnitt)
```

Kennwerte von Hand: `A` in mm², die Traegheitsmomente in 10⁶ mm⁴. Ein Umriss fehlt.

- `masse: Mapping[str, float]`

#### VonHand.flaechenwerte

```python
def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str, kennwerte: Sequence[Kennwert]=EBEN) -> Tuple[List[Berechnung], Werte]
```

### AusBauteil

```python
@dataclass(frozen=True, kw_only=True)
class AusBauteil(Stabquerschnitt)
```

Aus einem Bauteil des Projekts -- seine Werte gehen ein, und er kann ein E_eq haben.

- `bezug: str` – Die Kennung der Platte oder Analyse.
- `quelle: Mapping[str, str] = field(default_factory=dict)` – Die Wert-IDs, aus denen er rechnet.
- `eq: Optional[Any] = None` – Die Frage nach seinem E_eq ([[opencivil.spannungsanalyse.modul#Modulfrage|Modulfrage]]) -- sie gilt fuer die Staebe, die sein Material nehmen; `None`: E_cm. Sie baut ihre Berechnungen selbst ein.

#### AusBauteil.bauteil

```python
@property
def bauteil(self) -> str
```

#### AusBauteil.modulfrage

```python
@property
def modulfrage(self) -> Optional[Any]
```

### AusPlatte

```python
@dataclass(frozen=True, kw_only=True)
class AusPlatte(AusBauteil)
```

Der Streifen `b × h` einer Platte -- `quelle` sind `b` und `h`.

#### AusPlatte.flaechenwerte

```python
def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str, kennwerte: Sequence[Kennwert]=EBEN) -> Tuple[List[Berechnung], Werte]
```

#### AusPlatte.umriss

```python
def umriss(self, loesung: Any) -> Umriss
```

### AusAnalyse

```python
@dataclass(frozen=True, kw_only=True)
class AusAnalyse(AusBauteil)
```

Der Bruttoquerschnitt einer Querschnittsanalyse -- `quelle` je Kennwert, `I` ist `I_y`.

- `flaechen: Tuple[Sequence[Tuple[float, float]], ...] = ()` – Die Polygone ihrer Flaechen, in mm -- Aussparungen mit, das Bild fuellt gerade-ungerade.

#### AusAnalyse.flaechenwerte

```python
def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str, kennwerte: Sequence[Kennwert]=EBEN) -> Tuple[List[Berechnung], Werte]
```

#### AusAnalyse.umriss

```python
def umriss(self, loesung: Any) -> Umriss
```

### _stellen

```python
def _stellen(wert: float) -> int
```

So viele Nachkommastellen, wie ein Mass hat -- 8.75 bleibt 8.75, bis drei.


## Konstanten

- `Definieren = Callable[[str, str, Einheit, str, int], WertDef]` – Wie das System einen Wert anlegt: Kurzname, Zeichen, Einheit, Beschreibung, Stellen.
- `Umriss = List[Sequence[Tuple[float, float]]]` – Ein Umriss in mm -- der erste aussen, die weiteren Loecher.
- `_A = Kennwert('A', MM2, 0, 'Querschnittsfläche')`
- `EBEN = (_A, Kennwert('I', MIO_MM4, 2, 'Flächenträgheitsmoment'))` – Was ein Stab des ebenen Rahmens braucht: `I` um die Achse senkrecht zur Ebene.
- `RAEUMLICH = (_A, Kennwert('I_y', MIO_MM4, 2, 'Flächenträgheitsmoment um y'), Kenn…` – Was ein Stab im Raum braucht ([[opencivil.stabwerk3d]]).
- `Werte = Dict[str, str]` – Je Kennwert die Wert-ID, die ihn liefert.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.stabwerk.querschnitte]]

## Gebraucht von

- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk3d.rechnung]]
