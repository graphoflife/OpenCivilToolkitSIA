---
erzeugt: 0667b03e2fae
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/fachwerk.py
> das Fachwerk mit veraenderlicher Neigung.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/fachwerk.py)

## VERANTWORTUNG

Das Druckfeld eines Stegs mit Buegeln, an einer Stelle: was er bei einer
Neigung der Druckdiagonalen aufnimmt ([[opencivil.querschnitt.fachwerk#fachwerk|fachwerk]]), zwischen welchen
Neigungen gesucht wird ([[opencivil.querschnitt.fachwerk#Konstanten|ALPHA_MIN]], [[opencivil.querschnitt.fachwerk#Konstanten|ALPHA_MAX]], bei Normalzug
gehoben, [[opencivil.querschnitt.fachwerk#druckfeldgrenzen|druckfeldgrenzen]]), mit welchem `k_c` ([[opencivil.querschnitt.fachwerk#Konstanten|K_C]]) –
und welche Neigung den groessten Widerstand gibt ([[opencivil.querschnitt.fachwerk#guenstigste|guenstigste]]).
Fuer die Buegel einer Platte ([[opencivil.nachweis.querkraft_buegel]]),
eine Schubwand des gezeichneten Querschnitts
([[opencivil.querschnitt.schubwaende]]) und die Wendel eines Pfahls
([[opencivil.pfahl.innen_quer]]).

Bis 2026-10-17 standen die beiden Funktionen beim Querkraftnachweis, und
die Schubwaende holten sie von dort. Bis 2026-11-21 standen die Grenzen und
`k_c` bei der Platte, sieben Module holten sie dort, und die Suche stand
dreimal da, einmal je Nutzer.

## Inhalt

### Buegelpunkt

```python
@dataclass(frozen=True)
class Buegelpunkt
```

Was bei einer bestimmten Neigung der Druckdiagonalen aufnehmbar ist.

Bei der Platte in N/m, je Laufmeter wie ihr `V_Ed`; bei einer Schubwand
in N, fuer die ganze Wand.

- `alpha: int` – Neigung der Druckdiagonalen in Grad.
- `V_Rd_s: float` – Bügel: waechst, je flacher die Diagonale liegt.
- `V_Rd_c: float` – Druckdiagonale: groesst bei 45°, faellt nach beiden Seiten.

#### Buegelpunkt.V_Rd

```python
@property
def V_Rd(self) -> float
```

Massgebend ist der kleinere der beiden – eines von beiden versagt.

### fachwerk

```python
def fachwerk(*, alpha: int, a_sw_s: float, z: float, b_w: float, f_yd: float, f_cd: float, k_c: float) -> Buegelpunkt
```

Fachwerkmodell mit veraenderlicher Neigung der Druckdiagonalen – fuer die
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

`V_Rd,s` waechst mit flacherer Diagonale, `V_Rd,c` faellt dabei –
das Kleinere von beiden hat sein Groesstes dort, wo sich die beiden
Aeste treffen. Gesucht wird ganzgradig; bei Gleichstand gilt die
steilere Neigung, weil sie die Druckdiagonale weniger beansprucht.

### druckfeldgrenzen

```python
def druckfeldgrenzen(alpha_min: int, alpha_max: int, zugkraft: bool) -> Tuple[int, int]
```

Die beiden Grenzwinkel der Druckdiagonalen in Grad, angepasst an das
Vorzeichen von `N_Ed`.

Bei Normalzug steilt sich die Druckdiagonale auf: `alpha_min` ist dann
mindestens 40°, und `alpha_max` wird notfalls mitgehoben, damit der
Bereich nicht leer wird (SIA 262:2025, 4.3.3.3.3). Bis 2026-11-14 wurde
`alpha_min` auf genau 40° gesetzt – auch von 42° herunter.

### Neigungssuche

```python
@dataclass(frozen=True)
class Neigungssuche
```

Was [[opencivil.querschnitt.fachwerk#guenstigste|guenstigste]] findet.

- `alpha_min: int`
- `alpha_max: int` – Die verwendeten Grenzen; bei Normalzug angehoben.
- `punkte: Tuple[Buegelpunkt, ...]` – Der Widerstand je ganzem Grad zwischen den beiden.
- `massgebend: Buegelpunkt` – Der Punkt mit dem groessten Widerstand.

### guenstigste

```python
def guenstigste(punkt: Callable[[int], Buegelpunkt], *, alpha_min: int, alpha_max: int, zugkraft: bool) -> Neigungssuche
```

Die Neigung mit dem groessten Widerstand, ganzgradig zwischen den
Grenzen, die eine Normalzugkraft hebt ([[opencivil.querschnitt.fachwerk#druckfeldgrenzen|druckfeldgrenzen]]).
`punkt` ist das Fachwerk des Nutzers bei einer Neigung in Grad – die
Buegel einer Platte je Laufmeter, eine Schubwand, eine Wendel.
Zwischenwerte sind eine Genauigkeit, die das Fachwerkmodell nicht
hergibt.


## Konstanten

- `ALPHA_MIN = 30` – Vorgabe fuer die Neigung der Druckdiagonalen, in Grad: 30° ist im Normalfall die untere Grenze (SIA 262:2025, 4.3.3.3.3), 45° die obere der Norm (4.3.3.3.2, Gl. (42)).
- `ALPHA_MAX = 45`
- `ALPHA_ZUG = 40` – Bei einer Normalzugkraft steilt sich die Druckdiagonale auf. Beide Grenzen werden dann auf mindestens diesen Wert gehoben (SIA 262:2025, 4.3.3.3.3).
- `K_C = 0.55` – Vorgabe fuer den Abminderungsbeiwert der Betondruckfestigkeit in der Druckdiagonalen: der Wert fuer Stege, deren Druckfeld die Bewehrung schief kreuzt (SIA 262:2025, 4.2.1.7).
- `REFERENZ_ALPHA_MIN = 'SIA 262:2025, 4.3.3.3.3'` – Wo die Grenzen der Neigung und k_c stehen – fuer die Platte, die Querschnittsanalyse und den Pfahl.
- `REFERENZ_ALPHA_MAX = 'SIA 262:2025, 4.3.3.3.2, (42)'`
- `REFERENZ_K_C = 'SIA 262:2025, 4.2.1.7'`

## Gebraucht von

- [[opencivil.nachweis.qa_kennzahlen]]
- [[opencivil.nachweis.querkraft_buegel]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.pfahl.innen_quer]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.schubwaende]]
