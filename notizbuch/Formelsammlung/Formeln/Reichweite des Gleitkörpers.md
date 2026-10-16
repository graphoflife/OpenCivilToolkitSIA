---
erzeugt: 368b15c8a666
art: formel
tags: [formel]
normstelle: "Kap. 9.2.10"
---
> [!info] Normstelle
> Kap. 9.2.10

$$
L_{Gl} = b \cdot \tan\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \cdot e^{\frac{\pi}{2} \tan \varphi_{eff}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b$ | Breite des Fundaments | m | Vorgabe |
| $\varphi_{eff}$ | Reibungswinkel, Bemessungswert | ° | [[Bemessungswert des Reibungswinkels]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  L_{Gl} &= b \cdot \tan\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \cdot e^{\frac{\pi}{2} \tan \varphi_{eff}} \\
  &= 2\,\mathrm{m} \cdot \tan\left(45^\circ + \frac{27.51{}^{\circ}}{2}\right) \cdot e^{\frac{\pi}{2} \tan 27.51{}^{\circ}} \\
  &= 7.47\,\mathrm{m}
\end{aligned}
$$

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie weit der Gleitkörper neben dem Fundament an die Oberfläche tritt,
gemessen ab der Sohlkante auf Höhe der Sohle. Er besteht aus dem Keil unter
dem Fundament, der logarithmischen Spirale und dem äusseren Keil unter
$45° - \varphi/2$.

Mit wachsendem $\varphi$ reicht er weit hinaus: bei $\varphi = 30°$ etwa
4.3-mal die Breite $b$. Was in diesem Bereich abgegraben oder aufgeschüttet
wird, ändert die Tragfähigkeit. Die Formel gilt für waagrechte Sohle und
waagrechtes Gelände; das Bild der Situation zeichnet ihn so.
