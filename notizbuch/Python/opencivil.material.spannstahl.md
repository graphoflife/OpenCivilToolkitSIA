---
erzeugt: 60fd0ce1d8d2
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/spannstahl.py
> Spannstahl nach SIA 262:2025.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/spannstahl.py)

## VERANTWORTUNG

Sortentabelle, Erzeugnisse und Kennwerte fuer Spannstahl, aufgebaut wie
Beton und Betonstahl ([[opencivil.material.basis]]): jeder Kennwert ist
eine eigene, einzeln ueberschreibbare Berechnung.


## SORTEN UND ERZEUGNISSE

Tabelle 7 (3.3.2.2) nennt je Erzeugnis – Draht, Litze oder Stab mit seinem
Durchmesser – die Querschnittsflaeche A_p, die Zugfestigkeit f_pk und die
0.1-%-Dehngrenze f_p0.1k. Die Festigkeiten haengen nur an der Sorte: jede
Sorte Y… hat in allen ihren Zeilen dieselben. Darum ist die Sorte das
Material, und die Erzeugnisse stehen bei ihr ([[opencivil.material.spannstahl#Erzeugnis|Erzeugnis]]): ein
Spannglied waehlt eines davon, und die Flaeche kommt aus der Tabelle – eine
Litze 15.7 mm hat 150 mm², nicht π·d²/4. Die Sorten stehen in der Folge der
Tabelle 10 (4.2.3.1), Y1860 zuerst. Am 2026-11-26 gegen die gedruckten
Tabellen 7 und 10 geprueft.


## DER MODUL

Er haengt am Erzeugnis, nicht an der Sorte: 200 GPa fuer Draehte und Staebe
(3.3.2.4.1), 195 GPa fuer Litzen (3.3.2.4.2). Beide stehen als Kennwerte da,
wie beim Baustahl die beiden Spalten der Dicke; welcher gilt, sagt das
Erzeugnis ([[opencivil.material.spannstahl#Erzeugnis.modul|Erzeugnis.modul]]).


## DAS GESETZ

Figur 17 (4.2.3.3) idealisiert nur den Zug: mit E_p bis f_pd, dann
waagrecht bis eps_ud = 2 % (Tabelle 10) – ideal plastisch, wie 4.2.3.5 es
zulaesst ([[opencivil.querschnitt.werkstoffgesetz#Spannstahlgesetz|Spannstahlgesetz]]).
f_pd = f_p0.1k / gamma_s nach Gleichung (5) (2.4.2.5) mit gamma_s = 1.15
(2.4.2.6). Tabelle 10 nennt dieselben Zahlen gerundet: 1390 statt 1391
N/mm² bei Y1860 – gerechnet wird ungerundet, wie f_yd des Betonstahls.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.spannstahl import spannstahl

werk = Rechenwerk()
y1860 = spannstahl("Y1860").ins_rechenwerk(werk)
print(werk.loese(y1860.id_von("f_pd")).wert(y1860.id_von("f_pd")))
```

## Inhalt

### Erzeugnisart

```python
class Erzeugnisart(Wahl)
```

Was Tabelle 7 unterscheidet: Draht, Litze oder Stab (glatt oder gerippt).

- `DRAHT = 'draht'`
- `LITZE = 'litze'`
- `STAB = 'stab'`

#### Erzeugnisart.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Erzeugnisart.mehrzahl

```python
@property
def mehrzahl(self) -> str
```

#### Erzeugnisart.kuerzel

```python
@property
def kuerzel(self) -> str
```

Was die Bezeichnung der Tabelle hinter die Sorte setzt: C, S7 oder H.

#### Erzeugnisart.modul

```python
@property
def modul(self) -> str
```

Der Kurzname des Moduls, der fuer diese Art gilt (3.3.2.4).

#### Erzeugnisart.erklaerung

```python
@property
def erklaerung(self) -> str
```

Was an der Art haengt, wo die Flaeche eines Glieds eingegeben ist: ihr Modul.

### Erzeugnis

```python
@dataclass(frozen=True)
class Erzeugnis
```

Eine Zeile von Tabelle 7: Art, Durchmesser in mm, Querschnittsflaeche A_p in mm².

- `art: Erzeugnisart`
- `durchmesser: float`
- `flaeche: float`

#### Erzeugnis.modul

```python
@property
def modul(self) -> str
```

Der Kurzname des Moduls, mit dem es rechnet: `E_p` oder `E_p_litze`.

#### Erzeugnis.bezeichnung

```python
def bezeichnung(self, sorte: str) -> str
```

Wie Tabelle 7 es nennt, mit dem Dezimalpunkt des Werkzeugs: «Y1860S7-15.7».

### Spannstahlsorte

```python
@dataclass(frozen=True)
class Spannstahlsorte
```

Eine Sorte: f_pk und f_p0.1k in N/mm², dazu ihre Erzeugnisse aus Tabelle 7.

- `f_pk: float`
- `f_p01k: float`
- `erzeugnisse: Tuple[Erzeugnis, ...]`

### erzeugnis

```python
def erzeugnis(sorte: str, durchmesser: float) -> Optional[Erzeugnis]
```

Das Erzeugnis der Sorte mit diesem Durchmesser – `None`, wenn Tabelle 7
es fuer die Sorte nicht nennt. Je Sorte hat jedes einen eigenen
Durchmesser; daran waehlt ein Spannglied seines.

### erzeugnisarten

```python
def erzeugnisarten(sorte: str) -> Tuple[Erzeugnisart, ...]
```

In welchen Arten Tabelle 7 die Sorte nennt, in ihrer Folge: Y1860 als Draht und Litze.

### spannstahlsorten_zum_anlegen

```python
def spannstahlsorten_zum_anlegen() -> List[str]
```

Die Sorten in der Reihenfolge, in der neue angelegt werden – wie in Tabelle 10.

### spannstahl

```python
def spannstahl(sorte: str=ERSTER_SPANNSTAHL, *, name: Optional[str]=None, praefix: Optional[str]=None, abweichungen: Optional[Mapping[str, Groesse]]=None, symbol_index: str='') -> Baustoff
```

Erzeugt einen Spannstahl aus der Sortentabelle.

:param sorte: Bezeichnung aus [[opencivil.material.spannstahl#Konstanten|SPANNSTAHLSORTEN]], z.B. `'Y1860'`.
:param abweichungen: Zahlenwerte, die von der Tabelle abweichen.


## Konstanten

- `TABELLE_7 = 'SIA 262:2025, 3.3.2.2, Tabelle 7'` – Wo die Sortentabelle steht – jeder Wert aus ihr nennt diese Stelle.
- `_STAEBE = _reihe(_S, (26.0, 531.0), (26.5, 552.0), (32.0, 804.0), (36.0, 1018.0…` – Die Staebe der Sorten Y1030, Y1050 und Y1230 – in Tabelle 7 je dieselben vier.
- `SPANNSTAHLSORTEN = {'Y1860': Spannstahlsorte(1860.0, 1600.0, _reihe(_D, (3.0, 7.1), (4.0…` – Spannstahlsorten nach SIA 262:2025, Tabelle 7, in der Folge der Tabelle 10.
- `ERSTER_SPANNSTAHL = 'Y1860'` – Womit ein neuer Spannstahl anfaengt: die Folge der Tabelle 10.
- `SPANNSTAHL_VORLAGEN = (KennwertVorlage(kurzname='f_pk', symbol='f_{pk}', einheit=N_PRO_MM2,…`

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.wahl]]
- [[opencivil.material.basis]]
- [[opencivil.material.betonstahl]]

## Gebraucht von

- [[opencivil.material.arten]]
- [[opencivil.projekt.frueher]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.spannglieder]]
- [[opencivil.querschnitt.spannglieder]]
- [[opencivil.web.api]]
- [[opencivil.web.werkstoffkurven]]

## Formeln aus diesem Modul

- [[Bemessungswert der Fliessgrenze]]
- [[Fliessdehnung]]
