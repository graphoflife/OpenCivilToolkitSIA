---
erzeugt: 45679a98bc18
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/produkte.py
> Durchstanzbewehrung und Stahlpilze, wie man sie kaufen kann.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/produkte.py)

## VERANTWORTUNG

Die Produkte, aus denen die Bemessung wählt, mit ihren Regeln -- Typen,
Durchmesser, Höhen, Abstände, der Faktor des Gutachtens -- und woher jede
Zahl stammt. Gerechnet wird hier nichts, was über ein Produkt hinausgeht:
die Anordnung um die Stütze steht in [[opencivil.durchstanzen.bewehrung|.bewehrung]], der Nachweis in
[[opencivil.durchstanzen.nachweis|.nachweis]].


## ANCOPLUS (AncoTech AG)

Doppelkopfanker auf einer Montageleiste, je Leiste 2 bis 9 Anker gleichen
Durchmessers. Die Typen «D…» haben ungleiche Abstände: der erste Anker
liegt 0.375·d vom Rand der Stütze, bis und mit dem dritten folgen sie sich
im Abstand 0.60·d, danach 0.75·d. So hat es das Gutachten Muttoni /
Fernández Ruiz von 2007 für die erhöhte Obergrenze 3·k_r festgelegt
(Bericht 07-A05-R1c, zu SIA 262:2003, S. 5–6). Ein neueres Gutachten zu
SIA 262:2025 war nicht lesbar; die Regeln gelten darum **nach Vorgabe,
nicht nachgeschlagen**.


## ZEUS (AncoTech AG)

Stahlpilze aus Stahlprofilen, als einfaches Kreuz, Doppelkreuz oder H-Kreuz,
s × s im Grundriss, Höhe h. Aus der Preisliste 12.2018 (S. 8–9). Profile,
Armlängen und Widerstände sind nicht veröffentlicht: den Widerstand des
Pilzes selbst (SIA 262:2025, 4.3.6.6.1) bestätigt der Hersteller.


## EINHEITEN

SI-Basis, Längen in m.

## Inhalt

### Ankertyp

```python
@dataclass(frozen=True)
class Ankertyp
```

Ein Durchmesser von ancoPLUS: Kennbuchstabe, ⌀ und die lieferbaren Höhen h_A.

- `buchstabe: str`
- `durchmesser: float`
- `h_min: float`
- `h_max: float`

#### Ankertyp.flaeche

```python
@property
def flaeche(self) -> float
```

Die Querschnittsfläche eines Ankers.

### groesster_durchmesser

```python
def groesster_durchmesser(d: float) -> Optional[float]
```

Der grösste Ankerdurchmesser, den das Gutachten bei dieser statischen Höhe zulässt.

### ankerhoehe

```python
def ankerhoehe(h: float, c_zug: float, c_druck: float) -> float
```

Die Höhe h_A der Anker: die Plattendicke ohne beide Überdeckungen, auf
eine lieferbare Höhe abgerundet -- auf 5 mm, in Schritten von 10 mm.
Nach der Zulassung ETA-13/0196 und zwei Beispielen von AncoTech, nach
Vorgabe, nicht nachgeschlagen.

### k_sys

```python
def k_sys(c_druck: float, d: float, mit_ausnahme: bool) -> float
```

