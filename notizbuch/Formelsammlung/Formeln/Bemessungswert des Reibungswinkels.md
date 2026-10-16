---
erzeugt: 6fbcb1a49568
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 5.3.2.1"
---
> [!info] Normstelle
> SIA 267:2013, 5.3.2.1

*In der Herleitung: «Reibungswinkel, Bemessungswert»*

$$
\varphi_{eff} = \arctan\left(\frac{\tan \varphi_k}{\gamma_{\varphi}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varphi_k$ | Reibungswinkel, charakteristisch | ° | Vorgabe |
| $\gamma_{\varphi}$ | Partialfaktor des Reibungswinkels | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\varphi_{eff} = \arctan\left(\frac{\tan \varphi_k}{\gamma_{\varphi}}\right) = \arctan\left(\frac{\tan 32{}^{\circ}}{1.2}\right) = 27.51{}^{\circ}
$$

## Gebraucht von

- [[Formfaktor s_q]]
- [[Lastneigungsfaktor i_q]]
- [[Lastneigungsfaktor i_γ]]
- [[Reibungswinkel der Sohlfuge]]
- [[Reichweite des Gleitkörpers]]
- [[Sohlneigungsfaktor b_q]]
- [[Sohlneigungsfaktor b_γ]]
- [[Tiefe des Gleitkörpers]]
- [[Tiefenfaktor d_q]]
- [[Tragfähigkeitsfaktor N_c]]
- [[Tragfähigkeitsfaktor N_q]]
- [[Tragfähigkeitsfaktor N_γ]]

## Im Code

- [[opencivil.geotechnik.grundbruch|_phi_eff]]

## Themen

- [[Fundament]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Scherfestigkeit eines reibenden Bodens wächst mit $\tan\varphi$, nicht
mit dem Winkel selbst. Darum teilt der Partialfaktor den Tangens,
$\tan\varphi_{eff} = \tan\varphi_k / \gamma_{\varphi}$, und erst daraus
folgt der Winkel: mit $\gamma_{\varphi} = 1.2$ wird aus $\varphi_k = 30°$
der Bemessungswert $\varphi_{eff} = 25.7°$.

Alle Faktoren der Tragfähigkeitsformel und die Reibung in der Sohle rechnen
mit $\varphi_{eff}$. Die Sicherheit steckt damit im Boden und nicht in einem
globalen Faktor auf der Bruchlast.
