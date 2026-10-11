---
erzeugt: 9af49d08f88d
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

## Gebraucht von

- [[Erfüllungsgrad]]

## Im Code

- `opencivil.nachweis.querkraft:Querkraft._protokoll_ansatz`
- `opencivil.nachweis.querkraft:Querkraft._protokoll_fall`

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
