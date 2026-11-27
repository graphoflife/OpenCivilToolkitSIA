---
erzeugt: b58b14cdb3af
art: modul
tags: [modul]
---
> [!abstract] opencivil/fachwerkmodell/nachrechnung.py
> ein gefundenes Fachwerk, nachgerechnet.
> Paket [[opencivil.fachwerkmodell]] · [Quelltext](../../opencivil/fachwerkmodell/nachrechnung.py)

## VERANTWORTUNG

Was die Rechnung an einem Fachwerk prüft, das die Suche gefunden hat und
das im Projekt steht ([[opencivil.fachwerkmodell.nachrechnung#nachrechnen|nachrechnen]]): an jedem Knoten die Summe der
Stabkräfte und Lasten – wo ein Lager hält, nimmt es sie auf, sonst muss
sie null sein –, die Kräfte der Lager und das Ziel der Optimierung,
`V = Σ l · (w_Z · N⁺ + N⁻)`. Ihr wird nichts geglaubt, was sich
nachrechnen lässt: das Gleichgewicht folgt aus den Stäben, wie sie
dastehen.


## WAS OFFEN BLEIBT

Geht das Gleichgewicht nicht auf, steht je Last, die es nicht trägt, was
offen bleibt – eine Last neben jedem Stab, eine Scheibe, deren Teil kein
Lager hat. Die Grenze ist ein Millionstel der grössten Last (nach Vorgabe).

## Inhalt

### Lagerkraft

```python
@dataclass(frozen=True)
class Lagerkraft
```

Was ein Lager aufnimmt, in N: `R_x` nach rechts, `R_y` nach oben.

- `lager: Lager`
- `R_x: float`
- `R_y: float`

### Nachrechnung

```python
@dataclass(frozen=True)
class Nachrechnung
```

Was die Rechnung am Fachwerk fand.

- `fachwerk: Fachwerk`
- `laengen: Tuple[float, ...]` – Je Stab in m.
- `lagerkraefte: Tuple[Lagerkraft, ...]`
- `offen: Tuple[Tuple[Optional[Last], Punkt, float], ...]` – Wo das Gleichgewicht nicht aufgeht: die Last dort – oder keine –, der Ort und der Betrag in N.
- `V: float` – `Σ l · (w_Z · N⁺ + N⁻)` in N·m.
- `w_Z: float`

#### Nachrechnung.im_gleichgewicht

```python
@property
def im_gleichgewicht(self) -> bool
```

### nachrechnen

```python
def nachrechnen(modell: Modell, fachwerk: Fachwerk, w_Z: float) -> Nachrechnung
```

Siehe Dateikopf.


## Braucht

- [[opencivil.decke.geometrie]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.suche]]

## Gebraucht von

- [[opencivil.fachwerkmodell.herleitung]]
- [[opencivil.fachwerkmodell.werk]]
- [[opencivil.web.fachwerkdaten]]
