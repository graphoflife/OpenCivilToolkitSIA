---
erzeugt: 9f2796883f7e
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Es trägt das stärkere der beiden Gewölbe»*

$$
p_{Rd} = \max\left(p_{Rd,v};\ p_{Rd,h}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $p_{Rd,v}$ | Widerstand des lotrechten Gewölbes | kN/m² | Zwischenwert |
| $p_{Rd,h}$ | Widerstand des waagrechten Gewölbes | kN/m² | [[Widerstand des waagrechten Druckgewölbes einer Wand]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
p_{Rd} = \max\left(p_{Rd,v};\ p_{Rd,h}\right) = \max\left(2.33\,\mathrm{kN}/\mathrm{m}^{2};\ 14.46\,\mathrm{kN}/\mathrm{m}^{2}\right) = 14.46\,\mathrm{kN}/\mathrm{m}^{2}
$$

## Im Code

- [[opencivil.mauerwerk.querlast#Querlastnachweis.stelle|Querlastnachweis.stelle]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Wand trägt Querlast lotrecht zu Kopf und Fuss oder, wenn ihre Ränder
gehalten sind, waagrecht zu den Rändern (SIA 266:2015, 4.3.4.2, Figur 11).
Ob sich die beiden Gewölbe die Last teilen dürfen, sagt die Norm nicht.
Mauerwerk verformt sich wenig, bevor es versagt, und die beiden Gewölbe
erreichen ihre Grenze kaum bei derselben Durchbiegung. Das Werkzeug zählt
darum nur das stärkere, nicht beide zusammen – nach Vorgabe, nicht
nachgeschlagen, auf der sicheren Seite.

Ein Pfeiler bekommt die Querlast bis zur Mitte der Öffnungen neben ihm, am
Ende der Wand bis zu diesem: Brüstungen und Stürze geben die Last ihrer
Fläche an die Pfeiler daneben ab – nach Vorgabe, nicht nachgeschlagen. Sein
lotrechtes Gewölbe trägt so die Last der Breite $b_q$ auf seiner Breite
$l_w$; $p_{Rd,v}$ ist darum der Widerstand eines Streifens ohne Öffnungen,
mal $l_w/b_q$. Das waagrechte Gewölbe zählt nur in einer Wand ohne
Öffnung, deren Ränder beide gehalten und deren Stossfugen vollfugig
vermörtelt sind (4.3.4.3).

Beispiel: die Wand zwischen Querwänden im Prüfprojekt, 2.4 m breit, 2.7 m
hoch, 175 mm Kalksandstein. Lotrecht trägt sie 2.33 kN/m², waagrecht
14.46 kN/m². Es zählt das waagrechte Gewölbe; unter 1.5 kN/m² Wind ist der
Erfüllungsgrad 9.64.
