---
erzeugt: e583180f9262
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/nachweise.py
> die Nachweise einer Wand: Normalkraft und Teilflächen.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/nachweise.py)

## VERANTWORTUNG

Je Pfeiler und Kombination die Normalkraft mit Knicken und Ausmitte
([[opencivil.mauerwerk.nachweise#Normalkraft|Normalkraft]]), je Sturzauflager und Kombination die Pressung unter
ihm ([[opencivil.mauerwerk.nachweise#Teilflaechen|Teilflaechen]]) – nach SIA 266:2015. Beide lesen den Befund der
Wand ([[opencivil.mauerwerk.werk#Wandbefund|Wandbefund]]): ihre Werte, ihre
Pfeiler und was die Kombinationen ihnen geben. Rechnet die Wand nicht, ist
jede Stelle nicht führbar, und der Grund sagt, warum.


## DIE NORMALKRAFT

(4.3.1.3, Gl. (11))
N_xd am Fuss des Pfeilers gegen N_xRd = k_N · l_w · t_w · f_xd, mit der
Breite des Pfeilers als l_w. k_N kommt aus der Rechnung nach Theorie
2. Ordnung ([[opencivil.mauerwerk.knicken|knicken]]): am Kopf greift die
Normalkraft mit der Ausmitte der Lasten an, M_d / N_Ld, wo er sich drehen
kann, am Fuss mit der Vorgabe e_u; ein eingespannter Rand dreht sich nicht.
Drücken die Lasten am Kopf nicht, lässt sich der Nachweis nicht führen:
unbewehrtes Mauerwerk trägt keinen Zug (4.1.2). h_Ed nach Gl. (8)
steht zur Auskunft daneben: nach h_w / h_Ed ordnet Figur 19.

Trägt der Pfeiler in einer Kombination auch Schub, und steht die
Normalkraft quer zur Wand ausmittig, gilt Gl. (17) (4.3.3.1): l_w wird zur
gedrückten Länge l_2 = l_w − 2 · M_z2d / N_xd ([[opencivil.mauerwerk.nachweise#gedrueckte_laenge|gedrueckte_laenge]]).
Den Schub selbst weist [[opencivil.mauerwerk.schub|schub]] nach.


## DIE TEILFLÄCHEN

(4.2.1.2, Gl. (4))
Unter jedem Auflager eines Sturzes R_d gegen R_Rd = k_m · f_xd · A_0 mit
A_0 = a · t_w. Das Auflager endet am Rand der Öffnung, und der Sturz ist so
breit wie die Wand (nach Vorgabe, nicht nachgeschlagen): die Fläche A_1 mit
demselben Schwerpunkt ist A_0 selbst, also k_m = 1.


## EINHEITEN

SI-Basis.

## Inhalt

### Stelle

```python
@dataclass(frozen=True)
class Stelle
```

Wo ein Nachweis urteilt: an einem Pfeiler oder Sturzauflager, in einer Kombination.

- `ort: str` – «P1» oder «O1 links».
- `kombination: str`

#### Stelle.name

```python
@property
def name(self) -> str
```

#### Stelle.kennung

```python
@property
def kennung(self) -> str
```

### Stellenausgang

```python
@dataclass(kw_only=True)
class Stellenausgang(Fallausgang)
```

Wie eine Stelle ausging – und welche, für das Bild der Wand.

- `stelle: Stelle`
- `knicken: Optional[knicken.Knickergebnis] = None` – Bei der Normalkraft, was die Rechnung nach Theorie 2. Ordnung fand.

### Wandnachweis

```python
class Wandnachweis(Teilnachweis)
```

Was beide Nachweise teilen: je Stelle ein Erfüllungsgrad, der Befund der
Wand als Eingang, und die Stellen, an denen nicht geführt werden kann.

- `FELD: str = ''` – Wie der Nachweis im Aufbau und in seinen Kennungen heisst.

#### Wandnachweis.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### Wandnachweis.ansatz

```python
def ansatz(self, p: Protokoll, befund: 'Wandbefund') -> None
```

Was für jede Stelle gilt, einmal vor ihnen.

#### Wandnachweis.stelle

```python
def stelle(self, p: Protokoll, befund: 'Wandbefund', s: Stelle) -> Stellenausgang
```

Eine Stelle gerechnet und aufgeschrieben.

#### Wandnachweis.vergleichen

```python
@staticmethod
def vergleichen(p: Protokoll, E: Wert, R: Wert, definition: WertDef) -> Vergleich
```

Einwirkung `E` gegen Widerstand `R`, in die Herleitung geschrieben.

#### Wandnachweis.satz

```python
@staticmethod
def satz(v: Vergleich, namen: Sequence[str]) -> str
```

«N_xRd = 812.3 kN ≥ N_xd = 600.0 kN.» – `namen` die von Einwirkung und Widerstand.

### ohne_einwirkung

```python
def ohne_einwirkung(p: Protokoll, s: Stelle) -> Stellenausgang
```

### Normalkraft

```python
class Normalkraft(Wandnachweis)
```

Siehe Dateikopf.

- `LANGNAME = 'Normalkraft'`
- `ART = 'N'`
- `FELD = 'normalkraft'`

#### Normalkraft.ansatz

```python
def ansatz(self, p: Protokoll, befund: 'Wandbefund') -> None
```

#### Normalkraft.stelle

```python
def stelle(self, p: Protokoll, befund: 'Wandbefund', s: Stelle) -> Stellenausgang
```

### zug

```python
def zug(p: Protokoll, s: Stelle, pf: Pfeiler, a: Abtrag) -> Optional[Stellenausgang]
```

Nicht führbar, wenn die Lasten am Kopf nicht drücken – sonst `None`.
Mit dem Eigengewicht ist N nie kleiner als N_L: das schliesst einen Zug
am Fuss ein.

### ausmitten

```python
def ausmitten(p: Protokoll, zw: Zwischenwerte, befund: 'Wandbefund', a: Abtrag, pf: Pfeiler) -> Tuple[Optional[Wert], Optional[Wert]]
```

Die Ausmitten quer zur Wand am Kopf, M_d / N_Ld, und am Fuss, die
Vorgabe e_u – je `None`, wo der Rand eingespannt ist.

### ausmittig

```python
def ausmittig(e_o: Optional[Wert], e_u: Optional[Wert]) -> bool
```

Ob die Normalkraft quer zur Wand ausmittig steht, an einem Rand, der sich drehen kann.

### knicken_unter

```python
def knicken_unter(befund: 'Wandbefund', l: float, N: float, e_o: Optional[Wert], e_u: Optional[Wert]) -> knicken.Knickergebnis
```

k_N der Wand und ihr Zustand unter `N` auf der Länge `l` in m ([[opencivil.mauerwerk.knicken|.knicken]]).

### gedrueckte_laenge

```python
def gedrueckte_laenge(p: Protokoll, zw: Zwischenwerte, a: Abtrag, pf: Pfeiler, N: Wert, l_w: Wert) -> Wert
```

l_2 = l_w − 2 · M_z2d / N_xd: so lang ist der Pfeiler am Fuss gedrückt,
wenn die Resultierende um M_z2d / N_xd neben seiner Mitte steht. Der
Betrag von M_z2d, denn es zählt nicht, nach welcher Seite.

### _kopf

```python
def _kopf(p: Protokoll, zw: Zwischenwerte, befund: 'Wandbefund', M_d: float, N_L: float) -> Optional[Wert]
```

Die Ausmitte der Lasten am Kopf, M_d / N_Ld – `None`, wo er eingespannt ist.

### _wo

```python
def _wo(hoehe: float, h: float) -> str
```

Wo in der Wand – `hoehe` als Anteil ab dem Fuss: «am Kopf», «1.35 m über dem Fuss».

### _grenze_text

```python
def _grenze_text(erg: knicken.Knickergebnis, k: str, h: float, t: float) -> str
```

Was k_N begrenzt, als Satz – `k` ist k_N, wie es dasteht.

### pfeiler_von

```python
def pfeiler_von(befund: 'Wandbefund', name: str) -> Pfeiler
```

### Teilflaechen

```python
class Teilflaechen(Wandnachweis)
```

Siehe Dateikopf.

- `LANGNAME = 'Teilflächenpressung'`
- `ART = 'TF'`
- `FELD = 'teilflaechen'`

#### Teilflaechen.ansatz

```python
def ansatz(self, p: Protokoll, befund: 'Wandbefund') -> None
```

#### Teilflaechen.stelle

```python
def stelle(self, p: Protokoll, befund: 'Wandbefund', s: Stelle) -> Stellenausgang
```


## Konstanten

- `REFERENZ_TEILFLAECHE = 'SIA 266:2015, 4.2.1.2, Gl. (4), Figur 2'` – Wo die Regeln der Teilflächen stehen.
- `REFERENZ_H_ED = 'SIA 266:2015, 4.3.1.2, Gl. (8)'`
- `REFERENZ_GL_17 = 'SIA 266:2015, 4.3.3.1, Gl. (17)'`
- `NULL = 1e-09` – Unter diesem Betrag in SI ist eine Kraft, ein Moment oder eine Ausmitte null.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.mauerwerk.knicken]]
- [[opencivil.mauerwerk.lasten]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.werk]]

## Gebraucht von

- [[opencivil.mauerwerk.schub]]
- [[opencivil.projekt.aufbau.mauerwerk]]
- [[opencivil.web.mauerwerkdaten]]

## Formeln aus diesem Modul

- [[Ausmitte am Kopf – sie bleibt, wenn die Lasten wachsen]] · `_kopf`
- [[Beiwert der Teilflächenpressung im Mauerwerk]] · `Teilflaechen.stelle`
- [[Bezugswert der Knicklänge einer Wand]] · `Normalkraft.stelle`
- [[Fläche des Auflagers]] · `Teilflaechen.stelle`
- [[Gedrückte Länge am Fuss eines Pfeilers]] · `gedrueckte_laenge`
- [[Gleichgewicht der verformten Wand – Ausmitte der Last und Auslenkung w]] · `Normalkraft.ansatz`
- [[Grenze der Ausmitte einer Wand aus Mauerwerk]] · `Normalkraft.ansatz`
- [[Krümmung einer Wand aus Mauerwerk]] · `Normalkraft.ansatz`
- [[Normalkraftwiderstand eines Pfeilers aus Mauerwerk]] · `Normalkraft.stelle`
- [[Widerstand eines Sturzauflagers]] · `Teilflaechen.stelle`
