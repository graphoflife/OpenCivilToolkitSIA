---
erzeugt: 9dbef48296b2
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Platz für die Anker zwischen den Überdeckungen»*

$$
h_{frei} = h - c_{nom} - c_v
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $h$ | Plattendicke | mm | Vorgabe |
| $c_{nom}$ | Überdeckung der Zugbewehrung oben | mm | Vorgabe |
| $c_v$ | Überdeckung der Durchstanzbewehrung unten | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
h_{frei} = h - c_{nom} - c_v = 280\,\mathrm{mm} - 30\,\mathrm{mm} - 30\,\mathrm{mm} = 220\,\mathrm{mm}
$$

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#nachweisen|nachweisen]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Plattendicke weniger die Überdeckung der Zugbewehrung und die der Anker
auf der Druckseite: so hoch dürfen die Anker sein. Die Höhe $h_A$ ist die
nächstkleinere, die ancoPLUS liefert -- sie endet auf 5 mm, in Schritten von
10 mm. Diese Regel ist aus der Zulassung des Herstellers und zwei seiner
Beispiele abgeleitet, nicht nachgeschlagen.
