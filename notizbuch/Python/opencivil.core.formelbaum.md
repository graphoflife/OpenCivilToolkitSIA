---
erzeugt: 756535111d9d
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/formelbaum.py
> die Vorlage einer Formel als Rechenbaum.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/formelbaum.py)

## VERANTWORTUNG

Liest die Vorlage einer Formelzeile -- LaTeX mit `@name`-Platzhaltern --
als Baum, setzt darin fuer einen Platzhalter eine andere Formel ein, kuerzt,
setzt den Baum wieder als LaTeX, mit Symbolen und mit Zahlen, und rechnet
ihn nach. Daraus baut die Kurzform eines Nachweises aus mehreren Zeilen eine
([[opencivil.core.kurzform]]):

```
x    = \frac{A_s \cdot f_yd}{0.85 \cdot b \cdot f_cd}
M_Rd = A_s \cdot f_yd \cdot (d - \frac{0.85 \cdot x}{2})
->     A_s \cdot f_yd \cdot (d - \frac{A_s \cdot f_yd}{2 \cdot b \cdot f_cd})
```

Gelesen wird die Teilmenge von LaTeX, in der die Formeln dieses Werkzeugs
stehen: `+ - \cdot \times /`, Nebeneinander als Produkt, `\frac`,
`\sqrt`, Klammern, Hochzahlen mit fester Zahl, `\pi`, `\min`,
`\max`, Betraege und die Winkelfunktionen. Was darueber hinausgeht -- eine
Zahl mit Einheit, `\text`, `\sum`, ein Winkel in Grad -- wirft
[[opencivil.core.formelbaum#Unlesbar|Unlesbar]], und die Formel bleibt, wie sie geschrieben ist. Die
Kurzform rechnet jede Umformung nach; ein falsch gelesener Baum gibt darum
nie eine falsche Formel, nur keine kuerzere.

Gekuerzt wird wenig, und nur, was dasteht: gleiche Faktoren in Zaehler und
Nenner, Faktoren eins, Summanden null. Zahlen werden nicht verrechnet -- die
0.85 des Spannungsblocks soll man wiedererkennen, solange sie dasteht.

## Inhalt

### Unlesbar

```python
class Unlesbar(Exception)
```

Die Vorlage geht ueber das hinaus, was der Baum lesen kann.

### Zahl

```python
@dataclass(frozen=True)
class Zahl
```

Eine Zahl, die in der Vorlage steht -- so geschrieben, wie sie dasteht.

- `wert: float`
- `text: str = field(default='', compare=False)`

### Blatt

```python
@dataclass(frozen=True)
class Blatt
```

Ein Platzhalter mit seinem Wert. `empirisch`: die Einheit, in der er
in eine empirische Formel als blanke Zahl eingeht -- in ein solches Blatt
wird nie eingesetzt, die Formel dahinter rechnet in SI.

- `kennung: str`
- `wert: Wert = field(compare=False)`
- `empirisch: Optional[Einheit] = None`

### Produkt

```python
@dataclass(frozen=True)
class Produkt
```

Faktoren mit ihrer Hochzahl -- ein Nenner hat eine negative.

- `faktoren: Tuple[Tuple['Ausdruck', Fraction], ...]`
- `vorzeichen: int = 1`

### Summe

```python
@dataclass(frozen=True)
class Summe
```

- `terme: Tuple['Ausdruck', ...]`

### Funktion

```python
@dataclass(frozen=True)
class Funktion
```

`min`, `max`, `abs` oder eine Winkelfunktion ([[opencivil.core.formelbaum#Konstanten|WINKEL]]).

- `name: str`
- `argumente: Tuple['Ausdruck', ...]`

### negiert

```python
def negiert(a: Ausdruck) -> Ausdruck
```

### _zerlegen

```python
def _zerlegen(vorlage: str) -> List[Teil]
```

Die Vorlage in `(art, text)`: platz, zahl, befehl oder zeichen.

### _Leser

```python
class _Leser
```

Rekursiver Abstieg: Summe, Produkt, Potenz, Einheit.

#### _Leser.schau

```python
def schau(self) -> Teil
```

#### _Leser.nimm

```python
def nimm(self) -> Teil
```

#### _Leser.erwarte

```python
def erwarte(self, art: str, text: str) -> None
```

#### _Leser.summe

```python
def summe(self) -> Ausdruck
```

#### _Leser.produkt

```python
def produkt(self) -> Ausdruck
```

#### _Leser.potenz

```python
def potenz(self) -> Ausdruck
```

#### _Leser.einheit

```python
def einheit(self) -> Ausdruck
```

#### _Leser.gruppe

```python
def gruppe(self) -> Ausdruck
```

Das Argument von `\frac` oder `\sqrt`: eine `{...}`-Gruppe.

#### _Leser.links

```python
def links(self) -> Ausdruck
```

`\left( ... \right)`, mit `[` ebenso; `|` ist ein Betrag.

#### _Leser.argumente

```python
def argumente(self) -> Tuple[Ausdruck, ...]
```

Die Argumente von `\min` und `\max`, durch `;` oder `,` getrennt.

### _bruch

```python
def _bruch(hoch: Ausdruck) -> Fraction
```

Eine Hochzahl als Bruch -- sie muss eine feste Zahl sein.

### lesen

```python
def lesen(zeile: Formelzeile) -> Ausdruck
```

Die Vorlage einer Formelzeile als gekuerzter Baum ([[opencivil.core.formelbaum#normal|normal]]).

### normal

```python
def normal(a: Ausdruck) -> Ausdruck
```

Flach und gekuerzt: ein Produkt im Produkt geht in diesem auf, eine
Summe in der Summe ebenso; gleiche Faktoren zaehlen ihre Hochzahlen
zusammen, und was danach eins ist (oder null in einer Summe), entfaellt.

### einsetzen

```python
def einsetzen(a: Ausdruck, kennung: str, teil: Ausdruck) -> Ausdruck
```

`a` mit `teil` an jedem nicht empirischen Blatt `kennung`, gekuerzt.

### blaetter

```python
def blaetter(a: Ausdruck) -> List[Blatt]
```

Die Blaetter in der Reihenfolge, in der sie dastehen -- jedes einmal.

### empirische

```python
def empirische(a: Ausdruck) -> List[Tuple[str, Einheit]]
```

`(Symbol, Einheit)` je empirischem Blatt -- fuer den Einheitenhinweis.

### rechnen

```python
def rechnen(a: Ausdruck) -> float
```

Der Wert des Baums in SI; ein empirisches Blatt in seiner Einheit. Eine
negative Zahl unter einer Wurzel gibt `nan` -- dann stimmt nichts mehr.

### symbolisch

```python
def symbolisch(a: Ausdruck) -> str
```

### numerisch

```python
def numerisch(a: Ausdruck) -> str
```

### _produkt_setzen

```python
def _produkt_setzen(a: Produkt, blatt: Blattsatz, vorn: bool) -> str
```

Zahlen zuerst, ein Nenner als Bruch, ein Minus vorne.

### _faktor

```python
def _faktor(f: Ausdruck, hoch: Fraction, blatt: Blattsatz, *, vorn: bool, allein: bool) -> str
```

Ein Faktor mit seiner (positiven) Hochzahl; `allein` im Zaehler oder Nenner.


## Konstanten

- `WINKEL = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'cot': lambda x: …` – Die Winkelfunktionen, wie LaTeX sie schreibt -- mit ihrer Rechnung.
- `_FUNKTIONEN = {'min': min, 'max': max, 'abs': abs, **WINKEL}`
- `EINS = Zahl(1.0, '1')`
- `_ABSTAENDE = {',', ';', ':', '!', ' ', 'quad', 'qquad'}` – Zwischenraeume -- sie tragen nichts zur Rechnung bei.
- `_BEFEHL = re.compile('\\\\([A-Za-z]+|.)')`
- `_ZAHL = re.compile('\\d+(?:\\.\\d+)?')`
- `_ZEICHEN = set('{}()[]|+-^;,/')`
- `_FAKTORBEFEHLE = {'frac', 'tfrac', 'dfrac', 'sqrt', 'left', 'pi', 'min', 'max', *WINKE…` – Was ein Faktor sein kann, der ohne Rechenzeichen folgt: `2 \\cos x`.
- `_ZU = {'(': ')', '[': ']', '|': '|'}`
- `Blattsatz = Callable[[Blatt, bool, bool], str]` – Wie ein Blatt dasteht: `(blatt, vorn, hoch) -> LaTeX` -- `vorn`, wenn kein Rechenzeichen davorsteht, `hoch`, wenn ein Exponent folgt.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.core.kurzform]]
