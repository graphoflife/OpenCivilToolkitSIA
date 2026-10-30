---
erzeugt: 0d4251c53f46
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 2.4.2.3"
---
> [!info] Normstelle
> SIA 262:2025, 2.4.2.3

$$
f_{cd} = \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_{fc}$ | Beiwert zur Berücksichtigung der Festigkeitsminderung | – | [[Beiwert zur Berücksichtigung der Festigkeitsminderung]] |
| $f_{ck}$ | Charakteristische Zylinderdruckfestigkeit | N/mm² | Vorgabe |
| $\gamma_c$ | Teilsicherheitsbeiwert für Beton | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
f_{cd} = \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c} = \frac{1 \cdot 30\,\mathrm{N}/\mathrm{mm}^{2}}{1.5} = 20\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Beiwert der Parabel]]
- [[Druckzonenhöhe bei reiner Biegung]]
- [[Druckzonenhöhe im Stützstreifen]]
- [[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]]
- [[Widerstand der Druckdiagonalen]]

## Im Code

- [[opencivil.material.beton]]

## Themen

- [[Beton]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Festigkeit, mit der die Tragsicherheit rechnet. Die charakteristische
Festigkeit $f_{ck}$ ist ein 5-%-Fraktil aus Zylinderprüfungen; sie wird mit dem
[[Beiwert zur Berücksichtigung der Festigkeitsminderung]] gemindert und durch
den Teilsicherheitsbeiwert $\gamma_c$ geteilt. Der deckt ab, was die Prüfung
nicht erfasst: die Festigkeit im Bauwerk gegenüber der im Prüfkörper,
Abweichungen der Abmessungen, die Ungenauigkeit des Modells.

$f_{cd}$ ist die Spannung im [[Spannungsblock des Betons]] und das Plateau der
[[Parabel-Rechteck-Beziehung des Betons]]. Rechnet ein Kapitel mit
charakteristischen Werten, steht an seiner Stelle $f_{ck}$.
