---
erzeugt: eb44d8daeb4e
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Dehnung auf halber Höhe»*

$$
\varepsilon_v = 1.5 \cdot \frac{f_{yd}}{E_s}
$$

*In der Herleitung: «Dehnung auf halber Höhe»*

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

Die Längsdehnung in der Mitte der Platte ist das Mass für die Öffnung des
kritischen Schubrisses. Sie wächst mit dem Moment: über dem
[[Dekompressionsmoment]] dehnt sich die Bewehrung linear, bis sie beim
Biegewiderstand $m_{Rd}$ die Fliessdehnung $f_{yd}/E_s$ erreicht.

Übersteigt das Moment den Widerstand -- etwa bei einer Kurve, die über
$m_{Rd}$ hinaus gezeichnet wird --, gilt ein fester Wert: das 1.5-fache der
Fliessdehnung, unabhängig vom Moment.
