---
erzeugt: 1e355307caba
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/resistenzlinie.py
> die Linie, gegen die der M-N-Nachweis haelt.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/resistenzlinie.py)

## VERANTWORTUNG

Eine Schnittstelle fuer beide Arten Resistenzlinie, damit der Nachweis und
alles, was an ihm mitliest -- Querkraft, sproedes Versagen, Knicken --, nicht
fragen muss, welche er vor sich hat:

* [[opencivil.nachweis.resistenzlinie#Handlinie|Handlinie]] -- das Polygon der Handrechnung
  ([[opencivil.nachweis.handrechnung]]): wenige Eckpunkte, dazwischen
  geradlinig interpoliert. Jede Zahl laesst sich von Hand nachrechnen.
* [[opencivil.nachweis.resistenzlinie#Ebenenlinie|Ebenenlinie]] -- der Rand des Dehnungsfaechers
  ([[opencivil.nachweis.dehnungsfaecher]]), mit dem Spannungsblock oder
  der Parabel, die gedrueckte Bewehrung eingeschlossen. Ihr Polygon dient zum
  Zeichnen und zum Eingrenzen. Den Widerstand bei einer Normalkraft (oder
  einem Moment) sucht sie auf dem Faecher selbst, zwischen den beiden Ebenen,
  die ihn einschliessen -- nicht auf der Sehne dazwischen. So haengt keine
  Zahl im Bericht an der Schrittweite der Zeichnung.


## DIE SCHNITTSTELLE

```python
innerhalb(N, M)              ob ein Punkt drin liegt
kante(achse, fest, positiv)  der aeusserste Schnitt, mit Stuetzpunkten
moment_bei(N, positiv)       der Momentenwiderstand bei einer Normalkraft
eckwerte()                   N und M an den Spitzen, M bei N = 0
protokoll_treffer(...)       wie ein Widerstand gefunden wurde
```


## WIE EIN WIDERSTAND DER EBENENLINIE IN DIE HERLEITUNG KOMMT

Nicht die Suche, sondern ihre Probe -- wie bei der Querschnittsanalyse: die
gefundene Ebene, die Kraft jedes Teils und die Summen. Das laesst sich mit
dem Taschenrechner nachpruefen, die Suche nicht.


## VORZEICHEN

```
N > 0   Zug
M > 0   Zug an der Unterseite
```
Bezugsachse fuer M ist die halbe Querschnittshoehe.

## Inhalt

### Treffer

```python
@dataclass(frozen=True)
class Treffer
```

Wo eine Gerade `achse.gegen = fest` die Linie aeusserst trifft.

- `wert: float` – Der Wert auf der gesuchten Achse, in SI.
- `a: Any`
- `b: Any` – Die Stuetzpunkte des Polygons, zwischen denen er liegt.
- `eps_oben: Optional[float] = None`
- `eps_unten: Optional[float] = None` – Die Dehnungsebene dort -- nur bei der Ebenenlinie, die ihn genau sucht.

### Widerstandslinie

```python
class Widerstandslinie
```

Was der M-N-Nachweis von einer Resistenzlinie braucht -- siehe Dateikopf.

- `wahl: Rechenwahl`
- `punkte: List[Any]`

#### Widerstandslinie.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Widerstandslinie.innerhalb

```python
def innerhalb(self, N: float, M: float) -> bool
```

#### Widerstandslinie.kante

```python
def kante(self, achse: geo.Achse, fest: float, positiv: bool) -> Optional[Treffer]
```

#### Widerstandslinie.moment_bei

```python
def moment_bei(self, N: float, positiv: bool) -> Optional[float]
```

Der Momentenwiderstand bei dieser Normalkraft, als Betrag -- `None`,
wenn sie ausserhalb der Linie liegt.

#### Widerstandslinie.eckwerte

```python
def eckwerte(self) -> Dict[str, float]
```

#### Widerstandslinie.protokoll_treffer

```python
def protokoll_treffer(self, p: Protokoll, treffer: Treffer, *, achse: geo.Achse, fest: float, basis: str, titel: str='') -> None
```

### _eckwerte

```python
def _eckwerte(extrem: Callable[[geo.Achse, bool], float], bei_null: Sequence[float]) -> Dict[str, float]
```

Die Eckwerte, in SI -- bei beiden Linien in derselben Gestalt.
`extrem(achse, positiv)` ist der groesste (oder kleinste) Wert der
Linie auf einer Achse.

### Handlinie

```python
class Handlinie(Widerstandslinie)
```

Das Polygon der Handrechnung -- geradlinig zwischen den Eckpunkten.

#### Handlinie.innerhalb

```python
def innerhalb(self, N: float, M: float) -> bool
```

#### Handlinie.kante

```python
def kante(self, achse: geo.Achse, fest: float, positiv: bool) -> Optional[Treffer]
```

#### Handlinie.eckwerte

```python
def eckwerte(self) -> Dict[str, float]
```

#### Handlinie.protokoll_treffer

```python
def protokoll_treffer(self, p: Protokoll, treffer: Treffer, *, achse: geo.Achse, fest: float, basis: str, titel: str='') -> None
```

Zwischen welchen beiden Eckpunkten geradlinig interpoliert wurde, und
mit welchem Anteil.

Ohne diesen Schritt stuende in der Mitschrift eine Zahl, die zwar aus
nachvollziehbaren Eckpunkten stammt, aber selbst vom Himmel faellt.

Faellt die festgehaltene Groesse genau auf einen Eckpunkt -- der haeufige
Fall `N_Ed = 0`, und ebenso `M_Ed = 0` bei reiner Normalkraft --, wird
nicht interpoliert. Dort stuende sonst ein Bruch mit null im Zaehler, der
nichts erklaert und nur so aussieht, als waere etwas gerechnet worden.

### Ebenenlinie

```python
class Ebenenlinie(Widerstandslinie)
```

Der Rand des Dehnungsfaechers -- genau nachgeschaerft, siehe Dateikopf.

`beton` ist das Gesetz der Wahl
([[opencivil.nachweis.rechenwahl#betongesetz|betongesetz]]). Der Stahl kommt je
Lage mit ihrer [[opencivil.nachweis.querschnittsloeser#Stahllage|Stahllage]] -- als [[opencivil.querschnitt.werkstoffgesetz#Stahlgesetz|Stahlgesetz]], ohne
Abfall jenseits von `eps_ud`: die unterste Lage liegt im Faecher genau
auf dieser Grenze, und ein Gesetz, das dort auf null faellt, kippte an
der Rundung.

#### Ebenenlinie.kraefte

```python
def kraefte(self, eps_oben: float, eps_unten: float) -> Tuple[float, float]
```

N und M der Ebene durch `eps_oben` und `eps_unten` -- um die halbe Hoehe.

#### Ebenenlinie.kante

```python
def kante(self, achse: geo.Achse, fest: float, positiv: bool) -> Optional[Treffer]
```

Der aeusserste Schnitt, auf dem Faecher gesucht: zwischen den beiden
Ebenen, deren Punkte ihn einschliessen. Zwei benachbarte Punkte liegen
im selben Abschnitt des Faechers, und dort ist jede Ebene dazwischen
selbst eine des Faechers -- die Suche bleibt auf dem Rand.

Einmal je Frage gerechnet: das Urteil, der Grad und der Widerstand
bei N_Ed fragen dieselbe Kante.

#### Ebenenlinie.innerhalb

```python
def innerhalb(self, N: float, M: float) -> bool
```

Genau statt am Polygon: bei dieser Normalkraft zwischen dem linken und
dem rechten Rand. So kann das Urteil nie dem Erfuellungsgrad
widersprechen, der an denselben Raendern gemessen wird.

#### Ebenenlinie.eckwerte

```python
def eckwerte(self) -> Dict[str, float]
```

Auch die Spitzen liegen meist zwischen zwei Ebenen -- das groesste
Moment, und ebenso die groesste Druckkraft: kippt die Ebene ein wenig
um den Punkt C, fliesst die gedrueckte Bewehrung und traegt mehr als
beim gleichmaessigen -eps_c1d. Sie werden dort gesucht, wie der
Widerstand bei N = 0.

#### Ebenenlinie._extrem

```python
def _extrem(self, achse: geo.Achse, positiv: bool) -> float
```

Der groesste (oder kleinste) Wert auf einer Achse: um den Punkt der
Linie, der ihn traegt, ueber die Ebenen bis zu seinen beiden
Nachbarn -- mit dem Goldenen Schnitt.

#### Ebenenlinie.erreicht

```python
def erreicht(self, eps_oben: float, eps_unten: float) -> List[str]
```

Welche Grenzen diese Ebene erreicht -- die, die ihren Bruchzustand bestimmen.

#### Ebenenlinie.protokoll_ansatz

```python
def protokoll_ansatz(self, p: Protokoll, *, f_c: Wert, E_cm: Wert, phi: Wert, basis: str) -> None
```

Wie die Linie entsteht -- einmal je Nachweis, vor den Kombinationen.
Den Titel setzt der Nachweis.

#### Ebenenlinie.protokoll_treffer

```python
def protokoll_treffer(self, p: Protokoll, treffer: Treffer, *, achse: geo.Achse, fest: float, basis: str, titel: str='') -> None
```

Die Probe des Bruchzustands, an dem der Widerstand liegt: die Ebene,
die Kraft jedes Teils, die Summen -- und welche Grenze ihn bestimmt.

Der Stahl mit seiner vollen Spannung, `F = sigma_s · A_s`; der Beton
als Resultierende ohne die Flaeche, die der Stahl einnimmt. So ist
jede Zeile fuer sich nachzurechnen, und die Summe ist die der Fasern.

### _trifft

```python
def _trifft(a: float, b: float) -> bool
```

Ob zwei SI-Werte fuer die Mitschrift als derselbe gelten.

Die Schranke haengt an der Groesse der Werte, nicht an einer festen Zahl:
Momente liegen im Bereich 1e5 Nm, und dort ist ein absoluter Abstand von
1e-9 unerreichbar streng.

### _k

```python
def _k(si_wert: float) -> str
```

Ein SI-Wert in Kilo-Einheiten, eine Nachkommastelle.


## Konstanten

- `AUF_DER_GRENZE = 1e-12` – Ab welchem Abstand eine Dehnung nicht mehr auf ihrer Grenze liegt. Die gefundene Ebene haelt ihren Drehpunkt bis auf Rundung (1e-18); was naeher als dies an einer Grenze liegt, liegt auf ihr.
- `GOLDSCHRITTE = 30` – Schritte des Goldenen Schnitts, der eine Spitze der Linie zwischen zwei Ebenen sucht: das Fenster schrumpft auf 1e-6 einer Schrittweite. An der Spitze ist die Linie flach -- der Fehler im Wert ist das Quadrat davon.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.dehnungsfaecher]]
- [[opencivil.nachweis.linie]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.web.diagrammdaten]]

## Formeln aus diesem Modul

- [[Bilineare Beziehung des Betonstahls]] · `Ebenenlinie.protokoll_ansatz`
- [[Schnittgrössen aus der Spannungsverteilung]] · `Ebenenlinie.protokoll_ansatz`
- [[Widerstand bei festgehaltenem N_Ed]] · `Handlinie.protokoll_treffer`
