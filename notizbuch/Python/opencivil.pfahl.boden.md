---
erzeugt: a52e9dc8dfe3
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/boden.py
> der Baugrund um einen Pfahl.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/boden.py)

## VERANTWORTUNG

Die Schichten des Baugrunds, wie der Pfahl sie braucht ([[opencivil.pfahl.boden#Pfahlschicht|Pfahlschicht]]):
Dicke, Raumlast, das Verhalten -- drainiert mit φ'_k und c'_k, undrainiert
mit s_u,k ([[opencivil.pfahl.boden#Verhalten|Verhalten]]) -- und woher die Mantelreibung kommt:
gerechnet oder eingegeben ([[opencivil.pfahl.boden#Mantel|Mantel]]). Dazu als Zahlen die Spannungen
im Boden und die Stücke des Mantels, über die die Mantelreibung summiert
wird ([[opencivil.pfahl.boden#Profil|Profil]]).


## TIEFEN UND WASSER

z zählt ab Oberkante Terrain nach unten, in m; die Schichten liegen vom
Terrain an untereinander. Unter dem Grundwasserspiegel t_w steht das
Porenwasser unter u = γ_w · (z − t_w), und es zählt die wirksame Spannung
σ'_v = σ_v − u -- mit einer Raumlast γ je Schicht über und unter dem
Wasser, darunter also γ − γ_w, wie beim Grundbruch.


## DIE STÜCKE DES MANTELS

Je Schicht der Teil des Pfahls, der in ihr steckt, am Grundwasserspiegel
noch einmal geteilt: innerhalb eines Stücks ändert sich σ'_v linear, der Wert
in seiner Mitte ist also sein Mittel, und die Summe über die Stücke das
Integral der Mantelreibung. Das Buch rechnet mit der Spannung auf halber
Einbindetiefe (Kap. 12.5) -- dasselbe, solange kein Wasserspiegel das Stück
teilt.


## EINHEITEN

Die Schichten als Grössen; das Profil in SI-Basis.

## Inhalt

### Verhalten

```python
class Verhalten(Wahl)
```

Womit eine Schicht trägt: drainiert mit φ'_k und c'_k, undrainiert mit s_u,k.

- `DRAINIERT = 'drainiert'`
- `UNDRAINIERT = 'undrainiert'`

#### Verhalten.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Verhalten.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Mantel

```python
class Mantel(Wahl)
```

Woher die Mantelreibung einer Schicht kommt.

- `RECHNEN = 'rechnen'`
- `EINGEBEN = 'eingeben'`

#### Mantel.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Mantel.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Pfahlschicht

```python
@dataclass(frozen=True)
class Pfahlschicht
```

Eine Schicht des Baugrunds, vom Terrain an nach unten gezählt. Welche
ihrer Zahlen gelten, hängt an Verhalten und Mantel ([[opencivil.pfahl.boden#Pfahlschicht.kurznamen|kurznamen]]);
die übrigen stehen da und gehen nicht ein.

- `name: str`
- `d: Groesse` – Die Dicke der Schicht.
- `gamma: Groesse` – Die Raumlast, über und unter dem Wasser dieselbe.
- `verhalten: Verhalten`
- `phi_k: Groesse` – Der Reibungswinkel, charakteristisch -- drainiert.
- `c_k: Groesse` – Die Kohäsion, charakteristisch -- drainiert; sie zählt nur am Fuss.
- `s_u: Groesse` – Die undrainierte Scherfestigkeit, charakteristisch -- undrainiert.
- `mantel: Mantel`
- `q_s: Groesse` – Die Mantelreibung, charakteristisch -- eingegeben.
- `K: Groesse` – Der Erddruckbeiwert am Mantel -- gerechnet, drainiert.
- `delta_faktor: Groesse` – Der Reibungswinkel zwischen Pfahl und Boden im Verhältnis zu φ'_k -- gerechnet, drainiert.
- `alpha: Groesse` – Die Adhäsion im Verhältnis zu s_u,k -- gerechnet, undrainiert.

#### Pfahlschicht.drainiert

```python
@property
def drainiert(self) -> bool
```

#### Pfahlschicht.kurznamen

```python
def kurznamen(self) -> Tuple[str, ...]
```

Die Zahlen, die gelten: Dicke und Raumlast, die Festigkeit, die Mantelreibung.

### Stueck

```python
@dataclass(frozen=True)
class Stueck
```

Ein Stück des Mantels in einer Schicht, auf einer Seite des Wassers -- z in m.

- `schicht: int` – Die Schicht, in der es liegt: ihr Platz in der Liste, ab null.
- `z_o: float`
- `z_u: float`

#### Stueck.h

```python
@property
def h(self) -> float
```

#### Stueck.mitte

```python
@property
def mitte(self) -> float
```

### Profil

```python
class Profil
```

Die Schichten als Zahlen: ihre Grenzen, Raumlasten und das Wasser, in
SI-Basis -- woraus die Spannungen in jeder Tiefe folgen.

#### Profil.tiefe

```python
@property
def tiefe(self) -> float
```

Wie tief die unterste Schicht reicht.

#### Profil.schicht_bei

```python
def schicht_bei(self, z: float) -> int
```

Die Schicht, in der die Tiefe z liegt -- an einer Grenze die untere:
ein Fuss auf der Grenze steht auf ihr.

#### Profil.sigma_v

```python
def sigma_v(self, z: float) -> float
```

Die totale Spannung aus dem Gewicht des Bodens darüber.

#### Profil.u

```python
def u(self, z: float) -> float
```

Der Porenwasserdruck unter dem Grundwasserspiegel.

#### Profil.sigma_v_wirksam

```python
def sigma_v_wirksam(self, z: float) -> float
```

#### Profil.stuecke

```python
def stuecke(self, oben: float, unten: float) -> List[Stueck]
```

Der Mantel von `oben` bis `unten` in Stücken, je Schicht und Seite des Wassers.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.wahl]]

## Gebraucht von

- [[opencivil.pfahl.aussen]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.projekt.pfahl]]
- [[opencivil.web.api]]
