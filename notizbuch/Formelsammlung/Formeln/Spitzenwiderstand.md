---
erzeugt: 6b343d5c7a03
art: formel
tags: [formel]
normstelle: "Kap. 12.5, Bild 12.4; SIA 267:2013, 9.4.4.1.1"
---
> [!info] Normstelle
> Kap. 12.5, Bild 12.4; SIA 267:2013, 9.4.4.1.1

$$
R_{b,k} = A_b \cdot q_{b,k}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $A_b$ | Fläche des Fusses | m² | [[Fläche des Pfahlquerschnitts]] |
| $q_{b,k}$ | Spitzendruck | kPa | [[Spitzendruck drainiert]], [[Spitzendruck undrainiert]], Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
R_{b,k} = A_b \cdot q_{b,k} = 0.636\,\mathrm{m}^{2} \cdot 4714\,\mathrm{kPa} = 2999\,\mathrm{kN}
$$

## Gebraucht von

- [[Äusserer Widerstand auf Druck]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._fuss]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Spitzendruck mal der Fläche des Fusses: was der Fuss trägt
(SIA 267:2013, 9.4.4.1.1). Er setzt voraus, dass die Schicht unter dem Fuss
mächtig genug ist, dass er sie nicht durchstanzt (Kap. 12.5). Ein Fuss
⌀ 800 mit 9000 kN/m² trägt 0.503 m² · 9000 kN/m² ≈ 4530 kN.
