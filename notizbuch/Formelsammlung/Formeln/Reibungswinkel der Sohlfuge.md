---
erzeugt: 541a2cd751e5
art: formel
tags: [formel]
normstelle: "Kap. 9.2.18"
---
> [!info] Normstelle
> Kap. 9.2.18

$$
\delta^{*} = k_{\delta} \cdot \varphi_{eff}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_{\delta}$ | Sohlreibungswinkel im Verhältnis zum Reibungswinkel, δ\*/φ | – | Vorgabe |
| $\varphi_{eff}$ | Reibungswinkel, Bemessungswert | ° | [[Bemessungswert des Reibungswinkels]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\delta^{*} = k_{\delta} \cdot \varphi_{eff} = 1 \cdot 27.51{}^{\circ} = 27.51{}^{\circ}
$$

## Gebraucht von

- [[Gleitwiderstand]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Gleiten.pruefe|Gleiten.pruefe]]

## Themen

- [[Gleiten]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Reibung zwischen Fundament und Boden ist meist kleiner als die im Boden
selbst; das Kapitel nennt für $\delta^{*}$ etwa $2/3\,\varphi$ bis
$1 \cdot \varphi$. Das Werkzeug fragt nach dem Verhältnis
$k_{\delta} = \delta^{*}/\varphi$ und rechnet es mit dem Bemessungswert
$\varphi_{eff}$.
