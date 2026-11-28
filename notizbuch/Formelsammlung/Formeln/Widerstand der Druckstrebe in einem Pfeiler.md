---
erzeugt: ec22b94e3b18
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.3.2.2, Gl. (13), Figur 7 und 8"
---
> [!info] Normstelle
> SIA 266:2015, 4.3.2.2, Gl. (13), Figur 7 und 8

*In der Herleitung: «Widerstand der Druckstrebe»*

$$
N_{Rd} = f_{yd} \cdot l_2 \cdot t_{nom} \cdot \cos^{2} \alpha
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yd}$ | Druckfestigkeit der Wand parallel zu den Lagerfugen | N/mm² | Zwischenwert |
| $l_2$ | Gedrückte Länge am Fuss | mm | [[Gedrückte Länge am Fuss eines Pfeilers]] |
| $t_{nom}$ | Dicke, auf der die Strebe trägt | mm | [[Dicke einer Schubwand mit ausmittiger Normalkraft]] |
| $\alpha$ | Neigung der Druckstrebe | ° | [[Neigung der Druckstrebe in einem Pfeiler]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  N_{Rd} &= f_{yd} \cdot l_2 \cdot t_{nom} \cdot \cos^{2} \alpha \\
  &= 1.36\,\mathrm{N}/\mathrm{mm}^{2} \cdot 487\,\mathrm{mm} \cdot 127\,\mathrm{mm} \cdot \cos^{2} 7.8{}^{\circ} \\
  &= 82.6\,\mathrm{kN}
\end{aligned}
$$

## Im Code

- [[opencivil.mauerwerk.schub#Schub.gedrueckt|Schub.gedrueckt]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Strebe trägt auf der gedrückten Länge $l_2$ und der Dicke $t_{nom}$.
Ihre Kraft ist $N_{xd}/\cos\alpha$; quer zu ihr ist sie
$l_2 \cos\alpha$ breit. Ihre Spannung darf $f_{yd}$ erreichen:
$N_{xd}/\cos\alpha \le f_{yd}\, l_2 \cos\alpha\, t_{nom}$, nach
$N_{xd}$ aufgelöst Gl. (13) (4.3.2.2). Mittig steht die ganze Dicke
$t_w$ da; ausmittig die kleinere nach 4.3.3.1.

Ob die Lagerfugen dabei halten, prüft das Gleiten nach Gl. (14). Den
erweiterten Nachweis nach 4.3.2.3 mit dem Beiwert $k_V$ rechnet das
Werkzeug nicht.
