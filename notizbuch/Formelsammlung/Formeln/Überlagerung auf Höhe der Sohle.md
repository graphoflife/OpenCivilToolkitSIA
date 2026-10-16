---
erzeugt: 58bc1da03ced
art: formel
tags: [formel]
normstelle: ["Kap. 9.2.8", "Kap. 9.2.17"]
---
> [!info] Normstellen
> Kap. 9.2.8 · Kap. 9.2.17

*In der Herleitung: «Überlagerung auf Höhe der Sohle, Grundwasser tiefer»*

$$
\sigma_{v,0} = \gamma \cdot t + q_{Ed}
$$

*In der Herleitung: «Überlagerung auf Höhe der Sohle, Lage 1: Grundwasser über der Sohle»*

$$
\sigma_{v,0} = \gamma \cdot t_1 + \gamma' \cdot \left(t - t_1\right) + q_{Ed}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\gamma$ | Raumlast des Bodens | kN/m³ | Vorgabe |
| $t$ | Tiefe der Sohle unter Terrain | m | Vorgabe |
| $q_{Ed}$ | Bemessungslast neben dem Fundament | kPa | Vorgabe |
| $t_1$ | Tiefe des höchsten Grundwasserspiegels unter Terrain | m | Vorgabe |
| $\gamma'$ | Raumlast des Bodens unter Auftrieb | kN/m³ | [[Raumlast unter Auftrieb]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\sigma_{v,0} = \gamma \cdot t + q_{Ed} = 21\,\mathrm{kN}/\mathrm{m}^{3} \cdot 1.2\,\mathrm{m} + 0\,\mathrm{kPa} = 25.2\,\mathrm{kPa}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \sigma_{v,0} &= \gamma \cdot t_1 + \gamma' \cdot \left(t - t_1\right) + q_{Ed} \\
  &= 21\,\mathrm{kN}/\mathrm{m}^{3} \cdot 0.4\,\mathrm{m} + 11\,\mathrm{kN}/\mathrm{m}^{3} \cdot \left(1\,\mathrm{m} - 0.4\,\mathrm{m}\right) + 0\,\mathrm{kPa} \\
  &= 15\,\mathrm{kPa}
\end{aligned}
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch._grundwasser|Grundbruch._grundwasser]]
- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._undrainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die lotrechte Spannung im Boden neben dem Fundament, auf Höhe der Sohle. Sie
hält den Gleitkörper nieder und geht mit $N_q$ in die Formel ein.

Sie ist das Gewicht des Bodens über der Sohle und die Auflast $q$. Steht
Grundwasser über der Sohle (Bild 9.2.10, Lage 1 und 2), zählt unter dem
Spiegel nur [[Raumlast unter Auftrieb|γ']]. Undrainiert zählen die totalen
Spannungen; das Wasser spielt dort keine Rolle.
