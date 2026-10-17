---
erzeugt: dc221fceef7d
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/spannungsgrenzen.py
> wogegen die Stahlspannung gehalten wird.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/spannungsgrenzen.py)

## VERANTWORTUNG

Die zulaessige Stahlspannung der Gebrauchsnachweise, an der Platte wie am
gezeichneten Querschnitt ([[opencivil.nachweis.spannungsbegrenzung]]):

* **die Grenzen** -- gegen das Fliessen `f_yd - 80 N/mm²`
  ([[opencivil.nachweis.spannungsgrenzen#GrenzeGegenFliessen|GrenzeGegenFliessen]]), aus der Rissbreite `sigma_s,adm`
  ([[opencivil.nachweis.spannungsgrenzen#GrenzeAusRissbreite|GrenzeAusRissbreite]]), jede mit ihren Woertern, Eingaben und
  ihrem Absatz in der Herleitung ([[opencivil.nachweis.spannungsgrenzen#Spannungsgrenze|Spannungsgrenze]]);
* **die Stellen**, an denen gemessen wird -- bei der Platte ihre Lagen, beim
  gezeichneten Querschnitt jeder Stab ([[opencivil.nachweis.spannungsgrenzen#Stelle|Stelle]]) --, und je Stelle
  ihre Grenze, in Gruppen gleicher Grenze hergeleitet ([[opencivil.nachweis.spannungsgrenzen#Grenzen|Grenzen]]).

Gegen das Fliessen gilt je Stahl dieselbe Zahl, fuer jede Geometrie
([[opencivil.nachweis.spannungsgrenzen#gegen_fliessen|gegen_fliessen]]); mit welchem Durchmesser die Rissbreite zaehlt, sagt
die Geometrie selbst ([[opencivil.nachweis.spannungsbegrenzung#Stahlspannungsort.aus_rissbreite|aus_rissbreite]]).
Bis 2026-10-17 standen die Grenzen im Modul des Nachweises und fuer den
gezeichneten Querschnitt ein zweites Mal in `stabgrenzen.py`.

## Inhalt

### Stelle

```python
@dataclass(frozen=True)
class Stelle
```

Wo eine Stahlspannung gemessen wird: eine Lage der Platte, ein Stab des gezeichneten Querschnitts.

- `stahl: Baustoff`
- `E_s: float`
- `eps_y: float` – Die Fliessdehnung `f_s / E_s`, im Wertesatz der Wahl.

### Stahlzustand

```python
@dataclass(frozen=True)
class Stahlzustand
```

Was ein Ort fuer eine Rechnung vorbereitet -- aus ihren Eingaben: die
Stellen und ihre Staehle. Jeder Ort fuegt hinzu, was nur er braucht.

- `stellen: Tuple[Stelle, ...]`
- `staehle: Tuple[Baustoff, ...]` – Jeder Stahl der Stellen einmal, in der Folge, in der seine Grenze hergeleitet wird.

### Grenzgruppe

```python
@dataclass
class Grenzgruppe
```

Stellen mit derselben zulaessigen Spannung -- und woraus sie entsteht.

- `sigma: float` – `sigma_s,adm` in Pa.
- `stahl: Baustoff`
- `stab: Optional['Stabangabe'] = None` – Nur beim gezeichneten Querschnitt, wo die Rissbreite zaehlt: ein Stab der Gruppe, fuer Durchmesser und Beton. Bei normaler Anforderung, gegen das Fliessen und an der Platte gilt die Grenze fuer jede Stelle des Stahls.
- `stellen: List[int] = field(default_factory=list)` – Die Stellen der Gruppe, nach ihrer Nummer.
- `wert: Optional[Wert] = None` – Die Grenze, wie sie in Herleitung und Vergleich steht -- gesetzt beim Protokollieren.

### Grenzen

```python
@dataclass(frozen=True)
class Grenzen
```

Die Grenze jeder Stelle -- und die Gruppen, in denen sie hergeleitet wird.

- `gruppen: List[Grenzgruppe]`
- `je_stelle: List[int]` – Je Stelle die Nummer ihrer Gruppe.

#### Grenzen.gruppe

```python
def gruppe(self, i: int) -> Grenzgruppe
```

#### Grenzen.sigma

```python
def sigma(self, i: int) -> float
```

#### Grenzen.strengste

```python
@property
def strengste(self) -> int
```

Die Stelle mit der kleinsten Grenze -- sie steht da, wo keine gezogen ist.

### nach_stahl

```python
def nach_stahl(zustand: Stahlzustand, sigma: Callable[[Baustoff], float]) -> Grenzen
```

Je Stahl eine Gruppe, in der Folge der Staehle des Zustands -- jede
Stelle in der ihres Stahls. `sigma` gibt die Grenze eines Stahls.

### je_stahl

```python
def je_stahl(name: str, symbol: str, stahl: Baustoff, alle: Sequence[Baustoff]) -> Tuple[str, str]
```

Name und Zeichen eines Werts, der zu einem Stahl gehoert -- mit dem
Stahl daran, sobald es mehr als einen gibt.

### gegen_fliessen

```python
def gegen_fliessen(zustand: Stahlzustand, e: Eingaben, p: Protokoll, basis: str) -> Grenzen
```

`f_yd - 80 N/mm²` je Stahl, hergeleitet -- fuer jede Geometrie dasselbe:
der Durchmesser zaehlt hier nicht. Setzt [[opencivil.nachweis.spannungsgrenzen#Grenzgruppe|Grenzgruppe.wert]].

### Spannungsgrenze

```python
class Spannungsgrenze(ABC)
```

Wogegen ein Stahlspannungsnachweis haelt -- und alles, was nur dazugehoert.

Die Zahl, die Eingaben, aus denen sie entsteht, und die Absaetze, die sie
begruenden. Dazu die Woerter, unter denen der Nachweis ueberall erscheint:
Wert-ID, Symbol, Tabellenzeile, Ueberschrift. Zwei Grenzen mit gleichem
`langname` stuenden als zwei ununterscheidbare Zeilen in derselben
Tabelle.

Die Absaetze sind **nicht** zu einem Text mit Platzhaltern
zusammenzulegen: der eine argumentiert fuer `f_yd`, der andere fuer
`f_yk`. Ein Text, der beides behauptet, behauptet nichts.

Eine Grenze ist eine Klasse, kein Gegenstand: was sie von der Geometrie
braucht, fragt sie den Ort
([[opencivil.nachweis.spannungsbegrenzung#Stahlspannungsort|Stahlspannungsort]]).

- `idteil: str` – Teil der Wert-ID: `<bauteil>.nachweis.<idteil>`, bei der Platte mit der Richtung.
- `symbolteil: str` – Index am Erfuellungsgrad.
- `art: str` – Kurzzeichen im Urteil.
- `langname: str` – Spalte «Nachweis» der Zusammenfassung.
- `thema: str` – Thema in der Formelsammlung, und wovon der Erfuellungsgrad spricht.
- `einwirkung: str` – «häufiger» / «quasi-ständiger» -- im Titel.
- `lastindex: str` – Index an M_Ed und N_Ed in der Herleitung.
- `fallwort: str` – Ueberschrift je Fall.
- `referenz: str`
- `einleitung: str` – Der erste Satz der Herleitung: wozu der Nachweis da ist.

#### Spannungsgrenze.gilt_bei

```python
@classmethod
def gilt_bei(cls, anforderung: Rissanforderung) -> bool
```

Ob der Nachweis bei dieser Rissanforderung verlangt ist.

#### Spannungsgrenze.bezuege

```python
@classmethod
@abstractmethod
def bezuege(cls, ort: 'Stahlspannungsort') -> List[Eingabebezug]
```

Was nur diese Grenze braucht, zusaetzlich zur gemeinsamen Rechnung.

#### Spannungsgrenze.bestimmen

```python
@classmethod
@abstractmethod
def bestimmen(cls, ort: 'Stahlspannungsort', zustand: Stahlzustand, e: Eingaben, p: Protokoll, anforderung: Rissanforderung, basis: str) -> Grenzen
```

Die zulaessige Stahlspannung jeder Stelle -- gerechnet und
mitgeschrieben, mit [[opencivil.nachweis.spannungsgrenzen#Grenzgruppe|Grenzgruppe.wert]] gesetzt.

#### Spannungsgrenze.festlegung

```python
@classmethod
@abstractmethod
def festlegung(cls, p: Protokoll, ort: 'Stahlspannungsort') -> None
```

Welche Werte die Grenze ansetzt, und warum -- nur der Absatz.

### GrenzeGegenFliessen

```python
class GrenzeGegenFliessen(Spannungsgrenze)
```

`f_yd - 80 N/mm²` unter haeufiger Einwirkung -- das Fliessen verhindern.

Nur bei erhoehter und hoher Anforderung -- bei normaler steht in
Tabelle 17 ein Strich ([[opencivil.nachweis.rissanforderung#Rissanforderung.gegen_fliessen|Rissanforderung.gegen_fliessen]]). Der
Aufbau fragt [[opencivil.nachweis.spannungsgrenzen#GrenzeGegenFliessen.gilt_bei|gilt_bei]].

- `idteil = 'spannung'`
- `symbolteil = '\\sigma'`
- `art = 'σ_s'`
- `langname = 'Risse: Häufige Lastfälle'`
- `thema = 'Stahlspannung gegen Fliessen'`
- `einwirkung = 'häufiger'`
- `lastindex = 'häufig'`
- `fallwort = 'Häufiger Lastfall'`
- `referenz = 'SIA 262:2025, Tabelle 17'`
- `einleitung = 'Unter häufiger Einwirkung darf die Bewehrung nicht fliessen – sonst …`

#### GrenzeGegenFliessen.gilt_bei

```python
@classmethod
def gilt_bei(cls, anforderung: Rissanforderung) -> bool
```

#### GrenzeGegenFliessen.bezuege

```python
@classmethod
def bezuege(cls, ort: 'Stahlspannungsort') -> List[Eingabebezug]
```

#### GrenzeGegenFliessen.bestimmen

```python
@classmethod
def bestimmen(cls, ort: 'Stahlspannungsort', zustand: Stahlzustand, e: Eingaben, p: Protokoll, anforderung: Rissanforderung, basis: str) -> Grenzen
```

#### GrenzeGegenFliessen.festlegung

```python
@classmethod
def festlegung(cls, p: Protokoll, ort: 'Stahlspannungsort') -> None
```

### GrenzeAusRissbreite

```python
class GrenzeAusRissbreite(Spannungsgrenze)
```

`sigma_s,adm` aus der Rissanforderung, unter quasi-staendiger Einwirkung.

Dieselbe zulaessige Spannung wie bei der Zwaengung -- dieselbe Funktion,
[[opencivil.nachweis.spannungsgrenzen#GrenzeAusRissbreite|mindestbewehrung.zulaessige_stahlspannung]], und keine zweite
Fassung davon. Bei normaler Anforderung `f_yk`: die Bewehrung darf
unter Dauerlast nicht fliessen. Bei erhoehter und hoher zusaetzlich die
Wurzelformel mit `w_nom`.

**Mit welchem Durchmesser, sagt die Geometrie**
([[opencivil.nachweis.spannungsbegrenzung#Stahlspannungsort.aus_rissbreite|aus_rissbreite]]):
die Platte nimmt den dicksten Stab der Tragrichtung, der gezeichnete
Querschnitt je Stab den eigenen.

- `idteil = 'spannung_riss'`
- `symbolteil = '\\sigma,w'`
- `art = 'σ_s,w'`
- `langname = 'Risse: Quasi-ständige Lastfälle'`
- `thema = 'Stahlspannung aus Rissbreite'`
- `einwirkung = 'quasi-ständiger'`
- `lastindex = '\\text{quasi-ständig}'`
- `fallwort = 'Quasi-ständiger Lastfall'`
- `referenz = 'SIA 262:2025, 4.4.2'`
- `einleitung = 'Unter quasi-ständiger Einwirkung begrenzt die Stahlspannung die Riss…`

#### GrenzeAusRissbreite.bezuege

```python
@classmethod
def bezuege(cls, ort: 'Stahlspannungsort') -> List[Eingabebezug]
```

#### GrenzeAusRissbreite.bestimmen

```python
@classmethod
def bestimmen(cls, ort: 'Stahlspannungsort', zustand: Stahlzustand, e: Eingaben, p: Protokoll, anforderung: Rissanforderung, basis: str) -> Grenzen
```

#### GrenzeAusRissbreite.festlegung

```python
@classmethod
def festlegung(cls, p: Protokoll, ort: 'Stahlspannungsort') -> None
```


## Konstanten

- `FLIESSABSTAND = 80000000.0` – Abstand zur Bemessungsfliessgrenze, in Pa. SIA 262:2025, Tabelle 17.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.stabgrenzen]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.projekt.aufbau]]

## Formeln aus diesem Modul

- [[Zulässige Stahlspannung]] · `gegen_fliessen`
