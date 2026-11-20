---
erzeugt: 08aab168984e
art: formel
tags: [formel]
normstelle: "SIA 261:2020, 16.5.2.4"
---
> [!info] Normstelle
> SIA 261:2020, 16.5.2.4

$$
\sum W = \sum_i W_i
$$

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\sum W = \sum_i W_i = 10220\,\mathrm{kN}
$$

## Gebraucht von

- [[Ersatzkraft]]

## Im Code

- [[opencivil.erdbeben.ersatzkraft#Lauf|Lauf.__init__]]

## Themen

- [[Erdbeben]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Alle Geschosse über der Einspannung zusammen. Mit dieser Summe rechnet die
[[Ersatzkraft]] (41). Ob das Gewicht nach oben gleich bleibt oder abnimmt,
wie es ein regelmässiger Aufriss verlangt (16.5.1.4), prüft die Rechnung an
den $W_i$ selbst: ist ein Geschoss schwerer als das darunter, gilt das
Verfahren nicht, und die Meldung nennt das Geschoss.
