---
erzeugt: cface1426591
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/biegung_normalkraft.py
> Nachweis für Biegung mit Normalkraft.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/biegung_normalkraft.py)

## VERANTWORTUNG

Prueft beliebig viele Schnittgroessenkombinationen gegen die M-N-Interaktion
eines Querschnitts.


## ZWEI LINIEN, EINE DAVON MASSGEBEND

Welche massgebend ist, waehlt das Kapitel ([[opencivil.nachweis.rechenwahl#Rechenwahl|Rechenwahl]]):

* **Handrechnung Block 0.85·x** -- das Polygon aus wenigen Eckpunkten in
  [[opencivil.nachweis.handrechnung]]. Seine Herleitung steht
  vollstaendig in der Mitschrift.
* **Block 0.85·x genau** oder **Parabel** -- der Rand des Dehnungsfaechers,
  mit der gedrueckten Bewehrung. Den Widerstand bei der Einwirkung sucht er
  genau; in die Mitschrift kommt die Probe dieses Bruchzustands, nicht die
  Suche.

Beide stehen hinter derselben Schnittstelle
([[opencivil.nachweis.resistenzlinie]]). Die andere Linie steht zum
Vergleich im Diagramm: die Parabel neben der Handrechnung, sonst die
Handrechnung.

Mit charakteristischen Werten heissen die Widerstaende `N_Rk` und
`M_Rk`; die Kennungen der Werte bleiben dieselben.


## VORZEICHEN

```
N > 0   Zug
M > 0   Zug an der Unterseite (Feldmoment)
```
Bezugsachse fuer M ist die halbe Querschnittshoehe.


## EINHEITEN

N und M gelten fuer die betrachtete Breite `b`. Mit `b = 1 m` sind es also
unmittelbar die Werte pro Laufmeter.


## ERFUELLUNGSGRAD

Ob ein Punkt drin liegt oder nicht, entscheidet die massgebende Linie
([[opencivil.nachweis.resistenzlinie#Widerstandslinie.innerhalb|Widerstandslinie.innerhalb]]). Nur *wie weit* er von ihr entfernt ist,
haengt vom gewaehlten Massstab ab -- siehe [[opencivil.nachweis.biegung_normalkraft#Erfuellungsart|Erfuellungsart]] und
[[opencivil.nachweis.biegung_normalkraft#BiegungNormalkraft._auswerten|BiegungNormalkraft._auswerten]].

## Inhalt

### Erfuellungsart

```python
class Erfuellungsart(str, Enum)
```

Massstab, in dem der Abstand zur Resistenzlinie gemessen wird.

- `AUTOMATISCH = 'automatisch'` – Beide Wege werden gerechnet, massgebend ist der kleinere Erfuellungsgrad -- siehe [[opencivil.nachweis.biegung_normalkraft#BiegungNormalkraft._auswerten|BiegungNormalkraft._auswerten]]. Der Regelfall.
- `NORMALKRAFT_KONSTANT = 'N_konstant'` – Bei festgehaltener Normalkraft waagrecht bis zur Momentengrenze. Der Regelfall: die Normalkraft ist meist vorgegeben, aufnehmen muss der Querschnitt das Moment.
- `MOMENT_KONSTANT = 'M_konstant'` – Bei festgehaltenem Moment senkrecht bis zur Normalkraftgrenze.
- `NAECHSTER_PUNKT = 'naechster_Punkt'` – Kuerzester Weg zur Linie, gemessen im auf die Groesstwerte normierten Diagramm (sonst waere der Abstand von der Wahl der Einheiten abhaengig).

#### Erfuellungsart.beschriftung

```python
@property
def beschriftung(self) -> str
```

### Schnittgroessen

```python
@dataclass(frozen=True)
class Schnittgroessen
```

Eine zu prüfende Kombination aus Moment und Normalkraft.

- `name: str`
- `M_Ed: Groesse`
- `N_Ed: Groesse = field(default_factory=lambda: Groesse(0, KN))`
- `art: Erfuellungsart = Erfuellungsart.AUTOMATISCH`

#### Schnittgroessen.kennung

```python
@property
def kennung(self) -> str
```

### Normierung

```python
@dataclass(frozen=True)
class Normierung
```

Der kuerzeste Abstand im normierten Diagramm -- alles, was die Mitschrift
davon braucht.

Normiert wird auf die groesste Normalkraft und das groesste Moment der
Linie; ohne das haenge der Abstand von der Wahl der Einheiten ab. Der
Grad ist `rand / laenge` -- ein Verhaeltnis von Laengen im Diagramm,
nicht von Momenten.

- `N_ref: float`
- `M_ref: float`
- `laenge: float` – Die Einwirkung als Abstand vom Ursprung.
- `abstand: float` – Kuerzester Abstand zur Resistenzlinie.
- `rand: float` – `laenge + abstand` innerhalb, `laenge - abstand` ausserhalb, nicht unter null -- der Widerstand im normierten Diagramm.

### Auswertung

```python
@dataclass
class Auswertung
```

Ergebnis der Prüfung einer Kombination.

- `schnittgroessen: Schnittgroessen`
- `innerhalb: bool`
- `erfuellungsgrad: float` – Widerstand/Einwirkung -- ab 1 erfuellt. Unendlich, wenn nichts einwirkt.
- `widerstand: Optional[Tuple[float, float]]` – Der massgebende Punkt auf der Linie als (N, M) in N bzw. Nm.
- `begruendung: str = ''`
- `achse: geo.Achse = geo.MOMENT` – Auf welcher Achse verglichen wird. Haengt vom Massstab ab.
- `ed: float = 0.0` – Einwirkung in der verglichenen Groesse, in SI (N bzw. Nm).
- `rd: float = 0.0` – Widerstand in derselben Groesse, in SI.
- `massstab: Erfuellungsart = Erfuellungsart.NORMALKRAFT_KONSTANT` – Welcher Massstab tatsaechlich gegriffen hat.
- `treffer: Optional[Treffer] = None` – Wo auf der Linie der Widerstand liegt -- zwischen welchen Stuetzpunkten, bei der Ebenenlinie auch auf welcher Ebene. Fuer die Mitschrift, damit dort nicht bloss das Ergebnis steht.
- `linie: Optional[Widerstandslinie] = None` – Die Linie, die ihn geliefert hat -- sie schreibt, wie.
- `normierung: Optional[Normierung] = None` – Nur beim kuerzesten Abstand: dort ist der Grad kein Verhaeltnis von Momenten, sondern von Laengen im normierten Diagramm.

### BiegungNormalkraft

```python
class BiegungNormalkraft(Nachweis)
```

Nachweis der Biege- und Normalkrafttragfaehigkeit über die M-N-Interaktion.

Erzeugt für jede Kombination einen Erfüllungsgrad und ein Urteil. Gemessen
wird gegen die Linie der Wahl ([[opencivil.nachweis.biegung_normalkraft#BiegungNormalkraft|massgebend]]); die andere
([[opencivil.nachweis.biegung_normalkraft#BiegungNormalkraft|vergleich]]) steht im Diagramm daneben.

- `THEMA = 'Biegung und Normalkraft'`

#### BiegungNormalkraft.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### BiegungNormalkraft._linie

```python
def _linie(self, wahl: Rechenwahl, e: Eingaben, p: Protokoll) -> Widerstandslinie
```

Die Resistenzlinie einer Wahl -- und ihre Herleitung in `p`.

#### BiegungNormalkraft.handlinie

```python
@property
def handlinie(self) -> List[Eckpunkt]
```

Die Eckpunkte der Handrechnung, ob massgebend oder Vergleich -- sonst leer.

#### BiegungNormalkraft.linie

```python
@property
def linie(self) -> List[Linienpunkt]
```

Die Punkte der Linie aus Dehnungsebenen, ob massgebend oder Vergleich.

#### BiegungNormalkraft.moment_bei

```python
def moment_bei(self, N_Ed: float, positiv: bool) -> Optional[float]
```

Der Momentenwiderstand bei dieser Normalkraft, auf der gewaehlten Seite.

Fuer beliebige Normalkraefte, nicht nur die der Kombinationen: die
Querkraftkurve laesst den Benutzer ein N_Ed einstellen und braucht dann
den passenden Widerstand. Beide Seiten der Linie sind moeglich --
positiv (Zug unten) und negativ (Zug oben).

`None`, wenn die Normalkraft ausserhalb der Resistenzlinie liegt.

:param N_Ed: Normalkraft in N, Zug positiv.
:return: Moment in Nm, Betrag der gewaehlten Seite.

#### BiegungNormalkraft.widerstand_bei_n

```python
def widerstand_bei_n(self, kombination: str) -> Optional[Auswertung]
```

Der Momentenwiderstand bei der Normalkraft dieser Kombination.

Liegt erst nach dem Lauf vor. Der Querkraftnachweis darf sich darauf
verlassen: er fuehrt `d_m_rd` als Eingang, und damit steht die
Reihenfolge im Graphen statt in einer Annahme.

#### BiegungNormalkraft._als_wert

```python
def _als_wert(self, auswertung: Auswertung, seite: str)
```

Verpackt Einwirkung bzw. Widerstand als darstellbaren Wert.

Welche Groesse verglichen wird, haengt vom Massstab ab -- bei
'Normalkraft konstant' das Moment, bei 'Moment konstant' die Normalkraft.
Das Urteil traegt deshalb Symbol und Einheit selbst mit sich. Beim
kuerzesten Abstand sind es Laengen im normierten Diagramm -- sonst
stuenden zwei Momente da, deren Quotient nicht der Grad ist.

#### BiegungNormalkraft._auswerten

```python
def _auswerten(self, kombination: Schnittgroessen, eckwerte: Mapping[str, float]) -> Auswertung
```

Bestimmt den Erfuellungsgrad einer Kombination.

Gemessen wird gegen die massgebende Linie -- damit die Zahl im Urteil
dieselbe ist, die in der Herleitung steht.

Bei `AUTOMATISCH` werden **beide** Wege gerechnet -- der
Momentenwiderstand bei festgehaltener Normalkraft und der
Normalkraftwiderstand bei festgehaltenem Moment -- und der kleinere
Erfuellungsgrad gilt. Vorher entschied eine Schwelle am Anteil der
Grenznormalkraft, in welcher Richtung gemessen wird; das war eine
Faustregel, die nahe den Spitzen der Linie den groesseren der beiden
Werte stehen lassen konnte.

Der Vergleich erscheint **nicht** in der Mitschrift. Er ist kein
Rechenschritt, sondern die Festlegung, in welcher Richtung gemessen
wird; was dann gerechnet wurde, steht vollstaendig da.

#### BiegungNormalkraft._messen

```python
def _messen(self, kombination: Schnittgroessen, achse: geo.Achse, innerhalb: bool) -> Optional[Auswertung]
```

Widerstand auf einer Achse, bei festgehaltener Gegenachse.

Waagrecht und senkrecht sind derselbe Vorgang mit vertauschten Achsen --
deshalb eine Methode. Die Einwirkung wird dafuer als Punkt derselben
Ebene gelesen; damit fallen die Sonderfaelle weg.

#### BiegungNormalkraft._naechster

```python
def _naechster(self, kombination: Schnittgroessen, eckwerte: Mapping[str, float], innerhalb: bool) -> Auswertung
```

Kuerzester Abstand, im auf die Eckwerte normierten Diagramm -- zum
Polygon der massgebenden Linie. Bei der Linie aus Dehnungsebenen ist
das ihr gezeichneter Rand: der naechste Punkt ist eine Frage der
Geometrie, nicht eines Bruchzustands.

#### BiegungNormalkraft._normiert

```python
def _normiert(self, auswertung: Auswertung) -> Tuple[Wert, Wert]
```

Einwirkung und Widerstand im normierten Diagramm -- fuer Tabelle und Herleitung.

#### BiegungNormalkraft._protokoll_naechster

```python
def _protokoll_naechster(self, p: Protokoll, auswertung: Auswertung, eckwerte: Mapping[str, float], basis: str) -> Tuple[Wert, Wert]
```

Der kuerzeste Abstand, Schritt fuer Schritt -- und daraus Einwirkung und
Widerstand im normierten Diagramm, deren Quotient der Grad ist.

### linienbezuege

```python
def linienbezuege(querschnitt: Plattenquerschnitt, posten, richtung: Richtung, satz: Werkstoffsatz) -> List[Eingabebezug]
```

Was eine Resistenzlinie dieser Richtung braucht -- unter den Namen, die
[[opencivil.nachweis.biegung_normalkraft#resistenzlinie|resistenzlinie]] liest: die Festigkeiten des Wertesatzes, `f_cd`
und `f_yd` oder `f_ck` und `f_yk`, `E_cm` fuer die Parabel, die
Bewehrung dieser Richtung und je Stahlsorte ihre Kennwerte.

### resistenzlinie

```python
def resistenzlinie(wahl: Rechenwahl, e: Eingaben, p: Protokoll, *, querschnitt: Plattenquerschnitt, posten, richtung: Richtung, basis: str, schritte: int=dehnungsfaecher.SCHRITTE, fasern: int=dehnungsfaecher.FASERN, vorsatz: str='', ebene: int=2, wahltitel: str='Rechenwahl') -> Widerstandslinie
```

Die Resistenzlinie einer Wahl aus den Eingaben von [[opencivil.nachweis.biegung_normalkraft#linienbezuege|linienbezuege]]
-- und ihre Herleitung in `p`: unter ihrem Titel zuerst, womit sie
rechnet, dann wie sie entsteht. Die Tragsicherheit baut so ihre Linie,
das Knicken seine, wenn es anders waehlt.

### gleiche_linie

```python
def gleiche_linie(a: Rechenwahl, b: Rechenwahl) -> bool
```

Ob zwei Wahlen dieselbe Resistenzlinie ergeben -- die Kriechzahl zaehlt
nur, wo sie wirkt.

### protokoll_widerstand

```python
def protokoll_widerstand(p: Protokoll, auswertung: Auswertung, titel: str='', *, basis: str) -> None
```

Schreibt, wie der Widerstand auf der Linie gefunden wurde -- die Linie,
die ihn geliefert hat, weiss wie: das Polygon zeigt seine Interpolation,
die Linie aus Dehnungsebenen die Probe ihres Bruchzustands.

Frei und nicht an [[opencivil.nachweis.biegung_normalkraft#BiegungNormalkraft|BiegungNormalkraft]] gebunden: der
Querkraftnachweis rechnet mit dem Momentenwiderstand bei der wirkenden
Normalkraft und muss dieselbe Herleitung zeigen. Zweimal geschrieben
liefe sie frueher oder spaeter auseinander.

### _in

```python
def _in(si_wert: float, achse: geo.Achse) -> str
```

Ein SI-Wert in der Einheit seiner Achse, mit Einheitenzeichen.


## Konstanten

- `ACHSE_ZU = {Erfuellungsart.NORMALKRAFT_KONSTANT: geo.MOMENT, Erfuellungsart.MOME…` – Welche Achse ein Massstab sucht. Die einzige Stelle, an der die beiden Begriffe zusammenkommen -- Erfuellungsart ist fuer die Oberflaeche da, Achse fuer die Geometrie.
- `MASSSTAB = {a.name: m for m, a in ACHSE_ZU.items()}`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.dehnungsfaecher]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.linie]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Bezugsgrösse der Normalkraft]] · `BiegungNormalkraft._protokoll_naechster`
- [[Bezugsgrösse des Moments]] · `BiegungNormalkraft._protokoll_naechster`
- [[Einwirkung im normierten Diagramm]] · `BiegungNormalkraft._protokoll_naechster`
- [[Kürzester Abstand zur Resistenzlinie]] · `BiegungNormalkraft._protokoll_naechster`
- [[Widerstand im normierten Diagramm]] · `BiegungNormalkraft._protokoll_naechster`
