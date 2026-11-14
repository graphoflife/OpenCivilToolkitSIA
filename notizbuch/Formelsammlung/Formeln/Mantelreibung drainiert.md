---
erzeugt: 3658b348e5be
art: formel
tags: [formel]
normstelle: "Kap. 12.5"
---
> [!info] Normstelle
> Kap. 12.5

*In der Herleitung: «Mantelreibung drainiert, σ'\_v in der Mitte des Stücks»*

$$
q_{s,k} = K \cdot \sigma'_v \cdot \tan\delta \qquad \delta = k_{\delta} \cdot \varphi'_k
$$

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand._mantel|AeussererWiderstand._mantel]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Boden drückt seitlich mit K · σ'_v gegen den Pfahl. Verschiebt sich der
Pfahl genug gegen den Boden, reibt er daran mit dem Winkel δ. An einem rauen
Pfahl ist δ etwa so gross wie φ' (Kap. 12.5). K liegt an Bohrpfählen eher
tiefer als an Rammpfählen und erreicht höchstens etwa den Ruhedruckbeiwert
K_0 = 1 − sin φ' (Kap. 2.7, 12.5); darüber gibt die Rechnung einen Hinweis.

Mit K = 0.5, φ' = 30°, δ = φ' und σ'_v = 100 kN/m² reibt jeder
Quadratmeter Mantel mit 0.5 · 100 · tan 30° = 28.9 kN/m².
