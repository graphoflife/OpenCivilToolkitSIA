---
erzeugt: 6c173b75310d
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
M_{Riss}(N) = M_{Riss} - N \cdot \frac{h}{6}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{Riss}$ | – | kNm | Zwischenwert |
| $N$ | – | kN | Zwischenwert |
| $h$ | Plattendicke | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{Riss}(N) = M_{Riss} - N \cdot \frac{h}{6} = 41.4\,\mathrm{kNm} - \left(-300\,\mathrm{kN}\right) \cdot \frac{300\,\mathrm{mm}}{6} = 56.4\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.spannungsanalyse#_herleitung|_herleitung]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Am Bruttoquerschnitt reisst der gezogene Rand, wenn $N/A + M/W$ die wirksame
Zugfestigkeit erreicht. Mit $A = b h$ und $W = b h^2/6$ verschiebt eine
Normalkraft das Rissmoment um $N \cdot h/6$: Druck hebt es, Zug senkt es.
Beim Rissmoment springt die Krümmung bei demselben Moment vom ungerissenen auf
den gerissenen Wert.

Gerechnet wird wie beim [[Rissmoment des ungerissenen Querschnitts]] am
Bruttoquerschnitt ohne Stahl -- nach Vorgabe, nicht nachgeschlagen.
