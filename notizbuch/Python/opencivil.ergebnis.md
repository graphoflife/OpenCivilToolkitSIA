---
erzeugt: 4a200f6a0bdf
art: modul
tags: [modul]
---
> [!abstract] opencivil/ergebnis.py
> ein gerechnetes Projekt, wie man es ohne Oberflaeche braucht.
> Paket [[opencivil]] · [Quelltext](../../opencivil/ergebnis.py)

## VERANTWORTUNG

Buendelt, was [[opencivil.projekt.projekt#Projekt.rechnen|Projekt.rechnen]] liefert -- die Beschreibung, den Aufbau
und die Loesung -- und die drei Arten, sie anzusehen: die Zusammenfassung,
den vollstaendigen Bericht und das LaTeX-Dokument.


## KEINE EIGENE RECHNUNG, KEINE EIGENE DARSTELLUNG

Alles hier ruft auf, was Oberflaeche und Berichte auch benutzen. Ein zweiter
Weg zu denselben Zahlen waere ein zweiter Ort, an dem sie auseinanderlaufen.

```python
from opencivil import Projekt

p = Projekt("Decke über EG")
p.beton("C30/37")
p.stahl("B500B")
q = p.platte("Decke", h=300, x=[18, 12], y=[12, 12])
q.einwirkung("Feld", M_Ed=100)
ergebnis = p.rechnen()
print(ergebnis.zusammenfassung())
```

## Inhalt

### Ergebnis

```python
@dataclass
class Ergebnis
```

Ein gerechnetes Projekt.

- `projekt: 'Projekt'`
- `aufbau: 'Aufbau'`
- `loesung: Loesung`

#### Ergebnis.erfuellt

```python
@property
def erfuellt(self) -> bool
```

Ob alle gefuehrten Nachweise aufgehen -- die ausgeschalteten zaehlen nicht.

#### Ergebnis.urteile

```python
@property
def urteile(self) -> List[NachweisUrteil]
```

Die gefuehrten Urteile, so wie sie in der Zusammenfassung stehen.

#### Ergebnis.stille_maengel

```python
@property
def stille_maengel(self) -> List[NachweisUrteil]
```

Was ausgeschaltet ist und trotzdem nicht aufgeht.

#### Ergebnis.warnungen

```python
@property
def warnungen(self) -> List[str]
```

Was beim Aufbau aufgefallen ist -- etwa eine Platte ohne Einwirkung.

#### Ergebnis.urteile_von

```python
def urteile_von(self, bauteil: str) -> List[NachweisUrteil]
```

Die gefuehrten Urteile einer Platte oder Analyse -- nach Name oder Kennung.

#### Ergebnis.wert

```python
def wert(self, wert_id: str) -> Wert
```

Ein einzelner gerechneter Wert, mit Einheit, Herkunft und Norm.

#### Ergebnis.balkensystem

```python
def balkensystem(self, bauteil: str) -> 'Balkensystem'
```

Ein gerechnetes Balkensystem -- nach Name oder Kennung. Am Objekt
stehen das Ergebnis (`ergebnis`: Meldungen, Faelle mit
Verschiebungen und Lagerkraeften) und je Fall die Verlaeufe der
Schnittgroessen (`verlaeufe("Eigengewicht")`), in SI.

#### Ergebnis.analysen

```python
def analysen(self) -> Dict[str, List[Analyse]]
```

Die Spannung-Dehnung-Analysen je Platte -- Bilder, keine Nachweise.

Dieselben, die die Oberflaeche zeichnet: je Fall das Querschnittsbild
(Dehnungsebene, Spannungen, Schnittgroessen) oder die
Momenten-Kruemmungs-Linie, in SI.

#### Ergebnis.zusammenfassung

```python
def zusammenfassung(self) -> str
```

Je Platte eine Tabelle der Nachweise -- wie in der Oberflaeche.

#### Ergebnis.bericht

```python
def bericht(self) -> str
```

Der vollstaendige Bericht mit Herleitung, als Text.

#### Ergebnis.markdown

```python
def markdown(self, pfad: Optional[str | Path]=None) -> str
```

Der Bericht als Markdown, mit den Formeln als LaTeX-Mathe.

Mit `pfad` auch als `.md`-Datei abgelegt; zurueck kommt der Text
in jedem Fall.

#### Ergebnis.latex

```python
def latex(self, pfad: str | Path, *, pdf: bool=False) -> Ausgabeergebnis
```

Das LaTeX-Dokument, auf Wunsch auch als PDF.

`pdf` ist aus, solange niemand es verlangt: uebersetzt wird mit dem,
was auf dem Rechner an TeX liegt, und das ist nicht ueberall etwas.


## Braucht

- [[opencivil.bericht.konsole]]
- [[opencivil.bericht.latex_dokument]]
- [[opencivil.bericht.markdown]]
- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.core.berechnung]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.projekt]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.stabwerk.rechnung]]

## Gebraucht von

- [[opencivil.projekt.projekt]]
