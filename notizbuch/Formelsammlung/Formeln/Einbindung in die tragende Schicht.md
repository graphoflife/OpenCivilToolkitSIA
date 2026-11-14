---
erzeugt: d760dd350e47
art: formel
tags: [formel]
normstelle: "Kap. 12.4, Bild 12.3"
---
> [!info] Normstelle
> Kap. 12.4, Bild 12.3

*In der Herleitung: «Einbindung in die Schicht am Fuss»*

$$
h = z_F - z_{o,3}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $z_F$ | Tiefe des Fusses | m | Zwischenwert |
| $z_{o,3}$ | Oberkante der Schicht 3 | m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
h = z_F - z_{o,3} = 13.5\,\mathrm{m} - 8\,\mathrm{m} = 5.5\,\mathrm{m}
$$

## Gebraucht von

- [[Form- und Tiefenfaktor des Pfahlfusses]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._fuss_drainiert]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie tief der Fuss in die Schicht reicht, in der er steht: von ihrer Oberkante
bis zum Fuss. Zusammen mit dem Durchmesser bestimmt sie den Form- und
Tiefenfaktor X -- je tiefer im Verhältnis zum Durchmesser, desto mehr hilft
der Boden darüber mit (Kap. 12.4, Bild 12.3; Kap. 12.5, Bild 12.4). Ein
Pfahl ⌀ 800, der 4 m in den Silt reicht, hat h/D = 5.
