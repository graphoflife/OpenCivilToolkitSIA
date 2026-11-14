---
erzeugt: 763f1bd2fef2
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 2.4.2.3, (2)"
---
> [!info] Normstelle
> SIA 262:2025, 2.4.2.3, (2)

$$
f_{cd} = \frac{\eta_{fc} \cdot \eta_t \cdot f_{ck}}{\gamma_c}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_{fc}$ | Beiwert zur Berücksichtigung der Festigkeitsminderung | – | [[Beiwert zur Berücksichtigung der Festigkeitsminderung]] |
| $\eta_t$ | Beiwert für die Dauer der Einwirkung | – | Vorgabe |
| $f_{ck}$ | Charakteristische Zylinderdruckfestigkeit | N/mm² | Vorgabe |
| $\gamma_c$ | Teilsicherheitsbeiwert für Beton | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
f_{cd} = \frac{\eta_{fc} \cdot \eta_t \cdot f_{ck}}{\gamma_c} = \frac{1 \cdot 1 \cdot 30\,\mathrm{N}/\mathrm{mm}^{2}}{1.5} = 20\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Beiwert der Parabel]]
- [[Druckzonenhöhe aus dem Kräftegleichgewicht]]
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
[[Beiwert zur Berücksichtigung der Festigkeitsminderung]] und mit $\eta_t$
für die Dauer der Einwirkung gemindert und durch den Teilsicherheitsbeiwert
$\gamma_c$ geteilt. Der deckt ab, was die Prüfung
nicht erfasst: die Festigkeit im Bauwerk gegenüber der im Prüfkörper,
Abweichungen der Abmessungen, die Ungenauigkeit des Modells.

$\eta_t = 1.0$ ist der Normalfall: $f_{ck}$ ist an Proben von höchstens 28
Tagen bestimmt, und in den ersten drei Monaten wirken nicht mehr als 85 %
der Bemessungslast. Sonst gilt 0.85, bei Anprall oder Explosion 1.2. Eine
Normsorte rechnet mit 1.0; wer davon abweicht, legt ein eigenes Material
an. Mit $\eta_t = 0.85$ hat C30/37 $f_{cd} = 17.0$ statt
$20.0\,\mathrm{N/mm^2}$.

Tabelle 8 der Norm nennt die Werte gerundet, etwa 10.5 statt 10.67 N/mm²
für C16/20. Das Werkzeug rechnet mit der Formel.

$f_{cd}$ ist die Spannung im [[Spannungsblock des Betons]] und das Plateau der
[[Parabel-Rechteck-Beziehung des Betons]]. Rechnet ein Kapitel mit
charakteristischen Werten, steht an seiner Stelle $f_{ck}$.
