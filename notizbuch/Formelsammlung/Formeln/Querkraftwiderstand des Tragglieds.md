---
erzeugt: d3463811f9ae
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 5.1.4.1, (41); SIA 267:2013, 9.5.2.4.1, (50)"
---
> [!info] Normstelle
> SIA 263:2013, 5.1.4.1, (41); SIA 267:2013, 9.5.2.4.1, (50)

*In der Herleitung: «Querkraftwiderstand des Tragglieds: der Stahl fliesst auf Schub bei f\_yd / √3»*

$$
V_{Rd} = \eta_i \cdot \frac{A_v \cdot f_{yd}}{\sqrt{3}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\eta_i$ | Umrechnungsfaktor des inneren Widerstands | – | Vorgabe |
| $A_v$ | Wirksame Schubfläche | mm² | [[Wirksame Schubfläche eines Kreisquerschnitts]] |
| $f_{yd}$ | Bemessungswert der Fliessgrenze | N/mm² | [[Bemessungswert der Fliessgrenze]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
V_{Rd} = \eta_i \cdot \frac{A_v \cdot f_{yd}}{\sqrt{3}} = 0.8 \cdot \frac{648\,\mathrm{mm}^{2} \cdot 435\,\mathrm{N}/\mathrm{mm}^{2}}{\sqrt{3}} = 130.1\,\mathrm{kN}
$$

## Im Code

- [[opencivil.pfahl.innen_quer#InnererQuerwiderstand._tragglied|InnererQuerwiderstand._tragglied]]

## Themen

- [[Innerer Pfahlwiderstand quer]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Stahl fliesst auf Schub bei τ_y = f_y/√3 (SIA 263:2013, 1.2), und so viel
trägt die wirksame Schubfläche (5.1.4.1, (41)). Die Norm teilt dort durch
γ_M1 = 1.05 (4.1.3); hier steht f_yd nach SIA 262, durch γ_s = 1.15 geteilt,
wie beim Tragglied längs -- rund 9 % weniger, nach Vorgabe. Dazu η_i wie
längs (SIA 267:2013, 9.5.2.4.1, (50)).

Vollstab ⌀ 36 mm, B500B: V_Rd = 0.8 · 648 mm² · 435 N/mm² / √3 = 130 kN.

Reicht die Querkraft über die Hälfte davon, ist der Biegewiderstand
abzumindern (SIA 263:2013, 5.1.5.1). Die Herleitung weist darauf hin,
rechnet es aber nicht.
