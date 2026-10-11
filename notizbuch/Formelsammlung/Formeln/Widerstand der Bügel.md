---
erzeugt: 91fe1607ee4e
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
V_{Rd,s} = \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot \alpha
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{\varnothing,V}$ | Querschnitt eines Bügelschenkels | mm² | [[Querschnitt eines Bügelschenkels]] |
| $s_{V,x}$ | Bügelteilung in x-Richtung | mm | Vorgabe |
| $s_{V,y}$ | – | mm | [[Teilung in y aus der Stabzahl]] |
| $d$ | – | mm | [[Statische Höhe]] |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |
| $\alpha$ | – | ° | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_{Rd,s} &= \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot \alpha \\
  &= \frac{50.3\,\mathrm{mm}^{2}}{200\,\mathrm{mm} \cdot 200\,\mathrm{mm}} \cdot 0.9 \cdot 249\,\mathrm{mm} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \cot 30{}^{\circ} \\
  &= 212.1\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

## Gebraucht von

- [[Querkraftwiderstand mit Querkraftbewehrung]]

## Im Code

- [[opencivil.nachweis.querkraft#Querkraft|Querkraft._protokoll_fall_buegel]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Schnitt längs der Druckdiagonalen schneidet auf der Länge
$0.9\,d \cdot \cot\alpha$ Bügel; jeder zieht mit seiner Fläche mal $f_{yd}$.
Je Quadratmeter Platte steht die Bügelfläche
$A_{\varnothing,V} / (s_{V,x} \cdot s_{V,y})$, und so ergibt sich der
Widerstand je Laufmeter. Flache Diagonalen nutzen die Bügel besser -- bis
die Druckdiagonalen begrenzen.
