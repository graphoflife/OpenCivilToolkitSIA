---
erzeugt: 60ab72f2749d
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/interaktion.py
> Bruchzustand gezeichneter Querschnitte, auch schief.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/interaktion.py)

## VERANTWORTUNG

Zu einem beliebigen Querschnitt -- Polygone aus verschiedenen Werkstoffen,
Aussparungen, Staebe -- die Dehnungsebenen des Bruchzustands, die
Interaktionslinie und den Widerstand fuer eine Einwirkung (N, M_y, M_z).


## DIE EBENE, SCHRAEG

Die Zugrichtung ist `n = (cos ψ, sin ψ)`, ein Einheitsvektor in der
Querschnittsebene. Mit dem Bezugspunkt S (dem Schwerpunkt) heisst:

```
v = n · (p - S)          Abstand in Zugrichtung
u = t · (p - S)          Lage entlang der Nulllinie, t = (-n_z, n_y)
eps(p) = eps_m + chi · v
```

Fuer eine feste Neigung ψ ist das dieselbe Aufgabe wie bei der Platte: eine
Ebene mit zwei Unbekannten ueber `v`. Darum wird der Querschnitt je ψ in
Streifen quer zu n zerlegt ([[opencivil.querschnitt.interaktion#Richtung|Richtung]]) und mit
[[opencivil.querschnitt.fasern#Faserquerschnitt|Faserquerschnitt]] integriert.


## DIE STREIFEN

Ihre Grenzen fallen auf jede Polygonecke, dazwischen wird gleichmaessig
unterteilt. Zwischen zwei Ecken aendert sich die Breite jedes Polygons linear
-- die Breite in der Streifenmitte mal die Dicke ist also exakt die Flaeche.
Gerechnet wird die Spannung in der Streifenmitte (Mittelpunktsregel). Wo ein
Polygon in einem anderen liegt, ersetzt es dieses: es zaehlt fuer seinen
Werkstoff und wird dem des umgebenden abgezogen.


## DER BRUCHZUSTAND

Jeder Werkstoff hat einen Dehnungsbereich, ueberwacht an seinen aeussersten
Punkten. Beim Beton kommt der C-Punkt dazu (vollstaendig gedrueckt: an der
Stelle `(1 - eps_c1d/eps_c2d) · h` vom gedrueckten Rand hoechstens
`eps_c1d`). Zusammen begrenzen diese Grenzen in `(eps_m, chi)` ein
konvexes Vieleck ([[opencivil.querschnitt.fasern#Dehnungsgrenzen|Dehnungsgrenzen]]).
Sein Rand mit `chi >= 0` ist der Dehnungsfaecher: vom gleichmaessigen Zug
ueber die Drehung um den gezogensten Stab, dann um den gedrueckten Rand, dann
um den C-Punkt, bis zum gleichmaessigen Druck -- fuer jede Form, ohne dass ein
Abschnitt benannt wird. Auch die Platte rechnet so, als Rechteck mit je Lage
einem Stab ([[opencivil.nachweis.rechenwahl#Gesetze.querschnitt|querschnitt]]). Bis
2026-11-20 fuhr sie dieselben drei Abschnitte in einem eigenen Faecher ab,
mit eigenen Grenzen und eigenen Fasern.


## DIE FLAECHE DER WIDERSTAENDE

Alle Bruchzustaende zusammen bilden im Raum (N, M_y, M_z) eine geschlossene
Flaeche; jeder Faecher ist eine Linie darauf. Ein Interaktionsdiagramm ist ein
Schnitt durch sie, bei festem N, M_y oder M_z -- das liest nur ein Bild, und
es steht in [[opencivil.querschnitt.widerstandsflaeche]].


## DER WIDERSTAND EINER EINWIRKUNG

Bei festem N und fester Richtung des Moments: auf dem Faecher der Neigung ψ
der Punkt mit `N = N_Ed` -- und ψ so, dass sein Moment in die Richtung von
`(M_y,Ed, M_z,Ed)` zeigt. Bei einem doppelt symmetrischen Querschnitt steht
die Nulllinie dann senkrecht zum Moment; bei einem L nicht, und genau das ist
die schiefe Biegung.


## VORZEICHEN (wie in der ganzen Querschnittsanalyse)

```
N > 0     Zug
M_y > 0   Zug unten      M_y = -Σ F·(z - z_S)
M_z > 0   Zug links      M_z = -Σ F·(y - y_S)
```
Ein positives Moment zieht also auf der negativen Seite seiner Achse.


## EINHEITEN

SI-Basis: Meter, Quadratmeter, Pascal, Newton.

## Inhalt

### Werkstoff

```python
@dataclass(frozen=True)
class Werkstoff
```

Ein Werkstoff, wie die Interaktion ihn braucht: Gesetz und Grenzen.

- `name: str`
- `gesetz: Gesetz`
- `eps_min: float` – Groesste zulaessige Stauchung, negativ.
- `eps_max: float` – Groesste zulaessige Dehnung; `inf` beim Beton, der im Zug nichts traegt.
- `c_punkt: Optional[Tuple[float, float]] = None` – `(eps_c1d, eps_c2d)` beim Beton: die Regel fuer den ganz gedrueckten Querschnitt. Sonst nichts.
- `verdraengbar: bool = False` – Ob ein Stab ihn an seiner Stelle ersetzt -- beim Beton ja.
- `grenzname: str = ''` – Wie seine Dehnungsgrenze heisst, wo er nur an einer Stelle liegt -- ein Spannglied hat seinen eigenen Werkstoff ([[opencivil.querschnitt.spannglieder]]) und heisst wie das Glied. Leer: «Beton C30/37, Rand oben», «Stahl B500B, äusserste Lage unten».
- `wort: str = 'Stahl'` – Was er ist, vor seinem Namen in der Dehnungsgrenze: «Beton», «Holz», «Baustahl» -- ein Stab bleibt «Stahl». Bis 2026-11-26 hiess jeder Werkstoff ausser dem Beton «Stahl», auch eine Flaeche aus Holz.

### Teil

```python
@dataclass(frozen=True)
class Teil
```

Ein Polygon des Querschnitts, Punkte in Metern.

- `punkte: Tuple[Punkt, ...]`
- `werkstoff: Optional[int]` – Index in die Werkstoffe; `None` fuer eine Aussparung.
- `eltern: Optional[int]` – Das Polygon, in dem es liegt und das es dort ersetzt.

### Bewehrung

```python
@dataclass(frozen=True)
class Bewehrung
```

Ein Stab -- oder ein Stueck einer verschmierten Stablinie.

- `lage: Punkt`
- `flaeche: float`
- `werkstoff: int`
- `verdraengt: Optional[int] = None` – Der Werkstoff, in dem der Stab liegt und den er dort ersetzt.
- `grenzpunkte: Tuple[Punkt, ...] = ()` – Wo seine Dehnungsgrenze ueberwacht wird. Leer: an der Stablage. Ein Stueck einer Linie meldet die Linienenden, damit die Grenze am Ende der Linie gilt und nicht erst in der Mitte ihres letzten Stuecks.
- `dicke: Optional[float] = None` – Ueber welche Tiefe der verdraengte Werkstoff gemittelt wird, wenn sein Gesetz springt. Ohne Angabe ein Quadrat gleicher Flaeche; die Lage einer Platte ist ein Band ueber die ganze Breite, so dick wie ihr Stahl darauf verschmiert.

### linie_als_bewehrung

```python
def linie_als_bewehrung(von: Punkt, bis: Punkt, flaeche: float, werkstoff: int, verdraengt: Optional[int]) -> List[Bewehrung]
```

Eine verschmierte Stablinie als Folge kurzer Stuecke.

Die Dehnung aendert sich entlang der Linie linear; jedes Stueck sitzt in
der Mitte seines Abschnitts (Mittelpunktsregel) und traegt seinen Anteil
der Flaeche. Die Grenze gilt an beiden Linienenden.

### Bruchpunkt

```python
@dataclass(frozen=True)
class Bruchpunkt
```

Eine Dehnungsebene des Faechers und was sie erzeugt.

- `psi: float` – Neigung der Zugrichtung, im Bogenmass.
- `eps_m: float` – Dehnung im Bezugspunkt.
- `chi: float` – Kruemmung in Zugrichtung, 1/m, nie negativ.
- `N: float`
- `M_y: float`
- `M_z: float`

#### Bruchpunkt.zugrichtung

```python
@property
def zugrichtung(self) -> Punkt
```

#### Bruchpunkt.moment

```python
@property
def moment(self) -> float
```

Betrag des Moments.

### Kraftanteil

```python
@dataclass(frozen=True)
class Kraftanteil
```

Was ein Werkstoff oder ein Stab zum Bruchzustand beitraegt.

- `name: str`
- `N: float`
- `y: float` – Angriffspunkt, absolut; bei N = 0 der Bezugspunkt.
- `z: float`
- `eps: Optional[float] = None` – Dehnung -- nur bei einem Stab, beim Beton haengt sie am Ort.
- `sigma: Optional[float] = None`

### Richtung

```python
@dataclass
class Richtung
```

Der Querschnitt fuer eine Neigung ψ der Zugrichtung, fertig zum Integrieren.

- `psi: float`
- `n: Punkt`
- `t: Punkt`
- `fasern: Faserquerschnitt`
- `grenzen: Dehnungsgrenzen`
- `gruppen_werkstoff: Tuple[int, ...]` – Je Fasergruppe ihr Werkstoff -- fuer die Aufschluesselung.
- `beton: Optional[Tuple[float, float]]` – Kleinstes und groesstes v des Betons -- fuer x und d.
- `staebe_v: Tuple[float, ...]` – Je Bewehrung ihr v.
- `umriss: Tuple[float, float] = (0.0, 0.0)` – Kleinstes und groesstes v der Flaechen, aus welchem Werkstoff auch immer -- ueber diese Tiefe laeuft das Bild einer Spannung-Dehnung-Analyse. Beim Stahlbeton dasselbe wie [[opencivil.querschnitt.interaktion#Richtung|beton]].
- `fliessgrenzen: Tuple[Dehnungsgrenze, ...] = ()` – Wo eine Flaeche zu fliessen beginnt: je Werkstoff, dessen Gesetz fliesst ([[opencivil.querschnitt.werkstoffgesetz#Gesetz.fliessbereich|fliessbereich]]), an seinen aeussersten Punkten -- dort erreicht eine ebene Dehnung jede Schwelle zuerst. Beim Stahlbeton keine: der Beton fliesst nicht, und den Stahl der Lagen fragt der Fliessbeginn nur auf Zug.

#### Richtung.momente

```python
def momente(self, N: float, M: float, M_quer: float) -> Tuple[float, float]
```

Aus `Σ F·v` und `Σ F·u` die Momente um die Achsen.

Mit `z - z_S = v·n_z + u·n_y` und `y - y_S = v·n_y - u·n_z`:

```
M_y = -(n_z · Σ F·v + n_y · Σ F·u)
M_z = -(n_y · Σ F·v - n_z · Σ F·u)
```

#### Richtung.punkt

```python
def punkt(self, eps_m: float, chi: float) -> Bruchpunkt
```

### Querschnitt

```python
class Querschnitt
```

Ein gezeichneter Querschnitt im Bruchzustand.

`bezug` ist der Punkt, auf den sich N und die Momente beziehen -- in der
Querschnittsanalyse der Schwerpunkt des Bruttoquerschnitts.

#### Querschnitt.richtung

```python
def richtung(self, psi: float) -> Richtung
```

Fasern und Grenzen fuer diese Neigung -- gerechnet einmal je ψ.

#### Querschnitt._grenzen

```python
def _grenzen(self, v_von, n: Punkt) -> Tuple[List[Dehnungsgrenze], Optional[Tuple[float, float]], List[Dehnungsgrenze]]
```

Die Dehnungsgrenzen fuer diese Neigung: je Werkstoff an seinen
aeussersten Punkten, beim Beton dazu die C-Punkte -- jede mit ihrem
Namen und der Seite, auf der sie liegt. Die Seite grosser v ist die,
auf die die Zugrichtung `n` zeigt. Eine Flaeche nennt ihren Rand,
ein Stab seine Lage. Dazu dieselben Stellen einer Flaeche, deren
Gesetz fliesst, mit seinem elastischen Bereich ([[opencivil.querschnitt.interaktion#Richtung|Richtung.fliessgrenzen]]).

#### Querschnitt._knicke

```python
@staticmethod
def _knicke(grenzen: Dehnungsgrenzen, chi_max: float, oben: bool) -> List[float]
```

Wo die massgebende Grenze wechselt, entlang einer Kette des Vielecks.

Die obere Kette ist `min(eps_max - chi·arm)` (der gezogenste Punkt
bestimmt), die untere `max(eps_min - chi·arm)`. Beide sind stueckweise
linear in chi; zurueck kommen die Knicke von 0 bis `chi_max`.

#### Querschnitt.faecher

```python
def faecher(self, psi: float, schritte: int=SCHRITTE) -> List[Bruchpunkt]
```

Die Ebenen des Faechers fuer diese Neigung, von gleichmaessigem Zug
bis zu gleichmaessigem Druck -- je Abschnitt `schritte`
Stuetzstellen, und dazwischen weitere, wo die Linie zwischen zwei
Stuetzstellen merklich von deren Sehne abweicht ([[opencivil.querschnitt.interaktion#Konstanten|FAECHER_SEHNE]])
oder N zu weit springt ([[opencivil.querschnitt.interaktion#Konstanten|FAECHER_LUECKE]]).

Zwei benachbarte Stuetzstellen liegen im selben Abschnitt des
Faechers, und dort ist die Ebene linear in ihren beiden Groessen: die
Mitte zweier Ebenen liegt wieder auf dem Faecher.

#### Querschnitt._dazwischen

```python
def _dazwischen(self, r: Richtung, a: Tuple[float, float], pa: Bruchpunkt, b: Tuple[float, float], pb: Bruchpunkt, dn: float, dm: float, tiefe: int) -> List[Bruchpunkt]
```

Ebenen zwischen zwei Stuetzstellen, durch Halbieren -- bis die Mitte
auf der Sehne liegt, in N gelesen, und N nicht mehr weit springt.

#### Querschnitt.faecherebenen

```python
def faecherebenen(self, psi: float, schritte: int) -> List[Tuple[float, float]]
```

Die Ebenen des Faechers als `(eps_m, chi)`, ohne Verfeinerung: je
Abschnitt `schritte` gleich weit in der Kruemmung, die Knicke
eingeschlossen -- so liegen zwei benachbarte im selben Abschnitt.
Die genaue Linie der Platte zeichnet damit und sucht dazwischen.

#### Querschnitt._auf_kette

```python
@staticmethod
def _auf_kette(r: Richtung, chi: float, oben: bool) -> float
```

Die Dehnung im Bezugspunkt auf der oberen oder unteren Kette.

#### Querschnitt.reine_normalkraft

```python
def reine_normalkraft(self, zug: bool) -> Bruchpunkt
```

Der Bruchzustand bei gleichmaessiger Dehnung -- der groesste Zug oder
der groesste Druck, fuer jede Neigung derselbe. Was jeder Werkstoff
dazu beitraegt, sagt [[opencivil.querschnitt.interaktion#Querschnitt.anteile|anteile]].

#### Querschnitt.normalkraft_grenzen

```python
def normalkraft_grenzen(self) -> Tuple[float, float]
```

Groesste Zug- und groesste Druckkraft ([[opencivil.querschnitt.interaktion#Querschnitt.reine_normalkraft|reine_normalkraft]]).

#### Querschnitt.bei_normalkraft

```python
def bei_normalkraft(self, psi: float, N: float) -> Optional[Bruchpunkt]
```

Die Ebene des Faechers mit `N_int = N`, fuer diese Neigung.

Erst eingegrenzt zwischen zwei Stuetzstellen -- vom Zug her die
erste, zwischen denen N die Seite wechselt --, dann mit dem
Illinois-Verfahren auf der Strecke dazwischen. Zwei benachbarte
Stuetzstellen liegen im selben Abschnitt des Faechers, und dort ist die
Ebene linear in ihren beiden Groessen: die Strecke dazwischen bleibt
auf dem Faecher. `None`, wenn N jenseits der reinen Zug- oder
Druckkraft liegt.

#### Querschnitt.neigung_fuer

```python
@staticmethod
def neigung_fuer(M_y: float, M_z: float) -> float
```

Die Zugrichtung, die zu einem Moment gehoert, wenn der Querschnitt
symmetrisch waere: das Moment `(M_y, M_z)` zieht auf der Seite
`-(sin φ, cos φ)`. M_y > 0 zieht unten, M_z > 0 links.

#### Querschnitt.in_richtung

```python
def in_richtung(self, N: float, M_y: float, M_z: float) -> Optional[Bruchpunkt]
```

Der Bruchzustand bei dieser Normalkraft, dessen Moment in die Richtung
von `(M_y, M_z)` zeigt.

Die Richtung φ des Moments nimmt ab, wenn die Zugrichtung ψ zunimmt --
bei Symmetrie ist `φ = -90° - ψ`. Gesucht wird von der Neigung aus,
die bei Symmetrie gaelte ([[opencivil.core.suche#winkel_suchen|winkel_suchen]]).
`None`, wenn N jenseits der reinen Zug- oder Druckkraft liegt.

#### Querschnitt.anteile

```python
def anteile(self, punkt: Bruchpunkt) -> List[Kraftanteil]
```

Was jeder Werkstoff und jeder Stab zu diesem Bruchzustand beitraegt --
fuer die Probe in der Herleitung.

Der Werkstoff als Resultierende mit Angriffspunkt, jeder Stab mit
Dehnung, Spannung und Kraft. Die Summe der Kraefte ist N, die Summe
der Momente M_y und M_z -- das laesst sich von Hand nachrechnen.

#### Querschnitt.dehnung

```python
def dehnung(self, punkt: Bruchpunkt, p: Punkt) -> float
```

Die Dehnung dieser Ebene an einem Ort des Querschnitts.

#### Querschnitt.zugbewehrung

```python
def zugbewehrung(self, punkt: Bruchpunkt) -> List[Tuple[float, Bewehrung]]
```

Die Zugbewehrung dieser Ebene, je Stab mit seinem v: die gedehnten
Staebe auf der gezogenen Seite des Schwerpunkts.

Die Frage der Platte nach der gezogenen Lage, fuer jede Form. Ein
gedehnter Stab auf der anderen Seite liegt nur knapp jenseits der
Nulllinie -- etwa die obere Bewehrung bei Zug unten -- und ist keine
Zugbewehrung. Und ohne obere Bewehrung haelt bei Zug oben nur der Stahl
unten dagegen, kurz ueber dem gedrueckten Rand: das geht rechnerisch
auf, sagt aber weder ueber Duktilitaet noch ueber sproedes Versagen
etwas.

#### Querschnitt.druckzone

```python
def druckzone(self, punkt: Bruchpunkt) -> Tuple[float, float]
```

Druckzonenhoehe x und statische Hoehe d dieser Ebene, beide senkrecht
zur Nulllinie und ab dem gedrueckten Betonrand gemessen.

d reicht bis zum Schwerpunkt der Zugbewehrung ([[opencivil.querschnitt.interaktion#Querschnitt.zugbewehrung|zugbewehrung]]),
wie das Zeichen d in SIA 262:2025 definiert ist. Ohne Zugbewehrung ist
d null, ohne Beton beides null.


## Konstanten

- `STREIFEN = 200` – Streifen ueber die Tiefe des Querschnitts in Zugrichtung, mindestens. Die Grenzen fallen zusaetzlich auf jede Ecke. Mit 200 rechnet auch die genaue Linie der Platte ([[opencivil.nachweis.resistenzlinie#Ebenenlinie|Ebenenlinie]]); die Loeser nehmen weniger ([[opencivil.querschnitt.fasern#Konstanten|FASERN]]).
- `SCHRITTE = 24` – Stuetzstellen je Abschnitt des Faechers fuer die Zeichnung.
- `FAECHER_SEHNE = 0.001` – Wie weit die Linie eines Faechers hoechstens von der Sehne zwischen zwei Stuetzstellen abweichen darf -- als Teil des groessten Moments. Gleichmaessig in der Kruemmung verteilt, liegen die Stuetzstellen dort weit auseinander, wo die Nulllinie den Rand erreicht: N sprang am Unterzug zwischen zwei Stellen von -1762 auf -3267 kN, und die Linie dazwischen war eine Sehne.
- `FAECHER_LUECKE = 0.05` – Wie weit zwei Stuetzstellen in N hoechstens auseinanderliegen, als Teil der ganzen Spanne -- auch wo die Linie gerade ist, damit ein Ablesen bei einem N zwischen ihnen nicht ueber einen Knick hinweg greift.
- `FAECHER_TIEFE = 8` – Wie oft eine Luecke im Faecher hoechstens halbiert wird.
- `SUCHSCHRITTE = 4` – Stuetzstellen je Abschnitt, um die Stelle `N = N_Ed` einzugrenzen. Wenige genuegen: innerhalb eines Abschnitts aendert sich N glatt, und das Illinois-Verfahren findet die Stelle danach in wenigen Schritten.
- `EPS_ZUG_OHNE_GRENZE = 0.045` – Groesste Zugdehnung, wo kein Werkstoff eine nennt -- ein Querschnitt ganz ohne Bewehrung. Beton traegt keinen Zug; die Grenze legt nur fest, wo der Faecher beginnt.
- `WINKEL_SCHRANKE = 1e-07` – Wann zwei Richtungen des Moments als gleich gelten, im Bogenmass. Ein Zehnmillionstel verschiebt den Widerstand um weniger, als je gedruckt wird.
- `LINIENSTUECK = 0.02` – Teile einer verschmierten Stablinie: alle so viele Meter ein Stueck.

## Braucht

- [[opencivil.core.suche]]
- [[opencivil.querschnitt.fasern]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.gebrauchsebene]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.pfahl.innen]]
- [[opencivil.pfahl.innen_quer]]
- [[opencivil.pfahl.quer]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.bewehrungselemente]]
- [[opencivil.querschnitt.spannglieder]]
- [[opencivil.querschnitt.widerstandsflaeche]]
- [[opencivil.spannungsanalyse.schnitt]]
- [[opencivil.stahlbau.widerstand]]
