---
erzeugt: 90478e95aa05
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.6.1.5.2"
---
> [!info] Normstelle
> SIA 267:2013, 9.6.1.5.2

*In der Herleitung: «Fläche des Tragstabs nach der Abrostung»*

$$
A_s = \frac{\pi \cdot \left(\varnothing - 2 \cdot \Delta t\right)^{2}}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varnothing$ | Durchmesser des Stabs | mm | Vorgabe |
| $\Delta t$ | Abrostung aussen | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
A_s = \frac{\pi \cdot \left(\varnothing - 2 \cdot \Delta t\right)^{2}}{4} = \frac{\pi \cdot \left(40\,\mathrm{mm} - 2 \cdot 2\,\mathrm{mm}\right)^{2}}{4} = 1018\,\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Materialwiderstand des Stahls]]

## Im Code

- [[opencivil.pfahl.innen#InnererWiderstand|InnererWiderstand._mikropfahl]]

## Themen

- [[Innerer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie beim Rohr: der Stab rostet aussen um Δt, sein Durchmesser wird um 2 Δt
kleiner (SIA 267:2013, 9.6.1.5.2). Ein Stab ⌀ 40 hat mit Δt = 2 mm statt
1257 noch 1018 mm² -- ein Fünftel weniger.
