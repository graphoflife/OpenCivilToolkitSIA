---
erzeugt: d855c3ccaeb0
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.6.1.5.2"
---
> [!info] Normstelle
> SIA 267:2013, 9.6.1.5.2

*In der Herleitung: «Fläche des Tragrohrs nach der Abrostung»*

$$
A_s = \frac{\pi \cdot \left(\left(d_a - 2 \cdot \Delta t\right)^{2} - \left(d_a - 2 \cdot t\right)^{2}\right)}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d_a$ | Aussendurchmesser des Rohrs | mm | Vorgabe |
| $\Delta t$ | Abrostung aussen | mm | Vorgabe |
| $t$ | Wanddicke des Rohrs | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  A_s &= \frac{\pi \cdot \left(\left(d_a - 2 \cdot \Delta t\right)^{2} - \left(d_a - 2 \cdot t\right)^{2}\right)}{4} \\
  &= \frac{\pi \cdot \left(\left(88.9\,\mathrm{mm} - 2 \cdot 1\,\mathrm{mm}\right)^{2} - \left(88.9\,\mathrm{mm} - 2 \cdot 8\,\mathrm{mm}\right)^{2}\right)}{4} \\
  &= 1757\,\mathrm{mm}^{2}
\end{aligned}
$$

## Gebraucht von

- [[Materialwiderstand des Stahls]]

## Im Code

- [[opencivil.pfahl.innen#InnererWiderstand|InnererWiderstand._mikropfahl]]

## Themen

- [[Innerer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was vom Rohr bleibt, wenn es aussen um Δt rostet: der Aussendurchmesser wird
um 2 Δt kleiner, der innere bleibt. Statt eines weiteren Schutzes darf ein
Druckpfahl in schwach aggressivem Boden einen solchen Zuschlag für die
Korrosion haben (SIA 267:2013, 9.6.1.5.2). Ein Rohr 88.9 × 8 mm hat mit
Δt = 1 mm statt 2033 noch 1757 mm².
