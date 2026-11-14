---
erzeugt: 717b3517e086
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.4.2.3.7"
---
> [!info] Normstelle
> SIA 262:2025, 4.4.2.3.7

$$
h_{eff} = \min\left[500\,\mathrm{mm};\ h\right]
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h$ | Plattendicke | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
h_{eff} = \min\left[500\,\mathrm{mm};\ h\right] = \min\left[500\,\mathrm{mm};\ 300\,\mathrm{mm}\right] = 300\,\mathrm{mm}
$$

## Gebraucht von

- [[Beiwert für die Dicke]]
- [[Risskraft der gezogenen Querschnittshälfte]]

## Im Code

- [[opencivil.nachweis.mindestbewehrung#Rissnormalkraft|Rissnormalkraft._protokoll_ansatz]]

## Themen

- [[Zwängung auf Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Dicke, über die eine Zwängung den Querschnitt reissen lässt. Ist die
Begrenzung eingeschaltet, zählt höchstens 500 mm: bei massigen Bauteilen
wirkt je gezogenem Rand nur eine Zone von 250 mm mit, und $k_t$ gilt für
500 mm (SIA 262, 4.4.2.3.7). Unter Zug sind beide Ränder der Platte
gezogen, zusammen 500 mm. Ohne Begrenzung zählt die ganze Dicke.
