---
erzeugt: fc1d27ff3d81
art: modul
tags: [modul]
---
> [!abstract] opencivil/verbund/querschnitt.py
> ein gezeichneter Querschnitt aus Baustahl und Beton.
> Paket [[opencivil.verbund]] · [Quelltext](../../opencivil/verbund/querschnitt.py)

## VERANTWORTUNG

Was die Nachweise eines Verbundquerschnitts nach SIA 264:2014 aus der
Zeichnung brauchen, ohne Rechenwerk und ohne Herleitung, in mm und N/mm²:

* den Stahl fuer sich ([[opencivil.stahlbau.querschnitt#Stahlquerschnitt|Stahlquerschnitt]]):
  seine Bleche, die Querkraft seiner Profile;
* je Beton und je Betonstahl eine Gruppe dazu ([[opencivil.verbund.querschnitt#Verbundquerschnitt|Verbundquerschnitt.gruppen]]);
* den Querschnitt starr-plastisch ([[opencivil.verbund.querschnitt#Verbundquerschnitt.starr|Verbundquerschnitt.starr]]), je
  Gruppe mit der Festigkeit, die die Nachweise waehlen
  ([[opencivil.querschnitt.plastisch]]);
* was 5.1.2.2 fuer `β` misst: die Hoehe quer zur Nulllinie und wie weit der
  gedrueckte Beton von ihr reicht;
* die Klasse jedes Blechs an einer plastischen Nulllinie
  ([[opencivil.verbund.querschnitt#Verbundquerschnitt.zustaende|Verbundquerschnitt.zustaende]]).


## DER BETON, DIE STAEBE

Ein Polygon aus Beton zaehlt wie eines aus Stahl: +1, wo es liegt, -1 im
Elternteil, den es dort ersetzt ([[opencivil.querschnitt.plastisch#stuecke|stuecke]])
-- ein Profil im Beton nimmt ihn dort weg. Ein Stab ist ein Quadrat seiner
Flaeche um seine Mitte, eine verschmierte Linie ein Rechteck ihrer Flaeche
ueber ihre Laenge; beide verdraengen den Beton, in dem sie liegen, wie im
Stahlbeton. Liegt die Nulllinie in einem Stab, verteilt sich seine Kraft so
ueber das Quadrat -- nach Vorgabe, nicht nachgeschlagen.


## DIE KLASSEN (4.2.2.1, Tabellen 2 und 3)

Gefragt wird nur, ob jedes Blech die Klasse 1 oder 2 haelt: plastisch
rechnet der Verbund nur dann, und elastisch nach 5.1.2.4 und 5.1.2.5
rechnet ihn das Werkzeug nicht. Ein Blech darueber hat hier die Klasse 3 --
sie heisst «über 2». Gemessen wird wie im Stahl ([[opencivil.stahlbau.klasse]]),
mit `α` an der plastischen Nulllinie des Verbunds.


## KAMMERBETONIERT (4.2.2.1, Tabelle 3; 5.2.1.3)

Ein Flansch eines I-Profils gilt als kammerbetoniert, wenn Beton seine
Innenseite von der Ausrundung bis 0.4 b von der Mitte des Stegs deckt: so
breit muss der Beton nach dem Bild der Tabelle 3 mindestens sein,
`0.8 ≤ b_c/b`. Der Steg, wenn Beton ihn auf beiden Seiten zwischen den
Ausrundungen deckt. Geprueft wird an fuenf Punkten einen Millimeter neben
dem Blech, von einem Millimeter nach der Ausrundung bis einen Millimeter
vor dem Ende (nach Vorgabe, nicht nachgeschlagen). Breiterer Beton zaehlt
mit: eingebettet beult ein Blech nicht frueher (nach Vorgabe, nicht
nachgeschlagen).

Dann gelten fuer den Flansch die Grenzen der Tabelle 3, wo sie weiter sind
als die der SIA 263 mit `α`. Ein Steg der Klasse 3 darf nach 5.2.1.3 wie
einer der Klasse 2 rechnen; seine Grenze der Klasse 3 haengt aber an der
elastischen Spannung, und die rechnet das Werkzeug im Verbund nicht. Es
nimmt darum die kleinste fuer jedes `ψ`, 42ε bei reinem Druck (SIA 263,
Tabelle 5a), als Grenze der Klasse 2 -- auf der sicheren Seite, nach
Vorgabe, nicht nachgeschlagen. Dass der Steg mit dem Kammerbeton verduebelt
ist (5.2.1.2), nimmt es an. Dass die Duebel einen Druckflansch nach 4.2.2.3
in die Klasse 1 heben, prueft es nicht.

## Inhalt

### stahlflaechen

```python
def stahlflaechen(element: Bewehrungselement) -> List[Tuple[Tuple[Punkt, ...], Punkt]]
```

Die Flaechen eines Bewehrungselements als Polygone, je mit dem Punkt, an
dem es den Beton verdraengt -- siehe Dateikopf.

### Verbundquerschnitt

```python
class Verbundquerschnitt
```

Die Polygone und Staebe eines Verbundquerschnitts -- siehe Dateikopf.

#### Verbundquerschnitt.art

```python
def art(self, g: int) -> Baustoffart
```

#### Verbundquerschnitt.gruppen_der

```python
def gruppen_der(self, art: Baustoffart) -> List[int]
```

#### Verbundquerschnitt.stuecke

```python
def stuecke(self, stahl: Optional[Stahlquerschnitt]=None) -> Tuple[Stueck, ...]
```

Alle Stuecke -- mit `stahl`, wo die Querkraft einen Teil des Stahls genommen hat.

#### Verbundquerschnitt.starr

```python
def starr(self, zug: Sequence[float], druck: Sequence[float], stahl: Optional[Stahlquerschnitt]=None) -> Starrplastisch
```

Der Querschnitt starr-plastisch, je Gruppe mit `zug` und `druck`.

#### Verbundquerschnitt.flaechen_je_gruppe

```python
def flaechen_je_gruppe(self) -> List[float]
```

Je Gruppe ihre Flaeche in mm² -- beim Beton ohne, was Stahl und Staebe verdraengen.

#### Verbundquerschnitt.hoehe

```python
def hoehe(self, n: Tuple[float, float]) -> float
```

Die Hoehe des Querschnitts quer zur Nulllinie mit der Einheitsnormalen `n`, in mm.

#### Verbundquerschnitt.druckzone_beton

```python
def druckzone_beton(self, linie: Linie) -> float
```

Wie weit der gedrueckte Beton von der Nulllinie reicht, in mm --
`x_p` in 5.1.2.2; null, wo kein Beton gedrueckt ist.

#### Verbundquerschnitt.zustaende

```python
def zustaende(self, linie: Linie, eps: Sequence[float], stahl: Optional[Stahlquerschnitt]=None) -> List[Blechzustand]
```

Jedes Blech jedes Profils an der plastischen Nulllinie, mit `ε` je
Gruppe des Stahls -- Klasse 1, 2 oder 3 fuer «über 2»; ein
kammerbetoniertes Blech mit den Grenzen der SIA 264, wo sie weiter
sind, und dann mit ihrer Stelle (siehe Dateikopf).

#### Verbundquerschnitt.freie_gedrueckt

```python
def freie_gedrueckt(self, linie: Linie) -> List[Teil]
```

Die frei gezeichneten Flaechen aus Baustahl, die an der Nulllinie gedrueckt sind.

#### Verbundquerschnitt.kammerbetoniert

```python
def kammerbetoniert(self, teil: Teil, blech: Blech) -> bool
```

Ob Beton im I-Profil den Flansch innen, den Steg beidseits deckt -- siehe Dateikopf.


## Konstanten

- `KAMMER = {Halterung.EINSEITIG: ((9.0, 14.0), 'SIA 264, Tabelle 3'), Halterung.…` – Was der Kammerbeton je Blech erlaubt: die Grenzen `c/t` der Klassen 1 und 2, durch `ε`, und woher sie kommen -- siehe Dateikopf.
- `BREITE_BETON = 0.8` – Wie breit der Beton nach dem Bild der Tabelle 3 mindestens ist: `b_c/b`.
- `NEBEN = 1.0` – Wie weit neben dem Flansch und an wie vielen Stellen geprueft wird, ob Beton ihn deckt.
- `STELLEN = 5`

## Braucht

- [[opencivil.material.basis]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.bewehrungselemente]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.plastisch]]
- [[opencivil.stahlbau.klasse]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlprofile.bleche]]
- [[opencivil.stahlprofile.formen]]
- [[opencivil.stahlprofile.tabelle]]

## Gebraucht von

- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_werte]]
- [[opencivil.verbund.widerstand]]
