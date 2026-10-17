---
erzeugt: 746d7394b89b
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
\sigma(y, z) = -\frac{M_y\,(I_z z' - I_{yz} y') + M_z\,(I_y y' - I_{yz} z')}{I_y I_z - I_{yz}^2}\qquad y' = y - y_S,\ z' = z - z_S
$$

## Im Code

- [[opencivil.nachweis.rissgroessen#protokoll_spannung_ungerissen|protokoll_spannung_ungerissen]]

## Themen

- [[Sprödes Versagen je Richtung]]
- [[Zwängung auf Biegung]]
- [[Spannung-Dehnung-Analyse]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Biegespannung im ungerissenen, elastischen Querschnitt unter Momenten um
beide Achsen. Bei symmetrischen Querschnitten ist $I_{yz} = 0$, und die
Formel zerfällt in die bekannte $\sigma = -M_y z'/I_y - M_z y'/I_z$ -- mit den
Vorzeichen der Querschnittsanalyse zieht ein positives $M_y$ unten, wo $z'$
negativ ist. Bei unsymmetrischen koppelt das
Deviationsmoment beide Richtungen: ein Moment um $y$ allein biegt auch um
$z$.

Am gezogensten Betonpunkt beginnt der Riss; dort wird die Spannung gleich der
wirksamen Zugfestigkeit gesetzt.
