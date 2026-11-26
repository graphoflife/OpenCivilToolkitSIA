---
erzeugt: 646c632ed1df
art: formel
tags: [formel]
normstelle: "SIA 263:2013, Anhang B.5, (93); Figur 40"
---
> [!info] Normstelle
> SIA 263:2013, Anhang B.5, (93); Figur 40

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

- [[Wölbanteil der Kippspannung]]

## Im Code

- [[opencivil.nachweis.qa_stahl_stabilitaet#_Herleitung._druckgurt|_Herleitung._druckgurt]]

## Themen

- [[Knicken und Kippen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Druckgurt eines I ist der gedrückte Flansch mit einem Drittel des
gedrückten Stegs (Figur 40). Er weicht seitlich aus, quer zur Ebene des
Trägers; sein Trägheitsradius um die Achse im Steg sagt, wie leicht.
Fast alles davon kommt aus dem Flansch: der Steg ist dünn und liegt auf
der Achse.

Das Werkzeug nimmt als gedrückten Steg die Hälfte der Höhe zwischen den
Flanschen – die Biegung allein – und rechnet ohne Ausrundungen. Beim
Rechteckrohr gehören beide Stege dazu.
