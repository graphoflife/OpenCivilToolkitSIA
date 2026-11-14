---
erzeugt: 56646d7048c1
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.2.6"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.2.6

$$
m_{Dd} = -\frac{N_{Ed} \cdot h}{6}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{Ed}$ | – | kN | Zwischenwert |
| $h$ | Plattendicke | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
m_{Dd} = -\frac{N_{Ed} \cdot h}{6} = -\frac{0\,\mathrm{kN} \cdot 200\,\mathrm{mm}}{6} = 0\,\mathrm{kNm}
$$

## Gebraucht von

- [[Nominelle Dehnung der Zugbewehrung]]

## Im Code

- [[opencivil.nachweis.querkraft_ohne_buegel#QuerkraftOhneBuegel._protokoll_fall|QuerkraftOhneBuegel._protokoll_fall]]

## Themen

- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eine Normalkraft $N_{Ed}$ in der halben Höhe erzeugt am Rand die Spannung
$N/A$, ein Moment $m$ dazu $m/W$ -- im Streifen mit $A = b\,h$ und
$W = b\,h^2/6$. Spannungsfrei ist der gezogene Rand bei
$m = -N_{Ed} \cdot h/6$, Zug positiv gezählt:

- Druck macht $m_{Dd}$ positiv: bis dahin reisst nichts, und die Bewehrung
  bekommt keine Dehnung.
- Zug macht $m_{Dd}$ negativ: der Querschnitt ist schon ohne Moment
  gerissen, und die Bewehrung ist gedehnt.

Beispiel mit $h = 300\,\mathrm{mm}$: $N_{Ed} = -200\,\mathrm{kN}$ (Druck)
gibt $m_{Dd} = +10\,\mathrm{kNm}$, $N_{Ed} = +200\,\mathrm{kN}$ (Zug)
$m_{Dd} = -10\,\mathrm{kNm}$.

Mit einer Normalkraft misst die Norm das Moment in der
[[Nominelle Dehnung der Zugbewehrung|nominellen Dehnung]] ab $m_{Dd}$, und
auch eine Zugkraft geht in $m_{Rd}$ und $m_{Dd}$ ein (SIA 262, 4.3.3.2.6).
Die Formel $-N_{Ed}\,h/6$ selbst ist Mechanik des Rechtecks, kein Normtext.
