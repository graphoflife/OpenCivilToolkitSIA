---
erzeugt: 1d9a7d5f712c
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

### Schubwandnachweis

```python
class Schubwandnachweis(Nachweis)
```

Querkraft und Torsion, je Lastfall auf die Schubwaende verteilt.

- `THEMA = 'Querkraft und Torsion'`

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
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.schubwaende]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]

## Formeln aus diesem Modul

- [[Querkraft über die Federn der Wände]] · `Schubwandnachweis._protokoll_ansatz`
- [[Torsion in den Zellen (Bredt, mehrzellig)]] · `Schubwandnachweis._protokoll_ansatz`
- [[Versatz – Moment der Querkraftanteile um den Schwerpunkt]] · `Schubwandnachweis._ein_fall`
- [[Was die Zellen tragen]] · `Schubwandnachweis._ein_fall`
- [[Widerstand je Länge einer Wand (Fachwerk)]] · `Schubwandnachweis._protokoll_ansatz`
