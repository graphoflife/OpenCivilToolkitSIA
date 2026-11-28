---
erzeugt: f3ac4a8bc452
art: formel
tags: [formel]
normstelle: "SIA 266:2015, 4.2.1.1, Gl. (3)"
---
> [!info] Normstelle
> SIA 266:2015, 4.2.1.1, Gl. (3)

$$
f_{yd} = \frac{f_{yk}}{\gamma_M}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $f_{yk}$ | Druckfestigkeit senkrecht zu den Stossfugen, kennzeichnend | N/mm² | Vorgabe |
| $\gamma_M$ | Widerstandsbeiwert des Mauerwerks | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
f_{yd} = \frac{f_{yk}}{\gamma_M} = \frac{2.2\,\mathrm{N}/\mathrm{mm}^{2}}{2} = 1.1\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.material.mauerwerk#_durch_gamma|_durch_gamma]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Senkrecht zu den Stossfugen, also waagrecht längs der Wand, trägt Mauerwerk
weniger: die Steine stossen dort nur über die Stossfugen aneinander, die oft
nicht ganz mit Mörtel gefüllt sind. Gebraucht wird dieser Wert, wo die Wand
waagrecht Druck trägt, etwa in einem waagrechten Gewölbe, das Querlast zu
gehaltenen Rändern trägt.

Tabelle 1 nennt für diese Richtung keinen kennzeichnenden Wert, Tabelle 7
nur den Bemessungswert. Das Werkzeug setzt darum
$f_{yk} = \gamma_M \cdot f_{yd}$ der Tabelle 7; so gibt die Formel genau
deren Zahl. Sind die Stossfugen vollfugig vermauert, gilt der grössere Wert
([[Bemessungswert der Druckfestigkeit senkrecht zu den Stossfugen, vollfugig vermauert]]).
Im Verband rechnet die Wand mit $0.85 \cdot f_{yd}$.
