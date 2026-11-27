---
erzeugt: 26f87970be78
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 3.1.1; als Grenzdehnung nach Vorgabe"
---
> [!info] Normstelle
> SIA 264:2014, 3.1.1; als Grenzdehnung nach Vorgabe

$$
\varepsilon_{ud} = 15 \cdot \varepsilon_{yp}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varepsilon_{yp}$ | Fliessdehnung des Profilblechstahls | ‰ | [[Fliessdehnung]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_{ud} = 15 \cdot \varepsilon_{yp} = 15 \cdot 1.67\,\text{‰} = 25\,\text{‰}
$$

## Im Code

- [[opencivil.material.profilblech]]

## Themen

- [[Profilblechstahl]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für den Profilblechstahl nennt die Norm weder eine Spannung-Dehnung-Linie
noch eine Grenzdehnung. Das Werkzeug nimmt darum dasselbe Gesetz wie beim
Baustahl: elastisch bis zur [[Fliessdehnung]], dann ideal plastisch, und
es lässt die Linie beim Fünfzehnfachen der Fliessdehnung enden. Das ist
eine Vorgabe, nicht aus der Norm.

Gebraucht wird die Grenzdehnung nur im Bild des Materials. Die
Blechverbunddecke rechnet starr-plastisch: jeder Werkstoff trägt dort mit
einer einzigen Spannung, und eine Dehnung braucht es nicht.
