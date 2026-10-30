---
erzeugt: 676ccd20ddcf
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.5.10, Figur 26"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.5.10, Figur 26

*In der Herleitung: «Wirksame statische Höhe bis zu den Köpfen der Anker»*

$$
d_{v,out} = d - c_v
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d$ | – | mm | [[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]] |
| $c_v$ | Überdeckung der Durchstanzbewehrung unten | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d_{v,out} = d - c_v = 234\,\mathrm{mm} - 30\,\mathrm{mm} = 204\,\mathrm{mm}
$$

## Gebraucht von

- [[Durchstanzwiderstand im äusseren Nachweisschnitt]]

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#_mit_leisten|_mit_leisten]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ausserhalb der Durchstanzbewehrung reicht der Bruchkegel von der Zugbewehrung
bis zu den Köpfen der Anker auf der Druckseite; deren Überdeckung $c_v$ fehlt
der Platte dort (Figur 26). Darum ist $d_{v,out} = d - c_v$.
