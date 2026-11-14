---
erzeugt: 83f0910584a6
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.2.1.5, Figur 12"
---
> [!info] Normstelle
> SIA 262:2025, 4.2.1.5, Figur 12

$$
N_{Rd}^{-} = -b \cdot h \cdot f_{cd}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b$ | – | mm | Zwischenwert |
| $h$ | – | mm | Zwischenwert |
| $f_{cd}$ | – | N/mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
N_{Rd}^{-} = -b \cdot h \cdot f_{cd} = -1000\,\mathrm{mm} \cdot 300\,\mathrm{mm} \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} = -6000\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.handrechnung#Handrechnung._groesste_druckkraft|Handrechnung._groesste_druckkraft]]

## Themen

- [[Biegung und Normalkraft]]
- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der linke Eckpunkt der Handrechnung: der ganze Querschnitt gedrückt, überall
mit $f_{cd}$. Die Bewehrung zählt hier nicht mit -- die Handrechnung lässt
gedrückten Stahl stets weg und bleibt damit auf der sicheren Seite. Die Linie
aus Dehnungsebenen rechnet den Druckstahl mit und reicht entsprechend weiter.
