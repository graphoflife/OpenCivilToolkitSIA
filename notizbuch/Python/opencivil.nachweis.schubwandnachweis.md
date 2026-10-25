---
erzeugt: 6bea7acfafbe
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/schubwandnachweis.py
> Querkraft und Torsion am gezeichneten Querschnitt.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/schubwandnachweis.py)

## VERANTWORTUNG

Je Lastfall `(V_y, V_z, T)` auf die Schubwaende verteilt und jede Wand mit
dem Fachwerk nachgewiesen. Die Verteilung -- Federn nach `b_w · l`, Versatz,
Zellen nach Bredt -- steht in [[opencivil.querschnitt.schubwaende]]; hier
wird sie aufgeschrieben und geurteilt.

Liefert zudem je Lastfall die Laengszugkraft `ΔN, ΔM_y, ΔM_z`, wenn sie
zugeschaltet ist: der Nachweis von Biegung und Normalkraft liest sie.


## DER MASSSTAB

Je Wand `v_Rd / |q_Ed|`, gemessen am staerksten Stueck der Wand; massgebend
ist die schwaechste Wand.

## Inhalt

### schub_belastet

```python
def schub_belastet(biegung: Biegung, fall: Lastfall) -> bool
```

Ob ein Lastfall die Schubwaende belastet -- einachsig zaehlt `V_y`
nicht. Fuer den Nachweis und fuer den Aufbau, der fragt, ob es ihn
braucht.

### Schubbefund

```python
@dataclass
class Schubbefund
```

Was der Nachweis im Lauf fand: die Waende und ihre Zellen, je Lastfall
die Verteilung des Schubflusses und je Wand den Widerstand bei der
gewaehlten Neigung und ihren Vergleich -- fuer die Diagramme. Ein
Lastfall ohne Verteilung (keine Last, keine Wand) fehlt in allen dreien.

- `waende: List[sw.Wand]`
- `modell: sw.Zellenmodell`
- `verteilungen: Dict[str, sw.Verteilung] = field(default_factory=dict)`
- `widerstaende: Dict[str, List[sw.Wandwiderstand]] = field(default_factory=dict)`
- `vergleiche: Dict[str, List[Vergleich]] = field(default_factory=dict)` – Je Wand ihr staerkster Schubfluss gegen ihren Widerstand.

### Schubwandnachweis

```python
class Schubwandnachweis(Nachweis)
```

Querkraft und Torsion, je Lastfall auf die Schubwaende verteilt.

- `THEMA = 'Querkraft und Torsion'`
- `ART = 'V+T'`

#### Schubwandnachweis.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.schubwaende]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.web.diagrammdaten]]

## Formeln aus diesem Modul

- [[Querkraft über die Federn der Wände]] · `Schubwandnachweis._protokoll_ansatz`
- [[Torsion in den Zellen (Bredt, mehrzellig)]] · `Schubwandnachweis._protokoll_ansatz`
- [[Versatz – Moment der Querkraftanteile um den Schwerpunkt]] · `Schubwandnachweis._ein_fall`
- [[Was die Zellen tragen]] · `Schubwandnachweis._ein_fall`
- [[Widerstand je Länge einer Wand (Fachwerk)]] · `Schubwandnachweis._protokoll_ansatz`
