---
erzeugt: 2064775d3748
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/fem/belastung.py
> die Lasten eines Falls auf den Knoten.
> Paket [[opencivil.decke.fem]] · [Quelltext](../../opencivil/decke/fem/belastung.py)

## VERANTWORTUNG

Je Lastfall, was auf jeden Knoten des Netzes drückt, in N nach unten, dazu
die ganze Last und was davon neben den Platten liegt. Die Flächen kommen
von [[opencivil.decke.lasten#flaechen|flaechen]], wie in der Streifenmethode:
eine Flächenlast, eine Einzellast über ihre Verteilfläche `l_x × l_y`, das
Eigengewicht der Platten. Linienlasten und die Stege der Träger
([[opencivil.decke.lasten#stege|stege]]) liegen auf Linien des Netzes.


## WIE EINE LAST AN DIE KNOTEN GEHT

Was in einem Dreieck liegt, geht an seine drei Ecken nach den
Schwerpunktkoordinaten seiner Resultierenden – eine gleichmässige Last
über das ganze Dreieck je zu einem Drittel. Was auf einem Stück einer
Linie liegt, geht je zur Hälfte an seine Enden. Das DKT legt w im Innern
nicht fest; die Last geht darum an die Ecken, als wäre w dort linear (nach
Vorgabe, nicht nachgeschlagen). Die Summe stimmt immer, und mit feinerem
Netz auch die Verteilung.

## Inhalt

### Knotenlasten

```python
@dataclass
class Knotenlasten
```

Je Knoten die Kraft nach unten in N – und die Summen.

- `kraefte: List[float]`
- `summe: float = 0.0` – Alle Lasten zusammen, in N.
- `daneben: float = 0.0` – Was davon neben den Platten liegt, in N.
- `meldungen: List[Meldung] = field(default_factory=list)`

#### Knotenlasten.mal

```python
def mal(self, faktor: float) -> 'Knotenlasten'
```

#### Knotenlasten.plus

```python
def plus(self, andere: 'Knotenlasten') -> 'Knotenlasten'
```

### Raster

```python
class Raster
```

Die Dreiecke des Netzes in Zellen der Netzweite – damit eine Fläche nur die nahen schneidet.

#### Raster.nahe

```python
def nahe(self, ecken: Sequence[Punkt]) -> List[int]
```

Die Dreiecke, deren Rahmen den Rahmen von `ecken` trifft – jedes einmal.

#### Raster.bei

```python
def bei(self, p: Punkt) -> Tuple[int, Tuple[float, float, float]]
```

Das Dreieck, in dem `p` liegt, und die Schwerpunktkoordinaten dort – `(-1, …)`, wenn in keinem.

### schwerpunktkoordinaten

```python
def schwerpunktkoordinaten(netz: Netz, e: int, p: Punkt) -> Tuple[float, float, float]
```

`(λ_1, λ_2, λ_3)` von `p` im Dreieck `e`: je der Anteil seiner Ecke, zusammen eins.

### belasten

```python
def belasten(decke: Decke, netz: Netz, raster: Raster, lastfall: Lastfall) -> Knotenlasten
```

Die Lasten des Lastfalls auf den Knoten.

### _flaeche_verteilen

```python
def _flaeche_verteilen(kraefte: List[float], netz: Netz, raster: Raster, stueck: Sequence[Punkt], q: float) -> float
```

Ein konvexes Stück mit `q` in N/m² auf die Ecken der Dreiecke, die es deckt – zurück: was es trägt.

### _summe

```python
def _summe(heraus: Knotenlasten, name: str, was: str, gesamt: float, getragen: float) -> None
```

Die Last zur Summe – und was davon neben den Platten liegt, mit Meldung wie in der Streifenmethode.


## Braucht

- [[opencivil.decke.fem.netz]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.lasten]]
- [[opencivil.decke.modell]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.decke.fem.auswertung]]
- [[opencivil.decke.fem.rechnung]]
