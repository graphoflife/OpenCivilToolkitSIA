---
erzeugt: 4e3df7a27d65
art: formel
tags: [formel]
normstelle: ["SIA 263:2013, 5.2.6, (54); 5.2.2; 5.2.3, (52)", "SIA 263:2013, 5.3.5, (60); 4.5.3"]
---
> [!info] Normstellen
> SIA 263:2013, 5.2.6, (54); 5.2.2; 5.2.3, (52) · SIA 263:2013, 5.3.5, (60); 4.5.3

*In der Herleitung: «Klasse 3, (54): elastisch, bis die erste Faser fliesst – mit e, wo der Schwerpunkt neben dem Bezugspunkt liegt»*

$$
\frac{|N_{Ed}|}{N_{Rd}} + \frac{|\lambda M_{y,Ed} + e_z N_{Ed}|}{M_{y,Rd}} + \frac{|\lambda M_{z,Ed} + e_y N_{Ed}|}{M_{z,Rd}} \le 1
$$

## Im Code

- [[opencivil.nachweis.qa_stahl#StahlBiegungQA|StahlBiegungQA._ansatz]]

## Themen

- [[Stahlquerschnitt]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

In den Klassen 3 und 4 trägt der Querschnitt elastisch. Normalkraft und
Momente erzeugen Spannungen, die sich addieren; erreicht die Summe an einer
Faser $f_y$, ist der Widerstand erschöpft. Durch $f_y$ geteilt wird daraus
eine Summe von Ausnutzungen: jede Schnittgrösse durch ihren eigenen
Widerstand.

- **Klasse 3**, (54): $N_{Rd} = f_y A$ und $M_{Rd} = f_y W_{el}$ am ganzen
  Querschnitt.
- **Klasse 4**, (60): $N_{Rd} = f_y A_{eff}$ am wirksamen Querschnitt bei
  Druck, $M_{Rd} = f_y W_{eff}$ an dem bei Biegung. Unter Druck liegt der
  Schwerpunkt der wirksamen Fläche um $e_N$ neben dem des ganzen
  Querschnitts: die Normalkraft greift ausmittig an und erzeugt das Moment
  $e \cdot N$. Unter Zug zählt der ganze Querschnitt.

Auch in Klasse 3 kann der Schwerpunkt wandern, wenn eine grosse Querkraft
einem Blech einen Teil nimmt – siehe [[Minderung durch grosse Querkraft]].
Dann zählt $e \cdot N$ wie in (60).

Liegen die grössten Spannungen der Schnittgrössen nicht an derselben Faser,
ist die Summe auf der sicheren Seite.

Das Werkzeug hält $N$ fest und sucht den Faktor $\lambda$ auf die Momente,
bei dem die Summe gerade 1 wird – der
[[Erfüllungsgrad bei fester Normalkraft und fester Richtung]].
