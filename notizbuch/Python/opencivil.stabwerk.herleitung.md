---
erzeugt: 728584531c91
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/herleitung.py
> wie ein Balkensystem seine Rechnung aufschreibt.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/herleitung.py)

## VERANTWORTUNG

Die Herleitung der Steifigkeitsmethode, so dass man sie von Hand
nachrechnen kann: das System in Tabellen, die Ansaetze -- Steifigkeitsmatrix
eines Stabs, Drehung, Bettung, arbeitsgleiche Lasten, Gleichungssystem --,
die Matrizen mit Zahlen, solange sie klein genug sind, und je Lastfall und
Kombination die Verschiebungen der Knoten, die Kraefte an den Stabenden, die
Lagerkraefte, die Extremwerte und die Gleichgewichtsprobe.


## WIE VIEL MIT ZAHLEN

Die Matrix jedes Stabs bis [[opencivil.stabwerk.herleitung#Konstanten|STAEBE_MIT_MATRIX]] Teilstaebe, die
Gesamtmatrix bis [[opencivil.stabwerk.herleitung#Konstanten|UNBEKANNTE_MIT_MATRIX]] Unbekannte. Darueber stuende
eine Wand aus Zahlen, die niemand nachrechnet; die Tabellen gibt es immer.


## EINHEITEN

Laengen in m, Verschiebungen in mm, Drehungen in mrad, Kraefte in kN,
Momente in kNm -- in den Matrizen kN und m. Die Schnittgroessen mit den
Vorzeichen der Baustatik ([[opencivil.stabwerk.verlauf|verlauf]]).

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, system: 'Balkensystem') -> None
```

Die ganze Herleitung eines gerechneten Systems.

### _teilname

```python
def _teilname(system: 'Balkensystem', teil) -> str
```

Der Name eines Teilstabs: der seines Stabs -- mit Nummer, wenn dieser geteilt ist.

### _gleichgewicht

```python
def _gleichgewicht(p: Protokoll, fall: Fall) -> None
```

Lasten und Lagerkraefte zusammen -- null bis auf Rundung.

### _zahl

```python
def _zahl(x: float) -> str
```

Vier gueltige Ziffern -- ab einer Million und unter einem Tausendstel mit Zehnerpotenz.


## Konstanten

- `STAEBE_MIT_MATRIX = 6` – Bis zu so vielen Teilstaeben steht die Matrix jedes einzelnen mit Zahlen da.
- `UNBEKANNTE_MIT_MATRIX = 12` – Bis zu so vielen Unbekannten stehen Gesamtmatrix, Lastvektor und Loesung mit Zahlen da.
- `ANNAHME = 'Steifigkeit nach Vorgabe, nicht nachgeschlagen: E_cm für Beton und E…` – Was die Steifigkeit annimmt -- nach Vorgabe, nicht nachgeschlagen.
- `GLEICHUNGSSYSTEM_LATEX = '\\mathbf{K} = \\sum_{\\text{Stäbe}} \\mathbf{T}^{\\mathsf{T}} \\cdot…` – Das Gleichungssystem in Zeichen.
- `SCHNITTGROESSEN_LATEX = 'N(0) = -s_{u,a} \\qquad V(0) = s_{v,a} \\qquad M(0) = -s_{\\theta,a}…` – Von den Kraeften an den Stabenden zu den Schnittgroessen laengs des Stabs.
- `BIEGELINIE_LATEX = "v'' = \\frac{M}{EI} \\qquad u' = \\frac{N}{EA}"` – Die Biegelinie aus Moment und Normalkraft.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.stabwerk.matrix]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.stab]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.stabwerk.rechnung]]
