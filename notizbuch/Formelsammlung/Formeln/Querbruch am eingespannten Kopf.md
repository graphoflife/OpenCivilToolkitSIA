---
erzeugt: 1fbe2fd35787
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 9.4.4.2.2"
---
> [!info] Normstelle
> SIA 267:2013, 9.4.4.2.2

*In der Herleitung: «Eingespannter Kopf: ein Gelenk am Kopf und darunter der Pfahl um s\_r gedreht, oder ein zweites Gelenk in s\_h; s ab Kopf»*

$$
H \cdot s_r = M_R + \int_0^L p_{E,k} \cdot \left|s - s_r\right| ds \qquad H \cdot s_h = 2 \cdot M_R + \int_0^{s_h} p_{E,k} \cdot \left(s_h - s\right) ds
$$

## Im Code

- [[opencivil.pfahl.quer#AeussererQuerwiderstand._brueche|AeussererQuerwiderstand._brueche]]

## Themen

- [[Äusserer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Eingespannt dreht sich der Kopf nicht. Damit der Pfahl ausweichen kann,
braucht er ein Gelenk am Kopf (SIA 267:2013, 9.4.4.2.2; die Mechanismen
nach Vorgabe, wie unter [[Querbruch am frei drehbaren Kopf]]): kurz dreht
er sich darunter starr um s_r, lang knickt er ein zweites Mal in s_h und
steht darunter still. Ein Moment am Kopf ist hier Reaktion und zählt
nicht.

Mit p_E überall gleich c wird lang H = 2 · √(M_R · c), mit
s_h = 2 · √(M_R / c). Für c = 200 kN/m und M_R = 500 kNm: H = 632 kN in
s_h = 3.16 m -- gut 40 % mehr als frei drehbar. Ist er so kurz, dass
M_R ≥ c · L² / 2 -- hier bis L = 2.24 m --, schiebt er sich als Ganzes:
H = c · L.
