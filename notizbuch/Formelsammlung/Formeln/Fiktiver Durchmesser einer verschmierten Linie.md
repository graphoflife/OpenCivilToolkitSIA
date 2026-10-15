---
erzeugt: d01c5977671b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Linie 3: verschmiert, als Stäbe mit 150 mm Teilung»*

$$
\varnothing_{fikt} = \sqrt{\frac{4}{\pi} \cdot \frac{A_s}{l} \cdot s}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_s$ | Stahlfläche der Linie | mm² | Zwischenwert |
| $l$ | Länge der Linie | mm | Zwischenwert |
| $s$ | Angenommene Teilung | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varnothing_{fikt} = \sqrt{\frac{4}{\pi} \cdot \frac{A_s}{l} \cdot s} = \sqrt{\frac{4}{\pi} \cdot \frac{400\,\mathrm{mm}^{2}}{300\,\mathrm{mm}} \cdot 150\,\mathrm{mm}} = 16\,\mathrm{mm}
$$

## Im Code

- [[opencivil.nachweis.stabgrenzen#_protokoll_fiktiv|_protokoll_fiktiv]]

## Themen

- [[Zwängung auf Normalkraft]]
- [[Zwängung auf Biegung]]
- [[Stahlspannung aus Rissbreite]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die zulässige Stahlspannung aus der Rissbreite hängt am Durchmesser: ein Riss
verteilt sich auf die Stäbe, die ihn kreuzen, und bei gleicher Fläche sind es
um so mehr, je dünner sie sind. Eine verschmierte Linie trägt nur eine
Fläche, keinen Durchmesser. Sie wird darum gelesen, als lägen ihre Stäbe in
der Teilung $s = 150\,\mathrm{mm}$: jeder Stab hat die Fläche
$A_s / l \cdot s$, und sein Durchmesser ist der eines Kreises dieser Fläche.
Eine grössere Teilung gäbe dickere Stäbe und damit eine kleinere zulässige
Spannung. Die 150 mm sind eine Annahme des Benutzers vom 2026-10-15, keine
Normstelle.
