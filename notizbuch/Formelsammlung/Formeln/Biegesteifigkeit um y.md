---
erzeugt: 12a7ce5c5b09
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Biegesteifigkeit um y, «Balken 300×500» aus C30/37»*

$$
EI_{y} = E_{cm} \cdot I_{y}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $I_{y}$ | Flächenträgheitsmoment um y, Balken 300×500 | ·10⁶ mm⁴ | [[Flächenträgheitsmoment eines Rechtecks]], [[Flächenträgheitsmoment eines I-Profils um y]], Eingabe, Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
EI_{y,\text{Q1,C30/37}} = E_{cm} \cdot I_{y,\text{Q1}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 3125\,\cdot 10^{6}\,\mathrm{mm}^{4} = 105062\,\mathrm{kNm}^{2}
$$

## Im Code

- [[opencivil.stabwerk.rechnung#_modul_mal_kennwert|_modul_mal_kennwert]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie die [[Biegesteifigkeit]] der Ebene, um die Achse $y$ des Stabs: sie hält
die Biegung in der Ebene $x$-$z$, bei $\beta = 0$ also die in der lotrechten
Ebene durch den Stab. Bei einem Profil, dessen Steg in dieser Ebene steht,
ist $y$ die starke Achse.

Der E-Modul ist der des Materials, beim Beton der Mittelwert am
ungerissenen Bruttoquerschnitt, wie in der Ebene.
