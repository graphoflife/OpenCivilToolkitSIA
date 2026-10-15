---
erzeugt: 203a4e225f1c
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/sproedes_versagen.py
> Mindestbewehrung gegen sprödes Versagen.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/sproedes_versagen.py)

## VERANTWORTUNG

Prueft je Bewehrungslage, ob der Biegewiderstand das Rissmoment uebertrifft:

```python
M_Rd(N_Ed = 0)  >=  M_Riss
```


## WARUM DIESE FORM

Ein zu schwach bewehrter Querschnitt reisst und versagt im selben Augenblick.
Die Frage ist also nicht, welche Spannung im Stahl entsteht, sondern schlicht,
ob der bewehrte Querschnitt mehr traegt als der unbewehrte im Augenblick des
Risses. Genau das ist `M_Rd >= M_Riss`.

Frueher stand hier `M_s,adm = sigma_s,adm * A_s * z`. Das war ein anderer
Nachweis -- naemlich der gegen eine **Zwaengung auf Biegung**, und der steht
jetzt in [[opencivil.nachweis.mindestbewehrung]]. Bei normaler Anforderung
war er ausserdem *weniger* streng als `M_Rd`: `f_yk/f_yd = 1.15` wiegt den
kleineren Hebelarm des gerissenen Querschnitts mehr als auf.

`M_Rd(N_Ed = 0)` kommt aus der Resistenzlinie der Tragsicherheit und ist
dort hergeleitet; hier wird es nur noch gegenuebergestellt. Rechnet die
Tragsicherheit mit charakteristischen Werten, heisst es `M_Rk`. Das Rissmoment gehoert
dem **ungerissenen** Bruttoquerschnitt:

```
k_t      = 1 / (1 + 0.5 * h/3)            h in Metern
f_ct,eff = k_t * f_ctm
M_Riss   = f_ct,eff * h^2 * b / 6
```

Der Teiler 3 gilt fuer Platten unter Biegung -- es reisst der Randbereich, nicht
die halbe Hoehe wie beim Zwang (SIA 262:2025, 4.4.1.3).

## Inhalt

### Rissgroessen

```python
@dataclass(frozen=True)
class Rissgroessen
```

Das Rissmoment und was dazu gehoert -- je Platte, nicht je Lage.

- `k_t: float`
- `f_ct_eff: float`
- `M_Riss: float` – Rissmoment in Nm, bezogen auf die betrachtete Breite.

### beiwert_dicke

```python
def beiwert_dicke(h_riss: float) -> float
```

`k_t = 1 / (1 + 0.5 * h)` -- eine dicke Platte reisst nicht ueber ihre
ganze Hoehe gleichzeitig.

Empirisch: `h_riss` geht in Metern ein, und Meter ist die SI-Basis.
Unter Biegung ist es ein Drittel der Dicke, beim Zwang die rissaktive.

### rissmoment

```python
def rissmoment(*, h: float, b: float, f_ctm: float) -> Rissgroessen
```

Das Moment, bei dem der ungerissene Querschnitt aufreisst.

`h^2*b/6` ist das elastische Widerstandsmoment des Bruttoquerschnitts.
Alles in SI-Basis; Rueckgabe in Nm.

### rissmoment_wert

```python
def rissmoment_wert(basis: str, g: Rissgroessen) -> Wert
```

Das Rissmoment -- die Einwirkung in Tabelle und Herleitung.

### protokoll_zugfestigkeit

```python
def protokoll_zugfestigkeit(p: Protokoll, werte: Zwischenwerte, *, k_t: float, f_ct_eff: float, h: Wert, f_ctm: Wert, teiler: float, referenz: str, titel: str='Beiwert für die Plattendicke') -> Wert
```

Beiwert fuer die Plattendicke und wirksame Zugfestigkeit, hergeleitet.

Drei Nachweise brauchen die beiden Zeilen -- das spröde Versagen und beide
Zwängungen. `teiler` ist der Anteil der Dicke, der reisst: ein Drittel
unter Biegung, bei der Normalkraft die ganze rissaktive Dicke (`1`).
Zurueck kommt `f_ct,eff` fuer die Zeile danach.

### protokoll_rissmoment

```python
def protokoll_rissmoment(p: Protokoll, e: Eingaben, g: Rissgroessen, *, basis: str, referenz: str) -> None
```

Das Rissmoment von `k_t` an -- fuer das spröde Versagen und die
Zwängung auf Biegung dieselben drei Zeilen. Gebraucht werden die
Eingaben `h`, `b` und `f_ctm`.

### Lagenergebnis

```python
@dataclass
class Lagenergebnis
```

Was der Nachweis fuer eine Lage gefunden hat.

- `lage: Bewehrungslage`
- `M_Rd: float = 0.0` – Biegewiderstand bei N_Ed = 0 auf der Seite dieser Lage, in Nm (Betrag).
- `erfuellungsgrad: float = 0.0`
- `erfuellt: bool = False`
- `begruendung: str = ''`
- `hinweis: str = ''`

#### Lagenergebnis.machbar

```python
@property
def machbar(self) -> bool
```

### SproedesVersagen

```python
class SproedesVersagen(Nachweis)
```

Mindestbewehrung gegen sprödes Versagen.

Ein Nachweis je Platte, ein Urteil je Lage der Tragrichtung. In der
Zusammenfassung steht die ungünstigere der beiden -- geht die auf, geht
auch die andere auf.

`M_Rd(N=0)` kommt als Eingang aus dem M-N-Nachweis. Als Eingang und nicht
als mitgegebene Zahl, damit die Abhängigkeit im Graphen steht und die
Rückverfolgung sie zeigt.

- `THEMA = 'Sprödes Versagen'`

#### SproedesVersagen.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### SproedesVersagen._m_rd

```python
def _m_rd(self, erg: Lagenergebnis) -> Wert
```

Der Biegewiderstand der Lage -- der Widerstand in Tabelle und Herleitung.


## Konstanten

- `MOMENTENTEILER = 3.0` – Teiler der Plattendicke im Beiwert. Unter Biegung reisst der Randbereich, nicht die halbe Hoehe wie beim Zwang. SIA 262:2025, 4.4.1.3.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.querschnitt.schnittanalyse]]
- [[opencivil.spannungsanalyse]]

## Formeln aus diesem Modul

- [[Beiwert für die Dicke]] · `protokoll_zugfestigkeit`
- [[Rissmoment des ungerissenen Querschnitts]] · `protokoll_rissmoment`
- [[Wirksame Zugfestigkeit]] · `protokoll_zugfestigkeit`
