---
erzeugt: 146e8003e49c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\rho = \frac{n \cdot A_{s,2,x}}{b}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $n$ | – | – | Zwischenwert |
| $A_{s,2,x}$ | – | mm² | [[Bewehrung der Lage]] |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\rho = \frac{n \cdot A_{s,2,x}}{b} = \frac{17.85 \cdot 2450\,\mathrm{mm}^{2}}{1000\,\mathrm{mm}} = 43.73\,\mathrm{mm}
$$

## Gebraucht von

- [[Nulllinie des gerissenen Querschnitts]]

## Im Code

- [[opencivil.nachweis.mindestbewehrung#ZwaengungBiegung|ZwaengungBiegung._protokoll_lage]]

## Themen

- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Länge, keine Bewehrungsquote: die in Beton umgerechnete Stahlfläche
$n \cdot A_s$, verteilt auf die Breite $b$. Mit ihr wird die Gleichung für die
[[Nulllinie des gerissenen Querschnitts]] kurz. Nicht zu verwechseln mit dem
[[Bewehrungsgehalt]], der dasselbe Zeichen trägt.
