---
erzeugt: 7aece4791431
art: formel
tags: [formel]
normstelle: "Kap. 9.2.13"
---
> [!info] Normstelle
> Kap. 9.2.13

*In der Herleitung: «Tiefenfaktor der seitlichen Auflast»*

$$
d_q = 1 + 0.035 \cdot \tan \varphi_{eff} \cdot \left(1 - \sin \varphi_{eff}\right)^{2} \cdot \vartheta_t
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varphi_{eff}$ | Reibungswinkel, Bemessungswert | ° | [[Bemessungswert des Reibungswinkels]] |
| $\vartheta_t$ | Winkel der Einbindetiefe | ° | [[Winkel der Einbindetiefe]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  d_q &= 1 + 0.035 \cdot \tan \varphi_{eff} \cdot \left(1 - \sin \varphi_{eff}\right)^{2} \cdot \vartheta_t \\
  &= 1 + 0.035 \cdot \tan 27.51{}^{\circ} \cdot \left(1 - \sin 27.51{}^{\circ}\right)^{2} \cdot 31{}^{\circ} \\
  &= 1.16
\end{aligned}
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainiert]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für die Auflast wächst der Tiefenfaktor mit
$\tan\varphi\,(1 - \sin\varphi)^2$ -- am stärksten bei mittleren
Reibungswinkeln. Der Faktor des Gleitkörpergewichts bleibt $d_{\gamma} = 1$.
