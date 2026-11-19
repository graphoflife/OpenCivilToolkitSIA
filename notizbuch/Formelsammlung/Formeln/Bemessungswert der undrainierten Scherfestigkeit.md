---
erzeugt: fb3761368f7e
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 5.3.2.1, (5)"
---
> [!info] Normstelle
> SIA 267:2013, 5.3.2.1, (5)

*In der Herleitung: «Undrainierte Scherfestigkeit, Bemessungswert»*

$$
s_{u,d} = \frac{s_{u,k}}{\gamma_{cu}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $s_{u,k}$ | Undrainierte Scherfestigkeit, charakteristisch | kPa | Vorgabe |
| $\gamma_{cu}$ | Partialfaktor der undrainierten Scherfestigkeit | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
s_{u,d} = \frac{s_{u,k}}{\gamma_{cu}} = \frac{40\,\mathrm{kPa}}{1.5} = 26.7\,\mathrm{kPa}
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]
- [[Gleitwiderstand]]
- [[Lastneigungsfaktor i_c]]

## Im Code

- [[opencivil.geotechnik.grundbruch|_s_u_d]]

## Themen

- [[Fundament]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Undrainiert trägt ein Boden, der schneller belastet wird, als sein
Porenwasser abfliessen kann – typisch ein gesättigter Ton kurz nach dem
Bau. Gerechnet wird dann mit totalen Spannungen: die Scherfestigkeit hängt
nicht von der Normalspannung ab, und an die Stelle von Reibungswinkel und
Kohäsion tritt allein $s_u$ (die Norm schreibt $c_u$). Welcher Fall gilt,
wählt der Schalter «drainiert» oder «undrainiert»; feinkörniger Boden braucht
beide, je in einem eigenen Grundbruch (SIA 267:2013, 8.5.1.5, 8.5.1.6).

Der Bemessungswert ist der charakteristische, geteilt durch den
Partialfaktor (5.3.2.1, (5)): für $s_u$ ist es $\gamma_{cu} = 1.5$
(Tabelle 1), so viel wie $\gamma_c$ für die drainierte Kohäsion. Stammt
$s_{u,k}$ aus der Rückrechnung eines Bruchs, oder wird nach der
Beobachtungsmethode gebaut, darf der Faktor kleiner sein, nicht unter 1.3
(5.3.2.3).
