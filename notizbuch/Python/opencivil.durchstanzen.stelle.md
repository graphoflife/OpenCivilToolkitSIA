---
erzeugt: a9059987a6df
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/stelle.py
> die Durchstanzstelle: Platte, gestützte Fläche, Bewehrung, Last.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/stelle.py)

## VERANTWORTUNG

Was einen Durchstanznachweis beschreibt, als Vorgaben im Rechenwerk
([[opencivil.durchstanzen.stelle#Durchstanzstelle|Durchstanzstelle]]), und die Wahlen dazu: Decke oder Bodenplatte
([[opencivil.durchstanzen.stelle#Plattenart|Plattenart]]), Form und Lage der gestützten Fläche
([[opencivil.durchstanzen.stelle#Stuetzenform|Stuetzenform]], [[opencivil.durchstanzen.stelle#Lage|Lage]]), die Näherungsstufe der
Plattenrotation ([[opencivil.durchstanzen.stelle#Naeherungsstufe|Naeherungsstufe]]) und wie k_e bestimmt wird
([[opencivil.durchstanzen.stelle#KeArt|KeArt]]). Aus ihren Massen baut sie die Kandidaten des
Nachweisschnitts ([[opencivil.durchstanzen.stelle#Durchstanzstelle.kandidaten|Durchstanzstelle.kandidaten]]).


## DECKE UND BODENPLATTE

Bei einer Decke liegt die Zugbewehrung über der Stütze oben, bei einer
Bodenplatte unten -- die Bodenpressung drückt sie von unten gegen die Stütze.
Gerechnet wird gleich; anders heisst nur, was an Flächenlast innerhalb des
Nachweisschnitts abgezogen wird (4.3.6.2.6): bei der Decke Eigengewicht und
Nutzlast, bei der Bodenplatte die Bodenpressung.


## KOORDINATEN

In der Ebene der Platte, in m. Eine Stütze steht mit ihrer Achse im
Ursprung; der Plattenrand einer Randstütze liegt unten (y negativ), bei der
Eckstütze liegt ein zweiter links (x negativ). Ein Wandende liegt im
Ursprung, die Wand läuft nach +x; eine Wandecke liegt mit ihrer äusseren
Ecke im Ursprung, die Wände laufen nach +x und +y, die Platte liegt aussen.


## EINHEITEN

SI-Basis.

## Inhalt

### Plattenart

```python
class Plattenart(Wahl)
```

Decke oder Bodenplatte -- siehe Dateikopf.

- `DECKE = 'decke'`
- `BODENPLATTE = 'bodenplatte'`

#### Plattenart.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Plattenart.last

```python
@property
def last(self) -> str
```

Was an Flächenlast im Nachweisschnitt abgezogen wird (4.3.6.2.6).

#### Plattenart.zugseite

```python
@property
def zugseite(self) -> str
```

Wo die Zugbewehrung über der gestützten Fläche liegt.

#### Plattenart.druckseite

```python
@property
def druckseite(self) -> str
```

Die andere Seite -- dort liegen die unteren Köpfe der Durchstanzbewehrung.

### Stuetzenform

```python
class Stuetzenform(Wahl)
```

Die Form einer Stütze im Grundriss. Die Ovalstütze ist ein Rechteck mit
halbrunden Enden, b_x × b_y über alles -- so heisst sie in der Software von
Leviat (DURA); der Name ist nicht aus der Norm.

- `RECHTECK = 'rechteck'`
- `RUND = 'rund'`
- `OVAL = 'oval'`

#### Stuetzenform.beschriftung

```python
@property
def beschriftung(self) -> str
```

### Lage

```python
class Lage(Wahl)
```

Wo die gestützte Fläche in der Platte liegt.

- `INNEN = 'innen'`
- `RAND = 'rand'`
- `ECKE = 'ecke'`
- `WANDENDE = 'wandende'`
- `WANDECKE = 'wandecke'`

#### Lage.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Lage.wand

```python
@property
def wand(self) -> bool
```

#### Lage.k_e

```python
@property
def k_e(self) -> float
```

Die Näherung für k_e nach SIA 262:2025, 4.3.6.2.5 -- für Innenstützen
mit grossen Aussparungen in Stützennähe gilt 0.7 wie am Rand
([[opencivil.durchstanzen.stelle#Durchstanzstelle|Durchstanzstelle.k_e_naeherung]]).

### Naeherungsstufe

```python
class Naeherungsstufe(Wahl)
```

Wie die Plattenrotation geschätzt wird (SIA 262:2025, 4.3.6.4.2).

- `EINS = '1'`
- `ZWEI = '2'`
- `DREI = '3'`

#### Naeherungsstufe.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Naeherungsstufe.faktor

```python
@property
def faktor(self) -> float
```

Der Vorfaktor in Gleichung (60): 1.5, in Stufe 3 mit Momenten aus der Elastizitätstheorie 1.2.

### KeArt

```python
class KeArt(Wahl)
```

Woher k_e kommt: aus der Näherung (4.3.6.2.5) oder aus der Exzentrizität (57).

- `NAEHERUNG = 'naeherung'`
- `EXZENTRIZITAET = 'exzentrizitaet'`

#### KeArt.beschriftung

```python
@property
def beschriftung(self) -> str
```

### Durchstanzstelle

```python
@dataclass
class Durchstanzstelle
```

Platte, gestützte Fläche, Bewehrung und Einwirkung eines Durchstanznachweises
-- als Vorgaben im Rechenwerk. Die Masse der gestützten Fläche, die für die
Form und die Lage nicht gelten, gehen nicht ein: eine Rundstütze hat kein
b_x, eine Innenstütze keinen Randabstand.

- `name: str`
- `praefix: str`
- `plattenart: Plattenart`
- `beton: Baustoff`
- `stahl: Baustoff` – Der Stahl der Biegebewehrung.
- `h: Groesse`
- `c: Groesse` – Die Überdeckung auf der Zugseite.
- `c_v: Groesse` – Die Überdeckung der Durchstanzbewehrung auf der Druckseite (Figur 26).
- `D_max: Groesse`
- `phi_x: Groesse`
- `s_x: Groesse`
- `phi_y: Groesse`
- `s_y: Groesse`
- `aussen: Richtung` – Welche Lage der Zugbewehrung aussen liegt, näher am Rand.
- `form: Stuetzenform`
- `lage: Lage`
- `b_x: Groesse`
- `b_y: Groesse`
- `D: Groesse`
- `t: Groesse` – Die Dicke der Wand -- an Wandende und Wandecke.
- `a_x: Groesse` – Der Abstand der Stütze vom linken Plattenrand -- nur an der Ecke.
- `a_y: Groesse` – Der Abstand der Stütze vom unteren Plattenrand -- am Rand und an der Ecke.
- `l_x: Groesse`
- `l_y: Groesse`
- `stufe: Naeherungsstufe`
- `r_sx: Groesse`
- `r_sy: Groesse`
- `m_sdx: Groesse`
- `m_sdy: Groesse` – `r_s` und `m_sd` von Hand -- nur in Näherungsstufe 3.
- `V_d: Groesse`
- `q_d: Groesse` – Die Flächenlast, die im Nachweisschnitt abgezogen wird (4.3.6.2.6).
- `ke: KeArt`
- `e_x: Groesse`
- `e_y: Groesse` – Die Exzentrizität der Auflagerkraft gegenüber der Stützenachse.
- `aussparungen: Sequence[Sequence[Punkt]] = ()` – Je Aussparung ihre Ecken, in m.
- `definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)`
- `berechnungen: List[Berechnung] = field(default_factory=list, init=False)`

#### Durchstanzstelle.abschnitt

```python
@property
def abschnitt(self) -> Abschnitt
```

#### Durchstanzstelle.id_von

```python
def id_von(self, kurzname: str) -> str
```

#### Durchstanzstelle.ins_rechenwerk

```python
def ins_rechenwerk(self, werk) -> 'Durchstanzstelle'
```

#### Durchstanzstelle.masse

```python
def masse(self) -> Tuple[str, ...]
```

Die Masse der gestützten Fläche, die für Form und Lage gelten.

#### Durchstanzstelle.eingaben

```python
def eingaben(self) -> Tuple[str, ...]
```

Die Kurznamen, die der Nachweis liest.

#### Durchstanzstelle.stuetze

```python
def stuetze(self, masse: Dict[str, float]) -> Stuetzenflaeche
```

Die Stütze aus ihren Massen in m, mit der Achse im Ursprung.

#### Durchstanzstelle.raender

```python
def raender(self, masse: Dict[str, float]) -> Tuple[Halbebene, ...]
```

Die Plattenränder: unten am Rand, unten und links an der Ecke.

#### Durchstanzstelle.achse

```python
def achse(self, masse: Dict[str, float]) -> Punkt
```

Die Achse der gestützten Fläche -- von ihr gehen die Strahlen an Aussparungen vorbei.

#### Durchstanzstelle.kandidaten

```python
def kandidaten(self, masse: Dict[str, float], abstand: float, d_v: float) -> List[Kandidat]
```

Die möglichen Nachweisschnitte im Abstand `abstand` -- siehe [[opencivil.durchstanzen.schnitt|.schnitt]].

#### Durchstanzstelle.umriss

```python
def umriss(self, masse: Dict[str, float], d_v: float) -> List[Punkt]
```

Der Umriss der gestützten Fläche fürs Bild -- eine Wand 4·d_v weit, etwas
über den Schnitt hinaus, der entlang der Wand 3.5·d_v weit reicht.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.web.api]]
