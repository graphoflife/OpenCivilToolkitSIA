---
erzeugt: 1f7125c89e71
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Wirksames Widerstandsmoment, Zug unten»*

$$
W_{eff} = \frac{I_{eff}}{z}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $I_{eff}$ | Wirksames Trägheitsmoment | ·10⁶ mm⁴ | Zwischenwert |
| $z$ | Weiteste Faser | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
W_{eff} = \frac{I_{eff}}{z} = \frac{921.2\,\cdot 10^{6}\,\mathrm{mm}^{4}}{300\,\mathrm{mm}} = 3070.7\,\mathrm{cm}^{3}
$$

## Gebraucht von

- [[Biegespannung im Holz]]
- [[Biegewiderstand bis zum ersten Fliessen]]
- [[Biegewiderstand des Brettschichtholzes]]
- [[Biegewiderstand eines Holzquerschnitts]]
- [[Ideelles Kippmoment]]
- [[Saint-Venant-Anteil der Kippspannung]]

## Im Code

- [[opencivil.nachweis.qa_holz_werte#HolzwerteQA|HolzwerteQA._biegung]]
- [[opencivil.nachweis.qa_stahl#StahlBiegungQA._wirksam|StahlBiegungQA._wirksam]]
- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung._biegung|_Herleitung._biegung]]

## Themen

- [[Stahlquerschnitt]]
- [[Knicken und Kippen]]
- [[Holzquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Elastisch wächst die Spannung linear mit dem Abstand von der Nulllinie und
ist an der weitesten Faser $z$ am grössten. Das Widerstandsmoment $W = I/z$
verknüpft das Moment mit dieser grössten Spannung: $\sigma = M/W$.

- Klasse 3: $W_{el}$, mit $I$ und $z$ am ganzen Querschnitt.
- Klasse 4: $W_{eff}$, mit $I_{eff}$ und $z$ am wirksamen Querschnitt. Fallen
  gedrückte Streifen weg, rückt die Nulllinie zur gezogenen Seite; $z$ wird
  auf der gedrückten Seite grösser, $W_{eff}$ kleiner.

Mit mehreren Stählen zählt je Stahl seine weiteste Faser; massgebend ist
die mit dem kleinsten $f_y/z$.

Beim Holz gilt es am Bruttoquerschnitt, je Achse bis zur weiteren der
beiden äussersten Fasern – beim Rechteck $W = b h^2/6$.
