---
erzeugt: 0698a2d7d89c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Schubfläche für V\_z: der Schnitt bei z»*

$$
A_{V,z} = \frac{I_y \cdot b_{V,z}}{S_{V,z}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $I_y$ | Trägheitsmoment um y | ·10⁶ mm⁴ | Zwischenwert |
| $b_{V,z}$ | Breite des Holzes auf dem Schnitt | mm | Zwischenwert |
| $S_{V,z}$ | Statisches Moment jenseits des Schnitts | cm³ | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
A_{V,z} = \frac{I_y \cdot b_{V,z}}{S_{V,z}} = \frac{853.3\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 160\,\mathrm{mm}}{3200\,\mathrm{cm}^{3}} = 42667\,\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Querkraftwiderstand eines Holzquerschnitts]]
- [[Schubspannung aus Querkraft im Holz]]

## Im Code

- [[opencivil.nachweis.qa_holz_werte#HolzwerteQA|HolzwerteQA._schub]]

## Themen

- [[Holzquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Fläche, durch die geteilt die Querkraft die grösste Schubspannung
gibt. Beim Rechteck sind es zwei Drittel der Fläche: die Schubspannung ist
in der Mitte anderthalb Mal so gross wie im Mittel.
