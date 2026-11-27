---
erzeugt: b4ed6440c41a
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\gamma_{fl} = \rho_{fl} \cdot g
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\rho_{fl}$ | Dichte der Flüssigkeit | kg/m³ | Vorgabe |
| $g$ | Erdbeschleunigung | m/s² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\gamma_{fl} = \rho_{fl} \cdot g = 1000\,\mathrm{kg}/\mathrm{m}^{3} \cdot 10\,\mathrm{m}/\mathrm{s}^{2} = 10\,\mathrm{kN}/\mathrm{m}^{3}
$$

## Gebraucht von

- [[Raumlast des Grundwassers]]

## Im Code

- [[opencivil.material.fluessigkeit]]

## Themen

- [[Flüssigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Flüssigkeit trägt nichts, sie wiegt nur: Ihre Raumlast ist die Dichte
mal die Erdbeschleunigung. Mit $g = 10\ \mathrm{m/s^2}$ wie beim Eigengewicht
wiegt das Wasser mit $\rho_{fl} = 1000\ \mathrm{kg/m^3}$ genau
$10\ \mathrm{kN/m^3}$ – die Zahl, die Grundbruch und Pfahl bis 2026-11-27
als Vorgabe im Feld $\gamma_w$ hatten.

Die Dichte des Wassers ist nach Vorgabe, nicht nachgeschlagen: SIA 261:2020
rechnet den Wasserdruck mit der Raumlast $\gamma_{w,k}$ (4.4.2.1, Gl. (8)),
nennt dafür aber keine Zahl. Eine andere Flüssigkeit, Salzwasser oder eine
Bentonitsuspension, legt man als eigene an, mit ihrer Dichte. Wer die
Raumlast selbst kennt, überschreibt $\gamma_{fl}$ direkt.

Gebraucht wird sie als [[Raumlast des Grundwassers]].
