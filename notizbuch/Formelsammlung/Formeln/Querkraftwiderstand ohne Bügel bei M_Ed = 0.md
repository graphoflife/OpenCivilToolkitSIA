---
erzeugt: 70857ae36774
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.2.1, (35), (36)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.2.1, (35), (36)

*In der Herleitung: «Zug unten, M\_Ed = 0: ε\_v = 0, k\_d = 1»*

$$
V_{Rd}^{+}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{+}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\tau_{cd}$ | – | N/mm² | Zwischenwert |
| $d_v^{+}$ | – | mm | [[Wirksame Höhe ohne Abzug]], [[Wirksame Höhe, um die Einlage vermindert]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
V_{Rd}^{+}(M_{Ed} = 0) = \tau_{cd} \cdot d_v^{+} = 1.0954\,\mathrm{N}/\mathrm{mm}^{2} \cdot 248.1\,\mathrm{mm} = 271.8\,\mathrm{kN}/\mathrm{m}
$$

## Gebraucht von

- [[Kleinerer Widerstand beider Seiten]]

## Im Code

- [[opencivil.nachweis.kennzahlen#Plattenkennzahlen|Plattenkennzahlen._ohne_buegel]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ohne Moment und ohne Normalkraft ist die
[[Nominelle Dehnung der Zugbewehrung|nominelle Dehnung der Zugbewehrung]]
null und der [[Beiwert für den Querkraftwiderstand]] $k_d = 1$. Der
Widerstand ist dann $\tau_{cd} \cdot d_v$ -- der grösste, den die Platte ohne
Bügel hat. Mit wachsendem Moment öffnet sich der Schubriss, und der
Widerstand sinkt.

Je Seite gilt ihre eigene statische Höhe; die Kennzahl $V_{Rd,max}$ nimmt
das Kleinere beider Seiten.
