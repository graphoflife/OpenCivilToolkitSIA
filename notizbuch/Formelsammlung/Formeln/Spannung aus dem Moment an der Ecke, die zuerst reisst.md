---
erzeugt: fdaaef85992c
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\sigma_M = \frac{\left|M\right|}{W}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $M$ | – | kNm | Zwischenwert |
| $W$ | – | ·10⁶ mm³ | [[Widerstandsmoment zum gezogensten Betonpunkt]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\sigma_M = \frac{\left|M\right|}{W} = \frac{\left|-50\,\mathrm{kNm}\right|}{44.25\,\cdot 10^{6}\,\mathrm{mm}^{3}} = 1.13\,\mathrm{N}/\mathrm{mm}^{2}
$$

## Gebraucht von

- [[Rissnormalkraft beim Moment]]

## Im Code

- [[opencivil.spannungsanalyse.schnitt#Schnittpaar.herleitung_riss|Schnittpaar.herleitung_riss]]

## Themen

- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Beim gezeichneten Querschnitt reisst unter Zug die Ecke zuerst, an der
$N/A + \sigma_M$ die wirksame Zugfestigkeit ihres Betons zuerst erreicht.
$\sigma_M$ ist die Spannung, die das Moment allein dort weckt, am
ungerissenen Bruttoquerschnitt ohne Stahl: unter reiner Biegung mit dem
Deviationsmoment ([[Spannung im ungerissenen Querschnitt]]), als $|M|/W$ mit
dem [[Widerstandsmoment zum gezogensten Betonpunkt]] in der Richtung, in die
das Moment zieht. Ein negatives Moment zieht eine andere Ecke.

So rechnet die Spannung-Dehnung-Analyse, wenn die Nulllinie kippt -- abgeleitet
aus der Entscheidung des Benutzers vom 2026-10-17, unter reiner Biegung
gelte, wo $f_{ct}$ zuerst erreicht wird; nicht nachgeschlagen.
