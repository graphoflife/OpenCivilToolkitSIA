---
erzeugt: fd0c77522755
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\varepsilon_{c,Rand} \ge -\varepsilon_{c2d} \qquad -\varepsilon_{ud} \le \varepsilon_{s,i} \le \varepsilon_{ud} \qquad \varepsilon\left(z_C\right) \ge -\varepsilon_{c1d}, \quad z_C = h \cdot \left(1 - \frac{\varepsilon_{c1d}}{\varepsilon_{c2d}}\right)
$$

## Im Code

- [[opencivil.spannungsanalyse#_herleitung|_herleitung]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Wo eine Linie der Analyse endet: bei der grössten Verformung, zu der es noch
ein Gleichgewicht gibt -- dort, wo die erste Grenzdehnung erreicht ist. Der
Beton am gedrückten Rand bis $\varepsilon_{c2d}$, jede Stahllage bis
$\pm\varepsilon_{ud}$, und, sobald der ganze Querschnitt gedrückt ist, der
Beton im Punkt C bis $\varepsilon_{c1d}$. Es sind dieselben Grenzen wie im
Dehnungsfächer der genauen Resistenzlinie (siehe
[[opencivil.nachweis.dehnungsfaecher]]); die Linie endet darum dort, wo die
Resistenzlinie liegt.
