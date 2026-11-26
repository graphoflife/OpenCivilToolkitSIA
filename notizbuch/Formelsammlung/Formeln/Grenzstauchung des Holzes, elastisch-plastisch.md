---
erzeugt: acf5bb147df3
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 3.1.2.2; die Grenze nach Vorgabe"
---
> [!info] Normstelle
> SIA 265:2012, 3.1.2.2; die Grenze nach Vorgabe

$$
\varepsilon_{cu} = 3 \cdot \varepsilon_{c,0,d}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varepsilon_{c,0,d}$ | Stauchung an der Druckgrenze in Faserrichtung | ‰ | [[Stauchung an der Druckgrenze in Faserrichtung]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_{cu} = 3 \cdot \varepsilon_{c,0,d} = 3 \cdot 1.32\,\text{‰} = 3.95\,\text{‰}
$$

## Im Code

- [[opencivil.material.holz]]

## Themen

- [[Holz]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Kann ein Bauteil plastisch stauchen, lässt SIA 265:2012, 3.1.2.2 auf Druck
ein elastisch-plastisches Gesetz zu, nennt aber keine Grenze. Das Werkzeug
hält die Spannung bei $f_{c,0,d}$ bis zur dreifachen
[[Stauchung an der Druckgrenze in Faserrichtung]] – nach Vorgabe, nicht
nachgeschlagen. Bei C24 sind das 3 · 1.09 = 3.27 ‰; darüber trägt die
Faser nichts mehr.
