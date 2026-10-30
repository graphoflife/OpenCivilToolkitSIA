---
erzeugt: ca7a453331c4
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.6"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.6

*In der Herleitung: «Eigengewicht und Nutzlast innerhalb des Nachweisschnitts»*

$$
\Delta V_d = q_d \cdot A_q
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $q_d$ | Flächenlast im Nachweisschnitt: Eigengewicht und Nutzlast | kN/m² | Vorgabe |
| $A_q$ | Fläche innerhalb des Nachweisschnitts, ohne Aussparungen | m² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\Delta V_d = q_d \cdot A_q = 14\,\mathrm{kN}/\mathrm{m}^{2} \cdot 0.39\,\mathrm{m}^{2} = 5.5\,\mathrm{kN}
$$

## Gebraucht von

- [[Bemessungswert der Querkraft im Nachweisschnitt]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._lasten|Durchstanzen._lasten]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Flächenlast mal die Fläche innerhalb des Nachweisschnitts, ohne die
Aussparungen darin. Bei einer Decke sind es Eigengewicht und Nutzlast, bei
einer Bodenplatte die Bodenpressung, beide als Bemessungswert. Bei einer
Bodenplatte ist der Abzug oft gross. Abgezogen wird er in
[[Bemessungswert der Querkraft im Nachweisschnitt]].
