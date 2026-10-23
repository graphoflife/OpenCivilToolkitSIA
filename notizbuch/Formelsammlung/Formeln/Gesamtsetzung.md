---
erzeugt: 28169e940330
art: formel
tags: [formel]
normstelle: "Kap. 8.2"
---
> [!info] Normstelle
> Kap. 8.2

*In der Herleitung: «Setzung»*

$$
s = s_W + s_E
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $s_W$ | Setzung aus Wiederbelastung | mm | [[Setzung aus Wiederbelastung]] |
| $s_E$ | Setzung aus Erstbelastung | mm | [[Setzung aus Erstbelastung]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
s = s_W + s_E = 0.4\,\mathrm{mm} + 9.5\,\mathrm{mm} = 9.9\,\mathrm{mm}
$$

## Im Code

- [[opencivil.geotechnik.setzung#Setzung|Setzung._nachweis]]

## Themen

- [[Setzung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wieder- und Erstbelastung zusammen: die Setzung unter dem Punkt, für den
gerechnet wurde -- beim starren Fundament die mittlere, beim schlaffen die
grösste ([[Lage des Punktes längs L]]). Sie wird gegen die zulässige Setzung
gehalten, $s \le s_{zul}$, der [[Erfüllungsgrad]] ist $s_{zul}/s$. Welche
Setzung zulässig ist, hängt am Bauwerk -- an seinem Zweck, seiner
Konstruktion, seinen Anschlüssen (Kap. 8.12); die Vorgabe der Maske ist nur
ein Startwert.
