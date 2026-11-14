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
mit dem E eines eigenen Materials sonst, bei Stahl etwa $E_s$, am
ungerissenen Bruttoquerschnitt. So sieht es die Norm für die Analyse in der
Regel vor: ungerissen, mit dem Mittelwert. Dass die Bewehrung nicht
mitzählt, ist eine Vereinfachung, der Stab wird damit etwas weicher. Ein
gerissener Betonstab ist noch weicher; das darf man mit einer begründeten
Abschätzung ansetzen, etwa mit dem [[Äquivalenter E-Modul eines Stabs|äquivalenten Modul]].
