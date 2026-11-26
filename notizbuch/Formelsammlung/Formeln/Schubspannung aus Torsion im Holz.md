---
erzeugt: 3f447db1e516
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Schubspannung aus Torsion, in der Mitte der langen Seite»*

$$
\tau_{tor,d} = \frac{|T_{Ed}|}{W_T}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\vert T_{Ed}\vert $ | – | kNm | Zwischenwert |
| $W_T$ | Torsionswiderstandsmoment des Rechtecks | cm³ | [[Torsionswiderstandsmoment des Rechtecks]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\tau_{tor,d} = \frac{|T_{Ed}|}{W_T} = \frac{1\,\mathrm{kNm}}{2637.7\,\mathrm{cm}^{3}} = 0.38\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.nachweis.qa_holz#HolzSchubQA|HolzSchubQA._torsion]]

## Themen

- [[Holzquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Torsionsmoment durch das
[[Torsionswiderstandsmoment des Rechtecks]]: die grösste Schubspannung, in
der Mitte der langen Seite.
