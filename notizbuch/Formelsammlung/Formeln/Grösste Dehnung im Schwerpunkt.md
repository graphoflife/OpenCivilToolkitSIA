---
erzeugt: d235be0c5903
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\varepsilon_{m,u} = \varepsilon_{oben} + \left(\varepsilon_{unten} - \varepsilon_{oben}\right) \cdot \frac{v_o}{h}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varepsilon_{oben}$ | – | ‰ | Zwischenwert |
| $\varepsilon_{unten}$ | – | ‰ | Zwischenwert |
| $v_o$ | Abstand des oberen Rands vom Schwerpunkt | mm | Zwischenwert |
| $h$ | Ausdehnung des Betons in Zugrichtung | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \varepsilon_{m,u} &= \varepsilon_{oben} + \left(\varepsilon_{unten} - \varepsilon_{oben}\right) \cdot \frac{v_o}{h} \\
  &= 49.28\,\text{‰} + \left(-2.08\,\text{‰} - 49.28\,\text{‰}\right) \cdot \frac{300\,\mathrm{mm}}{600\,\mathrm{mm}} \\
  &= 23.6\,\text{‰}
\end{aligned}
$$

## Im Code

- [[opencivil.querschnitt.schnittanalyse#Schnittpaar.herleitung_dehnung_am_ende|Schnittpaar.herleitung_dehnung_am_ende]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Ebene ist linear über die Tiefe. Zwischen dem oberen Rand – dem
gegenüber der Zugseite – und dem unteren liegt der Schwerpunkt im Abstand
$v_o$ vom oberen; dort gilt die Dehnung, die mit der Normalkraft zusammengehört,
denn N greift im Schwerpunkt an. Bei der Platte liegt er auf halber Höhe, und
die Formel wird zum Mittel aus oben und unten.
