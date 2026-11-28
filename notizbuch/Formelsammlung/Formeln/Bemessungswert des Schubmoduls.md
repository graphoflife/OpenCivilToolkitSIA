---
erzeugt: a5514563a853
art: formel
tags: [formel]
normstelle: "SIA 266:2015, Tabelle 7; Gl. (2) und (5)"
---
> [!info] Normstelle
> SIA 266:2015, Tabelle 7; Gl. (2) und (5)

$$
G_d = \frac{G_k}{\gamma_M}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $G_k$ | Schubmodul, kennzeichnend | N/mm² | [[Schubmodul, kennzeichnend]] |
| $\gamma_M$ | Widerstandsbeiwert des Mauerwerks | – | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
G_d = \frac{G_k}{\gamma_M} = \frac{2800\,\mathrm{N}/\mathrm{mm}^{2}}{2} = 1400\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Im Code

- [[opencivil.material.mauerwerk#_durch_gamma|_durch_gamma]]

## Themen

- [[Mauerwerk]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Bemessungswert des Schubmoduls folgt wie $E_{xd}$ aus dem
kennzeichnenden Wert durch $\gamma_M$. Tabelle 7 nennt ihn in kN/mm² auf
eine Stelle gerundet – bei Leichtbackstein 0.4 für die 0.36, die die Formel
gibt. Gebraucht wird er, wo die Steifigkeit der Wand in ihrer Ebene zählt,
etwa wenn mehrere Wände eine waagrechte Kraft gemeinsam tragen: die steifere
zieht mehr an. Im Verband gilt auch er mal 0.85.
