---
erzeugt: a845515e6da5
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

- [[opencivil.nachweis.querkraft_ohne_buegel#QuerkraftOhneBuegel._protokoll_fall|QuerkraftOhneBuegel._protokoll_fall]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Normaldruckkraft $N_{Ed}$ in der halben Höhe drückt den Rand mit
$N/A$. Ein Moment $m$ zieht ihn mit $m/W$, bei $W = h^2/6$ je Laufmeter --
der Rand ist wieder spannungsfrei bei $m = |N| \cdot h/6$. Bis dahin reisst
nichts, und die Bewehrung bekommt keine Dehnung.

Nur Druck entlastet: eine Zugkraft bleibt hier unberücksichtigt.
