---
erzeugt: 9e3a99e6508e
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/zustand2.py
> Der gerissene Querschnitt, linear elastisch.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/zustand2.py)

## VERANTWORTUNG

Nulllinie und Hebelarm eines gerissenen Rechteckquerschnitts unter reiner
Biegung. Beton ohne Zugfestigkeit, beide Baustoffe linear elastisch, gedrueckte
Bewehrung vernachlaessigt.


## WARUM EIGENSTAENDIG

Zwei Nachweise brauchen dieselbe Nulllinie -- der Nachweis gegen das Rissmoment
und die Begrenzung der Stahlspannung unter haeufiger Einwirkung. Zwei
Rechenwege fuer dieselbe Groesse liefen frueher oder spaeter auseinander; das
ist in diesem Werkzeug schon zweimal passiert.


## DIE RECHNUNG


```
n = (E_s / E_cm) * (1 + phi)          Wertigkeit, mit Kriechen
b*x^2/2 = n*A_s*(d - x)               erstes Moment um die Nulllinie
x = sqrt(rho^2 + 2*d*rho) - rho       mit rho = n*A_s/b
z = d - x/3
```

`x` haengt **nicht** von der Last ab: im linearen Zustand ist die Nulllinie
eine reine Querschnittseigenschaft. Darum genuegt eine Formel, kein Suchen.

Die Betondruckspannung verlaeuft dreieckig -- null in der Nulllinie, groesst
an der gedrueckten Kante. Ihre Resultierende liegt bei `x/3` von dieser
Kante, nicht bei `2x/3`; das ist die Stelle, an der man sich beim Hebelarm
leicht vertut.


## KRIECHEN IST KONSERVATIV

`dx/drho = (rho+d)/sqrt(rho^2+2*d*rho) - 1 > 0`, denn `(rho+d)^2` uebertrifft
`rho^2+2*d*rho` um `d^2`. Groesseres `n` gibt also immer groesseres `x`
und damit kleineres `z` -- ein groesseres `phi` liegt auf der sicheren
Seite, fuer jede Geometrie.


## EINHEITEN

Alles in SI-Basis; Laengen in m, Flaechen in m^2, Moduln in Pa.

## Inhalt

### Zustand2

```python
@dataclass(frozen=True)
class Zustand2
```

Nulllinie und Hebelarm des gerissenen Querschnitts.

- `n: float` – Wertigkeit `E_s/E_c,eff` -- um wie viel steifer der Stahl ist.
- `rho: float` – `n * A_s / b` -- die Hilfsgroesse, aus der die Nulllinie folgt, in m.
- `x: float` – Druckzonenhoehe ab der gedrueckten Kante, in m.
- `z: float` – Innerer Hebelarm `d - x/3`, in m.

### wertigkeit

```python
def wertigkeit(*, E_s: float, E_cm: float, phi: float) -> float
```

`n = (E_s/E_cm) * (1 + phi)`.

Das Kriechen weicht den Beton auf: `E_c,eff = E_cm/(1+phi)`, und die
Wertigkeit ist `E_s/E_c,eff`. Die Klammer ist wesentlich -- ``E_s/(E_cm *
(1+phi))`` waere das Gegenteil.

### gerissen

```python
def gerissen(*, n: float, a_s: float, b: float, d: float) -> Zustand2
```

Nulllinie und Hebelarm bei reiner Biegung.

`a_s` ist die Bewehrung der **gezogenen** Seite; die gedrueckte bleibt
unberuecksichtigt.


## Gebraucht von

- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.spannungsbegrenzung]]
