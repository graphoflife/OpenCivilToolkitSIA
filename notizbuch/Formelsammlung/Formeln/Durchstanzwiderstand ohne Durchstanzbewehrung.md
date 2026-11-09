---
erzeugt: e404d8ba0036
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.3.6.3.1", "SIA 262:2025, 4.3.6.5.10, (58)", "SIA 262:2025, 4.3.6.6.2"]
---
> [!info] Normstellen
> SIA 262:2025, 4.3.6.3.1 · SIA 262:2025, 4.3.6.5.10, (58) · SIA 262:2025, 4.3.6.6.2

$$
V_{Rd,c} = k_r \cdot \tau_{cd} \cdot d_v \cdot u
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_r$ | – | – | [[Beiwert k_r]] |
| $\tau_{cd}$ | – | N/mm² | Zwischenwert |
| $d_v$ | – | mm | [[Wirksame Höhe ohne Abzug]] |
| $u$ | – | mm | [[Wirksamer Umfang des Nachweisschnitts]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_{Rd,c} &= k_r \cdot \tau_{cd} \cdot d_v \cdot u \\
  &= 0.721 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 234\,\mathrm{mm} \cdot 2102\,\mathrm{mm} \\
  &= 388.2\,\mathrm{kN}
\end{aligned}
$$

## Gebraucht von

- [[Querkraft für die Durchstanzbewehrung]]

## Im Code

- [[opencivil.durchstanzen.herleitung#widerstand|widerstand]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ohne Durchstanzbewehrung trägt der Beton allein: $\tau_{cd}$ mal
[[Beiwert k_r|k_r]], über die Fläche $d_v \cdot u$ des Nachweisschnitts. Der
Umfang ist der wirksame, um $k_e$ gemindert
([[Wirksamer Umfang des Nachweisschnitts]]). Gehalten wird der Widerstand
gegen die [[Bemessungswert der Querkraft im Nachweisschnitt|Querkraft im Schnitt]].

Ausserhalb der Durchstanzbewehrung trägt wieder der Beton allein
($V_{Rd,c,out}$, 4.3.6.5.10): mit $k_r$ von innen, aber mit der wirksamen
Höhe bis zu den Köpfen der Anker
([[Wirksame statische Höhe im äusseren Nachweisschnitt]]) und dem Umfang
des äusseren Schnitts. Reicht er nicht, braucht es längere Leisten oder mehr
davon. Um einen Stahlpilz ($V_{Rd,c,P}$, 4.3.6.6.2) gilt die wirksame Höhe
bis zu seiner Unterkante ([[Wirksame statische Höhe um den Stahlpilz]]); wo
der Beton um ihn nicht reicht, kommen Leisten um den Pilz dazu.
