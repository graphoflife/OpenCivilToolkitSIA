---
erzeugt: 3dc44faca293
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Grösste Krümmung»*

$$
\chi_{u} = \frac{\varepsilon_{unten} - \varepsilon_{oben}}{h}
$$

*In der Herleitung: «Grösste Krümmung»*

$$
\chi_{u} = \frac{\varepsilon_{unten} - \varepsilon_{oben}}{h_{\vartheta}} \cdot \cos\left(\vartheta\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\varepsilon_{unten}$ | – | ‰ | Zwischenwert |
| $\varepsilon_{oben}$ | – | ‰ | Zwischenwert |
| $h$ | Plattendicke | mm | Vorgabe, Zwischenwert |
| $h_{\vartheta}$ | Tiefe des Betons senkrecht zur Nulllinie | mm | Zwischenwert |
| $\vartheta$ | – | ° | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\chi_{u} = \frac{\varepsilon_{unten} - \varepsilon_{oben}}{h} = \frac{10.21\,\text{‰} - \left(-3.5\,\text{‰}\right)}{300\,\mathrm{mm}} = 0.04571\,\mathrm{m}^{-1}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  \chi_{u} &= \frac{\varepsilon_{unten} - \varepsilon_{oben}}{h_{\vartheta}} \cdot \cos\left(\vartheta\right) \\
  &= \frac{17.55\,\text{‰} - \left(-3.5\,\text{‰}\right)}{846.7\,\mathrm{mm}} \cdot \cos\left(-4.7{}^{\circ}\right) \\
  &= 0.02477\,\mathrm{m}^{-1}
\end{aligned}
$$

## Im Code

- [[opencivil.spannungsanalyse.herleitung#herleitung|herleitung]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Krümmung am Ende der $M$–$\chi$-Linie: Dehnung unten minus Dehnung oben,
geteilt durch die Höhe -- die Neigung der Dehnungsebene. Das Verhältnis der
grössten Krümmung zu der beim Fliessbeginn sagt, wie viel Verformung der
Querschnitt nach dem Fliessen noch zulässt.

Kippt die Nulllinie um $\vartheta$, gelten die Randdehnungen senkrecht zu
ihr, über die Tiefe $h_{\vartheta}$ des Betons in dieser Richtung. Die Linie
läuft über den Anteil der Krümmung senkrecht zur Achse der Biegung, darum
$\cos\vartheta$.
