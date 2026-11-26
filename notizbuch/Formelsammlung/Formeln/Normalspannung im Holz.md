---
erzeugt: 9cd098ece81c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Zugspannung»*

$$
\sigma_{t,0,d} = \frac{|N_{Ed}|}{A}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\vert N_{Ed}\vert $ | – | kN | Zwischenwert |
| $A$ | Fläche des Bruttoquerschnitts | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_{t,0,d} = \frac{|N_{Ed}|}{A} = \frac{100\,\mathrm{kN}}{64000\,\mathrm{mm}^{2}} = 1.56\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.nachweis.qa_holz#HolzBiegungQA._normalspannung|HolzBiegungQA._normalspannung]]
- [[opencivil.nachweis.qa_holz_stabilitaet#_Herleitung|_Herleitung.__init__]]

## Themen

- [[Holzquerschnitt]]
- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Gleichmässig über den Bruttoquerschnitt: $\sigma = N/A$. Löcher von
Verbindungen zieht das Werkzeug nicht ab.
