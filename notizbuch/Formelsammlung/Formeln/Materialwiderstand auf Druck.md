---
erzeugt: 60c21c35d903
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.5.2.4.2"
---
> [!info] Normstelle
> SIA 267:2013, 9.5.2.4.2

*In der Herleitung: «Materialwiderstand auf Druck: Beton ohne die Stäbe, dazu die Stäbe»*

$$
R_{mat,d} = \left(A_c - A_s\right) \cdot \sigma_c + A_s \cdot \sigma_s
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_c$ | Fläche des Pfahlquerschnitts | mm² | [[Fläche des Pfahlquerschnitts]] |
| $A_s$ | Fläche der Längsbewehrung | mm² | [[Fläche der Längsbewehrung]] |
| $\sigma_c$ | Spannung im Beton auf Druck, als Betrag | N/mm² | Zwischenwert |
| $\sigma_s$ | Spannung im Stahl auf Druck, als Betrag | N/mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  R_{mat,d} &= \left(A_c - A_s\right) \cdot \sigma_c + A_s \cdot \sigma_s \\
  &= \left(636173\,\mathrm{mm}^{2} - 3770\,\mathrm{mm}^{2}\right) \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} + 3770\,\mathrm{mm}^{2} \cdot 400\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 14156\,\mathrm{kN}
\end{aligned}
$$

## Gebraucht von

- [[Innerer Widerstand des Pfahls]]

## Im Code

- [[opencivil.pfahl.innen#InnererWiderstand._normalkraft|InnererWiderstand._normalkraft]]

## Themen

- [[Innerer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Querschnitt ganz gedrückt, nach SIA 262 (SIA 267:2013, 9.5.2.4.2): Beton
und Stäbe stauchen gleich, bis der Beton ε_c1d erreicht, und nicht weiter.
Darum steht der Beton bei f_cd und der Stahl bei ε_c1d · E_s =
2 ‰ · 200 000 N/mm² = 400 N/mm², unter seinem f_yd = 435 N/mm².

Ein Bohrpfahl ⌀ 900 aus C30/37 mit 12 ⌀ 20:
(636 173 − 3 770) mm² · 20 N/mm² + 3 770 mm² · 400 N/mm² = 14 156 kN.
