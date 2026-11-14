---
erzeugt: d7292ac346e7
art: formel
tags: [formel]
normstelle: "Kap. 12.5, Bild 12.5"
---
> [!info] Normstelle
> Kap. 12.5, Bild 12.5

*In der Herleitung: «Tragfähigkeitsfaktor undrainiert, abgelesen nach L/D, höchstens 9»*

$$
N_c = N_c\left(\tfrac{L}{D}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $L$ | Länge des Pfahls | m | Vorgabe |
| $D$ | Durchmesser des Pfahls | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_c = N_c\left(\tfrac{L}{D}\right) = N_c\left(\tfrac{15\,\mathrm{m}}{1200\,\mathrm{mm}}\right) = 9
$$

## Gebraucht von

- [[Spitzendruck undrainiert]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._fuss_undrainiert]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

N_c nach Skempton für einen runden Fuss, über dem Verhältnis von Länge zu
Durchmesser: 6.2 an der Oberfläche, ab etwa L/D = 10 dann 9, nie mehr
(Kap. 12.5, Bild 12.5). Abgelesen und dazwischen linear.
