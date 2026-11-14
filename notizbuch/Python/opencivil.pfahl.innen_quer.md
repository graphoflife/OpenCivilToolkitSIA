---
erzeugt: 974ae9f366f9
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/innen_quer.py
> der innere Widerstand eines Pfahls quer zu seiner Achse.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/innen_quer.py)

## VERANTWORTUNG

Der Nachweis [[opencivil.pfahl.innen_quer#InnererQuerwiderstand|InnererQuerwiderstand]], je Kombination, die den Pfahl
quer belastet ([[opencivil.pfahl.pfahl#Pfahl.quer_belastet|quer_belastet]]): in jeder Tiefe der
Verläufe ([[opencivil.pfahl.steifigkeit|.steifigkeit]]) Moment und Querkraft gegen den Widerstand des
Querschnitts ([[opencivil.pfahl.innen|.innen]]), beide mal η_i (SIA 267:2013, 9.5.2.4.1, (50)):

```
|M(z)| ≤ M_Rd(z) = η_i · M_R,d(N_V(z) / η_i)       (:func:`~.innen.biegewiderstand`)
|V(z)| ≤ V_Rd(z) = η_i · V_R,d
```


## DIE BIEGUNG

N_V ist die Normalkraft in derselben Tiefe, Druck positiv. Im Bohrpfahl
zieht das Fachwerk der Querkraft an beiden Gurten, je zur Hälfte, zusammen
F_tVd = \|V\| · cot α (SIA 262:2025, 4.3.3.4.11, (51)) -- ein Zug in der
Achse: N_V = N − F_tVd, mit dem α der Querkraft. Der Mikropfahl hat kein
Fachwerk: N_V = N.

M_Rd wird an [[opencivil.pfahl.innen_quer#Konstanten|STUETZSTELLEN]] gleich verteilten N_V gerechnet und
dazwischen linear gelesen ([[opencivil.pfahl.innen_quer#zwischen|zwischen]]): die Fläche der Widerstände ist
konvex, M_Rd in N also konkav -- die Gerade liegt darunter.


## DIE QUERKRAFT

* Bohrpfahl -- das Fachwerk ([[opencivil.querschnitt.fachwerk#fachwerk|fachwerk]])
  mit der Wendel:

```
    d = D/2 + 2 · r_s / π     bis zum Schwerpunkt der gezogenen Stäbe (4.3.3.4.2)
    z = 0.9 · d               (4.3.3.4.2)
    V_Rd,s = 0.7 · A_sw / s_w · z · f_yd · cot α      (45), 4.3.3.4.4
    V_Rd,c = b_w · z · k_c · f_cd · sin α · cos α     (47)

α ganzgradig zwischen 30° und 45°, unter Zug ab 40° (4.3.3.3.2, 4.3.3.3.3).
```
* Mikropfahl -- das Tragglied aus Stahl:

```
V_R,d = A_v · f_yd / √3,   A_v = 2 · A / π          (SIA 263:2013, 5.1.4.1, (41))
```


## NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md)

* Gezogen ist die halbe Bewehrung, die Stäbe gleichmässig auf dem Kreis.
* b_w ist die Sehne des Kreises auf der Höhe des Druckgurts -- die kleinste
  Breite zwischen den Gurten.
* α_min = 30° auch unter Druck, wo 4.3.3.3.3 bei bedeutendem Druck 25° zuliesse.
* Die Wendel aus dem Stahl der Längsbewehrung.
* F_tVd als Zug in der Achse, mit dem α der Querkraft.
* A_v = 2 · A / π für Rohr und Vollstab; f_yd nach SIA 262 statt f_y / γ_M1.


## EINHEITEN

SI-Basis.

## Inhalt

### gezogen

```python
def gezogen(N: float) -> bool
```

Ob die Normalkraft ein Zug ist, Druck positiv -- über dem Rauschen.

### stuetzstellen

```python
def stuetzstellen(von: float, bis: float) -> List[float]
```

[[opencivil.pfahl.innen_quer#Konstanten|STUETZSTELLEN]] Normalkräfte gleich verteilt von `von` bis `bis` -- eine, wo beide gleich sind.

### zwischen

```python
def zwischen(stellen: Sequence[float], werte: Sequence[float], x: float) -> float
```

Der Wert in x, linear zwischen den Stützstellen -- null, wo einer der
beiden Nachbarn nichts trägt: dazwischen ist unbekannt, wie viel.

### anteil

```python
def anteil(einwirkung: float, widerstand: float) -> float
```

\|E\| / R -- unendlich, wo nichts trägt und doch etwas wirkt.

### Schub

```python
@dataclass(frozen=True)
class Schub
```

Der Querkraftwiderstand für einen Bereich der Normalkraft: V_Rd, mal η_i, und das α des Fachwerks.

- `V_Rd: Wert`
- `alpha: Optional[Wert] = None` – Nur beim Bohrpfahl -- der Mikropfahl hat kein Fachwerk.

#### Schub.laengszug

```python
def laengszug(self, V: float) -> float
```

F_tVd = \|V\| · cot α (SIA 262:2025, 4.3.3.4.11, (51)), ohne Fachwerk null.

### Innenquerfall

```python
@dataclass
class Innenquerfall
```

In jeder Tiefe der Verläufe M_Rd und V_Rd einer Kombination, in SI -- für das Bild.

- `M_grenze: List[float]`
- `V_grenze: List[float]`

### Innenquerbefund

```python
@dataclass
class Innenquerbefund
```

Je Kombination, nach ihrem Namen, die Grenzen.

- `faelle: Dict[str, Innenquerfall] = field(default_factory=dict)`

### InnererQuerwiderstand

```python
class InnererQuerwiderstand(Nachweis)
```

Siehe Dateikopf.

- `THEMA = 'Innerer Pfahlwiderstand quer'`
- `ART = 'M-N'`

#### InnererQuerwiderstand.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### InnererQuerwiderstand._fachwerk

```python
def _fachwerk(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, innen: Innenbefund, bereiche: Sequence[bool]) -> Dict[bool, Schub]
```

Der Bohrpfahl: das Fachwerk mit der Wendel, je Bereich der Normalkraft -- Zug: `True`.

#### InnererQuerwiderstand._neigung

```python
def _neigung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, w: Dict[str, Wert], *, zug: bool, beide: bool) -> Schub
```

Die Neigung mit dem grössten Widerstand, Wendel, Druckdiagonalen und
V_Rd -- aus den Werten `w` des Fachwerks.

#### InnererQuerwiderstand._tragglied

```python
def _tragglied(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, innen: Innenbefund) -> Schub
```

Der Mikropfahl: das Tragglied aus Stahl fliesst auf Schub.

#### InnererQuerwiderstand._biegung

```python
def _biegung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, k: Kombination, v: Verlauf, q: Querschnitt, innen: Innenbefund, schub: Dict[bool, Schub]) -> Tuple[NachweisUrteil, List[float]]
```

In jeder Tiefe \|M\| gegen M_Rd mit der Normalkraft dort -- massgebend die knappste.

#### InnererQuerwiderstand._querkraft

```python
def _querkraft(self, p: Protokoll, werte: Zwischenwerte, k: Kombination, v: Verlauf, schub: Dict[bool, Schub]) -> Tuple[NachweisUrteil, List[float]]
```

In jeder Tiefe \|V\| gegen V_Rd -- massgebend die knappste.


## Konstanten

- `STUETZSTELLEN = 7` – An so vielen Normalkräften wird M_Rd gerechnet, dazwischen linear gelesen.
- `HEBELARM = 0.9` – Der Hebelarm der inneren Kräfte als Teil der statischen Höhe.
- `REFERENZ_HEBELARM = 'SIA 262:2025, 4.3.3.4.2'`
- `WENDEL = 0.7` – Was eine Wendel ohne weiteren Nachweis trägt, als Teil senkrechter Bügel.
- `REFERENZ_WENDEL = 'SIA 262:2025, 4.3.3.4.3, (45); 4.3.3.4.4'`
- `REFERENZ_LAENGSZUG = 'SIA 262:2025, 4.3.3.4.11, (51)'`
- `REFERENZ_ETA = 'SIA 267:2013, 9.5.2.4.1, (50)'`
- `REFERENZ_STAHL = 'SIA 263:2013, 5.1.4.1, (41)'`
- `S_W_REGEL = 0.4` – Die Ganghöhe der Wendel, die in der Regel nicht überschritten wird.
- `REFERENZ_S_W = 'SIA 267:2013, 9.6.3.2.4'`
- `SCHUB_BIEGUNG = 0.5` – Ab diesem Teil des Querkraftwiderstands mindert die Querkraft den Biegewiderstand des Stahls (SIA 263:2013, 5.1.5.1).
- `RAUSCHEN = 1.0` – Weniger Zug als das, in N, ist Rechenrauschen: am Fuss, der nicht trägt, bleibt statt null ein Millionstel Newton.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.querkraft_buegel]]
- [[opencivil.pfahl.innen]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.pfahl.steifigkeit]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.fachwerk]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.web.pfahldaten]]

## Formeln aus diesem Modul

- [[Hebelarm der inneren Kräfte]] · `InnererQuerwiderstand._fachwerk`
- [[Längszugkraft aus der Querkraft]] · `InnererQuerwiderstand._biegung`
- [[Normalkraft mit der Längszugkraft aus der Querkraft]] · `InnererQuerwiderstand._biegung`
- [[Querkraftwiderstand des Pfahls]] · `InnererQuerwiderstand._neigung`
- [[Querkraftwiderstand des Tragglieds]] · `InnererQuerwiderstand._tragglied`
- [[Querschnitt der Wendel]] · `InnererQuerwiderstand._fachwerk`
- [[Statische Höhe des Kreisquerschnitts]] · `InnererQuerwiderstand._fachwerk`
- [[Stegbreite des Kreisquerschnitts]] · `InnererQuerwiderstand._fachwerk`
- [[Widerstand der Druckdiagonalen im Pfahl]] · `InnererQuerwiderstand._neigung`
- [[Widerstand der Wendel]] · `InnererQuerwiderstand._neigung`
- [[Wirksame Schubfläche eines Kreisquerschnitts]] · `InnererQuerwiderstand._tragglied`
