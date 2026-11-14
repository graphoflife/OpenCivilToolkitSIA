---
erzeugt: 102944cb6aca
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.5.2.4.2"
---
> [!info] Normstelle
> SIA 267:2013, 9.5.2.4.2

*In der Herleitung: «Materialwiderstand auf Zug: nur der Stahl»*

$$
R_{mat,d,Z} = A_s \cdot \sigma_s
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_s$ | Fläche der Längsbewehrung | mm² | [[Fläche der Längsbewehrung]], [[Fläche des Tragrohrs nach Abrostung]], [[Fläche des Tragstabs nach Abrostung]] |
| $\sigma_s$ | Spannung im Stahl auf Zug, als Betrag | N/mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
R_{mat,d,Z} = A_s \cdot \sigma_s = 3770\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} = 1639\,\mathrm{kN}
$$

## Gebraucht von

- [[Innerer Widerstand des Pfahls]]

## Im Code

- [[opencivil.pfahl.innen#InnererWiderstand._normalkraft|InnererWiderstand._normalkraft]]

## Themen

- [[Innerer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Auf Zug trägt der Beton nichts: es bleibt der Stahl, gedehnt, bis er fliesst
(SIA 267:2013, 9.5.2.4.2). Beim Mikropfahl trägt auch auf Druck nur das
Tragglied (9.5.2.4.8), und weil kein Beton die Stauchung begrenzt, ebenfalls
mit f_yd. Zwölf Stäbe ⌀ 20 aus B500B tragen 3770 mm² · 435 N/mm² = 1639 kN.
