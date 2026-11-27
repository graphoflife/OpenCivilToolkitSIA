---
erzeugt: 9e01a717e38e
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.4.3.5"
---
> [!info] Normstelle
> SIA 264:2014, 5.4.3.5

*In der Herleitung: «Schublänge, gleichmässig verteilt – Endfeld»*

$$
L_s = \frac{0.9 \cdot L}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $L$ | Spannweite | m | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
L_s = \frac{0.9 \cdot L}{4} = \frac{0.9 \cdot 3\,\mathrm{m}}{4} = 675\,\mathrm{mm}
$$

## Gebraucht von

- [[Längsschubwiderstand nach der m-k-Methode]]

## Im Code

- [[opencivil.nachweis.qa_blechverbund#KennzahlenBlechQA|KennzahlenBlechQA._laengsschub]]

## Themen

- [[Blechverbunddecke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die m-k-Methode beruht auf Versuchen an Decken über ein Feld. Die
Schublänge $L_s$ ist das Stück vom Auflager bis zur Last, auf dem der
Längsschub die Verbindung von Blech und Beton beansprucht:

- unter gleichmässiger Last über das ganze Feld ein Viertel der
  Spannweite;
- unter zwei gleichen Einzellasten, symmetrisch im Feld, der Abstand $a$
  der Last vom nächsten Auflager.

Ein Feld einer durchlaufenden Decke darf als Einfeld mit kürzerer
Spannweite gerechnet werden: das Endfeld mit $0.9\,L$, ein Innenfeld mit
$0.8\,L$ (SIA 264, 5.4.3.5).

Andere Lastbilder lässt die Norm mit Versuchen oder Näherungen zu; das
Werkzeug kennt nur die beiden. Ob der Abstand $a$ in einem durchlaufenden
Feld ebenso verkürzt wird, sagt die Norm nicht: das Werkzeug nimmt ihn, wie
er eingegeben ist.
