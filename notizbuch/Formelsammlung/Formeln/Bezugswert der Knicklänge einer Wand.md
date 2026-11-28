---
erzeugt: e1159b2964d6
art: formel
tags: [formel]
normstelle: ["SIA 266:2015, 4.3.1.2, Gl. (8)", "SIA 266:2015, 4.3.3.1, Gl. (17)"]
---
> [!info] Normstellen
> SIA 266:2015, 4.3.1.2, Gl. (8) · SIA 266:2015, 4.3.3.1, Gl. (17)

*In der Herleitung: «Bezugswert der Knicklänge»*

$$
h_{Ed} = \pi \cdot \sqrt{\frac{E_{xd} \cdot l_w \cdot t_w^{3}}{12 \cdot N_{xd}}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{xd}$ | Elastizitätsmodul der Wand | N/mm² | Zwischenwert |
| $l_w$ | Breite des Pfeilers | mm | Zwischenwert |
| $t_w$ | Dicke der Wand | mm | Zwischenwert |
| $N_{xd}$ | Normalkraft am Fuss des Pfeilers | kN | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
h_{Ed} = \pi \cdot \sqrt{\frac{E_{xd} \cdot l_w \cdot t_w^{3}}{12 \cdot N_{xd}}} = \pi \cdot \sqrt{\frac{2975\,\mathrm{N}/\mathrm{mm}^{2} \cdot 800\,\mathrm{mm} \cdot \left(175\,\mathrm{mm}\right)^{3}}{12 \cdot 109.9\,\mathrm{kN}}} = 9.77\,\mathrm{m}
$$

## Im Code

- [[opencivil.mauerwerk.nachweise#Normalkraft.stelle|Normalkraft.stelle]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

$h_{Ed}$ ist die Länge, bei der ein beidseits gelenkiger Stab mit der
Steifigkeit des ungerissenen Mauerwerks, $E_{xd} \cdot l_w t_w^3/12$, unter
$N_{xd}$ nach Euler knickte. Je kürzer sie gegenüber der Höhe der Wand ist,
desto schlanker ist die Wand für ihre Last.

Der vereinfachte Nachweis nach 4.3.1.2 vergleicht die Höhe der Wand mit
ihr. Hier bezieht sie die Krümmung der Figur 3 auf die Wand; das
Verhältnis $h_w/h_{Ed}$ steht in der Herleitung zur Auskunft – nach ihm
ordnet Figur 19 die Kurven von $k_N$.

Trägt der Pfeiler auch Schub und steht die Normalkraft quer zur Wand
ausmittig, steift nur seine gedrückte Länge $l_2$ ihn aus; sie steht dann
statt $l_w$ (Gl. (17)).
