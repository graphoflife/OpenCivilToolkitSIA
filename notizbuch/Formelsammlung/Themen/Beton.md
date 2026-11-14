---
erzeugt: 463892e7b072
art: thema
tags: [thema]
---
> [!abstract] Baustoffe
> 7 Formeln, in der Folge, in der gerechnet wird.

## Formeln

1. [[Beiwert zur Berücksichtigung der Festigkeitsminderung]]
2. [[Bemessungswert der Betondruckfestigkeit]]
3. [[Bemessungswert der Schubspannungsgrenze]]
4. [[Mittelwert der Zylinderdruckfestigkeit]]
5. [[Mittelwert des Elastizitätsmoduls]]
6. [[Bemessungswert des Elastizitätsmoduls]]
7. [[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Beton tritt im Werkzeug mit wenigen Kennwerten auf, und alle folgen aus der
Festigkeitsklasse: aus der charakteristischen Zylinderdruckfestigkeit $f_{ck}$
und den Teilsicherheitsbeiwerten. Daraus entstehen zwei Familien von Werten.

- **Bemessungswerte** für die Tragsicherheit: $f_{cd}$ für Druck, $\tau_{cd}$
  für Schub, $E_{cd}$ für die Steifigkeit beim Knicken -- gemindert mit
  Beiwerten und geteilt durch Teilsicherheiten. In $f_{cd}$ steckt auch die
  Dauer der Einwirkung, $\eta_t$, im Normalfall 1.0.
- **Mittelwerte** für das Verhalten im Gebrauch: $f_{cm}$ und $E_{cm}$ sagen,
  wie sich der Beton im Mittel verhält, ohne Abzug für die Sicherheit.

Wie der Beton auf Druck antwortet, beschreiben zwei Gesetze: die
[[Parabel-Rechteck-Beziehung des Betons]] und der vereinfachte
[[Spannungsblock des Betons]]. Wie steil die Parabel beginnt, sagt der
[[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]]; der Block kennt ihn
nicht.

Jeder Kennwert ist ein eigener Wert im Rechenwerk. Er lässt sich je Sorte
überschreiben, und jede Formel, die ihn braucht, rechnet mit dem
überschriebenen weiter. Ob ein Kapitel mit Bemessungswerten oder mit
charakteristischen Werten rechnet, wählt es selbst (siehe
[[opencivil.nachweis.rechenwahl]]).
