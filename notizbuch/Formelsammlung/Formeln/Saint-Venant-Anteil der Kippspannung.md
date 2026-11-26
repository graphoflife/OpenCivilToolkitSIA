---
erzeugt: 41c69e515fc5
art: formel
tags: [formel]
normstelle: "SIA 263:2013, Anhang B.4, (92)"
---
> [!info] Normstelle
> SIA 263:2013, Anhang B.4, (92)

*In der Herleitung: «Saint-Venant-Anteil, mit K = I\_T»*

$$
\sigma_{Dv} = \frac{\eta \cdot \pi}{L_{D} \cdot W_{el}} \cdot \sqrt{G_{a} \cdot I_T \cdot E_{a} \cdot I_z}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta$ | Beiwert der Momentenverteilung beim Kippen | – | [[Beiwert η der Momentenverteilung beim Kippen]] |
| $L_{D}$ | Kipplänge | mm | Zwischenwert |
| $W_{el}$ | Elastisches Widerstandsmoment, ganzer Querschnitt | cm³ | Zwischenwert, [[Widerstandsmoment bis zur weitesten Faser]] |
| $G_{a}$ | Schubmodul des Baustahls | N/mm² | Vorgabe |
| $I_T$ | Torsionsträgheitsmoment nach St. Venant | ·10⁶ mm⁴ | [[Torsionsträgheitsmoment, nach Richardson aus beiden Gittern]] |
| $E_{a}$ | Elastizitätsmodul des Baustahls | N/mm² | Vorgabe |
| $I_z$ | Trägheitsmoment um z | ·10⁶ mm⁴ | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \sigma_{Dv} &= \frac{\eta \cdot \pi}{L_{D} \cdot W_{el}} \cdot \sqrt{G_{a,\text{S355}} \cdot I_T \cdot E_{a,\text{S355}} \cdot I_z} \\
  &= \frac{1.75 \cdot \pi}{3000\,\mathrm{mm} \cdot 3070.7\,\mathrm{cm}^{3}} \cdot \sqrt{81000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 1.6\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 210000\,\mathrm{N}/\mathrm{mm}^{2} \cdot 33.9\,\cdot 10^{6}\,\mathrm{mm}^{4}} \\
  &= 581.7\,\mathrm{N}/\mathrm{mm}^{2}
\end{aligned}
$$

## Gebraucht von

- [[Ideelle Kippspannung]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.kippen|_Herleitung.kippen]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Teil der [[Ideelle Kippspannung|ideellen Kippspannung]], den die
Torsionssteifigkeit $G \cdot I_T$ des ganzen Querschnitts trägt, zusammen
mit seiner Biegesteifigkeit um die schwache Achse. Er fällt mit der
Kipplänge und wächst mit $\eta$. $I_T$ rechnet die Querschnittsanalyse
am gezeichneten Querschnitt.

Ein offener, dünnwandiger Querschnitt ist weich gegen Torsion; bei ihm
ist der Anteil klein. Erfüllt der Querschnitt Klasse 3 nicht, setzt B.4
ihn null – das Werkzeug tut das bei einem Fall in Klasse 4.
