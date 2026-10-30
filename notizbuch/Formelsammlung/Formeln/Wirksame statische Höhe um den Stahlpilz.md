---
erzeugt: a623bc27841d
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.6.2"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.6.2

*In der Herleitung: «Wirksame statische Höhe bis zur Unterkante des Pilzes»*

$$
d_{v,P} = d - c_P
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d$ | – | mm | [[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]] |
| $c_P$ | – | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d_{v,P} = d - c_P = 234\,\mathrm{mm} - 20\,\mathrm{mm} = 214\,\mathrm{mm}
$$

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#_mit_pilz|_mit_pilz]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ausserhalb des Stahlpilzes beginnt der Bruchkegel an seiner Unterkante.
Darum reicht die wirksame Höhe von der Zugbewehrung bis dorthin: $d$ weniger
den Beton unter dem Pilz, 20 mm nach den Vorgaben der Software von AncoTech.
Gelesen aus 4.3.6.2.1 und Figur 21, nicht nachgeschlagen.
