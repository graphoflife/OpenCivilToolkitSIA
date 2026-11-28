---
erzeugt: 6f6d0f503c8a
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.3.1.1, Figur 3"
---
> [!info] Normstelle
> SIA 266:2015, 4.3.1.1, Figur 3

*In der Herleitung: «Krümmung der Wand unter der Ausmitte e\_z, bis e\_z t\_w»*

$$
\chi_y \cdot \frac{h_{Ed}^{2}}{t_w} = 4.1 \cdot \tan\left(2.4 \cdot \frac{e_z}{t_w}\right) \cdot \left[1 + \tan^{2}\left(2.4 \cdot \frac{e_z}{t_w}\right)\right] \qquad h_{Ed} = \pi \cdot \sqrt{\frac{B_{yd}}{N_{xd}}} \qquad B_{yd} = E_{xd} \cdot \frac{l_w \cdot t_w^{3}}{12}
$$

## Im Code

- [[opencivil.mauerwerk.nachweise#Normalkraft.ansatz|Normalkraft.ansatz]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Mauerwerk trägt keinen Zug. Steht die Normalkraft ausmittig, klafft die
Lagerfuge auf der abgewandten Seite, und nur der überdrückte Teil des
Querschnitts bleibt steif. Je grösser die Ausmitte, desto kleiner dieser
Teil und desto stärker krümmt sich die Wand – die Steifigkeit hängt an der
Ausmitte, nicht nur am Material.

Figur 3 gibt diesen Zusammenhang dimensionslos: die Krümmung $\chi_y$, mit
$h_{Ed}^2/t_w$ multipliziert, über der bezogenen Ausmitte $e_z/t_w$. Für
kleine Ausmitten ist er fast linear wie bei einem ungerissenen Stab, gegen
die Grenze der Ausmitte steigt er steil an. $h_{Ed}$ ist die Länge, bei der
die Wand als Eulerstab unter $N_{xd}$ knickte; mit ihr gilt die Kurve für jede
Dicke und Steifigkeit.

Die Steifigkeit $B_{yd}$ setzt das Werkzeug wie in Gl. (8) als
$E_{xd} \cdot l_w t_w^3/12$ an, ohne den Faktor, mit dem Figur 3 sie unter
grosser Normalkraft verkleinert – nach Vorgabe, nicht nachgeschlagen; offen
in [[TODO]].
