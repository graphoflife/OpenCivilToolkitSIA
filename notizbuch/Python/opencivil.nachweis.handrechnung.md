---
erzeugt: 4f31b0717b7e
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/handrechnung.py
> Eckpunkte der Resistenzlinie von Hand.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/handrechnung.py)

## VERANTWORTUNG

Rechnet die wenigen Punkte der M-N-Interaktion, die sich mit Papier und
Taschenrechner nachvollziehen lassen, und schreibt dabei jeden Schritt
mit -- Formel, eingesetzte Zahlen, Ergebnis. Aus den Punkten entsteht ein
Polygon, und gegen dieses Polygon wird nachgewiesen.


## WARUM NICHT GEGEN DIE GENAUE LINIE

Die punktweise aus Dehnungsebenen aufgebaute Linie in
[[opencivil.nachweis.biegung_normalkraft]] ist genauer, aber sie entsteht aus
einer Faserintegration ueber hunderte Stuetzstellen. Wer das Ergebnis prueft,
kann es nicht nachrechnen -- er kann es nur glauben. Genau das soll dieses
Werkzeug nicht verlangen. Die genaue Linie bleibt darum als Vergleich im
Diagramm stehen, das Urteil faellt aber ueber die Handrechnung.


## ANSATZ

* Druckzone als Spannungsblock der Hoehe `0.85 x` mit durchgehend `f_cd`
  -- oder `f_ck` mit charakteristischen Werten ([[opencivil.querschnitt.gesetzwahl#Werkstoffsatz|Werkstoffsatz]]);
  dann heissen die Eckpunkte `R_k` statt `R_d`.
* **Gedrueckter Stahl wird durchgehend vernachlaessigt.** Das liegt auf der
  sicheren Seite und erspart die Frage, ob er ueberhaupt fliesst.
* Bewehrung je Richtung zu zwei Lagen zusammengefasst -- eine je Seite.


## VORZEICHEN

```
N > 0   Zug
M > 0   Zug an der Unterseite
```
Bezugsachse fuer M ist die halbe Querschnittshoehe, wie bei der genauen Linie.


## DIE VIER PUNKTE (je Momentenvorzeichen, ausser wo vermerkt)


```
1  M_Rd bei N = 0      x aus dem Kraeftegleichgewicht, dann M aus dem Hebelarm
2  groesste Zugkraft   alles fliesst auf Zug; nur ein Punkt fuer beide Vorzeichen
3  groesste Druckkraft reiner Beton, ohne Stahl; M = 0
4  Punkt mit x = h/2   Nulllinie auf halber Hoehe, Block bis 0.85*h/2
```

Punkt 4 liegt knapp unterhalb des Balancepunkts und gibt dem Polygon den Bauch,
den die genaue Linie unter Druck hat. Die Zugbewehrung traegt dort, was ihre
Dehnung hergibt: `sigma_sd = min(E_s * eps_s; f_yd)`.

## Inhalt

### Posten

```python
@dataclass(frozen=True)
class Posten
```

Ein einzelner Bewehrungsposten, so wie er in die Handrechnung eingeht.

- `a_s: float` – Querschnittsflaeche in m^2, fuer die betrachtete Breite b.
- `z: float` – Schwerpunkt in m, ab Oberkante.
- `f_yd: float` – Bemessungswert der Fliessgrenze in Pa.
- `E_s: float` – Elastizitaetsmodul in Pa.
- `text: str = ''`
- `index: str = ''` – Index des Symbols, z.B. `1,x,g`.
- `stahl_index: str = ''` – Index der Stahlsorte -- leer, solange es nur eine gibt.
- `von_unten: bool = True`
- `satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG` – Ob `f_yd` die Bemessungs- oder die charakteristische Fliessgrenze ist.

#### Posten.symbol_f_yd

```python
@property
def symbol_f_yd(self) -> str
```

`f_{yd,        ext{B500B}}` -- die Posten einer Lage koennen sich
unterscheiden, darum je Posten.

### Lage

```python
@dataclass(frozen=True)
class Lage
```

Die zu einer Seite zusammengefasste Bewehrung.

- `a_s: float`
- `z: float`
- `f_yd: float`
- `E_s: float`
- `text: str = ''`
- `index: str = ''` – Index der zusammengefassten Lage, z.B. `1,x`.
- `stahl_index: str = ''` – Index der massgebenden Stahlsorte -- die mit dem kleinsten `f_yd`. Ohne ihn stuende bei zwei Sorten zweimal `f_yd` mit verschiedenen Zahlen im selben Bericht, und niemand koennte sagen, welche Sorte gemeint ist.
- `teile: Tuple[Posten, ...] = ()` – Die Posten, aus denen sie entstanden ist -- fuer die Mitschrift.
- `satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG`

#### Lage.symbol_flaeche

```python
@property
def symbol_flaeche(self) -> str
```

`A_{s,1,x}` -- oder schlicht `A_s`, wenn es keinen Index gibt.

Eine unbewehrte Seite hat keine Lagennummer, also auch keinen Index.
Ihn hier zu erzwingen ergaebe `A_{s,}` mit leerem Tiefstellen; darum
bildet die Lage ihr Symbol selbst, statt es an sieben Stellen
zusammenzusetzen.

#### Lage.symbol_f_yd

```python
@property
def symbol_f_yd(self) -> str
```

`f_{yd,        ext{B500B}}` -- oder `f_{yd}`, solange es nur eine Sorte gibt.

#### Lage.symbol_sigma_sd

```python
@property
def symbol_sigma_sd(self) -> str
```

Die angesetzte Stahlspannung; sie gehoert zur selben Sorte wie f_yd.

#### Lage.symbol_E_s

```python
@property
def symbol_E_s(self) -> str
```

#### Lage.symbol_d

```python
@property
def symbol_d(self) -> str
```

`d_{1,x}` -- oder schlicht `d`. Siehe [[opencivil.nachweis.handrechnung#Lage.symbol_flaeche|symbol_flaeche]].

#### Lage.symbol_z

```python
@property
def symbol_z(self) -> str
```

`z_{1,x}`, die Tiefe ab Oberkante -- oder `z`. Siehe [[opencivil.nachweis.handrechnung#Lage.symbol_flaeche|symbol_flaeche]].

### Eckpunkt

```python
@dataclass(frozen=True)
class Eckpunkt
```

Ein von Hand nachrechenbarer Punkt der Resistenzlinie.

- `kennung: str`
- `symbol: str` – LaTeX -- so steht der Punkt in der Mitschrift.
- `name: str` – Klartext -- fuer Kurzhinweise im Diagramm.
- `N: float` – Normalkraft in N (Zug positiv).
- `M: float` – Moment in Nm (Zug unten positiv).
- `x: Optional[Wert] = field(default=None, compare=False)`
- `d: Optional[Wert] = field(default=None, compare=False)` – Druckzonenhoehe und statische Hoehe -- nur bei M_Rd(N = 0), wie sie dort hergeleitet sind. Daraus rechnen die Kennzahlen der Platte x/d.

### Handrechnung

```python
class Handrechnung
```

Die Eckpunkte einer Richtung, samt Mitschrift.

Rechnet und schreibt in einem Zug -- wie jede Berechnung in diesem Werkzeug.
Was in der Mitschrift steht, ist genau das, was gerechnet wurde.

#### Handrechnung.rechnen

```python
def rechnen(self, p: Protokoll) -> List[Eckpunkt]
```

Rechnet alle Eckpunkte und schreibt die Herleitung.

#### Handrechnung._schwerpunkt

```python
def _schwerpunkt(self, p: Protokoll, lage: Lage) -> None
```

Schreibt, wie Tiefe und Querschnitt einer Lage aus mehreren Posten
entstehen.

Nach Flaechen gewichtet, wie [[opencivil.nachweis.handrechnung#lagen_zusammenfassen|lagen_zusammenfassen]] rechnet: die Lage
traegt die Fliessgrenze ihrer schwaechsten Sorte, also stehen alle
Posten unter derselben Spannung.

#### Handrechnung._groesste_druckkraft

```python
def _groesste_druckkraft(self, p: Protokoll) -> Eckpunkt
```

Reiner Beton ohne Stahl -- die einfachste aller Grenzen.

#### Handrechnung._groesste_zugkraft

```python
def _groesste_zugkraft(self, p: Protokoll) -> Eckpunkt
```

Beide Lagen fliessen auf Zug.

Es gibt hier nur *einen* Punkt, nicht je Momentenvorzeichen einen: der
Dehnungszustand ist eindeutig, also auch das zugehoerige Moment.

#### Handrechnung._seite

```python
def _seite(self, p: Protokoll, seite: Zugseite) -> List[Eckpunkt]
```

Die beiden Punkte eines Momentenvorzeichens -- des Moments, das `seite` zieht.

#### Handrechnung._bei_n_null

```python
def _bei_n_null(self, p: Protokoll, zug: Lage, d: Wert, seite: Zugseite) -> Eckpunkt
```

Reine Biegung: die Druckkraft im Beton haelt der Zugkraft die Waage.

#### Handrechnung._halbe_hoehe

```python
def _halbe_hoehe(self, p: Protokoll, zug: Lage, w_d: Wert, seite: Zugseite) -> Optional[Eckpunkt]
```

Der Punkt mit der Nulllinie auf halber Hoehe: `x = h/2`.

Der Spannungsblock reicht damit bis `0.85 * h/2`. Dieser Punkt liegt
knapp unterhalb des Balancepunkts und gibt dem Polygon den Bauch, den
die genaue Linie unter Druck hat.

**Die Zugbewehrung traegt, was ihre Dehnung hergibt:**
`sigma_sd = min(E_s * eps_s; f_yd)`. Frueher galt der Punkt nur,
solange sie fliesst -- also fuer `d >= h/2 * (1 + eps_yd/eps_c2d)` --,
sonst fiel er weg und mit ihm der ganze Bauch. Bei tief liegender
x-Bewehrung (dicke y-Lage aussen, x in der 2. Lage) lief das Polygon
dann geradlinig vom reinen Druck zu M_Rd(N = 0): bei N = -2000 kN
standen 81 kNm statt rund 250. Die Dehnungsebene ist dieselbe; der
Stahl rechnet nur mit der Spannung, die zu ihr gehoert.

Und er gilt nur, wenn es diese Zugbewehrung ueberhaupt gibt -- unter
der Nulllinie. Ohne sie blieb der Betondruckblock allein stehen und
schob dem Polygon ein Moment unter, das aus nichts stammte: eine
Platte nur mit unterer Bewehrung wies so ein negatives Moment von
220 kNm nach.

### gemeinsamer_index

```python
def gemeinsamer_index(teile: Sequence[Posten]) -> str
```

Der Index der zusammengefassten Lage: das, was ihre Teile gemein haben.

Grundbewehrung und Zulage einer Lage heissen `1,x,g` und `1,x,z` --
zusammengefasst also `1,x`. Gehen die Teile auseinander, bleibt der Index
leer; eine erfundene Bezeichnung waere schlimmer als gar keine.

### lagen_zusammenfassen

```python
def lagen_zusammenfassen(posten: Sequence[Posten]) -> Dict[str, Lage]
```

Fasst die Bewehrungsposten einer Richtung zu zwei Lagen zusammen.

Je Richtung liegen genau zwei Bewehrungslagen, jede davon aus Grund-
bewehrung und Zulage. Fuer die Handrechnung zaehlt je Seite nur die Summe
der Flaechen und ihr gemeinsamer Schwerpunkt.

Gruppiert wird nach `von_unten`, also nach der Zugehoerigkeit zur unteren
oder oberen Lage -- **nicht** nach der Hoehenlage. Grundbewehrung und Zulage
derselben Lage liegen naemlich auf leicht verschiedenen Hoehen, weil ihre
Durchmesser verschieden sind. Wer nach z gruppiert, bekommt drei Gruppen
statt zwei und verliert stillschweigend eine davon.

Die entstandene Lage behaelt ihre Teile ([[opencivil.nachweis.handrechnung#Lage|Lage.teile]]) und ihren
Index. Frueher kamen hier blanke Tupel an, in denen beides fehlte: die
Mitschrift schrieb dann `A_{s,}` mit leerem Index, und die Herleitung des
Schwerpunkts fiel still aus, weil sie `len(teile) > 1` verlangt.


## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.lagenaufbau]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]

## Formeln aus diesem Modul

- [[Beide Lagen fliessen auf Zug]] · `Handrechnung._groesste_zugkraft`
- [[Bewehrungsquerschnitt der zusammengefassten Lage]] · `Handrechnung._schwerpunkt`
- [[Dehnung der Zugbewehrung]] · `Handrechnung._halbe_hoehe`
- [[Druckzonenhöhe aus dem Kräftegleichgewicht]] · `Handrechnung._bei_n_null`
- [[Gleichmässiger Druck, ohne Bewehrung]] · `Handrechnung._groesste_druckkraft`
- [[Kräfte mal Hebelarm um die halbe Höhe]] · `Handrechnung._groesste_zugkraft`
- [[Kräftegleichgewicht]] · `Handrechnung._halbe_hoehe`
- [[Momentengleichgewicht um die halbe Höhe]] · `Handrechnung._halbe_hoehe`
- [[Momentenwiderstand bei reiner Biegung]] · `Handrechnung._bei_n_null`
- [[Nulllinie auf halber Höhe]] · `Handrechnung._halbe_hoehe`
- [[Schwerpunkt der zusammengefassten Lage]] · `Handrechnung._schwerpunkt`
- [[Stahlspannung, höchstens die Fliessgrenze]] · `Handrechnung._halbe_hoehe`
