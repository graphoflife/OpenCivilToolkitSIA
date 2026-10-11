---
erzeugt: 2bcfe9152f6f
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\varepsilon_{s,adm} = \frac{\sigma_{s,adm}}{E_s}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\sigma_{s,adm}$ | Widerstand | N/mm² | [[Zulässige Stahlspannung (normale Anforderung)]] |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \varepsilon_{s,adm} &= \frac{\sigma_{s,adm}}{E_s} \\
  &= \frac{500\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} \\
  &= 2.5\,\text{‰} \quad < \quad \varepsilon_{s,x} = 4.67\,\text{‰} \quad \Rightarrow \quad \text{NICHT erfüllt}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.spannungsbegrenzung#Spannungsbegrenzung._protokoll_fliessen|Spannungsbegrenzung._protokoll_fliessen]]

## Themen

- [[Stahlspannung aus Rissbreite]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Fliesst die Bewehrung unter der Einwirkung, bleibt ihre Spannung am Plateau
stehen, und ein Vergleich der Spannungen sagte nichts mehr. Verglichen wird
dann die Dehnung: die wirkende gegen die Dehnung, die zur zulässigen
Spannung gehört. Solange der Stahl elastisch bleibt, ist das genau der
Spannungsvergleich; fliesst er, fällt der Nachweis durch -- um so
deutlicher, je weiter er gedehnt ist.
