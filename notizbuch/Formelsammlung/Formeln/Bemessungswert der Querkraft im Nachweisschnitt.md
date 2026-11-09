---
erzeugt: 4fe024c6a341
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.6"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.6

*In der Herleitung: «Bemessungswert der Querkraft im Nachweisschnitt»*

$$
V_{d,red} = V_d - \Delta V_d
$$

*In der Herleitung: «Bemessungswert der Querkraft im Nachweisschnitt: keine Flächenlast abgezogen»*

$$
V_{d,red} = V_d
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $V_d$ | Bemessungswert der Auflagerkraft | kN | Vorgabe |
| $\Delta V_d$ | – | kN | [[Flächenlast innerhalb des Nachweisschnitts]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{d,red} = V_d - \Delta V_d = 900\,\mathrm{kN} - 5.5\,\mathrm{kN} = 894.5\,\mathrm{kN}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{d,red} = V_d = 1000\,\mathrm{kN}
$$

## Gebraucht von

- [[Halbe Querkraft für das Verformungsvermögen]]
- [[Mittleres Moment im Stützstreifen]]
- [[Querkraft für die Durchstanzbewehrung]]

## Im Code

- [[opencivil.durchstanzen.herleitung#querkraft|querkraft]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was innerhalb des Nachweisschnitts an Flächenlast angreift, geht in die
Stütze, ohne den Schnitt zu kreuzen. Es darf darum von der Auflagerkraft
abgezogen werden (4.3.6.2.6), siehe
[[Flächenlast innerhalb des Nachweisschnitts]]. Ohne Flächenlast ist
$V_{d,red} = V_d$.

Am äusseren Schnitt um die Anker ($V_{d,out}$) und am Schnitt um einen
Stahlpilz ($V_{d,P}$) ebenso, nur über die grössere Fläche innerhalb dieser
Schnitte.
