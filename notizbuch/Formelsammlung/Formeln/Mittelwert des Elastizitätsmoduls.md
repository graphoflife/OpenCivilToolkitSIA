---
erzeugt: 481809791069
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 3.1.2.3.3"
---
> [!info] Normstelle
> SIA 262:2025, 3.1.2.3.3

$$
E_{cm} = k_e \cdot \sqrt[3]{f_{cm}} \quad \left(f_{cm}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_e$ | Beiwert für die Gesteinskörnung | – | Vorgabe |
| $f_{cm}$ | Mittelwert der Zylinderdruckfestigkeit | N/mm² | [[Mittelwert der Zylinderdruckfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
E_{cm} = k_e \cdot \sqrt[3]{f_{cm}} = 10000 \cdot \sqrt[3]{38} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \quad \left(f_{cm}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

## Gebraucht von

- [[Bemessungswert des Elastizitätsmoduls]]
- [[Biegesteifigkeit]]
- [[Dehnsteifigkeit]]
- [[Wertigkeit im gerissenen Zustand]]
- [[Wirksamer Elastizitätsmodul]]

## Im Code

- [[opencivil.material.beton#_e_cm|_e_cm]]

## Themen

- [[Beton]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Elastizitätsmodul des Betons hängt an der Festigkeit und an der
Gesteinskörnung: steifere Körner geben einen steiferen Beton. Die Formel nimmt
ihn proportional zur dritten Wurzel der mittleren Festigkeit an; der Beiwert
$k_e$ trägt die Gesteinskörnung, im Beispielprojekt 10 000. Wie bei $\tau_{cd}$
geht die Festigkeit als blosse Zahl in N/mm² ein.

$E_{cm}$ ist der Modul des ungerissenen Betons unter kurzer Last. Unter Dauerlast
kriecht der Beton und wird weicher -- siehe [[Wirksamer Elastizitätsmodul]].
Für die Tragsicherheit wird er zum [[Bemessungswert des Elastizitätsmoduls]].
