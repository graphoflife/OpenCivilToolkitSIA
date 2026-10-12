---
erzeugt: c855f8928ff2
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Flächenträgheitsmoment, «Rundstütze» (Kreis)»*

$$
I_{\text{Q2}} = \frac{\pi \cdot \left(d_{\text{Q2}}\right)^{4}}{64}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d_{\text{Q2}}$ | Durchmesser, Rundstütze | mm | Vorgabe |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
I_{\text{Q2}} = \frac{\pi \cdot \left(d_{\text{Q2}}\right)^{4}}{64} = \frac{\pi \cdot \left(400\,\mathrm{mm}\right)^{4}}{64} = 1256.64\,\cdot 10^{6}\,\mathrm{mm}^{4}
$$

## Im Code

- [[opencivil.stabwerk.querschnitte]]

## Themen

- [[Stabquerschnitte]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Um jede Achse durch den Mittelpunkt dasselbe: ein Kreis biegt sich in jeder
Richtung gleich. Es wächst mit der vierten Potenz des Durchmessers -- eine
Rundstütze mit doppeltem Durchmesser ist sechzehnmal so steif.
