---
erzeugt: 5821cfd57e66
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.2.1"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.2.1

*In der Herleitung: «Zug unten, M\_Ed = M\_Rd»*

$$
V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+}) = k_d^{+} \cdot \tau_{cd} \cdot d_v^{+}
$$

*In der Herleitung: «Ansatz»*

$$
V_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_d^{+}$ | – | – | [[Beiwert für die statische Höhe]] |
| $\tau_{cd}$ | – | N/mm² | Zwischenwert |
| $d_v^{+}$ | – | mm | [[Wirksame Höhe (Einlage nicht massgebend)]], [[Wirksame Höhe, um die Einlage vermindert]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  V_{Rd}^{+}(M_{Ed} = M_{Rd}^{+}) &= k_d^{+} \cdot \tau_{cd} \cdot d_v^{+} \\
  &= 0.6062 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 249\,\mathrm{mm} \\
  &= 165.4\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.querkraft#Querkraft|Querkraft._protokoll_ansatz]]
- [[opencivil.nachweis.querkraft#protokoll_ohne_buegel|protokoll_ohne_buegel]]

## Themen

- [[Kennzahlen]]
- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ohne Bügel begrenzt der kritische Schubriss die Querkraft: über ihn muss die
Kraft durch die Verzahnung der Rissufer, und die trägt umso weniger, je
weiter sich der Riss öffnet. Die Rissöffnung wächst mit der Dehnung der
Platte und mit ihrer Höhe -- das fasst der
[[Beiwert für die statische Höhe]] $k_d$ zusammen. Der Widerstand ist dann
$k_d \cdot \tau_{cd}$ über die wirksame Höhe $d_v$.

Weil die Dehnung vom Moment abhängt, hängt auch der Widerstand von der
Einwirkung ab: er wird für jede Kombination aus Moment und Normalkraft neu
bestimmt, und im Diagramm steht er als Kurve über dem Moment.
