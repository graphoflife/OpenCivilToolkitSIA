---
erzeugt: f4377380ea13
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.5.2.3.1, (49)"
---
> [!info] Normstelle
> SIA 267:2013, 9.5.2.3.1, (49)

*In der Herleitung: «Erdwiderstand dort, Bemessungswert»*

$$
p_{E,d} = \frac{\eta_{a,tr} \cdot p_{E,k}}{\gamma_{M,a}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_{a,tr}$ | Umrechnungsfaktor des äusseren Widerstands quer | – | Vorgabe |
| $p_{E,k}$ | Erdwiderstand dort, charakteristisch | kN/m | Zwischenwert |
| $\gamma_{M,a}$ | Widerstandsbeiwert quer | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
p_{E,d} = \frac{\eta_{a,tr} \cdot p_{E,k}}{\gamma_{M,a}} = \frac{0.7 \cdot 274\,\mathrm{kN}/\mathrm{m}}{1.4} = 137\,\mathrm{kN}/\mathrm{m}
$$

## Im Code

- [[opencivil.pfahl.quer#AeussererQuerwiderstand._bettung|AeussererQuerwiderstand._bettung]]

## Themen

- [[Äusserer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Bettung der Steifigkeit ist elastisch und kennt keine Grenze, der Boden
schon. Bettung und Widerstand müssen nach der Norm über die Tiefe
zusammenpassen (SIA 267:2013, 9.5.4.5). Das Werkzeug vergleicht darum in
jeder Tiefe der Verläufe die Bettungskraft q_d = |p| · D mit dem
Erdwiderstand, abgemindert wie R_tr: p_E,d = η_a,tr · p_E,k / γ_M,a --
nach Vorgabe, nicht nachgeschlagen. Massgebend ist die Tiefe, in der q_d
dem Erdwiderstand am nächsten kommt; meist liegt sie nahe dem Kopf.

p_E,k = 274 kN/m in 2 m Tiefe: p_E,d = 0.7 · 274 / 1.4 = 137 kN/m. Hält der
Boden die Bettungskraft nicht, gibt er dort nach, und Verschiebung und
Moment sind grösser, als die elastische Rechnung zeigt. Am Terrain hält
Sand ohne Kohäsion nichts; eine Abminderung t_red der Bettung bildet das
ab ([[Abgeminderte Bettung am Terrain]]).
