---
erzeugt: 31a4a773e215
art: formel
tags: [formel]
normstelle: ["SIA 264:2014, 5.3.2.10, (20)", "SIA 264:2014, 5.3.3.3, (23); 5.3.4.1"]
---
> [!info] Normstellen
> SIA 264:2014, 5.3.2.10, (20) · SIA 264:2014, 5.3.3.3, (23); 5.3.4.1

*In der Herleitung: «Kritische Normalkraft um z»*

$$
N_{cr,z} = \frac{\pi^2 \cdot (EI)_{eff,\lambda,z}}{L_{K,z}^2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $(EI)_{eff,\lambda,z}$ | Biegesteifigkeit | MNm² | [[Biegesteifigkeit einer Verbundstütze für die Schlankheit]] |
| $L_{K,z}$ | Knicklänge | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{cr,z} = \frac{\pi^2 \cdot (EI)_{eff,\lambda,z}}{L_{K,z}^2} = \frac{\pi^2 \cdot 74.6\,\mathrm{MNm}^{2}}{\left(6000\,\mathrm{mm}\right)^2} = 20438.6\,\mathrm{kN}
$$

## Gebraucht von

- [[Bezogene Schlankheit einer Verbundstütze]]
- [[Vergrösserungsfaktor der Imperfektion einer Verbundstütze]]
- [[Vergrösserungsfaktor einer Verbundstütze]]

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall|_Fall._knicken]]
- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._zweite_ordnung|_Fall._zweite_ordnung]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die ideale Knicklast nach Euler, π² EI / L². Die Verbundstütze braucht sie
zweimal, mit je eigener Steifigkeit und Länge.

Für die Schlankheit, N_cr nach (20), gilt die Steifigkeit für die
Schlankheit und die Knicklänge der Achse. Diese Knicklast ist kein Widerstand; sie dient
der [[Bezogene Schlankheit einer Verbundstütze|bezogenen Schlankheit]].
Eine Knicklänge null heisst gehalten: um diese Achse knickt die Stütze
nicht.

Für die Bemessung, N_cr,eff nach (23), gilt die
[[Bemessungssteifigkeit einer Verbundstütze|Bemessungssteifigkeit]] und
als Knicklänge die Länge der Stütze: sie ist an ihren Enden seitlich
unverschieblich gehalten (5.3.4.1). Darum verlangt das Werkzeug um eine
Achse mit Moment, dass die Knicklänge nicht länger ist als die Stütze, und
bittet sonst um die Länge der Stütze. Mit N_cr,eff wächst das Moment im
[[Vergrösserungsfaktor einer Verbundstütze]].

Erreicht |N_Ed| N_cr,eff, knickt die Stütze aus: das Moment wüchse ohne
Grenze, und der Nachweis ist nicht erfüllt. Der Erfüllungsgrad ist dann
N_cr,eff/|N_Ed|.
