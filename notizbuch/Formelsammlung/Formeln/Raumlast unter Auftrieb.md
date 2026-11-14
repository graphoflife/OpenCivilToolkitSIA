---
erzeugt: 55a8e4af5845
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
| $\gamma$ | Raumlast des Bodens, ohne Partialfaktor | kN/m³ | Vorgabe |
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
die Raumlast unter Auftrieb. Das Buch bildet sie aus der gesättigten
Raumlast, $\gamma' = \gamma_g - \gamma_w$ (Kap. 1.4); das Werkzeug kennt
nur eine Raumlast $\gamma$ und nimmt sie auch unter dem Wasser. Ist sie die
feuchte, wird $\gamma'$ etwas kleiner: mit $\gamma = 21$ statt
$\gamma_g = 22\ \mathrm{kN/m^3}$ 11 statt 12, gut 8 % weniger. Das
liegt auf der sicheren Seite, denn $\gamma'$ hält den Gleitkörper nieder.

Wo das Wasser steht, entscheidet die [[Überlagerung auf Höhe der Sohle]] und
die [[Raumlast im Gleitkörper]].
