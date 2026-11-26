---
erzeugt: b7491516c3f8
art: formel
tags: [formel]
normstelle: "SIA 263:2013, Anhang B.1, (90)"
---
> [!info] Normstelle
> SIA 263:2013, Anhang B.1, (90)

$$
M_{cr} = W_{el} \cdot \sigma_{cr,D}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $W_{el}$ | Elastisches Widerstandsmoment, ganzer Querschnitt | cm³ | Zwischenwert, [[Widerstandsmoment bis zur weitesten Faser]] |
| $\sigma_{cr,D}$ | Ideelle Kippspannung | N/mm² | [[Ideelle Kippspannung]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{cr} = W_{el} \cdot \sigma_{cr,D} = 3070.7\,\mathrm{cm}^{3} \cdot 1407.8\,\mathrm{N}/\mathrm{mm}^{2} = 4323.1\,\mathrm{kNm}
$$

## Gebraucht von

- [[Schlankheit beim Kippen]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.kippen|_Herleitung.kippen]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Moment, bei dem der Druckgurt die [[Ideelle Kippspannung]] erreicht:
die Spannung mal das elastische Widerstandsmoment um die starke Achse,
am ganzen Querschnitt. Anhang B rechnet dabei mit Gabellagern an den
Enden des Felds und einer Last, die in der Stabachse angreift (B.1). Aus
dem Moment folgt die [[Schlankheit beim Kippen]].
