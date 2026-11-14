---
erzeugt: 9d3de1f54841
art: formel
tags: [formel]
normstelle: "Kap. 12.8, Bild 12.9"
---
> [!info] Normstelle
> Kap. 12.8, Bild 12.9

*In der Herleitung: «Längsfeder auf Druck»*

$$
k_v = \frac{1\,\mathrm{MN}}{w_0}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $w_0$ | Setzung des Kopfs unter 1 MN Druck | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
k_v = \frac{1\,\mathrm{MN}}{w_0} = \frac{1\,\mathrm{MN}}{0.913\,\mathrm{mm}} = 1095\,\mathrm{MN}/\mathrm{m}
$$

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit|Pfahlsteifigkeit._federn]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie weit sich der Kopf unter einer Normalkraft setzt, als Feder für das
Modell des Tragwerks: die Kraft durch die Setzung. Weil alles linear ist,
gibt jede Last dieselbe Feder; das Werkzeug setzt 1 MN an.

Auf Druck tragen Mantel und Fuss, auf Zug nur der Mantel -- die Zugfeder
ist darum weicher. Gerechnet wird mit E_s,k: in der Gebrauchstauglichkeit
zählen die Kennwerte des Bodens ohne Faktor (SIA 267:2013, 5.3.2.8).
⌀ 900 mm, 12 m lang, aus C30/37 in E_s,k = 30 MN/m²: 468 MN/m auf Druck,
396 MN/m auf Zug -- dieselben Zahlen wie die geschlossene Lösung von Cassan.
