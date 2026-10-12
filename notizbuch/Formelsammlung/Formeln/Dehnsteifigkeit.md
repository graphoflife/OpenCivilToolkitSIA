---
erzeugt: de1e745a0fc8
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Dehnsteifigkeit, «Stütze 300×300» aus C30/37»*

$$
EA_{\text{Q1}} = E_{cm} \cdot A_{\text{Q1}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $A_{\text{Q1}}$ | Querschnittsfläche, Stütze 300×300 | mm² | [[Fläche eines Rechtecks]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
EA_{\text{Q1}} = E_{cm} \cdot A_{\text{Q1}} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot 90000\,\mathrm{mm}^{2} = 3026\,\mathrm{MN}
$$

## Im Code

- [[opencivil.stabwerk.rechnung|_dehnsteifigkeit]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark sich ein Stab gegen eine Längskraft wehrt: $N = EA \cdot \varepsilon$.
Gerechnet wird mit dem [[Mittelwert des Elastizitätsmoduls]] beim Beton und
mit $E_s$ beim Stahl, am ungerissenen Bruttoquerschnitt. Das ist eine Annahme
nach Vorgabe, nicht nachgeschlagen: ein gerissener Betonstab ist weicher, und
die Bewehrung zählt hier nicht mit.
