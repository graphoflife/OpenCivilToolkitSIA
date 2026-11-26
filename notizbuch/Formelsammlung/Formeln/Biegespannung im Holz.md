---
erzeugt: d397b6b1c28b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Biegespannung um y, an der weitesten Faser»*

$$
\sigma_{m,y,d} = \frac{|M_{y,Ed}|}{W_y}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\vert M_{y,Ed}\vert $ | – | kNm | Zwischenwert |
| $W_y$ | Widerstandsmoment um y, bis zur weitesten Faser | cm³ | [[Widerstandsmoment bis zur weitesten Faser]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{m,y,d} = \frac{|M_{y,Ed}|}{W_y} = \frac{30\,\mathrm{kNm}}{4266.7\,\mathrm{cm}^{3}} = 7.03\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.nachweis.qa_holz#HolzBiegungQA._biegespannung|HolzBiegungQA._biegespannung]]
- [[opencivil.nachweis.qa_holz_stabilitaet#_Herleitung._biegespannung|_Herleitung._biegespannung]]

## Themen

- [[Holzquerschnitt]]
- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Linear-elastisch wächst die Biegespannung mit dem Abstand von der
Nulllinie und ist an der weitesten Faser am grössten:
$\sigma_m = M/W$, mit dem
[[Widerstandsmoment bis zur weitesten Faser]]. Beim Rechteck ist
$W = b h^2/6$. Liegen die Fasern ungleich weit vom Schwerpunkt, nimmt das
Werkzeug die weitere – auf der sicheren Seite.
