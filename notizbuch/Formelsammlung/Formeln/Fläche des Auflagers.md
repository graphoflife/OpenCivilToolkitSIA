---
erzeugt: a8d92d8da300
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
A_0 = a \cdot t_w
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $a$ | Auflagerlänge des Sturzes | mm | Zwischenwert |
| $t_w$ | Dicke der Wand | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
A_0 = a \cdot t_w = 150\,\mathrm{mm} \cdot 175\,\mathrm{mm} = 26250\,\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Beiwert der Teilflächenpressung im Mauerwerk]]
- [[Widerstand eines Sturzauflagers]]

## Im Code

- [[opencivil.mauerwerk.nachweise#Teilflaechen.stelle|Teilflaechen.stelle]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Sturz liegt an jedem Ende auf der Länge $a$ auf dem Mauerwerk auf. Das
Werkzeug nimmt an, er sei so breit wie die Wand dick ist – nach Vorgabe,
nicht nachgeschlagen. Auf diese Fläche drückt seine Auflagerkraft.
