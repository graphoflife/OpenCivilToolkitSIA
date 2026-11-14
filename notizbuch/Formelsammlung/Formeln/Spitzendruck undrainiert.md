---
erzeugt: a98d9c786ae2
art: formel
tags: [formel]
normstelle: "Kap. 12.5, Bild 12.5"
---
> [!info] Normstelle
> Kap. 12.5, Bild 12.5

*In der Herleitung: «Spitzendruck, undrainiert»*

$$
q_{b,k} = s_{u,k,2} \cdot N_c
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $s_{u,k,2}$ | Undrainierte Scherfestigkeit der Schicht 2, charakteristisch | kPa | Vorgabe |
| $N_c$ | Tragfähigkeitsfaktor, undrainiert | – | [[Tragfähigkeitsfaktor des Pfahlfusses undrainiert]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
q_{b,k} = s_{u,k,2} \cdot N_c = 110\,\mathrm{kPa} \cdot 9 = 990\,\mathrm{kPa}
$$

## Gebraucht von

- [[Spitzenwiderstand]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._fuss_undrainiert]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im undrainierten Ton bricht der Boden am Fuss mit seiner Scherfestigkeit:
q_b = s_u · N_c, mit dem N_c nach Skempton, in dem Form und Tiefe schon
stecken (Kap. 12.5, Bild 12.5). Die Überlagerung am Fuss zählt hier nicht --
sie hebt sich etwa mit dem Gewicht des Pfahls auf, das ebenso wenig unter den
Einwirkungen steht; nach Vorgabe, nicht nachgeschlagen. Bei s_u = 110 kN/m²
und N_c = 9 sind es 990 kN/m².
