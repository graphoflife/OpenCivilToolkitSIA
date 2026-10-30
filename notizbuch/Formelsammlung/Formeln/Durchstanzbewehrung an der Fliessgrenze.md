---
erzeugt: a2f0b0d857e6
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.5.3, (67)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.5.3, (67)

$$
V_{Rd,v} = \sum A_{sw} \cdot k_e \cdot f_{yd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\sum A_{sw}$ | Anrechenbare Durchstanzbewehrung | mm² | [[Anrechenbare Durchstanzbewehrung]] |
| $k_e$ | – | – | Zwischenwert, [[Beiwert der Momentenübertragung]] |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{Rd,v} = \sum A_{sw} \cdot k_e \cdot f_{yd} = 2513\,\mathrm{mm}^{2} \cdot 0.9 \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} = 983.5\,\mathrm{kN}
$$

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#_mit_leisten|_mit_leisten]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die anrechenbare Durchstanzbewehrung, als flösse sie: $f_{yd}$ statt der
Spannung aus der Rotation. Sie muss mindestens die halbe Querkraft tragen
([[Halbe Querkraft für das Verformungsvermögen]]). Das sichert ein
genügendes Verformungsvermögen (4.3.6.5.3).
