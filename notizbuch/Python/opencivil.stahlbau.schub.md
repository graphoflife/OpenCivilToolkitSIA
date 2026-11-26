---
erzeugt: ed470e1e50a3
art: modul
tags: [modul]
---
> [!abstract] opencivil/stahlbau/schub.py
> der Querkraftwiderstand eines Stahlprofils nach SIA 263:2013.
> Paket [[opencivil.stahlbau]] · [Quelltext](../../opencivil/stahlbau/schub.py)

## VERANTWORTUNG

Je Profil und Richtung, was der Querkraft widersteht: die Schubflaeche
`A_v` nach 5.1.4.1, Gleichung (41), und wo ein Steg schlank ist, das
Schubbeulen nach 4.5.4, Gleichung (13). Die Querkraft wirkt allein: ohne
Normalkraft und Biegung ist kein Blech gedrueckt, und der Querschnitt
rechnet plastisch (5.1.4).


## DIE SCHUBFLAECHEN

* I-Profil in Stegrichtung: (41a).
* Die anderen nach Vorgabe, nicht nachgeschlagen -- die Norm verweist dafuer
  auf SN EN 1993-1-1, die hier nicht vorliegt: das U in Stegrichtung
  `A - 2 b t_f + (t_w + r) t_f`, I und U quer dazu `2 b t_f`, das
  Rundrohr `2 t (D - t)`. So rechnen auch die Excel-Dateien des Benutzers.
* Das Rechteckrohr: je Wand in der Richtung (13), `b` zwischen den
  Mittellinien der beiden anderen Waende. Ohne Beulen sind das
  `2 τ_y t (h - t)/γ_M1`, wie in den Excel-Dateien.


## DAS SCHUBBEULEN

Beim I und beim U genuegt (42); haelt der Steg es nicht ein, widersteht er
nach (13) mit `b t = (h - t_f) t_w`. Der Beulwert ist der des langen Felds,
`k_τ = 5.34`: wo Quersteifen stehen, weiss das Werkzeug nicht (nach
Vorgabe, nicht nachgeschlagen). Flansche und Rundrohre beulen hier nicht --
nach Vorgabe, nicht nachgeschlagen: gewalzte sind dafuer zu gedrungen.


## RICHTUNG

`z` ist die Richtung, in der das ungedrehte Profil steht -- beim I und U
die des Stegs, beim Rechteckrohr die von `h`. Um 90° oder 270° gedreht,
traegt es dasselbe in `y`.


## WO DIE QUERKRAFT STEHT ([[opencivil.stahlbau.schub#streifen|streifen]])

Die Bleche parallel zu ihr: beim I und U in Stegrichtung der Steg zwischen
den Flanschen, `h_w = h - 2 t_f` wie in (43); quer dazu die Flansche
ganz, `2 b t_f` wie ihre Schubflaeche; beim Rechteckrohr die beiden Waende
in ihrer Richtung, je `h - 3 t` wie in 5.1.5.3. Das Rundrohr hat keine
solchen Bleche: dort steht die Schubflaeche gleichmaessig ueber den Ring
verteilt, `A_v/A` von jedem Teil (nach Vorgabe, nicht nachgeschlagen).

## Inhalt

### Schubwiderstand

```python
@dataclass(frozen=True)
class Schubwiderstand
```

Was ein Profil in einer Richtung traegt, in mm und N/mm²: die Flaeche,
auf der die Schubspannung `tau` wirkt -- `A_v` nach (41) oder `b t`
der Bleche nach (13) -- und woher beides kommt.

- `flaeche: float`
- `tau: float`
- `formel: str` – Die Flaeche als LaTeX, mit Zahlen: «A - 2 b t_f + ...» oder «2 \\cdot 92 \\cdot 4».
- `herkunft: str` – Die Stelle der Flaeche -- eine Normstelle oder «nach Vorgabe».
- `beulen: Optional['Schubbeulen'] = None` – Wie das Blech nach (13) beult -- `None` bei (41).
- `steg: Optional[Tuple[float, float]] = None` – Beim I und U in Stegrichtung (42): `(h - t_f)/t_w` und seine Grenze `√(4 E/f_y)`.

#### Schubwiderstand.V_Rd

```python
def V_Rd(self, gamma_M1: float) -> float
```

Der Widerstand in N.

### Schubbeulen

```python
@dataclass(frozen=True)
class Schubbeulen
```

Die Werte von (13) fuer ein Blech der Breite `b` und der Dicke `t`, in mm und N/mm².

- `b: float`
- `t: float`
- `tau_cr: float`

### tau_beulen

```python
def tau_beulen(b: float, t: float, *, E: float, tau_y: float) -> float
```

Die Schubspannung, bis zu der ein Blech nach (13) traegt: `0.9 √(τ_cr τ_y) ≤ τ_y`.

### kritisch

```python
def kritisch(b: float, t: float, *, E: float) -> float
```

Die kritische Schubspannung `τ_cr = k_τ · 0.9 E (t/b)²` (4.5.4.1).

### widerstand

```python
def widerstand(lage: Profillage, flaeche: float, richtung: str, *, f_y: float, tau_y: float, E: float) -> Schubwiderstand
```

Der Querkraftwiderstand eines Profils in `richtung` («y» oder «z») --
`flaeche` ist seine Flaeche `A` in mm², wie gezeichnet. Siehe Dateikopf.

### rund

```python
def rund(lage: Profillage) -> bool
```

Ob das Profil in jeder Richtung gleich traegt -- das Rundrohr.

### _parallel

```python
def _parallel(von: Punkt, bis: Punkt, richtung: str) -> bool
```

Ob die Strecke von `von` nach `bis` in `richtung` laeuft, «y» oder «z».

### streifen

```python
def streifen(lage: Profillage, richtung: str) -> List[Tuple[str, float, Tuple[Punkt, ...]]]
```

Wo die Querkraft in `richtung` im Profil steht -- siehe Dateikopf: je
Streifen der Name seines Blechs, sein Anteil und sein Umriss in der
Zeichnung. Beim Rundrohr der Ring mit `A_v/A`: der Umriss aussen mit
diesem Anteil, das Loch mit dem negativen.


## Konstanten

- `REFERENZ_SCHUB = 'SIA 263:2013, 5.1.4.1, (41)'`
- `REFERENZ_41A = 'SIA 263:2013, 5.1.4.1, (41a)'`
- `REFERENZ_42 = 'SIA 263:2013, 5.1.4.2, (42)'`
- `REFERENZ_BEULEN = 'SIA 263:2013, 4.5.4.1, (13); Figur 8'`
- `NACH_VORGABE = 'nach Vorgabe, nicht nachgeschlagen'`
- `K_TAU = 5.34` – Der Schubbeulwert des langen Felds ohne Quersteifen (Figur 8, α gross) -- siehe Dateikopf.

## Braucht

- [[opencivil.querschnitt.geometrie]]
- [[opencivil.stahlprofile.bleche]]
- [[opencivil.stahlprofile.lage]]
- [[opencivil.stahlprofile.tabelle]]

## Gebraucht von

- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.stahlbau.widerstand]]
