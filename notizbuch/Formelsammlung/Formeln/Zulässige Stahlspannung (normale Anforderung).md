---
erzeugt: 1f47f8f4797d
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.4.2"
---
> [!info] Normstelle
> SIA 262:2025, 4.4.2

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

- [[Zulässige Dehnung]]

## Im Code

- [[opencivil.nachweis.mindestbewehrung#protokoll_zulaessige_stahlspannung|protokoll_zulaessige_stahlspannung]]

## Themen

- [[Stahlspannung aus Rissbreite]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Bei normaler Anforderung an die Rissbreite gilt die Fliessgrenze: der Stahl
darf jede Spannung bis $f_{yk}$ haben, solange er nicht fliesst. Erst eine
erhöhte oder hohe Anforderung begrenzt zusätzlich über den Durchmesser (siehe
[[Zulässige Stahlspannung (Rissbreite w_nom)]]).
