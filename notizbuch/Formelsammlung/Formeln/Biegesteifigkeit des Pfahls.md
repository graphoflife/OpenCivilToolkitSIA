---
erzeugt: 3d0e7bab0e14
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Biegesteifigkeit des Pfahls»*

$$
EI = E_{cm} \cdot \frac{\pi \cdot D^{4}}{64}
$$

*In der Herleitung: «Biegesteifigkeit des Pfahls»*

$$
EI = E_s \cdot \frac{\pi \cdot \left(\varnothing - 2 \cdot \Delta t\right)^{4}}{64}
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
EI = E_{cm} \cdot \frac{\pi \cdot D^{4}}{64} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \cdot \frac{\pi \cdot \left(900\,\mathrm{mm}\right)^{4}}{64} = 1082.8\,\mathrm{MNm}^{2}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
EI = E_s \cdot \frac{\pi \cdot \left(\varnothing - 2 \cdot \Delta t\right)^{4}}{64} = 200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot \frac{\pi \cdot \left(40\,\mathrm{mm} - 2 \cdot 2\,\mathrm{mm}\right)^{4}}{64} = 0\,\mathrm{MNm}^{2}
$$

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit._querschnitt|Pfahlsteifigkeit._querschnitt]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark sich der Pfahl unter einem Moment krümmt: Elastizitätsmodul mal
Trägheitsmoment, mit denselben Annahmen wie bei der Dehnsteifigkeit -- der
Beton ungerissen und ohne Bewehrung, beim Mikropfahl nur der Stahl.
⌀ 900 mm aus C30/37: 33 620 N/mm² · 0.0322 m⁴ ≈ 1080 MNm².

Ein gerissener Pfahl ist weicher. Am Kopf verschiebt er sich dann weiter,
das grösste Moment wird etwas kleiner, weil er sich auf kürzerer Länge in
den Boden biegt. Ungerissen liegt die Rechnung für das Moment auf der
sicheren Seite, für die Verschiebung nicht.
