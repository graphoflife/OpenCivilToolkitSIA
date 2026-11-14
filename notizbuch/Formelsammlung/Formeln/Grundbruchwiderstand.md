---
erzeugt: 88a7c493d563
art: formel
tags: [formel]
normstelle: "Kap. 9.2.11; SIA 267:2013, 8.5.3.5"
---
> [!info] Normstelle
> Kap. 9.2.11; SIA 267:2013, 8.5.3.5

$$
N_{Rd} = \sigma_f \cdot b \cdot L
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\sigma_f$ | Bruchspannung in der Sohle | kPa | [[Bruchspannung in der Sohle]] |
| $b$ | Breite des Fundaments | m | Vorgabe |
| $L$ | Länge des Fundaments | m | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
N_{Rd} = \sigma_f \cdot b \cdot L = 568.8\,\mathrm{kPa} \cdot 2\,\mathrm{m} \cdot 2.5\,\mathrm{m} = 2843.8\,\mathrm{kN}
$$

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._widerstand]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die [[Bruchspannung in der Sohle]] mal Sohlfläche, wie das Buch die Bruchlast
des Rechteckfundaments schreibt (Kap. 9.2.11). Weil $\varphi_{eff}$ und
$c_{eff}$ schon Bemessungswerte sind, ist $N_{Rd}$ ein Bemessungswiderstand
und steht direkt gegen $N_{Ed}$ (SIA 267:2013, 8.5.3.5) -- ohne einen
globalen Sicherheitsfaktor, wie ihn das Buch für die zulässige Last
verwendet. Den Widerstandsbeiwert $\gamma_R$ der Norm (8.5.2.1) setzt das
Werkzeug 1.0. Ergibt die Formel eine negative Bruchspannung, gilt null.
