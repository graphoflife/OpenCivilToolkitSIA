---
erzeugt: 2c96442a15f4
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4.11, (51)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4.11, (51)

*In der Herleitung: «Längszugkraft aus der Querkraft, je zur Hälfte an beiden Gurten: ein Zug in der Achse»*

$$
F_{tVd} = \left|V\right| \cdot \cot \alpha
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\left\vert V\right\vert $ | Querkraft dort, als Betrag | kN | Zwischenwert |
| $\alpha$ | Neigung der Druckdiagonalen | ° | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
F_{tVd} = \left|V\right| \cdot \cot \alpha = 4.6\,\mathrm{kN} \cdot \cot 30{}^{\circ} = 8\,\mathrm{kN}
$$

## Gebraucht von

- [[Normalkraft mit der Längszugkraft aus der Querkraft]]

## Im Code

- [[opencivil.pfahl.innen_quer#InnererQuerwiderstand._biegung|InnererQuerwiderstand._biegung]]

## Themen

- [[Innerer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im Fachwerk drücken die Diagonalen schräg: ein Teil ihrer Kraft wirkt längs
des Pfahls, und den nehmen die Längsstäbe als Zug auf, je zur Hälfte im Zug-
und im Druckgurt (SIA 262:2025, 4.3.3.4.11, (51)). Mit der Wendel senkrecht
zur Achse fällt cot β weg. Je flacher die Diagonalen, desto grösser der Zug:
bei 30° das 1.73-fache der Querkraft, bei 45° gleich viel.

H = 100 kN am Kopf, α = 30°: F_tVd = 173 kN. Der Mikropfahl hat kein
Fachwerk und darum keine solche Kraft.
