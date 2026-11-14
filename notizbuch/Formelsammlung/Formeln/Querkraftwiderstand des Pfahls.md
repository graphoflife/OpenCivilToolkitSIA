---
erzeugt: 3c6bb92e06f9
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.5.2.4.1, (50)"
---
> [!info] Normstelle
> SIA 267:2013, 9.5.2.4.1, (50)

*In der Herleitung: «Querkraftwiderstand»*

$$
V_{Rd} = \eta_i \cdot \min\left[V_{Rd,s};\ V_{Rd,c}\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_i$ | Umrechnungsfaktor des inneren Widerstands | – | Vorgabe |
| $V_{Rd,s}$ | Widerstand der Wendel | kN | [[Widerstand der Wendel]] |
| $V_{Rd,c}$ | Widerstand der Druckdiagonalen | kN | [[Widerstand der Druckdiagonalen im Pfahl]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
V_{Rd} = \eta_i \cdot \min\left[V_{Rd,s};\ V_{Rd,c}\right] = 0.8 \cdot \min\left[335.9\,\mathrm{kN};\ 1374.8\,\mathrm{kN}\right] = 268.7\,\mathrm{kN}
$$

## Im Code

- [[opencivil.pfahl.innen_quer#InnererQuerwiderstand._neigung|InnererQuerwiderstand._neigung]]

## Themen

- [[Innerer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Kleinere von Wendel und Druckdiagonalen, bei der Neigung, die den
grössten Widerstand gibt: ganzgradig zwischen 30° und 45°, unter Zug ab 40°
(SIA 262:2025, 4.3.3.3.2, 4.3.3.3.3). Wie längs mindert η_i den Widerstand
(SIA 267:2013, 9.5.2.4.1, (50)): im Boden betoniert, sitzen auch Wendel und
Stäbe nicht sicher dort, wo sie sollen.

⌀ 900 mm: 0.8 · 336 = 269 kN unter Druck. Ein Zugpfahl trägt mit α = 40° nur
185 kN, denn cot 40° ist 0.69-mal cot 30°.

Nach Vorgabe, nicht nachgeschlagen: α_min = 30° auch unter grossem Druck, wo
die Norm 25° zuliesse; und die Querkraft zählt in jeder Tiefe, auch nahe dem
Kopf, wo nach 4.3.3.4.1 erst die im Abstand z · cot α massgebend wäre.
Beides liegt für die Querkraft auf der sicheren Seite.
