---
erzeugt: ec34b848d312
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.3.4.6, (47)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.3.4.6, (47)

*In der Herleitung: «Widerstand der Druckdiagonalen»*

$$
V_{Rd,c} = b_w \cdot z \cdot k_c \cdot f_{cd} \cdot \sin \alpha \cdot \cos \alpha
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $b_w$ | Breite des Stegs | mm | [[Stegbreite des Kreisquerschnitts]] |
| $z$ | Hebelarm der inneren Kräfte | mm | [[Hebelarm der inneren Kräfte]] |
| $k_c$ | Abminderung der Betondruckfestigkeit in der Druckdiagonalen | – | Zwischenwert |
| $f_{cd}$ | Bemessungswert der Betondruckfestigkeit | N/mm² | [[Bemessungswert der Betondruckfestigkeit]] |
| $\alpha$ | Neigung der Druckdiagonalen | ° | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  V_{Rd,c} &= b_w \cdot z \cdot k_c \cdot f_{cd} \cdot \sin \alpha \cdot \cos \alpha \\
  &= 474.4\,\mathrm{mm} \cdot 608.4\,\mathrm{mm} \cdot 0.55 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} \cdot \sin 30{}^{\circ} \cdot \cos 30{}^{\circ} \\
  &= 1374.8\,\mathrm{kN}
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

Wie bei der Platte (SIA 262:2025, 4.3.3.4.6, (47)), mit der Breite b_w des
Kreises statt eines Meters. Die Diagonalen sind längs gerissen und kreuzen
die Wendel schief; k_c = 0.55 mindert die Festigkeit des Betons darum wie in
einem Steg (4.2.1.7).

⌀ 900 mm, C30/37, α = 30°: V_Rd,c = 474 mm · 608 mm · 0.55 · 20 N/mm² · 0.43
= 1375 kN -- viermal so viel wie die Wendel.
