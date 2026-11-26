---
erzeugt: 1494c2a56217
art: formel
tags: [formel]
normstelle: "SIA 263:2013, Tabelle 5b"
---
> [!info] Normstelle
> SIA 263:2013, Tabelle 5b

*In der Herleitung: «Beiwert der Grenzschlankheiten, f\_y in N/mm²»*

$$
\varepsilon = \sqrt{\frac{235}{f_y}}
$$

## Im Code

- [[opencivil.nachweis.qa_stahl_kennzahlen#KennzahlenStahlQA|KennzahlenStahlQA._teile]]

## Themen

- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Grenzen für $c/t$ der Tabellen 5a und 5b gelten, wie sie dastehen, für
einen Stahl mit $f_y = 235\,\mathrm{N/mm^2}$. Ein festerer Stahl fliesst
später; bis dahin muss ein gedrücktes Blech länger halten, ohne
auszubeulen. Darum schrumpfen alle Grenzen mit $\varepsilon$: bei S355 ist
$\varepsilon = 0.81$, ein Blech darf also nur gut vier Fünftel so schlank
sein wie bei S235.

Das Werkzeug rechnet $\varepsilon$ je Teil mit der Fliessgrenze seiner
Dicke: über 40 mm ist $f_y$ kleiner und $\varepsilon$ damit grösser.
