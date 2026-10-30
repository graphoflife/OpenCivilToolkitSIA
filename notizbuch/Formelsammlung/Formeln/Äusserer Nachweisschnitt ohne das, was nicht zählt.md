---
erzeugt: a19f36c74ca5
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Äusserer Nachweisschnitt ohne das, was nicht zählt»*

$$
u_{out,red} = u_{out,0}
$$

*In der Herleitung: «Äusserer Nachweisschnitt ohne das, was nicht zählt»*

$$
u_{out,red} = u_{out,0} - \Delta u_{out}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $u_{out,0}$ | – | mm | Zwischenwert |
| $\Delta u_{out}$ | – | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
u_{out,red} = u_{out,0} = 6619\,\mathrm{mm}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
u_{out,red} = u_{out,0} - \Delta u_{out} = 5624\,\mathrm{mm} - 446\,\mathrm{mm} = 5178\,\mathrm{mm}
$$

## Gebraucht von

- [[Wirksamer Umfang des äusseren Nachweisschnitts]]

## Im Code

- [[opencivil.durchstanzen.mit_bewehrung#nachweisen|nachweisen]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der äussere Schnitt läuft im Abstand $0.5 \cdot d_{v,out}$ um die äussersten
Anker (Figur 26). Von einer Geraden zwischen zwei äussersten Ankern zählen
höchstens $1.5 \cdot d_{v,out}$ von jedem Ende: zwischen weit auseinander
liegenden Leisten trägt die Platte wie ohne Bewehrung. Hinter Aussparungen
zählt auch hier nichts (Figur 23d). Am Plattenrand endet er wie der innere,
wenn er so kürzer wird.
