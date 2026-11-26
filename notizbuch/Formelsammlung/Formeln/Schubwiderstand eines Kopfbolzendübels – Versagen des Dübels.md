---
erzeugt: ecb8014cc640
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 6.1.2.1, (31)"
---
> [!info] Normstelle
> SIA 264:2014, 6.1.2.1, (31)

*In der Herleitung: «Versagen des Dübels»*

$$
P_{Rd,s} = \frac{0.8 \cdot f_u}{\gamma_v} \cdot \frac{\pi \cdot d^{2}}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_u$ | Zugfestigkeit des Dübels, höchstens 500 N/mm² | N/mm² | Zwischenwert |
| $\gamma_v$ | Widerstandsbeiwert der Verdübelung | – | Zwischenwert |
| $d$ | Schaftdurchmesser des Kopfbolzendübels | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
P_{Rd,s} = \frac{0.8 \cdot f_u}{\gamma_v} \cdot \frac{\pi \cdot d^{2}}{4} = \frac{0.8 \cdot 450\,\mathrm{N}/\mathrm{mm}^{2}}{1.25} \cdot \frac{\pi \cdot \left(19\,\mathrm{mm}\right)^{2}}{4} = 81.7\,\mathrm{kN}
$$

## Gebraucht von

- [[Schubwiderstand eines Kopfbolzendübels]]

## Im Code

- [[opencivil.nachweis.qa_verbund_kennzahlen#KennzahlenVerbundQA._duebel|KennzahlenVerbundQA._duebel]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Hier schert der Schaft selbst ab: $0.8 \cdot f_u$ über seine Fläche
$\pi d^2/4$. Die Zugfestigkeit zählt höchstens mit 500 N/mm², auch wo der
Stahl mehr hält; die Vorgabe 450 N/mm² ist die der Kopfbolzendübel in
SIA 263, Tabelle 3.

In festem Beton ist dieser Wert der kleinere, in weichem
[[Schubwiderstand eines Kopfbolzendübels – Betonstauchung]].
