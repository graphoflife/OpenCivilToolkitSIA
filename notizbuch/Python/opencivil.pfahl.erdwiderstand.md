---
erzeugt: a897eb3acda6
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/erdwiderstand.py
> was der Boden quer zum Pfahl hält, und wie der Pfahl quer bricht.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/erdwiderstand.py)

## VERANTWORTUNG

* [[opencivil.pfahl.erdwiderstand#Erdwiderstand|Erdwiderstand]] -- je Meter Pfahl die grösste Kraft, die der Boden
  quer aufnimmt, über die Tiefe: p_E,k. Als Stücke, auf denen sie linear
  verläuft ([[opencivil.pfahl.erdwiderstand#Erdwiderstand.linien|Erdwiderstand.linien]]).
* [[opencivil.pfahl.erdwiderstand#brueche|brueche]] -- wie ein Pfahl quer zu seiner Achse bricht: der Boden
  längs des Pfahls gibt nach, und wo das Moment den Biegewiderstand M_R
  erreicht, knickt der Pfahl in einem Gelenk. Der kleinste Bruch ist der
  charakteristische Querwiderstand R_tr,k (SIA 267:2013, 9.4.4.2.2).


## DER ERDWIDERSTAND (Kap. 9.3.5, 9.3.6, 10.8)


```
drainiert    e_p = K_p · σ'_v + 2 · c' · √K_p     e_a = K_a · σ'_v − 2 · c' · √K_a
             K_p = (1 + sin φ') / (1 − sin φ')     K_a = 1 / K_p
undrainiert  e_p = σ_v + 2 · s_u                   e_a = σ_v − 2 · s_u
p_E,k = b' · (e_p − max(0; e_a))                    b' = 3 · D
```

Vorne, wohin sich der Pfahl schiebt, drückt der Boden passiv dagegen;
hinten drückt er nur noch aktiv nach, und wo e_a negativ würde, klafft ein
Spalt. Vor einem schmalen Körper wirkt der Erdwiderstand auf einer
breiteren Fläche als dieser, grob auf der dreifachen Breite.


## DIE BRÜCHE

s zählt ab dem Kopf. H wirkt am Kopf, beim frei drehbaren Kopf mit dem
Moment H · e dazu. Je Mechanismus leistet die Last dieselbe Arbeit, die
Boden und Gelenke verzehren; seine Lage ist die, bei der H am kleinsten
wird:

```
frei drehbar
  Drehung um s_r                    H · |s_r + e| = ∫ p_E · |s − s_r| ds
  Gelenk in s_h                     H · |s_h + e| = M_R + ∫₀^s_h p_E · (s_h − s) ds
  Verschiebung                      H = ∫ p_E ds
eingespannt
  Gelenk am Kopf, Drehung um s_r    H · s_r = M_R + ∫ p_E · |s − s_r| ds
  Gelenke am Kopf und in s_h        H · s_h = 2 · M_R + ∫₀^s_h p_E · (s_h − s) ds
  Verschiebung                      H = ∫ p_E ds
```

Unter einem Gelenk in s_h steht der Pfahl still. Gesucht wird auf Knoten,
höchstens [[opencivil.pfahl.erdwiderstand#Konstanten|SCHRITT]] auseinander; zwischen ihnen ist p_E linear, und
die Integrale sind exakt.


## NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md)

* Hinten der aktive Erddruck abgezogen, und beide auf der Breite 3 · D. Das
  Buch gibt die wirksame Breite für den passiven Druck vor einem schmalen
  Träger. Nur so hebt sich undrainiert σ_v vorne und hinten auf, und p_E
  wächst nicht ohne Grenze mit der Tiefe.
* Rankine, ohne Reibung zwischen Pfahl und Boden.
* Die Mechanismen: der ganze Pfahl starr, oder Gelenke, unter denen er
  stillsteht -- wie für kurze und lange Pfähle üblich. Die Norm verlangt
  nur, R_tr,k aus Erdwiderstand und innerem Widerstand zu rechnen.


## EINHEITEN

SI-Basis.

## Inhalt

### Festigkeit

```python
@dataclass(frozen=True)
class Festigkeit
```

Womit eine Schicht dem Pfahl quer widersteht -- in SI, φ' im Bogenmass.

- `drainiert: bool`
- `phi: float = 0.0`
- `c: float = 0.0`
- `s_u: float = 0.0`

#### Festigkeit.K_p

```python
@property
def K_p(self) -> float
```

Der Erdwiderstandsbeiwert nach Rankine, ohne Wandreibung -- undrainiert eins.

#### Festigkeit.erddruecke

```python
def erddruecke(self, sigma: float) -> Tuple[float, float]
```

e_p und e_a unter der Spannung `sigma` -- drainiert der wirksamen,
undrainiert der totalen, mit K_p = K_a = 1 und s_u statt c'.

### Linie

```python
@dataclass(frozen=True)
class Linie
```

Ein Stück des Pfahls, auf dem p_E,k linear verläuft -- z ab Terrain, p je Meter Pfahl.

- `schicht: int` – Die Schicht, in der es liegt: ihr Platz in der Liste, ab null.
- `oben: float`
- `unten: float`
- `p_oben: float`
- `p_unten: float`

#### Linie.p

```python
def p(self, z: float) -> float
```

### Erdwiderstand

```python
class Erdwiderstand
```

Siehe Dateikopf: p_E,k über die Tiefe, z ab Terrain.

#### Erdwiderstand.erddruecke

```python
def erddruecke(self, z: float, schicht: int) -> Tuple[float, float]
```

e_p und e_a in der Tiefe z, gerechnet mit der Schicht `schicht`.

#### Erdwiderstand.je_meter

```python
def je_meter(self, z: float, schicht: int) -> float
```

p_E,k = b' · (e_p − max(0; e_a)): vorne passiv, hinten aktiv oder ein Spalt.

#### Erdwiderstand.bei

```python
def bei(self, z: float) -> float
```

p_E,k in der Tiefe z -- an der Grenze zweier Schichten der kleinere Wert.

#### Erdwiderstand.linien

```python
def linien(self, oben: float, unten: float) -> List[Linie]
```

p_E,k von `oben` bis `unten` als lineare Stücke: je Schicht und
Seite des Wassers eines ([[opencivil.pfahl.boden#Profil.stuecke|stuecke]]), noch einmal
geteilt, wo e_a das Vorzeichen wechselt.

### Bruch

```python
@dataclass(frozen=True)
class Bruch
```

Ein Mechanismus an seiner ungünstigsten Lage: was bricht, wo, und bei welcher Querkraft.

- `was: str`
- `lage: Optional[float]` – s_r oder s_h ab Kopf, in m -- `None` bei der Verschiebung.
- `H: float`

### _Integrale

```python
class _Integrale
```

Vom Kopf bis zu jedem Knoten ∫ p ds und ∫ p · s ds, s ab Kopf -- exakt,
weil p zwischen zwei Knoten linear ist.

#### _Integrale.oben

```python
def oben(self, j: int) -> float
```

∫₀^s_j p · (s_j − s) ds: der Boden über dem Knoten, um ihn gedreht.

#### _Integrale.unten

```python
def unten(self, j: int) -> float
```

∫_s_j^L p · (s − s_j) ds: der Boden darunter.

### brueche

```python
def brueche(linien: Sequence[Linie], kopf: float, M_R: float, *, eingespannt: bool, e: float=0.0, schritt: float=SCHRITT) -> List[Bruch]
```

Die Mechanismen des Dateikopfs, jeder an seiner ungünstigsten Lage. Die
`linien` reichen vom Kopf in der Tiefe `kopf` bis zum Fuss; `e` ist
beim frei drehbaren Kopf der Hebel des Moments, M_Ed / H_Ed.


## Konstanten

- `SCHRITT = 0.01` – So weit liegen die Knoten höchstens auseinander, auf denen die Lage eines Bruchs gesucht wird, in m: H ändert sich dort kaum, ein Zentimeter verschiebt es um weniger, als je gedruckt wird.

## Braucht

- [[opencivil.pfahl.boden]]
- [[opencivil.pfahl.buch]]

## Gebraucht von

- [[opencivil.pfahl.quer]]
