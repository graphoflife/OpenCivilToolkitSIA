---
erzeugt: ae7c73d63c08
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Spannungsfunktion von Prandtl; am Rand des Hohlraums k ist φ = φ\_k»*

$$
\nabla^2 \phi = -2 \qquad \phi = 0 \ \text{am Rand} \qquad \oint_k \frac{\partial \phi}{\partial n}\, ds = -2\, A_k
$$

## Im Code

- [[opencivil.querschnitt.analyse#Querschnittsanalyse.torsion_protokollieren|Querschnittsanalyse.torsion_protokollieren]]

## Themen

- [[Querschnittsanalyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Unter Torsion nach St. Venant verdrillt sich ein Stab gleichmässig, um θ je
Länge, und sein Schub lässt sich aus einer einzigen Funktion φ(y, z)
ablesen: er läuft entlang ihrer Höhenlinien und ist $G\,\theta\,|\nabla\phi|$
stark. Damit die Verschiebungen zusammenpassen, gilt im Material
$\nabla^2\phi = -2$. Am freien Rand läuft der Schub dem Rand entlang, φ ist
dort fest -- am äusseren Rand null.

Auch am Rand eines Hohlraums ist φ fest, aber nicht null. Seinen Wert $\phi_k$
legt das Ringintegral fest, mit $n$ vom Hohlraum ins Material: die Wand um
den Hohlraum verdrillt sich genau so wie der Rest des Stabs, und das heisst
$\oint_k \partial\phi/\partial n\,ds = -2A_k$, mit $A_k$ der Fläche, die sein
Rand umschliesst -- eine Insel darin zählt mit.

Anschaulich ist φ eine Haut, über den Querschnitt gespannt und von unten
gleichmässig gedrückt (Seifenhautgleichnis): ihr Gefälle ist der Schub, ihr
Volumen das halbe $I_T$. Über einem Hohlraum liegt eine steife, gewichtslose
Platte, die sich frei heben kann.

Wie das Werkzeug die Gleichung löst, steht bei
[[Torsionsträgheitsmoment, nach Richardson aus beiden Gittern]].
