---
erzeugt: f61ff048f9e6
art: formel
tags: [formel]
normstelle: "Kap. 9.2.10"
---
> [!info] Normstelle
> Kap. 9.2.10

$$
H_{Gl} = b \cdot \frac{\cos \varphi_{eff}}{2 \cos\left(45^\circ + \frac{\varphi_{eff}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \tan \varphi_{eff}}
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
  H_{Gl} &= b \cdot \frac{\cos \varphi_{eff}}{2 \cos\left(45^\circ + \frac{\varphi_{eff}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{\varphi_{eff}}{2}\right) \tan \varphi_{eff}} \\
  &= 2\,\mathrm{m} \cdot \frac{\cos 27.51{}^{\circ}}{2 \cos\left(45^\circ + \frac{27.51{}^{\circ}}{2}\right)} \cdot e^{\frac{\pi}{180^\circ}\left(45^\circ + \frac{27.51{}^{\circ}}{2}\right) \tan 27.51{}^{\circ}} \\
  &= 2.92\,\mathrm{m}
\end{aligned}
$$

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie tief die Gleitfläche unter die Sohle reicht: die tiefste Stelle der
logarithmischen Spirale, bei $\varphi = 30°$ etwa 1.6-mal die Breite $b$.

Die Tiefe entscheidet, ob ein Grundwasserspiegel unter der Sohle das Gewicht
des Gleitkörpers mindert: liegt er um mindestens $H$ tiefer, bleibt der
Gleitkörper trocken (Bild 9.2.10, Lage 3).
