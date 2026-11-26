---
erzeugt: 6ab94605df2c
art: formel
tags: [formel]
normstelle: ["SIA 263:2013, 5.3.5, (60); 4.5.3", "SIA 263:2013, 5.2.6, (54); 5.2.2; 5.2.3, (52)"]
---
> [!info] Normstellen
> SIA 263:2013, 5.3.5, (60); 4.5.3 · SIA 263:2013, 5.2.6, (54); 5.2.2; 5.2.3, (52)

*In der Herleitung: «Widerstand, Zug unten»*

$$
M_{y,Rd}^{+} = \frac{f_{y} \cdot W_{eff}}{\gamma_{M1}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{y}$ | Streckgrenze | N/mm² | Vorgabe |
| $W_{eff}$ | Wirksames Widerstandsmoment | cm³ | [[Widerstandsmoment bis zur weitesten Faser]] |
| $\gamma_{M1}$ | Widerstandsbeiwert für Festigkeits- und Stabilitätsnachweise | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
M_{y,Rd}^{+} = \frac{f_{y,\text{S355}} \cdot W_{eff}}{\gamma_{M1,\text{S355}}} = \frac{355\,\mathrm{N}/\mathrm{mm}^{2} \cdot 3070.7\,\mathrm{cm}^{3}}{1.05} = 1038.2\,\mathrm{kNm}
$$

## Gebraucht von

- [[Kippwiderstand]]

## Im Code

- [[opencivil.nachweis.qa_stahl#StahlBiegungQA._wirksam|StahlBiegungQA._wirksam]]
- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung._biegung|_Herleitung._biegung]]

## Themen

- [[Stahlquerschnitt]]
- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

In Klasse 3 beult ein gedrücktes Blech, bevor der ganze Querschnitt
plastisch wird, in Klasse 4 sogar, bevor die erste Faser fliesst. Beide
rechnen darum elastisch: das Moment steigt, bis die weiteste Faser $f_y$
erreicht. Mit dem [[Widerstandsmoment bis zur weitesten Faser]] ist das
$M = f_y \cdot W$.

- **Klasse 3**, (52): $W_{el}$ am ganzen Querschnitt.
- **Klasse 4**, (56) und (60): $W_{eff}$ am wirksamen Querschnitt, ohne die
  Streifen, die beulen – siehe [[Mitwirkende Breite eines Blechs]].

Mit mehreren Stählen fliesst zuerst die Faser mit dem kleinsten $f_y/z$;
sie bestimmt den Widerstand.
