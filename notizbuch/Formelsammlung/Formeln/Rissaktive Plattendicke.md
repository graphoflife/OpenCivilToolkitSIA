---
erzeugt: c201d237240e
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

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
Begrenzung eingeschaltet, zählt höchstens 500 mm: dicke Bauteile reissen
nicht über ihre ganze Dicke gleichzeitig, die Zwängung wirkt in einer
Randzone. Ohne Begrenzung zählt die ganze Dicke.
