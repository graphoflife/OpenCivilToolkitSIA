---
erzeugt: 45e12a0f658b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
e_o = \frac{M_d}{N_{Ld}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_d$ | Moment der Ausmitten am Kopf | kNm | Zwischenwert |
| $N_{Ld}$ | Normalkraft aus den Lasten, ohne Eigengewicht | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
e_o = \frac{M_d}{N_{Ld}} = \frac{1.99\,\mathrm{kNm}}{99.5\,\mathrm{kN}} = 20\,\mathrm{mm}
$$

## Im Code

- [[opencivil.mauerwerk.nachweise#Normalkraft._kopf|Normalkraft._kopf]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Am Kopf eines Pfeilers wirken die Lasten mit ihren Ausmitten quer zur Wand:
eine Decke, die nur auf einem Teil der Dicke aufliegt, ein Träger neben der
Mitte. Ihre Momente summiert der Lastabtrag je Pfeiler zu $M_d$, ihre
Kräfte zu $N_{Ld}$ – ohne das Eigengewicht der Wand, das erst darunter
dazukommt. Der Quotient ist die Ausmitte der Lasten am Kopf; haben alle
dieselbe Ausmitte, ist er genau diese. Eine Decke, die 20 mm neben der Mitte
aufliegt, greift also mit 20 mm an, wie viel die Wand darunter auch wiegt.

Über die ganze Höhe rechnet der Nachweis mit der Normalkraft am Fuss und
setzt am Kopf diese Ausmitte an. Das Moment am Kopf ist so etwas grösser als
das der Lasten – nach Vorgabe, nicht nachgeschlagen, auf der sicheren Seite.
Lässt der Nachweis die Lasten wachsen, wachsen ihre Momente im selben
Verhältnis, und die Ausmitte bleibt.

Drücken die Lasten am Kopf nicht, lässt sich der Nachweis nicht führen:
unbewehrtes Mauerwerk trägt keinen Zug (SIA 266:2015, 4.1.2).

Ist der Kopf eingespannt, gilt diese Ausmitte nicht: die Einspannung nimmt
das Moment auf, und die Ausmitte am Kopf folgt aus dem
[[Gleichgewicht der verformten Wand – Ausmitte der Last und Auslenkung w]].
