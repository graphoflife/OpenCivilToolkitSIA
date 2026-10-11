---
erzeugt: a1d22e3ec4a7
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\alpha_{eff,x} = \frac{M_{Rd}}{M_{Ed}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{Rd}$ | Querkraftwiderstand x-Richtung – Feld | kNm | [[Widerstand bei festgehaltenem N_Ed]], [[Widerstand in der Richtung der Einwirkung]], Zwischenwert, [[Querkraftwiderstand mit Querkraftbewehrung]], [[Aufnehmbare Risskraft]], [[Aufnehmbares Moment der Bewehrung]], [[Zulässige Stahlspannung (Rissbreite w_nom)]], [[Zulässige Stahlspannung]], [[Querkraftwiderstand ohne Querkraftbewehrung]], [[Zulässige Dehnung]], [[Zulässige Stahlspannung (normale Anforderung)]], [[Widerstand im normierten Diagramm]] |
| $M_{Ed}$ | Einwirkung | kNm | Zwischenwert, [[Bezogene Druckzonenhöhe]], [[Risskraft der gezogenen Querschnittshälfte]], [[Rissmoment des ungerissenen Querschnitts]], [[Einwirkung im normierten Diagramm]], [[Bezogene Druckzonenhöhe bei reiner Biegung]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\alpha_{eff,x,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{235.9\,\mathrm{kNm}}{100\,\mathrm{kNm}} = 2.36 \quad \Rightarrow \quad \text{erfüllt}
$$

## Im Code

- `opencivil.core.berechnung:grad_formel`

## Themen

- [[Biegung und Normalkraft]]
- [[Schiefe Biegung]]
- [[Querkraft und Torsion]]
- [[Querkraft]]
- [[Duktilität]]
- [[Zwängung auf Normalkraft]]
- [[Sprödes Versagen]]
- [[Zwängung auf Biegung]]
- [[Stahlspannung aus Rissbreite]]
- [[Stahlspannung gegen Fliessen]]
- [[Knicken]]
- [[Duktilität je Richtung]]
- [[Sprödes Versagen je Richtung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->
