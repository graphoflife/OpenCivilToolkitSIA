---
erzeugt: 75d399903231
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 3.1.2.3.3, (10)"
---
> [!info] Normstelle
> SIA 262:2025, 3.1.2.3.3, (10)

$$
E_{cm} = k_E \cdot \sqrt[3]{f_{cm}} \quad \left(f_{cm}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_E$ | Beiwert des Elastizitätsmoduls je nach Gestein | – | Vorgabe |
| $f_{cm}$ | Mittelwert der Zylinderdruckfestigkeit | N/mm² | [[Mittelwert der Zylinderdruckfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
E_{cm} = k_E \cdot \sqrt[3]{f_{cm}} = 10000 \cdot \sqrt[3]{38} = 33620\,\mathrm{N}/\mathrm{mm}^{2} \quad \left(f_{cm}\ \text{in}\ \mathrm{N}/\mathrm{mm}^{2}\right)
$$

## Gebraucht von

- [[Beiwert der Parabel]]
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
$k_E$ trägt die Gesteinskörnung. Die Norm gibt ein Band je Gestein:
Alluvialkies 10 000 bis 12 000, gebrochener Kalk 8 000 bis 10 000,
glimmerhaltiges Gestein 6 000 bis 8 000. Das Werkzeug nimmt 10 000. Wie bei $\tau_{cd}$
geht die Festigkeit als blosse Zahl in N/mm² ein.

$E_{cm}$ ist der Modul des ungerissenen Betons unter kurzer Last. Unter Dauerlast
kriecht der Beton und wird weicher -- siehe [[Wirksamer Elastizitätsmodul]].
Für die Tragsicherheit wird er zum [[Bemessungswert des Elastizitätsmoduls]].
