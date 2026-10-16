---
erzeugt: 46ef76e19571
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

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
- [[Lastneigungsfaktor i_c]]
- [[Lastneigungsfaktor i_q]]
- [[Lastneigungsfaktor i_γ]]

## Im Code

- [[opencivil.geotechnik.grundbruch|_c_eff]]

## Themen

- [[Fundament]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Kohäsion ist der Teil der Scherfestigkeit, der auch ohne Normalspannung
trägt. Sie wird mit einem eigenen Partialfaktor $\gamma_c$ geteilt.

Mit $\varphi = 0$ -- undrainiert -- steht an ihrer Stelle die undrainierte
Scherfestigkeit $s_u$; das Werkzeug liest $c_{eff}$ dann als $s_u$ (siehe
[[Tragfähigkeitsformel undrainiert]]).
