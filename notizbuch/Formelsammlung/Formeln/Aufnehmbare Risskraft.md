---
erzeugt: 5c4587a9f424
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
N_{s,adm,2,x} = A_{s,2,x} \cdot \sigma_{s,adm,2,x}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,2,x}$ | – | mm² | [[Bewehrung der Lage]] |
| $\sigma_{s,adm,2,x}$ | – | N/mm² | [[Zulässige Stahlspannung (Rissbreite w_nom)]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{s,adm,2,x} &= A_{s,2,x} \cdot \sigma_{s,adm,2,x} \\
  &= 2450\,\mathrm{mm}^{2} \cdot 381\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 933.1\,\mathrm{kN} \quad \ge \quad N_{Riss} = 378.3\,\mathrm{kN} \quad \Rightarrow \quad \text{erfüllt}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.mindestbewehrung#Rissnormalkraft|Rissnormalkraft._protokoll_lage]]

## Themen

- [[Zwängung auf Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was eine Lage an Kraft aufnimmt, ohne die zulässige Spannung zu
überschreiten: ihre Fläche mal $\sigma_{s,adm}$. Der Nachweis verlangt, dass
sie die [[Risskraft der gezogenen Querschnittshälfte]] übertrifft.
