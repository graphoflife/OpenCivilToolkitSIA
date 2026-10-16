---
erzeugt: 579b752b0006
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.3.3.2.1", "SIA 262:2025, 4.3.3.4"]
---
> [!info] Normstellen
> SIA 262:2025, 4.3.3.2.1 · SIA 262:2025, 4.3.3.4

*In der Herleitung: «Querkraftwiderstand ohne Bügel bei M\_Ed = 0, das Kleinere beider Seiten»*

$$
V_{Rd,max} = \min\left[V_{Rd}^{+}(M_{Ed} = 0);\ V_{Rd}^{-}(M_{Ed} = 0)\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $V_{Rd}^{+}(M_{Ed} = 0)$ | – | kN/m | [[Querkraftwiderstand ohne Bügel bei M_Ed = 0]] |
| $V_{Rd}^{-}(M_{Ed} = 0)$ | – | kN/m | [[Querkraftwiderstand ohne Bügel bei M_Ed = 0]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  V_{Rd,max} &= \min\left[V_{Rd}^{+}(M_{Ed} = 0);\ V_{Rd}^{-}(M_{Ed} = 0)\right] \\
  &= \min\left[272.8\,\mathrm{kN}/\mathrm{m};\ 276.1\,\mathrm{kN}/\mathrm{m}\right] \\
  &= 272.8\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.kennzahlen#Plattenkennzahlen._kleinstes|Plattenkennzahlen._kleinstes]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Kennzahl ohne Momentenrichtung soll für beide gelten: massgebend ist
darum das Kleinere der beiden Seiten -- Zug unten mit der statischen Höhe
der unteren Lagen, Zug oben mit der der oberen. Beide Werte stehen in der
Herleitung darüber, für wen die Richtung kennt.
