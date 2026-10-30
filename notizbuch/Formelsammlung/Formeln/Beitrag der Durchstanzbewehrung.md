---
erzeugt: 40d35ef24f48
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.5.4, (68)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.5.4, (68)

$$
V_{Rd,s} = \sum A_{sw} \cdot k_e \cdot \sigma_{sd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\sum A_{sw}$ | Anrechenbare Durchstanzbewehrung | mm² | [[Anrechenbare Durchstanzbewehrung]] |
| $k_e$ | – | – | Zwischenwert, [[Beiwert der Momentenübertragung]] |
| $\sigma_{sd}$ | Spannung in der Durchstanzbewehrung | N/mm² | [[Spannung in der Durchstanzbewehrung]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{Rd,s} = \sum A_{sw} \cdot k_e \cdot \sigma_{sd} = 2513\,\mathrm{mm}^{2} \cdot 0.9 \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} = 983.5\,\mathrm{kN}
$$

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#_mit_leisten|_mit_leisten]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was die Durchstanzbewehrung zum Widerstand beiträgt: ihre anrechenbare
Fläche ([[Anrechenbare Durchstanzbewehrung]]) mal die Spannung, die sie bei
der Rotation der Platte erreicht ([[Spannung in der Durchstanzbewehrung]]),
mit $k_e$ gemindert wie der Umfang. Die Anker stehen senkrecht, $\sin\beta = 1$.
Er muss die [[Querkraft für die Durchstanzbewehrung]] tragen.
