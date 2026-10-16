---
erzeugt: ad724b3a2f31
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Grenzwert der Durchbiegung, nach Vorgabe»*

$$
w_{max} = \frac{L}{350}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $L$ | Spannweite | m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
w_{max} = \frac{L}{350} = \frac{6\,\mathrm{m}}{350} = 17.1\,\mathrm{mm}
$$

## Im Code

- [[opencivil.nachweis.verformung#Verformung|Verformung._einen_fall]]

## Themen

- [[Verformung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Durchbiegung wird gegen einen Bruchteil der Spannweite gehalten: je
länger das Feld, desto mehr Durchbiegung ist erträglich. $L/350$ ist so
eingebaut, wie der Benutzer es vorgegeben hat -- nach Vorgabe, nicht
nachgeschlagen. Welche Grenze für ein Bauteil gilt, hängt davon ab, was es
trägt und was an ihm hängt; das entscheidet der Ingenieur.
