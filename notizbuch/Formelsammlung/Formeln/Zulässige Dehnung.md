---
erzeugt: b14396695edc
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

## Gebraucht von

- [[Erfüllungsgrad]]

## Im Code

- `opencivil.nachweis.spannungsbegrenzung:Spannungsbegrenzung._protokoll_fliessen`

## Themen

- [[Stahlspannung aus Rissbreite]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
