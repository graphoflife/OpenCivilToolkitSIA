---
erzeugt: f5e68dff29af
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/weg.py
> ein Schnitt um die Stütze durch verschiedene Dicken.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/weg.py)

## VERANTWORTUNG

Liegt ein Plattenbereich neben der Stütze, ohne sie zu umschliessen
([[opencivil.durchstanzen.bereiche|.bereiche]]), kann ein Schnitt massgebend sein, der durch verschiedene
Dicken läuft – etwa durch einen dünneren Bereich, wo d kleiner ist.
SIA 262:2025, 4.3.6.2.7 verlangt, alle möglichen Schnitte zu rechnen; es
gilt der schwächste. Hier steht, was an jedem Punkt um die Stütze gilt
([[opencivil.durchstanzen.weg#Karte|Karte]]), wie der schwächste dieser Schnitte gesucht wird
([[opencivil.durchstanzen.weg#Netz|Netz]]), was er ergibt ([[opencivil.durchstanzen.weg#Wegschnitt|Wegschnitt]]) und wie die Herleitung
ihn zeigt ([[opencivil.durchstanzen.weg#schreiben|schreiben]]).


## DER WIDERSTAND


```
V_Rd,c,W = τ_cd · k_e · Σ k_r,i · d_v,i · u_red,i
```

über die Stellen i mit eigenem d – die Platte und jeder Bereich, durch den
der Schnitt läuft: (58) je Stelle, k_r,i nach (59) mit ihrem d und dem ψ der
Stütze ([[opencivil.durchstanzen.stufen|.stufen]]), k_e des ganzen Schnitts.


## NACH VORGABE, NICHT NACHGESCHLAGEN

die Norm regelt diese Schnitte nicht
im Einzelnen:

- Der Schnitt hält an jeder Stelle mindestens 0.5·d_v ihres d von der Stütze,
  wie der Schnitt um sie, und von jedem Bereich, der auf der Druckseite
  weiter vorsteht als die Stelle selbst – wie ausserhalb eines Stützenkopfs
  (Figur 24a).
- In einem Bereich, der auf der Gegenseite dicker ist, gilt sein d nur, wo er
  mindestens 0.5·d_v über die Stelle hinausreicht; sonst endete der Riss
  jenseits seiner Stufe ([[opencivil.durchstanzen.bereiche#Dicken.wirksam|.bereiche.Dicken.wirksam]]).
- Von der Stütze zählt nur, was höchstens 1.5·d_v ihres d von ihren Ecken
  liegt (Figur 23a), wie um sie; an den Ecken der Bereiche zählt alles.
- Gesucht wird auf [[opencivil.durchstanzen.weg#Konstanten|RICHTUNGEN]] Strahlen von der Stützenachse, bis
  [[opencivil.durchstanzen.weg#Konstanten|REICHWEITE]]·d über die Stütze und die Bereiche um sie hinaus. Wo auf
  einem Strahl eine neue Stelle beginnt, liegt ein Knoten, und ein Schnitt
  verbindet je einen Knoten jedes Strahls zu einem Ring. Massgebend ist der
  Ring mit der kleinsten Summe V_Rd,c + q_d·A, der mit der kleinsten Reserve
  ([[opencivil.durchstanzen.weg#Netz.ring|Netz.ring]]). Gesucht wird mit k_e der Stütze; den gefundenen Ring
  wertet [[opencivil.durchstanzen.schnitt|.schnitt]] genau aus, mit seinem k_e.
- Ein Ring, der überall mit demselben d rechnet, ist kein Schnitt durch
  verschiedene Dicken: er ist der Schnitt um die Stütze oder an einer Stufe,
  nur gröber gerechnet, und fällt weg.


## EINHEITEN

SI-Basis; Kräfte in N.

## Inhalt

### Karte

```python
class Karte
```

Was an einem Punkt um die Stütze gilt: wessen d, ob ein Schnitt dort liegen
darf und ob er dort zählt – siehe Dateikopf. Aussparungen zählen mit den
Schatten, die der Schnitt um die Stütze von ihnen hat (Figur 23d); die
genaue Auswertung misst sie am gefundenen Schnitt neu.

#### Karte.in_der_platte

```python
def in_der_platte(self, p: Punkt) -> bool
```

#### Karte.innerster

```python
def innerster(self, p: Punkt) -> Stelle
```

Der innerste Bereich, in dem `p` liegt – auf seinem Rand zählt als darin.

#### Karte.wo

```python
def wo(self, p: Punkt, innerster: Stelle) -> Stelle
```

Wessen d an `p` gilt: ein Bereich auf der Gegenseite nur, wo er d/2 weiter reicht.

#### Karte.abstand_zur_stuetze

```python
def abstand_zur_stuetze(self, p: Punkt) -> float
```

#### Karte.neben_ecke

```python
def neben_ecke(self, p: Punkt, d: float) -> bool
```

Ob `p` höchstens 1.5·d von einer Ecke der Stütze liegt, an ihrer nächsten Seite.

#### Karte.schluessel

```python
def schluessel(self, p: Punkt) -> Optional[Schluessel]
```

Was an `p` gilt – oder nichts, wo ein Schnitt nicht liegen darf.
Ausserhalb der Platte darf er überall liegen und zählt nicht.

#### Karte.stueckschluessel

```python
def stueckschluessel(self, p: Punkt) -> Tuple[Stelle, bool]
```

Was ein Stück des gefundenen Schnitts an `p` braucht: wessen d und ob
die Regel der Ecken es zählen lässt. Platte, Aussparungen und Schatten
prüft die Auswertung selbst ([[opencivil.durchstanzen.schnitt#auswerten|.schnitt.auswerten]]).

### _abstand_zur_box

```python
def _abstand_zur_box(p: Punkt, box: Box) -> float
```

Wie weit `p` vom Rechteck `box` liegt – höchstens so weit wie vom Polygon darin.

### reichweite

```python
def reichweite(dicken: Dicken, um: Sequence[Plattenbereich], stuetze: Stuetzenflaeche) -> float
```

Wie weit die Suche von der Stützenachse reicht, in m: über die Stütze und
die Bereiche um sie hinaus [[opencivil.durchstanzen.weg#Konstanten|REICHWEITE]]·d der Platte.

### neben

```python
def neben(dicken: Dicken, um: Sequence[Plattenbereich], stuetze: Stuetzenflaeche) -> Tuple[Tuple[Plattenbereich, ...], Tuple[Plattenbereich, ...]]
```

Die Bereiche, die die Stütze nicht umschliessen: die nahen, durch die ein
Schnitt um sie laufen kann, und die fernen, ausser [[opencivil.durchstanzen.weg#reichweite|reichweite]].

### Knoten

```python
@dataclass(frozen=True)
class Knoten
```

Ein Punkt auf einem Strahl, wo eine neue Stelle beginnt.

- `p: Punkt`
- `wo: Stelle`
- `d: float`
- `zaehlt: bool`

### Wegstelle

```python
@dataclass(frozen=True)
class Wegstelle
```

Wie viel vom Schnitt an einer Stelle zählt, und ihr d – in m.

- `wo: Stelle`
- `d: float`
- `u_red: float`

### Wegschnitt

```python
@dataclass(frozen=True)
class Wegschnitt
```

Der gefundene Schnitt, genau ausgewertet: was an ihm von der Last abhängt
und je Stelle, was von ihm zählt – die Platte zuerst, dann die Bereiche
nach ihrem Namen.

- `last: Schnittlast`
- `stellen: Tuple[Wegstelle, ...]`
- `wo = NAME` – Wo er liegt, für Sätze: «der Schnitt durch verschiedene Dicken».

#### Wegschnitt.V_Rd_c

```python
def V_Rd_c(self, psi: float, k_g: float, tau_cd: float) -> float
```

Der Widerstand, still – siehe Dateikopf.

### Netz

```python
class Netz
```

Die Knoten auf den Strahlen um die Stütze und je Paar benachbarter Knoten
Länge und Fläche – alles, was nicht von ψ abhängt. [[opencivil.durchstanzen.weg#Netz.ring|ring]] sucht den
schwächsten Ring bei einem ψ, [[opencivil.durchstanzen.weg#Netz.schnitt|schnitt]] wertet ihn aus; beide gelten
für Nachweis und Kennzahl.

`um` sind die Bereiche, die die Stütze umschliessen, `schatten` die der
Aussparungen am Schnitt um sie. `d_v` ist das der Stütze: mit ihm misst
die Auswertung, welche Aussparungen den Schnitt mindern (Figur 23d). `k_e`
ist das am Schnitt um die Stütze – mit ihm wird gesucht.

#### Netz.vollstaendig

```python
@property
def vollstaendig(self) -> bool
```

Ob jeder Strahl einen Knoten hat – sonst schliesst kein Ring.

#### Netz.warum_keiner

```python
@property
def warum_keiner(self) -> str
```

Warum [[opencivil.durchstanzen.weg#Netz.schnitt|schnitt]] keinen Schnitt gibt – für die Herleitung.

#### Netz._kanten

```python
def _kanten(self, k: int) -> Tuple[Tuple[Tuple[float, float], ...], ...]
```

Je Knoten auf Strahl `k` und auf dem nächsten: Länge und Fläche in der Platte.

#### Netz.ring

```python
def ring(self, psi: float, k_g: float, tau_cd: float) -> Optional[Tuple[int, ...]]
```

Je Strahl der Knoten des schwächsten Rings bei `psi` – der mit der
kleinsten Summe V_Rd,c + q_d·A, gesucht mit k_e der Stütze. Bei
gleicher Summe gilt der kürzere. Nichts, wo kein Ring schliesst.

#### Netz._schritt

```python
def _schritt(self, k: int, kosten: List[float], gewichte: List[List[float]], faktor: float, kurz: float) -> Tuple[List[float], List[int]]
```

Von Strahl `k` zum nächsten: je Knoten dort die kleinste Summe und woher sie kommt.

#### Netz.schnitt

```python
def schnitt(self, psi: float, k_g: float, tau_cd: float) -> Optional[Wegschnitt]
```

Der schwächste Schnitt durch verschiedene Dicken bei `psi`, genau
ausgewertet – nichts, wo kein Ring schliesst oder der schwächste
überall mit demselben d rechnet (Dateikopf).

### _strahl

```python
def _strahl(karte: Karte, winkel: float, weit: float, schritt: float) -> List[Knoten]
```

Die Knoten auf einem Strahl: je der erste Punkt, wo eine neue Stelle beginnt.

### _dreieck

```python
def _dreieck(achse: Punkt, a: Punkt, b: Punkt, raender: Sequence[Halbebene]) -> float
```

Die Fläche zwischen der Achse und der Strecke a–b, soweit sie in der Platte liegt.

### _geteilt

```python
def _geteilt(karte: Karte, a: Punkt, b: Punkt) -> List[Tuple[Tuple[Punkt, Punkt], Tuple[Stelle, bool]]]
```

Die Strecke a–b, geteilt, wo sich ändert, wessen d gilt oder ob die Regel
der Ecken zählen lässt – je Teil mit dem, was in ihm gilt.

### schreiben

```python
def schreiben(p: Protokoll, w: Zwischenwerte, e: Eingaben, ws: Wegschnitt, *, d: Wert, h_B: Dict[str, Wert], psi: Wert, k_g: Wert, tau_cd: Wert, k_e_stuetze: Wert, last: str, V_d: Optional[Wert]=None) -> Tuple[Wert, Wert]
```

Der Schnitt durch verschiedene Dicken mit denselben Schritten wie um die
Stütze, dazu je Stelle ihr Teil des Widerstands: zurück kommen die
Querkraft in ihm und sein Widerstand. `d` ist das d der Platte, `h_B`
sind die Dicken der Bereiche, `V_d` die Stützenkraft, wo es nicht die
eingegebene ist (die Kennzahl).

### _stelle_schreiben

```python
def _stelle_schreiben(p: Protokoll, w: Zwischenwerte, e: Eingaben, s: Wegstelle, *, d: Wert, h_B: Dict[str, Wert], psi: Wert, k_g: Wert, tau_cd: Wert, k_e: Wert) -> Wert
```

Was der Schnitt an einer Stelle trägt: (58) mit ihrem d und ihrem Teil des Schnitts.


## Konstanten

- `RICHTUNGEN = 72` – In wie viele Richtungen die Strahlen von der Stützenachse gehen – je 5°.
- `REICHWEITE = 4.0` – Wie weit die Suche über die Stütze und die Bereiche um sie hinaus reicht, in d der Platte.
- `SCHRITT = 0.1` – Wie fein ein Strahl abgetastet wird, in Teilen des kleinsten d.
- `GENAUIGKEIT = 0.0001` – Wie genau eine Grenze auf einem Strahl oder einer Strecke feststeht, in m.
- `TEILUNG = 0.005` – Wie fein die Strecken des gefundenen Schnitts abgetastet werden, bevor sie an den Grenzen der Stellen geteilt werden, in m.
- `NAME = 'durch verschiedene Dicken'` – Wie der Schnitt in Sätzen heisst: «am Schnitt durch verschiedene Dicken».
- `INDEX = Index('W')` – Wie seine Werte heissen: u_{0,W}, V_{Rd,c,W}.
- `REFERENZ = 'SIA 262:2025, 4.3.6.2.7'` – Wo die Norm verlangt, alle Schnitte zu rechnen.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.bereiche]]
- [[opencivil.durchstanzen.herleitung]]
- [[opencivil.durchstanzen.pruefung]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.durchstanzen.kennzahl]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.web.durchstanzdaten]]
