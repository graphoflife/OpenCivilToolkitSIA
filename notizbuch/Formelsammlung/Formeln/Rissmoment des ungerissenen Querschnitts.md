---
erzeugt: e044e84d6164
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.3.1.2", "SIA 262:2025, 4.4.2.3.4, Tabelle 17"]
---
> [!info] Normstellen
> SIA 262:2025, 4.3.1.2 · SIA 262:2025, 4.4.2.3.4, Tabelle 17

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

- [[opencivil.nachweis.rissgroessen#protokoll_rissmoment|protokoll_rissmoment]]
- [[opencivil.nachweis.rissgroessen#protokoll_rissmoment_rechteck|protokoll_rissmoment_rechteck]]

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
und risse etwas später; das bleibt hier unberücksichtigt. Beim spröden
Versagen liegt das auf der sicheren Seite, bei der Zwängung auf der
unsicheren; wie die Spannung-Dehnung-Analyse den Riss finden soll, ist
offen (siehe [[TODO]]).
