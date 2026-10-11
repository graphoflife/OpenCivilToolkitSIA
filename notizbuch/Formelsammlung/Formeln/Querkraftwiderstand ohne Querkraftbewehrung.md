---
erzeugt: 80f97ad24d6e
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.2.1"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.2.1

*In der Herleitung: «Ansatz»*

$$
V_{Rd} = k_d \cdot \tau_{cd} \cdot d_v \qquad k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g}
$$

*In der Herleitung: «Querkraftwiderstand»*

$$
V_{Rd,x} = k_d \cdot \tau_{cd} \cdot d_v
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_d$ | – | – | [[Beiwert für die statische Höhe]] |
| $\tau_{cd}$ | – | N/mm² | Zwischenwert |
| $d_v$ | – | mm | [[Wirksame Höhe, um die Einlage vermindert]], [[Wirksame Höhe (Einlage nicht massgebend)]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_{Rd,x}(M_{Ed} = 40\,\mathrm{kNm},\ N_{Ed} = 0\,\mathrm{kN}) &= k_d \cdot \tau_{cd} \cdot d_v \\
  &= 0.6077 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 125\,\mathrm{mm} \\
  &= 83.2\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.querkraft#Querkraft|Querkraft._protokoll_ansatz]]
- [[opencivil.nachweis.querkraft#Querkraft._protokoll_fall|Querkraft._protokoll_fall]]

## Themen

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
