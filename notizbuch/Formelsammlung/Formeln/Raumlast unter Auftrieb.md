---
erzeugt: b1516e258e43
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Raumlast des Bodens unter Auftrieb»*

$$
\gamma' = \gamma - \gamma_w
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\gamma$ | Raumlast des Bodens | kN/m³ | Vorgabe |
| $\gamma_w$ | Raumlast des Wassers | kN/m³ | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\gamma' = \gamma - \gamma_w = 21\,\mathrm{kN}/\mathrm{m}^{3} - 10\,\mathrm{kN}/\mathrm{m}^{3} = 11\,\mathrm{kN}/\mathrm{m}^{3}
$$

## Gebraucht von

- [[Raumlast im Gleitkörper]]
- [[Überlagerung auf Höhe der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch|_gamma_auftrieb]]

## Themen

- [[Fundament]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Unter dem Grundwasserspiegel trägt das Wasser einen Teil des Bodengewichts:
jedes Korn erfährt Auftrieb. Für die wirksamen Spannungen zählt darum nur
$\gamma' = \gamma - \gamma_w$. Mit $\gamma = 21$ und
$\gamma_w = 10\ \mathrm{kN/m^3}$ bleibt etwa die Hälfte.

Wo das Wasser steht, entscheidet die [[Überlagerung auf Höhe der Sohle]] und
die [[Raumlast im Gleitkörper]].
