---
erzeugt: 66975a6e2e15
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
  ([[opencivil.querschnitt.plastisch]]) – und in den zwei Teilen, die
  nur die Duebel verbinden ([[opencivil.verbund.querschnitt#Verbundquerschnitt.getrennt|Verbundquerschnitt.getrennt]], siehe
  unten);
* ob der Baustahl ein doppelsymmetrisches Profil ist – fuer (29)
  ([[opencivil.verbund.querschnitt#Verbundquerschnitt.doppelsymmetrisch|Verbundquerschnitt.doppelsymmetrisch]]) –, und auf welcher Seite
  des Baustahls der Beton liegt: zieht ein Moment diese Seite, liegt es im
  Bereich negativer Momente ([[opencivil.verbund.querschnitt#Verbundquerschnitt.zum_beton|Verbundquerschnitt.zum_beton]]);
* was 5.1.2.2 fuer `β` misst: die Hoehe quer zur Nulllinie und wie weit der
  gedrueckte Beton von ihr reicht;
* die Klasse jedes Blechs an einer plastischen Nulllinie
  ([[opencivil.verbund.querschnitt#Verbundquerschnitt.zustaende|Verbundquerschnitt.zustaende]]).


## DER BETON, DIE STAEBE

Ein Polygon aus Beton zaehlt wie eines aus Stahl: +1, wo es liegt, -1 im
Elternteil, den es dort ersetzt ([[opencivil.querschnitt.plastisch#stuecke|stuecke]])
– ein Profil im Beton nimmt ihn dort weg. Ein Stab ist ein Quadrat seiner
Flaeche um seine Mitte, eine verschmierte Linie ein Rechteck ihrer Flaeche
ueber ihre Laenge
([[opencivil.querschnitt.bewehrungselemente#Bewehrungselement.stahlflaechen|stahlflaechen]]);
beide verdraengen den Beton, in dem sie liegen, wie im Stahlbeton. Liegt
die Nulllinie in einem Stab, verteilt sich seine Kraft so ueber das Quadrat
– nach Vorgabe, nicht nachgeschlagen. Das Profilblech einer
Blechverbunddecke liegt am Rand ihres Betons und verdraengt keinen.


## WAS DIE DUEBEL VERBINDEN

Die Kopfbolzenduebel sitzen in der Fuge zwischen dem Beton und dem Profil.
Auf der einen Seite liegen Beton und Betonstahl ausserhalb der Profile –
die Platte –, auf der anderen der Baustahl mit dem Beton und den Staeben in
seiner konvexen Huelle: Kammerbeton zaehlt zum Stahl, denn er ist mit dem
Steg verbunden (5.2.1.2), nicht ueber die Duebel der Fuge (nach Vorgabe,
nicht nachgeschlagen). Was in der Huelle liegt, schneidet das Werkzeug aus
jedem Stueck aus ([[opencivil.querschnitt.geometrie#in_huelle|in_huelle]]): mit
umgekehrtem Gewicht auf der Seite des Betons, mit seinem eigenen auf der
des Stahls, dort mit dem Zusatz «in der Kammer» ([[opencivil.verbund.querschnitt#Verbundquerschnitt.fuge|Verbundquerschnitt.fuge]]).


## DIE KLASSEN (4.2.2.1, Tabellen 2 und 3)

Gefragt wird nur, ob jedes Blech die Klasse 1 oder 2 haelt: plastisch
rechnet der Verbund nur dann, und elastisch nach 5.1.2.4 und 5.1.2.5
rechnet ihn das Werkzeug nicht. Ein Blech darueber hat hier die Klasse 3 –
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
Tabelle 5a), als Grenze der Klasse 2 – auf der sicheren Seite, nach
Vorgabe, nicht nachgeschlagen. Dass der Steg mit dem Kammerbeton verduebelt
ist (5.2.1.2), nimmt es an. Dass die Duebel einen Druckflansch nach 4.2.2.3
in die Klasse 1 heben, prueft es nicht.

## Inhalt

### Verbundquerschnitt

```python
class Verbundquerschnitt
```

Die Polygone und Staebe eines Verbundquerschnitts – siehe Dateikopf.

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

Alle Stuecke – mit `stahl`, wo die Querkraft einen Teil des Stahls genommen hat.

#### Verbundquerschnitt.starr

```python
def starr(self, zug: Sequence[float], druck: Sequence[float], stahl: Optional[Stahlquerschnitt]=None) -> Starrplastisch
```

Der Querschnitt starr-plastisch, je Gruppe mit `zug` und `druck`.

#### Verbundquerschnitt.fuge

```python
@cached_property
def fuge(self) -> Tuple[Tuple[Stueck, ...], Tuple[Stueck, ...]]
```

Beton und Betonstahl je auf ihrer Seite der Fuge (siehe Dateikopf):
ausserhalb der Profile – mit dem, was in ihrer Huelle liegt,
abgezogen –, und in der Huelle eines Profils.

#### Verbundquerschnitt.getrennt

```python
def getrennt(self, zug: Sequence[float], druck: Sequence[float], stahl: Optional[Stahlquerschnitt]=None) -> Tuple[Starrplastisch, Starrplastisch]
```

Der Querschnitt starr-plastisch in den zwei Teilen, die nur die Duebel
verbinden ([[opencivil.verbund.querschnitt#Verbundquerschnitt.fuge|fuge]]): Beton und Betonstahl ausserhalb der Profile,
und der Baustahl – mit `stahl`, wo die Querkraft ihm einen Teil
genommen hat – mit dem Kammerbeton. Je Gruppe mit `zug` und
`druck`.

#### Verbundquerschnitt.doppelsymmetrisch

```python
@property
def doppelsymmetrisch(self) -> bool
```

Ob der Baustahl ein einziges Profil mit zwei Symmetrieachsen ist: ein
I-Profil oder ein Rohr. Ein frei gezeichneter Baustahl zaehlt nicht,
auch wo er symmetrisch ist – das Werkzeug prueft es nicht.

#### Verbundquerschnitt.zum_beton

```python
@cached_property
def zum_beton(self) -> Optional[Tuple[float, float]]
```

Ueber die Fuge ([[opencivil.verbund.querschnitt#Verbundquerschnitt.fuge|fuge]]): vom Schwerpunkt des Stahls mit dem
Kammerbeton zu dem von Beton und Betonstahl ausserhalb der Profile,
in mm, je nach Flaeche. `None`, wo ausserhalb nichts liegt oder die
Schwerpunkte keinen Millimeter auseinander – dort hat der Beton keine
Seite.

#### Verbundquerschnitt.flaechen_je_gruppe

```python
def flaechen_je_gruppe(self) -> List[float]
```

Je Gruppe ihre Flaeche in mm² – beim Beton ohne, was Stahl und Staebe verdraengen.

#### Verbundquerschnitt.hoehe

```python
def hoehe(self, n: Tuple[float, float]) -> float
```

Die Hoehe des Querschnitts quer zur Nulllinie mit der Einheitsnormalen `n`, in mm.

#### Verbundquerschnitt.druckzone_beton

```python
def druckzone_beton(self, linie: Linie) -> float
```

Wie weit der gedrueckte Beton von der Nulllinie reicht, in mm –
`x_p` in 5.1.2.2; null, wo kein Beton gedrueckt ist.

#### Verbundquerschnitt.zustaende

```python
def zustaende(self, linie: Linie, eps: Sequence[float], stahl: Optional[Stahlquerschnitt]=None) -> List[Blechzustand]
```

Jedes Blech jedes Profils an der plastischen Nulllinie, mit `ε` je
Gruppe des Stahls – Klasse 1, 2 oder 3 fuer «über 2»; ein
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

Ob Beton im I-Profil den Flansch innen, den Steg beidseits deckt – siehe Dateikopf.


## Konstanten

- `KAMMER = {Halterung.EINSEITIG: ((9.0, 14.0), 'SIA 264, Tabelle 3'), Halterung.…` – Was der Kammerbeton je Blech erlaubt: die Grenzen `c/t` der Klassen 1 und 2, durch `ε`, und woher sie kommen – siehe Dateikopf.
- `BREITE_BETON = 0.8` – Wie breit der Beton nach dem Bild der Tabelle 3 mindestens ist: `b_c/b`.
- `NEBEN = 1.0` – Wie weit neben dem Flansch und an wie vielen Stellen geprueft wird, ob Beton ihn deckt.
- `STELLEN = 5`
- `DOPPELSYMMETRISCH = (I_PROFIL, RECHTECKROHR_GERUNDET, RUNDROHR)` – Die Formen, deren Profile zwei Symmetrieachsen haben.
- `IN_DER_KAMMER = 'in der Kammer'` – Wie ein Stueck heisst, das in der Huelle eines Profils liegt – siehe Dateikopf.
- `SEITE_AB = 1.0` – Wie weit die Schwerpunkte von Baustahl und Beton mindestens auseinander liegen, in mm, damit der Beton eine Seite hat.

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
- [[opencivil.verbund.blechdecke]]
- [[opencivil.verbund.stuetze]]
- [[opencivil.verbund.widerstand]]
