---
erzeugt: 081634615512
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 6.1.2.1, (30) und (31)"
---
> [!info] Normstelle
> SIA 264:2014, 6.1.2.1, (30) und (31)

$$
P_{Rd} = \min\left(P_{Rd,c};\ P_{Rd,s}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $P_{Rd,c}$ | Schubwiderstand, Betonstauchung | kN | [[Schubwiderstand eines Kopfbolzendübels – Betonstauchung]] |
| $P_{Rd,s}$ | Schubwiderstand, Versagen des Dübels | kN | [[Schubwiderstand eines Kopfbolzendübels – Versagen des Dübels]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
P_{Rd} = \min\left(P_{Rd,c};\ P_{Rd,s}\right) = \min\left(84.1\,\mathrm{kN};\ 81.7\,\mathrm{kN}\right) = 81.7\,\mathrm{kN}
$$

## Gebraucht von

- [[Dübel für volle Verdübelung]]
- [[Was die Dübel tragen]]

## Im Code

- [[opencivil.nachweis.qa_verbund_kennzahlen#KennzahlenVerbundQA._duebel|KennzahlenVerbundQA._duebel]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Dübel versagt auf die schwächere Art: entweder staucht der Beton vor
dem Schaft ([[Schubwiderstand eines Kopfbolzendübels – Betonstauchung]]),
oder der Schaft schert ab
([[Schubwiderstand eines Kopfbolzendübels – Versagen des Dübels]]). Der
kleinere Wert ist sein Widerstand.

$\gamma_v = 1.25$ gilt immer, auch wo die Tragsicherheit mit
charakteristischen Werten rechnet: der Dübel ist kein Material des
Projekts mit eigener Wahl (nach Vorgabe).
