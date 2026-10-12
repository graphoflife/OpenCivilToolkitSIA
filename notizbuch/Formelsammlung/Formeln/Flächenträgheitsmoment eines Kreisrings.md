---
erzeugt: f6adef77f9a2
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment, «Rohr» (Kreisring)»*

$$
I_{\text{Q3}} = \frac{\pi \cdot \left(\left(D_{\text{Q3}}\right)^{4} - \left(D_{\text{Q3}} - 2 \cdot t_{\text{Q3}}\right)^{4}\right)}{64}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $D_{\text{Q3}}$ | Aussendurchmesser, Rohr | mm | Vorgabe |
| $t_{\text{Q3}}$ | Wanddicke, Rohr | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{\text{Q3}} &= \frac{\pi \cdot \left(\left(D_{\text{Q3}}\right)^{4} - \left(D_{\text{Q3}} - 2 \cdot t_{\text{Q3}}\right)^{4}\right)}{64} \\
  &= \frac{\pi \cdot \left(\left(168.3\,\mathrm{mm}\right)^{4} - \left(168.3\,\mathrm{mm} - 2 \cdot 10\,\mathrm{mm}\right)^{4}\right)}{64} \\
  &= 15.64\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie die Fläche: das Trägheitsmoment des Aussenkreises minus das des
Innenkreises, beide um dieselbe Achse. Weil das Material weit aussen liegt,
trägt ein Rohr mit wenig Fläche viel Biegung.
