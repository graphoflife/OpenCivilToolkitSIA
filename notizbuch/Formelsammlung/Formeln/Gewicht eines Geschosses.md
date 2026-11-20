---
erzeugt: db233db53329
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.2.3"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.2.3

*In der Herleitung: «Gewicht und Höhe eines Geschosses»*

$$
W_i = G_{k,i} + \psi_{2,i} \cdot Q_{k,i} \qquad z_i = \sum_{j \le i} h_j
$$

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf._gewichte|Lauf._gewichte]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Was im Beben mitschwingt: das ständige Gewicht des Geschosses und der
quasi-ständige Teil seiner Nutzlast, $\psi_2 \cdot Q_k$ -- dieselbe Summe
nimmt die Norm für die Auslenkung (16.5.2.3) und für die Verteilung (42).
Das Gewicht sitzt auf der Höhe seiner Decke, $z_i$, gezählt ab der Ebene, in
der das Beben angreift: der Einspannung der Wände. Bei steifen
Untergeschossen darf sie auf dem Erdgeschoss liegen (16.5.1.7); dann gehören
die Untergeschosse nicht in die Liste, die Kräfte sind aber bis in den
Baugrund zu verfolgen.

Die Vorgabe $\psi_2 = 0.3$ gilt für Wohn- und Büroflächen (SIA 260:2013,
Anhang A, Tabelle 2). Der Beiwert hängt an der Nutzung: für Lagerflächen ist
er dort 0.8, für Dächer 0.
