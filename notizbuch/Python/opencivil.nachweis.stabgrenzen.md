---
erzeugt: 5498ad9d3013
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/stabgrenzen.py
> die zulaessige Stahlspannung je Stab des gezeichneten Querschnitts.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/stabgrenzen.py)

## VERANTWORTUNG

Die Gebrauchsnachweise der Querschnittsanalyse ([[opencivil.nachweis.qa_gebrauch]])
halten jeden Stab gegen seine eigene Grenze. Hier steht, wie ein Stab zu ihr
kommt und wie sie in die Herleitung kommt, wo die Rissbreite zaehlt
([[opencivil.nachweis.stabgrenzen#grenzen_aus_rissbreite|grenzen_aus_rissbreite]]), mit derselben Funktion wie bei der Platte
([[opencivil.nachweis.mindestbewehrung#zulaessige_stahlspannung|zulaessige_stahlspannung]]).
Gegen das Fliessen gilt je Stahl `f_yd - 80 N/mm²`, fuer jede Geometrie
gleich ([[opencivil.nachweis.spannungsgrenzen#gegen_fliessen|gegen_fliessen]]).


## JE STAB

Die Platte haelt je Lage den dicksten Stab gegen die Rissbreite. Hier hat
jeder Stab seine Grenze -- mit seinem Durchmesser und dem `f_ctm` des
Betons, in dem er liegt (Benutzer, 2026-10-15). Staebe mit derselben Grenze
bilden eine Gruppe, die einmal hergeleitet wird
([[opencivil.nachweis.spannungsgrenzen#Grenzgruppe|Grenzgruppe]]).


## DER FIKTIVE DURCHMESSER

Eine verschmierte Linie hat keinen Durchmesser: sie bekommt einen fiktiven,
als laegen ihre Staebe 150 mm auseinander (Annahme des Benutzers,
2026-10-15):

```
⌀_fikt = sqrt(4/π · A_s/l · s)        s = 150 mm
```

Nach Vorgabe, nicht nachgeschlagen: die Grenze je Stab und der fiktive
Durchmesser. Siehe `notizbuch/Notizen/TODO.md`.


## EINHEITEN

SI-Basis; die Zeichnung in mm.

## Inhalt

### Stabangabe

```python
@dataclass(frozen=True)
class Stabangabe
```

Ein Stab -- oder ein Stueck einer verschmierten Linie --, wie die Nachweise ihn sehen.

- `element: Stabgruppe` – Das Element der Zeichnung, aus dem er stammt.
- `lage: Punkt` – in m.
- `flaeche: float` – in m².
- `beton: Baustoff` – Der Beton, in dem er liegt: er gibt `f_ctm` fuer die Rissbreite.
- `durchmesser: float` – in m -- bei einer verschmierten Linie der fiktive.

#### Stabangabe.stahl

```python
@property
def stahl(self) -> Baustoff
```

#### Stabangabe.verschmiert

```python
@property
def verschmiert(self) -> bool
```

#### Stabangabe.ort

```python
@property
def ort(self) -> str
```

Wie er in einem Satz heisst: Element und Lage, in mm.

### fiktiver_durchmesser

```python
def fiktiver_durchmesser(element: Stabgruppe) -> float
```

Der Durchmesser einer verschmierten Linie, in m: ihre Stahlflaeche je
Laenge, auf Staebe im Abstand [[opencivil.nachweis.stabgrenzen#Konstanten|FIKTIVE_TEILUNG]] verteilt.

### stabangaben

```python
def stabangaben(analyse: Querschnittsanalyse, q: Querschnitt, herkunft: Sequence[Stabgruppe]) -> List[Stabangabe]
```

Je Bewehrung des Querschnitts ihre Angaben -- in derselben Reihenfolge wie dort.

### _gruppieren

```python
def _gruppieren(staebe: Sequence[Stabangabe], schluessel: Callable[[Stabangabe], tuple], bilden: Callable[[Stabangabe], Grenzgruppe]) -> Grenzen
```

Je Schluessel eine Gruppe, in der Reihenfolge ihres ersten Stabs -- jeder Stab eine Stelle.

### grenzen_aus_rissbreite

```python
def grenzen_aus_rissbreite(analyse: Querschnittsanalyse, e: Eingaben, staebe: Sequence[Stabangabe], anforderung: Rissanforderung) -> Grenzen
```

`sigma_s,adm` je Stab aus der Rissanforderung: bei normaler Anforderung
`f_yk` seines Stahls, bei erhoehter und hoher dazu die Rissbreite mit
seinem Durchmesser und dem `f_ctm` seines Betons.

### protokoll_rissbreitengrenzen

```python
def protokoll_rissbreitengrenzen(p: Protokoll, e: Eingaben, analyse: Querschnittsanalyse, staebe: Sequence[Stabangabe], grenzen: Grenzen, anforderung: Rissanforderung, basis: str, *, referenz: str) -> None
```

`sigma_s,adm` aus der Rissbreite, je Gruppe gleicher Staebe einmal
hergeleitet -- vorher der fiktive Durchmesser jeder verschmierten Linie,
die ihn braucht. Bei mehreren Gruppen danach eine Tabelle, welche Elemente
zu welcher gehoeren. Setzt [[opencivil.nachweis.spannungsgrenzen#Grenzgruppe|Grenzgruppe.wert]].

### _protokoll_fiktiv

```python
def _protokoll_fiktiv(p: Protokoll, s: Stabangabe, basis: str) -> Wert
```

Der fiktive Durchmesser einer verschmierten Linie, hergeleitet.

### _tabelle_grenzen

```python
def _tabelle_grenzen(p: Protokoll, staebe: Sequence[Stabangabe], grenzen: Grenzen) -> None
```

Welche Elemente zu welcher Grenze gehoeren.


## Konstanten

- `FIKTIVE_TEILUNG = 0.15` – Die Teilung, mit der eine verschmierte Linie einen fiktiven Durchmesser bekommt, in m -- Annahme des Benutzers, 2026-10-15.
- `GRENZE_JE_STAB = 'Jeder gezogene Stab hält gegen seine eigene Grenze, mit seinem Durch…` – Wie die Grenze aus der Rissbreite hier gemessen wird.
- `FIKTIV = 'Eine verschmierte Linie hat keinen Durchmesser – sie bekommt einen f…` – Woher eine verschmierte Linie ihren Durchmesser hat.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.interaktion]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.spannungsgrenzen]]

## Formeln aus diesem Modul

- [[Fiktiver Durchmesser einer verschmierten Linie]] · `_protokoll_fiktiv`
