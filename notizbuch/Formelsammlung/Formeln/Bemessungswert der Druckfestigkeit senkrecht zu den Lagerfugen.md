---
erzeugt: 7b01485b1510
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.2.1.1, Gl. (3)"
---
> [!info] Normstelle
> SIA 266:2015, 4.2.1.1, Gl. (3)

$$
f_{xd} = \frac{f_{xk}}{\gamma_M}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{xk}$ | Druckfestigkeit senkrecht zu den Lagerfugen, kennzeichnend | N/mm² | Vorgabe |
| $\gamma_M$ | Widerstandsbeiwert des Mauerwerks | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
f_{xd} = \frac{f_{xk}}{\gamma_M} = \frac{7\,\mathrm{N}/\mathrm{mm}^{2}}{2} = 3.5\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.material.mauerwerk#_durch_gamma|_durch_gamma]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Mauerwerk trägt vor allem Druck senkrecht zu den Lagerfugen, in einer
gewöhnlichen Wand also lotrecht: die Last der Decken und Wände darüber. Die
Norm benennt die Richtungen nach den Fugen, nicht nach dem Raum: x steht
senkrecht zu den Lagerfugen, y längs der Wand, senkrecht zu den Stossfugen
(SIA 266:2015, Figur 1).

Für Standardmauerwerk steht der kennzeichnende Wert $f_{xk}$ je Sorte in
Tabelle 1; geteilt durch $\gamma_M = 2.0$ gibt er den Bemessungswert, die
Zahl der Tabelle 7. Deklariertes Mauerwerk bringt seinen Wert aus der
Deklaration mit. Steht die Wand im Verband – mehrere Steine über die Dicke
–, rechnet sie mit $0.85 \cdot f_{xd}$ (4.2.1.1). Das wählt die Wand, nicht
das Material; ihre Herleitung zeigt beide Zahlen.
