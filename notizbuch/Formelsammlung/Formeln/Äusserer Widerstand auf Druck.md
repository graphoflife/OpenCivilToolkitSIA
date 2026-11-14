---
erzeugt: 915663713556
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.4.4.1.1, (41); 9.4.4.1.6"
---
> [!info] Normstelle
> SIA 267:2013, 9.4.4.1.1, (41); 9.4.4.1.6

*In der Herleitung: «Äusserer Widerstand auf Druck, charakteristisch»*

$$
R_{a,k} = R_{b,k} + R_{s,k}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $R_{b,k}$ | Spitzenwiderstand | kN | [[Spitzenwiderstand]] |
| $R_{s,k}$ | Mantelwiderstand | kN | [[Mantelwiderstand]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
R_{a,k} = R_{b,k} + R_{s,k} = 2999\,\mathrm{kN} + 1085\,\mathrm{kN} = 4084\,\mathrm{kN}
$$

## Gebraucht von

- [[Bemessungswert des äusseren Widerstands]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._aus_schichten]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Fuss und Mantel zusammen (SIA 267:2013, 9.4.4.1.1, (41)); die Norm will beide
Teile möglichst getrennt bestimmt sehen. Beide sind Bruchwerte: der Mantel
trägt schon bei kleinen Verschiebungen voll, der Fuss erst, wenn sich der
Pfahl deutlich setzt -- darum schert er hier in der Regel örtlich ab.

Kommt R_a,k aus Versuchen, ist er der kleinste gemessene Wert
(SIA 267:2013, 9.4.4.1.6) und wird eingegeben.
