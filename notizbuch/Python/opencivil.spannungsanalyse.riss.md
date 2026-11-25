---
erzeugt: 974571889f1c
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/riss.py
> wo eine Linie reisst.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/riss.py)

## VERANTWORTUNG

Der Riss einer Linie -- fuer die Platte und den gezeichneten Querschnitt
dieselbe Rechnung und dieselbe Herleitung ([[opencivil.spannungsanalyse.riss#Bruttoriss|Bruttoriss]]). Gerechnet
wird am ungerissenen Bruttoquerschnitt, ohne Stahl, wie beim sproeden
Versagen ([[opencivil.nachweis.rissgroessen]]):

```python
M_Riss(N) = (f_ct,eff - N/A) · W        W zur Ecke, die unter reiner Biegung zuerst reisst
N_Riss(M) = (f_ct,eff,t - σ_M) · A      σ_M aus M, an der Ecke, die zuerst reisst
```

Unter reiner Biegung mit dem Deviationsmoment `I_yz`, «einachsig» mit
`W = I/v`. `f_ct,eff` mit `k_t` fuer ein Drittel der Tiefe, unter Zug
fuer die rissaktive Dicke; der Beton der Ecke gibt `f_ctm`. Die Platte ist
ein Rechteck `b × h` und immer einachsig: `A = b·h`, `W = b·h²/6`.

Was nur das Paar weiss, schreibt es selbst: woher `A` und `I` kommen --
aus der Querschnittsanalyse oder aus `b` und `h` -- und welche Dicke
unter Zug reisst: beim gezeichneten Querschnitt die kleinere Abmessung
`min(h; b)`, bei der Platte ihre Dicke `h`, denn ihr Streifen `b` ist
keine Abmessung der Platte
([[opencivil.nachweis.rissgroessen#rissaktive_dicke|rissaktive_dicke]]). Bis 2026-11-21
rechnete die Platte ihren Riss selbst, in `b` und `h`:
`M_Riss(N) = M_Riss - N·h/6` -- dieselben Zahlen, aber eine zweite
Rechnung, und ihre Herleitung nannte `M_Riss`, ohne es herzuleiten.


## NACH VORGABE

Der Bruttoquerschnitt ohne Stahl, wie beim sproeden Versagen. Der ungerissene
Zustand daneben rechnet mit Stahl und Kriechzahl und ist darum steifer; beim
Rissmoment steht sein Rand etwas unter `f_ct,eff`. SIA 262:2025 laesst den
Querschnitt reissen, wenn der Beton `f_ctm` oder eine Fraktile erreicht,
ohne `k_t` (4.2.1.14), und rechnet ihn ungerissen mit dem Stahl
(4.1.4.1.4) -- Entscheid des Benutzers offen (`notizbuch/Notizen/TODO.md`).
Das Rissmoment nimmt `k_t` fuer ein Drittel der Tiefe, auch unter Zug; die
Rissnormalkraft die ganze rissaktive Dicke. Beim selben N und M reissen die
beiden Linien darum nicht am selben Punkt.


## EINHEITEN

SI-Basis wie im ganzen Querschnittsmodul.

## Inhalt

### Bruttoriss

```python
class Bruttoriss
```

Der Riss eines Paars am Bruttoquerschnitt: Rechnung und Herleitung, dazu
der reine Betonquerschnitt des aequivalenten Moduls -- derselbe
Querschnitt.

Das Paar gibt den Bruttoquerschnitt (`brutto`) mit seinem Rissmoment
unter reiner Biegung (`riss`), seine Flaeche `A`, die rissaktive
Dicke unter Zug (`t_zug`), die Zugseite (`seite`), den gerissenen
Loeser (`gerissen`) und seine Wahl (`wahl`) -- und zwei Stuecke
Herleitung, die nur es kennt: [[opencivil.spannungsanalyse.riss#Bruttoriss.herleitung_bruttoquerschnitt|herleitung_bruttoquerschnitt]] und
[[opencivil.spannungsanalyse.riss#Bruttoriss.herleitung_dicke_unter_zug|herleitung_dicke_unter_zug]].

- `brutto: Bruttoquerschnitt`
- `riss: Rissmoment`
- `A: float`
- `t_zug: float`
- `seite: Zugseite`
- `gerissen: Faserloeser`
- `wahl: Rechenwahl`
- `ZUR_ANDEREN_ACHSE = ''` – Was die Erklaerung der festen Nulllinie ueber das Moment um die andere Achse sagt -- beim gezeichneten Querschnitt ist «einachsig» eine Wahl; an der Platte, einem Rechteck, entsteht keines.
- `DICKE_UNTER_ZUG = ''` – Welche Dicke unter Zug reisst, in Worten.

#### Bruttoriss.art

```python
@property
def art(self) -> Rechenart
```

Die Rechenart des Betons der Ecke, die zuerst reisst: seine Kennwerte
und sein Gesetz zeigt die Herleitung. Die Platte hat nur ihn.

#### Bruttoriss.betone

```python
@property
def betone(self) -> Tuple[Any, ...]
```

Die Betone des Querschnitts, jeder einmal -- aus den Ecken des Bruttoquerschnitts.

#### Bruttoriss.einachsig

```python
@property
def einachsig(self) -> bool
```

Ob die Nulllinie parallel zur Achse der Biegung bleibt, statt zu kippen.

#### Bruttoriss.I

```python
@property
def I(self) -> float
```

Das Traegheitsmoment um die Achse der Biegung, m⁴.

#### Bruttoriss.W

```python
@property
def W(self) -> float
```

Das Widerstandsmoment zur Ecke, die unter reiner Biegung zuerst reisst, m³.

#### Bruttoriss.M_Riss

```python
@property
def M_Riss(self) -> float
```

Das Rissmoment ohne Normalkraft, in Nm.

#### Bruttoriss.k_t_zug

```python
@property
def k_t_zug(self) -> float
```

`k_t` fuer die rissaktive Dicke unter Zug.

#### Bruttoriss.rissmoment_bei

```python
def rissmoment_bei(self, N: float) -> float
```

`M_Riss(N) = (f_ct,eff - N/A)·W` in Nm, N Zug positiv -- Druck hebt es, Zug senkt es.

#### Bruttoriss.rissnormalkraft

```python
def rissnormalkraft(self, M: float) -> Rissnormalkraft
```

Die Rissnormalkraft beim Moment `M` -- an der Ecke, die zuerst reisst.

#### Bruttoriss.rissnormalkraft_bei

```python
def rissnormalkraft_bei(self, M: float) -> float
```

`N_Riss(M) = (f_ct,eff,t - σ_M)·A` in N -- ein Moment senkt sie, gleich in welche Richtung.

#### Bruttoriss.I_c

```python
@property
def I_c(self) -> float
```

Der reine Betonquerschnitt fuer den aequivalenten Modul: `I` -- kippt
die Nulllinie, `I - I_yz²/I_quer`
([[opencivil.spannungsanalyse.schnitt]], «Der aequivalente Modul»).

#### Bruttoriss.A_c

```python
@property
def A_c(self) -> float
```

Dasselbe fuer die Normalkraft: `A`.

#### Bruttoriss.herleitung_bruttoquerschnitt

```python
def herleitung_bruttoquerschnitt(self, p: Protokoll, w: Zwischenwerte, ein: Callable[[str], 'Wert'], h: 'Wert') -> Tuple['Wert', 'Wert']
```

`A` und `I` als Werte der Herleitung -- woher sie kommen, weiss das Paar.

#### Bruttoriss.herleitung_dicke_unter_zug

```python
def herleitung_dicke_unter_zug(self, p: Protokoll, w: Zwischenwerte, h: 'Wert') -> 'Wert'
```

Die rissaktive Dicke unter Zug, `t` -- wie das Paar sie misst.

#### Bruttoriss.herleitung_riss

```python
def herleitung_riss(self, p: Protokoll, w: Zwischenwerte, linie: 'Linie', ein: Callable[[str], 'Wert'], h: 'Wert') -> Tuple['Wert', 'Wert']
```

Wo die Linie reisst: das Rissmoment bei N oder die Rissnormalkraft bei
M, am Bruttoquerschnitt. Zurueck kommen dessen `A` und `I`, wie die
Herleitung sie nennt -- auf sie bezieht sich der aequivalente Modul.

#### Bruttoriss._herleitung_rissmoment

```python
def _herleitung_rissmoment(self, p: Protokoll, w: Zwischenwerte, linie: 'Linie', ein: Callable[[str], 'Wert'], h: 'Wert', A: 'Wert', W: Optional['Wert']) -> None
```

Das Rissmoment bei der Normalkraft der Linie.

#### Bruttoriss._herleitung_rissnormalkraft

```python
def _herleitung_rissnormalkraft(self, p: Protokoll, w: Zwischenwerte, linie: 'Linie', ein: Callable[[str], 'Wert'], h: 'Wert', A: 'Wert', I: 'Wert', v: Optional['Wert']) -> None
```

Die Rissnormalkraft beim Moment der Linie.

#### Bruttoriss.herleitung_traegheit

```python
def herleitung_traegheit(self, p: Protokoll, w: Zwischenwerte, I: 'Wert') -> 'Wert'
```

Der reine Betonquerschnitt des Moduls ueber dem Moment: der Bruttoquerschnitt.

#### Bruttoriss.herleitung_flaeche

```python
def herleitung_flaeche(self, p: Protokoll, w: Zwischenwerte, A: 'Wert') -> 'Wert'
```

Der reine Betonquerschnitt des Moduls ueber der Normalkraft: der Bruttoquerschnitt.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse.linie]]

## Gebraucht von

- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]

## Formeln aus diesem Modul

- [[Rissmoment bei der Normalkraft]] · `Bruttoriss._herleitung_rissmoment`
- [[Rissnormalkraft beim Moment]] · `Bruttoriss._herleitung_rissnormalkraft`
- [[Spannung aus dem Moment an der Ecke, die zuerst reisst]] · `Bruttoriss._herleitung_rissnormalkraft`
- [[Widerstandsmoment zum gezogenen Rand]] · `Bruttoriss.herleitung_riss`
