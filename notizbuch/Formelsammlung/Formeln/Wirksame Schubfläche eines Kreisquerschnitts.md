---
erzeugt: 24c2357ad722
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.4.1, (41)"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.4.1, (41)

*In der Herleitung: «Wirksame Schubfläche des runden Tragglieds»*

$$
A_v = \frac{2 \cdot A}{\pi}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A$ | Querschnitt des Tragglieds | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
A_v = \frac{2 \cdot A}{\pi} = \frac{2 \cdot 1018\,\mathrm{mm}^{2}}{\pi} = 648\,\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Querkraftwiderstand des Tragglieds]]

## Im Code

- [[opencivil.pfahl.innen_quer#InnererQuerwiderstand._tragglied|InnererQuerwiderstand._tragglied]]

## Themen

- [[Innerer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im Stahl trägt die Querkraft die Fläche, die in ihrer Richtung durchläuft
(SIA 263:2013, 5.1.4.1). Für runde Querschnitte nennt die Norm keinen Wert;
sie verweist auf SN EN 1993-1-1, die hier nicht vorliegt.

Ein dünner Ring, in dem der Schub überall gleich stark längs der Wand
fliesst: auf jeder Hälfte summiert sich dieser Fluss zu einer Kraft in
Richtung der Querkraft, 2·r·t·τ. Beide Hälften tragen 4·r·t·τ, bei einer
Fläche von 2·π·r·t -- also A_v = 2·A/π. Ein Vollstab ist ein Bündel solcher
Ringe; jeder trägt seine 2/π, zusammen wieder 2·A/π, für den Stab eher
wenig.

Vollstab ⌀ 36 mm: A = 1018 mm², A_v = 648 mm². Nach Vorgabe, nicht
nachgeschlagen.
