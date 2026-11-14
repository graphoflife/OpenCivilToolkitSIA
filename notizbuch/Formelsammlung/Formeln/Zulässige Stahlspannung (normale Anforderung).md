---
erzeugt: 727c74049575
art: formel
tags: [formel]
normstelle: "SIA 262:2025, Tabelle 17"
---
> [!info] Normstelle
> SIA 262:2025, Tabelle 17

$$
\sigma_{s,adm} = f_{yk}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yk}$ | Charakteristische Fliessgrenze | N/mm² | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{s,adm} = f_{yk} = 500\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Aufnehmbare Risskraft]]
- [[Zulässige Dehnung]]

## Im Code

- [[opencivil.nachweis.mindestbewehrung#protokoll_zulaessige_stahlspannung|protokoll_zulaessige_stahlspannung]]

## Themen

- [[Stahlspannung aus Rissbreite]]
- [[Zwängung auf Normalkraft]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Bei normaler Anforderung an die Rissbreite gilt die Fliessgrenze: der Stahl
darf jede Spannung bis $f_{yk}$ haben, solange er nicht fliesst. Erst eine
erhöhte oder hohe Anforderung begrenzt zusätzlich über den Durchmesser (siehe
[[Zulässige Stahlspannung (Rissbreite w_nom)]]).
