---
erzeugt: f91cab4973ad
art: modul
tags: [modul]
---
> [!abstract] opencivil/notizbuch/bibliothek.py
> die Python-Bibliothek als Seiten.
> Paket [[opencivil.notizbuch]] · [Quelltext](../../opencivil/notizbuch/bibliothek.py)

## VERANTWORTUNG

Je Modul und je Paket eine Seite im Notizbuch, aus den Docstrings: was das
Modul verantwortet, seine Klassen und Funktionen samt Signatur, seine
Konstanten, was es braucht und wer es braucht, und welche Formeln es
schreibt. Gelesen wird mit `ast` -- nichts wird dafuer importiert. Was ueber
ein Modul zu sagen ist, steht in seinem Docstring; die Seite ist ganz
erzeugt, ohne eigenen Teil.


## AUS DEM DOCSTRING WIRD MARKDOWN

* Die Kopfzeile `opencivil/<pfad>.py -- Kurzbeschreibung.` wird zur
  Kurzbeschreibung oben auf der Seite.
* Eine Zeile in GROSSBUCHSTABEN wird zur Ueberschrift -- im Docstring eines
  Moduls oder Pakets; in dem einer Klasse oder Funktion bleibt sie fett. Eine
  Klammer gehoert dazu (`VORZEICHEN (wie in …):`), ein Schwanz nach
  ` -- ` in Kleinbuchstaben beginnt den Absatz darunter.
* Eingerueckt wird Code: nach `::`, direkt unter einer Ueberschrift und nach
  einer Leerzeile. Eingerueckte Zeilen direkt nach einer Textzeile setzen
  deren Absatz fort.
* `x` wird `x`; eine Rolle wie `` :class:`~opencivil.x.Y ``` wird ein Link
  auf die Seite des Moduls und die Ueberschrift dort. Was sich nicht
  aufloesen laesst, bleibt Code -- ein Test haelt die Liste leer.
* Was Markdown, Obsidian oder MathJax anders lesen wuerden -- `$`, `<`,
  `|`, `%%`, `==`, `[[` --, wird maskiert.


## WIE EIN NAME AUFGELOEST WIRD

In dieser Folge: ein ganzes Modul; das laengste Modul am Anfang des Namens;
eine Klasse oder Funktion im eigenen Modul; was das Modul importiert; ein
Modul mit diesem Ende (`latex.Mathe`); ein Name, den es im ganzen Paket
nur einmal gibt.

## Inhalt

### Eintrag

```python
@dataclass
class Eintrag
```

Eine Klasse, Funktion oder Methode -- eine Ueberschrift auf der Seite.

- `anker: str`
- `knoten: ast.AST`
- `stufe: int`

### Modul

```python
@dataclass
class Modul
```

- `name: str`
- `pfad: Path`
- `baum: ast.Module`
- `zeilen: List[str]`
- `paket: bool`
- `importe: Dict[str, str] = field(default_factory=dict)` – Lokaler Name -> voller Name, wie das Modul ihn importiert.
- `braucht: Set[str] = field(default_factory=set)`
- `eintraege: List[Eintrag] = field(default_factory=list)`

#### Modul.doc

```python
@property
def doc(self) -> str
```

#### Modul.kurz

```python
@property
def kurz(self) -> str
```

#### Modul.anker

```python
@property
def anker(self) -> Set[str]
```

### Bibliothek

```python
class Bibliothek
```

Alle Module des Pakets, gelesen und verknuepft.

#### Bibliothek.lesen

```python
@classmethod
def lesen(cls, paket: Path=PAKET) -> 'Bibliothek'
```

#### Bibliothek.ziel

```python
def ziel(self, text: str, modul: Modul, klasse: Optional[str]=None, tiefe: int=0) -> Optional[Tuple[str, str]]
```

`(Modul, Anker)` zu einem Namen, wie ihn ein Docstring nennt -- Anker
leer: die Seite. `klasse` ist die Klasse, in deren Docstring er steht.

#### Bibliothek._im_modul

```python
def _im_modul(self, modul: Modul, rest: str) -> Optional[str]
```

Die Ueberschrift zu einem Namen in diesem Modul: genau so, oder die
Klasse davor, oder die einzige Methode dieses Namens -- eine Konstante
steht unter «Konstanten».

