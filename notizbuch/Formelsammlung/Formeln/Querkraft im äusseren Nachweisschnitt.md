---
erzeugt: 3f07cd5258db
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.6"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.6

*In der Herleitung: «Querkraft im äusseren Nachweisschnitt»*

$$
V_{d,out} = V_d - q_d \cdot A_{out}
$$

*In der Herleitung: «Querkraft im äusseren Nachweisschnitt: keine Flächenlast»*

$$
V_{d,out} = V_d
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $V_d$ | Bemessungswert der Auflagerkraft | kN | Vorgabe |
| $q_d$ | Flächenlast im Nachweisschnitt: Eigengewicht und Nutzlast | kN/m² | Vorgabe |
| $A_{out}$ | Fläche innerhalb des Schnitts, ohne Aussparungen | m² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{d,out} = V_d - q_d \cdot A_{out} = 900\,\mathrm{kN} - 14\,\mathrm{kN}/\mathrm{m}^{2} \cdot 3.392\,\mathrm{m}^{2} = 852.5\,\mathrm{kN}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{d,out} = V_d = 1000\,\mathrm{kN}
$$

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#_querkraft|_querkraft]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Auflagerkraft weniger die Flächenlast innerhalb des äusseren Schnitts,
ohne Aussparungen -- wie beim inneren
([[Bemessungswert der Querkraft im Nachweisschnitt]]), nur über eine grössere
Fläche (4.3.6.2.6).
