---
erzeugt: 74e5096dea84
art: formel
tags: [formel]
normstelle: ["SIA 267:2013, 9.5.2.2.1, (42)", "SIA 267:2013, 9.5.2.2.1, (42); 9.5.2.3.1, (49)"]
---
> [!info] Normstellen
> SIA 267:2013, 9.5.2.2.1, (42) · SIA 267:2013, 9.5.2.2.1, (42); 9.5.2.3.1, (49)

*In der Herleitung: «Äusserer Widerstand auf Druck, Bemessungswert»*

$$
R_{a,d} = \frac{\eta_a \cdot R_{a,k}}{\gamma_{M,a}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_a$ | Umrechnungsfaktor des äusseren Widerstands | – | Vorgabe |
| $R_{a,k}$ | Äusserer Widerstand auf Druck | kN | [[Äusserer Widerstand auf Druck]], Vorgabe |
| $\gamma_{M,a}$ | Widerstandsbeiwert auf Druck | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
R_{a,d} = \frac{\eta_a \cdot R_{a,k}}{\gamma_{M,a}} = \frac{0.7 \cdot 4084\,\mathrm{kN}}{1.3} = 2199\,\mathrm{kN}
$$

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand._bemessung|AeussererWiderstand._bemessung]]
- [[opencivil.pfahl.quer#AeussererQuerwiderstand|AeussererQuerwiderstand._querkraft]]

## Themen

- [[Äusserer Pfahlwiderstand]]
- [[Äusserer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Aus dem charakteristischen Widerstand wird der Bemessungswert mit zwei
Faktoren (SIA 267:2013, 9.5.2.2.1, (42)). Der Umrechnungsfaktor η_a sagt, wie
gut R_a,k bekannt ist: höchstens 0.7 aus einer Berechnung, 0.9 aus
vergleichbarer Erfahrung oder aus dynamischen Versuchen, 1.0 aus statischen
Versuchen (9.5.2.2.5, (45) bis (48)). Der Widerstandsbeiwert γ_M,a ist 1.3
auf Druck und 1.6 auf Zug (9.5.2.2.4, (43), (44)).

Aus einer Berechnung bleiben so auf Druck 0.7/1.3 = 54 % von R_a,k, auf Zug
0.7/1.6 = 44 %; aus einem statischen Versuch 77 % und 63 %.

Quer zur Achse gilt dieselbe Formel. Die Norm will R_tr,d für das Objekt
festgelegt, in der Regel mit γ_M,a mindestens 1.4 (9.5.2.3.1, (49)); das
Werkzeug nimmt 1.4. Für η_a gelten quer dieselben Grenzen wie längs
(9.5.2.3.2), und R_tr,k ist immer gerechnet: höchstens 0.7. Mit
R_tr,k = 678 kN wird R_tr,d = 0.7 · 678 kN / 1.4 = 339 kN -- zusammen ein
Faktor 2.
