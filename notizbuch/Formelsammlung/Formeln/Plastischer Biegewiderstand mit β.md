---
erzeugt: 38d8b3a788af
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.1.2.2, Figur 1"
---
> [!info] Normstelle
> SIA 264:2014, 5.1.2.2, Figur 1

*In der Herleitung: «Plastischer Momentenwiderstand, mit β gemindert»*

$$
M_{y,Rd}^{+} = \beta \cdot M_{y,pl,Rd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\beta$ | Abminderungsbeiwert für S420 und S460 | – | [[Abminderungsbeiwert β nach Figur 1]] |
| $M_{y,pl,Rd}$ | Plastischer Momentenwiderstand, ohne β | kNm | [[Probe – Moment um y]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{y,Rd}^{+} = \beta \cdot M_{y,pl,Rd} = 0.907 \cdot 932.9\,\mathrm{kNm} = 845.8\,\mathrm{kNm}
$$

## Gebraucht von

- [[Erfüllungsgrad]]

## Im Code

- [[opencivil.nachweis.qa_verbund#VerbundBiegungQA|VerbundBiegungQA._plastisch]]
- [[opencivil.nachweis.qa_verbund_kennzahlen#KennzahlenVerbundQA|KennzahlenVerbundQA._biegung]]

## Themen

- [[Kennzahlen]]
- [[Verbundquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Moment des plastischen Zustands, aus den Kräften je Teil und Zone
([[Probe – Moment um y]], [[Probe – Moment um z]]), gemindert mit β aus
[[Abminderungsbeiwert β nach Figur 1]]. Nur mit S420 oder S460 und einer
tiefen Druckzone ist β kleiner als eins; sonst ist der Widerstand das
plastische Moment selbst.
