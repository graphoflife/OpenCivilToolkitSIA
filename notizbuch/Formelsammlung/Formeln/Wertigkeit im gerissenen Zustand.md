---
erzeugt: 7bf1cdec7f60
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
n = \frac{E_s}{E_{cm}} \cdot \left(1 + \varphi\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_s$ | Elastizitätsmodul des Betonstahls | N/mm² | Vorgabe |
| $E_{cm}$ | Mittelwert des Elastizitätsmoduls | N/mm² | [[Mittelwert des Elastizitätsmoduls]] |
| $\varphi$ | – | – | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
n = \frac{E_s}{E_{cm}} \cdot \left(1 + \varphi\right) = \frac{200000\,\mathrm{N}/\mathrm{mm}^{2}}{33620\,\mathrm{N}/\mathrm{mm}^{2}} \cdot \left(1 + 2\right) = 17.85
$$

## Im Code

- [[opencivil.nachweis.mindestbewehrung#ZwaengungBiegung|ZwaengungBiegung._protokoll_ansatz]]

## Themen

- [[Zwängung auf Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Im gerissenen Querschnitt wirken Beton und Stahl elastisch zusammen. Rechnet
man den Stahl in Beton um, zählt er $n$-fach: das Verhältnis der Moduln. Der
Beton kriecht unter der Zwängung, die sich über lange Zeit aufbaut, darum
mit dem wirksamen Modul $E_{cm}/(1+\varphi)$. Ein grösseres $\varphi$ macht
den Beton weicher, die Druckzone tiefer, den Hebelarm kleiner -- und liegt
damit auf der sicheren Seite.
