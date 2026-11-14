---
erzeugt: a4626815929b
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.5.10, Figur 26"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.5.10, Figur 26

*In der Herleitung: «Wirksame statische Höhe bis zur Verankerung der Anker»*

$$
d_{v,out} = d - c_v
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d$ | – | mm | [[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]] |
| $c_v$ | Abstand der Verankerung der Durchstanzbewehrung von der Druckseite, unten | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d_{v,out} = d - c_v = 234\,\mathrm{mm} - 30\,\mathrm{mm} = 204\,\mathrm{mm}
$$

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#_leisten_schreiben|_leisten_schreiben]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ausserhalb der Durchstanzbewehrung reicht der Bruchkegel von der Zugbewehrung
bis zur Verankerung der Anker auf der Druckseite, bei ancoPLUS bis zu den
Köpfen; ihr Abstand $c_v$ von der Oberfläche fehlt der Platte dort
(Figur 26). Darum ist $d_{v,out} = d - c_v$.
