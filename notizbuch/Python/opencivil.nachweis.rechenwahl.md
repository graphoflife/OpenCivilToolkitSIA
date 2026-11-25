---
erzeugt: f74b52e809c9
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/rechenwahl.py
> womit ein Kapitel rechnet.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/rechenwahl.py)

## VERANTWORTUNG

Was ein Nachweis-Kapitel aus seiner Wahl macht -- der Kriechzahl, dem
Wertesatz und der Rechenart ([[opencivil.querschnitt.gesetzwahl]]): die
eine Stelle, die daraus die Werkstoffgesetze, die Bewehrungslagen und den
Querschnitt der Platte samt Loeser baut, und welche Rechenarten ein Kapitel
anbietet. Die
Kapitel der Platte und die Spannung-Dehnung-Analyse fragen hier, keines baut
seine Gesetze oder Lagen selbst.


## JE MATERIAL SEIN WERTESATZ

Ein Kapitel waehlt den Wertesatz je Baustoff
([[opencivil.querschnitt.gesetzwahl#Wertesaetze|Wertesaetze]]): der Beton liest
`f_cd` oder `f_ck` nach seinem, jeder Stahl `f_yd` oder `f_yk`
nach seinem (Benutzer, 2026-11-20). Die Herleitung nennt ihn einmal, wenn
alle denselben haben, sonst je Baustoff ([[opencivil.nachweis.rechenwahl#protokoll_rechenwahl|protokoll_rechenwahl]]).


## JEDE LAGE MIT IHREM STAHL

Der Editor laesst je Seite einen eigenen Stahl waehlen. Jede Lage traegt
darum ihren Stahl ([[opencivil.nachweis.querschnittsloeser#Stahllage|Stahllage]]), angemeldet wird je Sorte unter
`{kennwert}__{sorte}` ([[opencivil.nachweis.rechenwahl#lagenbezuege|lagenbezuege]],
[[opencivil.material.basis#Baustoff.eingabename|eingabename]]), gebaut von
[[opencivil.nachweis.rechenwahl#stahllagen|stahllagen]]. Bis 2026-10-12 nahmen Stahlspannung, Knicken, Querkraft
und Analyse den Stahl der ersten Lage fuer alle.


## WER WAS ANBIETET

Die Handrechnung gibt es nur, wo ein Polygon aus Eckpunkten Sinn ergibt: in
der Tragsicherheit und bei den Stahlspannungen. Beim Knicken und in den
Spannung-Dehnung-Analysen wird die Normalkraft genau gerechnet, Ebene fuer
Ebene -- dort waere die Handrechnung nur der Spannungsblock mit
weggelassener Druckbewehrung, also eine schlechtere 0.85·x-Vereinfachung
([[opencivil.nachweis.rechenwahl#Konstanten|FASERARTEN]]). Der gezeichnete Querschnitt rechnet immer ueber die
Fasern: auch seine Stahlspannungen bieten darum keine Handrechnung an. Bis
2026-11-25 boten die Stahlspannungen dazu «elastisch» an
([[opencivil.querschnitt.gesetzwahl]]).

Die Verformung beim Knicken rechnet nur praezise ([[opencivil.nachweis.rechenwahl#Konstanten|VERFORMUNGSARTEN]],
Benutzer, 2026-10-15). Mit dem Spannungsblock hat das Moment ueber der
Kruemmung flache Stuecke: dort traegt jede Kruemmung dasselbe Moment, die
Ausmitte zweiter Ordnung ist nicht eindeutig, und nahe der Grenzkraft hing
N_Rd davon ab, wie gesucht wurde -- an der Stuetze des Pruefprojekts
4099.5 kN halbiert, 4200 kN mit Warmstart.

## Inhalt

### Betonkennwerte

```python
@dataclass(frozen=True)
class Betonkennwerte
```

Die Zahlen, aus denen das Betongesetz entsteht -- SI, im Wertesatz des
Betons. Den Stahl traegt jede Lage selbst ([[opencivil.nachweis.rechenwahl#stahllagen|stahllagen]]).

- `f_c: float` – `f_cd` oder `f_ck`.
- `E_c: float` – Der Modul der Wahl, ohne Kriechen: `E_cm`, beim Knicken `E_cd`.
- `eps_c1d: float`
- `eps_c2d: float`
- `name: str = ''` – Der Name des Betons («C30/37») -- so heissen die Grenzen seiner Dehnung.

#### Betonkennwerte.aus_eingaben

```python
@classmethod
def aus_eingaben(cls, e: Eingaben, wahl: Rechenwahl, beton) -> 'Betonkennwerte'
```

Aus den Eingaben, die [[opencivil.nachweis.rechenwahl#betonbezuege|betonbezuege]] fuer `beton` anmeldet.

### betonbezuege

```python
def betonbezuege(satz: Werkstoffsatz, beton, *, modul: str='E_cm') -> List[Eingabebezug]
```

Was das Betongesetz einer Wahl braucht -- unter den Kurznamen des
Wertesatzes dieses Betons, `f_cd` oder `f_ck`, und des Moduls der Wahl
([[opencivil.querschnitt.gesetzwahl#Rechenwahl|modul]]). So steht in
der Herleitung das Zeichen, mit dem gerechnet wird. Die Reihenfolge ist
die, in der die Werte in der Herleitung der Baustoffe erscheinen.

### staehle

```python
def staehle(posten: Sequence[Postenbezug]) -> List
```

Die Staehle der Posten, jeder einmal, in der Reihenfolge der Posten.

### stahlbezuege

```python
def stahlbezuege(posten: Sequence[Postenbezug], kennwerte: Sequence[str]) -> List[Eingabebezug]
```

Je Stahl der Posten diese Kennwerte, unter seinem [[opencivil.material.basis#Baustoff.eingabename|eingabename]].

### lagenbezuege

```python
def lagenbezuege(posten: Sequence[Postenbezug], wahl: Rechenwahl) -> List[Eingabebezug]
```

Was [[opencivil.nachweis.rechenwahl#stahllagen|stahllagen]] liest: je Posten Flaeche und Tiefe, je Stahl
seine Kennwerte in seinem Wertesatz.

### stahllagen

```python
def stahllagen(posten: Sequence[Postenbezug], wahl: Rechenwahl, wert: Callable[[str], float]) -> List[Stahllage]
```

Je Bewehrungsposten eine Lage, mit dem Stahl ihrer Lage in dessen
Wertesatz -- die eine Stelle, die Lagen baut.

`wert` liefert zu einer Wert-ID die Zahl in SI: in einem Nachweis aus
seinen Eingaben (`Eingaben.si_nach_id` ueber [[opencivil.nachweis.rechenwahl#lagenbezuege|lagenbezuege]]), in
der Spannung-Dehnung-Analyse aus der Loesung.

### bezuege_vereinen

```python
def bezuege_vereinen(*listen: Sequence[Eingabebezug]) -> List[Eingabebezug]
```

Mehrere Listen von Eingaben zu einer -- jeder Name einmal.

Derselbe Name mit derselben Wert-ID ist dieselbe Eingabe und wird einmal
angemeldet. Derselbe Name mit einer anderen ID waere eine Verwechslung:
die Rechnung laese dann die eine Zahl unter dem Namen der anderen.

### Gesetze

```python
@dataclass(frozen=True)
class Gesetze
```

Was zu einer Wahl gehoert -- Gesetze, Lagen, und wie die Fasern rechnen.

- `wahl: Rechenwahl`
- `beton: Gesetz`
- `kennwerte: Betonkennwerte` – Die Zahlen des Betons -- seine Grenzdehnungen begrenzen die Suche ([[opencivil.nachweis.rechenwahl#Gesetze|grenzen]]).

#### Gesetze.stahl

```python
def stahl(self, s: Stahlgesetz) -> Stahlgesetz
```

Der Stahl einer Lage, wie der Loeser ihn rechnet -- in der Handrechnung nur auf Zug.

#### Gesetze.verdraengt

```python
@property
def verdraengt(self) -> bool
```

Die Handrechnung zaehlt den Beton auch, wo der Stahl liegt.

#### Gesetze.lagen

```python
def lagen(self, lagen: Sequence[Stahllage]) -> List[Stahllage]
```

Die Lagen, mit denen gerechnet wird -- in der Handrechnung je Seite eine ([[opencivil.nachweis.querschnittsloeser#je_seite|je_seite]]).

#### Gesetze.querschnitt

```python
def querschnitt(self, *, h: float, b: float, lagen: Sequence[Stahllage], streifen: int=FASERN) -> Querschnitt
```

Die Platte als Querschnitt der Interaktion, wie der gezeichnete und der
Pfahl ([[opencivil.querschnitt.interaktion#Querschnitt|Querschnitt]]): ein
Rechteck b·h um die halbe Hoehe, darin je Lage, mit der gerechnet wird
([[opencivil.nachweis.rechenwahl#Gesetze.lagen|lagen]]), ein Stab in ihrer Tiefe. Der Beton gedrueckt bis
`-eps_c2d` samt Punkt C, jeder Stahl bis `±eps_ud`: die Grenzen
zieht die Interaktion an beiden Raendern, an den Punkten C und an den
aeussersten Lagen jedes Stahls -- benannt nach Beton und Stahl. Eine
Lage ist ein Band ueber die ganze Breite: der Beton, den sie
verdraengt, so dick wie ihr Stahl ueber b verschmiert.

`streifen` wie beim gezeichneten Querschnitt: so viele, wie ein
Loeser Fasern hat ([[opencivil.querschnitt.fasern#Konstanten|FASERN]]), ohne
Angabe; die genaue Resistenzlinie nimmt mehr. Bis 2026-11-20 baute
die Platte ihre Fasern, Grenzen und Faecher selbst.

#### Gesetze.loeser

```python
def loeser(self, *, h: float, b: float, lagen: Sequence[Stahllage], suche: Suche=HALBIEREN) -> Faserloeser
```

Der Loeser zu dieser Wahl: der Querschnitt ([[opencivil.nachweis.rechenwahl#Gesetze.querschnitt|querschnitt]]) mit
Zug unten, im Fenster seiner Grenzen. Ein Fenster fuer jeden Loeser
der Platte -- Stahlspannung, Knicken, Analysen. Bis 2026-10-18
suchten die Stahlspannungen den Beton fest bis 3 ‰ und den Stahl am
Betonrand, das Knicken mit `eps_c2d`, aber den Stahl ebenso am Rand
(Benutzer, 2026-10-18). `suche` sagt, wie gesucht wird -- das
Knicken nimmt [[opencivil.core.suche#Konstanten|ILLINOIS]].

### protokoll_rechenwahl

```python
def protokoll_rechenwahl(p: Protokoll, wahl: Rechenwahl, basis: str, stoffe: Sequence, *, titel: str='Rechenwahl') -> Wert
```

Womit das Kapitel rechnet, in einer Zeile: phi (nur wo es wirkt), Werte,
Rechenart. Rechnen alle `stoffe` mit demselben Wertesatz, steht er
einmal da, sonst je Baustoff mit seinem Namen -- ebenso die Rechenart je
Beton. Zurueck kommt phi als Wert -- fuer die Formeln danach.

### protokoll_gesetze

```python
def protokoll_gesetze(p: Protokoll, wahl: Rechenwahl, e: Eingaben, basis: str, *, titel: str, beton, posten) -> None
```

Die Werkstoffgesetze der Wahl, so wie gerechnet wird: jedes Gesetz
schreibt sich selbst
([[opencivil.querschnitt.werkstoffgesetz#Gesetz.protokoll|protokoll]]), mit den
Werten, mit denen es rechnet -- der Beton mit dem wirksamen Modul, jeder
Stahl der Posten mit seinen, jeder in seinem Wertesatz; bei mehreren
Staehlen mit dem Namen im Titel.

Der wirksame Modul selbst steht nicht hier: wo er gebraucht wird, schreibt
ihn das Kapitel an der Stelle, an der er erklaert wird
([[opencivil.nachweis.querschnittsloeser#protokoll_wirksamer_modul|protokoll_wirksamer_modul]]).

### protokoll_gesetze_nach_wahl

```python
def protokoll_gesetze_nach_wahl(p: Protokoll, e: Eingaben, analyse: Querschnittsanalyse, wahl: Rechenwahl, basis: str, *, titel: str) -> None
```

Die Werkstoffgesetze einer Wahl, je Material eines gezeichneten
Querschnitts -- die von
[[opencivil.querschnitt.analyse#Querschnittsanalyse.querschnitt|querschnitt]];
jedes schreibt sich selbst, mit seinen Werten, wie bei der Platte
([[opencivil.nachweis.rechenwahl#protokoll_gesetze|protokoll_gesetze]]). Vor jedem Beton sein wirksamer Modul, wo ein
Gesetz an ihm haengt. Fuer die Gebrauchsnachweise und das Knicken des
gezeichneten Querschnitts.

### gesetze

```python
def gesetze(wahl: Rechenwahl, w: Betonkennwerte, *, ungerissen: bool=False) -> Gesetze
```

Die Gesetze zu einer Wahl, `ungerissen` mit dem ungerissenen Beton
([[opencivil.querschnitt.gesetzwahl#betongesetz|betongesetz]]) -- fuer ein
Bauteil mit einem Beton, der Platte: seine Rechenart ist die der Wahl
([[opencivil.querschnitt.gesetzwahl#Rechenwahl.art|art]]). Der Stahl kommt
je Lage dazu, samt seinem `eps_ud` -- bis 2026-10-12 rechneten die
Stahlspannungen fest mit 4.5 %, das Knicken und die Analysen mit dem der
ersten Lage.


## Konstanten

- `RECHENARTEN = (Rechenart.HANDRECHNUNG, Rechenart.BLOCK, Rechenart.PARABEL)` – Was die Tragsicherheit anbietet.
- `FASERARTEN = (Rechenart.BLOCK, Rechenart.PARABEL)` – Was das Knicken und die Spannung-Dehnung-Analysen anbieten: nur, was ueber die Fasern rechnet -- siehe «Wer was anbietet» oben.
- `VERFORMUNGSARTEN = (Rechenart.PARABEL,)` – Was die Verformung beim Knicken anbietet: nur praezise -- siehe «Wer was anbietet» oben.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.suche]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.fasern]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.lagenaufbau]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querkraft_ohne_buegel]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.staebe]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.web.api]]
