---
erzeugt: 969012555901
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
g_k = \rho \cdot g \cdot t_w
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\rho$ | Dichte für das Eigengewicht | kg/m³ | Vorgabe |
| $g$ | Erdbeschleunigung | m/s² | Vorgabe |
| $t_w$ | Dicke der Wand | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
g_k = \rho \cdot g \cdot t_w = 1800\,\mathrm{kg}/\mathrm{m}^{3} \cdot 10\,\mathrm{m}/\mathrm{s}^{2} \cdot 175\,\mathrm{mm} = 3.15\,\mathrm{kN}/\mathrm{m}^{2}
$$

## Im Code

- [[opencivil.mauerwerk.herleitung#_lasten|_lasten]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Je Quadratmeter Ansicht wiegt eine Wand ihre Dichte mal die
Erdbeschleunigung mal ihre Dicke. Die Dichte bringt das Mauerwerk mit,
Standardmauerwerk aus SIA 261:2020, Anhang A, Tabelle 28; $g = 10$ m/s² wie
überall im Werkzeug.

Das Eigengewicht kommt in den Lastfall, der es trägt, und geht wie jede
Last zu den Pfeilern: was über einem Pfeiler liegt, in ihn, was über einer
Öffnung liegt, über den Sturz. Ein Sturz wiegt wie Mauerwerk – nach
Vorgabe, nicht nachgeschlagen.
