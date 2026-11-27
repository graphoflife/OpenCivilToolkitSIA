---
erzeugt: 3246cca23521
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/systeme.py
> woraus die Durchstanzbewehrung besteht.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/systeme.py)

## VERANTWORTUNG

Je System ([[opencivil.durchstanzen.systeme#Durchstanzsystem|Durchstanzsystem]]) die Regeln, nach denen die Bemessung
([[opencivil.durchstanzen.bewehrung#bemessen|.bewehrung.bemessen]]) eine Bewehrung zusammenstellt: welche
Durchmesser es gibt und wie hoch ein Element wird, wie weit die Elemente
einer Leiste vom Rand der gestützten Fläche stehen, der Faktor k_sys
anstelle der 2 in Gleichung (70), der Stahl, und wie ein Vorschlag heisst
und sich erklärt. Gleich für alle Systeme ist die Anordnung um die Stütze
([[opencivil.durchstanzen.bewehrung#leisten_anordnen|.bewehrung.leisten_anordnen]]): Leisten senkrecht zum Rand der
gestützten Fläche, beim zweiten Element höchstens 1.5·d_v auseinander
(SIA 262:2025, 5.5.3.9). Gewählt wird das System an der Stelle; das
Werkzeug sucht darin Durchmesser, Anzahl und Leisten selbst. Bis 2026-11-26
gab es nur ancoPLUS, seit 2026-11-27 auch HALFEN HDB.


## ANCOPLUS ([[opencivil.durchstanzen.systeme#AncoPlus|AncoPlus]])

Doppelkopfanker auf Leisten, mit den Werten des Herstellers
([[opencivil.durchstanzen.produkte|.produkte]]): Typen und Höhen aus der Preisliste, Abstände und k_sys
aus dem Gutachten von 2007 – nach Vorgabe, nicht nachgeschlagen.


## NACH DER NORM ([[opencivil.durchstanzen.systeme#NachNorm|NachNorm]])

Bügel und HALFEN HDB stehen, wie die Norm es verlangt (SIA 262:2025,
5.5.3.8, 5.5.3.9, 5.5.3.12, Tabelle 21): mindestens zwei Reihen, den
Abstand s_1 der Reihen und den Durchmesser höchstens nach Tabelle 21, s_0
kleiner als s_1, und tangential höchstens 1.5·d_v beim zweiten Ring;
Elemente näher als 0.35·d_v zählen nicht. Gewählt sind, nach Vorgabe, nicht
nachgeschlagen:

- das erste Element 0.35·d_v vom Rand, auf 5 mm aufgerundet – so nah, wie
  es noch zählt;
- das zweite bei d_v, auf 5 mm abgerundet, höchstens s_1 weiter – so
  zählen zwei Reihen;
- danach s_1, so gross, wie Tabelle 21 es zulässt, auf 5 mm abgerundet;
- die Durchmesser des Systems bis zur Grenze der Tabelle 21.

In (70) gilt die 2 der Norm: mehr lässt 4.3.6.5.9 nur für Systeme zu, deren
Sicherheit Versuche zeigen, und die halten dafür meist strengere Regeln ein
als die Norm.


## BÜGEL ([[opencivil.durchstanzen.systeme#Buegel|Buegel]])

Senkrechte Bügel, die die Biegebewehrung auf beiden Seiten umfassen. Eine
Leiste ist hier eine Linie von Bügelschenkeln, vom Rand der gestützten
Fläche nach aussen; jeder Schenkel ist ein Element. Die Durchmesser sind die
der Bügelsuche ([[opencivil.material.betonstahl#Konstanten|BUEGELDURCHMESSER]]),
aus B500B; die Höhe ist der ganze Platz zwischen den Überdeckungen.


## HALFEN HDB ([[opencivil.durchstanzen.systeme#HalfenHdb|HalfenHdb]])

Doppelkopfanker auf Leisten wie ancoPLUS, mit den Durchmessern des
Herstellers ([[opencivil.durchstanzen.produkte|.produkte]]). Den Faktor 3.5 in (70) nennt der Hersteller
nach einem Gutachten, das nicht vorliegt, und mit ihm die strengeren
Regeln, die 4.3.6.5.9 dafür verlangt. Darum stehen die Anker nach der Norm,
und es gilt die 2. Die Höhe ist der Platz zwischen den Überdeckungen, auf
5 mm abgerundet – nach Vorgabe, nicht nachgeschlagen: die Unterlage nennt
keine Höhen. Der Stahl ist B500B: die Unterlage nennt B500, und in (67) und
(69) zählen nur f_sd und E_s, für jede Duktilitätsklasse gleich.


## EINHEITEN

SI-Basis, Längen in m.

## Inhalt

### _ab

```python
def _ab(x: float) -> float
```

Auf [[opencivil.durchstanzen.systeme#Konstanten|RASTER]] abgerundet.

### _auf

```python
def _auf(x: float) -> float
```

Auf [[opencivil.durchstanzen.systeme#Konstanten|RASTER]] aufgerundet.

### System

```python
class System(ABC)
```

Die Regeln eines Systems – siehe Dateikopf.

- `NAME: str` – Wie es im Schalter und in der Herleitung heisst.
- `ELEMENT: str` – Ein Element, auch mehrere: «Anker», «Bügelschenkel».
- `ELEMENTEN: str` – Dasselbe im Dativ Mehrzahl: «zwischen zwei äussersten Ankern».
- `VERANKERUNG: str` – Was auf der Druckseite verankert ist und c_v misst: «Ankerköpfe», «Bügel».
- `LEISTEN: str` – Was um die gestützte Fläche steht: «Leisten», «Bügel».
- `LEISTE: str` – Was die Elemente einer Richtung trägt, in der Einzahl: «Leiste», «Linie».
- `FORM: str` – Wie das Bild der Leiste ein Element zeichnet: «kopfanker», ein Schaft mit zwei Köpfen, oder «buegel».
- `ENDEN: str` – Wie die Enden eines Elements heissen – das Bild zeichnet sie schematisch: «Köpfe», «Biegungen».
- `KEINES: str` – Das Urteil, wenn es keines gibt: «Kein ancoPLUS passt in diese Platte.»
- `KEINES_REICHT: str` – Der Hinweis, wenn auch der stärkste Versuch nicht alles erfüllt.
- `STAHL = 'B500B'` – Der Stahl der Elemente – in (67) und (69) gilt seine Fliessgrenze (4.3.6.5.4).
- `ANZAHLEN: range = produkte.ANKER_JE_LEISTE` – Wie viele Elemente eine Leiste tragen kann: bei ancoPLUS die lieferbaren Leisten, bei Bügeln und HDB nach Vorgabe ebenso viele Reihen – mindestens zwei, wie 5.5.3.8 es verlangt.

#### System.elemente

```python
@abstractmethod
def elemente(self, d: float, h_A: float) -> List[Element]
```

Die Elemente, die bei der statischen Höhe d und der Höhe h_A in Frage kommen, dünnste zuerst.

#### System.hoehe

```python
@abstractmethod
def hoehe(self, h: float, c: float, c_v: float) -> float
```

Die Höhe eines Elements zwischen den Überdeckungen c (Zugseite) und c_v (Druckseite).

#### System.hoehentext

```python
@property
@abstractmethod
def hoehentext(self) -> str
```

Wie die Höhe zustande kommt – der Titel ihrer Zeile in der Herleitung.

#### System.abstaende

```python
@abstractmethod
def abstaende(self, d: float, d_v: float, anzahl: int) -> Tuple[float, ...]
```

Die Abstände einer Leiste vom Rand der gestützten Fläche an: zum ersten Element, dann von Element zu Element.

#### System.k_sys

```python
@abstractmethod
def k_sys(self, c_v: float, d: float, ausnahme: bool) -> float
```

Der Faktor anstelle der 2 in Gleichung (70); `ausnahme`: Innenstütze, Wandende, einspringende Ecke.

#### System.k_sys_text

```python
@property
@abstractmethod
def k_sys_text(self) -> str
```

Woher k_sys kommt, für die Herleitung.

#### System.k_sys_titel

```python
@abstractmethod
def k_sys_titel(self, c_v: float, d: float) -> str
```

Der Titel der Zeile von k_sys – mit den Zahlen, nach denen er sich richtet.

#### System.name

```python
@abstractmethod
def name(self, vorschlag: 'Vorschlag') -> str
```

Wie ein Vorschlag heisst – je Länge der Leisten, wie viele es sind.

#### System.regeln

```python
@abstractmethod
def regeln(self, vorschlag: 'Vorschlag', h_A: str, wo: str) -> str
```

Der Satz der Herleitung, der den Vorschlag und seine Regeln nennt; `wo`: «um den Stahlpilz».

#### System.warum_keines

```python
@property
@abstractmethod
def warum_keines(self) -> str
```

Warum es in dieser Platte keines gibt – wenn [[opencivil.durchstanzen.systeme#System.elemente|elemente]] leer bleibt oder keine Leiste Platz findet.

### AncoPlus

```python
class AncoPlus(System)
```

ancoPLUS von AncoTech – siehe Dateikopf und [[opencivil.durchstanzen.produkte|.produkte]].

- `NAME = 'ancoPLUS'`
- `ELEMENT = 'Anker'`
- `ELEMENTEN = 'Ankern'`
- `VERANKERUNG = 'Ankerköpfe'`
- `LEISTEN = 'Leisten'`
- `LEISTE = 'Leiste'`
- `FORM = 'kopfanker'`
- `ENDEN = 'Köpfe'`
- `KEINES = 'Kein ancoPLUS passt in diese Platte.'`
- `KEINES_REICHT = 'Kein ancoPLUS erfüllt alle Bedingungen; gerechnet ist der stärkste V…`
- `STAHL = produkte.STAHL`

#### AncoPlus.elemente

```python
def elemente(self, d: float, h_A: float) -> List[Element]
```

#### AncoPlus.hoehe

```python
def hoehe(self, h: float, c: float, c_v: float) -> float
```

#### AncoPlus.hoehentext

```python
@property
def hoehentext(self) -> str
```

#### AncoPlus.abstaende

```python
def abstaende(self, d: float, d_v: float, anzahl: int) -> Tuple[float, ...]
```

#### AncoPlus.k_sys

```python
def k_sys(self, c_v: float, d: float, ausnahme: bool) -> float
```

#### AncoPlus.k_sys_text

```python
@property
def k_sys_text(self) -> str
```

#### AncoPlus.k_sys_titel

```python
def k_sys_titel(self, c_v: float, d: float) -> str
```

#### AncoPlus.name

```python
def name(self, vorschlag: 'Vorschlag') -> str
```

«12 × ancoPLUS DA3-0215», mit gekürzten Leisten «… + 2 × ancoPLUS DA2-0215».

#### AncoPlus.regeln

```python
def regeln(self, vorschlag: 'Vorschlag', h_A: str, wo: str) -> str
```

#### AncoPlus.warum_keines

```python
@property
def warum_keines(self) -> str
```

### NachNorm

```python
class NachNorm(System)
```

Ein System, das allein die Norm regelt – Bügel und HALFEN HDB; siehe Dateikopf.

- `DURCHMESSER: Tuple[float, ...]` – Die Durchmesser in mm, dünnste zuerst – genommen bis zur Grenze der Tabelle 21.
- `LINIEN: str` – Die Mehrzahl von [[opencivil.durchstanzen.systeme#NachNorm|LEISTE]]: «Linien», «Leisten».

#### NachNorm.elemente

```python
def elemente(self, d: float, h_A: float) -> List[Element]
```

#### NachNorm.abstaende

```python
def abstaende(self, d: float, d_v: float, anzahl: int) -> Tuple[float, ...]
```

#### NachNorm.k_sys

```python
def k_sys(self, c_v: float, d: float, ausnahme: bool) -> float
```

#### NachNorm.k_sys_titel

```python
def k_sys_titel(self, c_v: float, d: float) -> str
```

#### NachNorm.anordnung

```python
def anordnung(self) -> str
```

Die Sätze der Herleitung, wie die Elemente nach der Norm stehen – siehe Dateikopf.

### Buegel

```python
class Buegel(NachNorm)
```

Bügel nach SIA 262:2025, 5.5.3 – siehe Dateikopf.

- `NAME = 'Bügel'`
- `ELEMENT = 'Bügelschenkel'`
- `ELEMENTEN = 'Bügelschenkeln'`
- `VERANKERUNG = 'Bügel'`
- `LEISTEN = 'Bügel'`
- `LEISTE = 'Linie'`
- `LINIEN = 'Linien'`
- `FORM = 'buegel'`
- `ENDEN = 'Biegungen'`
- `KEINES = 'Keine Bügel passen in diese Platte.'`
- `KEINES_REICHT = 'Keine Bügel erfüllen alle Bedingungen; gerechnet ist der stärkste Ve…`
- `DURCHMESSER = BUEGELDURCHMESSER`

#### Buegel.hoehe

```python
def hoehe(self, h: float, c: float, c_v: float) -> float
```

#### Buegel.hoehentext

```python
@property
def hoehentext(self) -> str
```

#### Buegel.k_sys_text

```python
@property
def k_sys_text(self) -> str
```

#### Buegel.name

```python
def name(self, vorschlag: 'Vorschlag') -> str
```

«12 × 3 + 2 × 2 Bügelschenkel ⌀10»: je Länge der Linien, wie viele es sind.

#### Buegel.regeln

```python
def regeln(self, vorschlag: 'Vorschlag', h_A: str, wo: str) -> str
```

#### Buegel.warum_keines

```python
@property
def warum_keines(self) -> str
```

### HalfenHdb

```python
class HalfenHdb(NachNorm)
```

HALFEN HDB von Leviat, angeordnet nach der Norm – siehe Dateikopf und [[opencivil.durchstanzen.produkte|.produkte]].

- `NAME = 'HALFEN HDB'`
- `ELEMENT = 'Anker'`
- `ELEMENTEN = 'Ankern'`
- `VERANKERUNG = 'Ankerköpfe'`
- `LEISTEN = 'Leisten'`
- `LEISTE = 'Leiste'`
- `LINIEN = 'Leisten'`
- `FORM = 'kopfanker'`
- `ENDEN = 'Köpfe'`
- `KEINES = 'Kein HALFEN HDB passt in diese Platte.'`
- `KEINES_REICHT = 'Kein HALFEN HDB erfüllt alle Bedingungen; gerechnet ist der stärkste…`
- `DURCHMESSER = produkte.HDB_DURCHMESSER`

#### HalfenHdb.hoehe

```python
def hoehe(self, h: float, c: float, c_v: float) -> float
```

#### HalfenHdb.hoehentext

```python
@property
def hoehentext(self) -> str
```

#### HalfenHdb.k_sys_text

```python
@property
def k_sys_text(self) -> str
```

#### HalfenHdb.name

```python
def name(self, vorschlag: 'Vorschlag') -> str
```

«12 × HDB ⌀14 mit 3 Ankern + 4 × HDB ⌀14 mit 2 Ankern»: je Länge der
Leisten, wie viele es sind.

#### HalfenHdb.regeln

```python
def regeln(self, vorschlag: 'Vorschlag', h_A: str, wo: str) -> str
```

#### HalfenHdb.warum_keines

```python
@property
def warum_keines(self) -> str
```

### Durchstanzsystem

```python
class Durchstanzsystem(Wahl)
```

Woraus die Durchstanzbewehrung besteht – siehe Dateikopf.

- `ANCOPLUS = 'ancoplus'`
- `HDB = 'hdb'`
- `BUEGEL = 'buegel'`

#### Durchstanzsystem.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Durchstanzsystem.regeln

```python
@property
def regeln(self) -> System
```

Die Regeln dieses Systems.


## Konstanten

- `RASTER = 0.005` – Auf so viel werden Abstände gerundet.
- `SYSTEME = {Durchstanzsystem.ANCOPLUS: AncoPlus(), Durchstanzsystem.HDB: HalfenH…` – Je Stellung ihre Regeln – eine Instanz je System, ohne eigenen Zustand.

## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.durchstanzen.bewehrung]]
- [[opencivil.durchstanzen.produkte]]
- [[opencivil.durchstanzen.pruefung]]
- [[opencivil.material.betonstahl]]

## Gebraucht von

- [[opencivil.durchstanzen.bewehrung]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.web.durchstanzdaten]]
