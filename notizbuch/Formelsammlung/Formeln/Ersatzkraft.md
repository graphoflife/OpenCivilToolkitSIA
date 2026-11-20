---
erzeugt: 19d8246c5db7
art: formel
tags: [formel]
normstelle: ["SIA 261:2020, 16.5.2.4, (41)", "SIA 261:2020, 16.5.1.9"]
---
> [!info] Normstellen
> SIA 261:2020, 16.5.2.4, (41) · SIA 261:2020, 16.5.1.9

*In der Herleitung: «Ersatzkraft in x»*

$$
F_{d,x} = S_{d,x} \cdot \sum W
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $S_{d,x}$ | Ordinate des Bemessungsspektrums | – | [[Bemessungsspektrum (32)]], [[Bemessungsspektrum (31)]], [[Bemessungsspektrum (33)]] |
| $\sum W$ | Gewicht des Gebäudes | kN | [[Gewicht des Gebäudes]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
F_{d,x} = S_{d,x} \cdot \sum W = 0.193 \cdot 10220\,\mathrm{kN} = 1976\,\mathrm{kN}
$$

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._kippen|Lauf._kippen]]
- [[opencivil.erdbeben.ersatzkraft#Lauf._kraefte|Lauf._kraefte]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Beben als eine waagrechte Kraft je Hauptrichtung, am ganzen Gebäude:
sein Gewicht mal die Ordinate des Spektrums bei der Grundschwingzeit
(16.5.2.4). Jede Richtung hat ihr eigenes $T_1$ und ihr eigenes $q$
(16.5.1.5); gerechnet wird in jeder ein ebenes Modell, ohne die andere.

Für Abheben und Kippen verlangt die Norm $q = 1.0$ (16.5.1.9). Die
Herleitung rechnet $F_d$ darum ein zweites Mal mit dem Spektrum bei $q = 1$
-- daher die zweite Normstelle der Seite.
