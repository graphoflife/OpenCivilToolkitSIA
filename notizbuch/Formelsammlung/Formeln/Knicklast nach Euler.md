---
erzeugt: 15b7d6299798
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 4.5.1.4"
---
> [!info] Normstelle
> SIA 263:2013, 4.5.1.4

*In der Herleitung: «Knicklast um y»*

$$
N_{cr,y} = \frac{\pi^2 \cdot E_{a} \cdot I_y}{L_{K,y}^2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{a}$ | Elastizitätsmodul des Baustahls | N/mm² | Vorgabe |
| $I_y$ | Trägheitsmoment um y | ·10⁶ mm⁴ | Zwischenwert |
| $L_{K,y}$ | Knicklänge | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{cr,y} = \frac{\pi^2 \cdot E_{a,\text{S355}} \cdot I_y}{L_{K,y}^2} = \frac{\pi^2 \cdot 210000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 921.2\,\cdot 10^{6}\,\mathrm{mm}^{4}}{\left(6000\,\mathrm{mm}\right)^2} = 53037\,\mathrm{kN}
$$

## Gebraucht von

- [[Abgeminderter Biegewiderstand um die schwache Achse]]
- [[Abgeminderter Kippwiderstand im Stab]]
- [[Schlankheit beim Knicken]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.knicken|_Herleitung.knicken]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Druckkraft, bei der ein vollkommen gerader, elastischer Stab neben
der geraden Lage auch eine ausgebogene im Gleichgewicht hat. Sie wächst
mit der Biegesteifigkeit $E \cdot I$ und fällt mit dem Quadrat der
Knicklänge: doppelt so lang heisst ein Viertel.

Die Knicklänge ist die Länge der Halbwelle, in die der Stab ausweicht –
bei gelenkigen Enden seine Länge. Sie gilt je Achse; um eine gehaltene
Achse, $L_K = 0$, knickt der Stab nicht. In Klasse 4 gilt der ganze
Querschnitt (5.3.8).
