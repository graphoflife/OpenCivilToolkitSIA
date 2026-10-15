---
erzeugt: e4ba8608b8f5
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Rissaktive Dicke: die kleinere Abmessung, höchstens 500 mm»*

$$
t = \min\left[500\,\mathrm{mm};\ b;\ h\right]
$$

*In der Herleitung: «Rissaktive Dicke: die kleinere Abmessung»*

$$
t = \min\left[b;\ h\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b$ | Ausdehnung des Betons in y | mm | Zwischenwert |
| $h$ | Ausdehnung des Betons in z | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
t = \min\left[500\,\mathrm{mm};\ b;\ h\right] = \min\left[500\,\mathrm{mm};\ 800\,\mathrm{mm};\ 600\,\mathrm{mm}\right] = 500\,\mathrm{mm}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
t = \min\left[b;\ h\right] = \min\left[400\,\mathrm{mm};\ 400\,\mathrm{mm}\right] = 400\,\mathrm{mm}
$$

## Im Code

- [[opencivil.nachweis.qa_gebrauch#RissnormalkraftQA._risskraft|RissnormalkraftQA._risskraft]]

## Themen

- [[Zwängung auf Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Bei einer Zwängung auf Normalkraft reisst der ganze Querschnitt. Wie bei der
Platte mindert $k_t = 1/(1 + 0.5 \cdot t)$ die Zugfestigkeit eines dicken
Bauteils, das nicht über die ganze Dicke zugleich reisst. Die Platte hat
eine Dicke, ein gezeichneter Querschnitt zwei Abmessungen: angesetzt wird
die kleinere Ausdehnung des Betons, gemessen am umschreibenden Rechteck. Bei
einem Rechteck ist das seine Dicke, wie bei der Platte. Wahlweise wird sie
wie dort auf 500 mm begrenzt. Dass es die kleinere Abmessung ist, überträgt
die Regel der Platte – nach Vorgabe, nicht nachgeschlagen.
