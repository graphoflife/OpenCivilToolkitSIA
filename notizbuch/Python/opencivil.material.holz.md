---
erzeugt: 12a0947f6626
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/holz.py
> Holz nach SIA 265:2012.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/holz.py)

## VERANTWORTUNG

Sortentabelle und Kennwerte fuer Vollholz und Brettschichtholz, aufgebaut
wie die anderen Baustoffe ([[opencivil.material.basis]]): jeder Kennwert
ist eine eigene, einzeln ueberschreibbare Berechnung.


## DIE SORTENTABELLEN

SIA 265:2012, 3.3.2, Tabelle 6 nennt fuer Vollholz -- C16, C24 und C30 aus
Nadelholz, D30 aus Buche oder Eiche --, 3.4.2.2, Tabelle 7 fuer
Brettschichtholz aus Nadelholz -- GL24k bis GL36h -- je die kennzeichnenden
Eigenschaften und die Bemessungswerte der Festigkeit und der Steifigkeit.
Die Norm gibt die Bemessungswerte selbst an, fuer Feuchteklasse 1 und ohne
stossartige Einwirkung (eta_w = eta_t = 1); aus der Biegefestigkeit
gerechnet waeren sie nicht dieselben, denn die Tabellen runden. Am
2026-11-26 gegen die gedruckten Tabellen geprueft.


## FUER KNICKEN UND KIPPEN

SIA 265:2012, Anhang B, Tabellen 43 und 44 nennt je Sorte die
kennzeichnende Druckfestigkeit in Faserrichtung und das 5%-Fraktil des
Elastizitaetsmoduls -- die relative Schlankheit (4.2.8.4, 4.2.9.3) rechnet
mit ihnen. Am 2026-11-26 gegen das Seitenbild geprueft.


## DIE FEUCHTEKLASSE

