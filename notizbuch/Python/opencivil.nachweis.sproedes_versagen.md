---
erzeugt: e52b2ac4ef0a
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


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.platte]]
