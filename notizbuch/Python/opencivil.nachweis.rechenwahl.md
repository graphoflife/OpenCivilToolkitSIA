---
erzeugt: 8a04889eb51c
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
Querschnittsloeser baut, und welche Rechenarten ein Kapitel anbietet. Die
Kapitel der Platte und die Spannung-Dehnung-Analyse fragen hier, keines baut
seine Gesetze oder Lagen selbst.


## JEDE LAGE MIT IHREM STAHL

Der Editor laesst je Seite einen eigenen Stahl waehlen. Jede Lage traegt
darum ihren Stahl ([[opencivil.nachweis.querschnittsloeser#Stahllage|Stahllage]]), angemeldet wird je Sorte unter
`{kennwert}__{sorte}` ([[opencivil.nachweis.rechenwahl#lagenbezuege|lagenbezuege]]), gebaut von
[[opencivil.nachweis.rechenwahl#stahllagen|stahllagen]]. Bis 2026-10-12 nahmen Stahlspannung, Knicken, Querkraft
und Analyse den Stahl der ersten Lage fuer alle.


## WER WAS ANBIETET

Die Handrechnung gibt es nur, wo ein Polygon aus Eckpunkten Sinn ergibt: in
der Tragsicherheit und bei den Stahlspannungen. Beim Knicken und in den
Spannung-Dehnung-Analysen wird die Normalkraft genau gerechnet, Ebene fuer
Ebene -- dort waere die Handrechnung nur der Spannungsblock mit
weggelassener Druckbewehrung, also eine schlechtere 0.85·x-Vereinfachung
([[opencivil.nachweis.rechenwahl#Konstanten|FASERARTEN]]). Der gezeichnete Querschnitt rechnet immer ueber die
Fasern: seine Stahlspannungen bieten darum die Fasern und «elastisch» an,
ohne Handrechnung ([[opencivil.nachweis.rechenwahl#Konstanten|FASERSPANNUNGSARTEN]]).

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

Die Zahlen, aus denen das Betongesetz entsteht -- SI, im Wertesatz der
Wahl. Den Stahl traegt jede Lage selbst ([[opencivil.nachweis.rechenwahl#stahllagen|stahllagen]]).

- `f_c: float` – `f_cd` oder `f_ck`.
- `E_cm: float`
- `eps_c1d: float`
- `eps_c2d: float`

#### Betonkennwerte.aus_eingaben

```python
@classmethod
def aus_eingaben(cls, e: Eingaben, satz: Werkstoffsatz) -> 'Betonkennwerte'
```

Aus den Eingaben, die [[opencivil.nachweis.rechenwahl#betonbezuege|betonbezuege]] anmeldet.

### betonbezuege

```python
def betonbezuege(satz: Werkstoffsatz, beton) -> List[Eingabebezug]
```

Was das Betongesetz einer Wahl braucht -- unter den Kurznamen des
Wertesatzes, `f_cd` oder `f_ck`. So steht in der Herleitung das
Zeichen, mit dem gerechnet wird. Die Reihenfolge ist die, in der die
Werte in der Herleitung der Baustoffe erscheinen.

### staehle

```python
def staehle(posten) -> List
```

Die Staehle der Posten, jeder einmal, in der Reihenfolge der Posten.

### stahlname

```python
def stahlname(kennwert: str, stahl) -> str
```

Der Name, unter dem ein Kennwert dieses Stahls eingeht: `E_s__s1`.

### stahlbezuege

```python
def stahlbezuege(posten, kennwerte: Sequence[str]) -> List[Eingabebezug]
```

Je Stahl der Posten diese Kennwerte, unter [[opencivil.nachweis.rechenwahl#stahlname|stahlname]].

### lagenbezuege

```python
def lagenbezuege(posten, satz: Werkstoffsatz) -> List[Eingabebezug]
```

Was [[opencivil.nachweis.rechenwahl#stahllagen|stahllagen]] liest: je Posten Flaeche und Tiefe, je Stahl
seine Kennwerte im Wertesatz der Wahl.

### stahllagen

```python
def stahllagen(posten, satz: Werkstoffsatz, wert: Callable[[str], float]) -> List[Stahllage]
```

Je Bewehrungsposten eine Lage, mit dem Stahl ihrer Lage im Wertesatz der
Wahl -- die eine Stelle, die Lagen baut.

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
def lagen(self, lagen: Sequence[Stahllage], h: float) -> List[Stahllage]
```

Die Lagen, mit denen gerechnet wird -- in der Handrechnung je Seite eine.

#### Gesetze.loeser

```python
def loeser(self, *, h: float, b: float, lagen: Sequence[Stahllage], beton: Gesetz=None, klasse: Type[Querschnittsloeser]=Querschnittsloeser, **fenster) -> Querschnittsloeser
```

Der Loeser zu dieser Wahl. `fenster` sind die Grenzen der Suche
(`eps_druck`, `eps_zug`, `grenzen`) -- die bringt jeder Nutzer
selbst mit. `beton` ersetzt das Betongesetz, etwa durch den
ungerissenen Zustand; alles andere bleibt. `klasse` waehlt, wie
gesucht wird -- das Knicken nimmt
[[opencivil.nachweis.querschnittsloeser#QuerschnittsloeserIllinois|QuerschnittsloeserIllinois]].

### protokoll_rechenwahl

```python
def protokoll_rechenwahl(p: Protokoll, wahl: Rechenwahl, basis: str, *, titel: str='Rechenwahl') -> Wert
```

Womit das Kapitel rechnet, in einer Zeile: phi (nur wo es wirkt), Werte,
Rechenart. Zurueck kommt phi als Wert -- fuer die Formeln danach.

### protokoll_gesetze

```python
def protokoll_gesetze(p: Protokoll, wahl: Rechenwahl, e: Eingaben, basis: str, *, titel: str, posten) -> None
```

Die Werkstoffgesetze der Wahl, so wie gerechnet wird: jedes Gesetz
schreibt sich selbst
([[opencivil.querschnitt.werkstoffgesetz#Gesetz.protokoll|protokoll]]), mit den
Werten, mit denen es rechnet -- der Beton mit dem wirksamen Modul, jeder
Stahl der Posten mit seinen; bei mehreren Staehlen mit dem Namen im Titel.

Der wirksame Modul selbst steht nicht hier: wo er gebraucht wird, schreibt
ihn das Kapitel an der Stelle, an der er erklaert wird
([[opencivil.nachweis.querschnittsloeser#protokoll_wirksamer_modul|protokoll_wirksamer_modul]]).

### gesetze

```python
def gesetze(wahl: Rechenwahl, w: Betonkennwerte) -> Gesetze
```

Die Gesetze zu einer Wahl. Der Stahl kommt je Lage dazu, samt seinem
`eps_ud` -- bis 2026-10-12 rechneten die Stahlspannungen fest mit 4.5 %,
das Knicken und die Analysen mit dem der ersten Lage.


## Konstanten

- `RECHENARTEN = (Rechenart.HANDRECHNUNG, Rechenart.BLOCK, Rechenart.PARABEL)` – Was die Tragsicherheit anbietet.
- `SPANNUNGSARTEN = RECHENARTEN + (Rechenart.ELASTISCH,)` – Die Stahlspannungen zusaetzlich elastisch.
- `FASERARTEN = (Rechenart.BLOCK, Rechenart.PARABEL)` – Was das Knicken und die Spannung-Dehnung-Analysen anbieten: nur, was ueber die Fasern rechnet -- siehe «Wer was anbietet» oben.
- `FASERSPANNUNGSARTEN = FASERARTEN + (Rechenart.ELASTISCH,)` – Die Stahlspannungen des gezeichneten Querschnitts: ueber die Fasern, dazu elastisch -- eine Handrechnung gibt es dort nicht.
- `VERFORMUNGSARTEN = (Rechenart.PARABEL,)` – Was die Verformung beim Knicken anbietet: nur praezise -- siehe «Wer was anbietet» oben.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.web.api]]
