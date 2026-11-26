---
erzeugt: 8843755f5a43
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 6.1.1.6, (29)"
---
> [!info] Normstelle
> SIA 264:2014, 6.1.1.6, (29)

*In der Herleitung: «Kleinster Verdübelungsgrad, Profil doppelsymmetrisch»*

$$
\eta_{min} = \max\left(1 - \frac{355\ \mathrm{N}/\mathrm{mm}^{2}}{f_y} \cdot \left(0.75 - 0.03 \cdot L_e\right);\ 0.4\right) \quad \left(L_e\ \text{in}\ \mathrm{m}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_y$ | Fliessgrenze des Profils | N/mm² | Zwischenwert |
| $L_e$ | Abstand der Momentennullpunkte | m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \eta_{min} &= \max\left(1 - \frac{355\ \mathrm{N}/\mathrm{mm}^{2}}{f_y} \cdot \left(0.75 - 0.03 \cdot L_e\right);\ 0.4\right) \\
  &= \max\left(1 - \frac{355\ \mathrm{N}/\mathrm{mm}^{2}}{355\,\mathrm{N}/\mathrm{mm}^{2}} \cdot \left(0.75 - 0.03 \cdot 12\right);\ 0.4\right) \\
  &= 0.61 \quad \left(L_e\ \text{in}\ \mathrm{m}\right)
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.qa_verbund#VerbundBiegungQA._verlangt|VerbundBiegungQA._verlangt]]

## Themen

- [[Verbundquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Mit weniger Dübeln gleitet die Fuge, bis der Träger seinen Widerstand
erreicht, und jeder Dübel muss sich dabei weiter verformen. Weil der
Schlupf mit der Spannweite wächst, steigt die Grenze mit $L_e$, dem Abstand
der Momentennullpunkte; ein Profil mit höherer Fliessgrenze dehnt sich
weiter, bevor es fliesst, und verlangt ebenfalls mehr. Nie weniger als
0.4, und über 25 m volle Verdübelung.

Die Formel gilt im positiven Moment eines doppelsymmetrischen Profils. Im
negativen Moment – wo das Moment die Seite des Betons zieht – und bei
anderen Profilen verlangt das Werkzeug volle Verdübelung (nach Vorgabe für
die anderen Profile und dafür, woran es das negative Moment erkennt).
