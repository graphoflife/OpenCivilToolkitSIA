---
erzeugt: 97662cee799e
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Raumlast des Grundwassers, «Wasser»»*

$$
\gamma_w = \gamma_{fl}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\gamma_{fl}$ | Raumlast der Flüssigkeit | kN/m³ | [[Raumlast der Flüssigkeit]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\gamma_w = \gamma_{fl} = 10\,\mathrm{kN}/\mathrm{m}^{3}
$$

## Gebraucht von

- [[Raumlast unter Auftrieb]]

## Im Code

- [[opencivil.geotechnik.wasser|_raumlast]]

## Themen

- [[Fundament]]
- [[Pfahl]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Unter dem Grundwasserspiegel zählt das Gewicht des Wassers: Der Boden wiegt
dort nur noch $\gamma' = \gamma - \gamma_w$ ([[Raumlast unter Auftrieb]]),
und am Pfahl drückt das Porenwasser mit $u = \gamma_w \cdot (z - t_w)$.
$\gamma_w$ ist keine Zahl am Bauteil, sondern die Raumlast der Flüssigkeit,
die es als Wasser wählt ([[Raumlast der Flüssigkeit]]). Die Zeile setzt beide
gleich und nennt die Flüssigkeit beim Namen; wer ihre Dichte ändert oder
$\gamma_{fl}$ überschreibt, rechnet auch hier mit seiner Zahl.

Ist ein Boden nicht schwerer als das Wasser, wäre $\gamma'$ null oder
negativ, und er hätte unter dem Spiegel weder Reibung noch Gewicht. Dann
rechnet das Bauteil nicht und sagt es am Ort. Undrainiert braucht der
Grundbruch kein Wasser: dort gelten totale Spannungen.
