---
erzeugt: c9141393e20e
art: formel
tags: [formel]
normstelle: "Kap. 9.2.10"
---
> [!info] Normstelle
> Kap. 9.2.10

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

Die [[Bruchspannung in der Sohle]] mal Sohlfläche. Weil $\varphi_{eff}$ und
$c_{eff}$ schon Bemessungswerte sind, ist $N_{Rd}$ ein Bemessungswiderstand
und steht direkt gegen $N_{Ed}$ -- ohne einen globalen Sicherheitsfaktor, wie
ihn das Kapitel für die zulässige Last verwendet. Ergibt die Formel eine
negative Bruchspannung, gilt null.
