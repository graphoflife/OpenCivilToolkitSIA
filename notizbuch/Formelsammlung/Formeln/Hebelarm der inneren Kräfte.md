---
erzeugt: 079b02d1adfa
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4.2"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4.2

$$
z = 0.9 \cdot d
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d$ | Statische Höhe des Pfahls | mm | [[Statische Höhe des Kreisquerschnitts]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
z = 0.9 \cdot d = 0.9 \cdot 676\,\mathrm{mm} = 608.4\,\mathrm{mm}
$$

## Gebraucht von

- [[Stegbreite des Kreisquerschnitts]]
- [[Widerstand der Druckdiagonalen im Pfahl]]
- [[Widerstand der Wendel]]

## Im Code

- [[opencivil.pfahl.innen_quer#InnererQuerwiderstand._fachwerk|InnererQuerwiderstand._fachwerk]]

## Themen

- [[Innerer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Abstand zwischen der Zugkraft in den Stäben und der Druckkraft im Beton:
der Hebel, mit dem das Fachwerk die Querkraft trägt. Ohne genauere Rechnung
0.9·d (SIA 262:2025, 4.3.3.4.2), wie bei der Platte.

⌀ 900 mm: z = 0.9 · 676 = 608 mm.
