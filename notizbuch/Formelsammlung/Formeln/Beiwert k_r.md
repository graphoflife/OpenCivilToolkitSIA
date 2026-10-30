---
erzeugt: 4843431bdc6f
art: formel
tags: [formel]
normstelle: "SIA 262:2025, 4.3.6.3.2, (59)"
---
> [!info] Normstelle
> SIA 262:2025, 4.3.6.3.2, (59)

*In der Herleitung: «Beiwert für Bauteilgrösse, Plattenrotation und Grösstkorn»*

$$
k_r = \min\left[2;\ \frac{1}{0.45 + 0.18 \cdot \psi \cdot d \cdot k_g}\right] \quad \left(d\ \text{in}\ \mathrm{mm}\right)
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\psi$ | – | – | [[Massgebende Plattenrotation – die grössere]] |
| $d$ | – | mm | [[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]] |
| $k_g$ | – | – | [[Beiwert der Gesteinskörnung]] |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  k_r &= \min\left[2;\ \frac{1}{0.45 + 0.18 \cdot \psi \cdot d \cdot k_g}\right] \\
  &= \min\left[2;\ \frac{1}{0.45 + 0.18 \cdot 0.0186 \cdot 234 \cdot 1.2}\right] \\
  &= 0.721 \quad \left(d\ \text{in}\ \mathrm{mm}\right)
\end{aligned}
$$

## Gebraucht von

- [[Durchstanzwiderstand ohne Durchstanzbewehrung]]

## Im Code

- [[opencivil.durchstanzen.nachweis#Durchstanzen._k_r|Durchstanzen._k_r]]

## Themen

- [[Durchstanzen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

$k_r$ sagt, wie viel der Beton am kritischen Schubriss noch trägt. Je mehr
sich die Platte über der Stütze verdreht ([[Massgebende Plattenrotation – die grössere]]),
desto breiter der Riss und desto weniger Querkraft geht über die
Rissverzahnung. Die Bauteilgrösse geht über $d$ ein, das Grösstkorn über
$k_g$ ([[Beiwert der Gesteinskörnung]]). Die Gleichung rechnet mit $d$ in mm;
nach oben ist $k_r$ auf 2 begrenzt.
