---
erzeugt: 8462715ace7f
art: formel
tags: [formel]
normstelle: "Kap. 12.5, Bild 12.4"
---
> [!info] Normstelle
> Kap. 12.5, Bild 12.4

*In der Herleitung: «Spitzendruck, drainiert»*

$$
q_{b,k} = \left(c^{*} \cdot N_c + \sigma'_{v,F} \cdot N_q\right) \cdot X
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $c^{*}$ | Kohäsion am Fuss | kPa | [[Kohäsion für örtliches Abscheren]] |
| $N_c$ | Tragfähigkeitsfaktor der Kohäsion | – | [[Tragfähigkeitsfaktor N_c]] |
| $\sigma'_{v,F}$ | Wirksame Spannung am Fuss | kPa | [[Wirksame Spannung am Pfahlfuss]] |
| $N_q$ | Tragfähigkeitsfaktor der seitlichen Auflast | – | [[Tragfähigkeitsfaktor N_q]] |
| $X$ | Form- und Tiefenfaktor | – | [[Form- und Tiefenfaktor des Pfahlfusses]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  q_{b,k} &= \left(c^{*} \cdot N_c + \sigma'_{v,F} \cdot N_q\right) \cdot X \\
  &= \left(3.3\,\mathrm{kPa} \cdot 19.32 + 180\,\mathrm{kPa} \cdot 9.6\right) \cdot 2.63 \\
  &= 4714\,\mathrm{kPa}
\end{aligned}
$$

## Gebraucht von

- [[Spitzenwiderstand]]

## Im Code

- [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand._fuss_drainiert]]

## Themen

- [[Äusserer Pfahlwiderstand]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Bruchspannung unter dem Fuss nach der Formel des Grundbruchs, mit den
Tragfähigkeitsfaktoren von dort (Kap. 9.2.6) und dem Form- und Tiefenfaktor
X. Den Anteil aus der Breite lässt das Buch weg: gegen die grosse Tiefe des
Fusses ist er klein (Kap. 12.5). σ'_v und c' sind wirksame Grössen. Bei σ'_v = 274.5 kN/m², φ' = 29° ohne
Kohäsion (N_q = 16.4) und X = 2.0 sind es 274.5 · 16.4 · 2.0 ≈ 9000 kN/m².
