---
erzeugt: e3f97f4ec91d
art: formel
tags: [formel]
normstelle: "SIA 262:2025, Tabelle 17"
---
> [!info] Normstelle
> SIA 262:2025, Tabelle 17

$$
M_{s,adm,2,x} = \sigma_{s,adm,2,x} \cdot A_{s,2,x} \cdot z
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\sigma_{s,adm,2,x}$ | – | N/mm² | [[Zulässige Stahlspannung (Rissbreite w_nom)]] |
| $A_{s,2,x}$ | – | mm² | [[Bewehrung der Lage]] |
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

## Im Code

- [[opencivil.nachweis.mindestbewehrung#ZwaengungBiegung.protokoll_lage|ZwaengungBiegung.protokoll_lage]]

## Themen

- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Moment, das die Lage im gerissenen Zustand aufnimmt, wenn ihr Stahl bei
der zulässigen Spannung steht: Stahlkraft mal innerem Hebelarm. Der Nachweis
verlangt, dass es das Rissmoment übertrifft -- die Bewehrung muss das Moment
übernehmen, das der Beton beim Reissen abgibt.
