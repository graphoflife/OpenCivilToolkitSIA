---
erzeugt: c13a06d34731
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.4.1, (41)"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.4.1, (41)

*In der Herleitung: «Querkraftwiderstand»*

$$
V_{Rd} = \frac{\tau_y\, A_v}{\gamma_{M1}}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_kennzahlen#KennzahlenStahlQA|KennzahlenStahlQA._schub]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Querkraft eines Profils fliesst fast ganz durch die Bleche, die in
ihrer Richtung stehen: beim I und U in Stegrichtung durch den Steg, quer
dazu durch die Flansche. Ihre Fläche ist die Schubfläche $A_v$; plastisch
fliesst sie gleichmässig mit der Fliessschubspannung $\tau_y$, bei S355
$205\,\mathrm{N/mm^2}$, rund $f_y/\sqrt{3}$.

- I-Profil in Stegrichtung: $A_v$ nach (41a), der Steg über die ganze Höhe
  mit einem Teil der Flansche und Ausrundungen.
- U in Stegrichtung, I und U quer dazu und das Rundrohr: nach Vorgabe,
  nicht nachgeschlagen – so rechnen auch die Excel-Dateien des Benutzers.
- Rechteckrohr: je Wand in der Richtung nach (13), $b$ zwischen den
  Mittellinien der anderen Wände.

Ist ein Steg schlank, beult er, bevor er fliesst: ob er es ist, sagt
[[Steg ohne Schubbeulen]], und dann gilt
[[Schubbeulen des Blechs, ohne Quersteifen]]. Frei gezeichnete Flächen
tragen keine Querkraft.
