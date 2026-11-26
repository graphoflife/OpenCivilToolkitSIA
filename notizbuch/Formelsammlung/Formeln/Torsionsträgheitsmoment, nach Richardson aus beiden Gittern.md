---
erzeugt: 1ec351788d3e
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
I_T = \frac{4 \cdot I_{T,fein} - I_{T,grob}}{3}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $I_{T,fein}$ | – | ·10⁶ mm⁴ | Zwischenwert |
| $I_{T,grob}$ | – | ·10⁶ mm⁴ | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
I_T = \frac{4 \cdot I_{T,fein} - I_{T,grob}}{3} = \frac{4 \cdot 1.7\,\cdot 10^{6}\,\mathrm{mm}^{4} - 1.7\,\cdot 10^{6}\,\mathrm{mm}^{4}}{3} = 1.6\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

## Gebraucht von

- [[Saint-Venant-Anteil der Kippspannung]]

## Im Code

- [[opencivil.querschnitt.analyse#Querschnittsanalyse.torsion_protokollieren|Querschnittsanalyse.torsion_protokollieren]]

## Themen

- [[Querschnittsanalyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Gitter legt Rechteckzellen über den Umriss, die längere Seite in 30
geteilt, und jede waagrechte und lotrechte Kante liegt auf einer seiner
Linien: Rechteck, T und Hohlkasten treffen es genau. Je Zelle mit Material
gibt es einen Wert φ in ihrer Mitte. Zwischen zwei Nachbarn fliesst die
Länge ihrer gemeinsamen Kante, geteilt durch den Abstand der Mitten, mal den
Unterschied in φ. Liegt der Rand zwischen zwei Mitten, zählt der Abstand bis
zu ihm, an einer schrägen Kante genau geschnitten. Jeder Hohlraum ist ein
einziger Wert, belastet mit $2A_k$. Das gibt ein symmetrisches
Gleichungssystem; gelöst wird es mit konjugierten Gradienten, und $I_T$ ist
Last mal Lösung.

Der Fehler fällt mit dem Quadrat der Zellgrösse $h$:
$I_{T,h} \approx I_T + c\,h^2$. Ein zweites Gitter, jede Zelle halbiert, hat
noch $c\,h^2/4$, und $(4\,I_{T,fein} - I_{T,grob})/3$ hebt den Fehler heraus
(Extrapolation nach Richardson). Das zählt vor allem bei dünnen Wänden: mit
$n$ Zellen über die Dicke rechnet ein Gitter um etwa $2/n^2$ zu steif. Liegen
die beiden Gitter mehr als 5 % auseinander, ist das grobe zu grob, meist für
eine dünne schräge Wand, und es wird feiner gerechnet.

Gegen genaue Werte geprüft: Rechteck, gleichseitiges Dreieck, Kreis und Rohr
auf ein Promille; ein dünner Hohlkasten liegt knapp über Bredt, wie er soll.
Gerechnet wird am ungerissenen Querschnitt ohne Bewehrung -- was Risse daraus
machen, steht in [[TODO]].
