---
erzeugt: 1407baf7c98b
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.5.2, (66)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.5.2, (66)

$$
V_{d,s} = V_{d,red} - V_{Rd,c}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $V_{d,red}$ | – | kN | [[Bemessungswert der Querkraft im Nachweisschnitt]] |
| $V_{Rd,c}$ | Durchstanzwiderstand ohne Durchstanzbewehrung | kN | [[Durchstanzwiderstand ohne Durchstanzbewehrung]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{d,s} = V_{d,red} - V_{Rd,c} = 894.6\,\mathrm{kN} - 366\,\mathrm{kN} = 528.6\,\mathrm{kN}
$$

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#_leisten_schreiben|_leisten_schreiben]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Durchstanzbewehrung darf auf das bemessen werden, was der Beton nicht
trägt: die Querkraft im Nachweisschnitt weniger den
[[Durchstanzwiderstand ohne Durchstanzbewehrung]] (4.3.6.5.2, Gleichung (66)).
Gehalten wird sie gegen den [[Beitrag der Durchstanzbewehrung]].
