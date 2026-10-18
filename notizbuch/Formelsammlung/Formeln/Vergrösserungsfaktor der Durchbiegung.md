---
erzeugt: 0768ba687ea2
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.4.3.2.5"
---
> [!info] Normstelle
> SIA 262:2025, 4.4.3.2.5

*In der Herleitung: «Vergrösserungsfaktor der Durchbiegung – allgemein»*

$$
\omega_w = \frac{w}{w_c} = \frac{1 - 20 \cdot \rho'}{10 \cdot \rho^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d}\right)^{3} \qquad \rho = \frac{A_s}{b \cdot d} \qquad \rho' = \frac{A_s'}{b \cdot d'}
$$

*In der Herleitung: «Vergrösserungsfaktor, Zug unten»*

$$
\omega_w = \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{2,x}}\right)^{3}
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\rho_{o}$ | – | – | [[Bewehrungsgehalt]] |
| $\rho_{u}$ | – | – | [[Bewehrungsgehalt]] |
| $\varphi$ | Kriechzahl | – | Zwischenwert |
| $h$ | Plattendicke | mm | Vorgabe |
| $d_{2,x}$ | – | mm | [[Statische Höhe]] |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
\begin{aligned}
  \omega_w &= \frac{1 - 20 \cdot \rho_{o}}{10 \cdot \rho_{u}^{0.7}} \cdot \left(0.75 + 0.1 \cdot \varphi\right) \cdot \left(\frac{h}{d_{2,x}}\right)^{3} \\
  &= \frac{1 - 20 \cdot 0.00299}{10 \cdot 0.00988^{0.7}} \cdot \left(0.75 + 0.1 \cdot 2\right) \cdot \left(\frac{300\,\mathrm{mm}}{248.1\,\mathrm{mm}}\right)^{3} \\
  &= 4
\end{aligned}
$$

## Gebraucht von

- [[Wirksame Durchbiegung]]

## Im Code

- [[opencivil.nachweis.verformung#Vergroesserungsfaktor.rechne|Vergroesserungsfaktor.rechne]]

## Themen

- [[Verformung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

$w_c$ ist die Durchbiegung, die man elastisch am ungerissenen Betonquerschnitt
rechnet, mit der Steifigkeit $E_{cm}$ -- leicht zu bekommen, aber zu klein:
die gerissene Platte ist weicher, und unter Dauerlast kriecht der Beton. Der
Faktor $\omega_w = w/w_c$ schätzt, um wie viel beides die Durchbiegung
vergrössert.

- $\rho$, der Bewehrungsgehalt der gezogenen Seite, steht im Nenner: mehr
  Zugbewehrung macht den gerissenen Querschnitt steifer.
- $\rho'$ gehört zur Gegenseite und mindert den Faktor: gedrückte Bewehrung
  hält die Druckzone gegen das Kriechen.
- $0.75 + 0.1\,\varphi$ ist der Anteil des Kriechens, mit der Kriechzahl, die
  oben im Fenster «Verformung» steht.
- $(h/d)^3$ rechnet die Steifigkeit von der statischen Höhe auf die ganze
  Dicke um.

Gerechnet wird in x, je Seite, die ein Verformungsfall zieht -- einmal je
Platte, nicht je Fall; die Gegenseite der einen ist die gezogene der anderen.
Der Faktor geht in die [[Wirksame Durchbiegung]] ein.
