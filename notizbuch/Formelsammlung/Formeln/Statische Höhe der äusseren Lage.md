---
erzeugt: c29019b0b191
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Statische Höhe der Lage in x (aussen)»*

$$
d_x = h - c_{nom} - \frac{\varnothing_x}{2}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h$ | Plattendicke | mm | Vorgabe |
| $c_{nom}$ | Überdeckung der Zugbewehrung oben | mm | Vorgabe |
| $\varnothing_x$ | Stabdurchmesser in x | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
d_x = h - c_{nom} - \frac{\varnothing_x}{2} = 280\,\mathrm{mm} - 30\,\mathrm{mm} - \frac{16\,\mathrm{mm}}{2} = 242\,\mathrm{mm}
$$

## Gebraucht von

- [[Biegewiderstand im Stützstreifen]]
- [[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._statische_hoehe|Durchstanzen._statische_hoehe]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die äussere Lage liegt direkt hinter der Überdeckung. Ihre statische Höhe ist
die Plattendicke weniger die Überdeckung und den halben Stabdurchmesser.
Welche Richtung aussen liegt, ist eine Eingabe.
