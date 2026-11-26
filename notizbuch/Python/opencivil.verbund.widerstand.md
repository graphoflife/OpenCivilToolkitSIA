---
erzeugt: f5b2e1c1a826
art: modul
tags: [modul]
---
> [!abstract] opencivil/verbund/widerstand.py
> was ein Verbundquerschnitt in einem Lastfall aufnimmt.
> Paket [[opencivil.verbund]] · [Quelltext](../../opencivil/verbund/widerstand.py)

## VERANTWORTUNG

Zu einem Lastfall -- `N`, die Momente um den Bezugspunkt, die Querkraefte
-- der plastische Widerstand des gezeichneten Verbundquerschnitts nach
SIA 264:2014, ohne Herleitung, in N, mm und N/mm² ([[opencivil.verbund.widerstand#rechnen|rechnen]]); dazu
der Widerstand bei `N = 0` zu einer Seite ([[opencivil.verbund.widerstand#biegewiderstand|biegewiderstand]]). Die
Herleitung schreiben [[opencivil.nachweis.qa_verbund]] und
[[opencivil.nachweis.qa_verbund_kennzahlen]]. Der Reihe nach:

* grosse Querkraft mindert die Bleche, in denen sie steht, wie im Stahl
  ([[opencivil.stahlbau.widerstand#abmindern|abmindern]]): die Querkraft traegt
  der Stahl allein (4.3.2.2);
* der plastische Zustand bei `N_Ed` in der Richtung des Moments, je
  Gruppe mit ihrer Festigkeit: Baustahl `±f_y/γ_a`, Beton gedrueckt
  `0.85 f_ck/γ_c`, gezogen nichts (4.3.2.1), Betonstahl `±f_sk/γ_s`
  (5.1.2.1; 4.1.3);
* ob er gilt: jedes Blech in Klasse 1 oder 2 (4.2.2, Tabelle 2), und wo
  ein Moment Betonstahl zieht, dieser in der Duktilitaetsklasse B oder C
  (5.1.2.3); sonst steht grau, warum nicht ([[opencivil.verbund.widerstand#Fall|Fall.grund]]);
* `β` nach 5.1.2.2, wo ein Baustahl S420 oder S460 ist.


## DER MASSSTAB

Wie beim Stahl ([[opencivil.stahlbau.widerstand]]): `N` bleibt, das
Moment waechst in seiner Richtung, bis der Widerstand erreicht ist --
`α = M_Rd/M_Ed`. Ohne Moment `N_Rd/N_Ed`. Traegt schon die Normalkraft
allein nicht, misst `α` sie.

5.1.2.3 -- nach Vorgabe, nicht nachgeschlagen:
Die Norm nennt den Fall des negativen Moments eines Traegers: die Platte
gezogen. Der Querschnitt weiss nicht, was Platte ist; gefragt wird darum
jeder Betonstahl, den ein Moment zieht. Ohne Moment gilt die Regel nicht.

β (5.1.2.2, Figur 1):
`x_p` ist der Abstand der Nulllinie vom gedrueckten Rand des Betons, `h`
die Hoehe des ganzen Querschnitts quer zu ihr. `β = 1` bis ``x_p/h =
0.15``, dann gerade bis 0.85 bei 0.4. Darueber endet die Figur; das Werkzeug
rechnet dort nicht (nach Vorgabe, nicht nachgeschlagen). Ob ein Baustahl
S420 oder S460 ist, sagt seine Fliessgrenze bis 40 mm Dicke: ab 420 N/mm²
(nach Vorgabe, nicht nachgeschlagen).

## Inhalt

### duktil_text

```python
def duktil_text(namen: Sequence[str]) -> str
```

Warum ein gezogener Betonstahl den plastischen Widerstand verbietet (5.1.2.3).

### Beta

```python
@dataclass(frozen=True)
class Beta
```

`x_p` und `h` nach 5.1.2.2 an einer Nulllinie, in mm -- und was daraus folgt.

- `x_p: float`
- `h: float`

#### Beta.verhaeltnis

```python
@property
def verhaeltnis(self) -> float
```

#### Beta.beta

```python
@property
def beta(self) -> Optional[float]
```

`β` nach Figur 1 -- `None` ueber 0.4, wo sie endet.

### Fall

```python
@dataclass
class Fall
```

Was ein Lastfall am Verbundquerschnitt ergibt -- siehe Dateikopf. In N und N·mm.

- `N: float`
- `M_y: float`
- `M_z: float`
- `moment: float` – Wie gross das Moment ist ([[opencivil.querschnitt.biegung#Biegung.betrag|betrag]]).
- `querkraefte: Tuple[wd.Querkraft, ...]`
- `abgemindert: wd.Abgemindert`
- `starr: Starrplastisch`
- `linie: Linie` – Die plastische Nulllinie -- ohne Moment gleichmaessig gedrueckt oder gezogen.
- `zustaende: List[Blechzustand]`
- `freie: List[Teil]` – Die frei gezeichneten Flaechen aus Baustahl, die gedrueckt sind.
- `klasse: int` – 1, 2 oder 3 fuer «über 2» ([[opencivil.verbund.querschnitt]]).
- `plastisch: Optional[Zustand] = None`
- `beta: Optional[Beta] = None` – Nur mit einem Baustahl S420 oder S460 und gedruecktem Beton.
- `sproede: List[str] = field(default_factory=list)` – Die Namen der gezogenen Betonstaehle, die nicht in Klasse B oder C sind (5.1.2.3).
- `grund: str = ''` – Warum der Fall grau bleibt -- leer, wo er rechnet.
- `alpha: Optional[float] = None`
- `alpha_N: Optional[float] = None` – Wo die Normalkraft allein nicht traegt: um welchen Faktor sie kleiner sein muesste.

#### Fall.ohne_moment

```python
@property
def ohne_moment(self) -> bool
```

#### Fall.faktor_beta

```python
@property
def faktor_beta(self) -> float
```

### _fall

```python
def _fall(verbund: Verbundquerschnitt, ab: wd.Abgemindert, starr: Starrplastisch, eps: Sequence[float], N: float, M_y: float, M_z: float, moment: float, querkraefte: Sequence[wd.Querkraft], linie: Linie) -> Fall
```

Der Fall mit den Klassen an der Nulllinie -- grau, wo ein Blech ueber Klasse 2 liegt.

### sproede_gezogen

```python
def sproede_gezogen(verbund: Verbundquerschnitt, linie: Linie) -> List[str]
```

Die gezogenen Betonstaehle, die nicht in der Duktilitaetsklasse B oder C sind (5.1.2.3).

### _bewerten

```python
def _bewerten(fall: Fall, verbund: Verbundquerschnitt, hochfest: bool) -> None
```

5.1.2.3 und `β` an einem plastischen Zustand mit Moment -- siehe Dateikopf.

### rechnen

```python
def rechnen(verbund: Verbundquerschnitt, zug: Sequence[float], druck: Sequence[float], eps: Sequence[float], N: float, M_y: float, M_z: float, querkraefte: Sequence[wd.Querkraft], bezug: Punkt, biegung: Biegung, hochfest: bool) -> Fall
```

Ein Lastfall am Verbundquerschnitt -- siehe Dateikopf. `zug` und
`druck` je Gruppe die Festigkeiten, `eps` je Gruppe des Stahls sein
`ε`; `M_y` und `M_z`, wie sie zaehlen
([[opencivil.querschnitt.biegung#Biegung.wirkt|wirkt]]); `hochfest`, ob
ein Baustahl S420 oder S460 ist.

### biegewiderstand

```python
def biegewiderstand(verbund: Verbundquerschnitt, zug: Sequence[float], druck: Sequence[float], eps: Sequence[float], seite: Zugseite, bezug: Punkt, hochfest: bool) -> Fall
```

Der Widerstand bei `N = 0` gegen ein Moment, das `seite` zieht --
die Nulllinie parallel zu y oder z. Sein Moment steht in
[[opencivil.verbund.widerstand#Fall|Fall.plastisch]], mit `β` mal [[opencivil.verbund.widerstand#Fall.faktor_beta|Fall.faktor_beta]].


## Konstanten

- `REFERENZ_PLASTISCH = 'SIA 264:2014, 5.1.2.1; 4.1.3'`
- `REFERENZ_KLASSE = 'SIA 264:2014, 4.2.2.1, Tabellen 2 und 3; 5.2.1.3; SIA 263:2013, Tabe…`
- `REFERENZ_BETA = 'SIA 264:2014, 5.1.2.2, Figur 1'`
- `REFERENZ_DUKTIL = 'SIA 264:2014, 5.1.2.3'`
- `REFERENZ_QUERKRAFT = 'SIA 264:2014, 4.3.2.2; SIA 263:2013, 5.1.5.1, (43)'`
- `REFERENZ_SCHUB = 'SIA 264:2014, 4.3.2.2; SIA 263:2013, 5.1.4.1, (41)'`
- `HOCHFEST = 420.0` – Ab welcher Fliessgrenze bis 40 mm ein Baustahl als S420 oder S460 zaehlt, in N/mm².
- `UEBER_KLASSE_2 = 'Ein Blech liegt über Klasse 2: plastisch darf der Verbundquerschnitt…` – Warum ein Fall grau bleibt.
- `UEBER_FIGUR_1 = 'x_p/h liegt über 0.4, wo Figur 1 endet: dort rechnet das Werkzeug de…`

## Braucht

- [[opencivil.material.basis]]
- [[opencivil.material.betonstahl]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.plastisch]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlbau.widerstand]]
- [[opencivil.verbund.querschnitt]]

## Gebraucht von

- [[opencivil.nachweis.qa_verbund]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_werte]]
