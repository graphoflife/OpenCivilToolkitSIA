---
erzeugt: 42ce49539d20
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_stahl_werte.py
> was Kennzahlen und Nachweise eines Stahlquerschnitts teilen.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_stahl_werte.py)

## VERANTWORTUNG

Die Kennzahlen ([[opencivil.nachweis.qa_stahl_kennzahlen]]) und die
Nachweise je Lastfall ([[opencivil.nachweis.qa_stahl]]) lesen dieselben
Kennwerte und schreiben dieselben Tabellen; beides steht hier, je einmal:

* die Kennwerte je Gruppe -- Baustahl in einer Dicke -- und die Festigkeit,
  mit der gerechnet wird ([[opencivil.nachweis.qa_stahl_werte#Stahlwerte|Stahlwerte]]);
* die Tabelle der Bleche mit ihren Klassen ([[opencivil.nachweis.qa_stahl_werte#klassen|klassen]]);
* die Tabelle der mitwirkenden Breiten in Klasse 4 ([[opencivil.nachweis.qa_stahl_werte#breiten|breiten]]).


## BEMESSUNG ODER CHARAKTERISTISCH

Wie beim Stahlbeton rechnet ein Baustahl mit dem Wertesatz, den die
Tragsicherheit der Analyse fuer ihn waehlt
([[opencivil.querschnitt.gesetzwahl#Werkstoffsatz|Werkstoffsatz]]): mit `f_y/γ_M1`
und `τ_y/γ_M1` oder mit `f_y` und `τ_y`. Die Widerstaende heissen in
beiden Faellen `Rd` -- wie beim Stahlbeton (nach Vorgabe, nicht
nachgeschlagen).

## Inhalt

### stoffbezuege

```python
def stoffbezuege(stahl: Stahlquerschnitt) -> List[Eingabebezug]
```

Die Kennwerte aller Baustaehle des Querschnitts, als Eingaben.

### Stahlwerte

```python
class Stahlwerte
```

Die Kennwerte der Gruppen eines Stahlquerschnitts -- siehe Dateikopf.

#### Stahlwerte.wert

```python
def wert(self, g: int, kurz: str) -> Wert
```

Ein Kennwert der Gruppe `g`, in ihrer Dicke.

#### Stahlwerte.zahl

```python
def zahl(self, g: int, kurz: str) -> float
```

Derselbe als Zahl, Spannungen in N/mm².

#### Stahlwerte.gamma

```python
def gamma(self, g: int) -> float
```

`γ_M1` mit Bemessungswerten, sonst eins.

#### Stahlwerte.f

```python
@cached_property
def f(self) -> List[float]
```

Je Gruppe die Fliessgrenze, mit der gerechnet wird: `f_y/γ_M1` oder `f_y`.

#### Stahlwerte.eps

```python
@cached_property
def eps(self) -> List[float]
```

Je Gruppe `ε` -- immer mit `f_y`.

#### Stahlwerte.mit_gamma

```python
@property
def mit_gamma(self) -> bool
```

Ob einer der Staehle mit Bemessungswerten rechnet -- dann steht `γ_M1` in den Formeln.

#### Stahlwerte.formel

```python
def formel(self, g: int, x: str, zeichen: str='f_y') -> Tuple[str, Dict[str, Wert]]
```

`f_y X/γ_M1` der Gruppe `g` als Vorlage mit ihren Werten -- mit
charakteristischen Werten ohne `γ_M1`. `x` ist `X` in der
Vorlage, etwa `@W`.

#### Stahlwerte.bruch

```python
def bruch(self, oben: str) -> str
```

`oben/γ_M1` als LaTeX, wo mit Bemessungswerten gerechnet wird -- sonst `oben`.

### klassen

```python
def klassen(p: Protokoll, zustaende: Sequence[Blechzustand], freie: Sequence[Teil], titel: str) -> Tuple[int, str]
```

Die Klasse je Blech, als Tabelle, und die des Querschnitts -- die
unguenstigste -- mit dem Namen dessen, was sie bestimmt (ohne Namen in
Klasse 1). Gedrueckte freie Flaechen zaehlen mit Klasse 3.

### breiten

```python
def breiten(p: Protokoll, wirksam: Sequence[Wirksam], titel: str) -> None
```

Die mitwirkenden Breiten der Bleche in Klasse 4, als Tabelle mit ihren Formeln.


## Konstanten

- `KENNWERTE = ('f_y', 'f_y_dick', 'tau_y', 'tau_y_dick', 'gamma_M1', 'E_a')` – Was Kennzahlen und Nachweise je Baustahl lesen.
- `_JEDE_DICKE = ('gamma_M1', 'E_a', 'G_a')` – Was in jeder Dicke gilt -- die anderen Kennwerte haben einen Wert ueber 40 mm. `G_a` liest nur das Kippen ([[opencivil.nachweis.qa_stahl_stabilitaet]]).
- `ROHR_KLASSE_4 = f'{wd.ROHR_KLASSE_4} Der Widerstand steht darum auf null.'` – Warum ein Rundrohr der Klasse 4 nichts traegt.
- `SPANNUNG = Mathe('f_y\\ [\\mathrm{N}/\\mathrm{mm}^2]')`
- `WIDERSTANDSMOMENT = 'Widerstandsmoment bis zur weitesten Faser'` – Namen der Formeln, die Kennzahlen und Nachweise beide schreiben: eine Formel, ein Name in der Formelsammlung, gleich in welcher Klasse.
- `ELASTISCH = 'Biegewiderstand bis zum ersten Fliessen'`
- `NORMALKRAFT = 'Normalkraftwiderstand eines Stahlquerschnitts'`
- `PLASTISCH = 'Plastischer Biegewiderstand eines Stahlquerschnitts'`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.stahlbau.klasse]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlbau.widerstand]]
- [[opencivil.stahlprofile.bleche]]

## Gebraucht von

- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.nachweis.qa_stahl_stabilitaet]]

## Formeln aus diesem Modul

- [[Mitwirkende Breite eines Blechs]] · `breiten`
