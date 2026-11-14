---
erzeugt: a648cd82c565
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/achse.py
> was die Nachweise längs der Pfahlachse teilen.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/achse.py)

## VERANTWORTUNG

[[opencivil.pfahl.achse#Achsnachweis|Achsnachweis]]: je Kombination ein Erfüllungsgrad, und wie ein Fall
ausgeht -- N_Ed ≥ 0 drückt und steht gegen den Widerstand auf Druck,
N_Ed \< 0 zieht und steht als Z_Ed = −N_Ed gegen den auf Zug
([[opencivil.pfahl.achse#Achsnachweis.faelle|Achsnachweis.faelle]]). Äusserer und innerer Widerstand
unterscheiden sich nur darin, woher die beiden Widerstände kommen.


## EINHEITEN

SI-Basis.

## Inhalt

### Achsnachweis

```python
class Achsnachweis(Nachweis)
```

Siehe Dateikopf.

- `INDEX: str = ''` – Der Index des Widerstands: «a» für R_a,d, «i» für R_i,d.
- `TITEL: str = ''` – Wie die Herleitung ihn überschreibt: «Äusserer Widerstand».
- `WORT: str = ''` – Wie ein Satz ihn nennt: «äusserer Widerstand».

#### Achsnachweis.faelle

```python
def faelle(self, p: Protokoll, R: Wert, R_zug: Wert) -> List[NachweisUrteil]
```

Je Kombination ihre Normalkraft gegen den Widerstand ihrer Richtung.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.pfahl.pfahl]]

## Gebraucht von

- [[opencivil.pfahl.aussen]]
- [[opencivil.pfahl.innen]]
