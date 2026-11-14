---
erzeugt: d8bd242d7564
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.4.4.1.1"
---
> [!info] Normstelle
> SIA 267:2013, 9.4.4.1.1

*In der Herleitung: «Äusserer Widerstand auf Zug, charakteristisch: nur der Mantel»*

$$
R_{a,k,Z} = R_{s,k}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $R_{s,k}$ | Mantelwiderstand | kN | [[Mantelwiderstand]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
R_{a,k,Z} = R_{s,k} = 1085\,\mathrm{kN}
$$

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._aus_schichten]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wird der Pfahl gezogen, trägt der Fuss nichts: es bleibt der Mantel. Hier mit
derselben Mantelreibung wie auf Druck -- nach Vorgabe, nicht nachgeschlagen.
Der Pfahl selbst muss die Zugkraft dabei über seine ganze Länge tragen
(SIA 267:2013, 9.5.3.4.2).
