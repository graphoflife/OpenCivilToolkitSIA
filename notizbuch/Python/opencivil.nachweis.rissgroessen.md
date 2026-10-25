---
erzeugt: 08969e1353ef
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/rissgroessen.py
> wann der Beton reisst.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/rissgroessen.py)

## VERANTWORTUNG

Die Rissgroessen an einer Stelle -- fuer die Nachweise der Platte und des
gezeichneten Querschnitts wie fuer ihre Spannung-Dehnung-Analysen:

* **die rissaktive Dicke** ([[opencivil.nachweis.rissgroessen#rissaktive_dicke|rissaktive_dicke]]): unter Biegung ein
  Drittel der Hoehe in Biegerichtung, unter Zug die kleinere Abmessung
  `min(h; b)`, wahlweise hoechstens 500 mm;
* **der Beiwert** `k_t = 1/(1 + 0.5·t)` und mit ihm `f_ct,eff = k_t·f_ctm`
  ([[opencivil.nachweis.rissgroessen#beiwert_dicke|beiwert_dicke]], [[opencivil.nachweis.rissgroessen#protokoll_zugfestigkeit|protokoll_zugfestigkeit]]);
* **das Rissmoment unter reiner Biegung**: das Moment, bei dem `f_ct,eff`
  am ungerissenen Bruttoquerschnitt zum ersten Mal irgendwo erreicht wird
  ([[opencivil.nachweis.rissgroessen#rissmoment|rissmoment]]). Mit dem Deviationsmoment `I_yz` kippt die
  Nulllinie; «einachsig» bleibt sie parallel zur Achse der Biegung, und es
  gilt `W = I/v`. Bei der Platte, einem Rechteck, ist es beide Male
  `b·h²/6` ([[opencivil.nachweis.rissgroessen#rissmoment_rechteck|rissmoment_rechteck]]);
* **die Rissnormalkraft bei einem Moment**: die Zugkraft, bei der
  `f_ct,eff` zum ersten Mal irgendwo erreicht wird ([[opencivil.nachweis.rissgroessen#rissnormalkraft|rissnormalkraft]])
  -- fuer die Analyse des gezeichneten Querschnitts.

So hat es der Benutzer am 2026-10-17 entschieden. Bis dahin standen die
Rissgroessen viermal da -- im sproeden Versagen, in den Richtungsnachweisen
und in den beiden Paaren der Analyse --, und sie sagten schon Verschiedenes:
das Rissmoment rechnete auch einachsig mit `I_yz`, die Analyse ohne, und
fuer die rissaktive Dicke unter Zug gab es vier Regeln.


## DIE PLATTE UNTER ZUG

Ihre Breite `b` ist ein Streifen, keine Abmessung des Bauteils: in ihrer
Ebene ist die Platte unbegrenzt. Unter Zug reisst sie darum ueber ihre Dicke,
`t = h`, auch bei einem Streifen, der schmaler ist als die Platte dick.

Die Uebertragung der Regeln der Platte auf den gezeichneten Querschnitt
geschieht nach Vorgabe, nicht nachgeschlagen (`notizbuch/Notizen/TODO.md`).

## Inhalt

### beiwert_dicke

```python
def beiwert_dicke(t: float) -> float
```

`k_t = 1 / (1 + 0.5 * t)` -- ein dickes Bauteil reisst nicht ueber
seine ganze Hoehe gleichzeitig.

Empirisch: `t` geht in Metern ein, und Meter ist die SI-Basis. Welche
Dicke gilt, sagt [[opencivil.nachweis.rissgroessen#rissaktive_dicke|rissaktive_dicke]].

### rissaktive_dicke

```python
def rissaktive_dicke(*, h: float, b: float=math.inf, zug: bool, begrenzt: bool=False) -> float
```

Wie dick der Beton reisst, in m. Unter Biegung ein Drittel der Hoehe `h`
in Biegerichtung; unter Zug die kleinere Abmessung `min(h; b)`, mit
`begrenzt` hoechstens [[opencivil.nachweis.rissgroessen#Konstanten|DICKENGRENZE]]. Ohne `b` -- bei der
Platte, siehe Dateikopf -- die Dicke `h`.

### protokoll_zugfestigkeit

```python
def protokoll_zugfestigkeit(p: Protokoll, werte: Zwischenwerte, *, k_t: float, f_ct_eff: float, h: Wert, f_ctm: Wert, teiler: float, referenz: str, titel: str='Beiwert für die Plattendicke') -> Wert
```

Beiwert fuer die Dicke und wirksame Zugfestigkeit, hergeleitet.

`teiler` ist der Anteil der Dicke, der reisst: ein Drittel unter
Biegung, unter Zug die ganze rissaktive Dicke (`1`). Zurueck kommt
`f_ct,eff` fuer die Zeile danach.

### Rissgroessen

```python
@dataclass(frozen=True)
class Rissgroessen
```

Das Rissmoment eines Rechtecks und was dazu gehoert -- je Platte, nicht je Lage.

- `k_t: float`
- `f_ct_eff: float`
- `M_Riss: float` – Rissmoment in Nm, bezogen auf die betrachtete Breite.

### rissmoment_rechteck

```python
def rissmoment_rechteck(*, h: float, b: float, f_ctm: float) -> Rissgroessen
```

Das Moment, bei dem das ungerissene Rechteck `b × h` aufreisst --
`h²·b/6` ist sein elastisches Widerstandsmoment. Alles in SI-Basis;
Rueckgabe in Nm.

### rissmoment_wert

```python
def rissmoment_wert(basis: str, g: Rissgroessen) -> Wert
```

Das Rissmoment -- die Einwirkung in Tabelle und Herleitung.

### protokoll_rissmoment_rechteck

```python
def protokoll_rissmoment_rechteck(p: Protokoll, e: Eingaben, g: Rissgroessen, *, basis: str, referenz: str) -> None
```

Das Rissmoment von `k_t` an -- fuer das spröde Versagen und die
Zwängung auf Biegung der Platte dieselben drei Zeilen. Gebraucht werden
die Eingaben `h`, `b` und `f_ctm`.

### Ecke

```python
@dataclass(frozen=True)
class Ecke
```

Eine Ecke des Betons, vom Schwerpunkt aus in m -- und ihr Beton.

- `y: float`
- `z: float`
- `punkt: Tuple[float, float]` – Dieselbe Ecke in der Zeichnung, in mm.
- `stoff: Any`
- `f_ctm: float`

### Bruttoquerschnitt

```python
@dataclass(frozen=True)
class Bruttoquerschnitt
```

Der ungerissene Bruttoquerschnitt ohne Stahl: Traegheitsmomente um den
Schwerpunkt und die Ecken des Betons -- in SI.

- `I_y: float`
- `I_z: float`
- `I_yz: float`
- `ecken: Tuple[Ecke, ...]`
- `biegung: Biegung = SCHIEF` – Ob die Nulllinie kippt oder waagrecht bleibt -- wie die Analyse rechnet.

#### Bruttoquerschnitt.ausdehnung

```python
def ausdehnung(self, um_y: bool) -> Tuple[float, float]
```

Die Hoehe in Biegerichtung und die Breite quer dazu, in m -- aus der Zeichnung.

#### Bruttoquerschnitt.einheitsspannung

```python
def einheitsspannung(self, ecke: Ecke, M_y: float, M_z: float) -> float
```

Die Spannung an der Ecke beim Moment `(M_y, M_z)`, Zug positiv -- bei
einem Moment von eins in dieser Richtung die Einheitsspannung.
Einachsig bleibt die Nulllinie parallel zur Achse der Biegung, ohne
`I_yz`.

### rissbezuege

```python
def rissbezuege(analyse: Querschnittsanalyse) -> List[Eingabebezug]
```

Was der Bruttoquerschnitt liest, ueber die Grundbezuege hinaus: die Traegheitsmomente.

### bruttoquerschnitt

```python
def bruttoquerschnitt(analyse: Querschnittsanalyse, wert: Callable[[str], float]) -> Bruttoquerschnitt
```

Der Bruttoquerschnitt eines gezeichneten Querschnitts. `wert` liefert
zu einer Wert-ID die Zahl in SI -- aus den Eingaben eines Nachweises mit
[[opencivil.nachweis.rissgroessen#rissbezuege|rissbezuege]] ([[opencivil.core.berechnung#Eingaben.si_nach_id|si_nach_id]])
oder aus einer Loesung.

### Rissmoment

```python
@dataclass(frozen=True)
class Rissmoment
```

Das Rissmoment in einer Richtung -- und woraus es entsteht.

- `ecke: Ecke` – Die Ecke, die zuerst ihre Zugfestigkeit erreicht.
- `W: float` – Das Widerstandsmoment zu ihr, m³.
- `hoehe: float` – Die Ausdehnung des Betons in Biegerichtung, m -- fuer `k_t`.
- `k_t: float`
- `f_ct_eff: float`
- `M_Riss: float` – in Nm.

### rissmoment

```python
def rissmoment(q: Bruttoquerschnitt, M_y: float, M_z: float) -> Rissmoment
```

Das Rissmoment in der Richtung `(M_y, M_z)` -- einem Moment von eins:
das Moment unter reiner Biegung, bei dem `f_ct,eff` zum ersten Mal
irgendwo erreicht wird. Bei mehreren Betonen reisst zuerst die Ecke mit
der groessten Spannung, gemessen an ihrer Zugfestigkeit.

### Rissnormalkraft

```python
@dataclass(frozen=True)
class Rissnormalkraft
```

Die Rissnormalkraft bei einem Moment -- und woraus sie entsteht.

- `ecke: Ecke` – Die Ecke, die zuerst ihre Zugfestigkeit erreicht.
- `sigma_M: float` – Die Spannung, die das Moment allein an ihr weckt, Pa.
- `f_ct_eff: float`
- `N_Riss: float` – in N.

### rissnormalkraft

```python
def rissnormalkraft(q: Bruttoquerschnitt, M_y: float, M_z: float, *, k_t: float, A: float) -> Rissnormalkraft
```

Die Zugkraft, bei der der ungerissene Bruttoquerschnitt beim Moment
`(M_y, M_z)` -- in Nm, nicht von eins -- zum ersten Mal irgendwo
`f_ct,eff = k_t·f_ctm` erreicht: `N_Riss = (f_ct,eff - σ_M)·A` an der
Ecke, an der das am wenigsten Zug braucht. `k_t` gilt fuer die
rissaktive Dicke unter Zug ([[opencivil.nachweis.rissgroessen#rissaktive_dicke|rissaktive_dicke]]).

### protokoll_spannung_ungerissen

```python
def protokoll_spannung_ungerissen(p: Protokoll, biegung: Biegung) -> None
```

Wie der ungerissene Querschnitt Spannung traegt -- der Ansatz des Rissmoments.

### protokoll_ecke

```python
def protokoll_ecke(p: Protokoll, ecke: Ecke) -> None
```

Welche Ecke zuerst reisst -- in der Zeichnung, mit ihrem Beton.

### protokoll_widerstandsmoment

```python
def protokoll_widerstandsmoment(p: Protokoll, werte: Zwischenwerte, q: Bruttoquerschnitt, ecke: Ecke, W: float, M_y: float, M_z: float) -> Wert
```

`W = 1/σ` an der Ecke bei einem Moment von eins in der Richtung
`(M_y, M_z)`, um y -- einachsig `I_y/v`, sonst mit `I_yz`.

### protokoll_rissmoment

```python
def protokoll_rissmoment(p: Protokoll, e: Eingaben, analyse: Querschnittsanalyse, werte: Zwischenwerte, q: Bruttoquerschnitt, riss: Rissmoment, M_y: float, M_z: float, *, referenz: str) -> Wert
```

Die Herleitung von [[opencivil.nachweis.rissgroessen#rissmoment|rissmoment]] -- zurueck kommt `M_Riss`.

### _w_vorlage

```python
def _w_vorlage(M_y: float, M_z: float) -> str
```

`W = 1/σ` bei einem Moment von eins -- je Richtung ausgeschrieben.


## Konstanten

- `MOMENTENTEILER = 3.0` – Teiler der Hoehe in Biegerichtung im Beiwert. Unter Biegung reisst der Randbereich, nicht die halbe Hoehe wie beim Zwang. SIA 262:2025, 4.4.1.3.
- `DICKENGRENZE = 0.5` – Groesste rissaktive Dicke unter Zug, in m -- wo die Begrenzung eingeschaltet ist.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.biegung]]

## Gebraucht von

- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]

## Formeln aus diesem Modul

- [[Beiwert für die Dicke]] · `protokoll_zugfestigkeit`
- [[Rissmoment des ungerissenen Querschnitts]] · `protokoll_rissmoment`
- [[Rissmoment des ungerissenen Querschnitts]] · `protokoll_rissmoment_rechteck`
- [[Spannung im ungerissenen Querschnitt]] · `protokoll_spannung_ungerissen`
- [[Widerstandsmoment zum gezogensten Betonpunkt]] · `protokoll_widerstandsmoment`
- [[Wirksame Zugfestigkeit]] · `protokoll_zugfestigkeit`
