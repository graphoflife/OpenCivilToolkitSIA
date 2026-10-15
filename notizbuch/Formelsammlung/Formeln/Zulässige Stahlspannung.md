---
erzeugt: 8c9b79f2a3c8
art: formel
tags: [formel]
normstelle: "SIA 262:2025, Tabelle 17"
---
> [!info] Normstelle
> SIA 262:2025, Tabelle 17

$$
\sigma_{s,adm} = f_{yd} - 80\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{s,adm} = f_{yd} - 80\,\mathrm{N}/\mathrm{mm}^{2} = 435\,\mathrm{N}/\mathrm{mm}^{2} - 80\,\mathrm{N}/\mathrm{mm}^{2} = 355\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.nachweis.spannungsbegrenzung#GrenzeGegenFliessen.bestimmen|GrenzeGegenFliessen.bestimmen]]
- [[opencivil.nachweis.stabgrenzen#protokoll_fliessgrenzen|protokoll_fliessgrenzen]]

## Themen

- [[Stahlspannung gegen Fliessen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Unter häufiger Einwirkung soll die Bewehrung mit Abstand unter dem Fliessen
bleiben: die Grenze liegt 80 N/mm² unter der Fliessgrenze. Gerechnet wird
mit dem Bemessungswert $f_{yd}$ und nicht mit $f_{yk}$ -- die strengere der
beiden möglichen Lesarten; welche gemeint ist, sagt die Normstelle nicht
eindeutig. Für B500B gibt das rund 355 N/mm².
