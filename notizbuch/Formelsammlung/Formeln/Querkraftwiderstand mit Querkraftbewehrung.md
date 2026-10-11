---
erzeugt: 7e5408b9cddc
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4

*In der Herleitung: «Ansatz»*

$$
V_{Rd,s} = \frac{A_{\varnothing,V}}{s_{V,x} \cdot s_{V,y}} \cdot 0.9 \cdot d \cdot f_{yd} \cdot \cot\alpha \qquad V_{Rd,c} = 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin\alpha \cdot \cos\alpha
$$

*In der Herleitung: «Querkraftwiderstand»*

$$
V_{Rd,x} = \min\left[V_{Rd,s};\ V_{Rd,c}\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $V_{Rd,s}$ | – | kN/m | [[Widerstand der Bügel]] |
| $V_{Rd,c}$ | – | kN/m | [[Widerstand der Druckdiagonalen]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_{Rd,x}(M_{Ed} = 150\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) &= \min\left[V_{Rd,s};\ V_{Rd,c}\right] \\
  &= \min\left[212.1\,\mathrm{kN}/\mathrm{m};\ 1067.4\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 212.1\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.querkraft#Querkraft|Querkraft._protokoll_ansatz_buegel]]
- [[opencivil.nachweis.querkraft#Querkraft|Querkraft._protokoll_fall_buegel]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
