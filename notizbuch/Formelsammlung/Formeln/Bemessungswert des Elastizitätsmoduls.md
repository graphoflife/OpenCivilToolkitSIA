---
erzeugt: 520d0510b591
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.2.1.15, (33)"
---
> [!info] Normstelle
> SIA 262:2025, 4.2.1.15, (33)

$$
E_{cd} = \frac{E_{cm}}{\gamma_{cE}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $\gamma_{cE}$ | Teilsicherheitsbeiwert für den Elastizitätsmodul, Druckglieder mit Einflüssen 2. Ordnung | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
E_{cd} = \frac{E_{cm}}{\gamma_{cE}} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{1.2} = 28016\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]]

## Im Code

- [[opencivil.material.beton]]

## Themen

- [[Beton]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wo die Steifigkeit des Betons in die Tragsicherheit eingeht, wäre ein zu hoher
Modul unsicher: eine zu steife Druckzone unterschätzte die Verformung, beim
Knicken die Ausmitte zweiter Ordnung. Darum wird der Mittelwert durch den
Teilsicherheitsbeiwert $\gamma_{cE}$ geteilt.

$E_{cd}$ bestimmt den [[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]] und
damit, wie steil die Parabel des Betons beginnt.
