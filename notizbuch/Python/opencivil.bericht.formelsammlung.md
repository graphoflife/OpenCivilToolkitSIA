---
erzeugt: 0f3e568e68f9
art: modul
tags: [modul]
---
> [!abstract] opencivil/bericht/formelsammlung.py
> jede Formel einmal, ohne Zahlen.
> Paket [[opencivil.bericht]] · [Quelltext](../../opencivil/bericht/formelsammlung.py)

## VERANTWORTUNG

Sammelt aus einer Herleitung je Thema -- «Beton», «Querkraft», «Knicken» --
die Formeln in ihrer symbolischen Fassung, `Symbol = Formel`, mit Titel
und Normstelle, und die Erklaerungen dazu. Die Herleitung zeigt Formeln mit
Zahlen und laesst die Erklaerungen weg; hier ist es umgekehrt: keine Zahlen,
dafuer das Warum.


## ZWEI SAMMLUNGEN

* Die ganze, zum Nachschlagen ([[opencivil.bericht.formelsammlung#vollstaendig|vollstaendig]]): jede Formel des
  Werkzeugs, gleich welches Projekt offen ist und welche Nachweise darin
  laufen. Die Oberflaeche zeigt sie; vorab erzeugt von
  `python3 -m opencivil.web.bruecke`.
* Die eines Laufs ([[opencivil.bericht.formelsammlung#formelsammlung|formelsammlung]]): im Bericht als «Verwendete
  Formeln» -- die Erklaerungen zu dem, was er rechnet, und nicht zu allem.


## JEDE FORMEL EINMAL

Dieselbe Formel steht in der Herleitung oft mehrfach -- je Lage, je Fall, je
Platte, mit anderen Indizes an den Symbolen, fuer das negative Moment mit
Minus davor. Erkannt wird sie an ihrer Vorlage (`@name`-Form, siehe
[[opencivil.core.latex#Formelzeile|Formelzeile.vorlage]], ohne fuehrendes Minus) und dem Grundzeichen ihres
Ergebnisses; gezeigt wird die erste Fassung. Ein Ansatz ohne Zahlen
([[opencivil.core.protokoll#Protokoll.ansatz|Protokoll.ansatz]]) ist schon symbolisch und zaehlt mit seinem LaTeX.
Und was gesetzt gleich aussieht, ist dieselbe Formel: Summe und Schwerpunkt
einer Lage schreiben Handrechnung und Lagennachweise mit anderen
Platzhalternamen.

Einmal im ganzen Lauf, nicht je Thema: gemeinsame Bausteine -- die statische
Hoehe, der Querschnittsloeser, die Zugfestigkeit -- stehen beim ersten Thema,
das sie braucht, und nicht bei jedem noch einmal.


## WIE EINE FORMEL HEISST

Im Notizbuch steht jede Formel auf einer Seite, und die Seite heisst wie die
Formel ([[opencivil.bericht.formelsammlung#formelname|formelname]]): ihr Titel ohne Zahlenangabe, oder der Name, den
der Code ihr gibt, wo der Titel je nach Fall wechselt oder fuer sich nichts
sagt. Formeln mit gleichem Namen sind Fassungen derselben Seite.


## WOHER DAS THEMA KOMMT

Das Rechenwerk stempelt es auf jeden Block, den eine Berechnung schreibt
([[opencivil.core.protokoll#Protokoll.herkunft_stempeln|Protokoll.herkunft_stempeln]]). Zu welchem Bestandteil ein Thema
gehoert -- Beton, Betonstahl, Platte --, sagt der Abschnitt, unter dem es zum
ersten Mal steht: sein Namensraum beginnt mit der Art (`beton.b1`). Danach
zeigt die Oberflaeche je Bestandteil nur seine Formeln.

## Inhalt

### Thema

```python
@dataclass
class Thema
```

- `name: str`
- `art: str = ''` – Zu welchem Bestandteil es gehoert: `beton`, `betonstahl`, `querschnitt`.
- `erklaerungen: List[TextBlock] = field(default_factory=list)`
- `formeln: List[GleichungBlock] = field(default_factory=list)`

#### Thema.bloecke

```python
@property
def bloecke(self) -> List[GleichungBlock | TextBlock]
```

Wie das Thema dasteht, im Bericht und am Bildschirm: erst das Warum.

### ohne_zahlenangabe

```python
def ohne_zahlenangabe(titel: str) -> str
```

«Widerstand bei festgehaltenem N_Ed = -300.0 kN» ohne die Zahl.

### schluessel

```python
def schluessel(block: GleichungBlock | TextBlock) -> Optional[tuple]
```

Woran derselbe Eintrag wiederzuerkennen ist -- `None`: er gehoert nicht hinein.

### in_sammlung

```python
def in_sammlung(block: Block) -> bool
```

Gehoert diese Gleichung in die Formelsammlung -- und damit ins Notizbuch?

### formelname

```python
def formelname(block: GleichungBlock) -> str
```

Unter welchem Namen die Formel im Notizbuch steht: der Name, den der Code
ihr gibt, sonst ihr Titel ohne Zahlenangabe -- als Seitenname. Fuer die
Formel in der Herleitung und fuer ihre symbolische Fassung derselbe.

### ergebniszeichen

```python
def ergebniszeichen(block: GleichungBlock) -> str
```

Was die Formel liefert, ohne Fall und Sorte: `f_{cd}`. Leer bei einem
Ansatz -- der liefert keinen Wert.

### symbolisch

```python
def symbolisch(block: GleichungBlock) -> GleichungBlock
```

Die Formel ohne Zahlen, `Symbol = Formel`. Gebaut erst fuer einen neuen
Schluessel -- neun von zehn Gleichungen sind Wiederholungen.

### formelsammlung

```python
def formelsammlung(protokoll: Protokoll) -> List[Thema]
```

Je Thema, in der Folge ihres ersten Auftretens, Erklaerungen und Formeln.

### laeufe

```python
@functools.lru_cache(maxsize=1)
def laeufe() -> Tuple[Protokoll, ...]
```

Die Laeufe, aus denen die ganze Sammlung entsteht -- je Projekt ein
Protokoll, samt seinen Spannung-Dehnung-Analysen.

[[opencivil.projekt.projekt#Projekt.beispiel|Projekt.beispiel]] und [[opencivil.projekt.projekt#Projekt.jeder_nachweis|Projekt.jeder_nachweis]] fuehren
zusammen jeden Nachweis laut, mit allen Kennwerten der Baustoffe
(`alle_ziele`: sonst fehlte etwa ε_yd). Im schnellen Aufbau: die
Grenzkraftsuche beim Knicken schreibt keine eigene Formel, und ganz stille
Nachweise schreiben nichts -- dieselbe Sammlung, Zeichen fuer Zeichen, in
einem Zehntel der Zeit. Die Analysen sind kein Nachweis und laufen nicht
im Rechenwerk, schreiben aber ebenso auf, wie ihre Linien entstehen.
Der Titel eines Protokolls sagt, aus welchem Projekt es stammt.

Gerechnet wird einmal je Lauf des Programms, gut vier Sekunden; Bruecke
und Tests fragen mehrmals. Getrennt je Projekt, weil eine Kennung wie
`querschnitt.q1` in beiden vorkommt und je etwas anderes meint. Die
Protokolle werden geteilt -- nicht veraendern.

### vollstaendig

```python
def vollstaendig() -> List[Thema]
```

Jede Formel des Werkzeugs, zum Nachschlagen -- gleich, welches Projekt
offen ist und welche Nachweise darin laufen. Aus [[opencivil.bericht.formelsammlung#laeufe|laeufe]].

### anfuegen

```python
def anfuegen(p: Protokoll, themen: List[Thema]) -> None
```

Fuer den Bericht: je Thema ein Titel, die Erklaerungen, dann die Formeln.


## Konstanten

- `_ZAHLENANGABE = re.compile('\\s*=\\s*-?\\d[\\d,]*\\.\\d+(?:\\s*[^\\s–,;)]+)?')` – Eine Zahlenangabe in einem Titel: `= -300.0 kN`. Die Herleitung nennt damit den Fall, die Sammlung zeigt die Formel ohne ihn. Nur mit Nachkommastelle -- `bei M_Ed = 0` ist eine Bedingung und bleibt.
- `_GRUNDZEICHEN = re.compile('^[^_^({]*')` – Das Grundzeichen eines Ergebnisses: `\sigma_{s,adm,2,x}` -> `\sigma`. Ohne Index, denn der traegt Lage und Richtung; mit Zeichen, denn zwei Formeln mit derselben kurzen Vorlage (`@z`) und verschiedenen Ergebnissen sind verschiedene Formeln.
- `_FALLWERTE = re.compile('\\([^()]*\\\\mathrm\\{[^()]*\\)')` – Fallwerte im Ergebnissymbol: `V_{Rd,x}(M_{Ed} = 150\,\mathrm{kNm}, ...)`. Erkannt an der Einheit -- eine Bedingung wie `(N_{Ed}=0)` bleibt.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.notizbuch.namen]]
- [[opencivil.projekt]]
- [[opencivil.spannungsanalyse]]

## Gebraucht von

- [[opencivil.bericht.gliederung]]
- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.web.api]]
- [[opencivil.web.bruecke]]
