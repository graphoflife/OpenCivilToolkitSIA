---
erzeugt: fc64aefaa699
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.5.10, (58)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.5.10, (58)

$$
V_{Rd,c,out} = k_r \cdot \tau_{cd} \cdot d_{v,out} \cdot u_{out}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_r$ | – | – | [[Beiwert k_r]] |
| $\tau_{cd}$ | – | N/mm² | Zwischenwert |
| $d_{v,out}$ | – | mm | [[Wirksame statische Höhe im äusseren Nachweisschnitt]] |
| $u_{out}$ | – | mm | [[Wirksamer Umfang des äusseren Nachweisschnitts]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_{Rd,c,out} &= k_r \cdot \tau_{cd} \cdot d_{v,out} \cdot u_{out} \\
  &= 0.721 \cdot 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 204\,\mathrm{mm} \cdot 5957\,\mathrm{mm} \\
  &= 959.3\,\mathrm{kN}
\end{aligned}
$$

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#_mit_leisten|_mit_leisten]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ausserhalb der Durchstanzbewehrung trägt wieder der Beton allein. Gerechnet
wird wie ohne Bewehrung ([[Durchstanzwiderstand ohne Durchstanzbewehrung]]),
mit $k_r$ von innen, aber mit der wirksamen Höhe bis zu den Köpfen der Anker
([[Wirksame statische Höhe im äusseren Nachweisschnitt]]) und dem Umfang des
äusseren Schnitts ([[Wirksamer Umfang des äusseren Nachweisschnitts]])
(4.3.6.5.10). Reicht er nicht, braucht es längere Leisten oder mehr davon.
