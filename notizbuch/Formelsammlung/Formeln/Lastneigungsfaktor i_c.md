---
erzeugt: e845bb1b774d
art: formel
tags: [formel]
normstelle: ["Kap. 9.2.14", "Kap. 9.2.17"]
---
> [!info] Normstellen
> Kap. 9.2.14 · Kap. 9.2.17

*In der Herleitung: «Lastneigungsfaktor der Kohäsion»*

$$
i_c = i_q - \frac{1 - i_q}{N_q - 1}
$$

*In der Herleitung: «Lastneigungsfaktor, undrainiert»*

$$
i_c = 0.5 - \frac{1}{2} \sqrt{1 - \frac{T_{Ed}}{c_{eff} \cdot b \cdot L}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $i_q$ | Lastneigungsfaktor der seitlichen Auflast | – | [[Lastneigungsfaktor i_q]] |
| $N_q$ | Tragfähigkeitsfaktor der seitlichen Auflast | – | [[Tragfähigkeitsfaktor N_q]] |
| $T_{Ed}$ | Einwirkung in der Sohle | kN | Zwischenwert |
| $c_{eff}$ | Kohäsion, Bemessungswert | kPa | [[Bemessungswert der Kohäsion]] |
| $b$ | Breite des Fundaments | m | Vorgabe |
| $L$ | Länge des Fundaments | m | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
i_c = i_q - \frac{1 - i_q}{N_q - 1} = 0.77 - \frac{1 - 0.77}{13.95 - 1} = 0.76
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
i_c = 0.5 - \frac{1}{2} \sqrt{1 - \frac{T_{Ed}}{c_{eff} \cdot b \cdot L}} = 0.5 - \frac{1}{2} \sqrt{1 - \frac{40\,\mathrm{kN}}{26.7\,\mathrm{kPa} \cdot 1.5\,\mathrm{m} \cdot 2\,\mathrm{m}}} = 0.15
$$

## Gebraucht von

- [[Bruchspannung in der Sohle]]

## Im Code

- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._drainierter_fall]]
- [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch._undrainierter_fall]]

## Themen

- [[Grundbruch]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Für die Kohäsion folgt der Faktor aus [[Lastneigungsfaktor i_q|i_q]], wieder
über den Satz von Caquot. Bei sehr schräger Last kann er leicht negativ
werden; gerechnet wird mit dem Wert, wie ihn die Formel ergibt.

Undrainiert ist er ein Abzug in der Klammer,
$0.5 - \tfrac{1}{2}\sqrt{1 - T/(s_u\,b\,L)}$. Ist $T$ grösser als
$s_u\,b\,L$, kann die Sohle die Kraft nicht übertragen: die Wurzel hat keine
Lösung, und es gibt keinen Grundbruchwiderstand.
