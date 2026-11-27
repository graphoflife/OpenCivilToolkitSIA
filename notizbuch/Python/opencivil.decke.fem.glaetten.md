---
erzeugt: 334f9ca60c07
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/fem/glaetten.py
> die Schnittkräfte an den Knoten.
> Paket [[opencivil.decke.fem]] · [Quelltext](../../opencivil/decke/fem/glaetten.py)

## VERANTWORTUNG

Das Dreieck DKT gibt Momente, die über jedes Dreieck linear sind, an einer
gemeinsamen Kante aber nicht zusammenpassen. Für Bilder und Bericht gilt an
jedem Knoten das Mittel der Dreiecke um ihn, nach ihrer Fläche gewichtet –
über das Dreieck dazwischen linear, so dass das Bild an einer Kante nicht
springt. Gemittelt wird nur, wo die Platte durchläuft: an einem Lager,
einem Träger, einer Linienlast oder der Fuge zweier verschieden steifer
Platten springen die Schnittkräfte, und jede Seite behält ihren Wert
([[opencivil.decke.fem.netz#Netz|trennkanten]]). Die Dreiecke um einen
Knoten zerfallen so in Sektoren, und jeder hat sein Mittel.

Nach Vorgabe, nicht nachgeschlagen: wie gemittelt wird, regelt keine Norm.
Geprüft ist es an der gelenkig gelagerten Rechteckplatte nach Navier
(`tests/test_decke_fem.py`).

## Inhalt

### Glaettung

```python
class Glaettung
```

Je Ecke jedes Dreiecks ihr Sektor ([[opencivil.decke.fem.glaetten#Glaettung|sektor]]), und je Sektor sein
Knoten, eines seiner Dreiecke und die Fläche aller.

#### Glaettung._sektoren

```python
def _sektoren(self, k: int, ecken: List[Tuple[int, int]]) -> None
```

Die Dreiecke um den Knoten `k` in Sektoren: verbunden über Kanten, die keine Trennkanten sind.

#### Glaettung.mitteln

```python
def mitteln(self, werte: Eckwerte) -> List[Tuple[float, ...]]
```

Je Sektor das Mittel – aus den Werten jedes Dreiecks an seinen Ecken.


## Konstanten

- `Eckwerte = Sequence[Sequence[Sequence[float]]]` – Je Dreieck und Ecke ein Tupel von Werten – alle Tupel gleich lang.

## Braucht

- [[opencivil.decke.fem.netz]]

## Gebraucht von

- [[opencivil.decke.fem.rechnung]]
