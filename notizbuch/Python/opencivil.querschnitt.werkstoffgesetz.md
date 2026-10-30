---
erzeugt: d669fc86a082
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/werkstoffgesetz.py
> Spannungs-Dehnungs-Beziehungen.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/werkstoffgesetz.py)

## VERANTWORTUNG

Jedes Werkstoffgesetz ist ein Objekt, das rechnet und sich selbst als Formel
schreibt -- dieselben Werte, dieselben Aeste. Beton: die
Parabel-Rechteck-Beziehung (SIA 262:2025, 4.2.1.6, [[opencivil.querschnitt.werkstoffgesetz#Betongesetz|Betongesetz]]), der
Spannungsblock 0.85·x ([[opencivil.querschnitt.werkstoffgesetz#Spannungsblock|Spannungsblock]]), linear ohne Zug
([[opencivil.querschnitt.werkstoffgesetz#BetonElastisch|BetonElastisch]]) und ungerissen ([[opencivil.querschnitt.werkstoffgesetz#BetonUngerissen|BetonUngerissen]]).
Betonstahl: bilinear, auf Zug und Druck getrennt begrenzt, oder nur auf Zug
([[opencivil.querschnitt.werkstoffgesetz#Stahlgesetz|Stahlgesetz]], 4.2.2.4).

Bis 2026-10-16 rechneten Funktionen im Loeser, und gedruckt wurden Klassen
mit Platzhaltern oder Formeln von Hand. Jenseits von eps_c2d und beim
gedrueckten Stahl stand in der Herleitung etwas anderes, als gerechnet wurde.


## IN DIE HERLEITUNG

Jedes Gesetz schreibt sich selbst ([[opencivil.querschnitt.werkstoffgesetz#Gesetz.protokoll|Gesetz.protokoll]]): als Formel mit
den Zeichen der Werte, mit denen es rechnet, unter dem Namen seiner Seite im
Notizbuch, und danach diese Werte. Die Werte bringt, wer schreibt -- je
Rolle ([[opencivil.querschnitt.werkstoffgesetz#Konstanten|Werte]]), denn wie ein Kennwert im Rechenwerk heisst, weiss die
Platte anders als der gezeichnete Querschnitt. Bis 2026-10-17 schrieben fuenf
Stellen die Gesetze an, jede mit eigener Weiche nach Art des Gesetzes.


## JENSEITS DER GRENZDEHNUNG

Null: eine Faser jenseits ihrer Bruchstauchung oder Bruchdehnung traegt
nicht, und eine Suche bleibt im gueltigen Bereich. Auf der Grenze selbst
gilt das Gesetz -- auch um eine Rundung darueber ([[opencivil.querschnitt.werkstoffgesetz#Konstanten|RUNDUNG]]): wer den
Rand abfaehrt, die genaue Resistenzlinie, legt eine Lage genau auf `eps_ud`,
und die darf nicht an der letzten Stelle auf null kippen. Bis 2026-10-16
hielt der Loeser die Grenze hart und die Linie gar nicht -- zwei Gesetze fuer
eines.


## VORZEICHEN (im ganzen Querschnittsmodul gleich)

```
Dehnung   eps > 0  =  Zug
Spannung  sig > 0  =  Zug
```


## SCHNELL

Die Gesetze laufen in der Faserintegration hunderttausendfach. Jedes baut
darum einmal seine Funktion (`funktion`) mit blanken SI-Zahlen; die Fasern
rufen sie unmittelbar, ohne den Umweg ueber `__call__`
([[opencivil.querschnitt.fasern]]). Wer `funktion` aendert, misst: ein
`max()` statt eines Vergleichs kostete 28 ms je Platte.

## Inhalt

### k_sigma

```python
def k_sigma(E_c: float, f_c: float) -> float
```

Der Beiwert der Parabel zum Modul `E_c`: `E_c/(400·f_c)`, nie unter 1.

### anteil_punkt_c

```python
def anteil_punkt_c(eps_c1d: float, eps_c2d: float) -> float
```

Wo der Punkt C liegt, als Anteil der Hoehe ab dem gedrueckten Rand:
`1 - eps_c1d/eps_c2d`. Ist der ganze Querschnitt gedrueckt, laufen die
Ebenen des Bruchs durch ihn, mit der Stauchung `-eps_c1d` -- der reine
Druck endet darum bei `-eps_c1d`, nicht bei `-eps_c2d`. Bis
2026-10-16 stand die Formel dreimal da: im Faecher der Platte, in ihren
Grenzen und in der Interaktion des gezeichneten Querschnitts.

### _gebaut

```python
def _gebaut(gesetz, funktion: Funktion) -> None
```

Legt die Funktion an ein eingefrorenes Gesetz -- einmal, beim Bauen.

### Gesetz

```python
@dataclass(frozen=True)
class Gesetz
```

Was jedes Werkstoffgesetz ist: es rechnet -- `funktion`, einmal gebaut,
mit blanken SI-Zahlen --, es heisst wie seine Seite im Notizbuch
([[opencivil.querschnitt.werkstoffgesetz#Gesetz|NAME]]), und es schreibt sich selbst in eine Herleitung
([[opencivil.querschnitt.werkstoffgesetz#Gesetz.protokoll|protokoll]]). `mittel` hat nur ein Gesetz, das springt
([[opencivil.querschnitt.werkstoffgesetz#Spannungsblock.mittel|Spannungsblock.mittel]]).

- `NAME: ClassVar[str] = ''` – Die Seite im Notizbuch -- gleich, wer das Gesetz unter welchem Titel aufschreibt.
- `WORT: ClassVar[str] = ''` – Wie ein Titel das Gesetz nennt: «Beton, Parabel-Rechteck».
- `REFERENZ: ClassVar[str] = ''` – Die Normstelle, wo es eine hat.
- `ROLLEN: ClassVar[Tuple[str, ...]] = ()` – Die Rollen seiner Werte ([[opencivil.querschnitt.werkstoffgesetz#Konstanten|Werte]]), in der Folge der Angabe.
- `WERTTITEL: ClassVar[str] = 'Werte des Betons'` – Was die Zeile mit den Werten heisst.
- `mittel: ClassVar[Optional[Callable[[float, float], float]]] = None`
- `funktion: Funktion = field(init=False, repr=False, compare=False)`

#### Gesetz.spannung

```python
def spannung(self, eps: float) -> float
```

Spannung in N/m^2 zur Dehnung `eps`. Zug positiv.

#### Gesetz.seite

```python
@property
def seite(self) -> str
```

Die Seite im Notizbuch.

#### Gesetz.wort

```python
@property
def wort(self) -> str
```

#### Gesetz.referenz

```python
@property
def referenz(self) -> str
```

#### Gesetz.rollen

```python
@property
def rollen(self) -> Tuple[str, ...]
```

#### Gesetz.formel

```python
def formel(self, werte: Werte) -> str
```

Das Gesetz als Formel, mit den Zeichen von `werte`.

#### Gesetz.protokoll

```python
def protokoll(self, p: Protokoll, werte: Werte, *, titel: str, basis: str='') -> None
```

Das Gesetz in die Herleitung, so wie gerechnet wird: die Formel mit den
Zeichen von `werte` und danach diese Werte. `basis` ordnet die
Zwischenwerte zu, wo ein Gesetz welche hat.

### Betongesetz

```python
@dataclass(frozen=True)
class Betongesetz(Gesetz)
```

Parabel-Rechteck-Beziehung nach SIA 262:2025, 4.2.1.6.

Mit `eta = |eps| / eps_c1d` gilt fuer den Druckbereich:

```
          k_sigma * eta - eta^2
sig = f_cd -----------------------      für 0 <= |eps| <= eps_c1d
          1 + (k_sigma - 2) * eta

sig = f_cd                              für eps_c1d < |eps| <= eps_c2d
```

Jenseits von `eps_c2d` null -- siehe Dateikopf.

- `NAME = 'Parabel-Rechteck-Beziehung des Betons'`
- `WORT = 'Beton, Parabel-Rechteck'`
- `REFERENZ = 'SIA 262:2025, 4.2.1.6'`
- `ROLLEN = ('f_c', 'eps_c1d', 'eps_c2d')`
- `f_cd: float` – Festigkeit in N/m^2 (positiver Betrag) -- je nach Werkstoffsatz `f_cd` oder `f_ck`.
- `eps_c1d: float` – Dehnung am Ende des ansteigenden Astes (positiver Betrag).
- `eps_c2d: float` – Bruchdehnung (positiver Betrag).
- `k_sigma: float` – Gerechnet wird mit mindestens [[opencivil.querschnitt.werkstoffgesetz#Konstanten|K_SIGMA_MIN]] -- siehe dort.

#### Betongesetz.mit_modul

```python
@classmethod
def mit_modul(cls, *, f_c: float, E_c: float, eps_c1d: float, eps_c2d: float) -> 'Betongesetz'
```

Das Gesetz zum Modul `E_c` -- `k_sigma` aus [[opencivil.querschnitt.werkstoffgesetz#k_sigma|k_sigma]], die eine Stelle.

#### Betongesetz.formel

```python
def formel(self, werte: Werte) -> str
```

#### Betongesetz.protokoll

```python
def protokoll(self, p: Protokoll, werte: Werte, *, titel: str, basis: str='') -> None
```

Vorab der Beiwert der Parabel, aus dem Modul `E_c` der Werte.

#### Betongesetz.latex

```python
def latex(self, f: str='f_{cd}') -> str
```

Als Formel -- `f` ist das Zeichen der Festigkeit, `f_{ck}` bei charakteristischen Werten.

### Spannungsblock

```python
@dataclass(frozen=True)
class Spannungsblock(Gesetz)
```

Der vereinfachte, rechteckige Spannungsverlauf des Betons.

Unterhalb von `(1 - 0.85) * eps_c2d` keine Spannung, darueber
durchgehend `f_cd`. Liegt der gedrueckte Rand bei `eps_c2d` -- im
Bruchzustand --, ist das genau der Block der Hoehe `0.85 x`, mit dem die
Handrechnung rechnet. Als Gesetz gilt er auch dort, wo der Rand nicht bei
`eps_c2d` liegt; so setzt ihn die Interaktionslinie des gezeichneten
Querschnitts ein.

Die Normstelle des Blocks ist offen (`notizbuch/Notizen/TODO.md`); sie
wird nicht erfunden.

- `NAME = 'Spannungsblock des Betons'`
- `WORT = f'Beton, Spannungsblock {BLOCKANTEIL}·x'`
- `ROLLEN = ('f_c', 'eps_c2d')`
- `f_cd: float` – Festigkeit des Blocks in N/m^2 (positiver Betrag) -- je nach Werkstoffsatz `f_cd` oder `f_ck`.
- `eps_c2d: float` – Bruchdehnung (positiver Betrag).

#### Spannungsblock.eps_knick

```python
@property
def eps_knick(self) -> float
```

Ab dieser Stauchung (Betrag) setzt der Block ein.

#### Spannungsblock.mittel

```python
def mittel(self, eps_a: float, eps_b: float) -> float
```

Die mittlere Spannung, wenn die Dehnung linear von `eps_a` nach
`eps_b` laeuft -- genau: `f_cd` mal der Anteil, der im Block liegt,
zwischen dem Knick und `-eps_c2d`.

Der Block springt. In der Mitte einer Faser gelesen, springt darum auch
N, sobald eine Faser den Knick ueberschreitet -- am Kastentraeger um
gut 20 kN --, und keine Ebene trifft N_Ed genau. Ueber die Faser
gemittelt, waechst N stetig.

#### Spannungsblock.formel

```python
def formel(self, werte: Werte) -> str
```

#### Spannungsblock.latex

```python
def latex(self, f: str='f_{cd}') -> str
```

Als Formel -- `f` ist das Zeichen der Festigkeit, `f_{ck}` bei charakteristischen Werten.

### Stahlgesetz

```python
@dataclass(frozen=True)
class Stahlgesetz(Gesetz)
```

Bilineare Beziehung ohne Verfestigung nach SIA 262:2025, 4.2.2.4.

Zug und Druck werden getrennt begrenzt, weil `f_yd` und `f_yd^-` in der
Sortentabelle unterschiedlich sein duerfen. `nur_zug`: der gedrueckte
Stahl traegt nichts -- so laesst die Handrechnung die Druckbewehrung weg.

- `NAME = 'Bilineare Beziehung des Betonstahls'`
- `WORT = 'Stahl, bilinear'`
- `REFERENZ = 'SIA 262:2025, 4.2.2.4'`
- `ROLLEN = ('f_s', 'f_s_druck', 'E_s', 'eps_ud')`
- `WERTTITEL = 'Werte des Stahls'`
- `E_s: float` – Elastizitaetsmodul in N/m^2.
- `f_yd: float` – Fliessgrenze auf Zug in N/m^2 -- je nach Werkstoffsatz `f_yd` oder `f_yk`.
- `f_yd_druck: float` – Fliessgrenze auf Druck in N/m^2 (positiver Betrag).
- `eps_ud: float` – Grenzdehnung (positiver Betrag).
- `nur_zug: bool = False` – Der gedrueckte Stahl traegt nichts.

#### Stahlgesetz.eps_yd

```python
@property
def eps_yd(self) -> float
```

#### Stahlgesetz.seite

```python
@property
def seite(self) -> str
```

#### Stahlgesetz.wort

```python
@property
def wort(self) -> str
```

#### Stahlgesetz.referenz

```python
@property
def referenz(self) -> str
```

#### Stahlgesetz.rollen

```python
@property
def rollen(self) -> Tuple[str, ...]
```

#### Stahlgesetz.formel

```python
def formel(self, werte: Werte) -> str
```

#### Stahlgesetz.latex

```python
def latex(self, zug: str='f_{yd}', druck: str='f_{yd}^{-}') -> str
```

Als Formel -- `zug` und `druck` sind die Zeichen der Plateaus.

### _stahlfunktion

```python
def _stahlfunktion(E_s: float, f: float, f_druck: float, eps_ud: float, *, nur_zug: bool) -> Funktion
```

Die Funktion des Stahls, je Fall eine eigene: in der Schleife entscheidet
sie nichts, was schon beim Bauen feststeht. Sind beide Plateaus gleich --
bei den Normsorten --, rechnet sie mit dem Betrag.

### BetonElastisch

```python
@dataclass(frozen=True)
class BetonElastisch(Gesetz)
```

Beton ohne Zugfestigkeit, im Druck linear bis `f_c`, dann waagrecht --
fuer den gerissenen Gebrauchszustand.

`E_c` ist bereits der wirksame Modul, `E_cm/(1+phi)`, falls Kriechen
zaehlt; `f_c` die Festigkeit aus dem Werkstoffsatz, im Gebrauchszustand
`f_ck`. Linear und nicht als Parabel: im Gebrauchszustand liegt die
Betonspannung weit unter der Festigkeit, und dort ist die Parabel eine
Gerade. Die Grenze steht trotzdem da, damit eine Druckzone, die doch
einmal so weit kommt, nicht mehr aufnimmt, als der Beton hergibt. Ohne
`f_c` bleibt das Gesetz unbegrenzt linear -- fuer Rechnungen, die mit
Festigkeiten nichts zu tun haben.

- `NAME = 'Beton linear, ohne Zug'`
- `WORT = 'Beton, linear ohne Zug'`
- `ROLLEN = ('E_c', 'f_c')`
- `E_c: float`
- `f_c: float = math.inf`

#### BetonElastisch.formel

```python
def formel(self, werte: Werte) -> str
```

#### BetonElastisch.latex

```python
def latex(self, E: str='E_{c,eff}', f: str='f_{ck}') -> str
```

Als Formel -- `E` der Modul, `f` die Festigkeit, bei der es waagrecht wird.

### BetonUngerissen

```python
@dataclass(frozen=True)
class BetonUngerissen(Gesetz)
```

Beton linear in beiden Richtungen -- der ungerissene Vergleichszustand.

Ohne Abminderung im Zug und ohne Abbruch bei `f_ct`. Das ist Absicht:
gebraucht wird die *Steifigkeit* des ungerissenen Querschnitts, und wo er
reisst, sagt das Rissmoment -- oberhalb davon gilt die Linie gerissen,
dieser Zustand steht dort nur noch zum Vergleich. Ein Gesetz, das bei
`f_ct` abfiele, waere ausserdem nicht mehr monoton, und die Bisektion
des Loesers braucht Monotonie.

- `NAME = 'Beton ungerissen, in Druck und Zug'`
- `WORT = 'Beton, linear in Druck und Zug'`
- `ROLLEN = ('E_c',)`
- `E_c: float`

#### BetonUngerissen.formel

```python
def formel(self, werte: Werte) -> str
```

#### BetonUngerissen.latex

```python
def latex(self, E: str='E_{c,eff}') -> str
```

Als Formel -- `E` ist der Modul.

### Dehnungsebene

```python
@dataclass(frozen=True)
class Dehnungsebene
```

Eine ebene Dehnungsverteilung ueber die Querschnittshoehe.

Die Bernoulli-Hypothese steckt genau hier: die Dehnung ist linear ueber z.
`z` wird von der Oberkante nach unten gemessen.

- `eps_oben: float` – Dehnung an der Oberkante (z = 0).
- `eps_unten: float` – Dehnung an der Unterkante (z = h).
- `h: float` – Querschnittshoehe in m.

#### Dehnungsebene.durch_zwei_punkte

```python
@classmethod
def durch_zwei_punkte(cls, eps_a: float, z_a: float, eps_b: float, z_b: float, h: float) -> 'Dehnungsebene'
```

Legt die Ebene durch zwei Dehnungspunkte -- so wird der Fächer aufgebaut.

#### Dehnungsebene.bei

```python
def bei(self, z: float) -> float
```

Dehnung auf der Hoehe `z` (von Oberkante nach unten).

#### Dehnungsebene.kruemmung

```python
@property
def kruemmung(self) -> float
```

Kruemmung in 1/m.

#### Dehnungsebene.nulllinie

```python
@property
def nulllinie(self) -> float
```

Lage der Nulllinie in m von der Oberkante.

Bei reiner Zug- oder Druckbeanspruchung gibt es keine -- dann ist das
Ergebnis unendlich, was die Auswertung sauber ueberspringt.


## Konstanten

- `Werte = Mapping[str, Wert]` – Womit ein Gesetz sich anschreibt: je Rolle der Wert, mit seinem Zeichen. Beim Beton die Festigkeit des Wertesatzes `f_c` (`f_cd` oder `f_ck`), der Modul `E_c`, an dem ein Gesetz haengt -- der wirksame, wo Kriechen zaehlt --, und die Dehnungen `eps_c1d` und `eps_c2d`; beim Stahl die Plateaus `f_s` und `f_s_druck`, `E_s` und `eps_ud`.
- `RUNDUNG = 1e-12` – Um so viel darf eine Dehnung ueber ihrer Grenze liegen und gilt noch als auf ihr: eine Rundung. Ein Milliardstel Promille -- weit unter allem, was eine Eingabe oder eine Suche unterscheidet, weit ueber der letzten Stelle.
- `K_SIGMA_MIN = 1.0` – Kleiner rechnet die Parabel `k_sigma` nicht. Darunter haette ihr Nenner `1 + (k_sigma - 2)·eta` im ansteigenden Ast eine Nullstelle, bei `eta = 1/(2 - k_sigma)` -- die Spannung spraenge dort ins Unendliche und wechselte das Vorzeichen. So weit kommt es mit dem kriechweichen Modul: `E_cm/(1 + phi)` mit charakteristischen Werten und `phi = 2` gibt `k_sigma = 0.93`. Mit 1 ist der Beton bis `f_c` bei `eps_c1d` linear. Nach Vorgabe, nicht nachgeschlagen (`notizbuch/Notizen/TODO.md`).
- `K_SIGMA_LATEX = '\\max\\left(1;\\ \\frac{@E_c}{400 \\cdot @f_c}\\right)'` – Dieselbe Regel als Formel, fuer die Herleitung -- mit `@E_c` und `@f_c`.
- `K_SIGMA_SEITE = 'Beiwert der Parabel'` – Ihre Seite im Notizbuch -- eine fuer jede Herleitung, die sie anschreibt, mit welchem Modul auch immer.
- `STAHL_NUR_ZUG = 'Betonstahl nur auf Zug'` – Die Seite im Notizbuch fuer den Stahl der Handrechnung, der nur Zug traegt.
- `_JENSEITS_BETON = ' 0 & |\\varepsilon_c| > \\varepsilon_{c2d} \\quad (\\text{jenseits d…` – Was jenseits der Bruchstauchung gilt -- als Fall in der Formel der Parabel.
- `BLOCKANTEIL = 0.85` – Anteil der Druckzonenhoehe, ueber den der Spannungsblock wirkt. Steht hier und nirgends sonst: die Handrechnung der Platte, ihr Duktilitaetsnachweis, das Diagramm der Werkstoffgesetze und der gezeichnete Querschnitt meinen alle denselben Block.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.nachweis.dehnungsfaecher]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.fasern]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.spannungsanalyse.bild]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.schnitt]]
- [[opencivil.web.diagrammdaten]]

## Formeln aus diesem Modul

- [[Beiwert der Parabel]] · `Betongesetz.protokoll`
- [[Beton linear, ohne Zug]] · `Gesetz.protokoll`
- [[Beton ungerissen, in Druck und Zug]] · `Gesetz.protokoll`
- [[Betonstahl nur auf Zug]] · `Gesetz.protokoll`
- [[Bilineare Beziehung des Betonstahls]] · `Gesetz.protokoll`
- [[Parabel-Rechteck-Beziehung des Betons]] · `Gesetz.protokoll`
- [[Spannungsblock des Betons]] · `Gesetz.protokoll`
