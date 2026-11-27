---
erzeugt: 620f00643ce0
art: formel
tags: [formel]
normstelle: "nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Das Moment ändert sich über Δx um»*

$$
\Delta M = V_z \cdot \Delta x
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $V_z$ | Querkraft des Falls | kN | Zwischenwert |
| $\Delta x$ | Abstand der beiden Zustände längs des Bauteils, nach Vorgabe | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\Delta M = V_z \cdot \Delta x = 300\,\mathrm{kN} \cdot 10\,\mathrm{mm} = 3\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.nachweis.qa_schubfluss#SchubflussQA._fall|SchubflussQA._fall]]

## Themen

- [[Schubfluss]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Längs des Bauteils ändert sich das Moment mit der Querkraft,
$dM/dx = V$. Über $\Delta x = 10$ mm wächst es also um $V \cdot \Delta x$,
bei $V = 300$ kN um 3 kNm. Die Länge ist nach Vorgabe, nicht
nachgeschlagen: klein genug, dass sich der Zustand des Querschnitts kaum
ändert, und gross genug, dass die Suche der beiden Dehnungsebenen den
Unterschied genau trifft. Das Moment wächst im Betrag: $\Delta M$ hat das
Vorzeichen von $M$, ohne Moment das positive. Gibt es bei $M + \Delta M$
keine Gleichgewichtslage mehr, gilt der Schritt zurück, $M - \Delta M$.
