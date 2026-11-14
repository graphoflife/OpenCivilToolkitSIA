---
erzeugt: 9fe91a31f59d
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Dehnsteifigkeit des Pfahls»*

$$
EA = E_{cm} \cdot \frac{\pi \cdot D^{2}}{4}
$$

*In der Herleitung: «Dehnsteifigkeit des Pfahls»*

$$
EA = E_s \cdot \frac{\pi \cdot \left(\varnothing - 2 \cdot \Delta t\right)^{2}}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $D$ | Durchmesser des Pfahls | mm | Vorgabe |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |
| $\varnothing$ | Durchmesser des Stabs | mm | Vorgabe |
| $\Delta t$ | Abrostung aussen | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
EA = E_{cm} \cdot \frac{\pi \cdot D^{2}}{4} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot \frac{\pi \cdot \left(900\,\mathrm{mm}\right)^{2}}{4} = 21388\,\mathrm{MN}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
EA = E_s \cdot \frac{\pi \cdot \left(\varnothing - 2 \cdot \Delta t\right)^{2}}{4} = 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot \frac{\pi \cdot \left(40\,\mathrm{mm} - 2 \cdot 2\,\mathrm{mm}\right)^{2}}{4} = 204\,\mathrm{MN}
$$

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit._querschnitt|Pfahlsteifigkeit._querschnitt]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark sich der Pfahl unter einer Normalkraft verkürzt: Elastizitätsmodul
mal Fläche. Beim Bohrpfahl zählt der ganze Betonquerschnitt mit E_cm,
ungerissen und ohne die Bewehrung; beim Mikropfahl nur das Tragglied aus
Stahl nach der Abrostung, der Verpresskörper nicht. Beides ist nach Vorgabe
gewählt, nicht nachgeschlagen. Ein Bohrpfahl ⌀ 900 mm aus C30/37:
33 620 N/mm² · 0.636 m² ≈ 21 400 MN.
