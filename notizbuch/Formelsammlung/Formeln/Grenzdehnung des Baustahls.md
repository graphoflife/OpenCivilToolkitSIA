---
erzeugt: e2e0af30ab0b
art: formel
tags: [formel]
normstelle: "SIA 263:2013, 3.2.2.4; als Grenzdehnung nach Vorgabe"
---
> [!info] Normstelle
> SIA 263:2013, 3.2.2.4; als Grenzdehnung nach Vorgabe

$$
\varepsilon_{ud} = 15 \cdot \varepsilon_y
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varepsilon_y$ | Fliessdehnung des Baustahls | ‰ | [[Fliessdehnung]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\varepsilon_{ud} = 15 \cdot \varepsilon_y = 15 \cdot 1.69\,\text{‰} = 25.4\,\text{‰}
$$

## Im Code

- [[opencivil.material.baustahl]]

## Themen

- [[Baustahl]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wo die Linie des Baustahls endet. SIA 263:2013 nennt keine solche Dehnung;
die Spannung-Dehnung-Analysen des Werkzeugs brauchen eine. Gewählt ist, nach
Vorgabe, nicht nachgeschlagen, das 15-Fache der [[Fliessdehnung]]: so viel
verlangt 3.2.2.4 mindestens, damit die plastischen Verfahren EP und PP
gelten dürfen, und die Sorten der Tabelle 1 erfüllen es. Für S355 sind das
25.4 ‰ -- weniger als die 45 ‰ des B500B.

Der Stahl selbst bricht viel später: nach derselben Ziffer liegt seine
Bruchdehnung über 15 %. Die Grenze ist also keine Bruchdehnung, sondern die
Dehnung, bis zu der die Norm ein Fliessen zusichert. Jenseits trägt der
Stahl in der Rechnung nichts mehr, wie der Betonstahl jenseits seines
$\varepsilon_{ud}$.
