---
erzeugt: 39754a6a246e
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/stellen.py
> die massgebenden Stellen eines Balkensystems fuer einen Querschnitt.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/stellen.py)

## VERANTWORTUNG

Aus dem Befund eines ebenen oder raeumlichen Balkensystems je Kombination
die Stellen, an denen die Schnittgroessen einer Gruppe von Staeben
massgebend sind ([[opencivil.stabwerk.stellen#massgebende_stellen|massgebende_stellen]]) – fuer die Nachweise einer
Querschnittsanalyse, deren Querschnitt diese Staebe haben (Plan vom
2026-11-27, Schritt 12). Dazu ihre Herleitung ([[opencivil.stabwerk.stellen#Stellenherleitung|Stellenherleitung]]).


## DIE STELLEN

Je Kombination und ueber alle gewaehlten Staebe zusammen: das groesste und
das kleinste M_y, M_z und N, das groesste \|V_z\|, \|V_y\| und \|T\|
([[opencivil.stabwerk.stellen#Konstanten|KRITERIEN]]) – je mit den uebrigen Schnittgroessen an derselben
Stelle. Springt dort etwas, gilt jede Seite, auf der die Schnittgroesse
ihren Extremwert hat – unter einer Einzellast beim groessten Moment also
beide –, und der Name sagt sie. Was ueberall null ist, gibt
keine Stelle – in der Ebene M_z, V_y und T –, und eine Stelle, die
mehreres zugleich ist, steht einmal da, mit allen Gruenden. Bei gleichen
Werten gilt die vorderste Stelle des ersten Stabs
([[opencivil.stabwerk.verlauf#grenzwerte|grenzwerte]]). Die Folge: die
Kombinationen wie im System, darin die Gruende wie in [[opencivil.stabwerk.stellen#Konstanten|KRITERIEN]].


## VORZEICHEN – NACH VORGABE, NICHT NACHGESCHLAGEN

Die Stellen tragen die Vorzeichen der Querschnittsanalyse
([[opencivil.stabwerk.stellen#Konstanten|IN_DER_ANALYSE]]): der Querschnitt vom Anfang des Stabs her gesehen,
seine Unterseite auf der gestrichelten Faser. Dann sind `N`, `V_z`,
`M_y` und `T` die des Stabs ([[opencivil.stabwerk.verlauf|verlauf]]) –
in der Ebene `N`, `V` und `M` von Hand –, `M_z` und `V_y` haben
das andere Vorzeichen: ein positives `M_z` des Stabs zieht an seiner
Seite `+y`, von seinem Anfang her gesehen rechts, das der Analyse links.


## EINHEITEN

SI-Basis: N, Nm, m.

## Inhalt

### grund

```python
def grund(groesse: str, art: str) -> str
```

Wie ein Kriterium in einem Namen heisst: «max M_y», «max \|V_z\|».

### Stelle

```python
@dataclass(frozen=True)
class Stelle
```

Eine massgebende Stelle: wo, warum und die Schnittgroessen dort, mit denen der Analyse.

- `kombination: str`
- `stab: str`
- `x: float` – Wo auf dem Stab, in m ab seinem Anfang.
- `seite: str` – Wo etwas springt, ob die Werte «links» davon gelten, zum Anfang des Stabs hin, oder «rechts» – leer, wo nichts springt.
- `werte: Dict[str, float]` – Je Schnittgroesse ([[opencivil.stabwerk.verlauf#Konstanten|SCHNITTGROESSEN]]) ihr Wert in N oder Nm.
- `gruende: Tuple[str, ...] = field(default=())`

#### Stelle.name

```python
@property
def name(self) -> str
```

Wie sie als Lastfall heisst: «GZT, L3 bei x = 2.50 m», an einem
Sprung «GZT, L3 bei x = 2.50 m links». Warum sie massgebend ist,
sagt die Herleitung.

### massgebende_stellen

```python
def massgebende_stellen(kombinationen: Sequence[Tuple[str, Mapping[str, Stabverlauf]]], staebe: Sequence[str]) -> List[Stelle]
```

Je Kombination – `(Name, je Stab sein Verlauf)` – die massgebenden
Stellen der Staebe `staebe`, siehe Dateikopf. Ein Stab, den eine
Kombination nicht kennt, zaehlt dort nicht.

### _gewaehlt

```python
def _gewaehlt(verlaeufe: Mapping[str, Stabverlauf], groesse: str, art: str) -> Optional[Tuple[str, float, float]]
```

Stab, Stelle und Wert eines Kriteriums ueber alle Staebe – in der Analyse; null: keiner.

### _in_der_analyse

```python
def _in_der_analyse(extrem: Extrem, vorzeichen: int) -> Extrem
```

Kleinster und groesster Wert mit dem Vorzeichen der Analyse.

### _seiten

```python
def _seiten(verlauf: Stabverlauf, x: float, groesse: str, wert: float) -> List[Tuple[str, Dict[str, float]]]
```

Die Schnittgroessen an der Stelle, in der Analyse, je mit ihrer Seite
([[opencivil.stabwerk.stellen#Stelle|Stelle.seite]]): springt dort etwas, jede Seite, auf der
`groesse` den Wert `wert` hat – sonst eine ohne Seite.

### _gleich

```python
def _gleich(a: float, b: float) -> bool
```

Ob zwei Schnittgroessen gleich sind – bis auf [[opencivil.stabwerk.stellen#Konstanten|NULL]] und die Rundung.

### Stellenherleitung

```python
class Stellenherleitung(Prozedur)
```

Woher die Lastfaelle einer Querschnittsanalyse aus einem Balkensystem
kommen: das System, die Staebe, die Regel und je Stelle ihre Werte. Sie
rechnet nichts – die Stellen stehen fest, bevor die Nachweise gebaut
werden, denn die laufen ueber sie. Sie liest den Schwerpunkt des
Querschnitts: dort liegt die Achse des Stabs, und dort wirken auch die
Lastfaelle der Analyse. So steht sie in der Herleitung nach den Werten
des Querschnitts.

- `THEMA = 'Stellen aus dem Balkensystem'`

#### Stellenherleitung.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```


## Konstanten

- `IN_DER_ANALYSE = {'N': 1, 'V_y': -1, 'V_z': 1, 'T': 1, 'M_y': 1, 'M_z': -1}` – Je Schnittgroesse des Stabs ihr Vorzeichen in der Querschnittsanalyse – siehe Dateikopf.
- `KRITERIEN = (('M_y', 'max'), ('M_y', 'min'), ('M_z', 'max'), ('M_z', 'min'), ('N'…` – Welche Stellen massgebend sind, je `(Groesse, Art)`: `max` und `min` der Wert mit Vorzeichen, `betrag` der groesste Betrag – in dieser Folge stehen ihre Gruende.
- `NULL = 0.001` – Was als null gilt, in N und Nm: darunter gibt eine Groesse keine Stelle.
- `SPALTEN = (('N', 'N', 'kN'), ('V_y', 'V_y', 'kN'), ('V_z', 'V_z', 'kN'), ('T', …` – Die Spalten der Tabelle: Groesse, Kopf und Einheit – die Folge der Felder eines Lastfalls.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.sprache]]
- [[opencivil.stabwerk.verlauf]]

## Gebraucht von

- [[opencivil.projekt.aufbau.aus_system]]
