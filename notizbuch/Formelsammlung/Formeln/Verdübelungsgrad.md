---
erzeugt: de0016b50334
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 6.1.1.6, (29)"
---
> [!info] Normstelle
> SIA 264:2014, 6.1.1.6, (29)

$$
\eta = \frac{N}{N_f}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N$ | Dübel zwischen dem Schnitt und dem Momentennullpunkt | – | Zwischenwert |
| $N_f$ | Dübel für volle Verdübelung | – | [[Dübel für volle Verdübelung]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\eta = \frac{N}{N_f} = \frac{25}{34.99} = 0.715
$$

## Im Code

- [[opencivil.nachweis.qa_verbund#VerbundBiegungQA._verduebelung|VerbundBiegungQA._verduebelung]]

## Themen

- [[Verbundquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Welchen Anteil der vollen Verdübelung die eingebauten Dübel tragen. Bei
eins und darüber tragen Stahl und Beton wie ein Querschnitt. Darunter ist
der Träger teilweise verdübelt: der Beton trägt nur
[[Was die Dübel tragen]], und der Biegewiderstand sinkt. Wie klein der
Grad sein darf, sagt der
[[Kleinster Verdübelungsgrad|kleinste Verdübelungsgrad]].
