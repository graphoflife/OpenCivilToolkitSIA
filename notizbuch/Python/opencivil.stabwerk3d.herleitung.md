---
erzeugt: bf93e26bcbaf
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk3d/herleitung.py
> wie ein 3D-Balkensystem seine Rechnung aufschreibt.
> Paket [[opencivil.stabwerk3d]] · [Quelltext](../../opencivil/stabwerk3d/herleitung.py)

## VERANTWORTUNG

Wie in der Ebene ([[opencivil.stabwerk.herleitung]]), im Raum: das
System in Tabellen, die Ansaetze -- der Stab als drei ebene, seine Achsen,
Bettung, arbeitsgleiche Lasten, Gleichungssystem --, die Matrizen mit
Zahlen, solange sie klein genug sind, und je Lastfall und Kombination die
Verschiebungen der Knoten, die Schnittgroessen an den Stabenden, die
Lagerkraefte, die Extremwerte und die Gleichgewichtsprobe. Was die Ebene
schon schreibt -- Zahlen und Matrizen, Unbekannte, den Kopf eines Falls,
Lagerkraefte, Extremwerte, die Probe --, kommt von dort, mit den Groessen
des Raums.


## WIE VIEL MIT ZAHLEN

Die Gesamtmatrix wie in der Ebene; die Matrix eines Stabs, 12 × 12, nur
bis [[opencivil.stabwerk3d.herleitung#Konstanten|STAEBE_MIT_MATRIX]] Teilstaebe.


## EINHEITEN

Wie in der Ebene: Laengen in m, Verschiebungen in mm, Drehungen in mrad,
Kraefte in kN, Momente in kNm, in den Matrizen kN und m. Die
Schnittgroessen in den Achsen des Stabs ([[opencivil.stabwerk3d.verlauf|verlauf]]).

## Inhalt

### schreiben

```python
def schreiben(p: Protokoll, system: 'Balkensystem3d', befund: 'Raumbefund') -> None
```

Die ganze Herleitung eines gerechneten Systems.

### _verschiebungen

```python
def _verschiebungen(p: Protokoll, befund: 'Raumbefund', fall: Fall) -> None
```

Je Knoten seine Verschiebung und Drehung. Eine Drehung um eine Achse
des Systems, die eine gestrichene Achse beruehrt, ist nicht bestimmbar.


## Konstanten

- `STAEBE_MIT_MATRIX = 2` – Bis zu so vielen Teilstaeben steht die Matrix jedes einzelnen mit Zahlen da.
- `ANNAHME = 'Steifigkeit: E_cm und G_cm des Betons, E_a und G_a des Baustahls ode…` – Was die Steifigkeit und das Gleichgewicht annehmen.
- `DURCHBIEGUNG = 'Die Durchbiegungen f_y und f_z misst jeder Stab gegen die Gerade zwi…` – Was die Durchbiegungen f_y und f_z sind -- und was sie nicht sind.
- `SCHNITTGROESSEN_LATEX = '\\sigma = \\frac{N}{A} + \\frac{M_y \\cdot z}{I_y} + \\frac{M_z \\cd…` – Die Vorzeichen der Schnittgroessen, in den Achsen des Stabs.
- `BIEGELINIE_LATEX = "w'' = -\\frac{M_y}{EI_y} \\qquad v'' = -\\frac{M_z}{EI_z} \\qquad u'…` – Die Biegelinien, die Laengsverschiebung und die Verdrillung.
- `LAGERKRAEFTE = (('R_x', 'kN'), ('R_y', 'kN'), ('R_z', 'kN'), ('M_x', 'kNm'), ('M_y',…` – Eine Lagerkraft im Raum, in der Folge des Rechenkerns: Zeichen und Einheit.
- `SUMMEN = (('\\sum F_x', 'kN'), ('\\sum F_y', 'kN'), ('\\sum F_z', 'kN'), ('\\s…` – Die Summen der Gleichgewichtsprobe im Raum -- Momente um den Ursprung.
- `EINHEITEN = {'N': 'kN', 'V_y': 'kN', 'V_z': 'kN', 'T': 'kNm', 'M_y': 'kNm', 'M_z'…` – Je Schnittgroesse ihre Einheit -- Kraefte in kN, Momente in kNm.
- `EXTREMWERTE = (*((g, EINHEITEN[g], 0.001, 1) for g in SCHNITTGROESSEN), ('f_y', 'mm…` – Die Extremwerte im Raum: Groesse, Einheit, Faktor von SI und Nachkommastellen.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk.stab]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk3d.modell]]
- [[opencivil.stabwerk3d.raum]]
- [[opencivil.stabwerk3d.rechnung]]
- [[opencivil.stabwerk3d.stab]]
- [[opencivil.stabwerk3d.system]]
- [[opencivil.stabwerk3d.verlauf]]

## Gebraucht von

- [[opencivil.stabwerk3d.rechnung]]

## Formeln aus diesem Modul

- [[Achsen eines Stabs im Raum]] · `_ansaetze`
- [[Arbeitsgleiche Knotenkräfte]] · `_ansaetze`
- [[Bettung eines Stabs]] · `_ansaetze`
- [[Biegelinie eines Stabs im Raum]] · `_ansaetze`
- [[Gleichungssystem der Steifigkeitsmethode]] · `_ansaetze`
- [[Schnittgrössen eines Stabs im Raum]] · `_ansaetze`
- [[Steifigkeitsmatrix eines Stabs]] · `_ansaetze`
- [[Zerlegung eines Stabs im Raum]] · `_ansaetze`
