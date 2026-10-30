---
erzeugt: 785a8cdcd08b
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.3"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.3

*In der Herleitung: «Wirksamer Umfang des äusseren Nachweisschnitts, mit k\_e von innen»*

$$
u_{out} = k_e \cdot u_{out,red}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_e$ | – | – | Zwischenwert, [[Beiwert der Momentenübertragung]] |
| $u_{out,red}$ | – | mm | [[Äusserer Nachweisschnitt ohne das, was nicht zählt]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
u_{out} = k_e \cdot u_{out,red} = 0.9 \cdot 6619\,\mathrm{mm} = 5957\,\mathrm{mm}
$$

## Gebraucht von

- [[Durchstanzwiderstand im äusseren Nachweisschnitt]]

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#nachweisen|nachweisen]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der äussere Schnitt ([[Äusserer Nachweisschnitt ohne das, was nicht zählt]]),
mit $k_e$ gemindert wie der innere. Genommen wird das $k_e$ des inneren
Schnitts: aus der Näherung ist es dasselbe, aus der Exzentrizität wäre es
aussen grösser, der Wert von innen liegt auf der sicheren Seite.
