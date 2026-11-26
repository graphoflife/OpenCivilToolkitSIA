---
erzeugt: 9e8dcbdc7a8c
art: formel
tags: [formel]
normstelle: "SIA 263:2013, Anhang B.5, (93); Figur 40"
---
> [!info] Normstelle
> SIA 263:2013, Anhang B.5, (93); Figur 40

*In der Herleitung: «Trägheitsradius des Druckgurts»*

$$
i_{g} = \sqrt{\frac{I_{g}}{A_{g}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $I_{g}$ | Trägheitsmoment des Druckgurts, quer zum Flansch | ·10⁶ mm⁴ | Zwischenwert |
| $A_{g}$ | Fläche des Druckgurts | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
i_{g} = \sqrt{\frac{I_{g}}{A_{g}}} = \sqrt{\frac{16.9\,\cdot 10^{6}\,\mathrm{mm}^{4}}{5304\,\mathrm{mm}^{2}}} = 56.4\,\mathrm{mm}
$$

## Gebraucht von

- [[Schlankheit eines Holzstabs]]
- [[Wölbanteil der Kippspannung]]

## Im Code

- [[opencivil.nachweis.qa_holz_stabilitaet#_Herleitung|_Herleitung._knicken]]
- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung._druckgurt|_Herleitung._druckgurt]]

## Themen

- [[Knicken und Kippen]]
- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

$i = \sqrt{I/A}$: wie weit die Fläche im Mittel von der Achse liegt. Je
kleiner, desto leichter weicht ein gedrückter Teil seitlich aus. Beim
Rechteck ist es $h/\sqrt{12}$.

**Beim Holz** der Trägheitsradius des ganzen Querschnitts, je Achse: aus
ihm und der Knicklänge die [[Schlankheit eines Holzstabs]].

**Beim Kippen des Stahls** der des Druckgurts: der gedrückte Flansch mit
einem Drittel des gedrückten Stegs (Figur 40). Er weicht seitlich aus,
quer zur Ebene des Trägers; sein Trägheitsradius um die Achse im Steg
sagt, wie leicht. Fast alles davon kommt aus dem Flansch: der Steg ist
dünn und liegt auf der Achse. Das Werkzeug nimmt als gedrückten Steg die
Hälfte der Höhe zwischen den Flanschen – die Biegung allein – und rechnet
ohne Ausrundungen. Beim Rechteckrohr gehören beide Stege dazu.
