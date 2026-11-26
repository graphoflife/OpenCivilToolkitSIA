---
erzeugt: 8336c85812de
art: modul
tags: [modul]
---
> [!abstract] opencivil/erdbeben/ersatzkraft.py
> das Ersatzkraftverfahren nach SIA 261:2020, 16.5.2.
> Paket [[opencivil.erdbeben]] · [Quelltext](../../opencivil/erdbeben/ersatzkraft.py)

## VERANTWORTUNG

Das [[opencivil.erdbeben.ersatzkraft#Gebaeude|Gebaeude]] -- Standort, Verhaltensbeiwerte, Geschosse und
Tragwaende als Vorgaben im Rechenwerk -- und seine Rechnung
[[opencivil.erdbeben.ersatzkraft#Ersatzkraft|Ersatzkraft]]: je Hauptrichtung x und y die Grundschwingzeit, der
Wert des Bemessungsspektrums, die Ersatzkraft und ihre Verteilung auf die
Geschosse und auf die Waende. Ob das Verfahren gilt (16.5.2.1), sagen die
Urteile: je Richtung T_1 \<= 4 T_C (39), mit seinem Erfuellungsgrad, und --
nur wo Grund- oder Aufriss nicht regelmaessig sind -- eines dazu, rot. Was
eines davon verfehlt, gilt fuer das ganze Gebaeude: die Norm verlangt (39) in
beiden Richtungen.

DAS VERFAHREN, je Richtung:

```
W_i  = G_k,i + psi_2,i * Q_k,i                    Gewicht des Geschosses i
EI   = Summe n * eta_EI * E_cm * I                die Waende dieser Richtung
u    = Summe W_i * z_i^2 * (3 H - z_i) / (6 EI)   Kopf des Kragarms unter den W_i
T_1  = 2 * sqrt(u)                                (40), u in m, T_1 in s
S_d  = (31) bis (34)
F_d  = S_d * Summe W_i                            (41)
F_di = z_i * W_i / Summe z_j * W_j * F_d          (42)
V_i  = Summe_(j >= i) F_dj                        unter dem Geschoss i
M_i  = Summe_(j >= i) F_dj * (z_j - z_(i-1))      ebenda; M_1 = M_0 am Fuss
```

Die Waende einer Richtung stehen als ein Kragarm da, eingespannt am Fuss und
so hoch wie das Gebaeude; das Gewicht eines Geschosses wirkt waagrecht auf
der Hoehe seiner Decke, z_i ueber der Einspannung (16.5.2.3). Jede Wand
traegt von Querkraft und Moment am Fuss ihren Anteil an EI.


## DIE WAND IM GRUNDRISS

Ihr Querschnitt kommt aus einer Querschnittsanalyse, gezeichnet in y und z.
Bei 0 Grad liegt y in x des Gebaeudes: eine Kraft in x biegt sie um z, mit
I_z, eine in y mit I_y. Bei 90 Grad ist es umgekehrt ([[opencivil.erdbeben.ersatzkraft#Wandlage.traegheit|Wandlage.traegheit]]),
und im Bild liegt sie um 90 Grad gedreht ([[opencivil.erdbeben.ersatzkraft#Wandlage.im_grundriss|Wandlage.im_grundriss]]).


## NACH VORGABE, NICHT NACHGESCHLAGEN (auch in TODO)

- die Verteilung auf die Waende nach ihrer Biegesteifigkeit;
- nur die Biegung der Waende verformt, weder Schub noch Fundament;
- eta_EI = 0.5 als Anteil der ungerissenen Steifigkeit -- verlangt ist nur
  eine mittlere Steifigkeit bis zum Fliessbeginn (16.5.5.2). Nicht kappa:
  das ist in der Querschnittsanalyse die Kruemmung und in SIA 262:2025 die
  Vergroesserung der Querkraft fuer hoehere Eigenformen (97) (Benutzer,
  2026-11-21);
- g = 10 m/s^2 wie beim Eigengewicht
  ([[opencivil.stabwerk.rechnung#Konstanten|ERDBESCHLEUNIGUNG]]).


## QUELLE

SIA 261:2020: 16.2 (Einwirkung), 16.3 (Bauwerksklassen), 16.5.1 und 16.5.2.
Die Verhaltensbeiwerte stehen in SIA 262:2025, 4.3.9 (Tabellen 14 und 15),
und SIA 263:2013, 4.9.1; die Beiwerte psi_2 in SIA 260:2013, Anhang A.


## EINHEITEN

Alles in SI-Basis; T_1 = 2 * sqrt(u) nimmt u als Zahl in m.

## Inhalt

### duktile_waende

```python
def duktile_waende(richtungen: Sequence[str]) -> str
```

Der Hinweis, wo q duktiles Verhalten heisst: fuer schlanke Tragwaende
gelten dann eigene Bemessungswerte (SIA 262:2025, 4.3.9.4), die diese
Rechnung nicht kennt -- die Kraefte je Wand sind nicht schon die der
Bemessung.

### Erdbebenzone

```python
class Erdbebenzone(Wahl)
```

Die Zone des Standorts (16.2.1) -- sie gibt die Bodenbeschleunigung a_gd.

- `Z1A = 'Z1a'`
- `Z1B = 'Z1b'`
- `Z2 = 'Z2'`
- `Z3A = 'Z3a'`
- `Z3B = 'Z3b'`

#### Erdbebenzone.a_gd

```python
@property
def a_gd(self) -> float
```

Der Bemessungswert der Bodenbeschleunigung in m/s² (16.2.1.2).

### Spektrumwerte

```python
@dataclass(frozen=True)
class Spektrumwerte
```

Was eine Baugrundklasse dem Spektrum gibt (Tabelle 24): S, und T_B, T_C, T_D in s.

- `S: float`
- `T_B: float`
- `T_C: float`
- `T_D: float`

### Baugrundklasse

```python
class Baugrundklasse(Wahl)
```

Die Klasse des Baugrunds (16.2.2, Tabelle 24). Klasse F gibt es hier
nicht: dort braucht es eine spektrale Standortstudie (16.2.2.2).

- `A = 'A'`
- `B = 'B'`
- `C = 'C'`
- `D = 'D'`
- `E = 'E'`

#### Baugrundklasse.werte

```python
@property
def werte(self) -> Spektrumwerte
```

#### Baugrundklasse.erklaerung

```python
@property
def erklaerung(self) -> str
```

Der Baugrund der Klasse, kurz und in eigenen Worten -- fuer den Titel des Schalters.

### Bauwerksklasse

```python
class Bauwerksklasse(Wahl)
```

Die Bauwerksklasse (16.3, Tabelle 25) -- sie gibt den Bedeutungsbeiwert gamma_f.

- `I = 'I'`
- `II = 'II'`
- `III = 'III'`

#### Bauwerksklasse.gamma_f

```python
@property
def gamma_f(self) -> float
```

Der Bedeutungsbeiwert fuer die Tragsicherheit.

#### Bauwerksklasse.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Wandlage

```python
class Wandlage(Wahl)
```

Wie eine Wand im Grundriss liegt: wie in ihrer Querschnittsanalyse gezeichnet oder gedreht.

- `NULL = '0'`
- `NEUNZIG = '90'`

#### Wandlage.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Wandlage.erklaerung

```python
@property
def erklaerung(self) -> str
```

#### Wandlage.traegheit

```python
def traegheit(self, richtung: str) -> str
```

Welches Traegheitsmoment eine Kraft in `richtung` biegt: `I_z` oder `I_y`.

#### Wandlage.im_grundriss

```python
def im_grundriss(self, y: float, z: float) -> Tuple[float, float]
```

Wo der Punkt (y, z) der Querschnittsanalyse im Grundriss liegt, als (x, y).

### Schwingzeit

```python
class Schwingzeit(Wahl)
```

Woher die Grundschwingzeit kommt.

- `WAENDE = 'waende'`
- `HAND = 'hand'`

#### Schwingzeit.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Schwingzeit.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Regelmaessigkeit

```python
@dataclass(frozen=True)
class Regelmaessigkeit
```

Ein Schalter der Regelmaessigkeit: das Feld des Eintrags, wie er heisst,
seine Ziffer und ihre Kriterien in eigenen Worten -- fuer die Maske.

- `feld: str`
- `beschriftung: str`
- `ziffer: str`
- `kriterien: Tuple[str, ...]`

#### Regelmaessigkeit.als_dict

```python
def als_dict(self) -> dict
```

### Geschoss

```python
@dataclass(frozen=True)
class Geschoss
```

Ein Geschoss, von unten gezaehlt: Hoehe und Lasten.

- `name: str`
- `h: Groesse`
- `G_k: Groesse`
- `Q_k: Groesse`
- `psi_2: Groesse`

### Wandquerschnitt

```python
@dataclass(frozen=True)
class Wandquerschnitt
```

Was eine Wand aus ihrer Querschnittsanalyse nimmt: Namen und die Wert-IDs.

- `analyse: str` – Der Name der Querschnittsanalyse.
- `beton: str` – Der Name ihres Betons.
- `I_y: str`
- `I_z: str`
- `I_yz: str`
- `E_cm: str`

### Wand

```python
@dataclass(frozen=True)
class Wand
```

Eine oder mehrere gleiche Tragwaende -- `nummer` ist ihr Platz in der Liste, ab 1.

- `nummer: int`
- `name: str`
- `lage: Wandlage`
- `n: Groesse`
- `eta_EI: Groesse`
- `querschnitt: Wandquerschnitt`

### Gebaeude

```python
@dataclass
class Gebaeude(Rechenobjekt)
```

Ein Gebaeude im Erdbeben: die Eingaben als Vorgaben im Rechenwerk. Die
Geschosse liegen von unten nach oben; `waende` sind nur die, die
rechnen -- ihre Querschnittsanalyse rechnet und hat einen Beton.

- `WAS = 'Gebäude'`
- `name: str`
- `zone: Erdbebenzone`
- `baugrund: Baugrundklasse`
- `bauwerksklasse: Bauwerksklasse`
- `schwingzeit: Schwingzeit`
- `grundriss_regelmaessig: bool`
- `aufriss_regelmaessig: bool`
- `q_x: Groesse`
- `q_y: Groesse`
- `T1_x: Groesse`
- `T1_y: Groesse`
- `geschosse: Sequence[Geschoss]`
- `waende: Sequence[Wand]`
- `praefix: str`
- `definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)`
- `berechnungen: List[Berechnung] = field(default_factory=list, init=False)`

#### Gebaeude.abschnitt

```python
@property
def abschnitt(self) -> Abschnitt
```

Ueberschrift, unter der das Gebaeude in der Herleitung steht.

### Wandanteil

```python
@dataclass(frozen=True)
class Wandanteil
```

Was eine Wand einer Richtung traegt -- je eine von `n` gleichen; SI-Einheiten.

- `nummer: int`
- `name: str`
- `n: int`
- `EI: float` – Die Biegesteifigkeit einer Wand in dieser Richtung, N m².
- `anteil: float` – Ihr Anteil an EI der Richtung -- einer Wand, nicht aller n.
- `V: float` – Die Querkraft am Fuss, N.
- `M: float` – Das Moment am Fuss, N m.

### querkraefte

```python
def querkraefte(kraefte: Sequence[float]) -> Tuple[float, ...]
```

Je Geschoss, von unten, die Querkraft unter ihm: die Kraefte von dort bis oben.

### momente

```python
def momente(kraefte: Sequence[float], z: Sequence[float]) -> Tuple[float, ...]
```

Je Geschoss, von unten, das Moment unter ihm, auf der Hoehe der Decke
darunter: die Kraefte von dort bis oben, je mal ihr Abstand. Am Fuss ist
es das Kippmoment M_0 -- der Kragarm ist dort eingespannt.

### Richtungsbefund

```python
@dataclass(frozen=True)
class Richtungsbefund
```

Was eine Hauptrichtung ergab, in SI-Einheiten. Die Kraefte je Geschoss von unten.

- `richtung: str`
- `T1: float`
- `u: Optional[float]` – Die Auslenkung, aus der T_1 kommt -- `None` bei T_1 von Hand.
- `S_d: float`
- `F_d: float`
- `kraefte: Tuple[float, ...]`
- `M_0: float` – Das Kippmoment am Fuss: die Kraefte mal ihre Hoehe.
- `S_d_1: float`
- `F_d_1: float`
- `M_0_1: float` – Dasselbe mit q = 1.0, fuer Abheben und Kippen (16.5.1.9).
- `EI: float` – Die Biegesteifigkeit aller Waende dieser Richtung, N m² -- null ohne Wand.
- `waende: Tuple[Wandanteil, ...]`

### Erdbebenbefund

```python
@dataclass(frozen=True)
class Erdbebenbefund
```

Was die Rechnung ergab: Hoehen und Gewichte der Geschosse und je Richtung, was gilt.

- `z: Tuple[float, ...]` – Die Hoehe jedes Geschosses ueber der Einspannung, m -- dort wirkt sein Gewicht.
- `W: Tuple[float, ...]` – Die Gewichte, N.
- `richtungen: Tuple[Richtungsbefund, ...]` – Je Richtung, die sich rechnen liess.
- `gruende: Tuple[str, ...] = ()` – Warum das Verfahren nicht gilt -- leer, wo es gilt (16.5.2.1).
- `hinweise: Tuple[str, ...] = ()` – Was die Rechnung grau dazu sagt: je Querschnittsanalyse, deren y und z keine Hauptachsen sind, ein Satz -- und wo q duktiles Verhalten heisst, was das fuer die Waende bedeutet.

#### Erdbebenbefund.zulaessig

```python
@property
def zulaessig(self) -> bool
```

#### Erdbebenbefund.ohne_einwirkung

```python
@property
def ohne_einwirkung(self) -> bool
```

Ohne Gewicht keine Ersatzkraft -- dann rechnet keine Richtung.

### Ersatzkraft

```python
class Ersatzkraft(Nachweis)
```

Das Ersatzkraftverfahren je Hauptrichtung. Die Urteile sagen, ob es gilt
(16.5.2.1): je Richtung T_1 \<= 4 T_C (39), dazu -- nur wo es fehlt -- ein
regelmaessiger Grund- und Aufriss. Die Kraefte stehen im Befund.

- `THEMA = 'Erdbeben'`
- `LANGNAME = 'Ersatzkraftverfahren'`
- `ART = 'T1'`

#### Ersatzkraft.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

### _unregelmaessig

```python
def _unregelmaessig(g: Gebaeude, W: Sequence[float]) -> Tuple[str, ...]
```

Warum das Verfahren nicht gilt, abgesehen von T_1: der Grund- oder der
Aufriss, wie der Benutzer sie angibt -- und das Gewicht, das nach oben
zunimmt, was die Zahlen selbst zeigen.

### Lauf

```python
class Lauf
```

Ein Lauf der Rechnung, mit seinem Protokoll: Standort und Gewichte
einmal, dann je Richtung ([[opencivil.erdbeben.ersatzkraft#Lauf.richtung|richtung]]).

#### Lauf._standort

```python
def _standort(self) -> Dict[str, Wert]
```

a_gd, S, T_B, T_C, T_D, gamma_f und g -- aus den Tabellen der Norm, als Werte.

#### Lauf._gewichte

```python
def _gewichte(self) -> Tuple[List[float], List[float]]
```

Je Geschoss seine Hoehe ueber der Einspannung und sein Gewicht, von unten -- SI.

#### Lauf.hauptachsen

```python
def hauptachsen(self) -> Tuple[str, ...]
```

Je Querschnittsanalyse einer Wand, deren y und z merklich keine
Hauptachsen sind, der Hinweis -- derselbe wie im Raum
([[opencivil.stabwerk.stabquerschnitt#keine_hauptachsen|keine_hauptachsen]]).

#### Lauf.duktil

```python
def duktil(self) -> Tuple[str, ...]
```

Der Hinweis zu duktil bemessenen Waenden ([[opencivil.erdbeben.ersatzkraft#duktile_waende|duktile_waende]]) --
nur mit Wand, und in der Herleitung mit dem q, das ihn ausloest.

#### Lauf.richtung

```python
def richtung(self, r: str) -> Optional[Richtungsbefund]
```

Der Befund einer Richtung -- `None`, wo sich T_1 nicht rechnen laesst.

#### Lauf._steifigkeit

```python
def _steifigkeit(self, r: str) -> Tuple[Optional[Wert], Dict[int, float]]
```

EI aller Waende in `r` -- `None` ohne Wand --, je Wand das EI einer von ihnen in N m².

#### Lauf._schwingzeit

```python
def _schwingzeit(self, r: str, EI: Optional[Wert]) -> Tuple[Optional[Wert], Optional[float]]
```

T_1 von Hand oder aus den Waenden (40) -- ohne Wand keine; dazu u in m.

#### Lauf._spektrum

```python
def _spektrum(self, r: str, T1: Wert, q: Wert, zusatz: str) -> Wert
```

S_d(T_1) nach (31) bis (34), je nach dem Ast, in dem T_1 liegt.

#### Lauf._kraefte

```python
def _kraefte(self, r: str, S_d: Wert) -> Tuple[Wert, List[float], Wert]
```

F_d (41), die Kraefte je Geschoss (42) und das Kippmoment am Fuss.

#### Lauf._waende

```python
def _waende(self, r: str, EI: float, je_wand: Dict[int, float], F_d: float, M_0: float) -> Tuple[Wandanteil, ...]
```

Je Wand ihr Anteil an EI -- und so viel von Querkraft und Moment am Fuss.

#### Lauf._kippen

```python
def _kippen(self, r: str, T1: Wert, F_d: float, M_0: float) -> Tuple[float, float, float]
```

Dasselbe mit q = 1.0 -- fuer Abheben und Kippen (16.5.1.9): F_d, M_0 und S_d.

#### Lauf.zulaessigkeit

```python
def zulaessigkeit(self) -> Tuple[Tuple[NachweisUrteil, ...], Tuple[str, ...]]
```

Die Urteile, ob das Verfahren gilt (16.5.2.1) -- je Richtung T_1 \<= 4 T_C
(39), dazu, nur wo es fehlt, die Regelmaessigkeit -- und alle Gruende,
warum nicht. Wer verfehlt, nennt im Hinweis jeden Grund: das Verfahren
gilt fuer das Gebaeude oder gar nicht.

### angaben

```python
def angaben(gebaeude: Gebaeude, werte: Dict[str, Wert]) -> GleichungBlock
```

Ueber der Tabelle: in der ersten Zeile Standort und Bauwerksklasse, in der
zweiten, was sie geben, und die Verhaltensbeiwerte -- eine Zeile waere
breiter als die rechte Spalte.

### kraefte

```python
def kraefte(befund: Erdbebenbefund) -> TabellenBlock
```

Je Richtung T_1, S_d, F_d und das Kippmoment -- mit q und mit q = 1.0.


## Konstanten

- `SIA = 'SIA 261:2020'`
- `ZIFFER_ZONE = f'{SIA}, 16.2.1.2'`
- `ZIFFER_BAUGRUND = f'{SIA}, Tabelle 24'`
- `ZIFFER_BWK = f'{SIA}, Tabelle 25'`
- `ZIFFER_SPEKTRUM = f'{SIA}, 16.2.4.1'`
- `ZIFFER_GRENZE = f'{SIA}, 16.5.2.1, (39)'`
- `ZIFFER_T1 = f'{SIA}, 16.5.2.3, (40)'`
- `ZIFFER_F_D = f'{SIA}, 16.5.2.4, (41)'`
- `ZIFFER_F_DI = f'{SIA}, 16.5.2.5, (42)'`
- `ZIFFER_KIPPEN = f'{SIA}, 16.5.1.9'`
- `ZIFFER_STEIFIGKEIT = f'{SIA}, 16.5.5.2'`
- `NACH_VORGABE = 'nach Vorgabe, nicht nachgeschlagen'`
- `RICHTUNGEN = ('x', 'y')` – Die Hauptrichtungen des Gebaeudes, in denen gerechnet wird.
- `NICHT_ZULAESSIG = 'nicht zulässig – Antwortspektrenverfahren (16.5.3.1)'` – Was gilt, wo das Ersatzkraftverfahren nicht gilt (16.5.3.1).
- `REGELMAESSIGKEIT = 'Regelmässigkeit'` – Das Urteil, das nur steht, wo Grund- oder Aufriss nicht regelmaessig sind.
- `NICHT_GERECHNET = 'Nicht gerechnet: die Torsion (16.5.2.7), die vertikale Komponente (1…` – Was diese Rechnung nicht kennt -- grau im Ergebnis.
- `Q_NICHT_DUKTIL = 2.0` – Das groesste q fuer nicht-duktiles Verhalten (SIA 262:2025, 4.3.9.2.2, Tabelle 14); wer mehr ansetzt, bemisst duktil (4.3.9.3.5, Tabelle 15) -- und fuer Tragwaende gilt dann 4.3.9.4.
- `ZIFFER_DUKTIL = 'SIA 262:2025, 4.3.9.2.2, Tabelle 14; 4.3.9.3.5, Tabelle 15; 4.3.9.4'`
- `_A_GD = {Erdbebenzone.Z1A: 0.6, Erdbebenzone.Z1B: 0.8, Erdbebenzone.Z2: 1.0, …`
- `_SPEKTRUM = {Baugrundklasse.A: Spektrumwerte(1.0, 0.07, 0.25, 2.0), Baugrundklass…`
- `_BAUGRUND = {Baugrundklasse.A: 'Fels, darüber höchstens 5 m Lockergestein', Baugr…`
- `REGELMAESSIG = (Regelmaessigkeit('grundriss_regelmaessig', 'Grundriss regelmässig', …` – Was der Benutzer bejaht, wenn er Grund- und Aufriss regelmaessig nennt.
- `_Q_HINWEIS = 'Stahlbeton nicht duktil: 1.5 mit Betonstahl A, 2.0 mit B oder C (SIA…` – Was ueber dem Verhaltensbeiwert steht -- die Werte der Normen, in eigenen Worten.
- `VORGABEN = (Gruppe('Verhaltensbeiwert', lambda: tuple((Feld(f'q_{r}', f'q_{r}', …` – Die Vorgaben des Gebaeudes, je Kasten der Herleitung und Karte der Maske ([[opencivil.core.vorgaben]]).
- `GESCHOSS = 'Geschoss'`
- `WAND = 'Wand'`
- `JE_GESCHOSS = (Gruppe(GESCHOSS, lambda: (Feld('h', 'h', M, 'Höhe des Geschosses', 2…` – Die Vorgaben jedes Geschosses, je mit seiner Nummer von unten.
- `JE_WAND = (Gruppe(WAND, lambda: (Feld('n', 'n', EINHEITSLOS, 'Anzahl gleicher W…` – Die Vorgaben jeder Wand, je mit ihrer Nummer in der Liste.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.vorgaben]]
- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.stabquerschnitt]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.projekt.aufbau.erdbeben]]
- [[opencivil.projekt.erdbeben]]
- [[opencivil.web.api]]
- [[opencivil.web.erdbebendaten]]

## Formeln aus diesem Modul

- [[Auslenkung des Dachs]] · `Lauf._schwingzeit`
- [[Bemessungsspektrum (31)]] · `Lauf._spektrum`
- [[Bemessungsspektrum (32)]] · `Lauf._spektrum`
- [[Bemessungsspektrum (33)]] · `Lauf._spektrum`
- [[Bemessungsspektrum (34)]] · `Lauf._spektrum`
- [[Biegesteifigkeit der Wände]] · `Lauf._steifigkeit`
- [[Ersatzkraft]] · `Lauf._kippen`
- [[Ersatzkraft]] · `Lauf._kraefte`
- [[Ersatzkraft eines Geschosses]] · `Lauf._kraefte`
- [[Gewicht des Gebäudes]] · `Lauf.__init__`
- [[Gewicht eines Geschosses]] · `Lauf._gewichte`
- [[Grenze der Grundschwingzeit]] · `Lauf.zulaessigkeit`
- [[Grundschwingzeit]] · `Lauf._schwingzeit`
- [[Kippmoment am Fuss]] · `Lauf._kippen`
- [[Kippmoment am Fuss]] · `Lauf._kraefte`
