---
erzeugt: 0b70aa700444
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 3.1.4.1, Gl. (2)"
---
> [!info] Normstelle
> SIA 266:2015, 3.1.4.1, Gl. (2)

$$
G_k = 0.4 \cdot E_{xk}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{xk}$ | Elastizitätsmodul senkrecht zu den Lagerfugen, kennzeichnend | N/mm² | [[Elastizitätsmodul senkrecht zu den Lagerfugen, kennzeichnend]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
G_k = 0.4 \cdot E_{xk} = 0.4 \cdot 7000\,\mathrm{N}/\mathrm{mm}^{2} = 2800\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Bemessungswert des Schubmoduls]]

## Im Code

- [[opencivil.material.mauerwerk]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Schubmodul sagt, wie stark sich die Wand in ihrer Ebene verschiebt, wenn
sie Schub trägt – etwa unter Wind oder Erdbeben. Für Standardmauerwerk ist
er ein fester Anteil des Elastizitätsmoduls, $G_k = 0.4 \cdot E_{xk}$ (Gl.
(2)). Wie $E_{xk}$ gilt er mit seinem kennzeichnenden Wert für die
Verformungen im Gebrauch (4.2.2.1) und durch $\gamma_M$ geteilt für die
Tragsicherheit ([[Bemessungswert des Schubmoduls]]).
