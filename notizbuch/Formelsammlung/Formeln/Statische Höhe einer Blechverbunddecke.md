---
erzeugt: 3563dc59f49c
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.4.3.3; Figur 9"
---
> [!info] Normstelle
> SIA 264:2014, 5.4.3.3; Figur 9

*In der Herleitung: «Statische Höhe – bis zum Schwerpunkt des Blechs»*

$$
d_p = h - e
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h$ | Dicke der Decke | mm | Zwischenwert |
| $e$ | Schwerpunkt des Blechs über seiner Unterkante | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d_p = h - e = 140\,\mathrm{mm} - 31.1\,\mathrm{mm} = 108.9\,\mathrm{mm}
$$

## Gebraucht von

- [[Längsschubwiderstand nach der m-k-Methode]]
- [[Querkraftwiderstand einer Blechverbunddecke]]
- [[Schlankheit einer Blechverbunddecke]]

## Im Code

- [[opencivil.nachweis.qa_blechverbund#KennzahlenBlechQA._form|KennzahlenBlechQA._form]]

## Themen

- [[Blechverbunddecke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die statische Höhe $d_p$ reicht von der Oberkante der Decke bis zum
Schwerpunkt des Blechs, dorthin, wo das Blech seine Zugkraft trägt. So ist
sie in Figur 9 der SIA 264 eingezeichnet.

Gebraucht wird sie für den
[[Querkraftwiderstand einer Blechverbunddecke|Querkraftwiderstand]], für
den [[Längsschubwiderstand nach der m-k-Methode|Längsschubwiderstand]] und
für die [[Schlankheit einer Blechverbunddecke|Schlankheit]] $L/d_p$. Der
Biegewiderstand braucht sie nicht: er kommt aus dem plastischen Zustand
des ganzen Querschnitts.

Über 150 mm verweist die Norm für die Querkraft auf SIA 262. Das rechnet das
Werkzeug für die Decke nicht; die Querkraft steht dann grau.
