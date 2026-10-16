---
erzeugt: 3cbe6b578587
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

*In der Herleitung: «Wirksame Durchbiegung, Zug unten»*

$$
w_{eff} = \omega_w \cdot w
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $\omega_w$ | Vergrösserungsfaktor der Durchbiegung, Zug unten | – | [[Vergrösserungsfaktor der Durchbiegung]] |
| $w$ | Durchbiegung mit E\_cm | mm | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Beispielprojekt:

$$
w_{eff} = \omega_w \cdot w = 4 \cdot 3.5\,\mathrm{mm} = 14\,\mathrm{mm}
$$

## Im Code

- [[opencivil.nachweis.verformung#Verformung|Verformung._einen_fall]]

## Themen

- [[Verformung]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Der Benutzer rechnet $w$ selbst, an seinem System und mit der Steifigkeit
$E_{cm}$ des ungerissenen Querschnitts -- das ist $w_c$ der Norm. Mal den
[[Vergrösserungsfaktor der Durchbiegung]] der gezogenen Seite wird daraus die
Durchbiegung der gerissenen Platte unter Dauerlast, die gegen den
[[Grenzwert der Durchbiegung]] gehalten wird.

Ein Fall im Feld zieht die Platte unten, ein Kragarm oder ein Stützbereich
oben; danach richtet sich, welcher der beiden Faktoren gilt. Ist die gezogene
Seite in x unbewehrt, gibt es keinen Faktor und keinen Nachweis.
