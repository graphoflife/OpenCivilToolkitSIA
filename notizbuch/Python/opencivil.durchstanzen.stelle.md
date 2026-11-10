---
erzeugt: 699c5fb2e01a
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/stelle.py
> die Durchstanzstelle: Platte, gestützte Fläche, Bewehrung, Last.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/stelle.py)

## VERANTWORTUNG

Was einen Durchstanznachweis beschreibt, als Vorgaben im Rechenwerk
([[opencivil.durchstanzen.stelle#Durchstanzstelle|Durchstanzstelle]]), und die Wahlen dazu: Decke oder Bodenplatte
([[opencivil.durchstanzen.stelle#Plattenart|Plattenart]]), die Näherungsstufe der Plattenrotation
([[opencivil.durchstanzen.stelle#Naeherungsstufe|Naeherungsstufe]]) und wie k_e bestimmt wird ([[opencivil.durchstanzen.stelle#KeArt|KeArt]]). Was
Lage und Form der gestützten Fläche heissen, steht in [[opencivil.durchstanzen.flaeche|.flaeche]].
Welche Felder der Nachweis liest, sagt [[opencivil.durchstanzen.stelle#eingaben_fuer|eingaben_fuer]] -- dieselben Teile
bekommt die Maske über den Katalog, damit sie nichts davon nachbaut.


## DECKE UND BODENPLATTE

Bei einer Decke liegt die Zugbewehrung über der Stütze oben, bei einer
Bodenplatte unten -- die Bodenpressung drückt sie von unten gegen die Stütze.
Gerechnet wird gleich; anders heisst nur, was an Flächenlast innerhalb des
Nachweisschnitts abgezogen wird (4.3.6.2.6): bei der Decke Eigengewicht und
Nutzlast, bei der Bodenplatte die Bodenpressung.


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

#### Naeherungsstufe.eingaben

```python
@property
def eingaben(self) -> Tuple[str, ...]
```

Was die Stufe liest: die Spannweiten, in Stufe 2 dazu die Exzentrizität
für die Momente im Stützstreifen, in Stufe 3 statt beidem r_s und m_sd.

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

#### KeArt.eingaben

```python
@property
def eingaben(self) -> Tuple[str, ...]
```

### wirksame_stufe

```python
def wirksame_stufe(flaeche: GestuetzteFlaeche, stufe: Naeherungsstufe) -> Naeherungsstufe
```

Die Stufe, mit der gerechnet wird: Stufe 2 braucht die Momente im
Stützstreifen -- wo 4.3.6.4.7 keine nennt, an Wänden, rechnet sie wie
Stufe 1.

### eingaben_fuer

```python
def eingaben_fuer(flaeche: GestuetzteFlaeche, stufe: Naeherungsstufe, ke: KeArt) -> Tuple[str, ...]
```

Die Kurznamen, die der Nachweis liest: die Masse der gestützten Fläche,
was die wirksame Stufe liest und was k_e liest -- je ohne Doppel.

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
- `flaeche: GestuetzteFlaeche`
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

#### Durchstanzstelle.eingaben

```python
def eingaben(self) -> Tuple[str, ...]
```

Die Kurznamen, die der Nachweis liest -- siehe [[opencivil.durchstanzen.stelle#eingaben_fuer|eingaben_fuer]].


## Konstanten

- `VOR_DEN_MASSEN = ('h', 'c', 'c_v', 'D_max', 'phi_x', 's_x', 'phi_y', 's_y')` – Was der Nachweis an jeder Stelle liest -- vor den Massen der gestützten Fläche und danach.
- `NACH_DEN_MASSEN = ('V_d', 'q_d')`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.flaeche]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.web.durchstanzdaten]]
