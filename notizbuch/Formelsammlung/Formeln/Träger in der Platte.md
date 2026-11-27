---
erzeugt: b8fc1f6d2f88
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Ein Träger: Balken in der Mittelebene und Platte über seine Breite b»*

$$
\begin{aligned} & EI = E_{cm} \cdot b \cdot \frac{(h + h_T)^3 - h^3}{12} \\ & M = M_{\mathrm{Balken}} + b \cdot \bar{m}_t \qquad V = V_{\mathrm{Balken}} + b \cdot \bar{v}_t \end{aligned}
$$

## Im Code

- [[opencivil.decke.fem.herleitung#_ansaetze|_ansaetze]]

## Themen

- [[FEM der Decke]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Ein Träger ist in der FEM ein Balken in der Mittelebene der Platte, auf den
Kanten des Netzes längs seiner Achse. Seine Biegesteifigkeit ist die des
Rechtecks $b \times (h + h_T)$ ohne den Teil $b \times h$, den die Platte
über seine Breite schon trägt. Torsionssteifigkeit hat er keine: er hält die
Platte nur in der Höhe, nicht in der Drehung um seine Achse. Ob $h_T$ über
oder unter die Platte reicht, ist für die Steifigkeit gleich, denn der
Balken liegt in der Mittelebene.

Moment und Querkraft des Trägers sind, was der Balken trägt, und dazu, was
die Platte über seine Breite trägt: $b$ mal das Mittel von $m_t$ und $v_t$
quer über $b$, in Richtung der Achse. So hat auch ein Träger mit $h_T = 0$
seine Schnittkräfte; dann trägt nur die Platte.

Beispiel: Platte $h = 0.25\,\mathrm{m}$, Träger $b = 0.4\,\mathrm{m}$ und
$h_T = 0.30\,\mathrm{m}$, C30/37 ($E_{cm} = 32\,000\,\mathrm{N/mm^2}$):
$EI = 32\,000 \cdot 0.4 \cdot (0.55^3 - 0.25^3)/12 = 160.8\,\mathrm{MNm^2}$.

Die Querkraft des Balkens ist über jedes Stück zwischen zwei Knoten fest.
Am Lager liegt sie darum etwas unter dem wahren Wert, bei einem Netz von
0.2 m um etwa 7 %.
