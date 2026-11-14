---
erzeugt: 6bcdca1c472c
art: formel
tags: [formel]
normstelle: "Kap. 12.8, Bild 12.9"
---
> [!info] Normstelle
> Kap. 12.8, Bild 12.9

*In der Herleitung: «Feder am Fuss, in Schicht 3: A\_b · R / D mit R E\_s,k»*

$$
K_b = \frac{\pi \cdot D \cdot 4.5 \cdot E_{s,k,3}}{4}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $D$ | Durchmesser des Pfahls | mm | Vorgabe |
| $E_{s,k,3}$ | Verformungsmodul der Schicht 3, charakteristisch | MN/m² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
K_b = \frac{\pi \cdot D \cdot 4.5 \cdot E_{s,k,3}}{4} = \frac{\pi \cdot 900\,\mathrm{mm} \cdot 4.5 \cdot 120\,\mathrm{MN}/\mathrm{m}^{2}}{4} = 381.7\,\mathrm{MN}/\mathrm{m}
$$

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit._bettung|Pfahlsteifigkeit._bettung]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wie stark der Boden unter dem Fuss gegen eine Setzung hält: der Druck je
Setzung R mal der Fläche des Fusses, durch den Durchmesser. Für Bohrpfähle
gibt Cassan R ≈ 4.5 · E_s (Kap. 12.8, Bild 12.9). Massgebend ist die
Schicht, auf der der Fuss steht -- an einer Grenze die untere.

Der Fuss drückt nur: auf Zug hebt er ab und hat keine Feder. Wo er nicht
trägt, weil die Spitze ausgeschaltet ist, fehlt die Feder ganz. Kommt R_a,k
aus einem Versuch, zählt der Fuss immer mit -- nach Vorgabe, nicht
nachgeschlagen. ⌀ 900 mm auf E_s,k = 30 MN/m²: π · 0.9 · 4.5 · 30 / 4
≈ 95 MN/m.
