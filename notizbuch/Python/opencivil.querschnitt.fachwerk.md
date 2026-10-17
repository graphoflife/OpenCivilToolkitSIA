---
erzeugt: 041fb57d4eb8
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/fachwerk.py
> das Fachwerk mit veraenderlicher Neigung.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/fachwerk.py)

## VERANTWORTUNG

Was ein Steg mit Buegeln bei einer Neigung der Druckdiagonalen aufnimmt
([[opencivil.querschnitt.fachwerk#fachwerk|fachwerk]]), und welche Neigung den groessten Widerstand gibt
([[opencivil.querschnitt.fachwerk#beste_neigung|beste_neigung]]) -- fuer die Buegel einer Platte
([[opencivil.nachweis.querkraft]]) wie fuer eine Schubwand des
gezeichneten Querschnitts ([[opencivil.querschnitt.schubwaende]]). Zwei
reine Funktionen, darum im Querschnitt: bis 2026-10-17 standen sie beim
Querkraftnachweis, und die Schubwaende holten sie von dort.

## Inhalt

### Buegelpunkt

```python
@dataclass(frozen=True)
class Buegelpunkt
```

Was bei einer bestimmten Neigung der Druckdiagonalen aufnehmbar ist.

Beide Anteile in N/m, also je Laufmeter -- wie `V_Ed`.

- `alpha: int` – Neigung der Druckdiagonalen in Grad.
- `V_Rd_s: float` – Bügel: waechst, je flacher die Diagonale liegt.
- `V_Rd_c: float` – Druckdiagonale: groesst bei 45°, faellt nach beiden Seiten.

#### Buegelpunkt.V_Rd

```python
@property
def V_Rd(self) -> float
```

Massgebend ist der kleinere der beiden -- eines von beiden versagt.

### fachwerk

```python
def fachwerk(*, alpha: int, a_sw_s: float, z: float, b_w: float, f_yd: float, f_cd: float, k_c: float) -> Buegelpunkt
```

Fachwerkmodell mit veraenderlicher Neigung der Druckdiagonalen -- fuer die
Buegel einer Platte wie fuer eine Schubwand der Querschnittsanalyse.

Alles in SI-Basis: Flaechen in m^2, Laengen in m, Festigkeiten in Pa:

```
V_Rd,s = A_sw/s · z · f_yd · cot(alpha)
V_Rd,c = b_w · z · k_c · f_cd · sin(alpha) · cos(alpha)
```

`A_sw/s` ist der Bewehrungsgehalt je Laenge in Laengsrichtung, `z`
der Hebelarm der inneren Kraefte, `b_w` die Breite des Stegs.

### beste_neigung

```python
def beste_neigung(punkte: Sequence[Buegelpunkt]) -> Buegelpunkt
```

Die Neigung mit dem groessten Widerstand.

`V_Rd,s` waechst mit flacherer Diagonale, `V_Rd,c` faellt dabei --
das Kleinere von beiden hat sein Groesstes dort, wo sich die beiden
Aeste treffen. Gesucht wird ganzgradig; bei Gleichstand gilt die
steilere Neigung, weil sie die Druckdiagonale weniger beansprucht.


## Gebraucht von

- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.querschnitt.schubwaende]]
