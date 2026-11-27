---
erzeugt: e6d237ab94b4
art: modul
tags: [modul]
---
> [!abstract] opencivil/holzbau/gleichungen.py
> die Gleichungen von SIA 265:2012, 4.2, ohne Rechenwerk.
> Paket [[opencivil.holzbau]] · [Quelltext](../../opencivil/holzbau/gleichungen.py)

## VERANTWORTUNG

Die Zahlen der Nachweise eines Holzquerschnitts und eines Holzstabs, in
N/mm², mm und ohne Einheit – die Herleitungen schreiben
[[opencivil.nachweis.qa_holz]] und
[[opencivil.nachweis.qa_holz_stabilitaet]], mit denselben Funktionen:

* der Hoehenbeiwert `k_h` des Brettschichtholzes (3.4.2.3, (5));
* Biegung und Normalkraft: (6) und (10) allein, (14) ohne Normalkraft, (21)
  mit Zug, (22) mit Druck ([[opencivil.holzbau.gleichungen#biegung_normalkraft|biegung_normalkraft]]);
* Schub und Torsion: (23), (24) und (25) ([[opencivil.holzbau.gleichungen#schub_torsion|schub_torsion]]);
* Knicken: die relative Schlankheit nach (34) und `k_c` nach (30) und
  (31); Kippen: `λ_rel,m` nach (40) mit (41) und `k_m` nach (39); je
  Achse (29) mit Druck allein, (37) mit Druck und Biegung, (38) mit Biegung
  allein ([[opencivil.holzbau.gleichungen#stabachse|stabachse]]).


## DER ERFUELLUNGSGRAD

Wie beim Stahl: die Normalkraft bleibt, Momente und Querkraefte wachsen mit
`λ`, bis die Gleichung aufgeht – `α = λ`. Ohne Moment, oder wo schon
die Normalkraft allein nicht traegt, ist es ihr Verhaeltnis, `f/σ`. In
(25) wachsen Querkraft und Torsion zusammen.

## Inhalt

### k_h

```python
def k_h(h: float) -> float
```

`(600/h)^0.1 ≤ 1.1` bei Brettschichtholz unter 600 mm Hoehe, `h` in mm – sonst 1.

### Biegung

```python
@dataclass(frozen=True)
class Biegung
```

Biegung und Normalkraft in einem Lastfall: welche Gleichung, ihre beiden
Anteile und der Erfuellungsgrad.

- `gleichung: str` – `(6)`, `(10)`, `(14)`, `(21)` oder `(22)`.
- `n: float` – Der Anteil der Normalkraft: `σ/f`, in (22) `(σ_c/f_c)²`.
- `m: float` – Der Anteil der Biegung: `σ_m,y/f_m,y + σ_m,z/f_m,z`.
- `alpha: float`

#### Biegung.nur_normalkraft

```python
@property
def nur_normalkraft(self) -> bool
```

Ob `α` das Verhaeltnis der Normalkraft ist: ohne Moment, oder sie traegt nicht.

### biegung_normalkraft

```python
def biegung_normalkraft(sigma_N: float, sigma_m_y: float, sigma_m_z: float, *, f_t: float, f_c: float, f_m_y: float, f_m_z: float) -> Optional[Biegung]
```

Die Gleichung, die der Lastfall braucht – `sigma_N` positiv Zug, die
Biegespannungen als Betrag; `None` ohne Normalkraft und Moment.

### Schub

```python
@dataclass(frozen=True)
class Schub
```

Schub und Torsion in einem Lastfall: welche Gleichung, ihre Anteile, der Erfuellungsgrad.

- `gleichung: str` – `(23)`, `(24)` oder `(25)`.
- `v: float` – `τ_d/f_v,d` – in (25) im Quadrat.
- `t: float` – `τ_tor,d/f_v,d`.
- `alpha: float`

### schub_torsion

```python
def schub_torsion(tau: float, tau_tor: float, f_v: float) -> Optional[Schub]
```

(23) ohne Torsion, (24) ohne Querkraft, sonst (25) – als Betraege;
`None` ohne beides. In (25) wachsen beide mit `λ`:
`λ·t + λ²·v² = 1`.

### lambda_rel

```python
def lambda_rel(lam: float, f_c_0_k: float, E_0_05: float) -> float
```

(34): `λ/π · √(f_c,0,k/E_0,05)`.

### k_c

```python
def k_c(lambda_rel_: float, beta_c: float) -> float
```

(30) mit (31) – eins bis `λ_rel = 0.3`.

### sigma_m_crit

```python
def sigma_m_crit(a: float, b: float, h: float, E_0_05: float) -> float
```

(41): das Rechteck `b × h` zwischen Halterungen im Abstand `a`, in mm und N/mm².

### lambda_rel_m

```python
def lambda_rel_m(f_m_k: float, sigma_crit: float) -> float
```

(40): `√(f_m,k/σ_m,crit)`.

### k_m

```python
def k_m(lambda_rel_m_: float) -> float
```

(39): eins bis 0.75, dann eine Gerade bis 1.4, darueber `1/λ²`.

### Stabachse

```python
@dataclass(frozen=True)
class Stabachse
```

Der Nachweis eines Stabs fuer eine Hauptachse: (29) mit Druck allein,
(37) mit Druck und Biegung, (38) mit Biegung allein – die Anteile und
der Erfuellungsgrad.

- `gleichung: str`
- `druck: float` – `σ_c,0,d/(k_c·f_c,0,d)` – null in (38).
- `biegung: float` – `σ_m,d/(k_m·f_m,d)`.
- `alpha: float`

#### Stabachse.nur_druck

```python
@property
def nur_druck(self) -> bool
```

Ob `α` das Verhaeltnis der Druckkraft ist: ohne Moment, oder sie traegt nicht.

### stabachse

```python
def stabachse(sigma_c: float, sigma_m: float, *, f_c: float, f_m: float, k_c_: float=1.0, k_m_: float=1.0) -> Optional[Stabachse]
```

Der Nachweis fuer eine Achse, `sigma_c` als Betrag des Drucks: (29)
ohne Moment, (37) mit, (38) ohne Druck. `None` ohne beides. Die Achsen
gelten je fuer sich (4.2.8.5).


## Konstanten

- `REFERENZ_K_H = 'SIA 265:2012, 3.4.2.3, (5)'`
- `REFERENZ_6 = 'SIA 265:2012, 4.2.1.1, (6)'`
- `REFERENZ_10 = 'SIA 265:2012, 4.2.2.1, (10)'`
- `REFERENZ_14 = 'SIA 265:2012, 4.2.3.1, (14)'`
- `REFERENZ_21 = 'SIA 265:2012, 4.2.4.1, (21)'`
- `REFERENZ_22 = 'SIA 265:2012, 4.2.4.2, (22)'`
- `REFERENZ_23 = 'SIA 265:2012, 4.2.5.1, (23)'`
- `REFERENZ_24 = 'SIA 265:2012, 4.2.5.2, (24)'`
- `REFERENZ_25 = 'SIA 265:2012, 4.2.5.3, (25)'`
- `REFERENZ_29 = 'SIA 265:2012, 4.2.8.1, (29)'`
- `REFERENZ_K_C = 'SIA 265:2012, 4.2.8.2, (30) und (31); 4.2.8.3'`
- `REFERENZ_SCHLANKHEIT = 'SIA 265:2012, 4.2.8.4'`
- `REFERENZ_LAMBDA = 'SIA 265:2012, 4.2.8.4, (34); Anhang B'`
- `REFERENZ_37 = 'SIA 265:2012, 4.2.8.5, (37)'`
- `REFERENZ_38 = 'SIA 265:2012, 4.2.9.1, (38)'`
- `REFERENZ_K_M = 'SIA 265:2012, 4.2.9.2, (39)'`
- `REFERENZ_KIPPEN = 'SIA 265:2012, 4.2.9.3, (40) und (41)'`
- `REFERENZEN = {'(6)': REFERENZ_6, '(10)': REFERENZ_10, '(14)': REFERENZ_14, '(21)':…` – Je Gleichung ihre Stelle.
- `K_H_AB = 600.0` – Ab dieser Hoehe in mm gilt k_h = 1 (3.4.2.3).
- `K_H_HOECHSTENS = 1.1` – Groesser wird k_h nicht (5).
- `LAMBDA_0 = 0.3` – Bis zu dieser relativen Schlankheit knickt ein Stab nicht: k_c = 1 (4.2.8.2).

## Gebraucht von

- [[opencivil.nachweis.qa_holz]]
- [[opencivil.nachweis.qa_holz_kennzahlen]]
- [[opencivil.nachweis.qa_holz_stabilitaet]]
- [[opencivil.nachweis.qa_holz_werte]]
