---
erzeugt: 9ac02a225166
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

*In der Herleitung: «Keine Flächenlast im Schnitt abgezogen»*

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
V_{d,red} = V_d = 80\,\mathrm{kN}
$$

## Gebraucht von

- [[Mittleres Moment im Stützstreifen]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._lasten|Durchstanzen._lasten]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was innerhalb des Nachweisschnitts an Flächenlast angreift, geht in die
Stütze, ohne den Schnitt zu kreuzen. Es darf darum von der Auflagerkraft
abgezogen werden (4.3.6.2.6), siehe
[[Flächenlast innerhalb des Nachweisschnitts]]. Ohne Flächenlast ist
$V_{d,red} = V_d$.
