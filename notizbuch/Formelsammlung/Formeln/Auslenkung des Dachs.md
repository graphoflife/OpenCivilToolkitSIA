---
erzeugt: 6b2280ba4fa1
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.2.3, (40); nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.2.3, (40); nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Auslenkung des Dachs, die Gewichte waagrecht in x auf den Kern»*

$$
u_x = \sum_i \Delta u_i
$$

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
u_x = \sum_i \Delta u_i = 31.7\,\mathrm{mm}
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

Jedes Geschoss biegt sich mit seinem Kern; was es zur Auslenkung oben
beiträgt, sagt die [[Auslenkung aus einem Geschoss]], und die Summe gibt
$u$. Gerechnet wird nur mit der Biegung und mit einem Kern, der am Fuss
starr eingespannt ist. Gibt der Baugrund merklich
nach, gehört das dazu (16.5.1.8) – es macht $u$ grösser und
[[Grundschwingzeit|T₁]] länger und wird hier nicht gerechnet.
