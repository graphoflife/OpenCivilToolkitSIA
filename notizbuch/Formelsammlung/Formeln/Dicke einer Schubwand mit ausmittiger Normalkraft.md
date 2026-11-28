---
erzeugt: a82a2c61c5d0
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.3.3.1"
---
> [!info] Normstelle
> SIA 266:2015, 4.3.3.1

*In der Herleitung: «Dicke, auf der die Strebe trägt»*

$$
t_{nom} = t_w - 2 \cdot e_z
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $t_w$ | Dicke der Wand | mm | Zwischenwert |
| $e_z$ | Grösste Ausmitte quer zur Wand unter N\_xd | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
t_{nom} = t_w - 2 \cdot e_z = 175\,\mathrm{mm} - 2 \cdot 24\,\mathrm{mm} = 127\,\mathrm{mm}
$$

## Gebraucht von

- [[Widerstand der Druckstrebe in einem Pfeiler]]

## Im Code

- [[opencivil.mauerwerk.schub#Schub._dicke|Schub._dicke]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Steht die Normalkraft quer zur Wand ausmittig, ist nicht die ganze Dicke
gedrückt. Die Strebe, die den Schub trägt, findet nur in dem Teil Platz,
über dem die Resultierende mittig steht: $t_w - 2 e_z$ (4.3.3.1). Für $e_z$
nimmt das Werkzeug die grösste Ausmitte der verformten Wand unter
$N_{xd}$, gerechnet wie für $k_N$ nach Figur 3 auf der gedrückten Länge
$l_2$. Findet die Wand unter $N_{xd}$ kein Gleichgewicht, gilt die
vereinfachte Dicke $0.25\,t_w$ – dünner wird $t_{nom}$ ohnehin nicht, weil
die Ausmitte die Grenze $0.375\,t_w$ nicht überschreitet.

Die Norm setzt $t_{nom}$ in Gl. (18) mit dem Beiwert $k_V$ der Figur 9.
Das Werkzeug setzt es in die Druckstrebe nach Gl. (13) – nach Vorgabe,
nicht nachgeschlagen; offen in [[TODO]].
