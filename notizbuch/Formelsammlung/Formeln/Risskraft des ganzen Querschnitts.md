---
erzeugt: 4d5c9512854b
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.4.2.3.4, Tabelle 17"
---
> [!info] Normstelle
> SIA 262:2025, 4.4.2.3.4, Tabelle 17

$$
N_{Riss} = A_c \cdot f_{ct,eff}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_c$ | Betonfläche C30/37 | mm² | Zwischenwert |
| $f_{ct,eff}$ | – | N/mm² | [[Wirksame Zugfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
N_{Riss} = A_c \cdot f_{ct,eff} = 330000\,\mathrm{mm}^{2} \cdot 2.32\,\mathrm{N}/\mathrm{mm}^{2} = 765.6\,\mathrm{kN}
$$

## Im Code

- [[opencivil.nachweis.qa_gebrauch#RissnormalkraftQA._risskraft|RissnormalkraftQA._risskraft]]

## Themen

- [[Zwängung auf Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Reisst der ganze Querschnitt, gibt der Beton die Kraft ab, die er bis dahin
auf Zug getragen hat: seine Fläche mal seine wirksame Zugfestigkeit. Liegen
mehrere Betone im Querschnitt, zählt jeder mit seiner Fläche und seinem
$f_{ctm}$; ein Polygon, das in einem anderen liegt, ersetzt dieses dort. Die
Bewehrung muss die Kraft übernehmen, jeder Stab bis zu seiner zulässigen
Spannung. Bei der Platte nimmt jede Lage die gezogene Hälfte,
$h_{eff}/2 \cdot b \cdot f_{ct,eff}$ – zusammen derselbe Gedanke. Bei
massigen Bauteilen zählt mit dem Schalter «500 mm» nur die Randzone,
$A_{c,eff}$ (siehe [[Rissaktive Dicke des gezeichneten Querschnitts]]).
