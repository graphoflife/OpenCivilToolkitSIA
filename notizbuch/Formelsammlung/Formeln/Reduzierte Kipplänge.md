---
erzeugt: 16c034367142
art: formel
tags: [formel]
normstelle: "SIA 263:2013, Anhang B.5, (93)"
---
> [!info] Normstelle
> SIA 263:2013, Anhang B.5, (93)

$$
L_{K} = \frac{L_{D}}{\sqrt{\eta}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $L_{D}$ | Kipplänge | mm | Zwischenwert |
| $\eta$ | Beiwert der Momentenverteilung beim Kippen | – | [[Beiwert η der Momentenverteilung beim Kippen]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
L_{K} = \frac{L_{D}}{\sqrt{\eta}} = \frac{3000\,\mathrm{mm}}{\sqrt{1.75}} = 2267.8\,\mathrm{mm}
$$

## Gebraucht von

- [[Wölbanteil der Kippspannung]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.kippen|_Herleitung.kippen]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im Wölbanteil knickt der Druckgurt wie ein Stab zwischen den Punkten,
an denen er seitlich gehalten ist. Ein Moment, das zum Ende hin abfällt,
drückt den Gurt nicht überall gleich; das wirkt wie eine kürzere
Knicklänge. (93) teilt die Kipplänge dafür durch $\sqrt{\eta}$ – siehe
[[Beiwert η der Momentenverteilung beim Kippen]].
