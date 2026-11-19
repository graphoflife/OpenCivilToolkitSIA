---
erzeugt: 2d0bbb3cb6d6
art: formel
tags: [formel]
normstelle: "SIA 267:2013, 5.3.2.1, (5)"
---
> [!info] Normstelle
> SIA 267:2013, 5.3.2.1, (5)

*In der Herleitung: «Kohäsion, Bemessungswert»*

$$
c_{eff} = \frac{c_k}{\gamma_c}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $c_k$ | Kohäsion, charakteristisch | kPa | Vorgabe |
| $\gamma_c$ | Partialfaktor der Kohäsion | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
c_{eff} = \frac{c_k}{\gamma_c} = \frac{0\,\mathrm{kPa}}{1.5} = 0\,\mathrm{kPa}
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]
- [[Lastneigungsfaktor i_q]]
- [[Lastneigungsfaktor i_γ]]

## Im Code

- [[opencivil.geotechnik.grundbruch|_c_eff]]

## Themen

- [[Fundament]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Kohäsion ist der Teil der Scherfestigkeit, der auch ohne Normalspannung
trägt. Sie wird mit einem eigenen Partialfaktor $\gamma_c$ geteilt, nach
SIA 267:2013, Tabelle 1, 1.5 -- ebenso $\gamma_{cu}$ für die undrainierte
Scherfestigkeit. Neben $\varphi$ zählt sie nur, wo sie dauerhaft wirkt
(8.5.1.6), in der Sohlfuge beim Gleiten gar nicht (8.4.1.2).

Undrainiert steht an ihrer Stelle die undrainierte Scherfestigkeit $s_u$,
mit eigenem Feld und eigenem
[[Bemessungswert der undrainierten Scherfestigkeit|Bemessungswert]] (siehe
[[Tragfähigkeitsformel undrainiert]]). Bis 2026-11-19 hiess $\varphi = 0$
undrainiert, und $c_{eff}$ galt dann als $s_u$; seither wählt das ein
Schalter.
