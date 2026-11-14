---
erzeugt: 133b1f1290e8
art: formel
tags: [formel]
normstelle: "Kap. 12.5; SIA 267:2013, 9.4.4.1.1"
---
> [!info] Normstelle
> Kap. 12.5; SIA 267:2013, 9.4.4.1.1

$$
R_{s,k} = U \cdot \sum h \, q_{s,k}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $U$ | Umfang des Pfahls | m | [[Umfang des Pfahls]] |
| $\sum h \, q_{s,k}$ | Mantelreibung über die Länge | kN/m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
R_{s,k} = U \cdot \sum h \, q_{s,k} = 2.827\,\mathrm{m} \cdot 383.6\,\mathrm{kN}/\mathrm{m} = 1085\,\mathrm{kN}
$$

## Gebraucht von

- [[Äusserer Widerstand auf Druck]]
- [[Äusserer Widerstand auf Zug]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand._mantel|AeussererWiderstand._mantel]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Mantelreibung über den ganzen Mantel: je Stück seine Länge h mal q_s,k,
die Summe mal dem Umfang. R_s,k ist der eine Teil des äusseren Widerstands
(SIA 267:2013, 9.4.4.1.1).

Eine Schicht, die nicht trägt -- eine weiche Auffüllung, Torf --, bekommt
q_s,k = 0. Bei einem stehenden Pfahl zählt das Buch nur den Mantel in der
tragenden Schicht (Kap. 12.4, Bild 12.3); den Schichten darüber gibt man dann
ebenfalls null.
