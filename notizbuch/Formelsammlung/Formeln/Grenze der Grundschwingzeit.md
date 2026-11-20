---
erzeugt: 65fe7e5df0b1
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.2.1, (39)"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.2.1, (39)

$$
T_{1,max} = 4 \cdot T_C
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $T_C$ | Eckperiode T\_C | s | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
T_{1,max} = 4 \cdot T_C = 4 \cdot 0.4\,\mathrm{s} = 1.6\,\mathrm{s}
$$

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf.zulaessigkeit|Lauf.zulaessigkeit]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Ersatzkraftverfahren nimmt an, dass die erste Schwingungsform das
Verhalten bestimmt. Bei langen Schwingzeiten tragen höhere Formen merklich
bei. Als Kriterien nennt 16.5.2.1 darum in beiden Hauptrichtungen
$T_1 \le 4 \cdot T_C$ (39) und einen regelmässigen Grundriss (16.5.1.3) und
Aufriss (16.5.1.4). Der [[Erfüllungsgrad]] ist $T_{1,max}/T_1$.

Fehlt eine Bedingung, gilt das Verfahren für das ganze Gebäude nicht --
auch nicht für die Richtung, die sie erfüllt. Dann ist das
Antwortspektrenverfahren anzuwenden (16.5.3.1). Die Zahlen bleiben stehen,
die Meldung steht rot darüber und nennt jeden Grund.
