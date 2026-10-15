---
erzeugt: 13efa0aa3d6b
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/werkstoffgesetz.py
> Spannungs-Dehnungs-Beziehungen.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/werkstoffgesetz.py)

## VERANTWORTUNG

Liefert zu einer Dehnung die zugehoerige Spannung -- fuer Beton nach der
Parabel-Rechteck-Beziehung (SIA 262:2025, 4.2.1.6) oder vereinfacht als
Spannungsblock, und fuer Betonstahl nach der bilinearen Beziehung (4.2.2.4).


## VORZEICHEN (im ganzen Querschnittsmodul gleich)

```
Dehnung   eps > 0  =  Zug
Spannung  sig > 0  =  Zug
```
Beton nimmt keinen Zug auf; oberhalb der Bruchdehnung faellt die Spannung auf
null, was beim Aufbau der Interaktionslinie nie vorkommt, weil die Dehnungsebene
dort ohnehin begrenzt wird.


## WARUM HIER MIT BLANKEN ZAHLEN GERECHNET WIRD

Diese Funktionen laufen in der Faserintegration hunderttausendfach. Sie
arbeiten deshalb mit SI-Zahlen (N/m^2 und dimensionslose Dehnung) statt mit
[[opencivil.core.einheiten#Groesse|Groesse]]. Die Umrechnung geschieht einmal am Rand, in
[[opencivil.querschnitt.werkstoffgesetz#Betongesetz.aus_werten|Betongesetz.aus_werten]] bzw. [[opencivil.querschnitt.werkstoffgesetz#Stahlgesetz.aus_werten|Stahlgesetz.aus_werten]] -- dort ist
die Einheitenpruefung also weiterhin lueckenlos.

## Inhalt

### k_sigma

```python
def k_sigma(E_c: float, f_c: float) -> float
```

Der Beiwert der Parabel zum Modul `E_c`: `E_c/(400·f_c)`, nie unter 1.

### Betongesetz

```python
@dataclass(frozen=True)
class Betongesetz
```

Parabel-Rechteck-Beziehung nach SIA 262:2025, 4.2.1.6.

Mit `eta = |eps| / eps_c1d` gilt fuer den Druckbereich:

```
          k_sigma * eta - eta^2
sig = f_cd -----------------------      für 0 <= |eps| <= eps_c1d
          1 + (k_sigma - 2) * eta

sig = f_cd                              für eps_c1d < |eps| <= eps_c2d
```

- `NAME = 'Parabel-Rechteck-Beziehung des Betons'` – Die Seite im Notizbuch -- gleich, wer das Gesetz unter welchem Titel aufschreibt.
- `f_cd: float` – Bemessungsdruckfestigkeit in N/m^2 (positiver Betrag).
- `eps_c1d: float` – Dehnung am Ende des ansteigenden Astes (positiver Betrag).
- `eps_c2d: float` – Bruchdehnung (positiver Betrag).
- `k_sigma: float` – Gerechnet wird mit hoechstens [[opencivil.querschnitt.werkstoffgesetz#Konstanten|K_SIGMA_MIN]] -- siehe dort.

#### Betongesetz.aus_werten

```python
@classmethod
def aus_werten(cls, werte: Mapping[str, Wert]) -> 'Betongesetz'
```

Baut das Gesetz aus den Kennwerten des Betons (mit Einheitenpruefung).

#### Betongesetz.spannung

```python
def spannung(self, eps: float) -> float
```

Spannung in N/m^2 zur Dehnung `eps`. Zug positiv, also hier \<= 0.

#### Betongesetz.latex

```python
def latex(self, f: str='f_{cd}') -> str
```

Als Formel -- `f` ist das Zeichen der Festigkeit, `f_{ck}` bei charakteristischen Werten.

### Spannungsblock

```python
@dataclass(frozen=True)
class Spannungsblock
```

Der vereinfachte, rechteckige Spannungsverlauf des Betons.

Unterhalb von `(1 - 0.85) * eps_c2d` keine Spannung, darueber
durchgehend `f_cd`. Liegt der gedrueckte Rand bei `eps_c2d` -- im
Bruchzustand --, ist das genau der Block der Hoehe `0.85 x`, mit dem die
Handrechnung rechnet. Als Gesetz gilt er auch dort, wo der Rand nicht bei
`eps_c2d` liegt; so setzt ihn die Interaktionslinie des gezeichneten
Querschnitts ein.

Die Normstelle des Blocks ist offen (`notizbuch/Notizen/TODO.md`); sie
wird nicht erfunden.

- `NAME = 'Spannungsblock des Betons'` – Die Seite im Notizbuch, wie bei [[opencivil.querschnitt.werkstoffgesetz#Betongesetz|Betongesetz.NAME]].
- `f_cd: float` – Festigkeit des Blocks in N/m^2 (positiver Betrag) -- je nach Werkstoffsatz `f_cd` oder `f_ck`.
- `eps_c2d: float` – Bruchdehnung (positiver Betrag).

#### Spannungsblock.eps_knick

```python
@property
def eps_knick(self) -> float
```

Ab dieser Stauchung (Betrag) setzt der Block ein.

#### Spannungsblock.spannung

```python
def spannung(self, eps: float) -> float
```

Spannung in N/m^2 zur Dehnung `eps`. Zug positiv, also hier \<= 0.

#### Spannungsblock.mittel

```python
def mittel(self, eps_a: float, eps_b: float) -> float
```

Die mittlere Spannung, wenn die Dehnung linear von `eps_a` nach
`eps_b` laeuft -- genau: `f_cd` mal der Anteil, der ueber dem Knick
liegt.

Der Block springt. In der Mitte einer Faser gelesen, springt darum auch
N, sobald eine Faser den Knick ueberschreitet -- am Kastentraeger um
gut 20 kN --, und keine Ebene trifft N_Ed genau. Ueber die Faser
gemittelt, waechst N stetig.

#### Spannungsblock.latex

```python
def latex(self, f: str='f_{cd}') -> str
```

Als Formel -- `f` ist das Zeichen der Festigkeit, `f_{ck}` bei charakteristischen Werten.

### Stahlgesetz

```python
@dataclass(frozen=True)
class Stahlgesetz
```

Bilineare Beziehung ohne Verfestigung nach SIA 262:2025, 4.2.2.4.

Zug und Druck werden getrennt begrenzt, weil `f_yd` und `f_yd^-` in der
Sortentabelle unterschiedlich sein duerfen.

- `NAME = 'Bilineare Beziehung des Betonstahls'` – Die Seite im Notizbuch, wie bei [[opencivil.querschnitt.werkstoffgesetz#Betongesetz|Betongesetz.NAME]].
- `E_s: float` – Elastizitaetsmodul in N/m^2.
- `f_yd: float` – Fliessgrenze auf Zug in N/m^2.
- `f_yd_druck: float` – Fliessgrenze auf Druck in N/m^2 (positiver Betrag).
- `eps_ud: float` – Grenzdehnung (positiver Betrag).

#### Stahlgesetz.aus_werten

```python
@classmethod
def aus_werten(cls, werte: Mapping[str, Wert]) -> 'Stahlgesetz'
```

#### Stahlgesetz.spannung

```python
def spannung(self, eps: float) -> float
```

Spannung in N/m^2 zur Dehnung `eps`. Zug positiv.

#### Stahlgesetz.eps_yd

```python
@property
def eps_yd(self) -> float
```

#### Stahlgesetz.latex

```python
def latex(self, zug: str='f_{yd}', druck: str='f_{yd}^{-}') -> str
```

Als Formel -- `zug` und `druck` sind die Zeichen der Plateaus.

### Dehnungsebene

```python
@dataclass(frozen=True)
class Dehnungsebene
```

Eine ebene Dehnungsverteilung ueber die Querschnittshoehe.

Die Bernoulli-Hypothese steckt genau hier: die Dehnung ist linear ueber z.
`z` wird von der Oberkante nach unten gemessen.

- `eps_oben: float` – Dehnung an der Oberkante (z = 0).
- `eps_unten: float` – Dehnung an der Unterkante (z = h).
- `h: float` – Querschnittshoehe in m.

#### Dehnungsebene.durch_zwei_punkte

```python
@classmethod
def durch_zwei_punkte(cls, eps_a: float, z_a: float, eps_b: float, z_b: float, h: float) -> 'Dehnungsebene'
```

Legt die Ebene durch zwei Dehnungspunkte -- so wird der Fächer aufgebaut.

#### Dehnungsebene.bei

```python
def bei(self, z: float) -> float
```

Dehnung auf der Hoehe `z` (von Oberkante nach unten).

#### Dehnungsebene.kruemmung

```python
@property
def kruemmung(self) -> float
```

Kruemmung in 1/m.

#### Dehnungsebene.nulllinie

```python
@property
def nulllinie(self) -> float
```

Lage der Nulllinie in m von der Oberkante.

Bei reiner Zug- oder Druckbeanspruchung gibt es keine -- dann ist das
Ergebnis unendlich, was die Auswertung sauber ueberspringt.


## Konstanten

- `K_SIGMA_MIN = 1.0` – Kleiner rechnet die Parabel `k_sigma` nicht. Darunter haette ihr Nenner `1 + (k_sigma - 2)·eta` im ansteigenden Ast eine Nullstelle, bei `eta = 1/(2 - k_sigma)` -- die Spannung spraenge dort ins Unendliche und wechselte das Vorzeichen. So weit kommt es mit dem kriechweichen Modul: `E_cm/(1 + phi)` mit charakteristischen Werten und `phi = 2` gibt `k_sigma = 0.93`. Mit 1 ist der Beton bis `f_c` bei `eps_c1d` linear. Nach Vorgabe, nicht nachgeschlagen (`notizbuch/Notizen/TODO.md`).
- `K_SIGMA_LATEX = '\\max\\left(1;\\ \\frac{@E_c}{400 \\cdot @f_c}\\right)'` – Dieselbe Regel als Formel, fuer die Herleitung -- mit `@E_c` und `@f_c`.
- `BLOCKANTEIL = 0.85` – Anteil der Druckzonenhoehe, ueber den der Spannungsblock wirkt. Steht hier und nirgends sonst: die Handrechnung der Platte, ihr Duktilitaetsnachweis, das Diagramm der Werkstoffgesetze und der gezeichnete Querschnitt meinen alle denselben Block.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.nachweis.dehnungsfaecher]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.schnittanalyse]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.web.diagrammdaten]]
