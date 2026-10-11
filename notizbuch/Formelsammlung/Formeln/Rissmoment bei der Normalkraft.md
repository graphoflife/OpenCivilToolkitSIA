---
erzeugt: d6407ee53e1c
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

- `opencivil.spannungsanalyse:_herleitung`

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
