---
erzeugt: 5fd1259f3365
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.5.2.2.1, (42)"
---
> [!info] Normstelle
> SIA 267:2013, 9.5.2.2.1, (42)

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

## Themen

- [[Äusserer Pfahlwiderstand]]

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
