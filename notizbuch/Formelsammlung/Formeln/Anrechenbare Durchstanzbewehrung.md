---
erzeugt: 39345fd87677
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.5.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.5.4

$$
\sum A_{sw} = n_L \cdot n_A \cdot \frac{\pi \cdot \varnothing_{sw}^{2}}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $n_L$ | – | – | Zwischenwert |
| $n_A$ | – | – | Zwischenwert |
| $\varnothing_{sw}$ | – | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sum A_{sw} = n_L \cdot n_A \cdot \frac{\pi \cdot \varnothing_{sw}^{2}}{4} = 16 \cdot 2 \cdot \frac{\pi \cdot \left(10\,\mathrm{mm}\right)^{2}}{4} = 2513\,\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Beitrag der Durchstanzbewehrung]]
- [[Durchstanzbewehrung an der Fliessgrenze]]

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#_mit_leisten|_mit_leisten]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Angerechnet wird nur die Durchstanzbewehrung, die zwischen 0.35·d_v und d_v
vom Rand der gestützten Fläche liegt (4.3.6.5.4): dort kreuzt sie den
kritischen Schubriss. Bei ancoPLUS sind das die ersten beiden Anker jeder
Leiste. Die Summe ist die Zahl der Leisten mal die Anker im Bereich mal die
Fläche eines Ankers.
