---
erzeugt: 8b2c629e7e38
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/stabquerschnitt.py
> woher A und I eines Stabs kommen.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/stabquerschnitt.py)

## VERANTWORTUNG

Ein Querschnitt der Staebe, aufgeloest: je Art eine Klasse, die ihre
Berechnungen fuer `A` und `I` und ihren Umriss selbst traegt --

* nach Vorlage ([[opencivil.stabwerk.stabquerschnitt#NachVorlage|NachVorlage]]) -- die Formeln der Vorlage
  ([[opencivil.stabwerk.querschnitte|querschnitte]]), die Masse als Vorgaben;
* von Hand ([[opencivil.stabwerk.stabquerschnitt#VonHand|VonHand]]) -- `A` und `I` als Eingaben;
* aus einer Platte ([[opencivil.stabwerk.stabquerschnitt#AusPlatte|AusPlatte]]) -- die Formeln des Rechtecks mit
  `b` und `h` der Platte;
* aus einer Querschnittsanalyse ([[opencivil.stabwerk.stabquerschnitt#AusAnalyse|AusAnalyse]]) -- `A` und `I_y`
  ihres Bruttoquerschnitts.

Ueber die Werte der Platte und der Analyse haengt das System im Rechengraph
an ihnen: aendert sich deren Dicke, rechnet es neu. Nur ein Querschnitt aus
einem Bauteil ([[opencivil.stabwerk.stabquerschnitt#AusBauteil|AusBauteil]]) kann ein E_eq haben.

Bis 2026-10-25 war die Art ein Text, und vier Schichten fragten ihn je fuer
sich ab: die Beschreibung, der Aufbau, das Rechenwerk und das Bildchen
einer Zeile. Jetzt loest der Aufbau ihn einmal auf
([[opencivil.projekt.aufbau.balkensystem]]).

## Inhalt

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
def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str) -> Tuple[List[Berechnung], str, str]
```

Die Berechnungen fuer `A` und `I` -- und deren Wert-IDs.

#### Stabquerschnitt.umriss

```python
def umriss(self, loesung: Any) -> Umriss
```

Sein Umriss in mm, fuer das Bildchen seiner Zeile -- ohne einen leer.

#### Stabquerschnitt._formeln

```python
def _formeln(self, vorlage: Stabvorlage, quellen: Mapping[str, str], definieren: Definieren, abschnitt: Abschnitt, index: str) -> Tuple[List[Berechnung], str, str]
```

Die Formeln einer Vorlage, aus den Wert-IDs ihrer Masse.

#### Stabquerschnitt._a_und_i

```python
def _a_und_i(self, definieren: Definieren, index: str, berechnung: Callable[[WertDef, str, str], Berechnung]) -> Tuple[List[Berechnung], str, str]
```

`A` und `I` je als eine Berechnung -- von Hand eine Vorgabe, sonst ein Bezug.

### NachVorlage

```python
@dataclass(frozen=True, kw_only=True)
class NachVorlage(Stabquerschnitt)
```

Nach einer Vorlage: ihre Masse als Vorgaben, ihre Formeln.

- `vorlage: Stabvorlage`
- `masse: Mapping[str, float]` – Die Masse der Vorlage in mm -- was fehlte, mit seiner Vorgabe.

#### NachVorlage.flaechenwerte

```python
def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str) -> Tuple[List[Berechnung], str, str]
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

Kennwerte von Hand: `A` in mm², `I` in 10⁶ mm⁴. Ein Umriss fehlt.

- `masse: Mapping[str, float]`

#### VonHand.flaechenwerte

```python
def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str) -> Tuple[List[Berechnung], str, str]
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
def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str) -> Tuple[List[Berechnung], str, str]
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

Der Bruttoquerschnitt einer Querschnittsanalyse -- `quelle` sind `A` und `I`.

- `flaechen: Tuple[Sequence[Tuple[float, float]], ...] = ()` – Die Polygone ihrer Flaechen, in mm -- Aussparungen mit, das Bild fuellt gerade-ungerade.

#### AusAnalyse.flaechenwerte

```python
def flaechenwerte(self, definieren: Definieren, abschnitt: Abschnitt, index: str) -> Tuple[List[Berechnung], str, str]
```

#### AusAnalyse.umriss

```python
def umriss(self, loesung: Any) -> Umriss
```


## Konstanten

- `Definieren = Callable[[str, str, Einheit, str, int], WertDef]` – Wie das System einen Wert anlegt: Kurzname, Zeichen, Einheit, Beschreibung, Stellen.
- `Umriss = List[Sequence[Tuple[float, float]]]` – Ein Umriss in mm -- der erste aussen, die weiteren Loecher.
- `FLAECHENWERTE = (('A', MM2, 0, 'Querschnittsfläche'), ('I', MIO_MM4, 2, 'Flächenträgh…` – Was ein Querschnitt von Hand oder aus einer Analyse traegt.

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
- [[opencivil.stabwerk.rechnung]]
