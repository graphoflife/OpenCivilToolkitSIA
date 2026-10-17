---
erzeugt: 6c2a163bf284
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Rissnormalkraft beim Moment»*

$$
N_{Riss}(M) = f_{ct,eff} \cdot b \cdot h - \frac{6 \cdot \left|M\right|}{h}
$$

*In der Herleitung: «Rissnormalkraft beim Moment»*

$$
N_{Riss}(M) = \left(f_{ct,eff} - \sigma_M\right) \cdot A
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{ct,eff}$ | – | N/mm² | [[Wirksame Zugfestigkeit]] |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $h$ | Plattendicke | mm | Vorgabe |
| $M$ | – | kNm | Zwischenwert |
| $\sigma_M$ | aus dem Moment allein | N/mm² | [[Spannung aus dem Moment an der Ecke, die zuerst reisst]] |
| $A$ | Fläche des Bruttoquerschnitts | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{Riss}(M) &= f_{ct,eff} \cdot b \cdot h - \frac{6 \cdot \left|M\right|}{h} \\
  &= 2.52\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1000\,\mathrm{mm} \cdot 300\,\mathrm{mm} - \frac{6 \cdot \left|30\,\mathrm{kNm}\right|}{300\,\mathrm{mm}} \\
  &= 156.5\,\mathrm{kN}
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{Riss}(M) &= \left(f_{ct,eff} - \sigma_M\right) \cdot A \\
  &= \left(2.23\,\mathrm{N}/\mathrm{mm}^{2} - 1.13\,\mathrm{N}/\mathrm{mm}^{2}\right) \cdot 330000\,\mathrm{mm}^{2} \\
  &= 363.3\,\mathrm{kN}
\end{aligned}
$$

## Im Code

- [[opencivil.spannungsanalyse.platte#Loeserpaar.herleitung_riss|Loeserpaar.herleitung_riss]]
- [[opencivil.spannungsanalyse.schnitt#Schnittpaar.herleitung_riss|Schnittpaar.herleitung_riss]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Dieselbe Rissbedingung wie beim Rissmoment, nach der Normalkraft aufgelöst:
beim Moment $M$ reisst der Querschnitt, wenn die Zugkraft $N_{Riss}$
erreicht. Unter Zug reisst die ganze Dicke, darum gilt der
[[Beiwert für die Dicke]] mit der ganzen Höhe und nicht mit einem Drittel wie
beim Rissmoment -- nach Vorgabe, nicht nachgeschlagen. Bei der Platte zählt
das Vorzeichen des Moments nicht: sie ist oben wie unten dieselbe.

Beim gezeichneten Querschnitt gilt die kleinere Abmessung $\min(h; b)$ als
rissaktive Dicke, und es reisst die Ecke zuerst, an der das am wenigsten Zug
braucht: mit der [[Spannung aus dem Moment an der Ecke, die zuerst reisst]],
«einachsig» mit dem Abstand des Rands, den das Moment zieht.
