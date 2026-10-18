---
erzeugt: 48c9c9650b35
art: formel
tags: [formel]
---
> [!warning] Normstelle fehlt noch
> Sie kommt vom Benutzer und wird im Code eingetragen – von dort steht sie im Bericht und hier.

$$
V_{Rd,c} = 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin \alpha \cdot \cos \alpha
$$

## Grössen

| Zeichen | Bedeutung | Einheit | Woher |
| --- | --- | --- | --- |
| $d$ | – | mm | [[Statische Höhe]] |
| $k_c$ | Abminderung der Betondruckfestigkeit in der Druckdiagonalen | – | Vorgabe |
| $f_{cd}$ | Bemessungswert der Betondruckfestigkeit | N/mm² | [[Bemessungswert der Betondruckfestigkeit]] |
| $\alpha$ | – | ° | Zwischenwert |

## Beispiel

Mit den Zahlen aus dem Prüfprojekt «Jeder Nachweis»:

$$
\begin{aligned}
  V_{Rd,c} &= 0.9 \cdot d \cdot k_c \cdot f_{cd} \cdot \sin \alpha \cdot \cos \alpha \\
  &= 0.9 \cdot 249\,\mathrm{mm} \cdot 0.55 \cdot 20\,\mathrm{N}/\mathrm{mm}^{2} \cdot \sin 30{}^{\circ} \cdot \cos 30{}^{\circ} \\
  &= 1067.4\,\mathrm{kN}/\mathrm{m}
\end{aligned}
$$

## Gebraucht von

- [[Querkraftwiderstand mit Querkraftbewehrung]]

## Im Code

- [[opencivil.nachweis.querkraft#protokoll_mit_buegeln|protokoll_mit_buegeln]]

## Themen

- [[Querkraft]]
- [[Kennzahlen]]

<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->

## Theorie

Die Druckdiagonalen tragen die Querkraft schräg ab. Ihr Querschnitt je
Laufmeter ist $0.9\,d \cdot \cos\alpha$, ihre Kraft wirkt unter $\alpha$ --
daher $\sin\alpha \cdot \cos\alpha$, am grössten bei 45°. Der Beton in den
Diagonalen ist durch die Risse quer dazu geschwächt; $k_c$ mindert seine
Festigkeit entsprechend.
