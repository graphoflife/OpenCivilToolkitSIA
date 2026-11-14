---
erzeugt: 20ae968faabe
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/pruefung.py
> was der Durchstanznachweis rechnet, ohne Herleitung.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/pruefung.py)

## VERANTWORTUNG

Die Rechnung an einem Nachweisschnitt ([[opencivil.durchstanzen.pruefung#Schnittpruefung|Schnittpruefung]]) und mit einer
Durchstanzbewehrung ([[opencivil.durchstanzen.pruefung#Leistenpruefung|Leistenpruefung]]), je einmal. Die Suche nach
der Bewehrung und dem Stahlpilz fragt ihre Ergebnisse
([[opencivil.durchstanzen.mit_bewehrung|.mit_bewehrung]]), die Herleitung schreibt dieselben Zahlen
([[opencivil.durchstanzen.herleitung|.herleitung]]). Bis 2026-11-09 stand jede Bedingung zweimal, stumm für
die Suche und laut für die Herleitung, und der Schnitt um die Stütze, um die
Leisten und um den Pilz hatte je sein eigenes Werkzeug.


## DIE GLEICHUNGEN (SIA 262:2025)


```
u        = k_e · u_red                                  4.3.6.2.3
k_e      = 1 / (1 + e_u / b)                            (57)
V_d,red  = V_d − q_d · A                                4.3.6.2.6
V_Rd,c   = k_r · τ_cd · d_v · u                         (58)
V_Rd,max = η · min[k_sys · k_r; 3.5] · τ_cd · d_v · u   (70), 4.3.6.5.9
V_Rd,s   = η · ΣA_sw · k_e · σ_sd ≥ V_d − V_Rd,c        (66), (68)
σ_sd     = E_s·ψ/6 · (1 + f_ctm/f_yd · d/⌀_sw) ≤ f_yd   (69)
ΣA_sw · k_e · f_yd ≥ V_d / 2                            (67)
```

Im äusseren Schnitt (4.3.6.5.10) gilt (58) mit d_v,out. Die Anker stehen
senkrecht, sin β = 1. η ist 1, solange die Köpfe auf der Druckseite
höchstens d_v/6 tief liegen, sonst 0.7 (5.5.3.11). k_e nach (57) gilt je
Schnitt, mit dessen Fläche und Schwerpunkt; die Näherung nach 4.3.6.2.5
gilt für die gestützte Fläche und damit für jeden ihrer Schnitte. f_yd und
E_s in (67) und (69) sind die des Stahls der Anker (4.3.6.5.4).


## TABELLE 21 (5.5.3.8, 5.5.3.12)

Die Grenzen für den Durchmesser und den Abstand s_1 der Reihen hält die
Prüfung nicht fest: die Abstände des Produkts weichen bei einigen d davon
ab, und ob das Gutachten das nach 4.3.6.5.6 deckt, ist offen (TODO). Die
Herleitung sagt, wo es so ist.


## EINHEITEN

SI-Basis; Kräfte in N.

## Inhalt

### Grenzen

```python
@dataclass(frozen=True)
class Grenzen
```

Was Tabelle 21 bei einer statischen Höhe zulässt -- in m.

- `durchmesser: float`
- `s_1: float`

### tabelle_21

```python
def tabelle_21(d: float) -> Optional[Grenzen]
```

Die Grenzen nach Tabelle 21 bei dieser statischen Höhe -- `None` unter 140 mm.

### minderung

```python
def minderung(c_v: float, d_v: float) -> float
```

η auf (68) und (70): 1, solange c_v ≤ d_v/6, sonst 0.7 (5.5.3.11).

### kreisdurchmesser

```python
def kreisdurchmesser(flaeche: float) -> float
```

b in (57): der Durchmesser des Kreises mit der Fläche im Nachweisschnitt (4.3.6.2.4).

### beiwert_k_e

```python
def beiwert_k_e(e_u: float, b: float) -> float
```

Gleichung (57).

### widerstand

```python
def widerstand(k_r: float, tau_cd: float, d_v: float, u: float) -> float
```

Gleichung (58).

### druckdiagonale

```python
def druckdiagonale(k_sys: float, k_r: float, tau_cd: float, d_v: float, u: float) -> float
```

Gleichung (70), mit dem Faktor des Produkts anstelle der 2 (4.3.6.5.9).

### spannung

```python
def spannung(E_s: float, psi: float, f_ctm: float, f_yd: float, d: float, phi: float) -> float
```

σ_sd nach Gleichung (69).

### Schnittpruefung

```python
@dataclass(frozen=True)
class Schnittpruefung
```

Ein Nachweisschnitt und was aus ihm folgt: der wirksame Umfang, die
Fläche darin, die Querkraft, die ihn kreuzt, und die Widerstände an ihm.
Derselbe um die Stütze, um die äussersten Anker (Figur 26, mit d_v,out)
und um einen Stahlpilz (4.3.6.6.2, mit seinem d_v).

- `schnitt: Nachweisschnitt`
- `d_v: float`
- `k_e: float`
- `V_d: float` – Die Auflagerkraft.
- `q_d: float` – Die Flächenlast, die innerhalb des Schnitts abgezogen wird.

#### Schnittpruefung.auswertung

```python
@property
def auswertung(self) -> Auswertung
```

#### Schnittpruefung.u_red

```python
@property
def u_red(self) -> float
```

Was vom Schnitt zählt (Figur 23).

#### Schnittpruefung.u

```python
@property
def u(self) -> float
```

Der wirksame Umfang.

#### Schnittpruefung.flaeche

```python
@property
def flaeche(self) -> float
```

Die Fläche innerhalb des Schnitts, ohne Aussparungen.

#### Schnittpruefung.V_d_red

```python
@property
def V_d_red(self) -> float
```

Die Querkraft, die den Schnitt kreuzt.

#### Schnittpruefung.V_Rd_c

```python
def V_Rd_c(self, k_r: float, tau_cd: float) -> float
```

#### Schnittpruefung.V_Rd_max

```python
def V_Rd_max(self, k_sys: float, k_r: float, tau_cd: float) -> float
```

### Leistenpruefung

```python
@dataclass(frozen=True)
class Leistenpruefung
```

Eine Durchstanzbewehrung an ihrem Ort und die Nachweise mit ihr
(4.3.6.5.1): `innen` ist der Schnitt um die gestützte Fläche -- Stütze
oder Pilz --, `aussen` der um die äussersten Anker.

- `vorschlag: Vorschlag`
- `innen: Schnittpruefung`
- `aussen: Schnittpruefung`
- `k_r: float`
- `tau_cd: float`
- `sigma_sd: float`
- `f_yd: float` – Die Fliessgrenze der Anker (4.3.6.5.4).
- `k_sys: float`
- `eta: float` – η auf (68) und (70) -- siehe [[opencivil.durchstanzen.pruefung#minderung|minderung]].

#### Leistenpruefung.A_sw

```python
@property
def A_sw(self) -> float
```

#### Leistenpruefung.V_Rd_c

```python
@property
def V_Rd_c(self) -> float
```

#### Leistenpruefung.V_d_s

```python
@property
def V_d_s(self) -> float
```

Worauf die Bewehrung bemessen wird (66).

#### Leistenpruefung.V_Rd_s

```python
@property
def V_Rd_s(self) -> float
```

Was sie trägt (68).

#### Leistenpruefung.V_halb

```python
@property
def V_halb(self) -> float
```

#### Leistenpruefung.V_Rd_v

```python
@property
def V_Rd_v(self) -> float
```

Die Bewehrung an der Fliessgrenze (67).

#### Leistenpruefung.V_Rd_max

```python
@property
def V_Rd_max(self) -> float
```

#### Leistenpruefung.V_Rd_c_aussen

```python
@property
def V_Rd_c_aussen(self) -> float
```

#### Leistenpruefung.traegt

```python
@property
def traegt(self) -> bool
```

(66) und (67): die Bewehrung trägt, was der Beton nicht trägt, und fliessend die Hälfte.

#### Leistenpruefung.aussen_reicht

```python
@property
def aussen_reicht(self) -> bool
```

#### Leistenpruefung.diagonale_haelt

```python
@property
def diagonale_haelt(self) -> bool
```

#### Leistenpruefung.reicht

```python
@property
def reicht(self) -> bool
```

Was mehr oder längere Leisten erreichen können -- die Druckdiagonale nicht.

### Pilzbefund

```python
@dataclass(frozen=True)
class Pilzbefund
```

Ein Stahlpilz, seine gestützte Fläche bis an die Enden der Stege und der Schnitt um sie.

- `pilz: Stahlpilz`
- `umriss: Tuple[Punkt, ...]`
- `pruefung: Schnittpruefung`
- `V_Rd_c: float` – Der Widerstand um den Pilz, ohne Bewehrung.

#### Pilzbefund.reicht

```python
@property
def reicht(self) -> bool
```


## Konstanten

- `C_V_GRENZE = 1.0 / 6.0` – Höchstens so tief liegen die Köpfe der Durchstanzbewehrung auf der Druckseite, in Teilen von d_v; tiefer tragen (68) und (70) 30 % weniger (SIA 262:2025, 5.5.3.11).
- `C_V_MINDERUNG = 0.7`
- `TABELLE_21 = ((160.0, 12.0, 0.6, 0.0), (180.0, 14.0, 0.66, 0.0), (220.0, 16.0, 0.7…` – SIA 262:2025, Tabelle 21: bis zu dieser statischen Höhe d in mm höchstens dieser Durchmesser in mm und der Abstand s_1 = Faktor · d + Zuschlag; unter 140 mm keine Durchstanzbewehrung.
- `TABELLE_21_AB = 140.0`

## Braucht

- [[opencivil.durchstanzen.bewehrung]]
- [[opencivil.durchstanzen.produkte]]
- [[opencivil.durchstanzen.schnitt]]

## Gebraucht von

- [[opencivil.durchstanzen.bewehrung]]
- [[opencivil.durchstanzen.herleitung]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.nachweis]]
