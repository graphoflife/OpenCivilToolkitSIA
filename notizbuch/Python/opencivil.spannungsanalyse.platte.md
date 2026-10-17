---
erzeugt: a81f21c74d6e
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/platte.py
> das Paar einer Platte.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/platte.py)

## VERANTWORTUNG

Die beiden Querschnittsloeser einer Tragrichtung, gerissen und ungerissen,
dazu Riss, Bezugsflaeche des Moduls und was die Herleitung nur von der
Platte weiss ([[opencivil.spannungsanalyse.platte#Loeserpaar|Loeserpaar]], ein [[opencivil.spannungsanalyse.linie#Paar|Paar]]).

## Inhalt

### Loeserpaar

```python
@dataclass(frozen=True)
class Loeserpaar
```

Die beiden Querschnittsloeser einer Tragrichtung -- gerissen und nicht.

Sie unterscheiden sich in genau einem Stueck, dem Betongesetz. Alles
andere -- Hoehe, Breite, Lagen, Stahlgesetz, Grenzen -- ist dasselbe, und
das muss es sein: sonst verglichen die beiden Zustaende zwei verschiedene
Querschnitte. Dazu, was zum Riss und zum Fliessen gehoert, und womit
gerechnet wird.

- `gerissen: Querschnittsloeser`
- `ungerissen: Querschnittsloeser`
- `M_Riss: float` – Das Rissmoment ohne Normalkraft -- mit `k_t` fuer ein Drittel der Dicke.
- `k_t_zug: float = 1.0`
- `f_ct_eff_zug: float = 0.0` – Fuer die Rissnormalkraft: `k_t` fuer die ganze Dicke und `k_t·f_ctm`.
- `staehle: Tuple[Any, ...] = ()` – Die Staehle der Lagen, jeder einmal -- fuer die Fliessdehnung in der Herleitung. Fliessen beginnt, wo die erste Lage die Fliessdehnung ihres eigenen Stahls erreicht ([[opencivil.spannungsanalyse.platte#Loeserpaar|Stahlgesetz.eps_yd]] der Lage).
- `wahl: Rechenwahl = Rechenwahl(art=Rechenart.PARABEL)` – Womit gerechnet wird -- Kriechzahl, Wertesatz, Rechenart.
- `grenznamen: Tuple[str, ...] = ()` – Je Grenze des gerissenen Loesers, was sie ist -- fuer «massgebend».
- `ids: Mapping[str, str] = field(default_factory=dict)` – Kurzname -> Wert-ID der Eingaben, fuer die Herleitung.
- `E_cm: float = 0.0` – Der Modul des Betons -- daran misst sich der aequivalente Modul.
- `bezugsort = 'auf halber Höhe'` – Wo die Mitteldehnung gilt -- dort greift N an.

#### Loeserpaar.ebenen

```python
def ebenen(self) -> Zustaende
```

Die Ebenen der Platte: ein Rechteck, die Nulllinie bleibt parallel zur Achse.

#### Loeserpaar.rissmoment_bei

```python
def rissmoment_bei(self, N: float) -> float
```

Das Rissmoment bei der Normalkraft `N` (Zug positiv), in Nm.

Am Bruttoquerschnitt reisst der Rand, wenn `N/A + M/W = f_ct,eff`.
Mit `A = b·h` und `W = b·h²/6` -- denselben Werten, mit denen
[[opencivil.nachweis.rissgroessen#rissmoment_rechteck|rissmoment_rechteck]] das
Rissmoment ohne Normalkraft rechnet -- ist das
`M_Riss(N) = M_Riss(0) - N·h/6`. Druck hebt es, Zug senkt es.

Annahme, nicht nachgeschlagen (`notizbuch/Notizen/TODO.md`): der
Bruttoquerschnitt ohne Stahl, wie beim spröden Versagen. Der
ungerissene Zustand daneben rechnet mit Stahl und Kriechzahl und ist
darum steifer; beim Rissmoment steht sein Rand etwas unter
`f_ct,eff`.

`f_ct,eff` mit `k_t` fuer ein Drittel der Dicke, auch unter Zug:
Biegung bleibt bei `h/3`, nach Vorgabe. Die Rissnormalkraft nimmt die
ganze Dicke ([[opencivil.spannungsanalyse.platte#Loeserpaar.rissnormalkraft_bei|rissnormalkraft_bei]]); beim selben N und M reissen
die beiden Linien darum nicht am selben Punkt.

#### Loeserpaar.rissnormalkraft_bei

```python
def rissnormalkraft_bei(self, M: float) -> float
```

Die Zugkraft, bei der der Querschnitt mit dem Moment `M` reisst, in N.

Am Bruttoquerschnitt reisst der Rand, wenn `N/A + |M|/W = f_ct,eff`,
also `N_Riss(M) = f_ct,eff·b·h - 6·|M|/h`. Das Vorzeichen des
Moments zaehlt nicht -- der Querschnitt ist oben wie unten derselbe.

`f_ct,eff` mit `k_t = 1/(1 + 0.5·t)` fuer die ganze Dicke,
`t = h`: unter Zug reisst der ganze Querschnitt, nicht ein Drittel
wie unter Biegung. Nach Vorgabe, nicht nachgeschlagen
(`notizbuch/Notizen/TODO.md`). Bis 2026-10-09 galt das `f_ct,eff`
des Rissmoments, mit `t = h/3` -- am Beispiel 829 statt 757 kN.

#### Loeserpaar.I_c

```python
@property
def I_c(self) -> float
```

Der reine Betonquerschnitt fuer den aequivalenten Modul: `b·h³/12`.

#### Loeserpaar.A_c

```python
@property
def A_c(self) -> float
```

Dasselbe fuer die Normalkraft: `b·h`.

#### Loeserpaar.tiefe

```python
def tiefe(self, w: Zwischenwerte, ein: Callable[[str], 'Wert']) -> 'Wert'
```

Die Dicke, ueber die die Linie laeuft -- ein Wert der Platte.

#### Loeserpaar.herleitung_riss

```python
def herleitung_riss(self, p: Protokoll, w: Zwischenwerte, linie: Linie, ein: Callable[[str], 'Wert'], h: 'Wert') -> None
```

Wo die Linie reisst: das Rissmoment bei N, oder die Rissnormalkraft bei M.

#### Loeserpaar.herleitung_dehnung_am_ende

```python
def herleitung_dehnung_am_ende(self, p: Protokoll, w: Zwischenwerte, bruch: 'Grenzzustand', oben: 'Wert', unten: 'Wert', h: 'Wert') -> None
```

Die Dehnung, ueber die die N-eps-Linie laeuft, am Ende -- auf halber Hoehe.

#### Loeserpaar.herleitung_bezug

```python
def herleitung_bezug(self, p: Protokoll, w: Zwischenwerte, momente: bool, ein: Callable[[str], 'Wert'], h: 'Wert') -> 'Wert'
```

Der reine Betonquerschnitt des aequivalenten Moduls -- ein Rechteck b·h.

### loeserpaar

```python
def loeserpaar(querschnitt, richtung: Richtung, wert: Callable[[str], float], wahl: Rechenwahl=Rechenwahl(art=Rechenart.PARABEL)) -> Optional[Loeserpaar]
```

Das Loeserpaar einer Platte in einer Richtung -- `None` ohne Bewehrung.

`wert` liefert zu einer Wert-ID die Zahl in SI, aus einer Loesung.
`wahl` sagt, womit gerechnet wird: Kriechzahl, Wertesatz, Rechenart --
die Gesetze dazu baut [[opencivil.nachweis.rechenwahl#gesetze|gesetze]].

Stand frueher in der Schnittstelle zur Oberflaeche. Dort war sie ohne
Oberflaeche nicht erreichbar, und ein Test baute sie als eigene Kopie
nach -- er pruefte seine Kopie statt der echten.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.dehnungsfaecher]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.spannungsanalyse.art]]
- [[opencivil.spannungsanalyse.linie]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]

## Formeln aus diesem Modul

- [[Fläche eines Rechtecks]] · `Loeserpaar.herleitung_bezug`
- [[Flächenträgheitsmoment eines Rechtecks]] · `Loeserpaar.herleitung_bezug`
- [[Grösste Dehnung auf halber Höhe]] · `Loeserpaar.herleitung_dehnung_am_ende`
- [[Rissmoment bei der Normalkraft]] · `Loeserpaar.herleitung_riss`
- [[Rissnormalkraft beim Moment]] · `Loeserpaar.herleitung_riss`
