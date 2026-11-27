---
erzeugt: d652ada3fb44
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/herleitung.py
> wie ein Balkensystem seine Rechnung aufschreibt.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/herleitung.py)

## VERANTWORTUNG

Die Herleitung der Steifigkeitsmethode, so dass man sie von Hand
nachrechnen kann: das System in Tabellen, die Ansaetze – Steifigkeitsmatrix
eines Stabs, Drehung, Bettung, arbeitsgleiche Lasten, Gleichungssystem –,
die Matrizen mit Zahlen, solange sie klein genug sind, und je Lastfall und
Kombination die Verschiebungen der Knoten, die Kraefte an den Stabenden, die
Lagerkraefte, die Extremwerte und die Gleichgewichtsprobe.


## WIE VIEL MIT ZAHLEN

Die Matrix jedes Stabs bis [[opencivil.stabwerk.herleitung#Konstanten|STAEBE_MIT_MATRIX]] Teilstaebe, die
Gesamtmatrix bis [[opencivil.stabwerk.herleitung#Konstanten|UNBEKANNTE_MIT_MATRIX]] Unbekannte. Darueber stuende
eine Wand aus Zahlen, die niemand nachrechnet; die Tabellen gibt es immer.


## EINHEITEN

Laengen in m, Verschiebungen in mm, Drehungen in mrad, Kraefte in kN,
Momente in kNm – in den Matrizen kN und m. Die Schnittgroessen mit den
Vorzeichen der Baustatik ([[opencivil.stabwerk.verlauf|verlauf]]).

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, system: 'Balkensystem', befund: 'Systembefund') -> None
```

Die ganze Herleitung eines gerechneten Systems.

### halt_text

```python
def halt_text(halt: Halt, einheit: str, faktor: float=1000.0) -> str
```

### gelenke_text

```python
def gelenke_text(stab) -> str
```

Wo ein Stab ein Gelenk hat – in der Ebene und im Raum.

### linienlager_text

```python
def linienlager_text(*richtungen: Tuple[str, Halt]) -> str
```

Wie ein Stab aufliegt, je Richtung – `("quer", halt), ("längs", halt)`.

### teilname

```python
def teilname(e: Ergebnis, teil) -> str
```

Der Name eines Teilstabs: der seines Stabs – mit Nummer, wenn dieser geteilt ist.

### unbekannte

```python
def unbekannte(p: Protokoll, e: Ergebnis) -> None
```

### kopf_eines_falls

```python
def kopf_eines_falls(p: Protokoll, befund: 'Systembefund', fall) -> None
```

Titel, Beiwerte einer Kombination, Lastvektor und Loesung – in der Ebene und im Raum.

### lagerkraefte

```python
def lagerkraefte(p: Protokoll, befund: 'Systembefund', fall, groessen: Sequence[Tuple[str, str]]=LAGERKRAEFTE_DER_EBENE) -> None
```

### extremwerte

```python
def extremwerte(p: Protokoll, verlaeufe, groessen: Sequence[Tuple[str, str, str, float, int]]=EXTREMWERTE_DER_EBENE, durchbiegungen: Sequence[str]=(IN_DER_EBENE['w'],)) -> None
```

Kleinster und groesster Wert je Stab – dazu die massgebende der
`durchbiegungen` (Felder) ueber alle Staebe, wie der Bildschirm sie
zeigt ([[opencivil.stabwerk.verlauf#grenzwerte|grenzwerte]]).

### gleichgewicht

```python
def gleichgewicht(p: Protokoll, fall, summen=SUMMEN_DER_EBENE) -> None
```

Lasten und Lagerkraefte zusammen – null bis auf Rundung.

### _zahl

```python
def _zahl(x: float) -> str
```

Vier gueltige Ziffern – ab einer Million und unter einem Tausendstel mit Zehnerpotenz.

### matrix_latex

```python
def matrix_latex(zeilen: Sequence[Sequence[float]], faktor: float) -> str
```


## Konstanten

- `STAEBE_MIT_MATRIX = 6` – Bis zu so vielen Teilstaeben steht die Matrix jedes einzelnen mit Zahlen da.
- `UNBEKANNTE_MIT_MATRIX = 12` – Bis zu so vielen Unbekannten stehen Gesamtmatrix, Lastvektor und Loesung mit Zahlen da.
- `ANNAHME = 'Steifigkeit: E_cm des Betons, E_a des Baustahls oder das E eines eig…` – Was die Steifigkeit und das Gleichgewicht annehmen.
- `DURCHBIEGUNG = 'Die Durchbiegung w misst jeder Stab gegen die Gerade zwischen seinen…` – Was die Durchbiegung w ist – und was sie nicht ist.
- `GLEICHUNGSSYSTEM_LATEX = '\\mathbf{K} = \\sum_{\\text{Stäbe}} \\mathbf{T}^{\\mathsf{T}} \\cdot…` – Das Gleichungssystem in Zeichen.
- `SCHNITTGROESSEN_LATEX = 'N(0) = -s_{u,a} \\qquad V(0) = s_{v,a} \\qquad M(0) = -s_{\\theta,a}…` – Von den Kraeften an den Stabenden zu den Schnittgroessen laengs des Stabs.
- `BIEGELINIE_LATEX = "v'' = \\frac{M}{EI} \\qquad u' = \\frac{N}{EA}"` – Die Biegelinie aus Moment und Normalkraft.
- `LAGERKRAEFTE_DER_EBENE = (('R_x', 'kN'), ('R_z', 'kN'), ('M', 'kNm'))` – Eine Lagerkraft in der Ebene, in der Folge des Rechenkerns: Zeichen und Einheit.
- `EXTREMWERTE_DER_EBENE = tuple(((IN_DER_EBENE[g], g, *rest) for g, *rest in (('N', 'kN', 0.001…` – Die Extremwerte in der Ebene: Feld im Verlauf, Zeichen, Einheit, Faktor von SI und Nachkommastellen.
- `SUMMEN_DER_EBENE = (('\\sum F_x', 'kN'), ('\\sum F_z', 'kN'), ('\\sum M_0', 'kNm'))` – Die Summen der Gleichgewichtsprobe in der Ebene, in der Folge des Rechenkerns.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.stabwerk.matrix]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.stab]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk.verlauf]]
- [[opencivil.stabwerk3d.stab]]

## Gebraucht von

- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk3d.herleitung]]

## Formeln aus diesem Modul

- [[Arbeitsgleiche Knotenkräfte]] · `_ansaetze`
- [[Bettung eines Stabs]] · `_ansaetze`
- [[Biegelinie eines Stabs]] · `_ansaetze`
- [[Drehung in die Achsen des Stabs]] · `_ansaetze`
- [[Gleichungssystem der Steifigkeitsmethode]] · `_ansaetze`
- [[Schnittgrössen längs eines Stabs]] · `_ansaetze`
- [[Steifigkeitsmatrix eines Stabs]] · `_ansaetze`
