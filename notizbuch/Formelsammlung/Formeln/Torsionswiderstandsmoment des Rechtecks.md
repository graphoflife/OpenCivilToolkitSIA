---
erzeugt: caca1329586c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Torsionswiderstandsmoment: τ\_tor = T/W\_T»*

$$
W_T = k_2 \cdot h \cdot b^2
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_2$ | Torsionsbeiwert des Rechtecks | – | [[Torsionsbeiwert des Rechtecks]] |
| $h$ | Lange Seite des Rechtecks | mm | Zwischenwert |
| $b$ | Kurze Seite des Rechtecks | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
W_T = k_2 \cdot h \cdot b^2 = 0.258 \cdot 400\,\mathrm{mm} \cdot \left(160\,\mathrm{mm}\right)^2 = 2637.7\,\mathrm{cm}^{3}
$$

## Gebraucht von

- [[Schubspannung aus Torsion im Holz]]
- [[Torsionswiderstand eines Rechtecks aus Holz]]

## Im Code

- [[opencivil.nachweis.qa_holz_werte#HolzwerteQA|HolzwerteQA._torsion]]

## Themen

- [[Holzquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie das Widerstandsmoment bei der Biegung: das Torsionsmoment durch $W_T$
gibt die grösste Schubspannung. $b$ ist die kurze Seite, $h$ die lange,
$k_2$ der [[Torsionsbeiwert des Rechtecks]].
