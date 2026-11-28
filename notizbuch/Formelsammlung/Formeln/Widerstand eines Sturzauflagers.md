---
erzeugt: 5beca46341c4
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.2.1.2, Gl. (4), Figur 2"
---
> [!info] Normstelle
> SIA 266:2015, 4.2.1.2, Gl. (4), Figur 2

*In der Herleitung: «Widerstand des Auflagers»*

$$
R_{Rd} = k_m \cdot f_{xd} \cdot A_0
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_m$ | Beiwert der Teilflächenpressung | – | [[Beiwert der Teilflächenpressung im Mauerwerk]] |
| $f_{xd}$ | Druckfestigkeit der Wand | N/mm² | Zwischenwert |
| $A_0$ | Fläche des Auflagers | mm² | [[Fläche des Auflagers]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
R_{Rd} = k_m \cdot f_{xd} \cdot A_0 = 1 \cdot 2.98\,\mathrm{N}/\mathrm{mm}^{2} \cdot 26250\,\mathrm{mm}^{2} = 78.1\,\mathrm{kN}
$$

## Im Code

- [[opencivil.mauerwerk.nachweise#Teilflaechen.stelle|Teilflaechen.stelle]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Kraft eines Sturzauflagers darf das Mauerwerk auf der Fläche $A_0$ mit
$f_{xd}$ belasten, vergrössert um $k_m$. Die Kraft kommt aus dem Lastabtrag
der Wand: was über einem Auflager liegt, ganz, was über der Öffnung liegt,
wie bei einem einfachen Balken zwischen den Mitten der beiden Auflager –
nach Vorgabe, nicht nachgeschlagen. Sie geht weiter in den Pfeiler darunter
oder auf den nächsten Sturz.
