---
erzeugt: e3cdeb7a8e83
art: formel
tags: [formel]
normstelle: "nach Vorgabe, nicht nachgeschlagen"
---
> [!info] Normstelle
> nach Vorgabe, nicht nachgeschlagen

*In der Herleitung: «Schubspannung über b\_i»*

$$
\tau = \frac{v}{b_i}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $v$ | Schubfluss im Schnitt 1, Feld | kN/m | [[Schubfluss im Schnitt]] |
| $b_i$ | Schnitt 1: Länge, auf der er Material von Material trennt | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\tau = \frac{v}{b_i} = \frac{706.8\,\mathrm{kN}/\mathrm{m}}{180\,\mathrm{mm}} = 3.93\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.nachweis.qa_schubfluss#SchubflussQA._fall|SchubflussQA._fall]]

## Themen

- [[Schubfluss]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der [[Schubfluss im Schnitt|Schubfluss]] verteilt auf die Länge $b_i$, auf
der der Schnitt Material von Material trennt: die mittlere Schubspannung in
der Fuge, der Naht oder dem Steg. Wo der Schnitt durch ein Loch oder neben
dem Querschnitt läuft, zählt dieses Stück nicht. Ein Schnitt längs der Fuge
eines Aufbetons von 1000 mm Breite hat $b_i = 1000$ mm; bei $v = 421$ kN/m
ist $\tau = 421/1000 = 0.42$ N/mm².
