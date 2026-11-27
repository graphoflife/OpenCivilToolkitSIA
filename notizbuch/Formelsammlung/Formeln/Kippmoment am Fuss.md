---
erzeugt: 2e7136474d1a
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.1.9"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.1.9

*In der Herleitung: «Kippmoment am Fuss in x»*

$$
M_{0,x} = \sum_i F_{d,i} \cdot z_i
$$

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
M_{0,x} = \sum_i F_{d,i} \cdot z_i = 17065\,\mathrm{kNm}
$$

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._kippen|Lauf._kippen]]
- [[opencivil.erdbeben.ersatzkraft#Lauf._kraefte|Lauf._kraefte]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Moment der Geschosskräfte um die Einspannung: jede Kraft mal ihre Höhe.
Mit den Kräften aus dem Spektrum bei $q$ gehört es zur Bemessung des Kerns
am Fuss – besteht er aus getrennten Teilen, trägt jeder seinen Anteil an
den [[Trägheitsmomente des Kerns|Trägheitsmomenten]]. Liegt $q$
über 2.0, ist das Tragwerk duktil bemessen; für schlanke Tragwände gelten
dann die Bemessungswerte von SIA 262:2025, 4.3.9.4, die hier nicht
gerechnet werden. Für
Abheben und Kippen des Gebäudes rechnet die Herleitung es ein zweites Mal
mit $q = 1.0$ (16.5.1.9). Ob das Fundament diese Momente trägt, ist ein
eigener Nachweis und nicht Teil dieser Rechnung.
