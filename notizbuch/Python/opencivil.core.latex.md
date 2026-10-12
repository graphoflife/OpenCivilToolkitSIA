---
erzeugt: f2ee12724457
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/latex.py
> Bausteine fuer die LaTeX-Ausgabe von Berechnungen.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/latex.py)

## VERANTWORTUNG

Nimmt einer Berechnung die *mechanische* Haelfte der LaTeX-Arbeit ab. Von Hand
geschrieben wird nur die **analytische** Form einer Formel; die Fassung "mit
Zahlen und Einheiten" wird daraus automatisch erzeugt, indem die Platzhalter
durch die tatsaechlichen Werte ersetzt werden.

Damit verschwindet die schlimmste Doppelspurigkeit des alten Codes, in dem
jede Formel zweimal getippt wurde -- einmal symbolisch, einmal numerisch --
und beide Fassungen unbemerkt auseinanderlaufen konnten.


## PLATZHALTER

In der Vorlage steht `@name` fuer eine Eingabe. Wo der Name an ein Zeichen
grenzt, das noch zum Namen gehoeren koennte, schreibt man `@{name}`:

```
r"\frac{@eta_fc \cdot @f_ck}{@gamma_c}"

symbolisch -> \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c}
numerisch  -> \frac{0.933 \cdot 30\,\mathrm{N/mm^2}}{1.5}
```


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.core.latex import Formelzeile
zeile = Formelzeile.bauen(ergebnis, r"@a \cdot @b", {"a": wert_a, "b": wert_b})
print(zeile.einzeilig())
```

## Inhalt

### LatexFehler

```python
class LatexFehler(Exception)
```

Fehler beim Aufbau einer LaTeX-Ausgabe.

### text_latex

```python
def text_latex(text: str) -> str
```

Maskiert Sonderzeichen fuer den Fliesstext.

Umlaute bleiben unangetastet -- die Praeambel des Berichts stellt UTF-8
ein, damit 'Ueberdeckung' auch als 'Überdeckung' gesetzt werden kann.

### als_text

```python
def als_text(text: str) -> str
```

Verpackt deutschen Klartext fuer die Mathematikumgebung.

**Immer hierdurch**, nie `\text{...}` von Hand um eine Zeichenkette
legen, die nicht buchstabiert im Quelltext steht. Namen kommen aus dem
Projekt oder aus einer Berechnung und enthalten Zeichen wie `_`, die auch
im Textmodus Befehle sind: `M_Rd(N=0)` bringt KaTeX zum Abbruch, und
dann steht im Bericht der rohe Quelltext statt der Beschriftung.

### ohne_namen_im_index

```python
def ohne_namen_im_index(symbol: str) -> str
```

Das Symbol ohne Sorte und Fall im Index: `f_{cd,   ext{C30/37}}` ->
`f_{cd}`. Das Gegenstueck zu [[opencivil.material.basis#mit_index|opencivil.material.basis.mit_index]]
und zu den Fallnamen, die ein Nachweis an seine Symbole haengt.

### platzhalter_namen

```python
def platzhalter_namen(vorlage: str) -> list[str]
```

Liefert alle in einer Vorlage vorkommenden Platzhalternamen.

### _ersetzen

```python
def _ersetzen(vorlage: str, ersatz) -> str
```

Ersetzt alle Platzhalter mittels `(name, hoch, nach_rechenzeichen) -> str`.

`hoch` sagt, ob hinter dem Platzhalter ein Exponent steht: `@h^{2}`
braucht mit Zahl und Einheit eine Klammer, `(300 mm)^2` und nicht
`300 mm^2`. `nach_rechenzeichen`, ob davor ein Rechenzeichen steht --
dann braucht eine negative Zahl eine.

### einsetzen_symbolisch

```python
def einsetzen_symbolisch(vorlage: str, eingaben: Mapping[str, Wert], kontext: str='Formel') -> str
```

Ersetzt die Platzhalter durch die Symbole der Eingaben.

### _blank

```python
def _blank(wert: Wert, einheit: Einheit) -> str
```

Die Zahl eines Werts in einer anderen Einheit, ohne diese dazuzuschreiben.

Die Stellen wandern mit: 248.1 mm auf eine Stelle sind in Metern 0.2481,
nicht 0.2 -- sonst ginge in der Herleitung Genauigkeit verloren, die die
Rechnung hatte.

### einsetzen_numerisch

```python
def einsetzen_numerisch(vorlage: str, eingaben: Mapping[str, Wert], kontext: str='Formel', *, empirisch: Optional[Mapping[str, Einheit]]=None) -> str
```

Ersetzt die Platzhalter durch Zahlenwerte samt Einheit.

Negative Werte werden hinter einem Rechenzeichen geklammert, damit nicht
`a \cdot -5` entsteht; am Anfang eines Ausdrucks waere die Klammer
reine Unruhe.

`empirisch` nennt die Eingaben einer dimensionell inhomogenen
Normformel mit der Einheit, in der die Norm sie verlangt. Sie stehen als
blanke Zahl in dieser Einheit da: `\sqrt{30}` und nicht
`\sqrt{30\,\mathrm{N}/\mathrm{mm}^{2}}` -- die Wurzel einer
Spannung gibt es nicht, und so zu tun waere falsch.

### _gruppe

```python
def _gruppe(s: str, i: int) -> tuple[str, int]
```

Das Argument ab `i`: eine `{...}`-Gruppe oder ein einzelnes Zeichen.

### sichtbare_breite

```python
def sichtbare_breite(latex: str) -> float
```

Ungefaehr, wie breit eine Formel gesetzt wird -- in Zeichen.

Gezaehlt wird, was man sieht: ein Bruch so breit wie sein breiterer Teil,
Hoch- und Tiefgestelltes kleiner, `\alpha` oder `\cdot` als ein
Zeichen, Formatierung (`\left`, `\,`, `\mathrm`, die Klammern
einer Gruppe) fast nichts. Eine Umgebung mit Zeilen ist so breit wie ihre
breiteste Zeile.

### Formelzeile

```python
@dataclass(frozen=True)
class Formelzeile
```

Die vier Bestandteile einer ausgeschriebenen Formel.

Wird strukturiert gehalten statt als fertiger String, damit der Bericht
selbst entscheiden kann, ob er ein- oder mehrzeilig setzt. Das alte
Vorgehen -- den fertigen String an `" = "` wieder auseinanderzuschneiden --
ging kaputt, sobald in einer Formel ein Gleichheitszeichen vorkam.

- `symbol: str` – Linke Seite, z.B. `f_{cd}`.
- `analytisch: Optional[str]` – Von Hand geschriebene Formel mit Symbolen. None bei reinen Eingaben.
- `numerisch: Optional[str]` – Dieselbe Formel mit eingesetzten Zahlen und Einheiten.
- `ergebnis: str` – Resultat mit Einheit, z.B. `18.7\,\mathrm{MPa}`.
- `nachsatz: str = ''` – Was hinter dem Resultat steht: ein Vergleich mit Urteil, ein Hinweis.
- `vorlage: Optional[str] = None` – Die Vorlage mit `@name` -- dieselbe Formel, gleich welche Zahlen.
- `einheiten: str = ''` – Bei empirischen Formeln: in welchen Einheiten die Zahlen eingehen.
- `eingaben: Tuple[Tuple[str, Wert], ...] = field(default=(), compare=False, repr=False)` – Was die Vorlage einsetzt, je `(Platzhalter, Wert)` -- nur ihre Platzhalter, nicht jede Eingabe der Berechnung. Fuer das Notizbuch: welche Groessen eine Formel braucht, und welche Formel sie liefert.

#### Formelzeile.bauen

```python
@classmethod
def bauen(cls, ergebnis: Wert, vorlage: Optional[str]=None, eingaben: Optional[Mapping[str, Wert]]=None, *, empirisch: Optional[Mapping[str, Einheit]]=None, nachsatz: str='') -> 'Formelzeile'
```

Baut die Zeile aus Resultat, analytischer Vorlage und Eingaben.

Ohne Vorlage entsteht die schlichte Form `symbol = wert` -- passend
fuer Eingaben und Vorgabewerte. Zu `empirisch` siehe
[[opencivil.core.latex#einsetzen_numerisch|einsetzen_numerisch]]; welche Einheiten dort vorausgesetzt sind,
steht am Ende der Zeile, sonst liessen sich die blanken Zahlen nicht
lesen.

#### Formelzeile._teile

```python
def _teile(self) -> list[str]
```

Die darzustellenden Abschnitte, ohne sinnlose Wiederholungen.

#### Formelzeile._schluss

```python
def _schluss(self) -> str
```

Was hinter dem Resultat steht: Nachsatz, dann der Einheitenhinweis.

#### Formelzeile.einzeilig

```python
def einzeilig(self) -> str
```

`f_{cd} = \frac{...} = \frac{...} = 18.7\,\mathrm{MPa}`

#### Formelzeile.mehrzeilig

```python
def mehrzeilig(self) -> str
```

Dieselbe Zeile als `aligned`-Umgebung, fuer lange Formeln.

#### Formelzeile.darstellen

```python
def darstellen(self) -> str
```

Eine Zeile, solange sie gesetzt hineinpasst, sonst untereinander.

Gemessen wird, was man sieht ([[opencivil.core.latex#sichtbare_breite|sichtbare_breite]]), nicht der
Quelltext. Mit dessen Laenge standen kurze Formeln auf drei Zeilen,
weil `\left`, `\,\mathrm{mm}` und die Klammern der Gruppen
mitzaehlten.

### fest

```python
def fest(zahl: float, stellen: int) -> str
```

Eine Zahl mit fester Stellenzahl, fuer Tabellenspalten -- ohne «-0.0».

Was auf null rundet, hat kein Vorzeichen; ein Minus vor einer Null sieht
nach etwas aus, das es nicht gibt.

### urteil

```python
def urteil(erfuellt: bool) -> str
```

Das Urteil hinter einem Nachweis -- ein Wortlaut fuer alle.

### angabe

```python
def angabe(wert: Wert) -> str
```

`Symbol = Zahl Einheit` -- ein Wert, wie er in einem Vergleich steht.

### folgerung

```python
def folgerung(erfuellt: bool) -> str
```

`⇒ erfüllt` am Ende einer Zeile -- ein Wortlaut fuer alle.

### vergleich

```python
def vergleich(soll: str, rechts: str, erfuellt: bool, *, mit_urteil: bool=True) -> str
```

Der Nachsatz einer Formel, deren Resultat gegen etwas gehalten wird:

```
\quad \ge \quad N_{Riss} = 378.3\,\mathrm{kN}
\quad \Rightarrow \quad \text{NICHT erfüllt}
```

`soll` ist das Zeichen, das gelten muss; geht der Vergleich nicht auf,
steht sein Gegenteil da -- im Beispiel `<`.

### bedingung

```python
def bedingung(links: str, soll: str, rechts: str, erfuellt: bool, *, mit_urteil: bool=True) -> str
```

Ein Vergleich mit sichtbarem Ergebnis, z.B. fuer Nachweise:

```
M_{Ed} = 120\,\mathrm{kNm} \quad \le \quad M_{Rd} = 145\,\mathrm{kNm}
\quad \Rightarrow \quad \text{erfüllt}
```

### Mathe

```python
@dataclass(frozen=True)
class Mathe
```

Eine Tabellenzelle, die Mathematik ist -- Symbol, Einheit, Formel.

Nicht `Formel`: so heisst schon die deklarative Berechnung in
[[opencivil.core.berechnung]], und die beiden sind verschiedene Dinge.

Eine Zahl ist ebenfalls Mathe: ihr Minus ist ein Minuszeichen und kein
Bindestrich, und sie steht in derselben Schrift wie in den Gleichungen.

Jede andere Zelle ist Text: ein `str`. Vorher war jede Zelle LaTeX,
und reiner Text stand als `\text{...}` darin. Die Konsole druckte das
so ab, der Word-Knopf lieferte eine Formelmatrix statt einer Tabelle, und
die Oberflaeche las den Text per regulaerem Ausdruck wieder heraus.
Welche Art eine Zelle hat, weiss nur, wer sie schreibt -- also sagt sie
es.

- `latex: str`

### zelle_latex

```python
def zelle_latex(zelle: Zelle) -> str
```

Eine Zelle fuer ein LaTeX-Dokument: Text maskiert, Formel in `$...$`.

### tabelle

```python
def tabelle(kopf: Sequence[Zelle], zeilen: Iterable[Sequence[Zelle]], ausrichtung: Optional[str]=None, *, lang: bool=False) -> str
```

Eine Tabelle fuer ein LaTeX-Dokument.

`ausrichtung` je Spalte `l`, `c` oder `r` wie in LaTeX, dazu
`L`: links, und die Spalte darf umbrechen. Das braucht eine Textspalte,
die sonst die Tabelle ueber den Rand schoebe -- welche das ist, weiss nur,
wer die Tabelle schreibt.

Ohne `lang` ein `tabular` mit `\hline`, fuer die Kopierknoepfe:
es laeuft in jedem Dokument, ohne dass dort erst ein Paket geladen werden
muss, und `L` gilt darin als `l`. Kein `array` mehr: das ist eine
Formel und keine Tabelle, und Word und Markdown koennen damit nichts
anfangen.

Mit `lang` fuer den Bericht: die Tabelle darf ueber Seiten laufen und
wiederholt dort ihren Kopf (`longtable`). Hat sie eine `L`-Spalte,
nimmt sie die Zeilenbreite ein, und nur diese Spalten brechen um
(`xltabular`).

### fallunterscheidung

```python
def fallunterscheidung(faelle: Sequence[tuple[str, str]], gewaehlt: int=-1) -> str
```

Setzt eine `cases`-Umgebung und hebt den zutreffenden Fall hervor.

Genau dafuer gedacht, dass eine Formel je nach Eingaben anders lautet: der
Leser sieht alle Zweige und erkennt, welcher gegriffen hat.

:param faelle: Paare aus (Ausdruck, Bedingung).
:param gewaehlt: Index des zutreffenden Falls, oder -1 fuer keine Hervorhebung.


## Konstanten

- `_PLATZHALTER = re.compile('@\\{([A-Za-z_][A-Za-z0-9_]*)\\}|@([A-Za-z_][A-Za-z0-9_]*)…` – `@name` oder `@{name}`
- `_SONDERZEICHEN = {'\\': '\\textbackslash{}', '&': '\\&', '%': '\\%', '$': '\\$', '#': …`
- `_NAME_IM_INDEX = re.compile(',\\\\text\\{[^{}]*\\}')` – Ein Name im Index: `\alpha_{eff,x,\text{Feld}}`, `f_{cd,\text{C30/37}}`.
- `_RECHENZEICHEN = ('+', '-', '\\cdot', '\\times', '/')` – Nach diesen Zeichen braucht eine negative Zahl eine Klammer: `a - (-5)`, `a \\cdot (-5)`. Am Anfang eines Ausdrucks nicht: `-300 - (-1484.6)`.
- `ZEILENBREITE = 60.0` – Wie breit eine Formel gesetzt hoechstens sein darf, damit sie auf einer Zeile steht -- in Zeichen, wie [[opencivil.core.latex#sichtbare_breite|sichtbare_breite]] sie zaehlt. Etwa das, was auf einer A4-Seite und in der rechten Tafel noch Platz hat.
- `_OHNE_BREITE = {'left', 'right', 'mathrm', 'text', 'operatorname', 'mathbf', 'mathit…` – Befehle ohne eigene Breite: Formatierung, oder ihr Argument steht fuer sie.
- `_WOERTER = {'min', 'max', 'sin', 'cos', 'tan', 'cot', 'log', 'ln', 'exp', 'lim',…` – Operatoren, die mit ihren Buchstaben dastehen.
- `_RAEUME = {',': 0.2, ':': 0.25, ';': 0.3, '!': 0.0, ' ': 0.3, 'quad': 1.0, 'qqu…` – Zwischenraeume, in Zeichen.
- `_RELATIONEN = {'le', 'ge', 'leq', 'geq', 'approx', 'neq', 'equiv', 'Rightarrow', 'L…` – Relationen und Pfeile stehen mit Luft auf beiden Seiten, Rechenzeichen mit etwas weniger.
- `_BINAER = {'cdot', 'times', 'pm', 'mp'}`
- `_BEFEHL = re.compile('\\\\([A-Za-z]+|.)')`
- `_GEGENTEIL = {'\\le': '>', '\\ge': '<', '<': '\\ge', '>': '\\le'}` – Was statt des Sollzeichens dasteht, wenn der Vergleich nicht aufgeht.
- `Zelle = Union[str, Mathe]` – Eine Tabellenzelle: Text oder [[opencivil.core.latex#Mathe|Mathe]].
- `UMBRUCHSPALTE = '>{\\raggedright\\arraybackslash}X'` – Eine Spalte, die links steht und umbrechen darf -- `L` in der Ausrichtung.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.bericht.formelsammlung]]
- [[opencivil.bericht.gliederung]]
- [[opencivil.bericht.konsole]]
- [[opencivil.bericht.latex_dokument]]
- [[opencivil.bericht.markdown]]
- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.core.berechnung]]
- [[opencivil.core.protokoll]]
- [[opencivil.gleichungen.ausdruck]]
- [[opencivil.gleichungen.blatt]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.web.api]]
