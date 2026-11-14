---
erzeugt: ce6f7bc4a092
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

- [[opencivil.nachweis.spannungsgrenzen#gegen_fliessen|gegen_fliessen]]

## Themen

- [[Stahlspannung gegen Fliessen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Unter häufiger Einwirkung soll die Bewehrung mit Abstand unter dem Fliessen
bleiben: die Grenze liegt 80 N/mm² unter dem Bemessungswert der
Fliessgrenze $f_{yd}$, so nennt es SIA 262, Tabelle 17 ausdrücklich. Für
B500B gibt das 435 − 80 = 355 N/mm². Die Spannung selbst rechnet das
Kapitel mit seinen eigenen Werten; mit $f_{yd}$ statt $f_{yk}$ liegt die
Grenze auf der strengeren Seite.
