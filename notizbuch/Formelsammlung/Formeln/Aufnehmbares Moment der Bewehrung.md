---
erzeugt: 26f9902b4bb5
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
M_{s,adm,2,x} = \sigma_{s,adm,2,x} \cdot A_{s,2,x} \cdot z
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\sigma_{s,adm,2,x}$ | – | N/mm² | [[Zulässige Stahlspannung (Rissbreite w_nom)]] |
| $A_{s,2,x}$ | – | mm² | [[Bewehrung der Lage]], Zwischenwert |
| $z$ | – | mm | [[Innerer Hebelarm]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  M_{s,adm,2,x} &= \sigma_{s,adm,2,x} \cdot A_{s,2,x} \cdot z \\
  &= 381\,\mathrm{N}/\mathrm{mm}^{2} \cdot 2450\,\mathrm{mm}^{2} \cdot 211.4\,\mathrm{mm} \\
  &= 197.3\,\mathrm{kNm} \quad \ge \quad M_{Riss} = 41.4\,\mathrm{kNm} \quad \Rightarrow \quad \text{erfüllt}
\end{aligned}
$$

## Gebraucht von

- [[Erfüllungsgrad]]

## Im Code

- `opencivil.nachweis.mindestbewehrung:ZwaengungBiegung._protokoll_lage`

## Themen

- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
