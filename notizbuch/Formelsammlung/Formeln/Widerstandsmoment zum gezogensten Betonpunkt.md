---
erzeugt: ee68c3adca60
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Widerstandsmoment zum gezogensten Betonpunkt»*

$$
W = \frac{I_y \cdot I_z - I_{yz}^{2}}{I_{yz} \cdot y' - I_z \cdot z'}
$$

*In der Herleitung: «Widerstandsmoment zum gezogensten Betonpunkt»*

$$
W = \frac{I_y \cdot I_z - I_{yz}^{2}}{I_z \cdot z' - I_{yz} \cdot y'}
$$

*In der Herleitung: «Widerstandsmoment zum gezogensten Betonpunkt»*

$$
W = \frac{I_y \cdot I_z - I_{yz}^{2}}{I_{yz} \cdot z' - I_y \cdot y'}
$$

*In der Herleitung: «Widerstandsmoment zum gezogensten Betonpunkt»*

$$
W = \frac{I_y \cdot I_z - I_{yz}^{2}}{I_y \cdot y' - I_{yz} \cdot z'}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $I_y$ | – | ·10⁶ mm⁴ | Zwischenwert |
| $I_z$ | – | ·10⁶ mm⁴ | Zwischenwert |
| $I_{yz}$ | – | ·10⁶ mm⁴ | Zwischenwert |
| $y'$ | – | mm | Zwischenwert |
| $z'$ | – | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_{yz} \cdot y' - I_z \cdot z'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-400\,\mathrm{mm}\right) - 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-300\,\mathrm{mm}\right)} \\
  &= 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_z \cdot z' - I_{yz} \cdot y'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{22475\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 300\,\mathrm{mm} - 0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 400\,\mathrm{mm}} \\
  &= 44.25\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_{yz} \cdot z' - I_y \cdot y'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-300\,\mathrm{mm}\right) - 13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-400\,\mathrm{mm}\right)} \\
  &= 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  W &= \frac{I_y \cdot I_z - I_{yz}^{2}}{I_y \cdot y' - I_{yz} \cdot z'} \\
  &= \frac{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 22475\,\cdot 10^{6}\,\mathrm{mm}^{4} - \left(0\,\cdot 10^{6}\,\mathrm{mm}^{4}\right)^{2}}{13275\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot 400\,\mathrm{mm} - 0\,\cdot 10^{6}\,\mathrm{mm}^{4} \cdot \left(-300\,\mathrm{mm}\right)} \\
  &= 56.19\,\cdot 10^{6}\,\mathrm{mm}^{3}
\end{aligned}
$$

## Gebraucht von

- [[Rissmoment des ungerissenen Querschnitts]]

## Im Code

- [[opencivil.nachweis.richtungsnachweise#SproedesVersagenQA.pruefe|SproedesVersagenQA.pruefe]]

## Themen

- [[Sprödes Versagen je Richtung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Das Rissmoment ist Zugfestigkeit mal Widerstandsmoment. Für den gezeichneten
Querschnitt folgt das Widerstandsmoment aus der
[[Spannung im ungerissenen Querschnitt]]: gesucht ist das Moment, bei dem der
gezogenste Punkt gerade $f_{ct,eff}$ erreicht. Welche der vier Fassungen gilt,
hängt davon ab, um welche Achse das Moment wirkt und mit welchem Vorzeichen --
darum stehen hier vier.
