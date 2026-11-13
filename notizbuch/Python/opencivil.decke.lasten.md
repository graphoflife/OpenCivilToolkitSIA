---
erzeugt: 15140df9957f
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/lasten.py
> die Lasten eines Lastfalls auf den Streifen.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/lasten.py)

## VERANTWORTUNG

Aus den Lasten eines Lastfalls, was jeder Streifen trägt: eine Last je
Länge längs seiner Achse, genau integriert über seine Breite. Je Stelle geht
der Anteil seiner Richtung in ihn ([[opencivil.decke.aufteilung|aufteilung]]) --
liegt die Stelle in einem Unterzug derselben Richtung, in diesen.


## FLÄCHEN

Alles wird zu Flächen mit gleichmässiger Last: eine Flächenlast auf ihrem
Vieleck oder ihrer Platte, das Eigengewicht auf jeder Platte, eine
Einzellast auf ihrer Verteilfläche `lx × ly` und eine Linienlast auf einem
Band von [[opencivil.decke.lasten#Konstanten|LINIENBREITE]]. Eine Fläche wird in konvexe Stücke zerlegt,
mit den Stücken der Platten geschnitten, mit dem Band jedes Streifens und
seinen Anteilen. Ein konvexes Stück ist quer zur Achse linear breit
([[opencivil.decke.geometrie#breite|breite]]): die Last darauf ist eine
lineare Last je Länge, ohne Näherung.


## LINIENLASTEN

Eine Linienlast liegt auf einem Band von 1 mm. Wo die Linie im Innern liegt,
je zur Hälfte zu beiden Seiten -- auf einer Grenze zwischen zwei Streifen
trägt also jeder die Hälfte, keiner das Doppelte. Liegt sie auf dem Rand
einer Platte, ganz auf der Seite der Platte. Ein Millimeter verschiebt
nichts, was man in den Ergebnissen sähe.


## WAS DANEBEN LIEGT

Was ausserhalb der Platten liegt, trägt nichts; die Summe steht in
[[opencivil.decke.lasten#Belastung|Belastung.daneben]], und eine Meldung nennt die Last.

## Inhalt

### Belastung

```python
@dataclass
class Belastung
```

Je Streifen seine Lasten, in `s = p·n` seiner Richtung -- und die Summen.

- `je_streifen: Dict[str, List[Teillast]] = field(default_factory=dict)`
- `summe: float = 0.0` – Alle Lasten zusammen, in N.
- `daneben: float = 0.0` – Was davon neben den Platten liegt, in N.
- `meldungen: List[Meldung] = field(default_factory=list)`

#### Belastung.hinzu

```python
def hinzu(self, name: str, last: Teillast) -> None
```

### kombiniert

```python
def kombiniert(belastungen: Dict[str, Belastung], kombination: Kombination) -> Belastung
```

Eine Kombination: jede Last ihres Lastfalls mal dessen Beiwert -- alles ist linear.

### belasten

```python
def belasten(decke: Decke, zerlegung: Zerlegung, aufteilungen: Aufteilungen, lastfall: Lastfall) -> Belastung
```

Die Lasten des Lastfalls auf den Streifen.

### flaechen

```python
def flaechen(decke: Decke, lastfall: Lastfall, meldungen: List[Meldung]) -> List[Tuple[str, List[Punkt], float]]
```

Die Flächen des Lastfalls mit ihrer Last in N/m² -- ohne die Linienlasten.

### linienband

```python
def linienband(a: Punkt, b: Punkt, platten: Sequence[Sequence[Punkt]]) -> List[List[Punkt]]
```

Das Band einer Linienlast, in Stücken: wo die Linie im Innern liegt,
beidseits je halb so breit; wo eine Seite ausserhalb aller Platten
liegt, ganz auf der anderen.

### _verteilen

```python
def _verteilen(heraus: Belastung, zerlegung: Zerlegung, aufteilungen: Aufteilungen, g: int, stueck: Sequence[Punkt], q: float) -> None
```

Ein konvexes Stück mit `q` in N/m², auf einer Platte der Gruppe `g`, auf die Streifen beider Richtungen.

### _zuordnen

```python
def _zuordnen(heraus: Belastung, zerlegung: Zerlegung, streifen: Streifen, last: Streckenlast) -> None
```

In den Feldstreifen -- oder, wo er in einem Unterzug seiner Richtung liegt, in diesen.


## Konstanten

- `LINIENBREITE = 0.001` – Wie breit das Band einer Linienlast ist, in m.
- `DANEBEN = 1e-09` – Unter diesem Anteil der Last gilt eine Last als ganz auf den Platten.

## Braucht

- [[opencivil.decke.aufteilung]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.streifen]]
- [[opencivil.decke.traeger]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.decke.rechnung]]
