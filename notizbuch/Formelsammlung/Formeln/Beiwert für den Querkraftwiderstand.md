---
erzeugt: 1e263e00a816
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.2.1, (36)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.2.1, (36)

$$
k_d^{+} = \frac{1}{1 + \varepsilon_v^{+} \cdot d^{+} \cdot k_g} \quad \left(d^{+}\ \text{in}\ \mathrm{mm}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varepsilon_v^{+}$ | – | ‰ | [[Fliessdehnung]] |
| $d^{+}$ | – | mm | [[Statische Höhe]] |
| $k_g$ | – | – | [[Beiwert der Gesteinskörnung]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
k_d^{+} = \frac{1}{1 + \varepsilon_v^{+} \cdot d^{+} \cdot k_g} = \frac{1}{1 + 2.174\,\text{‰} \cdot 248.1 \cdot 1.2} = 0.6071 \quad \left(d^{+}\ \text{in}\ \mathrm{mm}\right)
$$

## Gebraucht von

- [[Querkraftwiderstand ohne Querkraftbewehrung]]

## Im Code

- [[opencivil.nachweis.querkraft_ohne_buegel#protokoll_ohne_buegel|protokoll_ohne_buegel]]

## Themen

- [[Kennzahlen]]
- [[Querkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Fasst zusammen, wie weit sich der kritische Schubriss öffnet: mit der
[[Nominelle Dehnung der Zugbewehrung|nominellen Dehnung der Zugbewehrung]],
mit der statischen Höhe -- grosse Bauteile haben breitere Risse, der
Massstabseffekt -- und mit der [[Beiwert der Gesteinskörnung|Gesteinskörnung]].
Je grösser das Produkt, desto kleiner $k_d$ und desto weniger Querkraft trägt
der Beton. Wie bei $\tau_{cd}$ ist die Formel empirisch: $d$ geht in mm ein.

Liegt die Zugbewehrung einer Richtung in mehreren Lagen, zählen alle: $d$
reicht bis zu ihrem gemeinsamen Schwerpunkt (SIA 262, 4.3.3.2.2; siehe
[[Statische Höhe]]). Im Beispielprojekt liegen unten ⌀18 auf 249 mm und eine
Zulage ⌀12 3 mm weiter innen; $d$ ist damit 248.1 statt 249 mm.

Bis 2026-11-14 hiess die Seite «Beiwert für die statische Höhe».
