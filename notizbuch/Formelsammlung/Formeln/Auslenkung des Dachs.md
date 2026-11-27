---
erzeugt: 0d08c30dd640
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.2.3, (40); nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.2.3, (40); nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Auslenkung des Dachs, die Gewichte waagrecht in x auf den Kragarm»*

$$
u_x = \sum_i \frac{W_i \cdot z_i^2 \cdot (3 \cdot H - z_i)}{6 \cdot EI_x}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $H$ | Höhe des Gebäudes | m | Zwischenwert |
| $EI_x$ | Biegesteifigkeit der Wände in x | MNm² | [[Biegesteifigkeit der Wände]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
u_x = \sum_i \frac{W_i \cdot z_i^2 \cdot (3 \cdot H - z_i)}{6 \cdot EI_x} = \sum_i \frac{W_i \cdot z_i^2 \cdot (3 \cdot 12\,\mathrm{m} - z_i)}{6 \cdot 87770\,\mathrm{MNm}^{2}} = 31.7\,\mathrm{mm}
$$

## Gebraucht von

- [[Grundschwingzeit]]

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._schwingzeit|Lauf._schwingzeit]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für die Schwingzeit nach (40) legt man die Gewichte waagrecht auf das
Tragwerk, jedes auf der Höhe seiner Decke (16.5.2.3), und schaut, wie weit
die Oberkante ausweicht. Die Auslenkung ist fiktiv: so belastet niemand das
Haus, sie dient nur der Schwingzeit.

Für einen Kragarm der Höhe $H$ unter einer Kraft $F$ auf der Höhe $z$
ist die Auslenkung der Spitze $F \cdot z^2 \cdot (3H - z) / (6\,EI)$; die
Summe über alle Geschosse gibt $u$. Gerechnet wird nur mit der Biegung und
mit Wänden, die am Fuss starr eingespannt sind. Gibt der Baugrund merklich
nach, gehört das dazu (16.5.1.8) – es macht $u$ grösser und
[[Grundschwingzeit|T₁]] länger und wird hier nicht gerechnet.
