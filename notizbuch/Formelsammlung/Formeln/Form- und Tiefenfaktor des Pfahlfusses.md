---
erzeugt: f6a9e9c8a3e4
art: formel
tags: [formel]
normstelle: "Kap. 12.5, Bild 12.4"
---
> [!info] Normstelle
> Kap. 12.5, Bild 12.4

*In der Herleitung: «Form- und Tiefenfaktor, abgelesen nach φ'\_k und h/D»*

$$
X = X\left(\varphi'_{k,3}, \tfrac{h}{D}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varphi'_{k,3}$ | Reibungswinkel der Schicht 3, charakteristisch | ° | Vorgabe |
| $h$ | Einbindung in die Schicht am Fuss | m | [[Einbindung in die tragende Schicht]] |
| $D$ | Durchmesser des Pfahls | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
X = X\left(\varphi'_{k,3}, \tfrac{h}{D}\right) = X\left(36{}^{\circ}, \tfrac{5.5\,\mathrm{m}}{900\,\mathrm{mm}}\right) = 2.63
$$

## Gebraucht von

- [[Spitzendruck drainiert]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._fuss_drainiert]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Faktor, der aus dem Spitzendruck eines langen Streifens an der Oberfläche
den eines runden Fusses in der Tiefe macht -- im Buch als Kurven über h/D,
eine je Reibungswinkel (Kap. 12.5, Bild 12.4). Hier abgelesen auf etwa ±0.02
und dazwischen linear. Ausserhalb von 15° bis 40° und von h/D = 2.5 bis 30
gilt der Wert am Rand, mit einer Warnung -- nach Vorgabe, nicht
nachgeschlagen. Bei 30° und h/D = 10 ist X = 2.24.

Abgelesen wird mit φ'_k, auch wenn der Fuss örtlich abschert -- nach Vorgabe,
nicht nachgeschlagen.
