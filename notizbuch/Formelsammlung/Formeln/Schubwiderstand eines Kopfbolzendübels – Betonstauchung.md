---
erzeugt: dd51a4402c56
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 6.1.2.1, (30)"
---
> [!info] Normstelle
> SIA 264:2014, 6.1.2.1, (30)

*In der Herleitung: «Betonstauchung, C30/37»*

$$
P_{Rd,c} = \frac{0.29 \cdot d^{2}}{\gamma_v} \cdot \sqrt{f_{ck} \cdot E_{cm}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d$ | Schaftdurchmesser des Kopfbolzendübels | mm | Zwischenwert |
| $\gamma_v$ | Widerstandsbeiwert der Verdübelung | – | Zwischenwert |
| $f_{ck}$ | Charakteristische Zylinderdruckfestigkeit | N/mm² | Vorgabe |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  P_{Rd,c} &= \frac{0.29 \cdot d^{2}}{\gamma_v} \cdot \sqrt{f_{ck} \cdot E_{cm}} \\
  &= \frac{0.29 \cdot \left(19\,\mathrm{mm}\right)^{2}}{1.25} \cdot \sqrt{30\,\mathrm{N}/\mathrm{mm}^{2} \cdot 33620\,\mathrm{N}/\mathrm{mm}^{2}} \\
  &= 84.1\,\mathrm{kN}
\end{aligned}
$$

## Gebraucht von

- [[Schubwiderstand eines Kopfbolzendübels]]

## Im Code

- [[opencivil.nachweis.qa_verbund_kennzahlen#KennzahlenVerbundQA._duebel|KennzahlenVerbundQA._duebel]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Vor dem Schaft des Dübels wird der Beton gestaucht. Was er dort aufnimmt,
wächst mit der Fläche $d^2$ und mit der Wurzel aus Festigkeit und
Steifigkeit des Betons: ein steiferer Beton verteilt die Pressung über eine
grössere Länge des Schafts. Die Formel gilt für verformungsfähige Dübel,
deren Länge $h_D$ mindestens $4d$ misst; ein kürzerer weist schon sein Feld
ab. Liegen mehrere Betone im Querschnitt, rechnet das Werkzeug mit dem, der
am wenigsten trägt (nach Vorgabe).

Der kleinere Wert aus dieser Formel und
[[Schubwiderstand eines Kopfbolzendübels – Versagen des Dübels]] ist der
[[Schubwiderstand eines Kopfbolzendübels]].
