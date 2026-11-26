---
erzeugt: 7e30e06fd72b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Torsionsbeiwert nach Saint-Venant: die grösste Schubspannung liegt in der Mitte der langen Seite»*

$$
k_2 = \frac{1 - \frac{192}{\pi^5} \cdot \frac{b}{h} \sum_{n = 1, 3, 5, \ldots} \frac{1}{n^5} \tanh\frac{n \pi \cdot h}{2 \cdot b}}{3 \left(1 - \frac{8}{\pi^2} \sum_{n = 1, 3, 5, \ldots} \frac{1}{n^2 \cosh\frac{n \pi \cdot h}{2 \cdot b}}\right)}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b$ | Kurze Seite des Rechtecks | mm | Zwischenwert |
| $h$ | Lange Seite des Rechtecks | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  k_2 &= \frac{1 - \frac{192}{\pi^5} \cdot \frac{b}{h} \sum_{n = 1, 3, 5, \ldots} \frac{1}{n^5} \tanh\frac{n \pi \cdot h}{2 \cdot b}}{3 \left(1 - \frac{8}{\pi^2} \sum_{n = 1, 3, 5, \ldots} \frac{1}{n^2 \cosh\frac{n \pi \cdot h}{2 \cdot b}}\right)} \\
  &= \frac{1 - \frac{192}{\pi^5} \cdot \frac{160\,\mathrm{mm}}{400\,\mathrm{mm}} \sum_{n = 1, 3, 5, \ldots} \frac{1}{n^5} \tanh\frac{n \pi \cdot 400\,\mathrm{mm}}{2 \cdot 160\,\mathrm{mm}}}{3 \left(1 - \frac{8}{\pi^2} \sum_{n = 1, 3, 5, \ldots} \frac{1}{n^2 \cosh\frac{n \pi \cdot 400\,\mathrm{mm}}{2 \cdot 160\,\mathrm{mm}}}\right)} \\
  &= 0.258
\end{aligned}
$$

## Gebraucht von

- [[Torsionswiderstandsmoment des Rechtecks]]

## Im Code

- [[opencivil.nachweis.qa_holz_werte#HolzwerteQA|HolzwerteQA._torsion]]

## Themen

- [[Holzquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Torsion eines vollen Rechtecks lässt sich nach Saint-Venant mit einer
Reihe genau lösen. Aus ihr folgen das Torsionsträgheitsmoment und die
grösste Schubspannung, in der Mitte der langen Seite; $k_2$ verbindet
beides zu $W_T = k_2 h b^2$. Beim Quadrat ist $k_2 = 0.208$, beim sehr
schmalen Rechteck gegen 1/3.
