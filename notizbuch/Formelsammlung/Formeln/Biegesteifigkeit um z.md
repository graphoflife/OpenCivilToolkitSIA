---
erzeugt: ca5643cfabad
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Biegesteifigkeit um z, «Balken 300×500» aus C30/37»*

$$
EI_{z} = E_{cm} \cdot I_{z}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $I_{z}$ | Flächenträgheitsmoment um z, Balken 300×500 | ·10⁶ mm⁴ | [[Flächenträgheitsmoment eines Rechtecks um z]], [[Flächenträgheitsmoment eines I-Profils um z]], Eingabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
EI_{z,\text{Q1,C30/37}} = E_{cm} \cdot I_{z,\text{Q1}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1125\,\cdot 10^{6}\,\mathrm{mm}^{4} = 37822\,\mathrm{kNm}^{2}
$$

## Im Code

- [[opencivil.stabwerk.rechnung#_modul_mal_kennwert|_modul_mal_kennwert]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Steifigkeit gegen Biegung in der Ebene $x$-$y$, quer zur lotrechten
Ebene des Stabs: bei einem waagrechten Balken die Biegung im Grundriss, etwa
unter Wind. Bei einem stehenden Profil ist $z$ die schwache Achse. Ein
IPE 300 ist um $z$ rund vierzehnmal weicher als um $y$, ein IPE 600
siebenundzwanzigmal, ein HEB 300 knapp dreimal.

Sonst wie die [[Biegesteifigkeit um y]].
