---
erzeugt: 282f920fbaf1
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.4.2.3.4, Tabelle 17"
---
> [!info] Normstelle
> SIA 262:2025, 4.4.2.3.4, Tabelle 17

$$
N_{Riss} = \frac{h_{eff}}{2} \cdot b \cdot f_{ct,eff}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h_{eff}$ | – | mm | [[Rissaktive Plattendicke]] |
| $b$ | Betrachtete Breite (x) | mm | Vorgabe |
| $f_{ct,eff}$ | – | N/mm² | [[Wirksame Zugfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{Riss} = \frac{h_{eff}}{2} \cdot b \cdot f_{ct,eff} = \frac{300\,\mathrm{mm}}{2} \cdot 1000\,\mathrm{mm} \cdot 2.52\,\mathrm{N}/\mathrm{mm}^{2} = 378.3\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.mindestbewehrung#Rissnormalkraft|Rissnormalkraft._protokoll_ansatz]]

## Themen

- [[Zwängung auf Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Zugkraft, bei der eine Zwängung den Querschnitt reissen lässt: die
wirksame Zugfestigkeit über die halbe rissaktive Dicke. Jede der beiden
Lagen, oben und unten, übernimmt die Hälfte -- die Kraft ihrer Seite. Diese
Kraft muss die Lage aufnehmen können, siehe [[Aufnehmbare Risskraft]].
