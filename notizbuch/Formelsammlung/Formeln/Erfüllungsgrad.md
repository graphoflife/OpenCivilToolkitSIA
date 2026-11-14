---
erzeugt: f21f4c440d1b
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
| $M_{Rd}$ | Biegewiderstand dort | kNm | [[Widerstand bei festgehaltenem N_Ed]], [[Widerstand in der Richtung der Einwirkung]], Zwischenwert |
| $M_{Ed}$ | – | kNm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\alpha_{eff,x,\text{Feld}} = \frac{M_{Rd}}{M_{Ed}} = \frac{235.9\,\mathrm{kNm}}{100\,\mathrm{kNm}} = 2.36 \quad \Rightarrow \quad \text{erfüllt}
$$

## Im Code

- [[opencivil.core.nachweis#Vergleich.zeile|Vergleich.zeile]]

## Themen

- [[Biegung und Normalkraft]]
- [[Verformung]]
- [[Schiefe Biegung]]
- [[Querkraft und Torsion]]
- [[Grundbruch]]
- [[Gleiten]]
- [[Setzung]]
- [[Äusserer Pfahlwiderstand]]
- [[Innerer Pfahlwiderstand]]
- [[Äusserer Pfahlwiderstand quer]]
- [[Innerer Pfahlwiderstand quer]]
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
- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Widerstand durch Einwirkung: 1 heisst gerade erfüllt, mehr heisst Reserve,
weniger nicht erfüllt. Beim M-N-Nachweis kommt es darauf an, in welcher
Richtung man misst:

- bei festgehaltener Normalkraft waagrecht bis zur Linie --
  $\alpha = M_{Rd}/M_{Ed}$;
- bei festgehaltenem Moment senkrecht -- $\alpha = N_{Rd}/N_{Ed}$;
- als kürzester Abstand im normierten Diagramm (siehe
  [[Widerstand im normierten Diagramm]]).

«Automatisch» rechnet beide ersten Wege und nimmt den kleineren Grad. Wird
ein Fall vom Moment beherrscht, fällt der Grad bei festgehaltenem Moment
gross aus: dort ist in Richtung der Normalkraft viel Platz. Das ist kein
Fehler, sondern die Natur dieses Massstabs.
