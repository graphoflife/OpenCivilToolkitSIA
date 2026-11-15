---
erzeugt: fce274bfd5b3
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Torsionsträgheitsmoment, «Balken 300×500» (Rechteck)»*

$$
I_{T} = s_{\text{Q1}} \cdot \left(t_{\text{Q1}}\right)^{3} \cdot \left(\frac{1}{3} - 0.21 \cdot \frac{t_{\text{Q1}}}{s_{\text{Q1}}} \cdot \left(1 - \frac{\left(t_{\text{Q1}}\right)^{4}}{12 \cdot \left(s_{\text{Q1}}\right)^{4}}\right)\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $s_{\text{Q1}}$ | Längere Seite, Balken 300×500 | mm | [[Längere Seite eines Rechtecks]] |
| $t_{\text{Q1}}$ | Kürzere Seite, Balken 300×500 | mm | [[Kürzere Seite eines Rechtecks]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  I_{T,\text{Q1}} &= s_{\text{Q1}} \cdot \left(t_{\text{Q1}}\right)^{3} \cdot \left(\frac{1}{3} - 0.21 \cdot \frac{t_{\text{Q1}}}{s_{\text{Q1}}} \cdot \left(1 - \frac{\left(t_{\text{Q1}}\right)^{4}}{12 \cdot \left(s_{\text{Q1}}\right)^{4}}\right)\right) \\
  &= 500\,\mathrm{mm} \cdot \left(300\,\mathrm{mm}\right)^{3} \cdot \left(\frac{1}{3} - 0.21 \cdot \frac{300\,\mathrm{mm}}{500\,\mathrm{mm}} \cdot \left(1 - \frac{\left(300\,\mathrm{mm}\right)^{4}}{12 \cdot \left(500\,\mathrm{mm}\right)^{4}}\right)\right) \\
  &= 2817.37\,\cdot 10^{6}\,\mathrm{mm}^{4}
\end{aligned}
$$

## Gebraucht von

- [[Torsionssteifigkeit]]

## Im Code

- [[opencivil.stabwerk.querschnitte#_torsion|_torsion]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein voller Rechteckquerschnitt unter Torsion nach St. Venant: der Schub
läuft im Kreis um die Mitte, am stärksten in der Mitte der langen Seiten.
Genau gibt es $I_T$ nur als Reihe; die Formel ist die Näherung von Roark mit
der kürzeren Seite $t$ und der längeren $s$. Für ein dünnes Brett geht sie
gegen $\frac{1}{3}\,s\,t^3$; ein Quadrat ergibt $0.1408\,t^4$, die Reihe
$0.1406\,t^4$.

T- und Doppel-T-Querschnitte der Vorlagen zerfallen in solche Rechtecke, die
sich addieren; den Knoten zwischen Steg und Flansch lassen sie weg. Das und
die Steifigkeit eines gerissenen Betonquerschnitts stehen in [[TODO]].
