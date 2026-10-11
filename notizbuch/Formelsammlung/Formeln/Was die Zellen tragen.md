---
erzeugt: 61357161e1ec
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
T_{Zellen} = T_{Ed} - \Delta T
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $T_{Ed}$ | – | kNm | Zwischenwert |
| $\Delta T$ | – | kNm | [[Versatz – Moment der Querkraftanteile um den Schwerpunkt]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
T_{Zellen} = T_{Ed} - \Delta T = 15\,\mathrm{kNm} - 0\,\mathrm{kNm} = 15\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.nachweis.schubwandnachweis#Schubwandnachweis|Schubwandnachweis._ein_fall]]

## Themen

- [[Querkraft und Torsion]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Torsion, die übrig bleibt: die einwirkende, vermindert um den
[[Versatz – Moment der Querkraftanteile um den Schwerpunkt|Versatz]]. Sie
verteilen die geschlossenen Zellen nach Bredt (siehe
[[Torsion in den Zellen (Bredt, mehrzellig)]]).