Der Faktor anstelle der 2 in Gleichung (70) -- siehe [[opencivil.durchstanzen.produkte#Konstanten|K_SYS_HOCH]].
`mit_ausnahme`: Innenstütze, Wandende oder einspringende Ecke.

### abstaende

```python
def abstaende(d: float, anzahl: int) -> Tuple[float, ...]
```

Die Abstände einer Leiste vom Rand der Stütze an, auf 5 mm abgerundet --
der erste vom Rand zum ersten Anker, dann von Anker zu Anker.

### typname

```python
def typname(typ: Ankertyp, anzahl: int, h_A: float) -> str
```

«DA3-0215»: ungleiche Abstände, Typ, Anker je Leiste, Höhe h_A in mm.

### Stahlpilz

```python
@dataclass(frozen=True)
class Stahlpilz
```

Ein ZEUS-Stahlpilz: Art, s × s im Grundriss, Höhe h, Abstand g der Doppelstege.

- `art: str`
- `s: float`
- `h: float`
- `g: float = 0.0`

#### Stahlpilz.name

```python
@property
def name(self) -> str
```

«ZEUS Kreuz 650 × 650, h = 160 mm».

#### Stahlpilz.armenden

```python
def armenden(self) -> Tuple[Tuple[float, float], ...]
```

Wo die Stege enden, von der Stützenachse aus: beim Kreuz die vier
Armenden, beim Doppel- und H-Kreuz je Arm zwei im Abstand g. Sie
umschliessen die gestützte Fläche ausserhalb des Pilzes
(SIA 262:2025, 4.3.6.6.2).


## Konstanten

- `QUELLE_ANCOPLUS = 'AncoTech, Gutachten Muttoni / Fernández Ruiz 2007 (07-A05-R1c) und P…` – Woher die Regeln von ancoPLUS stammen -- so steht es in der Herleitung.
- `QUELLE_ZEUS = 'AncoTech, Preisliste ZEUS 12.2018'`
- `ANKERTYPEN = (Ankertyp('X', 0.01, 0.125, 0.295), Ankertyp('A', 0.012, 0.125, 0.315…` – Die Typen von ancoPLUS mit ihren Höhen h_A (Preisliste ancoPLUS, S. 6). Bei 22, 25 und 28 mm nennt die Liste mehrere Buchstaben und für 25/28 auch 26/30 mm; genommen ist der erste Buchstabe und der kleinere Durchmesser.
- `ANKER_JE_LEISTE = range(2, 10)` – So viele Anker trägt eine Leiste -- nur ganze Elemente sind lieferbar.
- `ABSTAND_ERSTER = 0.375` – Die Abstände der Typen «D…», in Vielfachen von d (siehe Dateikopf): vom Rand der Stütze zum ersten Anker, bis zum dritten, danach.
- `ABSTAND_BIS_DRITTER = 0.6`
- `ABSTAND_DANACH = 0.75`
- `TANGENTIAL = 1.5` – Höchstens so weit stehen zwei Leisten beim zweiten Anker auseinander, in Vielfachen von d (Gutachten 2007, Regel 5).
- `GROESSTER_DURCHMESSER = ((0.18, 0.014), (0.22, 0.016), (0.26, 0.018), (0.34, 0.02), (0.6, 0.0…` – Die Durchmesser je statischer Höhe d (Gutachten 2007, Tabelle 1): bis zu diesem d höchstens dieser Durchmesser; unter 0.160 m keiner.
- `KLEINSTES_D = 0.16`
- `K_SYS_HOCH = 3.0` – Der Faktor des Gutachtens anstelle der 2 in Gleichung (70), und die Obergrenze anstelle der 3.5: für Innenstützen, Wandenden und einspringende Ecken 3·k_r, wenn die Überdeckung der unteren Köpfe höchstens d/10 ist; bei d/6 gilt wieder 2·k_r, dazwischen linear (Gutachten 2007, S. 5–7). Für Rand- und Eckstützen 2.0 wie in der Norm -- die Software von 2026 nennt dort 3.0, ein Gutachten dazu war nicht lesbar.
- `K_SYS_NORM = 2.0`
- `GRENZE = 3.5`
- `HOEHENSCHRITT = 0.01` – Die Höhen h_A enden auf 5 mm, in Schritten von 10 mm (Preisliste).
- `STAHLPILZE = tuple(sorted(_pilze('Kreuz', 470, (100, 120)) + _pilze('Kreuz', 530, …` – Die ZEUS-Pilze der Preisliste, kleinste zuerst. Die Sondertypen (Rechteck) und der Doppelkreuz ohne g sind weggelassen.
- `PILZ_UNTEN = 0.02` – Unter dem Pilz bleiben 20 mm Beton, über ihm 50 mm bis zur Oberfläche -- die Vorgaben der AncoTech-Software (Theorie 2010, S. 11, aus dem Bild).
- `PILZ_OBEN = 0.05`

## Gebraucht von

- [[opencivil.durchstanzen.bewehrung]]
- [[opencivil.durchstanzen.mit_bewehrung]]
