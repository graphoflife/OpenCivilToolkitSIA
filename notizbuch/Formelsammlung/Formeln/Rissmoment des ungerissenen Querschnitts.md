---
erzeugt: 783a5c19a06c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Rissmoment des ungerissenen Querschnitts»*

$$
M_{Riss} = f_{ct,eff} \cdot \frac{h^{2} \cdot b}{6}
$$

*In der Herleitung: «Rissmoment des ungerissenen Querschnitts»*

$$
M_{Riss} = f_{ct,eff} \cdot W
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{ct,eff}$ | – | N/mm² | [[Wirksame Zugfestigkeit]] |
| $h$ | Plattendicke | mm | Vorgabe |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $W$ | – | ·10⁶ mm³ | [[Widerstandsmoment zum gezogensten Betonpunkt]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{Riss} = f_{ct,eff} \cdot \frac{h^{2} \cdot b}{6} = 2.76\,\mathrm{N}/\mathrm{mm}^{2} \cdot \frac{\left(300\,\mathrm{mm}\right)^{2} \cdot 1000\,\mathrm{mm}}{6} = 41.4\,\mathrm{kNm}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{Riss} = f_{ct,eff} \cdot W = 2.64\,\mathrm{N}/\mathrm{mm}^{2} \cdot 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3} = 116.7\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.nachweis.richtungsnachweise#SproedesVersagenQA.pruefe|SproedesVersagenQA.pruefe]]
- [[opencivil.nachweis.sproedes_versagen#protokoll_rissmoment|protokoll_rissmoment]]

## Themen

- [[Sprödes Versagen]]
- [[Zwängung auf Biegung]]
- [[Sprödes Versagen je Richtung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Moment, bei dem der Beton am gezogenen Rand reisst: die wirksame
Zugfestigkeit mal dem Widerstandsmoment des ungerissenen Bruttoquerschnitts,
ohne Bewehrung. Bei der Platte ist das $b h^2/6$; beim gezeichneten
Querschnitt das [[Widerstandsmoment zum gezogensten Betonpunkt]].

Gerechnet wird mit dem Bruttoquerschnitt ohne Bewehrung -- es geht um den
Zustand vor dem Riss. Mit der Bewehrung wäre der Querschnitt etwas steifer
und risse etwas später; das bleibt hier unberücksichtigt, nach Vorgabe und
nicht nachgeschlagen.
