---
erzeugt: db97c9bb8e94
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 5.3.2.5"
---
> [!info] Normstelle
> SIA 267:2013, 5.3.2.5

*In der Herleitung: «Verformungsmodul der Tragsicherheit: hier führt zu wenig Steifigkeit zum Versagen»*

$$
E_{s,d} = \frac{E_{s,k}}{\gamma_E} \qquad \gamma_E = 1.5
$$

## Im Code

- [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit._kombinationen|Pfahlsteifigkeit._kombinationen]]

## Themen

- [[Pfahlsteifigkeit]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

In der Tragsicherheit rechnet das Werkzeug mit einem weicheren Boden: wo zu
wenig Steifigkeit zum Versagen führt, wird der Verformungsmodul durch γ_E
geteilt, objektbezogen festgelegt und mindestens 1.5 (SIA 267:2013,
5.3.2.5). Beim quer belasteten Pfahl ist das so: in weicherem Boden weicht
er weiter aus und biegt sich stärker. Das Werkzeug nimmt den kleinsten
Wert, 1.5 -- nach Vorgabe, nicht nachgeschlagen.

⌀ 900 mm aus C30/37 unter H = 100 kN, langer Pfahl: mit E_s,k = 30 MN/m²
höchstens M = 112 kNm, mit E_s,d = 20 MN/m² 124 kNm, gut 10 % mehr.

Die Federn am Kopf gelten dagegen mit E_s,k: sie gehören zur
Gebrauchstauglichkeit (5.3.2.8).
