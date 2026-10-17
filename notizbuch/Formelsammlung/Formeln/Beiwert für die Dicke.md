---
erzeugt: 69ee1c80c604
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.4.2", "SIA 262:2025, 4.4.1.3"]
---
> [!info] Normstellen
> SIA 262:2025, 4.4.2 · SIA 262:2025, 4.4.1.3

*In der Herleitung: «Beiwert für die Plattendicke»*

$$
k_t = \frac{1}{1 + 0.5 \cdot h_{eff}} \quad \left(h_{eff}\ \text{in}\ \mathrm{m}\right)
$$

*In der Herleitung: «Beiwert für die Plattendicke»*

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h_{eff}$ | – | mm | [[Rissaktive Plattendicke]] |
| $h$ | Plattendicke | mm | Vorgabe, Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_t = \frac{1}{1 + 0.5 \cdot h_{eff}} = \frac{1}{1 + 0.5 \cdot 0.3} = 0.87 \quad \left(h_{eff}\ \text{in}\ \mathrm{m}\right)
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_t = \frac{1}{1 + 0.5 \cdot h/3} = \frac{1}{1 + 0.5 \cdot 0.3/3} = 0.952 \quad \left(h\ \text{in}\ \mathrm{m}\right)
$$

## Gebraucht von

- [[Wirksame Zugfestigkeit]]

## Im Code

- [[opencivil.nachweis.rissgroessen#protokoll_zugfestigkeit|protokoll_zugfestigkeit]]

## Themen

- [[Zwängung auf Normalkraft]]
- [[Sprödes Versagen]]
- [[Zwängung auf Biegung]]
- [[Sprödes Versagen je Richtung]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Zugfestigkeit, die beim Reissen wirkt, ist bei dicken Bauteilen kleiner
als im Prüfkörper: Eigenspannungen aus dem Abfliessen der Hydratationswärme
und aus ungleichem Schwinden nehmen einen Teil vorweg, und die Wahrscheinlichkeit
einer schwachen Stelle wächst mit dem Volumen. $k_t$ mindert darum
$f_{ctm}$ mit der Dicke $t$, die reisst -- in Metern eingesetzt.

- Unter Normalkraft reisst die ganze rissaktive Dicke, $t = h_{eff}$.
- Unter Biegung reisst nur die gezogene Randzone; angesetzt wird ein Drittel
  der Höhe.
- Beim gezeichneten Querschnitt zählt ein Drittel der Höhe in
  Biegerichtung -- die Regel der Platte, übertragen, nach Vorgabe und nicht
  nachgeschlagen.
