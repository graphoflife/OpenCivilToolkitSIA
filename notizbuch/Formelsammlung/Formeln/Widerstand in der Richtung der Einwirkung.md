---
erzeugt: 198cf767c8b6
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.1.2; 5.1.8"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.1.2; 5.1.8

*In der Herleitung: «Widerstand in der Richtung der Einwirkung»*

$$
M_{Rd} = \sqrt{M_{y,Rd}^{2} + M_{z,Rd}^{2}}
$$

*In der Herleitung: «Widerstand in der Richtung der Einwirkung»*

$$
M_{Rd} = \lambda \cdot M_{Ed}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{y,Rd}$ | – | kNm | Zwischenwert, [[Probe – Moment um y]] |
| $M_{z,Rd}$ | – | kNm | Zwischenwert, [[Probe – Moment um z]] |
| $\lambda$ | – | – | Zwischenwert |
| $M_{Ed}$ | – | kNm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
M_{Rd} = \sqrt{M_{y,Rd}^{2} + M_{z,Rd}^{2}} = \sqrt{\left(211.8\,\mathrm{kNm}\right)^{2} + \left(0\,\mathrm{kNm}\right)^{2}} = 211.8\,\mathrm{kNm}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{Rd} = \lambda \cdot M_{Ed} = 4.478 \cdot 100\,\mathrm{kNm} = 447.8\,\mathrm{kNm}
$$

## Gebraucht von

- [[Erfüllungsgrad]]

## Im Code

- [[opencivil.nachweis.qa_holz#HolzBiegungQA|HolzBiegungQA._ein_fall]]
- [[opencivil.nachweis.qa_holz_stabilitaet#HolzStabilitaetQA._urteil|HolzStabilitaetQA._urteil]]
- [[opencivil.nachweis.qa_stahl#StahlBiegungQA._linear|StahlBiegungQA._linear]]
- [[opencivil.nachweis.qa_stahl#StahlBiegungQA|StahlBiegungQA._plastisch]]
- [[opencivil.nachweis.qa_stahl_stabilitaet#StahlStabilitaetQA._urteil|StahlStabilitaetQA._urteil]]
- [[opencivil.nachweis.schiefe_biegung#SchiefeBiegung|SchiefeBiegung._ein_fall]]

## Themen

- [[Schiefe Biegung]]
- [[Stahlquerschnitt]]
- [[Knicken und Kippen]]
- [[Holzquerschnitt]]
- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Betrag des Momentenvektors der gefundenen Ebene. Weil die Ebene so
gesucht ist, dass ihr Moment in dieselbe Richtung zeigt wie die Einwirkung,
ist das der Widerstand in genau dieser Richtung – und der Erfüllungsgrad das
Verhältnis der Beträge.

Wo linear gerechnet wird – beim Holz, beim Stahl der Klassen 3 und 4 und
beim Knicken und Kippen –, wachsen die Spannungen mit dem Moment. Dann ist
der Widerstand das $\lambda$-fache der Einwirkung, mit dem $\lambda$, bei
dem die Gleichung des Nachweises aufgeht.
