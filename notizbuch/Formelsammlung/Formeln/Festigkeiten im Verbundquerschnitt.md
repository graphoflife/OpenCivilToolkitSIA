---
erzeugt: 5dbcb9e88287
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 4.1.3, (1); 4.1.5; 4.3.2.1; 5.1.2.1"
---
> [!info] Normstelle
> SIA 264:2014, 4.1.3, (1); 4.1.5; 4.3.2.1; 5.1.2.1

*In der Herleitung: «Festigkeiten im plastischen Zustand – der Beton nur gedrückt»*

$$
f_{yd} = \frac{f_y}{\gamma_a} \qquad 0.85\, f_{cd} = 0.85\, \frac{\eta_{fc}\, f_{ck}}{\gamma_c},\ \eta_{fc} = 1 \qquad f_{sd} = \frac{f_{sk}}{\gamma_s}
$$

## Im Code

- [[opencivil.nachweis.qa_verbund_werte#festigkeiten|festigkeiten]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im plastischen Zustand trägt jeder Werkstoff mit einer einzigen Spannung:

- **Baustahl** gezogen und gedrückt mit $f_{yd} = f_y/\gamma_a$. Für
  $\gamma_a$ nimmt das Werkzeug den Widerstandsbeiwert $\gamma_{M1}$ des
  Materials, 1.05.
- **Beton** nur gedrückt, mit $0.85\, f_{cd}$ über die ganze Druckzone bis
  zur plastischen Nulllinie; $\eta_{fc}$ ist im Geltungsbereich der
  SIA 264 eins. Zug trägt er keinen.
- **Betonstahl** mit $f_{sd} = f_{sk}/\gamma_s$, gedrückt mit dem Wert,
  den sein Material dafür nennt.

Mit charakteristischen Werten fallen die Beiwerte weg; der Beton trägt dann
$0.85\, f_{ck}$.
