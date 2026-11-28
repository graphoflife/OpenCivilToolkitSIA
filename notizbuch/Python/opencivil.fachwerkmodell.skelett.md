---
erzeugt: 894a6a5df4fa
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/skelett.py
> aus der Form des SIMP die möglichen Stäbe eines Fachwerks.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/skelett.py)

## VERANTWORTUNG

Was das Verfahren SIMP ([[opencivil.fachwerkmodell.simp|simp]]) an
Material verteilt hat, als Fachwerk gelesen ([[opencivil.fachwerkmodell.skelett#moegliche_staebe|moegliche_staebe]]),
in den Schritten von Xia, Langelaar & Hendriks (2020), Abschnitt 2.3 –
ab dem dritten angepasst:

1. Zur Form gehört ein Element, wenn seine gefilterte Dichte mindestens
   0.5 ist; die Elemente unter Lagern und Lasten immer.
2. Die Form wird ausgedünnt, bis nur ihre Mittellinien bleiben, ein
   Element breit – nach Zhang & Suen (1984). Äste, die frei enden, fallen
   weg, und was an keinem Lager und keiner Last hängt: sie tragen nichts.
3. Knoten sind, wo eine Linie endet oder sich verzweigt, dazu jedes Lager
   und jede Last genau an ihrem Punkt. Biegt eine Linie zwischen zwei
   Knoten mehr als 1.5 Netzweiten von der Geraden ab, bekommt sie dort
   einen – nach Douglas & Peucker (1973).
4. Liegen Knoten näher als 5 % der kürzeren Seite des Rechtecks um die
   Scheiben, werden sie einer. Steht ein Stab weniger als 10° schief zur
   Senkrechten oder Waagrechten durch ein Lager oder eine Last, rückt sein
   anderer Knoten genau darauf.


## DIE MÖGLICHEN STÄBE

Die Quelle verbindet die Knoten längs der Linien; das allein wäre oft
beweglich, solange die Form noch nicht ganz klar ist. Hier ist darum jedes
Paar von Knoten ein möglicher Stab, wenn er ganz im Material liegt und
durch keinen dritten Knoten geht. Er kostet in der Optimierung umso mehr,
je mehr von ihm neben der Form liegt – um ein Element erweitert –, ganz
daneben zehnmal so viel wie ganz in ihr. So folgt das Fachwerk der Form,
wo sie trägt, und hilft sich mit einem Stab daneben, wo sie es nicht tut.
Die Kräfte bestimmt die Optimierung der Ground Structure
([[opencivil.fachwerkmodell.suche|suche]]).

Aus der Quelle sind die Schwelle 0.5 und die 5 %; die 1.5 Netzweiten, die
10°, das Zehnfache, das Wegfallen der freien Äste und die Paare sind nach
Vorgabe, nicht nachgeschlagen.

## Inhalt

### moegliche_staebe

```python
def moegliche_staebe(n: Netz, x: Sequence[float]) -> Grundstruktur
```

Die möglichen Stäbe der Form mit den Dichten `x`, je mit ihren Kosten – siehe Dateikopf.

### _element_bei

```python
def _element_bei(n: Netz, im_netz: Set[Platz], p: Punkt) -> Platz
```

Das Element, in dem `p` liegt – oder, liegt es in keinem, das mit der nächsten Mitte.

### ausgeduennt

```python
def ausgeduennt(pixel: Set[Platz], fest: Set[Platz]) -> Set[Platz]
```

Die Mittellinien der Elemente `pixel` nach Zhang & Suen (1984): in zwei
Teilschritten fällt weg, was am Rand liegt, die Linie nicht trennt und
kein Ende ist – bis nichts mehr wegfällt. `fest` bleibt.

### mittellinien

```python
def mittellinien(form: Set[Platz], fest: Set[Platz]) -> Set[Platz]
```

Die Mittellinien der `form`, ein Element breit: ausgedünnt
([[opencivil.fachwerkmodell.skelett#ausgeduennt|ausgeduennt]]), dann ohne die Elemente, die keine Verbindung
tragen – an einer Stufe einer schrägen Linie bleibt sonst eines zu viel
–, dann ohne die Äste, die frei enden: ohne Lager und Last am Ende
trägt ein Ast nichts. Was dann an keinem Lager und keiner Last hängt,
fällt ganz weg. `fest` bleibt.

### _einfach

```python
def _einfach(n: Sequence[bool]) -> bool
```

Ob ein Element einer Linie wegfallen kann, ohne dass sie zerfällt oder
ein Loch entsteht – seine Nachbarn `n` im Kreis: die Zahl von Yokoi
für Nachbarn auch über Eck ist eins. Am Ende einer Linie ist sie auch
eins; dort entscheidet der Aufrufer.

### _kreuzungen

```python
def _kreuzungen(n: Sequence[bool]) -> int
```

Wie oft der Kreis der Nachbarn von leer auf voll wechselt – 1 am Ende einer Linie, 2 mitten in ihr.

### _knoten

```python
def _knoten(n: Netz, linien: Set[Platz], unter: Dict[Platz, int], punkte: Sequence[Punkt]) -> Tuple[List[Punkt], Dict[Platz, int]]
```

Die Knoten der Linien – zuerst die `punkte` der Lager und Lasten –
und je Element einer Linie, zu welchem Knoten es gehört; die Elemente
mitten in einer Linie gehören zu keinem. Wo Enden und Verzweigungen
aneinanderstossen, ist es ein Knoten in ihrer Mitte – oder, ist ein
Element unter einem Lager oder einer Last dabei, an dessen Punkt.

### _zusammenhang

```python
def _zusammenhang(start: Platz, menge: Set[Platz], gesehen: Set[Platz]) -> List[Platz]
```

Die Elemente von `menge`, die über Nachbarn mit `start` zusammenhängen.

### _staebe_der_linien

```python
def _staebe_der_linien(n: Netz, linien: Set[Platz], knoten: List[Punkt], zu: Dict[Platz, int]) -> Set[Tuple[int, int]]
```

Je Stück einer Linie zwischen zwei Knoten gerade Stäbe von Knoten zu
Knoten, wie die Streben eines Fachwerkmodells: biegt das Stück mehr als
[[opencivil.fachwerkmodell.skelett#Konstanten|KNICK]] Netzweiten von der Geraden ab, bekommt es dort einen
Knoten, und jede Hälfte wird ebenso geprüft ([[opencivil.fachwerkmodell.skelett#_knicke|_knicke]]). So wird
auch ein Stück, das zu seinem Knoten zurückkehrt – um ein Loch der Form
–, ein Vieleck. Stossen zwei Knoten direkt aneinander, ein Stab; trifft
ein Stück mehr als zwei Knoten, je zwei ein Stab.

### _knicke

```python
def _knicke(weg: Sequence[Punkt], grenze: float) -> List[int]
```

Wo ein Weg geknickt ist, in seiner Folge: der Punkt, der am weitesten
von der Geraden zwischen seinen Enden liegt, wenn mehr als `grenze` –
dann ebenso in den beiden Hälften, nach Douglas & Peucker (1973). Sind
die Enden ein Punkt, gilt der Abstand zu ihm.

### _abstand

```python
def _abstand(p: Punkt, a: Punkt, b: Punkt) -> float
```

Wie weit `p` von der Geraden durch `a` und `b` liegt – sind sie ein Punkt, von ihm.

### _der_reihe_nach

```python
def _der_reihe_nach(anfang: Sequence[Platz], stueck: Set[Platz]) -> List[Platz]
```

Die Elemente eines Stücks nach ihrem Abstand von `anfang` längs des Stücks.

### _ausgerichtet

```python
def _ausgerichtet(knoten: List[Punkt], staebe: Set[Tuple[int, int]], fest: int) -> List[Punkt]
```

Weicht ein Stab zu einem Lager oder einer Last (den ersten `fest`)
weniger als [[opencivil.fachwerkmodell.skelett#Konstanten|SCHIEF]] von der Senkrechten oder Waagrechten ab,
rückt sein anderer Knoten genau auf sie: die Mittellinie trifft den
Punkt oft nur auf ein, zwei Elemente genau, und schon so wenig schief
hielte ein Lager, das nur in einer Richtung hält, den Stab nicht.

### _zusammengefasst

```python
def _zusammengefasst(n: Netz, knoten: List[Punkt], staebe: Set[Tuple[int, int]], fest: int) -> Tuple[List[Punkt], Set[Tuple[int, int]]]
```

Knoten näher als [[opencivil.fachwerkmodell.skelett#Konstanten|NAHE]] als einer: in ihrem Mittel – ist einer
ein Lager oder eine Last (die ersten `fest`), an dessen Punkt; zwei
solche bleiben zwei.

### _erweitert

```python
def _erweitert(form: Set[Platz], im_netz: Set[Platz]) -> Set[Platz]
```

Die Form und je Element ihre Nachbarn, soweit sie im Netz sind.

### _daneben

```python
def _daneben(n: Netz, form: Set[Platz], a: Punkt, b: Punkt) -> float
```

Welcher Teil der Strecke `a → b` neben den Elementen `form` liegt – geprüft alle Viertel einer Netzweite.

### _auf

```python
def _auf(p: Punkt, a: Punkt, b: Punkt) -> bool
```

Ob `p` auf der Strecke `a → b` liegt, nicht an ihren Enden – bis auf Rundung.


## Konstanten

- `QUELLE = 'Xia, Langelaar & Hendriks (2020), Abschnitt 2.3'` – Wo die Schritte nachzulesen sind.
- `VOLL_AB = 0.5` – Ab dieser gefilterten Dichte gehört ein Element zur Form.
- `NAHE = 0.05` – Wie nahe zwei Knoten liegen dürfen, bezogen auf die kürzere Seite des Rechtecks – aus der Quelle.
- `SCHIEF = 10.0` – Bis zu welchem Winkel in Grad ein Stab an einem Lager oder einer Last senkrecht oder waagrecht gerückt wird – nach Vorgabe, nicht nachgeschlagen.
- `KNICK = 1.5` – Ab wie vielen Netzweiten Abstand von der Geraden eine Linie einen Knick hat – so breit verwischt der Filter die Form (nach Vorgabe, nicht nachgeschlagen).
- `NEBEN = 10.0` – Wie viel mal mehr ein Stab neben der Form kostet als in ihr – nach Vorgabe, nicht nachgeschlagen.
- `RING = ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))` – Die acht Nachbarn eines Elements, im Kreis von oben an.

## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.fachwerkmodell.grundstruktur]]
- [[opencivil.fachwerkmodell.simp]]

## Gebraucht von

- [[opencivil.fachwerkmodell.form]]
- [[opencivil.fachwerkmodell.herleitung]]
