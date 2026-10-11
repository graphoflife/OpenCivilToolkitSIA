---
erzeugt: 62e6c77f6e5f
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.2.1.6"
---
> [!info] Normstelle
> SIA 262:2025, 4.2.1.6

$$
k_{\sigma} = \frac{E_{cd}}{400 \cdot f_{cd}}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $E_{cd}$ | Bemessungswert des Elastizitätsmoduls | N/mm² | [[Bemessungswert des Elastizitätsmoduls]] |
| $f_{cd}$ | Bemessungswert der Betondruckfestigkeit | N/mm² | [[Bemessungswert der Betondruckfestigkeit]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
k_{\sigma} = \frac{E_{cd}}{400 \cdot f_{cd}} = \frac{33620\,\mathrm{N}/\mathrm{mm}^{2}}{400 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2}} = 4.202
$$

## Im Code

- [[opencivil.material.beton]]
- [[opencivil.querschnitt.analyse#Querschnittsanalyse.werkstoffe_protokollieren|Querschnittsanalyse.werkstoffe_protokollieren]]

## Themen

- [[Beton]]
- [[Schiefe Biegung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die [[Parabel-Rechteck-Beziehung des Betons]] ist durch ihren Höchstwert
$f_{cd}$ bei der Dehnung $\varepsilon_{c1d}$ festgelegt. Wie steil sie bei null
beginnt, sagt $k_\sigma$: ihr Anstieg dort ist $k_\sigma \cdot f_{cd} /
\varepsilon_{c1d}$, also $k_\sigma$-mal die Sekante zum Höchstwert.

- $k_\sigma = 2$ gibt die gewöhnliche Parabel $\sigma = f_{cd}\,(2\eta - \eta^2)$.
- Ein grösseres $k_\sigma$ macht den Beton bei kleinen Dehnungen steifer; die
  Kurve steigt steil und biegt dann um.
- $k_\sigma = 1$ ist eine Gerade bis $f_{cd}$ bei $\varepsilon_{c1d}$. Kleiner
  wird er nicht angesetzt: darunter hätte der Nenner im ansteigenden Ast eine
  Nullstelle (siehe [[Beiwert der Parabel, mit dem wirksamen Modul]]).

Mit $k_\sigma = E_{cd}/(400 \cdot f_{cd})$ und $\varepsilon_{c1d}$ = 2 ‰ ist der
Anstieg bei null $1.25 \cdot E_{cd}$ -- ein bekannter Unterschied, den das
Werkzeug so lässt (entschieden 2026-10-11, siehe [[Arbeitsweise]]).
