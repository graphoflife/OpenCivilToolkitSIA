---
erzeugt: a474d55b5078
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 6.1.1.6, (29)"
---
> [!info] Normstelle
> SIA 264:2014, 6.1.1.6, (29)

$$
N_f = \frac{N_{c,f}}{P_{Rd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{c,f}$ | Kraft in Beton und Betonstahl ausserhalb der Profile, bei voller Verdübelung | kN | [[Kraft im Beton bei voller Verdübelung]] |
| $P_{Rd}$ | Schubwiderstand eines Kopfbolzendübels | kN | [[Schubwiderstand eines Kopfbolzendübels]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_f = \frac{N_{c,f}}{P_{Rd}} = \frac{2857\,\mathrm{kN}}{81.7\,\mathrm{kN}} = 34.99
$$

## Gebraucht von

- [[Verdübelungsgrad]]

## Im Code

- [[opencivil.nachweis.qa_verbund#VerbundBiegungQA._verduebelung|VerbundBiegungQA._verduebelung]]

## Themen

- [[Verbundquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

So viele Dübel braucht die Fuge zwischen dem Schnitt und dem
Momentennullpunkt, um die [[Kraft im Beton bei voller Verdübelung]] zu
tragen, jeder mit dem [[Schubwiderstand eines Kopfbolzendübels]]. Die Zahl
ist keine ganze: verglichen wird das Verhältnis, der [[Verdübelungsgrad]].
