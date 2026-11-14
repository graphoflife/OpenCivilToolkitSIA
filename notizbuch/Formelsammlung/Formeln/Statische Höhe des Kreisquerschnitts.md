---
erzeugt: 87660ee0dd66
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4.2"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4.2

*In der Herleitung: «Statische Höhe: bis zum Schwerpunkt der Stäbe in der gezogenen Hälfte»*

$$
d = \frac{D}{2} + \frac{2 \cdot r_s}{\pi}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $D$ | Durchmesser des Pfahls | mm | Vorgabe |
| $r_s$ | Radius des Bewehrungskreises | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
d = \frac{D}{2} + \frac{2 \cdot r_s}{\pi} = \frac{900\,\mathrm{mm}}{2} + \frac{2 \cdot 355\,\mathrm{mm}}{\pi} = 676\,\mathrm{mm}
$$

## Gebraucht von

- [[Hebelarm der inneren Kräfte]]
- [[Stegbreite des Kreisquerschnitts]]

## Im Code

- [[opencivil.pfahl.innen_quer#InnererQuerwiderstand._fachwerk|InnererQuerwiderstand._fachwerk]]

## Themen

- [[Innerer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im runden Pfahl liegen die Längsstäbe auf einem Kreis statt in einer Lage.
Bei mehreren Lagen zählt für die Querkraft der Schwerpunkt der gezogenen
Bewehrung (SIA 262:2025, 4.3.3.4.2). Gezogen ist hier die Hälfte der Stäbe,
die dem Druck gegenüberliegt; gleichmässig auf dem Halbkreis verteilt, liegt
ihr Schwerpunkt 2·r_s/π neben der Achse, wie der eines Halbkreisbogens. Die
statische Höhe reicht vom gedrückten Rand bis dorthin.

⌀ 900 mm, die Stäbe auf r_s = 355 mm: d = 450 + 226 = 676 mm, rund 0.75·D.

Nach Vorgabe, nicht nachgeschlagen: welche Stäbe als gezogen gelten. Bei
wenigen Stäben hängt ihr Schwerpunkt davon ab, wie der Pfahl zur Querkraft
gedreht ist; der Halbkreis mittelt das.
