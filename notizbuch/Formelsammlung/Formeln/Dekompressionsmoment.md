---
erzeugt: 41bd9625878b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{Ed}$ | – | kN | Zwischenwert |
| $h$ | Plattendicke | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
m_{Dd} = \frac{\left|\min(N_{Ed};\ 0)\right| \cdot h}{6} = \frac{\left|\min(0\,\mathrm{kN};\ 0)\right| \cdot 200\,\mathrm{mm}}{6} = 0\,\mathrm{kNm}
$$

## Gebraucht von

- [[Dehnung auf halber Höhe]]

## Im Code

- [[opencivil.nachweis.querkraft#Querkraft._protokoll_fall|Querkraft._protokoll_fall]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
