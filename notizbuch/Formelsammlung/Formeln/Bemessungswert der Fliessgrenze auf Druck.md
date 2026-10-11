---
erzeugt: 8ce74298661a
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 2.4.2.5"
---
> [!info] Normstelle
> SIA 262:2025, 2.4.2.5

$$
f_{yd}^{-} = \frac{f_{yk}^{-}}{\gamma_s}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yk}^{-}$ | Charakteristische Fliessgrenze auf Druck | N/mm² | Vorgabe |
| $\gamma_s$ | Teilsicherheitsbeiwert für Betonstahl | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
f_{yd}^{-} = \frac{f_{yk}^{-}}{\gamma_s} = \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{1.15} = 435\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.material.betonstahl]]

## Themen

- [[Betonstahl]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Auf Druck kann ein Stahl anders fliessen als auf Zug, und die Sortentabelle
darf beide getrennt nennen. Gebraucht wird $f_{yd}^{-}$ überall dort, wo
gedrückte Bewehrung mitträgt: in der Resistenzlinie aus Dehnungsebenen und im
Querschnittslöser. Die Handrechnung lässt gedrückte Bewehrung weg und braucht
sie nicht (siehe [[Betonstahl nur auf Zug]]).

Für die Sorten der Tabelle ist sie gleich $f_{yd}$.
