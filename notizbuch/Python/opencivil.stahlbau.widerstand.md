---
erzeugt: 7527dcee9da6
art: modul
tags: [modul]
---
> [!abstract] opencivil/stahlbau/widerstand.py
> was ein Stahlquerschnitt in einem Lastfall aufnimmt.
> Paket [[opencivil.stahlbau]] · [Quelltext](../../opencivil/stahlbau/widerstand.py)

## VERANTWORTUNG

Zu einem Lastfall -- `N`, die Momente `M_y` und `M_z` um den
Bezugspunkt, die Querkraefte `V_y` und `V_z` -- der Widerstand des
gezeichneten Querschnitts nach SIA 263:2013, ohne Herleitung, in N, mm und
N/mm² ([[opencivil.stahlbau.widerstand#rechnen|rechnen]]). Die Herleitung schreibt
[[opencivil.nachweis.qa_stahl]]. Der Reihe nach:

* grosse Querkraft mindert die Bleche, in denen sie steht ([[opencivil.stahlbau.widerstand#abmindern|abmindern]]);
* der plastische Zustand bei `N_Ed` in der Richtung des Moments
  ([[opencivil.querschnitt.plastisch#Starrplastisch.zustand|zustand]]) und der
  elastische, wenn (54) gerade aufgeht -- aus beiden die Klasse jedes Blechs;
* der Widerstand nach der Klasse, als Faktor auf das Moment: plastisch in den
  Klassen 1 und 2, elastisch nach (54) in Klasse 3, am wirksamen Querschnitt
  nach (60) in Klasse 4.


## DER MASSSTAB

Wie beim Stahlbeton ([[opencivil.nachweis.schiefe_biegung]]): die
Normalkraft bleibt, das Moment waechst in seiner Richtung, bis der
Widerstand erreicht ist -- `α = M_Rd/M_Ed`. Ohne Moment `N_Rd/N_Ed`.
Traegt schon die Normalkraft allein nicht, misst `α` sie: um welchen
Faktor sie kleiner sein muesste.


## PLASTISCH, KLASSEN 1 UND 2 (5.1.1.2, 5.1.8)

Die Norm laesst jeden Spannungszustand zu, der im Gleichgewicht ist und
nirgends `f_y` ueberschreitet. Der groesste davon: jede Gruppe ganz
gezogen oder ganz gedrueckt, getrennt an einer geraden Nulllinie. Gesucht
wird die Nulllinie, bei der `N = N_Ed` ist und das Moment in die Richtung
der Einwirkung zeigt -- mit derselben Suche wie beim Stahlbeton
([[opencivil.core.suche#winkel_suchen|winkel_suchen]]); einachsig liegt sie
waagrecht. Das ist das genaue Zusammenwirken, wo (44) bis (48) es naehern:
die Excel-Dateien des Benutzers rechnen mit (44), das auf der sicheren Seite
liegt.


## ELASTISCH, KLASSE 3 (54)

`N/N_Rd + M_y/M_y,Rd + M_z/M_z,Rd ≤ 1` mit `N_Rd = f_y A/γ_M1` (5.2.2)
und den elastischen Momenten bis zur weitesten Faser (52). Liegt der
Schwerpunkt des Querschnitts neben dem Bezugspunkt -- weil die Querkraft
einen Teil genommen hat --, zaehlt dazu `e N` wie in (60).


## AM WIRKSAMEN QUERSCHNITT, KLASSE 4 (60)

`N/A_eff + (M_y + e_z N)/W_y,eff + (M_z + e_y N)/W_z,eff ≤ f_y/γ_M1`, als
Widerstaende geschrieben wie (54): `A_eff` und `e` vom wirksamen
Querschnitt bei Druck -- bei Zug der ganze --, `W_eff` von dem bei Biegung
zur Seite, die das Moment zieht. Ohne Moment (55). Mit mehreren Staehlen
zaehlt je Glied die Gruppe, die zuerst fliesst -- auf der sicheren Seite.
Ein Rundrohr der Klasse 4 rechnet das Werkzeug nicht: SIA 263 nennt dafuer
keine mitwirkende Breite ([[opencivil.stahlbau.widerstand#Fall.rohr_klasse_4|Fall.rohr_klasse_4]]).


## DIE KLASSE JE LASTFALL

nach Vorgabe, nicht nachgeschlagen
`α` je Blech aus der plastischen Nulllinie im Widerstand, `ψ` aus den
elastischen Spannungen, wenn (54) gerade aufgeht -- beide bei der
Normalkraft des Lastfalls, im Zustand, in dem der Querschnitt versagt. Ohne
Moment gleichmaessig gedrueckt oder gezogen. Wo eine frei gezeichnete Flaeche
gedrueckt ist, hoechstens Klasse 3 ([[opencivil.stahlbau.querschnitt]]).


## QUERKRAFT (5.1.5.1, 5.1.7, 5.2.7, 5.3.6.1)

Uebersteigt `V_Ed` die Haelfte von `V_Rd`, zaehlen die Bleche, in denen
die Querkraft steht ([[opencivil.stahlbau.schub#streifen|streifen]]), fuer
Normalkraft und Biegung nur noch mit `1 - (V_Ed/V_Rd)²` -- beim I der Steg
wie in (43), (53) und (61). Nach Vorgabe, nicht nachgeschlagen: dasselbe
fuer jedes Profil und jede Richtung, auch fuer die Normalkraft, und in den
Klassen 3 und 4 statt der Vergleichsspannung (5.2.7, 5.3.7). Plastisch ist
das ein Spannungszustand nach 5.1.1.2: mit `τ = V_Ed/A_v` liesse die
Vergleichsspannung (4.3.5.4) dem Blech `√(1 - (V_Ed/V_Rd)²)` seiner
Fliessgrenze -- mehr als `1 - (V_Ed/V_Rd)²`. Den Querkraftwiderstand
tragen die Profile; `V_Rd` ist ihre Summe, und jedes mindert gleich. In
einem Querschnitt aus Rundrohren zaehlt die Resultierende aus `V_y` und
`V_z` ([[opencivil.stahlbau.widerstand#querkraefte|querkraefte]]).

## Inhalt

### Querkraft

```python
@dataclass(frozen=True)
class Querkraft
```

Die Querkraft eines Lastfalls in einer Richtung und was die Profile in ihr tragen, in N.

- `richtung: str`
- `V_Ed: float`
- `V_Rd: float`
- `resultierend: bool = False` – Ob es die Resultierende ist -- in einem Querschnitt aus Rundrohren ([[opencivil.stahlbau.widerstand#querkraefte|querkraefte]]).

#### Querkraft.symbol

```python
def symbol(self, index: str) -> str
```

`V_{z,Ed}` -- die Resultierende `V_{Ed}`.

#### Querkraft.name

```python
@property
def name(self) -> str
```

Wie sie im Text heisst: «Querkraft in z» oder «resultierende Querkraft».

#### Querkraft.gewicht

```python
@property
def gewicht(self) -> float
```

Was die Bleche der Querkraft fuer Normalkraft und Biegung verlieren:
`(V_Ed/V_Rd)²`, hoechstens eins -- bis zur Haelfte von `V_Rd` nichts.

### querkraefte

```python
def querkraefte(stahl: Stahlquerschnitt, V_y: float, V_z: float, V_Rd: Dict[str, float]) -> List[Querkraft]
```

Die Querkraefte eines Lastfalls, wie nachgewiesen: je Richtung, die einen
Widerstand hat -- in einem Querschnitt aus lauter Rundrohren ihre
Resultierende, denn ein Rundrohr traegt in jeder Richtung gleich; so
rechnen auch die Excel-Dateien des Benutzers. Ohne Profil keine.

### Abgemindert

```python
@dataclass(frozen=True)
class Abgemindert
```

Der Querschnitt fuer Normalkraft und Biegung, wie die Querkraft ihn laesst (Dateikopf).

- `stahl: Stahlquerschnitt`
- `streifen: Tuple[Stueck, ...] = ()` – Was die Querkraft nimmt, je Streifen mit negativem Gewicht -- beim Rundrohr dazu das Loch mit positivem.
- `weg: Dict[Tuple[int, str], float] = field(default_factory=dict)` – Je Teil und Blech, welcher Anteil fuer Normalkraft und Biegung fehlt.

#### Abgemindert.rest

```python
def rest(self, zustand: Blechzustand) -> float
```

Wie viel von einem Blech noch zaehlt -- sein Streifen der wirksamen
Breite nimmt nur diesen Rest.

### abmindern

```python
def abmindern(stahl: Stahlquerschnitt, querkraefte: Sequence[Querkraft]) -> Abgemindert
```

Der Querschnitt ohne das, was die Querkraft je Richtung nimmt -- siehe
Dateikopf. Steht sie in beiden Richtungen im selben Blech -- im
Rundrohr --, nimmt sie zusammen hoechstens das ganze.

### Glied

```python
@dataclass(frozen=True)
class Glied
```

Ein Moment in (54) oder (60): `|λ·a + b|/R` -- `a` das Moment der
Einwirkung, `b = e·N` der Versatz, `R` der Widerstand nach dem
Vorzeichen von `λ·a + b`: `plus` fuer ein positives Moment.

- `achse: str`
- `a: float`
- `b: float`
- `plus: float`
- `minus: float`

#### Glied.widerstand

```python
def widerstand(self, faktor: float) -> float
```

#### Glied.anteil

```python
def anteil(self, faktor: float) -> float
```

### nutzung

```python
def nutzung(n: float, glieder: Sequence[Glied], faktor: float) -> float
```

`n + Σ |λ a + b|/R` -- die linke Seite von (54) und (60).

### skala

```python
def skala(n: float, glieder: Sequence[Glied]) -> Optional[float]
```

Das groesste `λ ≥ 0` mit `n + Σ |λ a + b|/R ≤ 1` -- `None`, wo
schon `λ = 0` nicht reicht. Die Summe ist in `λ` konvex und
stueckweise gerade: gesucht durch Halbieren, bis auf 1e-12 genau.

### Widerstaende

```python
@dataclass(frozen=True)
class Widerstaende
```

Die Widerstaende eines Querschnitts fuer (54) oder (60), in N und N·mm:
`N_zug` und `N_druck` als Betraege, je Zugseite das Moment -- und der
Schwerpunkt, um den die Normalkraft wirkt, bei Zug und bei Druck.

- `N_zug: float`
- `N_druck: float`
- `M: Dict[Zugseite, float]`
- `zug: Punkt`
- `druck: Punkt`

#### Widerstaende.mitte

```python
def mitte(self, N: float) -> Punkt
```

#### Widerstaende.glieder

```python
def glieder(self, N: float, M_y: float, M_z: float, bezug: Punkt, einachsig: bool) -> List[Glied]
```

Die Momente von (54) oder (60) um den Schwerpunkt: `M + e N` mit
`e` gegen den Bezugspunkt.

#### Widerstaende.n

```python
def n(self, N: float) -> float
```

`N/N_Rd` mit dem Widerstand seines Vorzeichens.

### elastische

```python
def elastische(stahl: Stahlquerschnitt, f: Sequence[float]) -> Widerstaende
```

Die Widerstaende von (54): `f_y A` und je Achse `f_y W_el` bis zur weitesten Faser.

### plastische

```python
def plastische(stahl: Stahlquerschnitt, f: Sequence[float]) -> Widerstaende
```

Die Widerstaende der Klassen 1 und 2, je Achse fuer sich: `f_y A` und
je Zugseite `f_y W_pl` bei `N = 0` -- fuer das Zusammenwirken im Stab
([[opencivil.stahlbau.stabilitaet]]).

### Gebogen

```python
@dataclass(frozen=True)
class Gebogen
```

Der wirksame Querschnitt bei Biegung zu einer Seite, in mm und mm⁴.

- `breiten: List[Wirksam]`
- `I: float`
- `abstand: float` – Wie weit die Faser, die zuerst fliesst, von der Nulllinie liegt.
- `gruppe: int` – In welcher Gruppe sie liegt.

### Wirksame

```python
@dataclass(frozen=True)
class Wirksame
```

Der wirksame Querschnitt fuer (60) -- bei Druck und je Zugseite bei Biegung.

- `widerstaende: Widerstaende`
- `druck: List[Wirksam]` – Die mitwirkenden Breiten bei Druck.
- `A_eff: float`
- `biegung: Dict[Zugseite, Gebogen]`

### wirksame

```python
def wirksame(ab: Abgemindert, f: Sequence[float], eps: Sequence[float], seiten: Sequence[Zugseite]) -> Optional[Wirksame]
```

Die Widerstaende von (60) -- `None` mit einem Rundrohr der Klasse 4.

### spannungslinie

```python
def spannungslinie(stahl: Stahlquerschnitt, N: float, M_y: float, M_z: float, bezug: Punkt, einachsig: bool, faktor: float) -> Linie
```

Die Nulllinie der elastischen Spannungen bei `λ`, y und z als
Hauptachsen: `σ = N/A - M_y (z - z_S)/I_y - M_z (y - y_S)/I_z` mit den
Momenten `λ M + e N` um den Schwerpunkt -- einachsig ohne `M_z`.

### Fall

```python
@dataclass
class Fall
```

Was ein Lastfall am Querschnitt ergibt -- siehe Dateikopf. Kraefte in N, Momente in N·mm.

- `N: float`
- `M_y: float`
- `M_z: float`
- `moment: float` – Der Betrag des Moments, das zaehlt ([[opencivil.querschnitt.biegung#Biegung.betrag|betrag]]).
- `querkraefte: Tuple[Querkraft, ...]`
- `abgemindert: Abgemindert`
- `elastisch: Widerstaende`
- `zustaende: List[Blechzustand]`
- `freie: List[Teil]` – Die frei gezeichneten Flaechen, die gedrueckt sind.
- `klasse: int`
- `plastisch: Optional[Zustand] = None`
- `faktor_54: Optional[float] = None`
- `wirksam: Optional[Wirksame] = None`
- `glieder: List[Glied] = field(default_factory=list)` – Die Momente von (54) oder (60), nach der Klasse.
- `alpha: Optional[float] = None` – Der Erfuellungsgrad -- `None`, wo schon die Normalkraft nicht traegt (dann [[opencivil.stahlbau.widerstand#Fall|alpha_N]]) oder ein Rundrohr der Klasse 4 nichts.
- `alpha_N: Optional[float] = None` – Wo die Normalkraft allein nicht traegt: um welchen Faktor sie kleiner sein muesste.

#### Fall.ohne_moment

```python
@property
def ohne_moment(self) -> bool
```

#### Fall.rohr_klasse_4

```python
@property
def rohr_klasse_4(self) -> bool
```

#### Fall.n

```python
@property
def n(self) -> float
```

`N/N_Rd` der Klasse -- in Klasse 4 mit dem wirksamen Querschnitt.

### rechnen

```python
def rechnen(stahl: Stahlquerschnitt, f: Sequence[float], eps: Sequence[float], N: float, M_y: float, M_z: float, querkraefte: Sequence[Querkraft], bezug: Punkt, biegung: Biegung) -> Fall
```

Ein Lastfall am Querschnitt -- siehe Dateikopf. `f` je Gruppe die
Fliessgrenze, mit der gerechnet wird, `eps` ihr `ε`; `M_y` und
`M_z`, wie sie zaehlen ([[opencivil.querschnitt.biegung#Biegung.wirkt|wirkt]]).

### _fall

```python
def _fall(ab: Abgemindert, el: Widerstaende, eps: Sequence[float], N: float, M_y: float, M_z: float, moment: float, querkraefte: Sequence[Querkraft], pl: Linie, linie_el: Linie) -> Fall
```

Der Fall mit seinen Klassen: je Blech an den beiden Nulllinien,
gedrueckte freie Flaechen hoechstens 3.


## Konstanten

- `REFERENZ_PLASTISCH = 'SIA 263:2013, 5.1.1.2; 5.1.8'`
- `REFERENZ_54 = 'SIA 263:2013, 5.2.6, (54); 5.2.2; 5.2.3, (52)'`
- `REFERENZ_60 = 'SIA 263:2013, 5.3.5, (60); 4.5.3'`
- `REFERENZ_55 = 'SIA 263:2013, 5.3.2, (55)'`
- `REFERENZ_QUERKRAFT = 'SIA 263:2013, 5.1.5.1, (43); 5.1.7; 5.2.7; 5.3.6.1'`
- `HALBE_QUERKRAFT = 0.5` – Ab welchem Anteil an `V_Rd` die Querkraft die Bleche mindert, in denen sie steht (5.1.5.1).
- `ROHR_KLASSE_4 = 'Ein Rundrohr der Klasse 4 rechnet das Werkzeug nicht – SIA 263 nennt…` – Warum ein Rundrohr der Klasse 4 nicht gerechnet wird ([[opencivil.stahlbau.widerstand#Fall.rohr_klasse_4|Fall.rohr_klasse_4]]).
- `KEIN_MOMENT = 0.001` – Ab welchem Moment ein Lastfall als Biegung gilt, in N·mm -- wie beim Stahlbeton ([[opencivil.nachweis.schiefe_biegung#Konstanten|KEIN_MOMENT]], dort in Nm).

## Braucht

- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.plastisch]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlbau.schub]]

## Gebraucht von

- [[opencivil.nachweis.qa_blechverbund]]
- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_stahl_stabilitaet]]
- [[opencivil.nachweis.qa_stahl_werte]]
- [[opencivil.nachweis.qa_verbund]]
- [[opencivil.stahlbau.stabilitaet]]
- [[opencivil.verbund.widerstand]]
