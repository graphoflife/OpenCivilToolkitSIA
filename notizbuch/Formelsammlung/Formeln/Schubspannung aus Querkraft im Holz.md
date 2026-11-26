---
erzeugt: 59fbc2dbccd9
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Schubspannung aus V\_z, nach Jourawski»*

$$
\tau_{z,d} = \frac{|V_{z,Ed}|}{A_{V,z}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\vert V_{z,Ed}\vert $ | – | kN | Zwischenwert |
| $A_{V,z}$ | Schubfläche für eine Querkraft in z | mm² | [[Schubfläche nach Jourawski]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\tau_{z,d} = \frac{|V_{z,Ed}|}{A_{V,z}} = \frac{40\,\mathrm{kN}}{42667\,\mathrm{mm}^{2}} = 0.94\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Schubspannung aus zwei Querkräften]]

## Im Code

- [[opencivil.nachweis.qa_holz#HolzSchubQA._querkraft|HolzSchubQA._querkraft]]

## Themen

- [[Holzquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Querkraft durch die [[Schubfläche nach Jourawski]]: die grösste
Schubspannung des Querschnitts.
