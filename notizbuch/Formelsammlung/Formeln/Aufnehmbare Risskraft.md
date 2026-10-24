---
erzeugt: 8b09920f2b0d
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Aufnehmbare Risskraft»*

$$
N_{s,adm,2,x} = A_{s,2,x} \cdot \sigma_{s,adm,2,x}
$$

*In der Herleitung: «Aufnehmbare Risskraft»*

$$
N_{s,adm} = A_{s,1} \cdot \sigma_{s,adm,1} + A_{s,2} \cdot \sigma_{s,adm,2} + A_{s,3} \cdot \sigma_{s,adm,3} + A_{s,4} \cdot \sigma_{s,adm,4} + A_{s,5} \cdot \sigma_{s,adm,5}
$$

*In der Herleitung: «Aufnehmbare Risskraft»*

$$
N_{s,adm} = A_s \cdot \sigma_{s,adm}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{s,2,x}$ | – | mm² | [[Bewehrung der Lage]] |
| $\sigma_{s,adm,2,x}$ | – | N/mm² | [[Zulässige Stahlspannung (Rissbreite w_nom)]] |
| $A_{s,1}$ | – | mm² | Zwischenwert |
| $\sigma_{s,adm,1}$ | Widerstand | N/mm² | [[Zulässige Stahlspannung (Rissbreite w_nom)]] |
| $A_{s,2}$ | – | mm² | Zwischenwert |
| $\sigma_{s,adm,2}$ | Widerstand | N/mm² | [[Zulässige Stahlspannung (Rissbreite w_nom)]] |
| $A_{s,3}$ | – | mm² | Zwischenwert |
| $\sigma_{s,adm,3}$ | Widerstand | N/mm² | [[Zulässige Stahlspannung (Rissbreite w_nom)]] |
| $A_{s,4}$ | – | mm² | Zwischenwert |
| $\sigma_{s,adm,4}$ | Widerstand | N/mm² | [[Zulässige Stahlspannung (Rissbreite w_nom)]] |
| $A_{s,5}$ | – | mm² | Zwischenwert |
| $\sigma_{s,adm,5}$ | Widerstand | N/mm² | [[Zulässige Stahlspannung (Rissbreite w_nom)]] |
| $A_s$ | – | mm² | Zwischenwert |
| $\sigma_{s,adm}$ | Widerstand | N/mm² | [[Zulässige Stahlspannung (normale Anforderung)]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{s,adm,2,x} &= A_{s,2,x} \cdot \sigma_{s,adm,2,x} \\
  &= 2450\,\mathrm{mm}^{2} \cdot 381\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 933.1\,\mathrm{kN} \quad \ge \quad N_{Riss} = 378.3\,\mathrm{kN} \quad \Rightarrow \quad \text{erfüllt}
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{s,adm} &= A_{s,1} \cdot \sigma_{s,adm,1} + A_{s,2} \cdot \sigma_{s,adm,2} + A_{s,3} \cdot \sigma_{s,adm,3} + A_{s,4} \cdot \sigma_{s,adm,4} + A_{s,5} \cdot \sigma_{s,adm,5} \\
  &= 314\,\mathrm{mm}^{2} \cdot 361\,\mathrm{N}/\mathrm{mm}^{2} + 1206\,\mathrm{mm}^{2} \cdot 404\,\mathrm{N}/\mathrm{mm}^{2} + 452\,\mathrm{mm}^{2} \cdot 466\,\mathrm{N}/\mathrm{mm}^{2} + 400\,\mathrm{mm}^{2} \cdot 404\,\mathrm{N}/\mathrm{mm}^{2} + 118\,\mathrm{mm}^{2} \cdot 500\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 1032.4\,\mathrm{kN} \quad \ge \quad N_{Riss} = 765.6\,\mathrm{kN} \quad \Rightarrow \quad \text{erfüllt}
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{s,adm} &= A_s \cdot \sigma_{s,adm} \\
  &= 1885\,\mathrm{mm}^{2} \cdot 500\,\mathrm{N}/\mathrm{mm}^{2} \\
  &= 942.5\,\mathrm{kN} \quad \ge \quad N_{Riss} = 386.7\,\mathrm{kN} \quad \Rightarrow \quad \text{erfüllt}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.mindestbewehrung#Rissnormalkraft|Rissnormalkraft._protokoll_lage]]
- [[opencivil.nachweis.qa_gebrauch#RissnormalkraftQA.pruefe|RissnormalkraftQA.pruefe]]

## Themen

- [[Zwängung auf Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was eine Lage an Kraft aufnimmt, ohne die zulässige Spannung zu
überschreiten: ihre Fläche mal $\sigma_{s,adm}$. Der Nachweis verlangt, dass
sie die [[Risskraft der gezogenen Querschnittshälfte]] übertrifft.
