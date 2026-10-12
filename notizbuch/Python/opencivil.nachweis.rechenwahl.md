---
erzeugt: 264f824c3922
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/rechenwahl.py
> womit ein Kapitel rechnet.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/rechenwahl.py)

## VERANTWORTUNG

Was ein Nachweis-Kapitel waehlt -- die Kriechzahl, den Wertesatz und die
Rechenart -- und die eine Stelle, die daraus die Werkstoffgesetze und den
Querschnittsloeser baut. Die Kapitel der Platte und die
Spannung-Dehnung-Analyse fragen hier, keines baut seine Gesetze selbst.


## DIE RECHENARTEN

* **Handrechnung** -- im Loeser derselbe Querschnitt wie in der
  Resistenzlinie aus Handrechnung: der Spannungsblock, die Bewehrung nur auf
  Zug, je Seite zu einer Lage im Schwerpunkt zusammengefasst, und der Beton
  auch dort gezaehlt, wo der Stahl liegt. Die gedrueckte Bewehrung zaehlt
  nicht -- in keiner anderen Rechenart fehlt sie.
* **0.85·x-Vereinfachung** -- derselbe Spannungsblock, ueber die Hoehe
  integriert, jede Faser mit ihrer mittleren Spannung. Die gedrueckte
  Bewehrung wirkt mit und verdraengt den Beton an ihrer Stelle.
* **Praezise ohne Vereinfachung** -- die Parabel-Rechteck-Beziehung, ihr
  Anstieg mit dem wirksamen Modul `E_cm/(1+phi)`, `k_sigma` nie unter 1.
* **elastisch** -- nur fuer die Stahlspannungen: der Beton linear mit
  `E_cm/(1+phi)`, hoechstens `f_c`. So rechneten sie bis 2026-10-09 fest.

Die Namen hat der Benutzer am 2026-10-12 gewaehlt; vorher hiessen sie
«Handrechnung Block 0.85·x», «Block 0.85·x genau» und «Parabel».


## WER WAS ANBIETET

