---
erzeugt: 009a7ce008e0
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/platte.py
> das Paar einer Platte.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/platte.py)

## VERANTWORTUNG

Die beiden Loeser einer Tragrichtung, gerissen und ungerissen, und was die
Herleitung nur von der Platte weiss ([[opencivil.spannungsanalyse.platte#Loeserpaar|Loeserpaar]], ein
[[opencivil.spannungsanalyse.linie#Paar|Paar]]). Die Loeser sind die jedes
Querschnitts: die Platte als Rechteck mit Staeben
([[opencivil.nachweis.rechenwahl#Gesetze.loeser|loeser]]). Den Riss rechnet
sie wie der gezeichnete Querschnitt, am Bruttoquerschnitt – dem Rechteck
`b × h` ([[opencivil.spannungsanalyse.riss#Bruttoriss|Bruttoriss]]).

## Inhalt

### Loeserpaar

```python
@dataclass(frozen=True)
class Loeserpaar(Bruttoriss)
```

Die beiden Loeser einer Tragrichtung – gerissen und nicht.

Sie unterscheiden sich in genau einem Stueck, dem Betongesetz. Alles
andere – Hoehe, Breite, Lagen, Stahlgesetz, Grenzen – ist dasselbe, und
das muss es sein: sonst verglichen die beiden Zustaende zwei verschiedene
Querschnitte. Dazu, was zum Riss und zum Fliessen gehoert, und womit
gerechnet wird.

- `gerissen: Faserloeser`
- `ungerissen: Faserloeser`
- `h: float`
- `b: float` – Hoehe und Breite des Streifens, m.
- `brutto: Bruttoquerschnitt` – Das Rechteck `b × h` ohne Stahl – an ihm reisst die Platte.
- `riss: Rissmoment` – Das Rissmoment unter reiner Biegung, ohne Normalkraft.
- `staehle: Tuple[Any, ...] = ()` – Die Staehle der Lagen, jeder einmal – fuer die Fliessdehnung in der Herleitung. Fliessen beginnt, wo die erste Lage die Fliessdehnung ihres eigenen Stahls erreicht ([[opencivil.spannungsanalyse.platte#Loeserpaar|Stahlgesetz.eps_yd]] der Lage).
- `wahl: Rechenwahl = Rechenwahl(arten=Rechenarten.alle(Rechenart.PARABEL))` – Womit gerechnet wird – Kriechzahl, Wertesatz, Rechenart.
- `ids: Mapping[str, str] = field(default_factory=dict)` – Kurzname -> Wert-ID der Eingaben, fuer die Herleitung.
- `E_cm: float = 0.0` – Der Modul des Betons – daran misst sich der aequivalente Modul.
- `seite = Zugseite.UNTEN` – Ein positives Moment zieht unten.
- `DICKE_UNTER_ZUG = 'die Dicke der Platte'`
- `bezugsort = 'auf halber Höhe'` – Wo die Mitteldehnung gilt – dort greift N an.

#### Loeserpaar.ebenen

```python
def ebenen(self) -> Zustaende
```

Die Ebenen der Platte: ein Rechteck, die Nulllinie bleibt parallel zur Achse.

#### Loeserpaar.A

```python
@property
def A(self) -> float
```

Die Flaeche des Rechtecks, `b·h`.

#### Loeserpaar.t_zug

```python
@property
def t_zug(self) -> float
```

Die rissaktive Dicke unter Zug: die ganze Dicke der Platte.

#### Loeserpaar.tiefe

```python
def tiefe(self, w: Zwischenwerte, ein: Callable[[str], 'Wert']) -> 'Wert'
```

Die Dicke, ueber die die Linie laeuft – ein Wert der Platte.

#### Loeserpaar.herleitung_bruttoquerschnitt

```python
def herleitung_bruttoquerschnitt(self, p: Protokoll, w: Zwischenwerte, ein: Callable[[str], 'Wert'], h: 'Wert') -> Tuple['Wert', 'Wert']
```

Das Rechteck `b × h` des Streifens, ohne Stahl: `A` und `I` aus b und h.

#### Loeserpaar.herleitung_dicke_unter_zug

```python
def herleitung_dicke_unter_zug(self, p: Protokoll, w: Zwischenwerte, h: 'Wert') -> 'Wert'
```

Unter Zug reisst die ganze Dicke, `t = h`: der Streifen `b` ist keine
Abmessung der Platte ([[opencivil.nachweis.rissgroessen#rissaktive_dicke|rissaktive_dicke]]).
Ein Satz statt einer Formel – `t` steht fuer `h`, wie bisher.

#### Loeserpaar.herleitung_dehnung_am_ende

```python
def herleitung_dehnung_am_ende(self, p: Protokoll, w: Zwischenwerte, bruch: 'Grenzzustand', oben: 'Wert', unten: 'Wert', h: 'Wert') -> None
```

Die Dehnung, ueber die die N-eps-Linie laeuft, am Ende – auf halber Hoehe.

### loeserpaar

```python
def loeserpaar(querschnitt, richtung: Richtung, wert: Callable[[str], float], wahl: Rechenwahl=Rechenwahl(arten=Rechenarten.alle(Rechenart.PARABEL))) -> Optional[Loeserpaar]
```

Das Loeserpaar einer Platte in einer Richtung – `None` ohne Bewehrung.

`wert` liefert zu einer Wert-ID die Zahl in SI, aus einer Loesung.
`wahl` sagt, womit gerechnet wird: Kriechzahl, Wertesatz, Rechenart –
die Gesetze dazu baut [[opencivil.nachweis.rechenwahl#gesetze|gesetze]].

Stand frueher in der Schnittstelle zur Oberflaeche. Dort war sie ohne
Oberflaeche nicht erreichbar, und ein Test baute sie als eigene Kopie
nach – er pruefte seine Kopie statt der echten.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.riss]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.modul]]

## Formeln aus diesem Modul

- [[Fläche eines Rechtecks]] · `Loeserpaar.herleitung_bruttoquerschnitt`
- [[Flächenträgheitsmoment eines Rechtecks]] · `Loeserpaar.herleitung_bruttoquerschnitt`
- [[Grösste Dehnung auf halber Höhe]] · `Loeserpaar.herleitung_dehnung_am_ende`
