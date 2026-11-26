---
erzeugt: 2f44296bf19b
art: formel
tags: [formel]
normstelle: "SIA 265:2012, 4.2.8.1, (29)"
---
> [!info] Normstelle
> SIA 265:2012, 4.2.8.1, (29)

*In der Herleitung: «Knickwiderstand um z»*

$$
N_{K,z,Rd} = -k_{c,z} \cdot \eta_w \cdot f_{c,0,d} \cdot A
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $k_{c,z}$ | Knickbeiwert | – | [[Knickbeiwert des Holzes]] |
| $\eta_w$ | Beiwert der Holzfeuchte | – | Zwischenwert |
| $f_{c,0,d}$ | Bemessungswert der Druckfestigkeit in Faserrichtung | N/mm² | Vorgabe |
| $A$ | Fläche des Bruttoquerschnitts | mm² | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{K,z,Rd} &= -k_{c,z} \cdot \eta_w \cdot f_{c,0,d} \cdot A \\
  &= -0.466 \cdot 0.8 \cdot 14.5\,\mathrm{N}/\mathrm{mm}^{2} \cdot 64000\,\mathrm{mm}^{2} \\
  &= -346.1\,\mathrm{kN}
\end{aligned}
$$

## Im Code

- [[opencivil.nachweis.qa_holz_stabilitaet#_Herleitung.knickwiderstand|_Herleitung.knickwiderstand]]

## Themen

- [[Knicken und Kippen eines Holzstabs]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Druckkraft, die ein Stab um eine Achse noch trägt: die
Druckfestigkeit mal Fläche, gemindert mit dem
[[Knickbeiwert des Holzes]]. Negativ, wie jeder Druck im Werkzeug.
