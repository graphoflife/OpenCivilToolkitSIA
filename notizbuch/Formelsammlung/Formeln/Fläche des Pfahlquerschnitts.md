---
erzeugt: 38554e9eb340
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.5.2.4.7"
---
> [!info] Normstelle
> SIA 267:2013, 9.5.2.4.7

*In der Herleitung: «Fläche des Fusses»*

$$
A_b = \frac{\pi \cdot D^{2}}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $D$ | Durchmesser des Pfahls | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
A_b = \frac{\pi \cdot D^{2}}{4} = \frac{\pi \cdot \left(900\,\mathrm{mm}\right)^{2}}{4} = 0.636\,\mathrm{m}^{2}
$$

## Gebraucht von

- [[Materialwiderstand auf Druck]]
- [[Spitzenwiderstand]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._fuss]]
- [[opencivil.pfahl.innen#InnererWiderstand|InnererWiderstand._bohrpfahl]]

## Themen

- [[Äusserer Pfahlwiderstand]]
- [[Innerer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Kreisfläche des Pfahls. Am Fuss ist sie die Fläche, auf die der
Spitzendruck wirkt, im Querschnitt die Betonfläche samt den Stäben darin.
Beim Bohrpfahl zählt verrohrt der Aussendurchmesser der Verrohrung,
unverrohrt der des Bohrwerkzeugs (SIA 267:2013, 9.5.2.4.7). Beim Mikropfahl
ist es der Fuss des Verpresskörpers. Bei D = 900 mm sind es 0.636 m².
