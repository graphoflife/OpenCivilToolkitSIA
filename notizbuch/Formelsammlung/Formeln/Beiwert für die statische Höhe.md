---
erzeugt: 26a55df7636b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} \quad \left(d\ \text{in}\ \mathrm{mm}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varepsilon_v$ | – | ‰ | [[Dehnung auf halber Höhe]] |
| $d$ | – | mm | [[Statische Höhe]] |
| $k_g$ | – | – | [[Beiwert der Gesteinskörnung]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
k_d = \frac{1}{1 + \varepsilon_v \cdot d \cdot k_g} = \frac{1}{1 + 3.261\,\text{‰} \cdot 165 \cdot 1.2} = 0.6077 \quad \left(d\ \text{in}\ \mathrm{mm}\right)
$$

## Gebraucht von

- [[Querkraftwiderstand ohne Querkraftbewehrung]]

## Im Code

- [[opencivil.nachweis.querkraft#Querkraft._protokoll_fall|Querkraft._protokoll_fall]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Fasst zusammen, wie weit sich der kritische Schubriss öffnet: mit der
[[Dehnung auf halber Höhe]], mit der statischen Höhe -- grosse Bauteile
haben breitere Risse, der Massstabseffekt -- und mit der
[[Beiwert der Gesteinskörnung|Gesteinskörnung]]. Je grösser das Produkt,
desto kleiner $k_d$ und desto weniger Querkraft trägt der Beton. Wie bei
$\tau_{cd}$ ist die Formel empirisch: $d$ geht in mm ein.
