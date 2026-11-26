---
erzeugt: 87d272cfdec4
art: formel
tags: [formel]
normstelle: "SIA 263:2013, Anhang B.3, (91)"
---
> [!info] Normstelle
> SIA 263:2013, Anhang B.3, (91)

$$
\sigma_{cr,D} = \sqrt{\sigma_{Dv}^2 + \sigma_{Dw}^2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\sigma_{Dv}$ | Saint-Venant-Anteil der ideellen Kippspannung | N/mm² | [[Saint-Venant-Anteil der Kippspannung]], Zwischenwert |
| $\sigma_{Dw}$ | Wölbanteil der ideellen Kippspannung | N/mm² | [[Wölbanteil der Kippspannung]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{cr,D} = \sqrt{\sigma_{Dv}^2 + \sigma_{Dw}^2} = \sqrt{\left(581.7\,\mathrm{N}/\mathrm{mm}^{2}\right)^2 + \left(1282\,\mathrm{N}/\mathrm{mm}^{2}\right)^2} = 1407.8\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Ideelles Kippmoment]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.kippen|_Herleitung.kippen]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Spannung im Druckgurt, bei der ein vollkommen gerader Träger
seitlich ausweicht und sich dabei verdreht. Zwei Steifigkeiten halten
ihn: die Torsionssteifigkeit des ganzen Querschnitts – der
[[Saint-Venant-Anteil der Kippspannung|Saint-Venant-Anteil]] – und die
Biegesteifigkeit des Druckgurts quer zur Ebene des Trägers – der
[[Wölbanteil der Kippspannung|Wölbanteil]]. (91) setzt beide zusammen wie
die Katheten zur Hypotenuse.

Das gilt für einen doppelsymmetrischen Querschnitt (B.3).
