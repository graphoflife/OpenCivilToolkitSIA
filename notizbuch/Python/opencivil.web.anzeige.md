---
erzeugt: 73d6abed94c7
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/anzeige.py
> Zahlen und Zeilen, wie die Oberflaeche sie zeigt.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/anzeige.py)

## VERANTWORTUNG

Was der Kern der Oberflaeche gibt, steht in den Einheiten der Anzeige --
kN, kNm, mm, N/mm², Promille. Umgerechnet wird hier, mit den Einheiten des
Kerns ([[opencivil.core.einheiten]]): [[opencivil.web.anzeige#zahl|zahl]] von SI in eine
Einheit, [[opencivil.web.anzeige#si|si]] zurueck fuer das, was die Oberflaeche schickt. Eine
Groesse einer Linie traegt dazu Zeichen und Stellen
([[opencivil.web.anzeige#Anzeigegroesse|Anzeigegroesse]]).

Dazu die Zellen einer Zeile -- Text oder Formel, wie in den Tabellen der
Herleitung ([[opencivil.web.anzeige#zelle_dict|zelle_dict]]). Aus ihnen bestehen die Legenden der
Situationsbilder ([[opencivil.web.anzeige#zeile|zeile]], [[opencivil.web.anzeige#zahlformel|zahlformel]]): die Zahlen, ihr
Vergleich und das Urteil kommen aus dem Kern, die Oberflaeche setzt sie nur.

BIS 2026-11-10 standen die Einheiten der Anzeige auf drei Wegen da: als
Groesse nur fuer die Linien der Diagramme, sonst als nackte Faktoren -- und
`kN = 1e-3` in den Bildern hiess das Gegenteil von `kN = 1e3` beim
Bauen. Die Legenden baute das JS selbst, samt Urteil und Normstelle.

## Inhalt

### zahl

```python
def zahl(si_wert: Optional[float], einheit: Einheit) -> Optional[float]
```

Ein Wert in SI, in der Einheit der Anzeige -- `None` bleibt `None`.

### si

```python
def si(angezeigt: float, einheit: Einheit) -> float
```

Was die Oberflaeche in `einheit` schickt, in SI.

### punkte

```python
def punkte(liste: Iterable[Sequence[float]], einheit: Einheit) -> List[List[float]]
```

Punkte in SI als Listen `[x, y]` in der Einheit der Anzeige.

### Anzeigegroesse

```python
@dataclass(frozen=True)
class Anzeigegroesse
```

Eine Groesse einer Linie, wie sie in den Zeichendaten steht: Zeichen und Einheit.

- `zeichen: str`
- `einheit: Einheit`
- `latex: str = ''`
- `stellen: int = 1`
- `am_bezugsort: bool = False` – Ob sie an einem Ort des Querschnitts gilt -- die Mitteldehnung, nicht die Kruemmung.

#### Anzeigegroesse.zahl

```python
def zahl(self, si_wert: Optional[float]) -> Optional[float]
```

Ein Wert in SI, in der Einheit dieser Groesse.

#### Anzeigegroesse.als_dict

```python
def als_dict(self) -> dict
```

### zelle_dict

```python
def zelle_dict(zelle: Zelle) -> dict
```

Eine Zelle fuer die Oberflaeche: `{"text": ...}` oder `{"mathe": ...}`.
Die Oberflaeche setzt nur Formeln mit KaTeX -- Text aus LaTeX
zurueckzulesen, wie sie es frueher musste, entfaellt.

### zeile

```python
def zeile(*teile: Zelle) -> List[dict]
```

Eine Zeile einer Legende aus Text und Formeln, der Reihe nach.

### masszahl

```python
def masszahl(si_wert: float, einheit: Einheit, stellen: int) -> str
```

`Zahl Einheit` in LaTeX, gerundet wie in der Herleitung.

### zahlformel

```python
def zahlformel(zeichen: str, si_wert: float, einheit: Einheit, stellen: int) -> Mathe
```

`Zeichen = Zahl Einheit` als Formel -- eine Zahl in einer Zeile.

### urteil

```python
def urteil(links: str, soll: str, rechts: str, erfuellt: bool, grad: str) -> List[Zelle]
```

Ein Vergleich mit seinem Urteil, als Teile einer Zeile:
`s = 12 mm ≤ s_zul = 25 mm – erfüllt, α = 2.08`. `links` und
`rechts` in LaTeX, `soll` das Zeichen, das gelten muss -- geht er
nicht auf, steht sein Gegenteil da; `grad` der Erfuellungsgrad in LaTeX.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.balkendaten]]
- [[opencivil.web.diagrammdaten]]
- [[opencivil.web.durchstanzdaten]]
- [[opencivil.web.grundbruchdaten]]
- [[opencivil.web.pfahldaten]]
- [[opencivil.web.setzungsdaten]]
