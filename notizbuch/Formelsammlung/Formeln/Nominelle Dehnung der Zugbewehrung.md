---
erzeugt: 1fa5898654e2
art: formel
tags: [formel]
normstelle: ["SIA 262:2025, 4.3.3.2.3, (41)", "SIA 262:2025, 4.3.3.2.2, (39); 4.3.3.2.6"]
---
> [!info] Normstellen
> SIA 262:2025, 4.3.3.2.3, (41) · SIA 262:2025, 4.3.3.2.2, (39); 4.3.3.2.6

*In der Herleitung: «Nominelle Dehnung der Zugbewehrung»*

$$
\varepsilon_v = 1.5 \cdot \frac{f_{yd}}{E_s}
$$

*In der Herleitung: «Nominelle Dehnung der Zugbewehrung»*

$$
\varepsilon_v = \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |
| $m_{Ed}$ | – | kNm | Zwischenwert |
| $m_{Dd}$ | – | kNm | [[Dekompressionsmoment]] |
| $m_{Rd}(N_{Ed})$ | – | kNm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_v = 1.5 \cdot \frac{f_{yd}}{E_s} = 1.5 \cdot \frac{435\,\mathrm{N}/\mathrm{mm}^{2}}{200000\,\mathrm{N}/\mathrm{mm}^{2}} = 3.261\,\text{‰}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \varepsilon_v &= \frac{f_{yd} \cdot \left(\left|m_{Ed}\right| - m_{Dd}\right)}{E_s \cdot \left(\left|m_{Rd}(N_{Ed})\right| - m_{Dd}\right)} \\
  &= \frac{435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(\left|10\,\mathrm{kNm}\right| - 0\,\mathrm{kNm}\right)}{200000\,\mathrm{N}/\mathrm{mm}^{2} \cdot \left(\left|18.1\,\mathrm{kNm}\right| - 0\,\mathrm{kNm}\right)} \\
  &= 1.199\,\text{‰}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.querkraft_ohne_buegel#QuerkraftOhneBuegel._protokoll_fall|QuerkraftOhneBuegel._protokoll_fall]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

$\varepsilon_v$ ist die nominelle Dehnung der Zugbewehrung, mit der die Norm
den Widerstand ohne Bügel bemisst. Sie steht für die Öffnung des kritischen
Schubrisses -- eine Rechengrösse, keine Dehnung, die man am Bauteil misst.
Das Werkzeug rechnet sie so:

- bis zum [[Dekompressionsmoment]] null: der Querschnitt bleibt ungerissen;
- darüber wächst sie mit dem Moment und erreicht beim Biegewiderstand
  $m_{Rd}$ die [[Fliessdehnung]] $f_{yd}/E_s$. Diesen Wert lässt die Norm
  auch ohne weitere Rechnung als sichere Schätzung zu, solange die
  Bewehrung elastisch bleibt; die [[Kennzahlen]] nehmen ihn für den
  kleinsten Widerstand;
- übersteigt das Moment den Biegewiderstand, fliesst die Bewehrung, und es
  gilt fest das 1.5-fache der Fliessdehnung.

Beispiel ohne Normalkraft ($m_{Dd} = 0$), B500B mit $f_{yd} = 435$ und
$E_s = 200\,000\,\mathrm{N/mm^2}$, $m_{Rd} = 100\,\mathrm{kNm}$: bei
$m_{Ed} = 50\,\mathrm{kNm}$ ist $\varepsilon_v = 1.09$ ‰, bei
$100\,\mathrm{kNm}$ 2.17 ‰, darüber 3.26 ‰.

Die Norm verlangt den festen Wert schon, wo die Biegebewehrung plastisch
verformt werden könnte, etwa bei Schnittgrössen nach der
Plastizitätstheorie. Das Werkzeug weiss davon nichts; ob es danach fragen
soll, ist offen ([[TODO]]).