Die Handrechnung gibt es nur, wo ein Polygon aus Eckpunkten Sinn ergibt: in
der Tragsicherheit und bei den Stahlspannungen. Beim Knicken und in den
Spannung-Dehnung-Analysen wird die Normalkraft genau gerechnet, Ebene fuer
Ebene -- dort waere die Handrechnung nur der Spannungsblock mit
weggelassener Druckbewehrung, also eine schlechtere 0.85·x-Vereinfachung
([[opencivil.nachweis.rechenwahl#Konstanten|FASERARTEN]]).

Die Kriechzahl wirkt nur bei praezise und elastisch: an den anderen Gesetzen
haengt kein Modul. Der Wertesatz bestimmt, wo die Plateaus liegen
([[opencivil.nachweis.querschnittsloeser#Werkstoffsatz|Werkstoffsatz]]), und wie ein Widerstand heisst -- `R_d` oder
`R_k`.

## Inhalt

### Rechenart

```python
class Rechenart(str, Enum)
```

Wie der Querschnitt gerechnet wird -- siehe Dateikopf.

- `HANDRECHNUNG = 'handrechnung'`
- `BLOCK = 'block'`
- `PARABEL = 'parabel'`
- `ELASTISCH = 'elastisch'`

#### Rechenart.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Rechenart.kurz

```python
@property
def kurz(self) -> str
```

Fuer schmale Zeilen -- etwa die Auswahl auf der Karte einer Analyse.

#### Rechenart.latex

```python
@property
def latex(self) -> str
```

Der Name als Formeltext -- fuer die Zeile «Rechenwahl» der Herleitung.

#### Rechenart.mit_kriechzahl

```python
@property
def mit_kriechzahl(self) -> bool
```

Ob `phi` etwas aendert -- nur, wo ein Gesetz am Modul haengt.

#### Rechenart.mit_block

```python
@property
def mit_block(self) -> bool
```

Ob der Beton als Spannungsblock rechnet.

### Rechenwahl

```python
@dataclass(frozen=True)
class Rechenwahl
```

Was ein Kapitel waehlt: Kriechzahl, Wertesatz, Rechenart.

- `kriechzahl: float = 0.0`
- `satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG`
- `art: Rechenart = Rechenart.HANDRECHNUNG`

#### Rechenwahl.aus

```python
@classmethod
def aus(cls, kriechzahl: float, werkstoffsatz: str, rechenart: str) -> 'Rechenwahl'
```

Aus den Feldern einer Beschreibung -- Zahl und zwei Namen.

#### Rechenwahl.index

```python
@property
def index(self) -> str
```

`Rd` oder `Rk` -- wie ein Widerstand dieser Wahl heisst.

#### Rechenwahl.beschriftung

```python
@property
def beschriftung(self) -> str
```

Fuer Legenden: «Präzise ohne Vereinfachung, φ = 2, Bemessung» -- phi nur, wo es wirkt.

### Kennwerte

```python
@dataclass(frozen=True)
class Kennwerte
```

Die Zahlen, aus denen die Gesetze entstehen -- SI, im Wertesatz der Wahl.

- `f_c: float` – `f_cd` oder `f_ck`.
- `f_s: float` – `f_yd` oder `f_yk` -- dort beginnt das Plateau im Zug.
- `f_s_druck: float` – Dasselbe im Druck.
- `E_cm: float`
- `E_s: float`
- `eps_c1d: float`
- `eps_c2d: float`

#### Kennwerte.aus_eingaben

```python
@classmethod
def aus_eingaben(cls, e: Eingaben, satz: Werkstoffsatz) -> 'Kennwerte'
```

Aus den Eingaben, die [[opencivil.nachweis.rechenwahl#werkstoffbezuege|werkstoffbezuege]] anmeldet.

### werkstoffbezuege

```python
def werkstoffbezuege(satz: Werkstoffsatz, beton, stahl) -> List[Eingabebezug]
```

Was die Gesetze einer Wahl brauchen -- unter den Kurznamen des Wertesatzes,
`f_cd` oder `f_ck` usw. So steht in der Herleitung das Zeichen, mit dem
gerechnet wird.

### bezuege_vereinen

```python
def bezuege_vereinen(*listen: Sequence[Eingabebezug]) -> List[Eingabebezug]
```

Mehrere Listen von Eingaben zu einer -- jeder Name einmal.

Derselbe Name mit derselben Wert-ID ist dieselbe Eingabe und wird einmal
angemeldet. Derselbe Name mit einer anderen ID waere eine Verwechslung:
die Rechnung laese dann die eine Zahl unter dem Namen der anderen.

### betongesetz

```python
def betongesetz(wahl: Rechenwahl, *, f_c: float, E_cm: float, eps_c1d: float, eps_c2d: float) -> Gesetz
```

Der Beton im gerissenen Zustand -- je Rechenart. Die eine Stelle fuer
die Parabel und den Block: der Loeser und die genaue Resistenzlinie
bekommen ihren Beton beide hier.

### stahlgesetz

```python
def stahlgesetz(wahl: Rechenwahl, w: Kennwerte, *, eps_ud: float) -> Gesetz
```

Der Stahl -- in der Handrechnung nur auf Zug.

### Gesetze

```python
@dataclass(frozen=True)
class Gesetze
```

Was zu einer Wahl gehoert -- Gesetze, Lagen, und wie die Fasern rechnen.

- `wahl: Rechenwahl`
- `beton: Gesetz`
- `stahl: Gesetz`

#### Gesetze.gemittelt

```python
@property
def gemittelt(self) -> bool
```

Der Block springt: ueber jede Faser gemittelt, sonst springt N mit.

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
def loeser(self, *, h: float, b: float, lagen: Sequence[Stahllage], beton: Gesetz=None, **fenster) -> Querschnittsloeser
```

Der Loeser zu dieser Wahl. `fenster` sind die Grenzen der Suche
(`eps_druck`, `eps_zug`, `grenzen`) -- die bringt jeder Nutzer
selbst mit. `beton` ersetzt das Betongesetz, etwa durch den
ungerissenen Zustand; alles andere bleibt.

### protokoll_rechenwahl

```python
def protokoll_rechenwahl(p: Protokoll, wahl: Rechenwahl, basis: str, *, titel: str='Rechenwahl') -> Wert
```

Womit das Kapitel rechnet, in einer Zeile: phi (nur wo es wirkt), Werte,
Rechenart. Zurueck kommt phi als Wert -- fuer die Formeln danach.

### protokoll_gesetze

```python
def protokoll_gesetze(p: Protokoll, wahl: Rechenwahl, e: Eingaben, basis: str, *, titel: str) -> None
```

Die Werkstoffgesetze der Wahl, mit den Zeichen ihres Wertesatzes.

Der wirksame Modul steht nicht hier: wo er gebraucht wird, schreibt ihn
das Kapitel an der Stelle, an der er erklaert wird
([[opencivil.nachweis.querschnittsloeser#protokoll_wirksamer_modul|protokoll_wirksamer_modul]]).

### protokoll_betongesetz

```python
def protokoll_betongesetz(p: Protokoll, wahl: Rechenwahl, f_c: Wert, E_cm: Wert, basis: str, *, titel: str) -> None
```

Der Beton einer Wahl mit Block oder Parabel -- bei der Parabel samt ihrem
Beiwert aus dem wirksamen Modul `E_cm/(1+phi)`. `f_c` ist die
Festigkeit des Wertesatzes, `f_cd` oder `f_ck`.

### gesetze

```python
def gesetze(wahl: Rechenwahl, w: Kennwerte, *, eps_ud: float=0.045) -> Gesetze
```

Die Gesetze zu einer Wahl. `eps_ud` bringt der Nutzer mit: die
Stahlspannungen rechnen bis heute mit 4.5 %, das Knicken und die Analysen
mit dem Wert der Stahlsorte.


## Konstanten

- `RECHENARTEN = (Rechenart.HANDRECHNUNG, Rechenart.BLOCK, Rechenart.PARABEL)` – Was die Tragsicherheit anbietet.
- `SPANNUNGSARTEN = RECHENARTEN + (Rechenart.ELASTISCH,)` – Die Stahlspannungen zusaetzlich elastisch.
- `FASERARTEN = (Rechenart.BLOCK, Rechenart.PARABEL)` – Was das Knicken und die Spannung-Dehnung-Analysen anbieten: nur, was ueber die Fasern rechnet -- siehe «Wer was anbietet» oben.
- `ERSATZ_ALTER_WAHL = {Rechenart.HANDRECHNUNG.value: Rechenart.BLOCK.value}` – Was eine Datei von vor 2026-10-12 dort noch waehlen durfte, wo es die Wahl heute nicht mehr gibt -- und was daraus wird: aus der Handrechnung beim Knicken und in den Analysen derselbe Spannungsblock, ueber die Fasern gerechnet. Die Druckbewehrung zaehlt dann mit; der Widerstand steigt darum leicht.
- `STAHL_NUR_ZUG = 'Betonstahl nur auf Zug'` – Die Seite im Notizbuch fuer den Stahl der Handrechnung, der nur Zug traegt.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.platte]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Beiwert der Parabel, mit dem wirksamen Modul]] · `protokoll_betongesetz`
- [[Betonstahl nur auf Zug]] · `protokoll_gesetze`
- [[Parabel-Rechteck-Beziehung des Betons]] · `protokoll_betongesetz`
- [[Spannungsblock des Betons]] · `protokoll_betongesetz`
