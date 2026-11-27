---
erzeugt: a5ceaa844134
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Rissnormalkraft beim Moment»*

$$
N_{Riss}(M) = \left(f_{ct,eff} - \frac{M \cdot v_z}{I}\right) \cdot A
$$

*In der Herleitung: «Rissnormalkraft beim Moment»*

$$
N_{Riss}(M) = \left(f_{ct,eff} - \sigma_M\right) \cdot A
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{ct,eff}$ | – | N/mm² | [[Wirksame Zugfestigkeit]] |
| $M$ | – | kNm | Zwischenwert |
| $v_z$ | Abstand des gezogenen Rands vom Schwerpunkt | mm | Zwischenwert |
| $I$ | – | ·10⁶ mm⁴ | [[Flächenträgheitsmoment eines Rechtecks]] |
| $A$ | Fläche des Bruttoquerschnitts | mm² | [[Fläche eines Rechtecks]], Zwischenwert |
| $\sigma_M$ | aus dem Moment allein | N/mm² | [[Spannung aus dem Moment an der Ecke, die zuerst reisst]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{Riss}(M) &= \left(f_{ct,eff} - \frac{M \cdot v_z}{I}\right) \cdot A \\
  &= \left(2.52\,\mathrm{N}/\mathrm{mm}^{2} - \frac{30\,\mathrm{kNm} \cdot 150\,\mathrm{mm}}{2250\,\cdot 10^{6}\,\mathrm{mm}^{4}}\right) \cdot 300000\,\mathrm{mm}^{2} \\
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

- [[opencivil.spannungsanalyse.riss#Bruttoriss._herleitung_rissnormalkraft|Bruttoriss._herleitung_rissnormalkraft]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Dieselbe Rissbedingung wie beim Rissmoment, nach der Normalkraft aufgelöst:
beim Moment $M$ reisst der Querschnitt, wenn die Zugkraft $N_{Riss}$
erreicht. Unter Zug reisst die ganze Dicke, darum gilt der
[[Beiwert für die Dicke]] mit der ganzen Höhe und nicht mit einem Drittel wie
beim Rissmoment – nach Vorgabe, nicht nachgeschlagen. Bei der Platte zählt
das Vorzeichen des Moments nicht: sie ist oben wie unten dieselbe.

Beim gezeichneten Querschnitt gilt die kleinere Abmessung $\min(h; b)$ als
rissaktive Dicke, und es reisst die Ecke zuerst, an der das am wenigsten Zug
braucht: mit der [[Spannung aus dem Moment an der Ecke, die zuerst reisst]],
«einachsig» mit dem Abstand des Rands, den das Moment zieht.
