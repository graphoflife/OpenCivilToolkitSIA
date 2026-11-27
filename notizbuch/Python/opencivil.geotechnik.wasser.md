---
erzeugt: da90b8cd5b56
art: modul
tags: [modul]
---
> [!abstract] opencivil/geotechnik/wasser.py
> die Raumlast des Grundwassers, aus seiner Flüssigkeit.
> Paket [[opencivil.geotechnik]] · [Quelltext](../../opencivil/geotechnik/wasser.py)

## VERANTWORTUNG

Grundbruch und Pfahl rechnen mit γ_w, der Raumlast des Grundwassers. Seit
2026-11-27 ist sie keine Zahl am Bauteil mehr, sondern die Raumlast γ_fl
einer Flüssigkeit des Projekts ([[opencivil.material.fluessigkeit]]).
[[opencivil.geotechnik.wasser#raumlast|raumlast]] setzt beide gleich, als eigene Zeile der Herleitung – dort
steht so, welche Flüssigkeit gilt, und wer γ_fl überschreibt, rechnet auch
hier mit seiner Zahl.

## Inhalt

### raumlast

```python
def raumlast(praefix: str, abschnitt: Abschnitt, wasser: Baustoff) -> Tuple[WertDef, Formel]
```

γ_w des Bauteils mit dem Namensraum `praefix`: die Raumlast der Flüssigkeit `wasser`.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]

## Gebraucht von

- [[opencivil.geotechnik.fundament]]
- [[opencivil.pfahl.pfahl]]

## Formeln aus diesem Modul

- [[Raumlast des Grundwassers]] · `_raumlast`
