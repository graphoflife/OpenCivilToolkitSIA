---
erzeugt: d5d4d93ec81b
art: modul
tags: [modul]
---
> [!abstract] opencivil/erdbeben/kern.py
> der Kern eines Geschosses: seine Teile, je um ihren Schwerpunkt.
> Paket [[opencivil.erdbeben]] · [Quelltext](../../opencivil/erdbeben/kern.py)

## VERANTWORTUNG

Was ein Geschoss aus der Querschnittsanalyse seines Kerns nimmt
([[opencivil.erdbeben.kern#Kerndaten|Kerndaten]]): die zusammenhaengenden Teile der Zeichnung
([[opencivil.erdbeben.kern#teile|teile]]) und ihre Traegheitsmomente, als Prozedur mit Herleitung
([[opencivil.erdbeben.kern#Kern|Kern]]). Gezeichnet ist der ganze Kern, alle Waende in x und in y,
wie er im Grundriss liegt: y der Analyse liegt in x des Gebaeudes, z in y
(Benutzer, 2026-11-27). Bis dahin nahm jede Wand ihre eigene Analyse, mit
Anzahl und Lage 0 oder 90 Grad, ueber die ganze Hoehe.


## DIE TEILE

Zusammen haengen Polygone, die ein Stueck Kante gemeinsam haben
([[opencivil.querschnitt.geometrie#beruehren|beruehren]]) – eine Ecke allein
genuegt nicht –; was in einem Polygon liegt, gehoert zu ihm. Die Waende
eines Teils sind fest verbunden und biegen sich gemeinsam: sein I gilt um
seinen Schwerpunkt, mit dem Steiner-Anteil seiner Waende, wie im
Bruttoquerschnitt der Analyse. Getrennte Teile verbinden nur die Decken:
jeder biegt sich um seinen eigenen Schwerpunkt, und ihre I werden addiert,
ohne Steiner-Anteil zwischen ihnen (Benutzer, 2026-11-27; nach Vorgabe,
nicht nachgeschlagen). Eine Aussparung trennt ein Polygon hier nie, auch wo
sie es ganz durchschneidet.


## EINHEITEN

Die Zeichnung in mm, die Werte im Rechenwerk in m^4.

## Inhalt

### Kernteil

```python
@dataclass(frozen=True)
class Kernteil
```

Ein zusammenhaengender Teil des Kerns: seine Polygone und ihre Werte, in mm.

- `nummer: int` – Sein Platz, ab 1 – in der Folge, in der seine Polygone gezeichnet sind.
- `polygone: Tuple[str, ...]` – Die Namen seiner aeussersten Polygone – was darin liegt, gehoert dazu.
- `werte: geo.Flaechenwerte`

### teile

```python
def teile(punkte: Sequence[Sequence[geo.Punkt]], namen: Sequence[str], eltern: Sequence[Optional[int]], gewicht: Callable[[int], float]) -> Tuple[Kernteil, ...]
```

Die zusammenhaengenden Teile einer gueltigen Zeichnung
([[opencivil.querschnitt.analyse#Zeichnung|Zeichnung]]): `eltern` sagt je
Polygon, in welchem es liegt, `gewicht` zaehlt es wie dort – +1 mit
Material, -1 fuer eine Aussparung darin, 0 fuer Material in Material.

### Kerndaten

```python
@dataclass(frozen=True)
class Kerndaten
```

Was ein Kern aus seiner Querschnittsanalyse nimmt: Namen, E_cm und die Teile.

- `kennung: str` – Die Kennung der Querschnittsanalyse.
- `analyse: str` – Ihr Name.
- `beton: str` – Der Name ihres Betons.
- `E_cm: str` – Die Wert-ID von dessen E_cm.
- `teile: Tuple[Kernteil, ...]`

### Kern

```python
class Kern(Prozedur)
```

Die Traegheitsmomente eines Kerns: je Teil um seinen Schwerpunkt und
zusammen, ohne Steiner-Anteil zwischen den Teilen – siehe Dateikopf. Je
Teil gehen I_y und I_z ins Rechenwerk, wo es mehr als einen gibt: nach
ihnen verteilen sich die Kraefte am Fuss.

- `THEMA = 'Erdbeben'`

#### Kern.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```


## Konstanten

- `NACH_VORGABE = 'nach Vorgabe, nicht nachgeschlagen'`
- `MOMENTE = (('I_y', 'I_y', 'Trägheitsmoment um y'), ('I_z', 'I_z', 'Trägheitsmom…` – Die Traegheitsmomente des Kerns, je mit ihrem Zeichen und was sie sind.
- `JE_TEIL = ('I_y', 'I_z')` – Was je Teil ins Rechenwerk geht: das, wonach sich die Kraefte am Fuss verteilen.
- `_WAS = {kurz: was for kurz, _, was in MOMENTE}`
- `MM4 = 1e-12` – Von mm⁴ der Zeichnung nach m⁴.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.projekt.aufbau.erdbeben]]
- [[opencivil.web.erdbebendaten]]

## Formeln aus diesem Modul

- [[Trägheitsmomente des Kerns]] · `Kern.rechne`
