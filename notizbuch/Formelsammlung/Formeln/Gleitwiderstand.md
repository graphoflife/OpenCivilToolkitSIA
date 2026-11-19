---
erzeugt: f0d776f4fbe8
art: formel
tags: [formel]
normstelle: ["SIA 267:2013, 8.5.2.2, (31)", "SIA 267:2013, 8.5.2.2, (32)"]
---
> [!info] Normstellen
> SIA 267:2013, 8.5.2.2, (31) · SIA 267:2013, 8.5.2.2, (32)

*In der Herleitung: «Gleitwiderstand»*

$$
T_{Rd} = N_{Ed} \cdot \tan \delta_d
$$

*In der Herleitung: «Gleitwiderstand, undrainiert»*

$$
T_{Rd} = b \cdot L \cdot s_{u,d}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $N_{Ed}$ | Einwirkung normal zur Sohle | kN | Zwischenwert |
| $\delta_d$ | Sohlreibungswinkel, Bemessungswert | ° | [[Bemessungswert des Sohlreibungswinkels]] |
| $b$ | Breite des Fundaments | m | Vorgabe |
| $L$ | Länge des Fundaments | m | Vorgabe |
| $s_{u,d}$ | Undrainierte Scherfestigkeit, Bemessungswert | kPa | [[Bemessungswert der undrainierten Scherfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
T_{Rd} = N_{Ed} \cdot \tan \delta_d = 1500\,\mathrm{kN} \cdot \tan 27.51{}^{\circ} = 781.1\,\mathrm{kN}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
T_{Rd} = b \cdot L \cdot s_{u,d} = 1.5\,\mathrm{m} \cdot 2\,\mathrm{m} \cdot 26.7\,\mathrm{kPa} = 80\,\mathrm{kN}
$$

## Im Code

- [[opencivil.geotechnik.gleiten#Gleiten._widerstand|Gleiten._widerstand]]

## Themen

- [[Gleiten]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Drainiert nimmt die Sohlfuge $T$ durch Reibung auf, höchstens
$N_{Ed} \tan\delta_d$ (SIA 267:2013, 8.5.2.2, (31)). Die Kohäsion zählt dort
nicht mit: die Norm lässt $c'$ in der Fuge nur zu, wo sicher ist, dass sie
dauerhaft bleibt (8.4.1.2).

Undrainiert trägt die Sohlfläche mit der undrainierten Scherfestigkeit,
$T_{Rd} = b \cdot L \cdot s_{u,d}$ (8.5.2.2, (32)), und das
unabhängig von $N$. Bei feinkörnigen Böden ist dieser Kurzzeitnachweis
verlangt (8.5.1.5). Ohne Ausmitte ist die wirksame Fläche $A'$ der Norm die
ganze Sohle $b \cdot L$.

Ein Erdwiderstand vor dem Fundament wird nicht angesetzt. Die Norm erlaubt
ihn, mit $\gamma_M = 1.4$ (8.4.3.1, 8.5.2.3), das Buch nur, wenn er dauernd
vorhanden ist und die Verschiebung, die er braucht, zulässig ist
(Kap. 9.2.18); ohne ihn liegt die Rechnung auf der sicheren Seite. Die
Sicherheit steckt in $\delta_d$ und $s_{u,d}$; einen Widerstandsbeiwert
$\gamma_R$ (8.5.2.1) setzt das Werkzeug 1.0.
