---
erzeugt: 2a081607f603
art: formel
tags: [formel]
normstelle: "SIA 264:2014, 5.3.4.3; 5.3.4.4; 5.3.4.6; Figur 7"
---
> [!info] Normstelle
> SIA 264:2014, 5.3.4.3; 5.3.4.4; 5.3.4.6; Figur 7

*In der Herleitung: «Beiwert der Interaktion um y, höchstens 1»*

$$
\mu_{d,y} = \min\left(1;\ \frac{M_{pl,N,y,Rd}}{M_{pl,y,Rd}}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M_{pl,N,y,Rd}$ | Plastischer Biegewiderstand bei N\_Ed | kNm | Zwischenwert |
| $M_{pl,y,Rd}$ | Plastischer Biegewiderstand | kNm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\mu_{d,y} = \min\left(1;\ \frac{M_{pl,N,y,Rd}}{M_{pl,y,Rd}}\right) = \min\left(1;\ \frac{592.4\,\mathrm{kNm}}{863.9\,\mathrm{kNm}}\right) = 0.686
$$

## Gebraucht von

- [[Widerstand einer Verbundstütze nach (25)]]
- [[Zweiachsige Biegung einer Verbundstütze]]

## Im Code

- [[opencivil.nachweis.qa_verbund_stuetze#_Fall._interaktion|_Fall._interaktion]]

## Themen

- [[Verbundstütze]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Druckkraft ändert den plastischen Biegewiderstand: mit wenig Druck
steigt er beim Verbundquerschnitt sogar, mit viel sinkt er. μ_d ist der
Widerstand bei N_Ed durch den ohne Normalkraft, beide mit rechteckigen
Spannungsblöcken wie in Figur 7 – im gefüllten Rohr der Beton mit 1.0
(5.3.4.4). Mehr als 1 zählt nur, wo das Moment aus der Normalkraft selbst
entsteht, etwa weil sie ausmittig angreift (5.3.4.6). Woher das Moment
kommt, weiss das Werkzeug nicht; es nimmt höchstens 1, nach Vorgabe, im
[[TODO]].
