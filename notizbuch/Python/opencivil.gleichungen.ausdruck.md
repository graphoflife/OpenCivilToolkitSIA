---
erzeugt: 453ccd8a9f64
art: modul
tags: [modul]
---
> [!abstract] opencivil/gleichungen/ausdruck.py
> eine Zeile LaTeX: zerlegen, rechnen, setzen.
> Paket [[opencivil.gleichungen]] · [Quelltext](../../opencivil/gleichungen/ausdruck.py)

## VERANTWORTUNG

Liest die LaTeX-Teilmenge, die der Formeleditor (MathLive) schreibt, baut
daraus einen Syntaxbaum, rechnet ihn mit Einheiten aus und setzt ihn wieder als
Vorlage mit `@name` -- dieselbe Form, die jede Herleitung benutzt
([[opencivil.core.protokoll#Protokoll.formel|Protokoll.formel]]). Eine selbst geschriebene Gleichung steht so genau
da wie eine des Werkzeugs: Symbol, Formel, Zahlen, Ergebnis.


## KEIN EVAL, KEIN ROHES LATEX

Gerechnet wird ueber den Baum, nie ueber `eval`. Angezeigt wird nie, was
der Benutzer geschrieben hat, sondern was der Baum daraus macht: ein fremdes
`\href` kaeme so nie durch -- der Baum kennt diesen Befehl nicht und lehnt
die Zeile ab. (KaTeX laeuft zudem ohne `trust`.)


## WAS VERSTANDEN WIRD

Zahlen (`3.5`, `3{,}5`), Variablen mit Index (`f_{cd}`, `\sigma_s`),
`+ - \cdot \times /`, implizites Mal (`2a`), `\frac`, `^`,
`\sqrt`, `\sqrt[n]`, Klammern, Betrag, Winkelfunktionen, ``\\ln \\log
\\exp \\min \\max`, `\\pi`, Einheiten als `\\mathrm{kN}``, Grad als
`^{\circ}`. Nebeneinanderstehende Buchstaben sind ein Produkt (`ab` ist
`a \cdot b`) -- ein Name mit mehreren Zeichen braucht einen Index.

## Inhalt

### AusdruckFehler

```python
class AusdruckFehler(Exception)
```

Was an einer Zeile nicht stimmt -- als Satz fuer den Benutzer.

### _si_einheit

```python
def _si_einheit(dimension: Dimension) -> Einheit
```

Eine Einheit aus kg, m, s -- wo es keine gebraeuchliche gibt.

### anzeigeeinheit

```python
def anzeigeeinheit(groesse: Groesse, gewuenscht: Optional[Einheit]=None) -> Einheit
```

Die Einheit, in der ein Ergebnis dasteht.

### einheit_aus_text

```python
def einheit_aus_text(text: str) -> Optional[Einheit]
```

Die gewuenschte Ergebniseinheit einer Zeile: `kN/m^2`, `N/mm2`, `mm`.

Leer heisst: keine Vorgabe. Eine unbekannte Einheit ist ein Fehler der
Zeile, kein stilles Ignorieren.

### Token

```python
@dataclass(frozen=True)
class Token
```

- `art: str` – `zahl`, `buchstabe`, `befehl`, `zeichen` oder `ende`.
- `text: str`
- `stelle: int`

### zerlegen

```python
def zerlegen(latex: str) -> List[Token]
```

Die Zeile als Folge von Zeichen, Zahlen und Befehlen.

### Zahl

```python
@dataclass(frozen=True)
class Zahl
```

- `wert: float`
- `text: str`

### Masseinheit

```python
@dataclass(frozen=True)
class Masseinheit
```

- `einheit: Einheit`

### Name

```python
@dataclass(frozen=True)
class Name
```

Eine Variable. `latex` ist ihre gereinigte Schreibweise und ihr Schluessel.

- `latex: str`

### Operation

```python
@dataclass(frozen=True)
class Operation
```

- `zeichen: str` – `+`, `-`, `*` oder `/`.
- `links: 'Knoten'`
- `rechts: 'Knoten'`

### Potenz

```python
@dataclass(frozen=True)
class Potenz
```

- `basis: 'Knoten'`
- `exponent: 'Knoten'`

### Gegenzahl

```python
@dataclass(frozen=True)
class Gegenzahl
```

- `inhalt: 'Knoten'`

### Funktion

```python
@dataclass(frozen=True)
class Funktion
```

- `name: str`
- `argumente: Tuple['Knoten', ...]`

### Wurzel

```python
@dataclass(frozen=True)
class Wurzel
```

- `inhalt: 'Knoten'`
- `grad: Optional['Knoten'] = None`

### Betrag

```python
@dataclass(frozen=True)
class Betrag
```

- `inhalt: 'Knoten'`

### Konstante

```python
@dataclass(frozen=True)
class Konstante
```

- `latex: str`
- `wert: float`

### _Leser

```python
class _Leser
```

Rekursiver Abstieg ueber die Tokens einer Zeile.

#### _Leser.jetzt

```python
@property
def jetzt(self) -> Token
```

#### _Leser.nehmen

```python
def nehmen(self) -> Token
```

#### _Leser.ist

```python
def ist(self, *texte: str) -> bool
```

#### _Leser.erwarten

```python
def erwarten(self, text: str) -> None
```

#### _Leser._oeffnen

```python
def _oeffnen(self) -> Optional[str]
```

Eine oeffnende Klammer, auch `\left(` -- gibt die schliessende zurueck.

#### _Leser.ausdruck

```python
def ausdruck(self) -> Knoten
```

Summe: `summand (± summand)*`.

#### _Leser.summand

```python
def summand(self) -> Knoten
```

Produkt: `faktor ((· | / | nichts) faktor)*`.

#### _Leser.faktor

```python
def faktor(self) -> Knoten
```

#### _Leser.potenz

```python
def potenz(self) -> Knoten
```

#### _Leser._grad

```python
def _grad(self) -> bool
```

`^{\circ}` oder `^\circ` -- das Gradzeichen, kein Exponent.

#### _Leser.hochzahl

```python
def hochzahl(self) -> Knoten
```

Nach `^`: eine Gruppe `{...}` oder ein einzelnes Zeichen.

#### _Leser.gruppe

```python
def gruppe(self) -> Knoten
```

#### _Leser.primaer

```python
def primaer(self) -> Knoten
```

#### _Leser.name

```python
def name(self) -> Name
```

Buchstabe oder griechisches Zeichen, dahinter ein Index.

#### _Leser.index

```python
def index(self) -> str
```

Der Index eines Namens -- gereinigt, nur Buchstaben, Ziffern, Komma.

#### _Leser.masseinheit

```python
def masseinheit(self) -> Masseinheit
```

#### _Leser.funktion

```python
def funktion(self) -> Funktion
```

### Zeile

```python
@dataclass(frozen=True)
class Zeile
```

Eine gelesene Zeile: was definiert wird (oder nichts) und womit.

- `name: Optional[Name]` – Links vom Gleichheitszeichen -- `None` bei einer blossen Auswertung.
- `ausdruck: Knoten`

### lesen

```python
def lesen(latex: str) -> Zeile
```

`b = 2a + 1\,\mathrm{m}` definiert `b`; `a \cdot b =` oder
`a \cdot b` rechnet nur aus. Eine Neudefinition gilt ab ihrer Zeile.

### rechnen

```python
def rechnen(knoten: Knoten, werte: Mapping[str, Groesse]) -> Groesse
```

Den Baum ausrechnen -- `werte` nach Schreibweise der Namen.

### _ist_angabe

```python
def _ist_angabe(knoten: Knoten) -> bool
```

Eine Zahl mit Einheit -- `5\,\mathrm{kN}`, auch mit `/\mathrm{m}^{2}`.

### _ist_einheit

```python
def _ist_einheit(knoten: Knoten) -> bool
```

Ob der Teilbaum nur aus Einheiten besteht -- `\mathrm{kN}/\mathrm{m}^{2}`.

### setzen

```python
def setzen(knoten: Knoten, ph: Mapping[str, str]) -> str
```

Der Baum als Vorlage fuer [[opencivil.core.latex#Formelzeile.bauen|Formelzeile.bauen]] -- Namen als
`@platzhalter` (`ph`: Platzhalter je Name), alles andere aus dem Baum
neu geschrieben.

### namen

```python
def namen(knoten: Knoten) -> List[str]
```

Die Namen im Baum, in der Folge ihres ersten Auftretens.

### blattname

```python
@lru_cache(maxsize=None)
def blattname(symbol: str) -> str
```

Unter welchem Namen ein Projektwert im Blatt steht: `f_{cd}` fuer
`f_{cd,\text{C30/37}}`. Leer, wo das Symbol kein Name ist, den dieser
Leser versteht -- `\varnothing_{1,y,g}` etwa. Dieselbe Regel wie beim
Lesen einer Zeile, also nie ein Vorschlag, den das Blatt dann ablehnt.

Zwischengespeichert: die Symbole sind von Lauf zu Lauf dieselben.

### stellen

```python
def stellen(groesse: Groesse, einheit: Einheit, signifikant: int=4) -> int
```

Nachkommastellen fuer `signifikant` geltende Ziffern -- hoechstens 10.


## Konstanten

- `EINHEITENNAMEN = {name: e for name, e in EINHEITEN.items() if name.isalpha() and name …` – Was in `\mathrm{...}` stehen darf. Nur einfache Namen -- zusammengesetzte Einheiten entstehen im Ausdruck selbst: `\mathrm{kN}/\mathrm{m}^{2}`.
- `_VORZUG = {DIMENSIONSLOS: EINHEITSLOS, LAENGE: (1.0, MM, M), FLAECHE: (0.01, MM…` – Womit ein Ergebnis angezeigt wird, wenn die Zeile keine Einheit verlangt. Je Dimension eine Einheit oder eine Staffel `(Grenze in SI, klein, gross)`: 0.265 m liest sich als 265 mm, 5 kN/m² nicht als 0.005 N/mm².
- `_LEER = {'\\,', '\\;', '\\:', '\\!', '\\ ', '\\quad', '\\qquad', '\\enspace',…` – Abstaende -- sie tragen nichts zur Rechnung bei.
- `_GRIECHISCH = {f'\\{n}' for n in 'alpha beta gamma delta epsilon varepsilon zeta et…`
- `_FUNKTIONEN = {'\\sin', '\\cos', '\\tan', '\\cot', '\\arcsin', '\\arccos', '\\arcta…`
- `_MAL = {'\\cdot', '\\times', '*'}`
- `_ZUWEISUNG = {'\\coloneq', '\\coloneqq', '\\colonequals'}`
- `_ZAHL = re.compile('\\d+(?:(?:\\.|\\{,\\})\\d+)?|\\.\\d+')`
- `_WINKEL = {'\\sin': math.sin, '\\cos': math.cos, '\\tan': math.tan, '\\cot': la…`
- `_ARKUS = {'\\arcsin': math.asin, '\\arccos': math.acos, '\\arctan': math.atan}`

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]

## Gebraucht von

- [[opencivil.gleichungen.blatt]]
- [[opencivil.web.api]]
