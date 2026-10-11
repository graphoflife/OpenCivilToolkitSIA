---
erzeugt: 9b1bbe167dca
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Dehnungsebene und innere Kräfte»*

$$
\varepsilon(y, z) = \varepsilon_0 + \kappa \cdot v \qquad v = n_y (y - y_S) + n_z (z - z_S) \qquad N = \int_A \sigma\,\mathrm{d}A \qquad M_y = -\int_A \sigma\,(z - z_S)\,\mathrm{d}A \qquad M_z = -\int_A \sigma\,(y - y_S)\,\mathrm{d}A
$$

*In der Herleitung: «Dehnungsebene und innere Kräfte»*

$$
\varepsilon(z) = \varepsilon_m + \chi \cdot \left(z - \frac{h}{2}\right) \qquad N_{int} = \int_A \sigma\left(\varepsilon\right)\,\mathrm{d}A \qquad M_{int} = \int_A \sigma\left(\varepsilon\right) \cdot \left(z - \frac{h}{2}\right)\,\mathrm{d}A
$$

## Im Code

- [[opencivil.nachweis.querschnittsloeser#protokoll_verfahren|protokoll_verfahren]]
- [[opencivil.nachweis.schiefe_biegung#SchiefeBiegung|SchiefeBiegung._protokoll_ansatz]]

## Themen

- [[Schiefe Biegung]]
- [[Stahlspannung aus Rissbreite]]
- [[Stahlspannung gegen Fliessen]]
- [[Knicken]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Querschnitt bleibt eben (Bernoulli): die Dehnung ist eine lineare
Funktion der Lage. Bei der Platte hängt sie nur von der Tiefe $z$ ab -- zwei
Unbekannte, die Dehnung $\varepsilon_m$ auf halber Höhe und die Krümmung
$\chi$. Beim gezeichneten Querschnitt ist es eine schräge Ebene, mit der
Richtung $n$ der Nulllinie als drittem Parameter.

Aus der Ebene folgen über die Werkstoffgesetze die Spannungen, aus deren
Integral Normalkraft und Moment. Gesucht wird die Ebene, deren innere Kräfte
die Einwirkung treffen. Geschlossen geht das nicht, weil die Gesetze
nichtlinear sind: das Werkzeug sucht in zwei geschachtelten Halbierungen,
innen $\varepsilon_m$ zur Normalkraft, aussen $\chi$ zum Moment. Die Probe
in der Herleitung zeigt, dass die gefundene Ebene die Einwirkung trägt.
