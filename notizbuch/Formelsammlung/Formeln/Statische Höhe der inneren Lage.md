---
erzeugt: 85f5e1569d49
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Statische Höhe der Lage in y (innen)»*

$$
d_y = h - c_{nom} - \varnothing_x - \frac{\varnothing_y}{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h$ | Plattendicke | mm | Vorgabe |
| $c_{nom}$ | Überdeckung der Zugbewehrung oben | mm | Vorgabe |
| $\varnothing_x$ | Stabdurchmesser in x | mm | Vorgabe |
| $\varnothing_y$ | Stabdurchmesser in y | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d_y = h - c_{nom} - \varnothing_x - \frac{\varnothing_y}{2} = 280\,\mathrm{mm} - 30\,\mathrm{mm} - 16\,\mathrm{mm} - \frac{16\,\mathrm{mm}}{2} = 226\,\mathrm{mm}
$$

## Gebraucht von

- [[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._statische_hoehe|Durchstanzen._statische_hoehe]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die innere Lage liegt auf der äusseren. Ihre statische Höhe ist die
Plattendicke weniger die Überdeckung, den ganzen Stab der äusseren Lage und
den halben eigenen.
