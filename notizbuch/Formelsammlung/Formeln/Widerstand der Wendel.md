---
erzeugt: d30a42704676
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4.3, (45); 4.3.3.4.4"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4.3, (45); 4.3.3.4.4

*In der Herleitung: «Widerstand der Wendel: 70 % senkrechter Bügel»*

$$
V_{Rd,s} = 0.7 \cdot \frac{A_{sw}}{s_w} \cdot z \cdot f_{yd} \cdot \cot \alpha
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_{sw}$ | Querschnitt der Wendel | mm² | [[Querschnitt der Wendel]] |
| $s_w$ | Ganghöhe der Wendel | mm | Vorgabe |
| $z$ | Hebelarm der inneren Kräfte | mm | [[Hebelarm der inneren Kräfte]] |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |
| $\alpha$ | Neigung der Druckdiagonalen | ° | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  V_{Rd,s} &= 0.7 \cdot \frac{A_{sw}}{s_w} \cdot z \cdot f_{yd} \cdot \cot \alpha \\
  &= 0.7 \cdot \frac{157\,\mathrm{mm}^{2}}{150\,\mathrm{mm}} \cdot 608.4\,\mathrm{mm} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2} \cdot \cot 30{}^{\circ} \\
  &= 335.9\,\mathrm{kN}
\end{aligned}
$$

## Gebraucht von

- [[Querkraftwiderstand des Pfahls]]

## Im Code

- [[opencivil.pfahl.innen_quer#InnererQuerwiderstand._neigung|InnererQuerwiderstand._neigung]]

## Themen

- [[Innerer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Fachwerk der Bügel (SIA 262:2025, 4.3.3.4.3, (45)), für die Wendel
abgemindert: sie läuft rund um den Pfahl und steht nur an den Flanken in
Richtung der Querkraft, am gezogenen und am gedrückten Rand läuft sie quer
dazu. Ohne weiteren Nachweis zählt sie darum zu 70 % von Bügeln (4.3.3.4.4).
Ihre Steigung bleibt unberücksichtigt: beim ⌀ 900 steigt sie auf einem
Umgang von über zwei Metern um 150 mm.

⌀ 10 mm alle 150 mm, z = 608 mm, B500B, α = 30°: V_Rd,s = 0.7 · 1.05 mm²/mm
· 608 mm · 435 N/mm² · 1.73 = 336 kN.

Einzugeben ist die grösste Ganghöhe längs des Pfahls. SIA 267:2013,
9.6.3.2.4, will sie in der Regel nicht über 0.40 m und am Kopf eng, 0.10 bis
0.15 m; darüber gibt die Herleitung einen Hinweis.
