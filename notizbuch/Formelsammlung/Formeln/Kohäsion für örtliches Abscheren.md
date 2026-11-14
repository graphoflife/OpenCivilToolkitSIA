---
erzeugt: afe840b13e9f
art: formel
tags: [formel]
normstelle: "Kap. 9.2.7, 12.5"
---
> [!info] Normstelle
> Kap. 9.2.7, 12.5

$$
c^{*} = \tfrac{2}{3} \cdot c'_{k,3}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $c'_{k,3}$ | Kohäsion der Schicht 3, charakteristisch | kPa | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
c^{*} = \tfrac{2}{3} \cdot c'_{k,3} = \tfrac{2}{3} \cdot 5\,\mathrm{kPa} = 3.3\,\mathrm{kPa}
$$

## Gebraucht von

- [[Spitzendruck drainiert]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._fuss_drainiert]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie beim Reibungswinkel: schert der Boden am Fuss nur örtlich ab, zählen
zwei Drittel der Kohäsion (Kap. 9.2.7, 12.5). Aus c' = 6 kN/m² werden
4 kN/m².
