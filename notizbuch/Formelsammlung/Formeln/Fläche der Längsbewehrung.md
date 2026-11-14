---
erzeugt: b45d37bf7e04
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
A_s = n \cdot \frac{\pi \cdot \varnothing_l^{2}}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $n$ | Zahl der Längsstäbe | – | Vorgabe |
| $\varnothing_l$ | Durchmesser der Längsstäbe | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
A_s = n \cdot \frac{\pi \cdot \varnothing_l^{2}}{4} = 12 \cdot \frac{\pi \cdot \left(20\,\mathrm{mm}\right)^{2}}{4} = 3770\,\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Materialwiderstand auf Druck]]
- [[Materialwiderstand des Stahls]]

## Im Code

- [[opencivil.pfahl.innen#InnererWiderstand|InnererWiderstand._bohrpfahl]]

## Themen

- [[Innerer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Stäbe, die längs im Pfahl liegen, alle gleich dick. Sie tragen auf Druck
mit dem Beton und auf Zug allein. Zwölf Stäbe ⌀ 20 geben 3770 mm², 0.59 %
eines Querschnitts von ⌀ 900.
