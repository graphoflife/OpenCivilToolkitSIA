---
erzeugt: e859ce498756
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 4.5.2.2, (9); 4.5.2.3, (10)"
---
> [!info] Normstelle
> SIA 263:2013, 4.5.2.2, (9); 4.5.2.3, (10)

$$
M_{D,Rd} = \chi_{D} \cdot M_{y,Rd}^{+}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\chi_{D}$ | Abminderung beim Kippen | – | [[Abminderungsfaktor beim Knicken und Kippen]] |
| $M_{y,Rd}^{+}$ | Biegewiderstand des Querschnitts | kNm | [[Plastischer Biegewiderstand eines Stahlquerschnitts]], [[Biegewiderstand bis zum ersten Fliessen]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{D,Rd} = \chi_{D} \cdot M_{y,Rd}^{+} = 0.962 \cdot 1188\,\mathrm{kNm} = 1142.5\,\mathrm{kNm}
$$

## Gebraucht von

- [[Abgeminderter Kippwiderstand im Stab]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung.kippen|_Herleitung.kippen]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was der Träger an Moment trägt, bevor er kippt: der Biegewiderstand des
Querschnitts, gemindert mit $\chi_D$ (9). Wie beim Knicken fasst der
[[Abminderungsfaktor beim Knicken und Kippen]] zusammen, dass ein
wirklicher Träger weder das volle Moment des Querschnitts noch das
[[Ideelles Kippmoment|ideelle Kippmoment]] erreicht.

Der Biegewiderstand folgt der Klasse: plastisch in den Klassen 1 und 2,
elastisch in 3, am wirksamen Querschnitt in 4. Wo der Druckgurt
seitlich gehalten ist ($L_D = 0$), kippt der Träger nicht, und es bleibt
der Biegewiderstand.
