---
erzeugt: a9190df47208
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 8.5.2.2"
---
> [!info] Normstelle
> SIA 267:2013, 8.5.2.2

*In der Herleitung: «Sohlreibungswinkel, Bemessungswert»*

$$
\delta_d = \arctan\left(\frac{\tan \delta_k}{\gamma_{\varphi}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\delta_k$ | Sohlreibungswinkel, charakteristisch | ° | [[Reibungswinkel der Sohlfuge]] |
| $\gamma_{\varphi}$ | Partialfaktor des Reibungswinkels | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\delta_d = \arctan\left(\frac{\tan \delta_k}{\gamma_{\varphi}}\right) = \arctan\left(\frac{\tan 32{}^{\circ}}{1.2}\right) = 27.51{}^{\circ}
$$

## Gebraucht von

- [[Gleitwiderstand]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Gleiten._sohlreibung|Gleiten._sohlreibung]]

## Themen

- [[Gleiten]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie beim [[Bemessungswert des Reibungswinkels]] teilt der Partialfaktor den
Tangens und nicht den Winkel, denn die Reibung wächst mit
$\tan\delta$: $\tan\delta_d = \tan\delta_k/\gamma_{\varphi}$ (SIA 267:2013,
8.5.2.2, mit $\gamma_{\varphi}$ aus Tabelle 1). Die Grenze von 35° gilt
vorher, für $\delta_k$.

Mit $\varphi_k = 40°$, $k_{\delta} = 1$ und $\gamma_{\varphi} = 1.2$ wird
$\delta_k = 35°$ und $\delta_d = 30.3°$. Ohne die Grenze wäre es
$\varphi_{eff} = 35.0°$, und der [[Gleitwiderstand]] läge um 20 % höher.
