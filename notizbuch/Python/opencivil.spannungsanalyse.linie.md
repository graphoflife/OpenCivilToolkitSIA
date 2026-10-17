---
erzeugt: 8e7e9adb406b
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/linie.py
> die Linien eines Querschnitts.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/linie.py)

## VERANTWORTUNG

Die Momenten-Kruemmungs- und die Normalkraft-Dehnungs-Linie eines Paars von
Loesern, gerissen und ungerissen -- und was ein solches Paar dafuer bieten
muss ([[opencivil.spannungsanalyse.linie#Paar|Paar]]). Die Platte bietet es je Tragrichtung
([[opencivil.spannungsanalyse.platte#Loeserpaar|Loeserpaar]]), der gezeichnete
Querschnitt je Zugseite
([[opencivil.spannungsanalyse.schnitt#Schnittpaar|Schnittpaar]]); bis 2026-10-17
hiess es an den Funktionen dafuer `paar: Any`.

## Inhalt

### Paar

```python
class Paar(Protocol)
```

Die beiden Loeser eines Querschnitts, gerissen und ungerissen, und was die
Fragen und ihre Herleitung sonst von ihm wissen muessen. Was nur die Art
des Bauteils weiss -- die Tiefe, den Riss, die Dehnung am Ende, den reinen
Betonquerschnitt --, schreibt das Paar selbst in die Herleitung.

- `gerissen: Faserloeser`
- `ungerissen: Faserloeser`
- `wahl: Rechenwahl` – Womit gerechnet wird -- Kriechzahl, Wertesatz, Rechenart.
- `grenznamen: Tuple[str, ...]` – Je Grenze des gerissenen Loesers, was sie ist -- fuer «massgebend».
- `ids: Mapping[str, str]` – Kurzname -> Wert-ID der Eingaben, fuer die Herleitung.
- `staehle: Tuple[Any, ...]` – Die Staehle der Bewehrung, jeder einmal -- fuer die Fliessdehnung.
- `E_cm: float` – Der Modul des Betons -- daran misst sich der aequivalente Modul.
- `bezugsort: str` – Wo die Mitteldehnung gilt -- dort greift N an.

#### Paar.I_c

```python
@property
def I_c(self) -> float
```

#### Paar.A_c

```python
@property
def A_c(self) -> float
```

#### Paar.rissmoment_bei

```python
def rissmoment_bei(self, N: float) -> float
```

#### Paar.rissnormalkraft_bei

```python
def rissnormalkraft_bei(self, M: float) -> float
```

#### Paar.tiefe

```python
def tiefe(self, w: 'Zwischenwerte', ein: Callable[[str], 'Wert']) -> 'Wert'
```

#### Paar.herleitung_riss

```python
def herleitung_riss(self, p: 'Protokoll', w: 'Zwischenwerte', linie: 'Linie', ein: Callable[[str], 'Wert'], h: 'Wert') -> None
```

#### Paar.herleitung_dehnung_am_ende

```python
def herleitung_dehnung_am_ende(self, p: 'Protokoll', w: 'Zwischenwerte', bruch: 'Grenzzustand', oben: 'Wert', unten: 'Wert') -> None
```

#### Paar.herleitung_bezug

```python
def herleitung_bezug(self, p: 'Protokoll', w: 'Zwischenwerte', momente: bool, ein: Callable[[str], 'Wert'], h: 'Wert') -> 'Wert'
```

### Linienpunkt

```python
@dataclass(frozen=True)
class Linienpunkt
```

Ein Punkt einer Linie: die Kraft -- `M` bzw. `N` --, die Verformung,
die dort gilt -- `chi` bzw. `eps_m` --, und beide Zustaende zum
Vergleich.

- `kraft: float`
- `verformung: float` – Was gilt: ungerissen bis zum Riss, darueber gerissen.
- `gerissen: bool`
- `verformung_I: Optional[float]` – Ungerissen -- `None` ueber dem Riss, wo der Beton dafuer Zug ohne Grenze braeuchte, und wo der Zustand keine Loesung hat.
- `verformung_II: Optional[float]` – Gerissen, ohne Zugfestigkeit des Betons.

### Eckpunkt

```python
@dataclass(frozen=True)
class Eckpunkt
```

Ein benannter Punkt einer Linie.

- `kraft: float`
- `verformung: float`

### Grenzzustand

```python
@dataclass(frozen=True)
class Grenzzustand(Eckpunkt)
```

Das Ende einer Linie -- und welche Grenzdehnung es bestimmt.

- `eps_oben: float = 0.0`
- `eps_unten: float = 0.0`
- `massgebend: str = ''`

### Linie

```python
@dataclass
class Linie
```

`M(chi)` bei festgehaltener Normalkraft oder `N(eps_m)` bei
festgehaltenem Moment -- welche, sagt [[opencivil.spannungsanalyse.linie#Linie|art]].

- `art: Analyseart`
- `fest: float` – Was festgehalten wird: `N` in N oder `M` in Nm.
- `riss: float` – Die Kraft, bei der der Querschnitt reisst: `M_Riss(N)` oder `N_Riss(M)`.
- `punkte: List[Linienpunkt] = field(default_factory=list)`
- `bruch: Optional[Grenzzustand] = None`
- `fliessen: Optional[Eckpunkt] = None` – Wo der Stahl der am staerksten gezogenen Lage zu fliessen beginnt.
- `hinweis: str = ''`

#### Linie.hinweisen

```python
def hinweisen(self, satz: str) -> None
```

Einen Satz vor die bisherigen Hinweise stellen.

#### Linie.tragfaehig

```python
@property
def tragfaehig(self) -> bool
```

#### Linie.sprung

```python
@property
def sprung(self) -> Optional[Tuple[Linienpunkt, Linienpunkt]]
```

Die beiden Punkte des Risses: vor und nach dem Reissen, bei derselben Kraft.

### _Weg

```python
@dataclass(frozen=True)
class _Weg
```

Wie eine Linie laeuft -- der einzige Unterschied zwischen M-chi und N-eps.

`ebene` fuehrt von einer Verformung zur gerissenen Ebene ``(eps_m,
chi)` oder zu `None`, wo es kein Gleichgewicht gibt; `kraft`` liest
aus der Ebene die Kraft der Linie; `verformung_bei` sucht zu einer Kraft
die Verformung, mit einem der beiden Loeser.

- `ebene: Callable[[float], Optional[Tuple[float, float]]]`
- `kraft: Callable[[Tuple[float, float]], float]`
- `verformung_bei: Callable[[Faserloeser, float], Optional[float]]`
- `obergrenze: float` – Eine Verformung, ueber der es sicher kein Gleichgewicht mehr gibt.

### _grenze

```python
def _grenze(gut: Callable[[float], bool], unten: float, oben: float) -> float
```

Wo `gut` endet, zwischen `unten` (gut) und `oben` -- durch Halbieren.

### _massgebend

```python
def _massgebend(paar: Paar, eps_m: float, chi: float) -> str
```

Welche Grenzdehnung die Ebene erreicht -- die mit dem kleinsten Abstand.

### _linie

```python
def _linie(paar: Paar, weg: _Weg, art: Analyseart, fest: float, riss: float) -> Linie
```

Die Linie von null bis zum Bruch: ungerissen bis `riss`, dort der
Sprung, darueber gerissen -- ueber die Verformung gerechnet, mit dem
Fliessbeginn als Punkt der Linie.

### _durchlaufen

```python
def _durchlaufen(e: Ebene) -> bool
```

Ob eine Linie die Ebene nimmt: gefunden -- oder verfehlt an einem Sprung
des Spannungsblocks ([[opencivil.nachweis.querschnittsloeser#Ebene|Ebene.verfehlt]]). Eine Linie fragt nach der
Verformung, bei der ihre Kraft einen Wert durchlaeuft; am Sprung ist das
seine Stelle, auch wenn dort keine Ebene die Kraft genau erzeugt. Ein
Nachweis dagegen braucht die Ebene selbst.

### moment_kruemmung

```python
def moment_kruemmung(paar: Paar, *, N: float) -> Linie
```

Die Momenten-Kruemmungs-Linie bei der Normalkraft `N` (Zug positiv):
ungerissen bis `M_Riss(N)`, dort der Sprung, darueber gerissen bis zum
Bruch.

### normalkraft_dehnung

```python
def normalkraft_dehnung(paar: Paar, *, M: float) -> Linie
```

Die Normalkraft-Dehnungs-Linie beim Moment `M`, auf Zug: ungerissen
bis `N_Riss(M)`, dort der Sprung, darueber gerissen bis zum Bruch.
Die Dehnung ist die am Arm null -- dort greift `N` an: bei der Platte
auf halber Hoehe, beim gezeichneten Querschnitt im Schwerpunkt.


## Konstanten

- `KURVENPUNKTE = 40` – Punkte des gerissenen Teils einer Linie -- vor dem Fliessen ein Drittel, danach der Rest, denn dort waechst die Verformung am staerksten.
- `PUNKTE_UNGERISSEN = 10` – Punkte des ungerissenen Teils. Er ist beinahe gerade.

## Braucht

- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.spannungsanalyse.art]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]
