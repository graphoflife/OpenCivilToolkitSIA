---
erzeugt: 34a9d7c7d635
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.2.3"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.2.3

*In der Herleitung: «Nichts mindert den Schnitt»*

$$
u_{red} = u_0
$$

*In der Herleitung: «Nachweisschnitt ohne das, was nicht zählt»*

$$
u_{red} = u_0 - \Delta u_A
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $u_0$ | – | mm | [[Nachweisschnitt im Abstand d_v∕2]], Zwischenwert, [[Nachweisschnitt um das Wandende – 1.5·d_v entlang der Wand]], [[Nachweisschnitt um die Wandecke – je 1.5·d_v entlang der Wände]] |
| $\Delta u_A$ | – | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
u_{red} = u_0 = 2335\,\mathrm{mm}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
u_{red} = u_0 - \Delta u_A = 3811\,\mathrm{mm} - 353\,\mathrm{mm} = 3458\,\mathrm{mm}
$$

## Gebraucht von

- [[Wirksamer Umfang des Nachweisschnitts]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._nachweisschnitt|Durchstanzen._nachweisschnitt]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Nicht der ganze Schnitt zählt (Figur 23). An grossen gestützten Flächen
zählen gerade Stücke nur bis 1.5·d_v von einer Ecke, denn an den Ecken
ballt sich die Querkraft. Hinter einer Aussparung, die näher als 5·d_v am
Schnitt liegt, zählt nichts, was zwischen den beiden Strahlen von der
Stützenachse an ihr vorbei liegt. Mindert nichts den Schnitt, ist
$u_{red} = u_0$.
