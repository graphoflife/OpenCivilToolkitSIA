---
erzeugt: 489756d2e6ea
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «So weit darf τ\_d wachsen, mit der Torsion zusammen»*

$$
\tau_{Rd} = \lambda \cdot \tau_d
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\lambda$ | – | – | Zwischenwert |
| $\tau_d$ | Schubspannung aus beiden Querkräften | N/mm² | [[Schubspannung aus zwei Querkräften]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\tau_{Rd} = \lambda \cdot \tau_d = 1.249 \cdot 0.94\,\mathrm{N}/\mathrm{mm}^{2} = 1.18\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.nachweis.qa_holz#HolzSchubQA|HolzSchubQA._ein_fall]]

## Themen

- [[Holzquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie weit die Schubspannung aus Querkraft wachsen darf, wenn die Torsion im
selben Verhältnis mitwächst. Ihr Verhältnis zur Einwirkung ist der
Erfüllungsgrad – dieselbe Idee wie
[[Widerstand in der Richtung der Einwirkung]] bei der Biegung.
