---
erzeugt: c8b7c768bef1
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.4.3.2.5"
---
> [!info] Normstelle
> SIA 262:2025, 4.4.3.2.5

*In der Herleitung: «Vergrösserungsfaktor der Durchbiegung – allgemein»*

$$
\frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3} \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}
$$

*In der Herleitung: «Vergrösserungsfaktor, Zug unten»*

$$
\left(\frac{w}{w_c}\right)_{u} = \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{u}}\right)^{3}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\rho_{o}$ | – | – | [[Bewehrungsgehalt]] |
| $\rho_{u}$ | – | – | [[Bewehrungsgehalt]] |
| $\varphi$ | Kriechzahl | – | Vorgabe |
| $h$ | Plattendicke | mm | Vorgabe |
| $d_{u}$ | – | mm | [[Statische Höhe]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  \left(\frac{w}{w_c}\right)_{u} &= \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{u}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00299}{10 \cdot 0.00988^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{300\,\mathrm{mm}}{248.1\,\mathrm{mm}}\right)^{3} \\
  &= 4
\end{aligned}
$$

## Im Code

- `opencivil.querschnitt.platte:Lagenaufbau._vergroesserung`

## Themen

- [[Querschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