#### Bibliothek._in_modul

```python
def _in_modul(self, modul: Modul, rest: str, tiefe: int) -> Tuple[str, str]
```

In einem bestimmten Modul: die Ueberschrift, sonst was es weiterreicht, sonst die Seite.

#### Bibliothek.verweis

```python
def verweis(self, text: str, modul: Modul, klasse: Optional[str]=None) -> str
```

Der Link fuer eine Rolle -- oder Code, wenn sich nichts findet. Mit `~` zeigt er nur den letzten Teil.

#### Bibliothek.codestelle

```python
def codestelle(self, stelle: str) -> str
```

Ein Link zu `modul:Klasse.methode` -- so weit die Seite sie kennt.

#### Bibliothek.seiten

```python
def seiten(self, formeln: Dict[str, List[Tuple[str, str]]]) -> List[Seite]
```

Die Uebersicht, je Paket und je Modul eine Seite. `formeln` nennt je
Modul die Formeln, die es schreibt: `(Formelname, Funktion)`.

#### Bibliothek._felder

```python
def _felder(self, klasse: ast.ClassDef, modul: Modul) -> Iterable[str]
```

Die Felder einer Klasse mit ihrem Docstring oder `#:`-Kommentar.

#### Bibliothek._inline

```python
def _inline(self, text: str, modul: Modul, *, roh: bool=False, klasse: Optional[str]=None) -> str
```

Eine Zeile Docstring als Markdown: Code, Rollen als Links, der Rest maskiert.

### _eintraege

```python
def _eintraege(baum: ast.Module) -> Iterable[Eintrag]
```

Klassen, Funktionen und ihre Methoden -- oeffentlich, oder privat mit Docstring.

### _kommentar

```python
def _kommentar(modul: Modul, knoten: ast.AST) -> str
```

Die `#:`-Zeilen direkt ueber einer Zuweisung, zu einem Satz verbunden.

### _hat_konstante

```python
def _hat_konstante(modul: Modul, name: str) -> bool
```

Ob `name` unter «Konstanten» steht -- dieselbe Auswahl wie dort.

### _ueberschrift

```python
def _ueberschrift(m: re.Match) -> Tuple[str, str, bool]
```

Titel, der Rest als Beginn des Absatzes, und ob ein Codeblock folgt.

### _block

```python
def _block(zeilen: List[str], i: int) -> Tuple[List[str], int]
```

Ein eingerueckter Block ab `i`, gemeinsam ausgerueckt -- Leerzeilen darin bleiben.

### _ist_fortsetzung

```python
def _ist_fortsetzung(heraus: List[str]) -> bool
```

Ob die letzte Zeile ein Listenpunkt ist -- dann gehoert Eingeruecktes zu ihm.

### _maskieren

```python
def _maskieren(text: str, *, am_anfang: bool) -> str
```

Was Markdown, Obsidian oder MathJax anders lesen wuerden.

### _text

```python
def _text(text: str) -> str
```

Eine Kurzbeschreibung in einer Liste: ohne Rollen, maskiert.


## Konstanten

- `ORDNER = 'Python'`
- `PAKET = Path(__file__).resolve().parents[1]`
- `WURZEL = PAKET.parent`
- `WERTLAENGE = 70` – Wie weit der Wert einer Konstanten gezeigt wird.
- `_UEBERSCHRIFT = re.compile('^(?P<titel>[A-ZÄÖÜ][A-ZÄÖÜ0-9]*(?![a-zäöüß])(?:[ ,/-]+[A-…` – Eine Ueberschrift im Docstring: Woerter in Grossbuchstaben, mindestens vier Buchstaben, danach hoechstens ein Satzzeichen, eine Klammer oder ` -- `.
- `_ROLLE = re.compile(':(?:class|func|meth|attr|mod|data|exc|obj):`([^`]+)`')`
- `_CODE = re.compile('``(.+?)``')`
- `_LISTE = re.compile('^(\\s*)([*-]|\\d+\\.)\\s')`
- `_KOPF = re.compile('^opencivil[\\w/.]*\\s+--\\s+(.*)$')`

## Braucht

- [[opencivil.notizbuch.namen]]
- [[opencivil.notizbuch.tresor]]

## Gebraucht von

- [[opencivil.notizbuch.erzeugen]]
