---
erzeugt: f28fef8854ec
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Eigengewicht, «Stütze 300×300» aus C30/37»*

$$
g_{k} = \rho_{sb} \cdot g \cdot A_{\text{Q1}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\rho_{sb}$ | Dichte des Stahlbetons | kg/m³ | Vorgabe |
| $g$ | Erdbeschleunigung | m/s² | Vorgabe |
| $A_{\text{Q1}}$ | Querschnittsfläche, Stütze 300×300 | mm² | [[Fläche eines Rechtecks]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
g_{k,\text{Q1}} = \rho_{sb} \cdot g \cdot A_{\text{Q1}} = 2500\,\mathrm{kg}/\mathrm{m}^{3} \cdot 10\,\mathrm{m}/\mathrm{s}^{2} \cdot 90000\,\mathrm{mm}^{2} = 2.25\,\mathrm{kN}/\mathrm{m}
$$

## Im Code

- [[opencivil.stabwerk.rechnung#Balkensystem._eigengewicht|_eigengewicht]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was ein Stab je Meter seiner Länge wiegt: Dichte mal Erdbeschleunigung mal
Querschnittsfläche. Beim Beton gilt die Dichte des Stahlbetons, 2500 kg/m³ --
sie schliesst die Bewehrung schon ein, der Stahl kommt nicht noch einmal dazu.
Beim Stahl gilt seine Dichte, 7850 kg/m³. g ist auf 10 m/s² gerundet
(Benutzer, 2026-10-23).

Die Last zeigt senkrecht nach unten und liegt auf der ganzen Länge des Stabs,
je Meter Stab und nicht je Meter Grundriss: ein schräger Stab ist länger und
wiegt darum mehr. Sie gehört in den einen Lastfall, der das Eigengewicht
bekommt. Eine Linie ohne Querschnitt ist kein Stab und wiegt nichts.