Wie feucht das Holz im Bauwerk im Mittel ist, ordnet es einer von drei
Klassen zu (3.2.1.2, Tabelle 3, [[opencivil.material.holz#Feuchteklasse|Feuchteklasse]]). Ihr Beiwert η_w
(Tabelle 4) mindert die Bemessungswerte der Tabellen 6 und 7, die fuer
Klasse 1 gelten -- eine Wahl des Bauteils, nicht des Materials. Ebenso η_t
(2.2.6): 1.4 bei stossartiger Einwirkung, sonst 1.

Der Elastizitaetsmodul in Faserrichtung gilt fuer Biegung, Zug und Druck
zugleich: die Tabellen nennen ihn einmal als kennzeichnende Eigenschaft,
einmal als Steifigkeit, mit derselben Zahl. Was sie sonst nennen, kommt mit
dem Nachweis, der es braucht -- der hoehere Querdruck mit Vorholz oder an
einem Endauflager, und dass C16 fuer Zugglieder nicht zugelassen ist.


## DIE NORMVORGABEN

Der Beiwert gamma_M/eta_M (2.2.5, Tabelle 1) steckt in den Bemessungswerten
schon drin -- 1.7 fuer Vollholz, 1.5 fuer Brettschichtholz --; er steht zur
Auskunft dabei. Die Dichte fuer das Eigengewicht kommt aus der mittleren
Raumlast in SIA 261:2020, Anhang A, Tabelle 28 -- Nadelholz, auch
verleimtes, 5 kN/m³, Laubholz 7.5 kN/m³ --, mit g = 10 m/s² (Benutzer,
2026-10-23). Die Rohdichte der Tabellen ist eine andere Groesse: das
5%-Fraktil, fuer die Verbindungen.


## DAS GESETZ

Linear bis zum Bruch (3.1.2.1), auf Zug bis f_t,0,d, auf Druck bis f_c,0,d
([[opencivil.querschnitt.werkstoffgesetz#Holzgesetz|Holzgesetz]]). Kann ein
Bauteil plastisch stauchen, darf der Druck elastisch-plastisch gehen
(3.1.2.2); wie weit, sagt die Norm nicht -- nach Vorgabe, nicht
nachgeschlagen, bis [[opencivil.material.holz#Konstanten|STAUCHBARKEIT]] mal die Stauchung an der Grenze
([[opencivil.querschnitt.werkstoffgesetz#HolzPlastisch|HolzPlastisch]]).


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.holz import holz

werk = Rechenwerk()
c24 = holz("C24").ins_rechenwerk(werk)
print(werk.loese(c24.id_von("eps_t_0_d")).wert(c24.id_von("eps_t_0_d")))
```

## Inhalt

### Holzart

```python
class Holzart(Enum)
```

Woraus eine Sorte ist -- das sagt den Beiwert und die Dichte.

- `NADELHOLZ = 'Vollholz aus Nadelholz'`
- `LAUBHOLZ = 'Vollholz aus Laubholz'`
- `BRETTSCHICHTHOLZ = 'Brettschichtholz aus Nadelholz'`

#### Holzart.gamma_M_eta_M

```python
@property
def gamma_M_eta_M(self) -> float
```

SIA 265:2012, 2.2.5, Tabelle 1.

#### Holzart.dichte

```python
@property
def dichte(self) -> float
```

kg/m³ -- die mittlere Raumlast nach SIA 261:2020, Tabelle 28, durch g = 10 m/s².

#### Holzart.beta_c

```python
@property
def beta_c(self) -> float
```

Der Hilfswert der Geradheit beim Knicken -- SIA 265:2012, 4.2.8.3.

### Feuchteklasse

```python
class Feuchteklasse(Wahl)
```

Wie feucht das Holz im Bauwerk im Mittel ist -- SIA 265:2012, 3.2.1.2,
Tabelle 3, in eigenen Worten. Ihr Beiwert η_w mindert Festigkeit und
Steifigkeit gegenueber Klasse 1 (Tabelle 4); fuer Vollholz und
Brettschichtholz derselbe.

- `EINS = '1'`
- `ZWEI = '2'`
- `DREI = '3'`

#### Feuchteklasse.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Feuchteklasse.erklaerung

```python
@property
def erklaerung(self) -> str
```

Wo das Holz so feucht ist, in eigenen Worten.

#### Feuchteklasse.eta_w

```python
@property
def eta_w(self) -> float
```

Der Beiwert des Tragwiderstands -- Tabelle 4.

#### Feuchteklasse.eta_w_steifigkeit

```python
@property
def eta_w_steifigkeit(self) -> float
```

Der Beiwert der Steifigkeit -- Tabelle 4.

### Holzsorte

```python
@dataclass(frozen=True)
class Holzsorte
```

Eine Spalte von Tabelle 6 oder 7: N/mm², die Rohdichte in kg/m³ -- dazu
die ihrer Sorte aus Anhang B, Tabelle 43 oder 44.

- `art: Holzart`
- `f_m_k: float`
- `E_0_mean: float`
- `rho_k: float`
- `f_m_d: float`
- `f_t_0_d: float`
- `f_c_0_d: float`
- `f_t_90_d: float`
- `f_c_90_d: float`
- `f_v_d: float`
- `E_90_mean: float`
- `G_mean: float`
- `f_c_0_k: float`
- `E_0_05: float`

### eta_t

```python
def eta_t(stossartig: bool) -> float
```

Der Beiwert der Einwirkungsdauer: 1.4 bei stossartiger Einwirkung, sonst 1 (2.2.6).

### zugglied_grund

```python
def zugglied_grund(stoff: Baustoff) -> str
```

Warum dieses Holz kein Zugglied sein darf, als Satz -- leer, wo es darf
([[opencivil.material.holz#Konstanten|OHNE_ZUGGLIED]]).

### holzsorten_zum_anlegen

```python
def holzsorten_zum_anlegen() -> List[str]
```

Die Sorten in der Reihenfolge, in der neue angelegt werden: C24, dann die Tabellen.

### holz

```python
def holz(sorte: str=ERSTES_HOLZ, *, name: Optional[str]=None, praefix: Optional[str]=None, abweichungen: Optional[Mapping[str, Groesse]]=None, symbol_index: str='') -> Baustoff
```

Erzeugt ein Holz aus den Sortentabellen.

:param sorte: Bezeichnung aus [[opencivil.material.holz#Konstanten|HOLZSORTEN]], z.B. `'GL24h'`.
:param abweichungen: Zahlenwerte, die von der Tabelle abweichen.


## Konstanten

- `TABELLEN = 'SIA 265:2012, 3.3.2, Tabelle 6; 3.4.2.2, Tabelle 7'` – Wo die Sortentabellen stehen -- jeder Wert aus ihnen nennt diese Stelle.
- `TABELLE_1 = 'SIA 265:2012, 2.2.5, Tabelle 1'` – Wo der Beiwert gamma_M/eta_M steht.
- `ANHANG_B = 'SIA 265:2012, Anhang B, Tabellen 43 und 44'` – Wo die Werte fuer Knicken und Kippen stehen.
- `TABELLE_3 = 'SIA 265:2012, 3.2.1.2, Tabelle 3'` – Wo die Feuchteklassen stehen -- und ihr Beiwert eta_w.
- `TABELLE_4 = 'SIA 265:2012, 3.2.1.3, Tabelle 4'`
- `ETA_T_STOSSARTIG = 1.4` – Der Beiwert eta_t einer stossartigen Einwirkung -- sonst 1. Die Norm laesst ihn zu, sie verlangt ihn nicht: der Benutzer waehlt je Fall.
- `REFERENZ_ETA_T = 'SIA 265:2012, 2.2.6'`
- `STOSSARTIG = 'etwa Anprall, Erdbeben oder dynamische Lasten aus dem Strassenverkeh…` – Was als stossartig gilt, in eigenen Worten nach 2.2.6.
- `OHNE_ZUGGLIED = frozenset({'C16'})` – Die Sorten, aus denen Tabelle 6 kein Zugglied zulaesst (Fussnote 2).
- `REFERENZ_ETA = 'SIA 265:2012, 3.3.2; 3.4.2.2'` – Wo die Norm die Bemessungswerte der Tabellen mit eta_w und eta_t multipliziert.
- `RAUMLASTEN = 'SIA 261:2020, Anhang A, Tabelle 28'` – Wo die mittleren Raumlasten stehen.
- `STAUCHBARKEIT = 3.0` – Wie viele Stauchungen an der Druckgrenze weit der Druck elastisch-plastisch geht -- nach Vorgabe, nicht nachgeschlagen: SIA 265:2012, 3.1.2.2 laesst das Fliessen zu, ohne eine Grenze zu nennen.
- `HOLZSORTEN = {'C16': Holzsorte(_N, 16.0, 8000.0, 310.0, 9.5, 5.5, 9.5, 0.1, 1.5, 1…` – Holzsorten nach SIA 265:2012, Tabelle 6 (Vollholz) und Tabelle 7 (Brettschichtholz), in deren Folge -- in der zweiten Zeile f_c,0,k und E_0,05 aus Anhang B, Tabelle 43 und 44.
- `ERSTES_HOLZ = 'C24'` – Womit ein neues Holz anfaengt: die Sorte, die Tabelle 6 hervorhebt.
- `_SPALTEN = ('f_m_k', 'E_0_mean', 'f_m_d', 'f_t_0_d', 'f_c_0_d', 'f_t_90_d', 'f_c…` – Was aus der Spalte einer Sorte kommt, in N/mm² -- die Rohdichte steht extra.
- `HOLZ_VORLAGEN = (_tabellenwert('f_m_k', 'f_{m,k}', 'Biegefestigkeit, kennzeichnend', …`

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.wahl]]
- [[opencivil.material.basis]]

## Gebraucht von

- [[opencivil.material.arten]]
- [[opencivil.nachweis.qa_holz]]
- [[opencivil.nachweis.qa_holz_kennzahlen]]
- [[opencivil.nachweis.qa_holz_stabilitaet]]
- [[opencivil.nachweis.qa_holz_werte]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Dehnung beim Zugbruch in Faserrichtung]]
- [[Grenzstauchung des Holzes, elastisch-plastisch]]
- [[Stauchung an der Druckgrenze in Faserrichtung]]
