---
erzeugt: 7087d659134e
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.4.2.3.7", "SIA 262:2025, 4.4.1.3"]
---
> [!info] Normstellen
> SIA 262:2025, 4.4.2.3.7 · SIA 262:2025, 4.4.1.3

*In der Herleitung: «Rissaktive Dicke: die kleinere Abmessung, höchstens 500 mm»*

$$
t = \min\left[500\,\mathrm{mm};\ b;\ h\right]
$$

*In der Herleitung: «Rissaktive Dicke: die kleinere Abmessung»*

$$
t = \min\left[b;\ h\right]
$$

*In der Herleitung: «Rissaktive Dicke unter Zug: die kleinere Abmessung»*

$$
t = \min\left[h;\ b\right]
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

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
t = \min\left[h;\ b\right] = \min\left[600\,\mathrm{mm};\ 800\,\mathrm{mm}\right] = 600\,\mathrm{mm}
$$

## Im Code

- [[opencivil.nachweis.qa_gebrauch#RissnormalkraftQA._risskraft|RissnormalkraftQA._risskraft]]
- [[opencivil.spannungsanalyse.schnitt#Schnittpaar.herleitung_riss|Schnittpaar.herleitung_riss]]

## Themen

- [[Zwängung auf Normalkraft]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Bei einer Zwängung auf Normalkraft reisst der ganze Querschnitt. Wie bei der
Platte mindert $k_t = 1/(1 + 0.5 \cdot t)$ die Zugfestigkeit eines dicken
Bauteils, das nicht über die ganze Dicke zugleich reisst. Die Platte hat
eine Dicke, ein gezeichneter Querschnitt zwei Abmessungen: angesetzt wird
die kleinere Ausdehnung des Betons, gemessen am umschreibenden Rechteck. Bei
einem Rechteck ist das seine Dicke, wie bei der Platte. Die Norm nimmt die
kleinste Abmessung des gezogenen Teils (SIA 262, 4.4.1.3); bei Steg,
Flansch oder Hohlkasten ist das weniger als die Seite des Rechtecks -- das
ist offen, siehe [[TODO]].

Mit dem Schalter «500 mm» gilt bei massigen Bauteilen $k_t$ für 500 mm, und
in die [[Risskraft des ganzen Querschnitts]] geht nur der Beton bis 250 mm
vom Rand ein (SIA 262, 4.4.2.3.7). Unter zentrischem Zug sind alle Ränder
gezogen, auch die einer Aussparung; wo zwei Betone aneinanderstossen, ist
kein Rand.
